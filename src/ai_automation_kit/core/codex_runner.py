from __future__ import annotations

import ctypes
import errno
import hashlib
import json
import os
import re
import shutil
import signal
import stat
import struct
import subprocess
import sys
import threading
import time
import uuid
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ai_automation_kit.core.office_workspace_builder import (
    _append_jsonl,
    _entry_identity,
    _json_copy,
    _no_follow_flag,
    _open_directory_fd,
    _read_bytes_no_follow,
    _read_text_no_follow,
    _sha256_file,
    _utc_now,
    _write_all,
    _write_bytes_collision_safe,
    _write_json_atomic,
    _write_text_atomic,
    validate_period_id,
    validate_workspace_root,
)
from ai_automation_kit.core.office_workspace_state import (
    _load_period_state,
    _load_workspace_state,
    _save_period_state,
    _transition_period,
    _validated_style_reference,
    promote_run_result,
)
from ai_automation_kit.core.report_intake import MAX_FILE_BYTES
from ai_automation_kit.core.workflow_pack import (
    load_bundled_output_schema,
    load_bundled_pack,
    load_bundled_prompt_template,
)


RUN_METADATA_SCHEMA_VERSION = 2
COMMAND_VERSION = 1
RUN_LOCK_NAME = "codex-run.lock"
RUN_ID_RE = re.compile(r"^run-[0-9a-f]{32}$")
MIN_RUN_TIMEOUT_SECONDS = 60
MAX_RUN_TIMEOUT_SECONDS = 1800
DEFAULT_RUN_TIMEOUT_SECONDS = 900
CANCEL_GRACE_SECONDS = 5.0
WAIT_POLL_SECONDS = 0.05
MAX_EVENT_LINE_BYTES = 65536
MAX_EVENT_LINES = 1000
MAX_MISSING_QUESTIONS = 20
MAX_MISSING_QUESTION_CHARS = 500
MAX_RESULT_JSON_BYTES = MAX_FILE_BYTES
MAX_PROMPT_BYTES = 65536
ACCEPTED_EXTRACTION_STATUSES = frozenset(
    {"extracted", "metadata_only", "optional_isolation_unavailable", "optional_reader_missing"}
)
FINAL_STATUSES = {"questioning", "ready_for_review", "failed", "cancelled"}
ERROR_CATEGORIES = {
    "cancelled": "cancellation",
    "run_timeout": "timeout",
    "invalid_event_stream": "validation",
    "codex_exec_failed": "process",
    "invalid_result_json": "validation",
    "invalid_result_payload": "validation",
    "unsafe_output_staging": "validation",
    "promotion_failed": "promotion",
    "runner_internal_error": "internal",
    "runner_restarted": "recovery",
    "orphan_recovered": "recovery",
    "manual_recovery_completed": "recovery",
    "prompt_delivery_failed": "process",
}
SAFE_EVENT_NAMES = frozenset(
    {
        "error",
        "item.completed",
        "item.started",
        "item.updated",
        "run.finished",
        "run.started",
        "thread.started",
        "turn.completed",
        "turn.failed",
        "turn.started",
    }
)
SAFE_EVENT_STATUS_VALUES = frozenset(
    {"cancelled", "canceled", "completed", "failed", "in_progress", "pending", "queued", "running"}
)
SAFE_EVENT_PHASE_VALUES = frozenset({"executing", "finalizing", "preparing"})
CODEX_ENV_ALLOWLIST = (
    "HOME",
    "CODEX_HOME",
    "PATH",
    "LANG",
    "LC_ALL",
    "LC_CTYPE",
    "TMPDIR",
    "TEMP",
    "TMP",
    "XDG_CONFIG_HOME",
)

_REGISTRY_LOCK = threading.RLock()
_RECOVERY_LOCK = threading.RLock()
_RUN_REGISTRY: Dict[Tuple[str, str], "_ActiveRun"] = {}


class _DarwinProcBSDInfo(ctypes.Structure):
    _fields_ = [
        ("pbi_flags", ctypes.c_uint32),
        ("pbi_status", ctypes.c_uint32),
        ("pbi_xstatus", ctypes.c_uint32),
        ("pbi_pid", ctypes.c_uint32),
        ("pbi_ppid", ctypes.c_uint32),
        ("pbi_uid", ctypes.c_uint32),
        ("pbi_gid", ctypes.c_uint32),
        ("pbi_ruid", ctypes.c_uint32),
        ("pbi_rgid", ctypes.c_uint32),
        ("pbi_svuid", ctypes.c_uint32),
        ("pbi_svgid", ctypes.c_uint32),
        ("rfu_1", ctypes.c_uint32),
        ("pbi_comm", ctypes.c_char * 16),
        ("pbi_name", ctypes.c_char * 32),
        ("pbi_nfiles", ctypes.c_uint32),
        ("pbi_pgid", ctypes.c_uint32),
        ("pbi_pjobc", ctypes.c_uint32),
        ("e_tdev", ctypes.c_uint32),
        ("e_tpgid", ctypes.c_uint32),
        ("pbi_nice", ctypes.c_int32),
        ("pbi_start_tvsec", ctypes.c_uint64),
        ("pbi_start_tvusec", ctypes.c_uint64),
    ]


def codex_preflight(executable: str = "codex", timeout_seconds: int = 5) -> Dict:
    if not isinstance(timeout_seconds, int) or timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be a positive integer")
    try:
        completed = subprocess.run(
            [executable, "login", "status"],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
            env=_minimal_codex_environment(),
        )
    except FileNotFoundError:
        return {"ok": False, "code": "codex_unavailable", "next_action": "Install Codex CLI and retry"}
    except PermissionError:
        return {"ok": False, "code": "codex_unavailable", "next_action": "Check Codex CLI permissions and retry"}
    except subprocess.TimeoutExpired:
        return {"ok": False, "code": "codex_preflight_timeout", "next_action": "Retry after Codex responds"}

    if completed.returncode != 0:
        return {"ok": False, "code": "codex_not_logged_in", "next_action": "Run codex login"}
    return {"ok": True, "code": "ok", "next_action": None}


