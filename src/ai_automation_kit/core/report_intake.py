"""Safe, local-only intake of report files."""

from __future__ import annotations

import errno
import hashlib
import importlib
import io
import os
import re
import stat
import struct
import zipfile
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple
from xml.etree import ElementTree


MAX_FILE_BYTES = 10 * 1024 * 1024
MAX_FILES = 200
MAX_CONTAINER_MEMBERS = 256
MAX_CONTAINER_MEMBER_BYTES_MULTIPLIER = 4
MAX_CONTAINER_TOTAL_BYTES_MULTIPLIER = 8
MAX_CONTAINER_TEXT_BYTES_MULTIPLIER = 2

TEXT_EXTENSIONS = {".md", ".txt", ".csv", ".json"}
DOCUMENT_EXTENSIONS = {".docx", ".xlsx", ".pdf"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
ARCHIVE_EXTENSIONS = {".zip", ".tar", ".gz", ".bz2", ".xz", ".7z", ".rar", ".jar"}
SCRIPT_EXTENSIONS = {
    ".bat",
    ".cmd",
    ".command",
    ".js",
    ".ps1",
    ".py",
    ".rb",
    ".sh",
    ".php",
    ".pl",
    ".ts",
}
SUPPORTED_EXTENSIONS = TEXT_EXTENSIONS | DOCUMENT_EXTENSIONS | IMAGE_EXTENSIONS


class _ContainerLimitError(ValueError):
    def __init__(self, warning: str):
        super().__init__(warning)
        self.warning = warning


def _extension(path: Path) -> str:
    return path.suffix.lower()


def _classification(path: Path) -> Dict[str, str]:
    name = path.name.lower()
    period = "unknown"
    quarter = re.search(r"(?<!\d)(20\d{2})[-_ ]?q([1-4])(?!\d)", name, re.I)
    month = re.search(r"(?<!\d)(20\d{2})[-_年](0?[1-9]|1[0-2])月?(?!\d)", name)
    compact_month = re.search(r"(?<!\d)(20\d{2})(0[1-9]|1[0-2])(?!\d)", name)
    year = re.search(r"(?<!\d)(20\d{2})(?!\d)", name)
    if quarter:
        period = "{}-Q{}".format(quarter.group(1), quarter.group(2))
    elif month:
        period = "{}-{:02d}".format(int(month.group(1)), int(month.group(2)))
    elif compact_month:
        period = "{}-{}".format(compact_month.group(1), compact_month.group(2))
    elif year:
        period = year.group(1)

    role_signals = (
        ("sales", ("sales", "revenue", "売上", "販売")),
        ("financial", ("finance", "financial", "profit", "損益", "財務")),
        ("operations", ("operation", "operations", "ops", "業務", "運用")),
        ("metrics", ("kpi", "metric", "指標", "実績")),
        ("executive_summary", ("executive", "board", "summary", "概要")),
        ("data", ("data", "raw", "export", "データ")),
    )
    content_role = next(
        (role for role, signals in role_signals if any(signal in name for signal in signals)),
        None,
    )
    if content_role is None:
        if _extension(path) in {".csv", ".xlsx"}:
            content_role = "spreadsheet_data"
        elif _extension(path) in {".md", ".txt", ".json", ".docx", ".pdf"}:
            content_role = "narrative"
        elif _extension(path) in IMAGE_EXTENSIONS:
            content_role = "visual"
        else:
            content_role = "other"
    return {"report_period": period, "content_role": content_role}


def _record_base(path: Path, source_role: str) -> Dict:
    classification = _classification(path)
    return {
        "status": "rejected",
        "source_role": source_role,
        "original_path": str(path),
        "name": path.name,
        "extension": _extension(path),
        "bytes": None,
        "sha256": None,
        "extraction_status": "not_attempted",
        "text": None,
        "warnings": [],
        "reason": None,
        "classification": classification,
        "report_period": classification["report_period"],
        "content_role": classification["content_role"],
    }


def _rejected(
    path: Path,
    source_role: str,
    reason: str,
    *,
    size: Optional[int] = None,
    sha256: Optional[str] = None,
    warnings: Optional[List[str]] = None,
) -> Dict:
    record = _record_base(path, source_role)
    record["reason"] = reason
    record["bytes"] = size
    record["sha256"] = sha256
    if warnings:
        record["warnings"] = list(warnings)
    return record


def _is_hidden(path: Path) -> bool:
    return path.name.startswith(".")


def _is_script_or_executable(path: Path, mode: Optional[int] = None) -> bool:
    if _extension(path) in SCRIPT_EXTENSIONS:
        return True
    if mode is not None and mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH):
        return True
    return False


