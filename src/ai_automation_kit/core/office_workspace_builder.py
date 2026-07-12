from __future__ import annotations

import errno
import hashlib
import json
import os
import re
import secrets
import stat
import sys
import uuid
from datetime import datetime, timezone
from importlib import resources
from pathlib import Path
from typing import Dict, Optional

from ai_automation_kit.core.workflow_pack import load_bundled_pack


WORKSPACE_SCHEMA_VERSION = 1
MONTH_PERIOD_ID_RE = re.compile(r"^[0-9]{4}-(0[1-9]|1[0-2])$")
DAY_PERIOD_ID_RE = re.compile(r"^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$")
PUBLIC_FOLDERS = (
    "00_START_HERE",
    "01_APPROVED_PAST_OUTPUTS",
    "02_PAST_SUPPORTING_FILES",
    "03_CURRENT_INPUTS",
    "04_QUESTIONS",
    "05_DRAFTS",
    "06_APPROVED_OUTPUTS",
    "07_AUDIT",
)
PERIOD_FOLDERS = (
    "03_CURRENT_INPUTS",
    "04_QUESTIONS",
    "05_DRAFTS",
    "06_APPROVED_OUTPUTS",
)
SCRYPT_N = 2 ** 14
SCRYPT_R = 8
SCRYPT_P = 1
WORKSPACE_PLATFORM_ERROR = (
    "Phase 1A office workspace mutation requires macOS or Linux with "
    "race-resistant no-follow filesystem support. Use a local macOS/Linux "
    "Python environment; no workspace changes were made."
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _absolute_path(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(Path(path).expanduser())))


def _json_copy(value):
    return json.loads(json.dumps(value, ensure_ascii=False))


def _fsync_directory(path: Path) -> None:
    descriptor = _open_directory_fd(path)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def require_workspace_mutation_support() -> None:
    required_flags = (getattr(os, "O_NOFOLLOW", None), getattr(os, "O_DIRECTORY", None))
    dir_fd_functions = (os.open, os.stat, os.unlink, os.link)
    follow_symlink_functions = (os.stat, os.link)
    if (
        os.name != "posix"
        or not (sys.platform.startswith("darwin") or sys.platform.startswith("linux"))
        or any(flag is None for flag in required_flags)
        or any(function not in os.supports_dir_fd for function in dir_fd_functions)
        or any(function not in os.supports_follow_symlinks for function in follow_symlink_functions)
    ):
        raise RuntimeError(WORKSPACE_PLATFORM_ERROR)


def _no_follow_flag() -> int:
    flag = getattr(os, "O_NOFOLLOW", None)
    if flag is None:
        raise RuntimeError(WORKSPACE_PLATFORM_ERROR)
    return flag


