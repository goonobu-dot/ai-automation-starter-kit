"""Safe, local-only intake of report files."""

from __future__ import annotations

import errno
import hashlib
import importlib
import io
import itertools
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


def _open_no_follow(path: Path, flags: int):
    no_follow = getattr(os, "O_NOFOLLOW", 0)
    return os.open(str(path), flags | no_follow)


def _read_limited(path: Path, max_file_bytes: int) -> Tuple[Optional[bytes], Optional[str]]:
    try:
        descriptor = _open_no_follow(path, os.O_RDONLY)
    except FileNotFoundError:
        return None, "missing_path"
    except (PermissionError, OSError) as error:
        if getattr(error, "errno", None) == errno.ELOOP:
            return None, "symlink"
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
    try:
        return path.lstat(), None
    except FileNotFoundError:
        return None, "missing_path"
    except (PermissionError, OSError):
        return None, "unreadable"


def _image_metadata(path: Path, data: bytes) -> Dict[str, object]:
    extension = _extension(path)
    metadata: Dict[str, object] = {"format": extension.lstrip(".").upper()}
    if extension == ".png" and data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        metadata["width"], metadata["height"] = struct.unpack(">II", data[16:24])
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
                return struct.unpack(">HH", data[offset + 3:offset + 7])
        offset += segment_length
    return None, None


def _webp_dimensions(data: bytes) -> Tuple[Optional[int], Optional[int]]:
    if len(data) < 30 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        return None, None
    chunk = data[12:16]
    if chunk == b"VP8X" and len(data) >= 30:
        width = 1 + int.from_bytes(data[24:27], "little")
        height = 1 + int.from_bytes(data[27:30], "little")
        return width, height
    return None, None


def _xml_local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _zip_member(archive: zipfile.ZipFile, name: str, max_file_bytes: int) -> bytes:
    info = archive.getinfo(name)
    if info.file_size > max_file_bytes * 4:
        raise ValueError("zip_member_too_large")
    with archive.open(info, "r") as member:
        data = member.read(max_file_bytes * 4 + 1)
    if len(data) > max_file_bytes * 4:
        raise ValueError("zip_member_too_large")
    return data


def _extract_docx(data: bytes, max_file_bytes: int) -> str:
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        xml = ElementTree.fromstring(_zip_member(archive, "word/document.xml", max_file_bytes))
    paragraphs = []
    current = []
    for element in xml.iter():
        local_name = _xml_local_name(element.tag)
        if local_name == "t" and element.text:
            current.append(element.text)
        elif local_name == "p" and current:
            paragraphs.append("".join(current))
            current = []
    if current:
        paragraphs.append("".join(current))
    return "\n".join(paragraphs)


def _extract_xlsx(data: bytes, max_file_bytes: int) -> str:
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        shared_strings = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ElementTree.fromstring(_zip_member(archive, "xl/sharedStrings.xml", max_file_bytes))
            for item in root.iter():
                if _xml_local_name(item.tag) == "si":
                    shared_strings.append("".join(part.text or "" for part in item.iter() if _xml_local_name(part.tag) == "t"))
        lines = []
        sheet_names = sorted(name for name in archive.namelist() if name.startswith("xl/worksheets/") and name.endswith(".xml"))
        for sheet_name in sheet_names:
            root = ElementTree.fromstring(_zip_member(archive, sheet_name, max_file_bytes))
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
    except (KeyError, ValueError, zipfile.BadZipFile, ElementTree.ParseError):
        base["reason"] = "invalid_container"
        return base

    if extraction_status == "extraction_error":
        base["reason"] = "extraction_error"
        base["warnings"] = warnings
        return base

    base["status"] = "accepted"
    base["extraction_status"] = extraction_status
    base["text"] = text
    base["warnings"] = warnings
    base.pop("reason", None)
    return base