def start_codex_run(
    workspace: Path,
    period_id: str,
    *,
    executable: str = "codex",
    timeout_seconds: int = DEFAULT_RUN_TIMEOUT_SECONDS,
) -> Dict:
    if not isinstance(timeout_seconds, int) or not (MIN_RUN_TIMEOUT_SECONDS <= timeout_seconds <= MAX_RUN_TIMEOUT_SECONDS):
        raise ValueError(
            "timeout_seconds must be between {} to {} seconds".format(
                MIN_RUN_TIMEOUT_SECONDS, MAX_RUN_TIMEOUT_SECONDS
            )
        )

    root = validate_workspace_root(workspace)
    period_id = validate_period_id(period_id)
    _reconcile_workspace_runs(root)
    workspace_state = _load_workspace_state(root)
    period_state = _load_period_state(root, period_id)
    if period_state["stage"] != "ready_for_run":
        raise ValueError("start_codex_run requires ready_for_run stage")

    pack = load_bundled_pack(workspace_state["pack_id"])
    load_bundled_output_schema(pack["id"])
    prompt_template = load_bundled_prompt_template(pack["id"])
    accepted_records, source_manifest_hash = _load_verified_accepted_records(root, period_id, period_state)
    style_record = _verified_style_reference_record(root, period_id, period_state)
    if style_record is not None:
        accepted_records.append(style_record)
    run_id = _new_run_id(root / ".system" / "runs")
    run_root = root / ".system" / "runs" / run_id
    sandbox = run_root / "sandbox"
    input_snapshot = sandbox / "input_snapshot"
    output_staging = run_root / "output_staging"
    events_path = run_root / "events.jsonl"
    final_output_path = output_staging / "final.json"

    lock = _acquire_run_lock(root, run_id)
    process = None
    try:
        run_root.mkdir(mode=0o700, parents=True, exist_ok=False)
        sandbox.mkdir(mode=0o700)
        input_snapshot.mkdir(mode=0o700)
        output_staging.mkdir(mode=0o700)
        _write_text_atomic(events_path, "")

        snapshot_manifest = _snapshot_sources(input_snapshot, accepted_records, root, period_id)
        snapshot_manifest_hash = _sha256_file(input_snapshot / "source_manifest.json", "snapshot source manifest")
        prompt = _build_prompt(
            prompt_template=prompt_template,
            period_id=period_id,
            answers=period_state["answers"],
            snapshot_manifest=snapshot_manifest,
        )
        prompt_bytes = prompt.encode("utf-8")
        schema_path = _pack_schema_path(workspace_state["pack_manifest"]["output_schema_file"])
        command = [
            executable,
            "exec",
            "--cd",
            str(sandbox),
            "--sandbox",
            "workspace-write",
            "--json",
            "--output-schema",
            str(schema_path),
            "--output-last-message",
            str(final_output_path),
            "--skip-git-repo-check",
            "-",
        ]
        host_start_token = _process_start_token(os.getpid())
        launch_marker = _launch_marker_template(
            workspace_state=workspace_state,
            period_id=period_id,
            run_id=run_id,
            run_root=run_root,
            sandbox=sandbox,
            input_snapshot=input_snapshot,
            output_staging=output_staging,
            final_output_path=final_output_path,
            command=command,
            executable=executable,
            host_start_token=host_start_token,
        )
        _write_json_atomic(_launch_state_path(root, run_id), launch_marker)

        try:
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True,
                env=_minimal_codex_environment(),
            )
        except FileNotFoundError as error:
            raise ValueError("Codex executable is unavailable") from error
        except PermissionError as error:
            raise ValueError("Codex executable is not runnable") from error

        _after_popen(process)
        process_identity = _capture_process_identity(process.pid)

        _rewrite_run_lock(lock, run_id=run_id, pid=process.pid)

        period_state = _load_period_state(root, period_id)
        if period_state["stage"] != "ready_for_run":
            raise ValueError("period state changed before the run could start")
        _transition_period(period_state, "running")
        _save_period_state(root, period_state)

        record = _run_record_template(
            workspace=root,
            workspace_state=workspace_state,
            period_id=period_id,
            run_id=run_id,
            timeout_seconds=timeout_seconds,
            command=command[1:],
            pid=process.pid,
            process_identity=process_identity,
            host_start_token=host_start_token,
            prompt_bytes=len(prompt_bytes),
            prompt_sha256=hashlib.sha256(prompt_bytes).hexdigest(),
            source_manifest_hash=source_manifest_hash,
            snapshot_manifest_hash=snapshot_manifest_hash,
            input_snapshot=input_snapshot,
            sandbox=sandbox,
            output_staging=output_staging,
            events_path=events_path,
            final_output_path=final_output_path,
            pack=pack,
        )
        _write_json_atomic(run_root / "run.json", record)
        _remove_launch_marker(root, run_id)

        active = _ActiveRun(
            workspace=root,
            period_id=period_id,
            run_id=run_id,
            run_root=run_root,
            process=process,
            lock=lock,
            record=record,
            record_lock=threading.RLock(),
        )
        active.waiter = threading.Thread(target=_wait_for_process, args=(active, pack), daemon=True)
        active.stdin_writer = threading.Thread(target=_write_prompt, args=(active, prompt), daemon=True)
        with _REGISTRY_LOCK:
            _RUN_REGISTRY[(str(root), run_id)] = active
        _start_stream_threads(active)
        _before_prompt_writer(active)
        active.stdin_writer.start()
        active.waiter.start()
        return _json_copy(record)
    except Exception:
        if process is not None and process.poll() is None:
            _terminate_process_group(process.pid, force=True)
            try:
                process.wait(timeout=2.0)
            except Exception:
                pass
        with _REGISTRY_LOCK:
            _RUN_REGISTRY.pop((str(root), run_id), None)
        try:
            _mark_period_terminal(root, period_id, "failed")
        except Exception:
            pass
        _remove_launch_marker(root, run_id)
        _release_run_lock(lock)
        raise


def run_status(workspace: Path, run_id: str) -> Dict:
    root = validate_workspace_root(workspace)
    run_id = _validate_run_id(run_id)
    path = _run_state_path(root, run_id)
    if path.exists():
        _reconcile_run(root, run_id)
        return _load_json_object(path, "run metadata")
    launch_path = _launch_state_path(root, run_id)
    if launch_path.exists():
        return _reconcile_launch_marker(root, run_id)
    raise ValueError("run_id does not exist")


def cancel_run(workspace: Path, run_id: str) -> Dict:
    root = validate_workspace_root(workspace)
    run_id = _validate_run_id(run_id)
    with _REGISTRY_LOCK:
        active = _RUN_REGISTRY.get((str(root), run_id))
    if active is None:
        return run_status(root, run_id)

    with active.record_lock:
        if active.record["status"] in FINAL_STATUSES:
            return _json_copy(active.record)
        active.cancel_requested = True
        active.record["status"] = "cancelling"
        active.record["cancel_requested_at"] = _utc_now()
        _persist_record(active)
        return _json_copy(active.record)


def wait_for_run(workspace: Path, run_id: str, timeout_seconds: int) -> Dict:
    root = validate_workspace_root(workspace)
    run_id = _validate_run_id(run_id)
    if not isinstance(timeout_seconds, int) or timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be a positive integer")
    with _REGISTRY_LOCK:
        active = _RUN_REGISTRY.get((str(root), run_id))
    if active is None:
        return run_status(root, run_id)
    active.waiter.join(timeout_seconds)
    if active.waiter.is_alive():
        raise TimeoutError("run {} did not finish within {} seconds".format(run_id, timeout_seconds))
    return run_status(root, run_id)


@dataclass
class _RunLock:
    root: Path
    system_descriptor: int
    descriptor: int
    identity: Tuple[int, int]
    released: bool = False


@dataclass
class _ActiveRun:
    workspace: Path
    period_id: str
    run_id: str
    run_root: Path
    process: subprocess.Popen
    lock: _RunLock
    record: Dict
    record_lock: threading.RLock
    cancel_requested: bool = False
    stdout_events: List[Dict] = field(default_factory=list)
    stdout_invalid: bool = False
    stderr_bytes: int = 0
    stderr_digest: Any = field(default_factory=hashlib.sha256)
    waiter: Optional[threading.Thread] = None
    stdout_reader: Optional[threading.Thread] = None
    stderr_reader: Optional[threading.Thread] = None
    stdin_writer: Optional[threading.Thread] = None
    prompt_writer_done: threading.Event = field(default_factory=threading.Event)
    prompt_delivered: bool = False


def _start_stream_threads(active: _ActiveRun) -> None:
    active.stdout_reader = threading.Thread(target=_read_stdout_events, args=(active,), daemon=True)
    active.stderr_reader = threading.Thread(target=_read_stderr_metadata, args=(active,), daemon=True)
    active.stdout_reader.start()
    active.stderr_reader.start()