def _open_directory_fd(path: Path) -> int:
    absolute = _absolute_path(path)
    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | _no_follow_flag()
    descriptor = os.open(absolute.anchor, directory_flags)
    try:
        for component in absolute.parts:
            if component == absolute.anchor:
                continue
            next_descriptor = os.open(component, directory_flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = next_descriptor
        return descriptor
    except OSError as error:
        os.close(descriptor)
        if error.errno in {errno.ELOOP, errno.ENOTDIR}:
            raise ValueError("workspace path cannot use symlinked or non-directory components") from error
        raise


def _open_file_no_follow(path: Path, flags: int, label: str, mode: int = 0o600) -> int:
    absolute = _absolute_path(path)
    parent_descriptor = _open_directory_fd(absolute.parent)
    try:
        try:
            descriptor = os.open(absolute.name, flags | _no_follow_flag(), mode, dir_fd=parent_descriptor)
        except OSError as error:
            if error.errno == errno.ELOOP:
                raise ValueError("{} cannot be a symlink".format(label)) from error
            raise
    finally:
        os.close(parent_descriptor)
    file_stat = os.fstat(descriptor)
    if not stat.S_ISREG(file_stat.st_mode):
        os.close(descriptor)
        raise ValueError("{} must be a regular file".format(label))
    return descriptor


def _write_all(descriptor: int, payload: bytes) -> None:
    view = memoryview(payload)
    while view:
        written = os.write(descriptor, view)
        if written <= 0:
            raise OSError("short write while storing workspace data")
        view = view[written:]


def _entry_identity(parent_descriptor: int, name: str, label: str):
    try:
        file_stat = os.stat(name, dir_fd=parent_descriptor, follow_symlinks=False)
    except FileNotFoundError:
        return None
    if stat.S_ISLNK(file_stat.st_mode):
        raise ValueError("{} cannot be a symlink".format(label))
    if not stat.S_ISREG(file_stat.st_mode):
        raise ValueError("{} must be a regular file".format(label))
    return file_stat.st_dev, file_stat.st_ino


def _write_bytes_atomic(path: Path, payload: bytes) -> None:
    absolute = _absolute_path(path)
    parent_descriptor = _open_directory_fd(absolute.parent)
    temporary_name = ".{}.{}.tmp".format(absolute.name, secrets.token_hex(8))
    initial_identity = _entry_identity(parent_descriptor, absolute.name, str(absolute))
    temporary_descriptor = None
    try:
        temporary_descriptor = os.open(
            temporary_name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | _no_follow_flag(),
            0o600,
            dir_fd=parent_descriptor,
        )
        _write_all(temporary_descriptor, payload)
        os.fsync(temporary_descriptor)
        os.close(temporary_descriptor)
        temporary_descriptor = None
        if _entry_identity(parent_descriptor, absolute.name, str(absolute)) != initial_identity:
            raise ValueError("{} changed during atomic write".format(absolute))
        os.replace(
            temporary_name,
            absolute.name,
            src_dir_fd=parent_descriptor,
            dst_dir_fd=parent_descriptor,
        )
        os.fsync(parent_descriptor)
    finally:
        if temporary_descriptor is not None:
            os.close(temporary_descriptor)
        try:
            os.unlink(temporary_name, dir_fd=parent_descriptor)
        except FileNotFoundError:
            pass
        os.close(parent_descriptor)


def _write_text_atomic(path: Path, content: str) -> None:
    _write_bytes_atomic(path, content.encode("utf-8"))


def _write_json_atomic(path: Path, payload: Dict) -> None:
    _write_text_atomic(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def _append_jsonl(path: Path, payload: Dict) -> None:
    absolute = _absolute_path(path)
    line = json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n"
    descriptor = _open_file_no_follow(
        absolute,
        os.O_WRONLY | os.O_APPEND | os.O_CREAT,
        str(absolute),
    )
    try:
        _write_all(descriptor, line.encode("utf-8"))
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    _fsync_directory(absolute.parent)


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _read_bytes_no_follow(path: Path, label: str = "file") -> bytes:
    descriptor = _open_file_no_follow(path, os.O_RDONLY, label)
    try:
        with os.fdopen(descriptor, "rb") as handle:
            return handle.read()
    except Exception:
        try:
            os.close(descriptor)
        except OSError:
            pass
        raise


def _read_text_no_follow(path: Path, label: str = "file") -> str:
    try:
        return _read_bytes_no_follow(path, label).decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("{} must contain UTF-8 text".format(label)) from error


def _sha256_file(path: Path, label: str = "file") -> str:
    digest = hashlib.sha256()
    descriptor = _open_file_no_follow(path, os.O_RDONLY, label)
    with os.fdopen(descriptor, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_bytes_collision_safe(path: Path, payload: bytes) -> Path:
    absolute = _absolute_path(path)
    parent_descriptor = _open_directory_fd(absolute.parent)
    temporary_name = ".{}.{}.tmp".format(absolute.name, secrets.token_hex(8))
    temporary_descriptor = None
    number = 1
    try:
        while True:
            name = absolute.name if number == 1 else _collision_name(absolute.name, number)
            if _entry_identity(parent_descriptor, name, str(absolute.with_name(name))) is None:
                break
            number += 1

        temporary_descriptor = os.open(
            temporary_name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | _no_follow_flag(),
            0o600,
            dir_fd=parent_descriptor,
        )
        _write_all(temporary_descriptor, payload)
        os.fsync(temporary_descriptor)
        os.close(temporary_descriptor)
        temporary_descriptor = None

        while True:
            name = absolute.name if number == 1 else _collision_name(absolute.name, number)
            try:
                os.link(
                    temporary_name,
                    name,
                    src_dir_fd=parent_descriptor,
                    dst_dir_fd=parent_descriptor,
                    follow_symlinks=False,
                )
            except FileExistsError:
                _entry_identity(parent_descriptor, name, str(absolute.with_name(name)))
                number += 1
                continue
            os.fsync(parent_descriptor)
            return absolute.with_name(name)
    finally:
        if temporary_descriptor is not None:
            os.close(temporary_descriptor)
        try:
            os.unlink(temporary_name, dir_fd=parent_descriptor)
            os.fsync(parent_descriptor)
        except FileNotFoundError:
            pass
        os.close(parent_descriptor)


def _sanitize_workspace_name(name: str) -> str:
    candidate = re.sub(r"[^A-Za-z0-9._-]+", "_", name.strip())
    candidate = candidate.strip("._")
    return candidate or "office_workspace"


def _collision_name(name: str, number: int) -> str:
    path = Path(name)
    suffix = path.suffix
    stem = path.name[: -len(suffix)] if suffix else path.name
    return "{}__{}{}".format(stem, number, suffix)


def _collision_safe_path(path: Path) -> Path:
    if not path.exists():
        return path
    number = 2
    while True:
        candidate = path.with_name(_collision_name(path.name, number))
        if not candidate.exists():
            return candidate
        number += 1


def _path_uses_symlink(path: Path) -> bool:
    absolute = _absolute_path(path)
    return Path(os.path.realpath(os.fspath(absolute))) != absolute


def _ensure_existing_directory(path: Path, label: str) -> Path:
    absolute = _absolute_path(path)
    if _path_uses_symlink(absolute):
        raise ValueError("{} cannot use symlinked paths".format(label))
    try:
        mode = os.lstat(os.fspath(absolute)).st_mode
    except OSError as error:
        raise ValueError("{} is missing".format(label)) from error
    if not os.path.isdir(os.fspath(absolute)):
        raise ValueError("{} must be a directory".format(label))
    if os.path.islink(os.fspath(absolute)) or not os.path.isdir(os.fspath(absolute)):
        raise ValueError("{} cannot be a symlink".format(label))
    return absolute


def _ensure_existing_file(path: Path, label: str) -> Path:
    absolute = _absolute_path(path)
    try:
        descriptor = _open_file_no_follow(absolute, os.O_RDONLY, label)
    except OSError as error:
        raise ValueError("{} is missing".format(label)) from error
    os.close(descriptor)
    return absolute


def _workspace_root(parent: Path, name: str) -> Path:
    parent_directory = _ensure_existing_directory(parent, "workspace parent")
    root = parent_directory / _sanitize_workspace_name(name)
    return _collision_safe_path(root)


def _read_manifest() -> Dict:
    manifest_path = resources.files("ai_automation_kit").joinpath("packs", "manifest.json")
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def _pack_manifest_entry(pack_id: str) -> Dict:
    manifest = _read_manifest()
    entry = manifest.get(pack_id)
    if not isinstance(entry, dict):
        raise ValueError("unknown workflow pack: {}".format(pack_id))
    return _json_copy(entry)


def _pin_material(pin: str) -> Dict[str, str]:
    if not isinstance(pin, str) or not re.fullmatch(r"[0-9]{6,32}", pin):
        raise ValueError("pin must contain 6 to 32 digits")
    salt = secrets.token_bytes(16)
    pin_hash = _derive_scrypt_hex(pin, salt)
    return {"pin_salt": salt.hex(), "pin_hash": pin_hash}


def _derive_scrypt_hex(pin: str, salt: bytes) -> str:
    if hasattr(hashlib, "scrypt"):
        return hashlib.scrypt(pin.encode("utf-8"), salt=salt, n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P).hex()
    scrypt_class = _load_in_process_scrypt()
    if scrypt_class is None:
        raise RuntimeError(
            "PIN hashing is unavailable. Use a macOS/Linux Python runtime with hashlib.scrypt support."
        )
    try:
        derived = scrypt_class(
            salt=salt,
            length=64,
            n=SCRYPT_N,
            r=SCRYPT_R,
            p=SCRYPT_P,
        ).derive(pin.encode("utf-8"))
    except Exception:
        raise RuntimeError("PIN hashing failed in the in-process scrypt provider") from None
    if not isinstance(derived, bytes) or len(derived) != 64:
        raise RuntimeError("PIN hashing returned an invalid result")
    return derived.hex()


def _load_in_process_scrypt():
    try:
        from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
    except ImportError:
        return None
    return Scrypt


def _workspace_status_payload(state: Dict) -> Dict:
    return {
        "name": state["name"],
        "workspace_id": state["workspace_id"],
        "pack_id": state["pack_id"],
        "language": state["language"],
        "current_period": state["current_period"],
        "periods": list(state["periods"]),
        "updated_at": state["updated_at"],
    }


def _update_workspace_status(root: Path, state: Dict) -> None:
    _write_json_atomic(root / "00_START_HERE" / "workspace_status.json", _workspace_status_payload(state))


def validate_workspace_root(workspace: Path) -> Path:
    require_workspace_mutation_support()
    root = _ensure_existing_directory(workspace, "workspace")
    for folder in PUBLIC_FOLDERS:
        _ensure_existing_directory(root / folder, folder)
    _ensure_existing_directory(root / ".system", ".system")
    _ensure_existing_file(root / ".system" / "workspace.json", ".system/workspace.json")
    _ensure_existing_file(root / ".system" / "pack-manifest.json", ".system/pack-manifest.json")
    return root


def validate_period_id(period_id: str, period_type: Optional[str] = None) -> str:
    if period_type not in {None, "month", "day"}:
        raise ValueError("period_type must be 'month' or 'day'")
    if not isinstance(period_id, str):
        expected = "YYYY-MM-DD" if period_type == "day" else "YYYY-MM"
        raise ValueError("period_id must match strict {} format".format(expected))

    if period_type in {None, "month"} and MONTH_PERIOD_ID_RE.fullmatch(period_id):
        return period_id
    if period_type in {None, "day"} and DAY_PERIOD_ID_RE.fullmatch(period_id):
        try:
            datetime.strptime(period_id, "%Y-%m-%d")
        except ValueError:
            pass
        else:
            return period_id

    expected = "YYYY-MM-DD" if period_type == "day" else "YYYY-MM"
    if period_type is None:
        expected = "YYYY-MM or YYYY-MM-DD"
    raise ValueError("period_id must match strict {} format".format(expected))


def create_office_workspace(
    parent: Path,
    *,
    name: str,
    approver: str,
    pin: str,
    language: str = "ja",
    pack_id: str = "monthly-report",
) -> Path:
    require_workspace_mutation_support()
    if not isinstance(name, str) or not name.strip():
        raise ValueError("name must be a non-empty string")
    if not isinstance(approver, str) or not approver.strip():
        raise ValueError("approver must be a non-empty string")
    if language not in {"ja", "en"}:
        raise ValueError("language must be 'ja' or 'en'")

    pack = load_bundled_pack(pack_id)
    manifest_entry = _pack_manifest_entry(pack_id)
    root = _workspace_root(parent, name)
    root.mkdir(mode=0o700, parents=True, exist_ok=False)
    try:
        for folder in PUBLIC_FOLDERS:
            (root / folder).mkdir(mode=0o700)
        (root / ".system").mkdir(mode=0o700)
        (root / ".system" / "periods").mkdir(mode=0o700)
        start_here = root / "00_START_HERE" / "open_this_first.html"
        _write_text_atomic(
            start_here,
            "<!doctype html><html><body><h1>Office Workspace</h1><p>Use the operator UI to continue.</p></body></html>\n",
        )

        timestamp = _utc_now()
        pin_material = _pin_material(pin)
        workspace_state = {
            "schema_version": WORKSPACE_SCHEMA_VERSION,
            "workspace_id": uuid.uuid4().hex,
            "name": name.strip(),
            "root": str(root),
            "language": language,
            "pack_id": pack["id"],
            "created_at": timestamp,
            "updated_at": timestamp,
            "current_period": None,
            "periods": [],
            "approval": {
                "approver": approver.strip(),
                "pin_salt": pin_material["pin_salt"],
                "pin_hash": pin_material["pin_hash"],
                "kdf": {"name": "scrypt", "n": SCRYPT_N, "r": SCRYPT_R, "p": SCRYPT_P},
            },
            "pack_manifest": {
                "pack_id": pack_id,
                "pack_file": manifest_entry["pack_file"],
                "pack_sha256": manifest_entry["pack_sha256"],
                "output_schema_file": manifest_entry["output_schema_file"],
                "output_schema_sha256": manifest_entry["output_schema_sha256"],
            },
        }
        _write_json_atomic(root / ".system" / "workspace.json", workspace_state)
        _write_json_atomic(root / ".system" / "pack-manifest.json", workspace_state["pack_manifest"])
        _update_workspace_status(root, workspace_state)
        return root
    except Exception:
        if root.exists():
            for child in sorted(root.glob("**/*"), reverse=True):
                if child.is_file() or child.is_symlink():
                    child.unlink()
                elif child.is_dir():
                    child.rmdir()
            root.rmdir()
        raise


__all__ = [
    "PUBLIC_FOLDERS",
    "PERIOD_FOLDERS",
    "SCRYPT_N",
    "SCRYPT_P",
    "SCRYPT_R",
    "WORKSPACE_SCHEMA_VERSION",
    "create_office_workspace",
    "validate_period_id",
    "validate_workspace_root",
]