def _looks_binary(data: bytes) -> bool:
    if b"\x00" in data:
        return True
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return True
    return False


def _no_follow_flag() -> int:
    flag = getattr(os, "O_NOFOLLOW", None)
    if flag is None:
        raise OSError(errno.ENOTSUP, "O_NOFOLLOW is required for safe local intake")
    return flag


def _absolute_path(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path)))


def _open_directory_fd(path: Path, create: bool = False) -> int:
    path = _absolute_path(Path(path))
    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | _no_follow_flag()
    descriptor = os.open(path.anchor, directory_flags)
    try:
        for component in path.parts:
            if component == path.anchor:
                continue
            try:
                next_descriptor = os.open(component, directory_flags, dir_fd=descriptor)
            except FileNotFoundError:
                if not create:
                    raise
                os.mkdir(component, mode=0o700, dir_fd=descriptor)
                next_descriptor = os.open(component, directory_flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = next_descriptor
        return descriptor
    except Exception:
        try:
            os.close(descriptor)
        except OSError:
            pass
        raise


def _open_file_no_follow(path: Path) -> int:
    path = _absolute_path(Path(path))
    parent_descriptor = _open_directory_fd(path.parent)
    try:
        return os.open(path.name, os.O_RDONLY | _no_follow_flag(), dir_fd=parent_descriptor)
    finally:
        os.close(parent_descriptor)


def _unlink_at(directory_descriptor: int, name: str) -> None:
    os.unlink(name, dir_fd=directory_descriptor)


def _read_limited(path: Path, max_file_bytes: int) -> Tuple[Optional[bytes], Optional[str]]:
    try:
        descriptor = _open_file_no_follow(path)
    except FileNotFoundError:
        return None, "missing_path"
    except (PermissionError, OSError) as error:
        if getattr(error, "errno", None) == errno.ELOOP:
            return None, "unsafe_path"
        return None, "unreadable"
    try:
        with os.fdopen(descriptor, "rb") as source:
            data = source.read(max_file_bytes + 1)
    except (PermissionError, OSError):
        return None, "unreadable"
    if len(data) > max_file_bytes:
        return None, "file_too_large"
    return data, None


def _safe_lstat(path: Path):
    path = _absolute_path(Path(path))
    parent_descriptor = None
    try:
        parent_descriptor = _open_directory_fd(path.parent)
        return os.stat(path.name, dir_fd=parent_descriptor, follow_symlinks=False), None
    except FileNotFoundError:
        return None, "missing_path"
    except (PermissionError, OSError) as error:
        if getattr(error, "errno", None) == errno.ELOOP:
            return None, "unsafe_path"
        return None, "unreadable"
    finally:
        if parent_descriptor is not None:
            os.close(parent_descriptor)


def _image_metadata(path: Path, data: bytes) -> Dict[str, object]:
    extension = _extension(path)
    metadata: Dict[str, object] = {"format": extension.lstrip(".").upper()}
    if extension == ".png":
        dimensions = _png_dimensions(data)
        metadata["width"], metadata["height"] = dimensions
    elif extension in {".jpg", ".jpeg"}:
        width, height = _jpeg_dimensions(data)
        metadata["width"], metadata["height"] = width, height
    elif extension == ".webp":
        width, height = _webp_dimensions(data)
        metadata["width"], metadata["height"] = width, height
    if "width" not in metadata or "height" not in metadata:
        metadata["width"] = None
        metadata["height"] = None
    return metadata


def _png_dimensions(data: bytes) -> Tuple[Optional[int], Optional[int]]:
    if len(data) < 24 or not data.startswith(b"\x89PNG\r\n\x1a\n") or struct.unpack(">I", data[8:12])[0] != 13 or data[12:16] != b"IHDR":
        return None, None
    width, height = struct.unpack(">II", data[16:24])
    if width == 0 or height == 0:
        return None, None
    return width, height


def _jpeg_dimensions(data: bytes) -> Tuple[Optional[int], Optional[int]]:
    if not data.startswith(b"\xff\xd8"):
        return None, None
    offset = 2
    while offset + 4 <= len(data):
        if data[offset] != 0xFF:
            offset += 1
            continue
        marker = data[offset + 1]
        offset += 2
        if marker in (0xD8, 0xD9):
            continue
        if offset + 2 > len(data):
            break
        segment_length = struct.unpack(">H", data[offset:offset + 2])[0]
        if marker in range(0xC0, 0xC4) or marker in range(0xC5, 0xC8) or marker in range(0xC9, 0xCC) or marker in range(0xCD, 0xD0):
            if segment_length >= 7 and offset + 7 <= len(data):
                height, width = struct.unpack(">HH", data[offset + 3:offset + 7])
                return width, height
        offset += segment_length
    return None, None


def _webp_dimensions(data: bytes) -> Tuple[Optional[int], Optional[int]]:
    if len(data) < 20 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        return None, None
    riff_size = struct.unpack("<I", data[4:8])[0]
    if riff_size + 8 > len(data):
        return None, None
    chunk = data[12:16]
    chunk_size = struct.unpack("<I", data[16:20])[0]
    if chunk == b"VP8X" and chunk_size >= 10 and len(data) >= 30:
        width = 1 + int.from_bytes(data[24:27], "little")
        height = 1 + int.from_bytes(data[27:30], "little")
        return width, height
    if chunk == b"VP8L" and chunk_size >= 5 and len(data) >= 25 and data[20] == 0x2F:
        width = 1 + (data[21] | ((data[22] & 0x3F) << 8))
        height = 1 + ((data[22] >> 6) | (data[23] << 2) | ((data[24] & 0x0F) << 10))
        return width, height
    if chunk == b"VP8 " and chunk_size >= 10:
        frame = data[20:]
        signature = frame.find(b"\x9d\x01\x2a")
        if signature >= 0 and len(frame) >= signature + 7:
            width, height = struct.unpack("<HH", frame[signature + 3:signature + 7])
            return width & 0x3FFF, height & 0x3FFF
    return None, None


def _valid_binary_format(path: Path, data: bytes) -> bool:
    extension = _extension(path)
    if extension == ".png":
        return _png_dimensions(data) != (None, None)
    if extension in {".jpg", ".jpeg"}:
        width, height = _jpeg_dimensions(data)
        return bool(width and height) and b"\xff\xd9" in data
    if extension == ".webp":
        return _webp_dimensions(data) != (None, None)
    if extension == ".pdf":
        return data.startswith(b"%PDF-") and b"%%EOF" in data
    return True


def _xml_local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _zip_limits(max_file_bytes: int) -> Tuple[int, int, int, int]:
    return (
        MAX_CONTAINER_MEMBERS,
        max_file_bytes * MAX_CONTAINER_MEMBER_BYTES_MULTIPLIER,
        max_file_bytes * MAX_CONTAINER_TOTAL_BYTES_MULTIPLIER,
        max_file_bytes * MAX_CONTAINER_TEXT_BYTES_MULTIPLIER,
    )


def _zip_preflight(archive: zipfile.ZipFile, max_file_bytes: int) -> Dict[str, object]:
    max_members, max_member_bytes, max_total_bytes, _ = _zip_limits(max_file_bytes)
    infos = archive.infolist()
    if len(infos) > max_members:
        raise _ContainerLimitError("zip_member_count_limit")
    total_bytes = 0
    by_name = {}
    for info in infos:
        try:
            member_bytes = int(info.file_size)
        except (AttributeError, TypeError, ValueError):
            raise ValueError("invalid_container")
        if member_bytes < 0 or member_bytes > max_member_bytes:
            raise _ContainerLimitError("zip_member_size_limit")
        total_bytes += member_bytes
        if total_bytes > max_total_bytes:
            raise _ContainerLimitError("zip_total_size_limit")
        by_name[info.filename] = info
    return by_name


def _zip_member(archive: zipfile.ZipFile, info: object, max_file_bytes: int) -> bytes:
    _, max_member_bytes, _, _ = _zip_limits(max_file_bytes)
    with archive.open(info, "r") as member:
        data = member.read(max_member_bytes + 1)
    if len(data) > max_member_bytes:
        raise _ContainerLimitError("zip_member_size_limit")
    return data


def _extract_docx(data: bytes, max_file_bytes: int) -> str:
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        members = _zip_preflight(archive, max_file_bytes)
        if "word/document.xml" not in members:
            raise ValueError("invalid_container")
        xml = ElementTree.fromstring(_zip_member(archive, members["word/document.xml"], max_file_bytes))
    paragraphs = []
    current = []
    _, _, _, max_text_bytes = _zip_limits(max_file_bytes)
    text_bytes = 0
    for element in xml.iter():
        local_name = _xml_local_name(element.tag)
        if local_name == "t" and element.text:
            text_bytes += len(element.text.encode("utf-8"))
            if text_bytes > max_text_bytes:
                raise _ContainerLimitError("extracted_text_size_limit")
            current.append(element.text)
        elif local_name == "p" and current:
            paragraphs.append("".join(current))
            current = []
    if current:
        paragraphs.append("".join(current))
    return "\n".join(paragraphs)


def _extract_xlsx(data: bytes, max_file_bytes: int) -> str:
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        members = _zip_preflight(archive, max_file_bytes)
        shared_strings = []
        if "xl/sharedStrings.xml" in members:
            root = ElementTree.fromstring(_zip_member(archive, members["xl/sharedStrings.xml"], max_file_bytes))
            for item in root.iter():
                if _xml_local_name(item.tag) == "si":
                    shared_strings.append("".join(part.text or "" for part in item.iter() if _xml_local_name(part.tag) == "t"))
        lines = []
        sheet_names = sorted(name for name in members if name.startswith("xl/worksheets/") and name.endswith(".xml"))
        if not sheet_names:
            raise ValueError("invalid_container")
        _, _, _, max_text_bytes = _zip_limits(max_file_bytes)
        text_bytes = 0
        for sheet_name in sheet_names:
            root = ElementTree.fromstring(_zip_member(archive, members[sheet_name], max_file_bytes))
            for row in (element for element in root.iter() if _xml_local_name(element.tag) == "row"):
                values = []
                for cell in (element for element in row if _xml_local_name(element.tag) == "c"):
                    cell_type = cell.attrib.get("t")
                    value = next((child.text for child in cell if _xml_local_name(child.tag) == "v"), None)
                    if cell_type == "s" and value is not None:
                        try:
                            value = shared_strings[int(value)]
                        except (ValueError, IndexError):
                            pass
                    elif cell_type == "inlineStr":
                        value = "".join(part.text or "" for part in cell.iter() if _xml_local_name(part.tag) == "t")
                    text_bytes += len((value or "").encode("utf-8")) + 1
                    if text_bytes > max_text_bytes:
                        raise _ContainerLimitError("extracted_text_size_limit")
                    values.append(value or "")
                if values:
                    lines.append("\t".join(values))
    return "\n".join(lines)


def _extract_pdf(data: bytes) -> Tuple[str, Optional[str], List[str]]:
    try:
        reader_module = importlib.import_module("pypdf")
    except ImportError:
        return "optional_reader_missing", None, ["pypdf_not_installed"]
    try:
        reader = reader_module.PdfReader(io.BytesIO(data), strict=False)
        text = "\n".join((page.extract_text() or "") for page in reader.pages).strip()
        return "extracted", text, [] if text else ["pdf_text_empty"]
    except Exception as error:
        return "extraction_error", None, ["pdf_reader_error:{}".format(type(error).__name__)]


def extract_text(path: Path, *, max_file_bytes: int = MAX_FILE_BYTES) -> Dict:
    """Read and extract one local file without following source symlinks."""
    path = Path(path)
    base = _record_base(path, "unknown")
    base["status"] = "rejected"
    if max_file_bytes <= 0:
        raise ValueError("max_file_bytes must be positive")
    file_stat, stat_error = _safe_lstat(path)
    if stat_error:
        base["reason"] = stat_error
        return base
    base["bytes"] = file_stat.st_size
    if stat.S_ISLNK(file_stat.st_mode):
        base["reason"] = "symlink"
        return base
    if not stat.S_ISREG(file_stat.st_mode):
        base["reason"] = "not_a_regular_file"
        return base
    if _is_hidden(path):
        base["reason"] = "hidden_file"
        return base
    if _is_script_or_executable(path, file_stat.st_mode):
        base["reason"] = "script_or_executable"
        return base
    if _extension(path) in ARCHIVE_EXTENSIONS:
        base["reason"] = "archive"
        return base

    data, read_error = _read_limited(path, max_file_bytes)
    if read_error:
        base["reason"] = read_error
        return base
    assert data is not None
    base["bytes"] = len(data)
    base["sha256"] = hashlib.sha256(data).hexdigest()
    if data.startswith((b"#!", b"\xef\xbb\xbf#!")):
        base["reason"] = "script_or_executable"
        return base
    extension = _extension(path)
    if extension not in SUPPORTED_EXTENSIONS:
        base["reason"] = "unknown_binary" if _looks_binary(data[:4096]) else "unsupported_extension"
        return base
    if extension in IMAGE_EXTENSIONS | {".pdf"} and not _valid_binary_format(path, data):
        base["reason"] = "invalid_format"
        return base

    warnings = []
    try:
        if extension in TEXT_EXTENSIONS:
            text = data.decode("utf-8")
            extraction_status = "extracted"
        elif extension == ".docx":
            text = _extract_docx(data, max_file_bytes)
            extraction_status = "extracted"
        elif extension == ".xlsx":
            text = _extract_xlsx(data, max_file_bytes)
            extraction_status = "extracted"
        elif extension == ".pdf":
            extraction_status, text, warnings = _extract_pdf(data)
        else:
            text = None
            extraction_status = "metadata_only"
            base["metadata"] = _image_metadata(path, data)
            warnings.append("ocr_not_attempted")
    except UnicodeDecodeError:
        base["reason"] = "invalid_utf8"
        return base
    except _ContainerLimitError as error:
        base["reason"] = "expanded_content_too_large"
        base["warnings"] = [error.warning]
        return base
    except (KeyError, ValueError, zipfile.BadZipFile, ElementTree.ParseError):
        base["reason"] = "invalid_container"
        return base

    if extraction_status == "extraction_error":
        base["reason"] = "extraction_error"
        base["warnings"] = warnings
        return base
    if extension in {".docx", ".xlsx"} and not text:
        warnings.append("empty_extracted_text")

    base["status"] = "accepted"
    base["extraction_status"] = extraction_status
    base["text"] = text
    base["warnings"] = warnings
    base["reason"] = None
    return base


def _iter_source_paths(paths: Iterable[Path]) -> Iterator[Tuple[Path, Optional[str]]]:
    for raw_path in paths:
        path = Path(raw_path)
        file_stat, stat_error = _safe_lstat(path)
        if stat_error or file_stat is None or stat.S_ISLNK(file_stat.st_mode) or not stat.S_ISDIR(file_stat.st_mode):
            yield path, None
            continue
        if _is_hidden(path):
            yield path, "hidden_directory"
            continue
        for root, directories, filenames in os.walk(str(path), topdown=True, followlinks=False):
            directories.sort()
            filenames.sort()
            hidden_directories = []
            symlink_directories = []
            for directory in list(directories):
                candidate = Path(root) / directory
                if _is_hidden(candidate):
                    directories.remove(directory)
                    hidden_directories.append(candidate)
                elif candidate.is_symlink():
                    directories.remove(directory)
                    symlink_directories.append(candidate)
            for candidate in hidden_directories:
                yield candidate, "hidden_directory"
            for candidate in symlink_directories:
                yield candidate, None
            for filename in filenames:
                yield Path(root) / filename, None


def inspect_sources(
    past_paths: List[Path],
    material_paths: List[Path],
    *,
    max_file_bytes: int = MAX_FILE_BYTES,
    max_files: int = MAX_FILES,
) -> Dict:
    """Discover, validate, extract, hash, classify, and deduplicate local inputs."""
    if max_file_bytes <= 0:
        raise ValueError("max_file_bytes must be positive")
    if max_files <= 0:
        raise ValueError("max_files must be positive")

    records = []
    skipped = []
    seen_hashes = set()
    inspected = 0
    truncated = False
    stop = False
    for paths, source_role in ((past_paths, "past_output"), (material_paths, "current_material")):
        if stop:
            break
        for path, skip_reason in _iter_source_paths(paths):
            if skip_reason:
                skipped.append({"path": str(path), "reason": skip_reason})
                continue
            if inspected >= max_files:
                truncated = True
                stop = True
                break
            inspected += 1
            result = extract_text(path, max_file_bytes=max_file_bytes)
            result["source_role"] = source_role
            if result.get("status") != "accepted":
                records.append(result)
                continue
            digest = result.get("sha256")
            if digest in seen_hashes:
                records.append(_rejected(path, source_role, "duplicate_content", size=result.get("bytes"), sha256=digest))
                continue
            seen_hashes.add(digest)
            records.append(result)

    accepted = [record for record in records if record.get("status") == "accepted"]
    rejected = [record for record in records if record.get("status") == "rejected"]
    return {
        "records": records,
        "accepted": accepted,
        "rejected": rejected,
        "skipped": skipped,
        "truncated": truncated,
        "counts": {"accepted": len(accepted), "rejected": len(rejected), "inspected": inspected, "total": len(records)},
    }


def _ensure_directory(path: Path) -> bool:
    descriptor = None
    try:
        descriptor = _open_directory_fd(path, create=True)
        return True
    except OSError:
        return False
    finally:
        if descriptor is not None:
            os.close(descriptor)


def _sanitized_name(value: str) -> str:
    candidate = Path(str(value)).name
    candidate = re.sub(r"[^A-Za-z0-9._-]", "_", candidate)
    candidate = candidate.lstrip(".")
    return candidate or "file"


def _collision_name(name: str, number: int) -> str:
    path = Path(name)
    suffix = path.suffix
    stem = path.name[:-len(suffix)] if suffix else path.name
    return "{}__{}{}".format(stem, number, suffix)


def _copy_rejected(record: Dict, reason: str) -> Dict:
    return {
        "status": "copy_rejected",
        "source_role": record.get("source_role"),
        "original_path": record.get("original_path"),
        "name": record.get("name"),
        "reason": reason,
    }


def _path_is_within(path: Path, workspace: Path) -> bool:
    try:
        return os.path.commonpath([str(_absolute_path(path)), str(_absolute_path(workspace))]) == str(_absolute_path(workspace))
    except ValueError:
        return False


def _destination_directory_is_unchanged(path: Path, workspace: Path, expected_identity: Tuple[int, int]) -> bool:
    if not _path_is_within(path, workspace):
        return False
    observed, error = _safe_lstat(path)
    if error or observed is None or not stat.S_ISDIR(observed.st_mode):
        return False
    return (observed.st_dev, observed.st_ino) == expected_identity


def copy_approved_files(records: List[Dict], workspace: Path) -> List[Dict]:
    """Copy only accepted records into a collision-safe, role-separated intake area."""
    workspace = Path(workspace)
    outcomes = []
    accepted_records = []
    for record in records:
        if "status" not in record:
            outcomes.append(_copy_rejected(record, "missing_status"))
        elif record["status"] == "accepted":
            accepted_records.append(record)
    if not _ensure_directory(workspace):
        return outcomes + [_copy_rejected(record, "workspace_unavailable") for record in accepted_records]
    intake = workspace / "00_intake"
    if not _ensure_directory(intake):
        return outcomes + [_copy_rejected(record, "workspace_unavailable") for record in accepted_records]
    role_directories = {}
    for role in ("past_output", "current_material"):
        directory_name = "past" if role == "past_output" else "current"
        directory = intake / directory_name
        if not _ensure_directory(directory):
            return outcomes + [_copy_rejected(record, "workspace_unavailable") for record in accepted_records]
        role_directories[role] = directory

    for record in accepted_records:
        role = record.get("source_role")
        destination_directory = role_directories.get(role)
        original_value = record.get("original_path")
        if destination_directory is None:
            outcomes.append(_copy_rejected(record, "invalid_source_role"))
            continue
        if not original_value:
            outcomes.append(_copy_rejected(record, "missing_original_path"))
            continue
        source = Path(str(original_value))
        file_stat, stat_error = _safe_lstat(source)
        if stat_error:
            reason = "unsafe_source_path" if stat_error == "unsafe_path" else stat_error
            outcomes.append(_copy_rejected(record, reason))
            continue
        if file_stat is None or stat.S_ISLNK(file_stat.st_mode):
            outcomes.append(_copy_rejected(record, "symlink"))
            continue
        if not stat.S_ISREG(file_stat.st_mode):
            outcomes.append(_copy_rejected(record, "not_a_regular_file"))
            continue
        name = _sanitized_name(record.get("name", source.name))
        expected_hash = record.get("sha256")
        expected_bytes = record.get("bytes")
        directory_descriptor = None
        try:
            directory_descriptor = _open_directory_fd(destination_directory)
        except OSError:
            outcomes.append(_copy_rejected(record, "unsafe_destination_path"))
            continue
        try:
            opened_destination_stat = os.fstat(directory_descriptor)
            opened_destination_identity = (opened_destination_stat.st_dev, opened_destination_stat.st_ino)
        except OSError:
            os.close(directory_descriptor)
            outcomes.append(_copy_rejected(record, "unsafe_destination_path"))
            continue
        number = 1
        try:
            while True:
                candidate_name = name if number == 1 else _collision_name(name, number)
                try:
                    descriptor = os.open(
                        candidate_name,
                        os.O_WRONLY | os.O_CREAT | os.O_EXCL | _no_follow_flag(),
                        0o600,
                        dir_fd=directory_descriptor,
                    )
                except FileExistsError:
                    number += 1
                    continue
                except OSError as error:
                    reason = "unsafe_destination_path" if error.errno == errno.ELOOP else "copy_failed"
                    outcomes.append(_copy_rejected(record, reason))
                    break

                digest = hashlib.sha256()
                byte_count = 0
                try:
                    with os.fdopen(descriptor, "wb") as destination_file:
                        source_descriptor = _open_file_no_follow(source)
                        with os.fdopen(source_descriptor, "rb") as source_file:
                            for chunk in iter(lambda: source_file.read(1024 * 1024), b""):
                                digest.update(chunk)
                                byte_count += len(chunk)
                                destination_file.write(chunk)
                    actual_hash = digest.hexdigest()
                    # The dir_fd anchors the write and cleanup; this postcheck detects rename or replacement races without claiming an OS-wide guarantee against every concurrent mutation.
                    if not _destination_directory_is_unchanged(destination_directory, workspace, opened_destination_identity):
                        try:
                            _unlink_at(directory_descriptor, candidate_name)
                        except OSError:
                            pass
                        outcomes.append(_copy_rejected(record, "destination_changed_during_copy"))
                        break
                    if expected_hash and actual_hash != expected_hash:
                        _unlink_at(directory_descriptor, candidate_name)
                        outcomes.append(_copy_rejected(record, "source_hash_mismatch"))
                        break
                    if expected_bytes is not None and byte_count != expected_bytes:
                        _unlink_at(directory_descriptor, candidate_name)
                        outcomes.append(_copy_rejected(record, "source_size_mismatch"))
                        break
                except OSError as error:
                    try:
                        _unlink_at(directory_descriptor, candidate_name)
                    except OSError:
                        pass
                    unsafe_errors = {errno.ELOOP, errno.ENOTDIR, errno.ENOTSUP}
                    reason = "unsafe_source_path" if error.errno in unsafe_errors else "copy_failed"
                    outcomes.append(_copy_rejected(record, reason))
                    break
                outcomes.append(
                    {
                        "status": "copied",
                        "source_role": role,
                        "original_path": str(source),
                        "copied_path": str(destination_directory / candidate_name),
                        "destination_path": str(destination_directory / candidate_name),
                        "name": candidate_name,
                        "bytes": byte_count,
                        "sha256": actual_hash,
                    }
                )
                break
        finally:
            os.close(directory_descriptor)
    return outcomes