def _read_stdout_events(active: _ActiveRun) -> None:
    stream = active.process.stdout
    if stream is None:
        active.stdout_invalid = True
        return
    line_number = 0
    while True:
        raw_line = stream.readline(MAX_EVENT_LINE_BYTES + 1)
        if not raw_line:
            return
        if len(raw_line) > MAX_EVENT_LINE_BYTES and not raw_line.endswith(b"\n"):
            active.stdout_invalid = True
            _drain_line(stream)
            continue
        line_number += 1
        if line_number > MAX_EVENT_LINES:
            active.stdout_invalid = True
            continue
        try:
            text = raw_line.decode("utf-8")
        except UnicodeDecodeError:
            active.stdout_invalid = True
            continue
        if not text.strip():
            continue
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            active.stdout_invalid = True
            continue
        sanitized = _sanitize_event(payload, line_number)
        if sanitized is None:
            active.stdout_invalid = True
            continue
        active.stdout_events.append(sanitized)


def _read_stderr_metadata(active: _ActiveRun) -> None:
    stream = active.process.stderr
    if stream is None:
        return
    while True:
        chunk = stream.read(4096)
        if not chunk:
            return
        active.stderr_bytes += len(chunk)
        active.stderr_digest.update(chunk)


def _wait_for_process(active: _ActiveRun, pack: Dict) -> None:
    process = active.process
    deadline = time.time() + int(active.record["timeout_seconds"])
    termination_reason = None
    termination_deadline = None
    try:
        while True:
            return_code = process.poll()
            if return_code is not None:
                break
            if active.cancel_requested and termination_reason is None:
                termination_reason = "cancelled"
                termination_deadline = time.time() + CANCEL_GRACE_SECONDS
                _terminate_process_group(process.pid, force=False)
            elif termination_reason is None and time.time() >= deadline:
                termination_reason = "run_timeout"
                termination_deadline = time.time() + CANCEL_GRACE_SECONDS
                _terminate_process_group(process.pid, force=False)
            elif termination_reason is not None and termination_deadline is not None and time.time() >= termination_deadline:
                _terminate_process_group(process.pid, force=True)
                termination_deadline = None
            time.sleep(WAIT_POLL_SECONDS)

        if active.stdout_reader is not None:
            active.stdout_reader.join(2.0)
        if active.stderr_reader is not None:
            active.stderr_reader.join(2.0)
        if active.stdin_writer is not None:
            active.stdin_writer.join(2.0)
        for event in active.stdout_events:
            _append_jsonl(_events_path(active.run_root), event)
        _finalize_run(active, pack, termination_reason)
    except Exception:
        try:
            _mark_period_terminal(active.workspace, active.period_id, "failed")
            _update_final_record(active, status="failed", error_code="runner_internal_error", exit_code=process.poll())
        except Exception:
            pass
    finally:
        with _REGISTRY_LOCK:
            _RUN_REGISTRY.pop((str(active.workspace), active.run_id), None)
        _release_run_lock(active.lock)


def _finalize_run(active: _ActiveRun, pack: Dict, termination_reason: Optional[str]) -> None:
    return_code = active.process.poll()
    if termination_reason == "cancelled":
        _mark_period_terminal(active.workspace, active.period_id, "cancelled")
        _update_final_record(active, status="cancelled", error_code="cancelled", exit_code=return_code)
        return
    if termination_reason == "run_timeout":
        _mark_period_terminal(active.workspace, active.period_id, "failed")
        _update_final_record(active, status="failed", error_code="run_timeout", exit_code=return_code)
        return
    if not active.prompt_writer_done.is_set() or not active.prompt_delivered:
        _restore_period_retryable(active.workspace, active.period_id)
        _update_final_record(active, status="failed", error_code="prompt_delivery_failed", exit_code=return_code)
        return
    if active.stdout_invalid:
        _mark_period_terminal(active.workspace, active.period_id, "failed")
        _update_final_record(active, status="failed", error_code="invalid_event_stream", exit_code=return_code)
        return
    if return_code != 0:
        _mark_period_terminal(active.workspace, active.period_id, "failed")
        _update_final_record(active, status="failed", error_code="codex_exec_failed", exit_code=return_code)
        return

    try:
        result = _load_validated_result(active.run_root, pack)
    except ValueError as error:
        _mark_period_terminal(active.workspace, active.period_id, "failed")
        _update_final_record(
            active,
            status="failed",
            error_code=str(error),
            exit_code=return_code,
        )
        return

    try:
        promoted = promote_run_result(active.workspace, active.period_id, active.run_id, result)
    except Exception:
        _mark_period_terminal(active.workspace, active.period_id, "failed")
        _update_final_record(active, status="failed", error_code="promotion_failed", exit_code=return_code)
        return

    _update_final_record(
        active,
        status=promoted["stage"],
        error_code=None,
        exit_code=return_code,
        promoted_stage=promoted["stage"],
    )


def _load_validated_result(run_root: Path, pack: Dict) -> Dict:
    final_output = _validate_output_staging(run_root / "output_staging")
    if final_output.stat().st_size > MAX_RESULT_JSON_BYTES:
        raise ValueError("invalid_result_payload")
    try:
        payload = json.loads(_read_text_no_follow(final_output, "Codex final output"))
    except json.JSONDecodeError as error:
        raise ValueError("invalid_result_json") from error
    except ValueError as error:
        raise ValueError("invalid_result_json") from error
    return _normalize_result_payload(payload, pack)


def _normalize_result_payload(payload: Any, pack: Dict) -> Dict:
    if not isinstance(payload, dict) or set(payload) != {"missing_questions", "draft_markdown"}:
        raise ValueError("invalid_result_payload")
    missing_questions = payload["missing_questions"]
    draft_markdown = payload["draft_markdown"]
    if not isinstance(missing_questions, list) or len(missing_questions) > MAX_MISSING_QUESTIONS:
        raise ValueError("invalid_result_payload")
    normalized_questions = []
    for item in missing_questions:
        if not isinstance(item, str):
            raise ValueError("invalid_result_payload")
        stripped = item.strip()
        if not stripped or len(stripped) > MAX_MISSING_QUESTION_CHARS:
            raise ValueError("invalid_result_payload")
        normalized_questions.append(stripped)
    if not isinstance(draft_markdown, str):
        raise ValueError("invalid_result_payload")
    max_bytes = int(pack["outputs"][0]["max_bytes"])
    if len(draft_markdown.encode("utf-8")) > max_bytes:
        raise ValueError("invalid_result_payload")
    return {"missing_questions": normalized_questions, "draft_markdown": draft_markdown}


def _validate_output_staging(output_staging: Path) -> Path:
    entries = list(output_staging.iterdir())
    if len(entries) != 1 or entries[0].name != "final.json":
        raise ValueError("unsafe_output_staging")
    final_output = entries[0]
    file_stat = os.lstat(os.fspath(final_output))
    if not stat.S_ISREG(file_stat.st_mode) or stat.S_ISLNK(file_stat.st_mode) or file_stat.st_nlink != 1:
        raise ValueError("unsafe_output_staging")
    return final_output