def _iter_source_paths(paths: Iterable[Path]) -> Iterator[Path]:
    for raw_path in paths:
        path = Path(raw_path)
        file_stat, stat_error = _safe_lstat(path)
        if stat_error or file_stat is None or stat.S_ISLNK(file_stat.st_mode) or not stat.S_ISDIR(file_stat.st_mode):
            yield path
            continue
        for root, directories, filenames in os.walk(str(path), topdown=True, followlinks=False):
            directories.sort()
            filenames.sort()
            symlink_directories = []
            for directory in list(directories):
                candidate = Path(root) / directory
                if candidate.is_symlink():
                    directories.remove(directory)
                    symlink_directories.append(candidate)
            for candidate in symlink_directories:
                yield candidate
            for filename in filenames:
                yield Path(root) / filename


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
    seen_hashes = set()
    # Stop the filesystem walk after one overflow candidate so discovery stays bounded.
    candidates = itertools.chain(
        ((path, "past_output") for path in _iter_source_paths(past_paths)),
        ((path, "current_material") for path in _iter_source_paths(material_paths)),
    )
    for index, (path, source_role) in enumerate(candidates):
        if index >= max_files:
            records.append(_rejected(path, source_role, "max_files_exceeded"))
            break
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
        "counts": {"accepted": len(accepted), "rejected": len(rejected), "total": len(records)},
    }


def _ensure_directory(path: Path) -> bool:
    path = Path(path)

    def validate_components() -> bool:
        current = Path(path.anchor) if path.anchor else Path(".")
        for part in path.parts:
            if part == path.anchor:
                continue
            current = current / part
            try:
                component_stat = current.lstat()
            except FileNotFoundError:
                return True
            except OSError:
                return False
            if stat.S_ISLNK(component_stat.st_mode) or not stat.S_ISDIR(component_stat.st_mode):
                return False
        return True

    try:
        if not validate_components():
            return False
        path.mkdir(parents=True, exist_ok=True)
        return validate_components() and path.is_dir() and not path.is_symlink()
    except OSError:
        return False


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


def copy_approved_files(records: List[Dict], workspace: Path) -> List[Dict]:
    """Copy only accepted records into a collision-safe, role-separated intake area."""
    workspace = Path(workspace)
    accepted_records = [record for record in records if record.get("status", "accepted") == "accepted"]
    if not _ensure_directory(workspace):
        return [_copy_rejected(record, "workspace_unavailable") for record in accepted_records]
    intake = workspace / "00_intake"
    if not _ensure_directory(intake):
        return [_copy_rejected(record, "workspace_unavailable") for record in accepted_records]
    role_directories = {}
    for role in ("past_output", "current_material"):
        directory_name = "past" if role == "past_output" else "current"
        directory = intake / directory_name
        if not _ensure_directory(directory):
            return [_copy_rejected(record, "workspace_unavailable") for record in accepted_records]
        role_directories[role] = directory

    outcomes = []
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
            outcomes.append(_copy_rejected(record, stat_error))
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
        number = 1
        while True:
            candidate_name = name if number == 1 else _collision_name(name, number)
            destination = destination_directory / candidate_name
            try:
                descriptor = os.open(str(destination), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            except FileExistsError:
                number += 1
                continue
            except OSError:
                outcomes.append(_copy_rejected(record, "copy_failed"))
                descriptor = None
            if descriptor is None:
                break
            digest = hashlib.sha256()
            byte_count = 0
            try:
                with os.fdopen(descriptor, "wb") as destination_file:
                    descriptor = None
                    source_descriptor = _open_no_follow(source, os.O_RDONLY)
                    with os.fdopen(source_descriptor, "rb") as source_file:
                        for chunk in iter(lambda: source_file.read(1024 * 1024), b""):
                            digest.update(chunk)
                            byte_count += len(chunk)
                            destination_file.write(chunk)
                actual_hash = digest.hexdigest()
                if expected_hash and actual_hash != expected_hash:
                    destination.unlink(missing_ok=True)
                    outcomes.append(_copy_rejected(record, "source_hash_mismatch"))
                    break
                if expected_bytes is not None and byte_count != expected_bytes:
                    destination.unlink(missing_ok=True)
                    outcomes.append(_copy_rejected(record, "source_size_mismatch"))
                    break
            except (OSError, ValueError):
                if descriptor is not None:
                    try:
                        os.close(descriptor)
                    except OSError:
                        pass
                try:
                    destination.unlink()
                except OSError:
                    pass
                outcomes.append(_copy_rejected(record, "copy_failed"))
                break
            outcomes.append(
                {
                    "status": "copied",
                    "source_role": role,
                    "original_path": str(source),
                    "copied_path": str(destination),
                    "destination_path": str(destination),
                    "name": candidate_name,
                    "bytes": byte_count,
                    "sha256": actual_hash,
                }
            )
            break
    return outcomes