def _run_record_template(
    *,
    workspace: Path,
    workspace_state: Dict,
    period_id: str,
    run_id: str,
    timeout_seconds: int,
    command: List[str],
    pid: int,
    process_identity: Dict,
    host_start_token: str,
    prompt_bytes: int,
    prompt_sha256: str,
    source_manifest_hash: str,
    snapshot_manifest_hash: str,
    input_snapshot: Path,
    sandbox: Path,
    output_staging: Path,
    events_path: Path,
    final_output_path: Path,
    pack: Dict,
) -> Dict:
    return {
        "schema_version": RUN_METADATA_SCHEMA_VERSION,
        "run_id": run_id,
        "workspace_id": workspace_state["workspace_id"],
        "period_id": period_id,
        "status": "running",
        "started_at": _utc_now(),
        "finished_at": None,
        "timeout_seconds": timeout_seconds,
        "pid": pid,
        "process_group_id": process_identity["process_group_id"],
        "session_id": process_identity["session_id"],
        "process_start_token": process_identity["process_start_token"],
        "executable_identity": process_identity["executable_identity"],
        "host_pid": os.getpid(),
        "host_start_token": host_start_token,
        "prompt_bytes": prompt_bytes,
        "prompt_sha256": prompt_sha256,
        "prompt_delivered": False,
        "command_version": COMMAND_VERSION,
        "command": command,
        "source_manifest_hash": source_manifest_hash,
        "snapshot_manifest_hash": snapshot_manifest_hash,
        "pack_id": pack["id"],
        "pack_hash": workspace_state["pack_manifest"]["pack_sha256"],
        "output_schema_hash": workspace_state["pack_manifest"]["output_schema_sha256"],
        "run_root": str(workspace / ".system" / "runs" / run_id),
        "input_snapshot": str(input_snapshot),
        "sandbox": str(sandbox),
        "output_staging": str(output_staging),
        "events_path": str(events_path),
        "final_output_path": str(final_output_path),
        "stderr_bytes": 0,
        "stderr_sha256": hashlib.sha256(b"").hexdigest(),
        "exit_code": None,
        "error_code": None,
        "error_category": None,
    }


def _update_final_record(
    active: _ActiveRun,
    *,
    status: str,
    error_code: Optional[str],
    exit_code: Optional[int],
    promoted_stage: Optional[str] = None,
) -> None:
    with active.record_lock:
        active.record["status"] = status
        active.record["finished_at"] = _utc_now()
        active.record["exit_code"] = exit_code
        active.record["stderr_bytes"] = active.stderr_bytes
        active.record["stderr_sha256"] = active.stderr_digest.hexdigest()
        active.record["prompt_delivered"] = active.prompt_delivered
        active.record["error_code"] = error_code
        active.record["error_category"] = _error_category(error_code)
        if promoted_stage is not None:
            active.record["promoted_stage"] = promoted_stage
        _persist_record(active)


def _persist_record(active: _ActiveRun) -> None:
    _write_json_atomic(_run_state_path(active.workspace, active.run_id), active.record)


def _mark_period_terminal(workspace: Path, period_id: str, terminal_stage: str) -> None:
    period_state = _load_period_state(workspace, period_id)
    if period_state["stage"] != "running":
        return
    _transition_period(period_state, terminal_stage)
    _save_period_state(workspace, period_state)


def _load_verified_accepted_records(workspace: Path, period_id: str, period_state: Dict) -> Tuple[List[Dict], str]:
    manifest_path = _source_manifest_disk_path(workspace, period_id)
    actual_hash = _sha256_file(manifest_path, "period source manifest")
    if actual_hash != period_state.get("source_manifest_hash"):
        raise ValueError("period source manifest hash no longer matches the recorded state")
    manifest = _load_json_object(manifest_path, "period source manifest")
    accepted = manifest.get("accepted")
    if not isinstance(accepted, list) or not accepted:
        raise ValueError("period source manifest does not contain accepted records")
    return accepted, actual_hash


def _verified_style_reference_record(workspace: Path, period_id: str, period_state: Dict) -> Optional[Dict]:
    style_reference = _validated_style_reference(
        workspace,
        period_id,
        period_state.get("style_reference"),
    )
    if style_reference is None:
        return None
    source = workspace / style_reference["relative_path"]
    payload = _read_bytes_no_follow(source, "style_reference")
    if len(payload) > MAX_FILE_BYTES:
        raise ValueError("style_reference exceeds the allowed file size")
    return {
        "source_role": "style_reference",
        "original_path": str(source),
        "name": source.name,
        "sha256": style_reference["sha256"],
        "bytes": len(payload),
        "extraction_status": "extracted",
    }


def _snapshot_sources(
    input_snapshot: Path,
    accepted_records: List[Dict],
    workspace: Path,
    period_id: str,
) -> Dict:
    snapshot_records = []
    for record in accepted_records:
        copied_path, workspace_relative_source = _copy_snapshot_record(
            input_snapshot, record, workspace, period_id
        )
        relative_path = copied_path.relative_to(input_snapshot).as_posix()
        snapshot_records.append(
            {
                "relative_path": "input_snapshot/{}".format(relative_path),
                "sha256": record["sha256"],
                "size": record["bytes"],
                "extraction_status": record["extraction_status"],
                "provenance": {
                    "source_role": record["source_role"],
                    "workspace_relative_path": workspace_relative_source,
                    "source_sha256": record["sha256"],
                },
            }
        )
    manifest = {
        "generated_at": _utc_now(),
        "records": snapshot_records,
    }
    _write_json_atomic(input_snapshot / "source_manifest.json", manifest)
    os.chmod(input_snapshot / "source_manifest.json", 0o444)
    return manifest


def _copy_snapshot_record(
    input_snapshot: Path,
    record: Dict,
    workspace: Path,
    period_id: str,
) -> Tuple[Path, str]:
    required = {"source_role", "original_path", "sha256", "bytes", "extraction_status"}
    if not isinstance(record, dict) or not required <= set(record):
        raise ValueError("accepted record is missing integrity metadata")
    source_role = record["source_role"]
    if source_role not in {"past_output", "past_supporting", "current_material", "style_reference"}:
        raise ValueError("accepted record source_role is invalid")
    if (
        not isinstance(record["extraction_status"], str)
        or record["extraction_status"] not in ACCEPTED_EXTRACTION_STATUSES
    ):
        raise ValueError("accepted record extraction_status is invalid")
    expected_hash = str(record["sha256"])
    expected_bytes = int(record["bytes"])
    if expected_bytes < 0 or expected_bytes > MAX_FILE_BYTES:
        raise ValueError("accepted record size is invalid")
    source = Path(str(record["original_path"]))
    workspace_relative_source = _validate_snapshot_source_path(
        source, source_role, workspace, period_id
    )
    payload = _read_bytes_no_follow(source, "snapshot source")
    if len(payload) != expected_bytes:
        raise ValueError("snapshot source hash mismatch")
    actual_hash = hashlib.sha256(payload).hexdigest()
    if actual_hash != expected_hash:
        raise ValueError("snapshot source hash mismatch")
    target_dir = input_snapshot / source_role
    target_dir.mkdir(mode=0o700, exist_ok=True)
    copied_path = _write_bytes_collision_safe(target_dir / _safe_snapshot_name(record.get("name", source.name)), payload)
    os.chmod(copied_path, 0o444)
    if copied_path.stat().st_size != expected_bytes or _sha256_file(copied_path, "snapshot copy") != expected_hash:
        raise ValueError("snapshot copy verification failed")
    return copied_path, workspace_relative_source


def _validate_snapshot_source_path(source: Path, source_role: str, workspace: Path, period_id: str) -> str:
    if not source.is_absolute() or ".." in source.parts:
        raise ValueError("snapshot source is outside the authorized source root")
    authorized_roots = {
        "past_output": workspace / "01_APPROVED_PAST_OUTPUTS",
        "past_supporting": workspace / "02_PAST_SUPPORTING_FILES",
        "current_material": workspace / "03_CURRENT_INPUTS" / period_id,
        "style_reference": workspace / "06_APPROVED_OUTPUTS",
    }
    authorized_root = authorized_roots.get(source_role)
    if authorized_root is None:
        raise ValueError("accepted record source_role is invalid")
    normalized_source = Path(os.path.abspath(os.fspath(source)))
    normalized_root = Path(os.path.abspath(os.fspath(authorized_root)))
    try:
        relative = normalized_source.relative_to(normalized_root)
    except ValueError as error:
        raise ValueError("snapshot source is outside the authorized source root") from error
    if not relative.parts:
        raise ValueError("snapshot source is outside the authorized source root")
    normalized_workspace = Path(os.path.abspath(os.fspath(workspace)))
    return normalized_source.relative_to(normalized_workspace).as_posix()


def _safe_snapshot_name(value: str) -> str:
    candidate = re.sub(r"[^A-Za-z0-9._-]+", "_", str(value)).strip("._")
    return candidate or "source.bin"


def _build_prompt(
    prompt_template: Dict,
    period_id: str,
    answers: Dict,
    snapshot_manifest: Dict,
) -> str:
    source_manifest = {"records": snapshot_manifest["records"]}
    variables = {
        "period_id": period_id,
        "source_manifest": json.dumps(source_manifest, ensure_ascii=False, indent=2, sort_keys=True),
        "answers": json.dumps(answers, ensure_ascii=False, indent=2, sort_keys=True),
    }
    if list(variables) != prompt_template["allowed_variables"]:
        raise ValueError("workflow prompt variables do not match the trusted template")
    prompt = prompt_template["template"].format(**variables)
    if len(prompt.encode("utf-8")) > MAX_PROMPT_BYTES:
        raise ValueError("rendered Codex prompt exceeds the allowed size")
    return prompt


def _write_prompt(active: _ActiveRun, prompt: str) -> None:
    stream = active.process.stdin
    if stream is None:
        active.prompt_writer_done.set()
        return
    payload = prompt.encode("utf-8")
    delivered = 0
    try:
        while delivered < len(payload):
            written = stream.write(payload[delivered:])
            if not isinstance(written, int) or written <= 0:
                return
            delivered += written
        stream.flush()
        stream.close()
        active.prompt_delivered = delivered == len(payload)
    except (BrokenPipeError, OSError, ValueError):
        try:
            stream.close()
        except (OSError, ValueError):
            pass
    finally:
        active.prompt_writer_done.set()


def _before_prompt_writer(active: _ActiveRun) -> None:
    return None


def _pack_schema_path(resource_name: str) -> Path:
    resource = resources.files("ai_automation_kit").joinpath("packs", resource_name)
    if hasattr(resource, "__fspath__"):
        return Path(os.fspath(resource))
    return Path(str(resource))


def _minimal_codex_environment() -> Dict[str, str]:
    environment = {
        key: os.environ[key]
        for key in CODEX_ENV_ALLOWLIST
        if key in os.environ
    }
    environment.setdefault("PATH", os.defpath)
    return environment


def _launch_marker_template(
    *,
    workspace_state: Dict,
    period_id: str,
    run_id: str,
    run_root: Path,
    sandbox: Path,
    input_snapshot: Path,
    output_staging: Path,
    final_output_path: Path,
    command: List[str],
    executable: str,
    host_start_token: str,
) -> Dict:
    argv_bytes = _canonical_argv_bytes(command)
    return {
        "schema_version": 1,
        "status": "launching",
        "run_id": run_id,
        "workspace_id": workspace_state["workspace_id"],
        "period_id": period_id,
        "created_at": _utc_now(),
        "host_pid": os.getpid(),
        "host_start_token": host_start_token,
        "command_version": COMMAND_VERSION,
        "expected_argv": list(command),
        "expected_argv_sha256": hashlib.sha256(argv_bytes).hexdigest(),
        "executable_identity": _requested_executable_identity(executable),
        "run_root": str(run_root),
        "sandbox": str(sandbox),
        "input_snapshot": str(input_snapshot),
        "output_staging": str(output_staging),
        "final_output_path": str(final_output_path),
        "error_code": None,
        "error_category": None,
        "manual_recovery": None,
    }


def _canonical_argv_bytes(argv: List[str]) -> bytes:
    return json.dumps(argv, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def _requested_executable_identity(executable: str) -> Dict:
    environment = _minimal_codex_environment()
    if os.sep in executable or (os.altsep is not None and os.altsep in executable):
        resolved = os.path.abspath(executable)
    else:
        resolved = shutil.which(executable, path=environment.get("PATH"))
    if not resolved:
        raise ValueError("Codex executable is unavailable")
    executable_stat = os.stat(resolved)
    if not stat.S_ISREG(executable_stat.st_mode):
        raise ValueError("Codex executable is not a regular file")
    return {
        "path": resolved,
        "device": int(executable_stat.st_dev),
        "inode": int(executable_stat.st_ino),
    }


def _after_popen(process: subprocess.Popen) -> None:
    return None


def _remove_launch_marker(root: Path, run_id: str) -> None:
    path = _launch_state_path(root, run_id)
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def _capture_process_identity(pid: int) -> Dict:
    process_group_id = os.getpgid(pid)
    session_id = os.getsid(pid)
    if process_group_id != pid or session_id != pid:
        raise RuntimeError("Codex process did not start in its own session and process group")
    start_token = _process_start_token(pid)
    executable_identity = None
    stable_observations = 0
    deadline = time.time() + 0.5
    while time.time() < deadline:
        observed = _process_executable_identity(pid)
        if observed == executable_identity:
            stable_observations += 1
        else:
            executable_identity = observed
            stable_observations = 1
        if stable_observations >= 3:
            break
        time.sleep(0.01)
    if stable_observations < 3 or executable_identity is None:
        raise RuntimeError("Codex executable identity did not stabilize")
    return {
        "process_group_id": process_group_id,
        "session_id": session_id,
        "process_start_token": start_token,
        "executable_identity": executable_identity,
    }


def _process_start_token(pid: int) -> str:
    if not isinstance(pid, int) or pid <= 0:
        raise ProcessLookupError(pid)
    if sys.platform.startswith("linux"):
        stat_payload = Path("/proc/{}/stat".format(pid)).read_text(encoding="utf-8")
        closing_parenthesis = stat_payload.rfind(")")
        fields = stat_payload[closing_parenthesis + 2 :].split()
        if closing_parenthesis < 0 or len(fields) <= 19:
            raise ProcessLookupError(pid)
        boot_id = Path("/proc/sys/kernel/random/boot_id").read_text(encoding="ascii").strip()
        fingerprint = "linux:{}:{}:{}".format(boot_id, pid, fields[19])
    elif sys.platform == "darwin":
        info = _darwin_process_info(pid)
        fingerprint = "darwin:{}:{}:{}".format(pid, info.pbi_start_tvsec, info.pbi_start_tvusec)
    else:
        raise RuntimeError("Codex process recovery requires macOS or Linux")
    return hashlib.sha256(fingerprint.encode("ascii")).hexdigest()


def _process_executable_identity(pid: int) -> Dict[str, int]:
    if sys.platform.startswith("linux"):
        executable_stat = os.stat("/proc/{}/exe".format(pid))
    elif sys.platform == "darwin":
        libproc = ctypes.CDLL("/usr/lib/libproc.dylib", use_errno=True)
        buffer = ctypes.create_string_buffer(4096)
        length = libproc.proc_pidpath(pid, buffer, ctypes.sizeof(buffer))
        if length <= 0:
            raise ProcessLookupError(pid)
        executable_stat = os.stat(os.fsdecode(buffer.value))
    else:
        raise RuntimeError("Codex process recovery requires macOS or Linux")
    return {"device": int(executable_stat.st_dev), "inode": int(executable_stat.st_ino)}


def _darwin_process_info(pid: int) -> _DarwinProcBSDInfo:
    libproc = ctypes.CDLL("/usr/lib/libproc.dylib", use_errno=True)
    info = _DarwinProcBSDInfo()
    result = libproc.proc_pidinfo(pid, 3, 0, ctypes.byref(info), ctypes.sizeof(info))
    if result != ctypes.sizeof(info) or info.pbi_pid != pid:
        raise ProcessLookupError(pid)
    return info


def _reconcile_workspace_runs(root: Path) -> None:
    runs_root = root / ".system" / "runs"
    if not runs_root.exists():
        return
    for candidate in runs_root.iterdir():
        try:
            candidate_stat = os.lstat(os.fspath(candidate))
        except FileNotFoundError:
            continue
        if not stat.S_ISDIR(candidate_stat.st_mode) or stat.S_ISLNK(candidate_stat.st_mode):
            continue
        if not RUN_ID_RE.fullmatch(candidate.name):
            continue
        if (candidate / "run.json").exists():
            _reconcile_run(root, candidate.name)
            continue
        if (candidate / "launch.json").exists():
            launch = _reconcile_launch_marker(root, candidate.name)
            if launch.get("status") == "manual_recovery_required":
                raise ValueError(
                    "manual recovery required for {}; inspect .system/runs/{}/launch.json".format(
                        candidate.name, candidate.name
                    )
                )
            if launch.get("status") == "launching":
                raise ValueError("Codex launch is already in progress for {}".format(candidate.name))


def _reconcile_run(root: Path, run_id: str) -> Optional[Dict]:
    with _REGISTRY_LOCK:
        if (str(root), run_id) in _RUN_REGISTRY:
            return None
    with _RECOVERY_LOCK:
        path = _run_state_path(root, run_id)
        if not path.exists():
            return None
        record = _load_json_object(path, "run metadata")
        if record.get("status") not in {"running", "cancelling"}:
            return record
        if _process_token_matches(record.get("host_pid"), record.get("host_start_token")):
            return record

        process_group_matches = _recorded_process_group_matches(record)
        if process_group_matches:
            _terminate_recovered_process(record)
            error_code = "orphan_recovered"
        else:
            error_code = "runner_restarted"

        _restore_period_retryable(root, record.get("period_id"))
        _release_recovered_lock(root, run_id)
        record["status"] = "failed"
        record["finished_at"] = _utc_now()
        record["exit_code"] = None
        record["error_code"] = error_code
        record["error_category"] = _error_category(error_code)
        record["recovered_at"] = _utc_now()
        _write_json_atomic(path, record)
        return record


def _reconcile_launch_marker(root: Path, run_id: str) -> Dict:
    with _RECOVERY_LOCK:
        path = _launch_state_path(root, run_id)
        marker = _load_json_object(path, "launch marker")
        _validate_launch_marker(marker, root, run_id)
        if marker["status"] == "failed":
            return marker
        if marker["status"] == "manual_recovery_required":
            if _run_lock_entry_exists(root):
                return marker
            return _resume_manual_launch_recovery(root, path, marker)
        if _process_token_matches(marker.get("host_pid"), marker.get("host_start_token")):
            return marker

        inspection_status, matches = _find_launch_process_matches(marker)
        if inspection_status != "ok" or len(matches) != 1:
            return _mark_launch_manual_recovery(path, marker, inspection_status, len(matches))
        process_record = matches[0]
        _terminate_recovered_process(process_record)
        if _recorded_process_group_matches(process_record):
            return _mark_launch_manual_recovery(path, marker, "termination_unverified", 1)
        error_code = "orphan_recovered"

        _restore_period_retryable(root, marker["period_id"])
        _release_recovered_lock(root, run_id)
        marker["status"] = "failed"
        marker["finished_at"] = _utc_now()
        marker["error_code"] = error_code
        marker["error_category"] = _error_category(error_code)
        _write_json_atomic(path, marker)
        return marker


def _resume_manual_launch_recovery(root: Path, path: Path, marker: Dict) -> Dict:
    inspection_status, matches = _find_launch_process_matches(marker)
    if inspection_status == "ok" and not matches:
        _restore_period_retryable(root, marker["period_id"])
        marker["status"] = "failed"
        marker["finished_at"] = _utc_now()
        marker["error_code"] = "manual_recovery_completed"
        marker["error_category"] = _error_category(marker["error_code"])
        marker["inspection_status"] = "no_exact_match"
        marker["match_count"] = 0
        _write_json_atomic(path, marker)
        return marker

    protected_pid = matches[0]["pid"] if len(matches) == 1 else os.getpid()
    _ensure_manual_recovery_lock(root, marker["run_id"], protected_pid)
    if inspection_status == "ok" and len(matches) == 1:
        inspection_status = "exact_process_still_running"
    return _mark_launch_manual_recovery(path, marker, inspection_status, len(matches))


def _validate_launch_marker(marker: Dict, root: Path, run_id: str) -> None:
    required = {
        "schema_version",
        "status",
        "run_id",
        "workspace_id",
        "period_id",
        "created_at",
        "host_pid",
        "host_start_token",
        "command_version",
        "expected_argv",
        "expected_argv_sha256",
        "executable_identity",
        "run_root",
        "sandbox",
        "input_snapshot",
        "output_staging",
        "final_output_path",
        "error_code",
        "error_category",
        "manual_recovery",
    }
    optional = {"finished_at", "inspection_status", "match_count"}
    if not required <= set(marker) or not set(marker) <= required | optional:
        raise ValueError("launch marker fields are invalid")
    if marker["schema_version"] != 1 or marker["run_id"] != run_id:
        raise ValueError("launch marker identity is invalid")
    if marker["status"] not in {"launching", "failed", "manual_recovery_required"}:
        raise ValueError("launch marker status is invalid")
    expected_root = root / ".system" / "runs" / run_id
    expected_paths = {
        "run_root": expected_root,
        "sandbox": expected_root / "sandbox",
        "input_snapshot": expected_root / "sandbox" / "input_snapshot",
        "output_staging": expected_root / "output_staging",
        "final_output_path": expected_root / "output_staging" / "final.json",
    }
    if any(marker[key] != str(value) for key, value in expected_paths.items()):
        raise ValueError("launch marker paths are invalid")
    argv = marker["expected_argv"]
    if not isinstance(argv, list) or not argv or any(not isinstance(item, str) for item in argv):
        raise ValueError("launch marker argv is invalid")
    if hashlib.sha256(_canonical_argv_bytes(argv)).hexdigest() != marker["expected_argv_sha256"]:
        raise ValueError("launch marker argv hash mismatch")
    executable_identity = marker["executable_identity"]
    if not isinstance(executable_identity, dict) or set(executable_identity) != {"path", "device", "inode"}:
        raise ValueError("launch marker executable identity is invalid")


def _find_launch_process_matches(marker: Dict) -> Tuple[str, List[Dict]]:
    executable_identity = marker["executable_identity"]
    try:
        executable_stat = os.stat(executable_identity["path"])
    except OSError:
        return "executable_unavailable", []
    if {
        "device": int(executable_stat.st_dev),
        "inode": int(executable_stat.st_ino),
    } != {"device": executable_identity["device"], "inode": executable_identity["inode"]}:
        return "executable_identity_mismatch", []

    process_ids = _list_process_ids()
    if process_ids is None:
        return "inspection_failed", []
    expected_argv = marker["expected_argv"]
    matches = []
    inspected = 0
    for pid in process_ids:
        try:
            argv = _process_argv(pid)
        except (OSError, RuntimeError, ValueError):
            continue
        inspected += 1
        if len(argv) < len(expected_argv) or argv[-len(expected_argv) :] != expected_argv:
            continue
        try:
            identity = _capture_process_identity(pid)
        except (OSError, RuntimeError, ValueError):
            continue
        identity["pid"] = pid
        matches.append(identity)
    if inspected == 0:
        return "inspection_failed", []
    return "ok", matches


def _list_process_ids() -> Optional[List[int]]:
    try:
        completed = subprocess.run(
            ["ps", "-axo", "pid="],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            env=_minimal_codex_environment(),
            timeout=2,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if completed.returncode != 0:
        return None
    return [int(value) for value in completed.stdout.decode("ascii", errors="ignore").split() if value.isdigit()]


def _process_argv(pid: int) -> List[str]:
    if sys.platform.startswith("linux"):
        payload = Path("/proc/{}/cmdline".format(pid)).read_bytes()
        values = payload.rstrip(b"\0").split(b"\0") if payload else []
        return [os.fsdecode(value) for value in values]
    if sys.platform == "darwin":
        return _darwin_process_argv(pid)
    raise RuntimeError("Codex launch recovery requires macOS or Linux")


def _darwin_process_argv(pid: int) -> List[str]:
    libc = ctypes.CDLL(None, use_errno=True)
    mib = (ctypes.c_int * 3)(1, 49, pid)
    size = ctypes.c_size_t(0)
    if libc.sysctl(mib, 3, None, ctypes.byref(size), None, 0) != 0 or size.value <= 4:
        raise ProcessLookupError(pid)
    buffer = ctypes.create_string_buffer(size.value)
    if libc.sysctl(mib, 3, buffer, ctypes.byref(size), None, 0) != 0:
        raise ProcessLookupError(pid)
    payload = buffer.raw[: size.value]
    argument_count = struct.unpack_from("i", payload, 0)[0]
    if argument_count <= 0:
        return []
    offset = 4
    executable_end = payload.find(b"\0", offset)
    if executable_end < 0:
        raise ValueError("process argv is malformed")
    offset = executable_end
    while offset < len(payload) and payload[offset] == 0:
        offset += 1
    argv = []
    while offset < len(payload) and len(argv) < argument_count:
        end = payload.find(b"\0", offset)
        if end < 0:
            end = len(payload)
        argv.append(os.fsdecode(payload[offset:end]))
        offset = end + 1
    if len(argv) != argument_count:
        raise ValueError("process argv is incomplete")
    return argv


def _mark_launch_manual_recovery(path: Path, marker: Dict, inspection_status: str, match_count: int) -> Dict:
    marker["status"] = "manual_recovery_required"
    marker["error_code"] = "launch_recovery_unverified"
    marker["error_category"] = "recovery"
    marker["inspection_status"] = inspection_status
    marker["match_count"] = match_count
    marker["manual_recovery"] = {
        "action": "Stop the matching Codex process group, confirm it is no longer running, remove .system/codex-run.lock, then retry",
        "expected_argv_sha256": marker["expected_argv_sha256"],
        "launch_marker": ".system/runs/{}/launch.json".format(marker["run_id"]),
    }
    _write_json_atomic(path, marker)
    return marker


def _process_token_matches(pid: Any, expected_token: Any) -> bool:
    if not isinstance(pid, int) or pid <= 0 or not isinstance(expected_token, str):
        return False
    try:
        return _process_start_token(pid) == expected_token
    except (OSError, RuntimeError, ValueError):
        return False


def _recorded_child_matches(record: Dict) -> bool:
    pid = record.get("pid")
    process_group_id = record.get("process_group_id")
    expected_executable = record.get("executable_identity")
    session_id = record.get("session_id")
    if not isinstance(pid, int) or pid <= 0 or process_group_id != pid or session_id != pid:
        return False
    if not isinstance(expected_executable, dict) or set(expected_executable) != {"device", "inode"}:
        return False
    if not _process_token_matches(pid, record.get("process_start_token")):
        return False
    try:
        if os.getpgid(pid) != process_group_id or os.getsid(pid) != session_id:
            return False
        return _process_executable_identity(pid) == expected_executable
    except (OSError, RuntimeError, ValueError):
        return False


def _terminate_recovered_process(record: Dict) -> None:
    if not _recorded_process_group_matches(record):
        return
    process_group_id = int(record["process_group_id"])
    try:
        os.killpg(process_group_id, signal.SIGTERM)
    except ProcessLookupError:
        return
    deadline = time.time() + CANCEL_GRACE_SECONDS
    while time.time() < deadline:
        if not _recorded_process_group_matches(record):
            return
        time.sleep(WAIT_POLL_SECONDS)
    if not _recorded_process_group_matches(record):
        return
    try:
        os.killpg(process_group_id, signal.SIGKILL)
    except ProcessLookupError:
        return
    observe_deadline = time.time() + 2.0
    while time.time() < observe_deadline and _recorded_process_group_matches(record):
        time.sleep(WAIT_POLL_SECONDS)


def _recorded_process_group_matches(record: Dict) -> bool:
    if _recorded_child_matches(record):
        return True
    pid = record.get("pid")
    process_group_id = record.get("process_group_id")
    session_id = record.get("session_id")
    if not isinstance(pid, int) or pid <= 0 or process_group_id != pid or session_id != pid:
        return False
    if _process_token_matches(pid, record.get("process_start_token")):
        try:
            return os.getpgid(pid) == process_group_id and os.getsid(pid) == session_id
        except OSError:
            return False
    if _pid_is_running(pid):
        return False
    return _process_group_has_members(process_group_id, session_id)


def _process_group_has_members(process_group_id: int, session_id: int) -> bool:
    try:
        completed = subprocess.run(
            ["ps", "-axo", "pid=,pgid="],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            env=_minimal_codex_environment(),
            timeout=2,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    if completed.returncode != 0:
        return False
    for line in completed.stdout.decode("ascii", errors="ignore").splitlines():
        fields = line.split()
        if len(fields) != 2 or not all(field.isdigit() for field in fields):
            continue
        observed_pid, observed_group = (int(field) for field in fields)
        if observed_group != process_group_id:
            continue
        try:
            if os.getsid(observed_pid) == session_id:
                return True
        except OSError:
            continue
    return False


def _restore_period_retryable(root: Path, period_id: Any) -> None:
    if not isinstance(period_id, str):
        return
    period_state = _load_period_state(root, period_id)
    if period_state["stage"] == "running":
        _transition_period(period_state, "failed")
    if period_state["stage"] in {"failed", "cancelled"}:
        _transition_period(period_state, "ready_for_run")
    _save_period_state(root, period_state)


def _release_recovered_lock(root: Path, run_id: str) -> None:
    system_descriptor = _open_directory_fd(root / ".system")
    lock_descriptor = None
    try:
        try:
            lock_descriptor = os.open(
                RUN_LOCK_NAME,
                os.O_RDONLY | _no_follow_flag(),
                dir_fd=system_descriptor,
            )
        except FileNotFoundError:
            return
        lock_stat = os.fstat(lock_descriptor)
        if not stat.S_ISREG(lock_stat.st_mode):
            return
        with os.fdopen(lock_descriptor, "rb", closefd=False) as handle:
            try:
                payload = json.loads(handle.read().decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                return
        if not isinstance(payload, dict) or payload.get("run_id") != run_id:
            return
        opened_identity = (lock_stat.st_dev, lock_stat.st_ino)
        if _entry_identity(system_descriptor, RUN_LOCK_NAME, "Codex run lock") != opened_identity:
            return
        os.unlink(RUN_LOCK_NAME, dir_fd=system_descriptor)
        os.fsync(system_descriptor)
    finally:
        if lock_descriptor is not None:
            os.close(lock_descriptor)
        os.close(system_descriptor)


def _run_lock_entry_exists(root: Path) -> bool:
    try:
        os.lstat(os.fspath(root / ".system" / RUN_LOCK_NAME))
    except FileNotFoundError:
        return False
    return True


def _ensure_manual_recovery_lock(root: Path, run_id: str, pid: int) -> None:
    try:
        lock = _acquire_run_lock(root, run_id)
    except ValueError:
        return
    try:
        _rewrite_run_lock(lock, run_id=run_id, pid=pid)
    finally:
        lock.released = True
        os.close(lock.descriptor)
        os.close(lock.system_descriptor)


def _acquire_run_lock(root: Path, run_id: str) -> _RunLock:
    system_descriptor = _open_directory_fd(root / ".system")
    lock_descriptor = None
    try:
        while True:
            try:
                lock_descriptor = os.open(
                    RUN_LOCK_NAME,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL | _no_follow_flag(),
                    0o600,
                    dir_fd=system_descriptor,
                )
                break
            except FileExistsError:
                _entry_identity(system_descriptor, RUN_LOCK_NAME, "Codex run lock")
                if _reclaimable_lock(root / ".system" / RUN_LOCK_NAME):
                    os.unlink(RUN_LOCK_NAME, dir_fd=system_descriptor)
                    os.fsync(system_descriptor)
                    continue
                raise ValueError(
                    "Codex run is already in progress, or a stale run lock remains; "
                    "after confirming no Codex run is active, inspect/remove "
                    ".system/{} manually and retry".format(RUN_LOCK_NAME)
                )
        identity_stat = os.fstat(lock_descriptor)
        identity = (identity_stat.st_dev, identity_stat.st_ino)
        _write_all(
            lock_descriptor,
            (json.dumps({"pid": os.getpid(), "run_id": run_id, "started_at": _utc_now()}) + "\n").encode("utf-8"),
        )
        os.fsync(lock_descriptor)
        os.fsync(system_descriptor)
        return _RunLock(root=root, system_descriptor=system_descriptor, descriptor=lock_descriptor, identity=identity)
    except Exception:
        if lock_descriptor is not None:
            os.close(lock_descriptor)
        os.close(system_descriptor)
        raise


def _rewrite_run_lock(lock: _RunLock, *, run_id: str, pid: int) -> None:
    payload = {"pid": pid, "run_id": run_id, "started_at": _utc_now(), "host_pid": os.getpid()}
    os.ftruncate(lock.descriptor, 0)
    os.lseek(lock.descriptor, 0, os.SEEK_SET)
    _write_all(lock.descriptor, (json.dumps(payload) + "\n").encode("utf-8"))
    os.fsync(lock.descriptor)
    os.fsync(lock.system_descriptor)


def _release_run_lock(lock: _RunLock) -> None:
    if lock.released:
        return
    try:
        current = _entry_identity(lock.system_descriptor, RUN_LOCK_NAME, "Codex run lock")
        if current == lock.identity:
            os.unlink(RUN_LOCK_NAME, dir_fd=lock.system_descriptor)
            os.fsync(lock.system_descriptor)
    except FileNotFoundError:
        pass
    finally:
        try:
            os.close(lock.descriptor)
        finally:
            os.close(lock.system_descriptor)
        lock.released = True


def _reclaimable_lock(path: Path) -> bool:
    try:
        payload = json.loads(_read_text_no_follow(path, "Codex run lock"))
    except (OSError, ValueError, json.JSONDecodeError):
        return False
    if not isinstance(payload, dict):
        return False
    pid = payload.get("pid")
    if not isinstance(pid, int) or pid <= 0:
        return False
    host_pid = payload.get("host_pid")
    if host_pid is not None and (not isinstance(host_pid, int) or host_pid <= 0):
        return False
    if _pid_is_running(pid):
        return False
    if isinstance(host_pid, int) and host_pid != pid and _pid_is_running(host_pid):
        return False
    return True


def _pid_is_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError as error:
        if error.errno == errno.ESRCH:
            return False
        return True
    return True


def _terminate_process_group(pid: int, *, force: bool) -> None:
    try:
        group_id = os.getpgid(pid)
    except OSError as error:
        if error.errno == errno.ESRCH:
            return
        raise
    try:
        os.killpg(group_id, signal.SIGKILL if force else signal.SIGTERM)
    except OSError as error:
        if error.errno != errno.ESRCH:
            raise


def _new_run_id(runs_root: Path) -> str:
    runs_root.mkdir(mode=0o700, parents=True, exist_ok=True)
    while True:
        candidate = "run-" + uuid.uuid4().hex
        if not (runs_root / candidate).exists():
            return candidate


def _validate_run_id(run_id: str) -> str:
    if not isinstance(run_id, str) or not RUN_ID_RE.fullmatch(run_id):
        raise ValueError("run_id must be a safe run identifier")
    return run_id


def _load_json_object(path: Path, label: str) -> Dict:
    try:
        payload = json.loads(_read_text_no_follow(path, label))
    except json.JSONDecodeError as error:
        raise ValueError("{} contains invalid JSON".format(label)) from error
    if not isinstance(payload, dict):
        raise ValueError("{} must be a JSON object".format(label))
    return payload


def _sanitize_event(payload: Any, line_number: int) -> Optional[Dict]:
    if not isinstance(payload, dict):
        return None
    if "event" in payload:
        event_name = payload["event"]
    elif "type" in payload:
        event_name = payload["type"]
    else:
        return None
    if not isinstance(event_name, str) or not event_name.strip():
        return None
    normalized_event = event_name.strip()
    if normalized_event in SAFE_EVENT_NAMES:
        sanitized = {"line": line_number, "event": normalized_event}
    else:
        sanitized = {
            "line": line_number,
            "event": "unrecognized",
            "event_name_metadata": _untrusted_text_metadata(event_name),
        }
    for key, allowed_values in (
        ("status", SAFE_EVENT_STATUS_VALUES),
        ("phase", SAFE_EVENT_PHASE_VALUES),
    ):
        value = payload.get(key)
        if not isinstance(value, str):
            continue
        normalized_value = value.strip()
        if normalized_value in allowed_values:
            sanitized[key] = normalized_value
        else:
            sanitized[key + "_metadata"] = _untrusted_text_metadata(value)
    return sanitized


def _untrusted_text_metadata(value: str) -> Dict:
    payload = value.encode("utf-8")
    return {
        "marker": "unrecognized",
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def _drain_line(stream) -> None:
    while True:
        chunk = stream.readline()
        if not chunk or chunk.endswith(b"\n"):
            return


def _error_category(error_code: Optional[str]) -> Optional[str]:
    if error_code is None:
        return None
    return ERROR_CATEGORIES.get(error_code, "internal")


def _run_state_path(workspace: Path, run_id: str) -> Path:
    return workspace / ".system" / "runs" / run_id / "run.json"


def _launch_state_path(workspace: Path, run_id: str) -> Path:
    return workspace / ".system" / "runs" / run_id / "launch.json"


def _events_path(run_root: Path) -> Path:
    return run_root / "events.jsonl"


def _source_manifest_disk_path(workspace: Path, period_id: str) -> Path:
    return workspace / ".system" / "periods" / period_id / "source_manifest.json"


__all__ = [
    "MAX_RUN_TIMEOUT_SECONDS",
    "MIN_RUN_TIMEOUT_SECONDS",
    "RUN_LOCK_NAME",
    "cancel_run",
    "codex_preflight",
    "run_status",
    "start_codex_run",
    "wait_for_run",
]
