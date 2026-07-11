from __future__ import annotations

import getpass
import hashlib
import hmac
import json
import os
import re
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from typing import Dict, List, Optional

from ai_automation_kit.core.office_workspace_builder import (
    PERIOD_FOLDERS,
    WORKSPACE_SCHEMA_VERSION,
    _append_jsonl,
    _absolute_path,
    _derive_scrypt_hex,
    _entry_identity,
    _json_copy,
    _no_follow_flag,
    _open_directory_fd,
    _read_bytes_no_follow,
    _read_text_no_follow,
    _sha256_file,
    _update_workspace_status,
    _utc_now,
    _write_all,
    _write_bytes_collision_safe,
    _write_json_atomic,
    validate_period_id,
    validate_workspace_root,
)
from ai_automation_kit.core.report_intake import inspect_sources
from ai_automation_kit.core.workflow_pack import load_bundled_pack


PERIOD_SCHEMA_VERSION = 1
PERIOD_STAGES = (
    "created",
    "inputs_ready",
    "reviewed",
    "questioning",
    "ready_for_run",
    "running",
    "ready_for_review",
    "approved",
    "cancelled",
    "failed",
)
PERIOD_TRANSITIONS = {
    "created": {"inputs_ready"},
    "inputs_ready": {"reviewed"},
    "reviewed": {"questioning", "ready_for_run"},
    "questioning": {"ready_for_run"},
    "ready_for_run": {"running"},
    "running": {"questioning", "ready_for_review", "cancelled", "failed"},
    "ready_for_review": {"approved"},
    "cancelled": {"ready_for_run"},
    "failed": {"ready_for_run"},
    "approved": set(),
}
RUN_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
HEX_64_RE = re.compile(r"^[0-9a-f]{64}$")
HEX_128_RE = re.compile(r"^[0-9a-f]{128}$")


def _workspace_state_path(workspace: Path) -> Path:
    return validate_workspace_root(workspace) / ".system" / "workspace.json"


def _pack_manifest_path(workspace: Path) -> Path:
    return validate_workspace_root(workspace) / ".system" / "pack-manifest.json"


def _period_root(workspace: Path, period_id: str) -> Path:
    return validate_workspace_root(workspace) / ".system" / "periods" / validate_period_id(period_id)


def _period_state_path(workspace: Path, period_id: str) -> Path:
    return _period_root(workspace, period_id) / "state.json"


def _source_manifest_path(workspace: Path, period_id: str) -> Path:
    return _period_root(workspace, period_id) / "source_manifest.json"


def _read_json(path: Path, label: str) -> Dict:
    try:
        payload = json.loads(_read_text_no_follow(path, label))
    except json.JSONDecodeError as error:
        raise ValueError("{} contains invalid JSON".format(label)) from error
    except OSError as error:
        raise ValueError("cannot read {}".format(label)) from error
    if not isinstance(payload, dict):
        raise ValueError("{} must contain a JSON object".format(label))
    return payload


def _load_workspace_state(workspace: Path) -> Dict:
    state = _read_json(_workspace_state_path(workspace), ".system/workspace.json")
    required = {
        "schema_version",
        "workspace_id",
        "name",
        "root",
        "language",
        "pack_id",
        "created_at",
        "updated_at",
        "current_period",
        "periods",
        "approval",
        "pack_manifest",
    }
    if set(state) != required:
        raise ValueError("workspace state fields do not match schema version 1")
    if state["schema_version"] != WORKSPACE_SCHEMA_VERSION:
        raise ValueError("workspace state schema_version is not supported")
    if state["root"] != str(validate_workspace_root(workspace)):
        raise ValueError("workspace state belongs to another workspace")
    if not isinstance(state["periods"], list) or any(not isinstance(item, str) for item in state["periods"]):
        raise ValueError("workspace periods must be a list of period ids")
    approval = state["approval"]
    if not isinstance(approval, dict):
        raise ValueError("workspace approval must be an object")
    for key in ("approver", "pin_salt", "pin_hash", "kdf"):
        if key not in approval:
            raise ValueError("workspace approval.{} is required".format(key))
    if not HEX_128_RE.fullmatch(str(approval["pin_hash"])):
        raise ValueError("workspace approval.pin_hash must be a 64-byte hex digest")
    if not re.fullmatch(r"[0-9a-f]{32}", str(approval["pin_salt"])):
        raise ValueError("workspace approval.pin_salt must be hex encoded")
    return state


def _save_workspace_state(workspace: Path, state: Dict) -> Dict:
    state["updated_at"] = _utc_now()
    _write_json_atomic(_workspace_state_path(workspace), state)
    _update_workspace_status(validate_workspace_root(workspace), state)
    return state


def _period_questions(pack: Dict) -> List[Dict]:
    return [
        {
            "id": item["id"],
            "required": bool(item["required"]),
            "status": "pending",
            "source": "pack",
            "question": item["id"],
            "max_length": item.get("max_length"),
        }
        for item in pack["questions"]
    ]


def _period_template(workspace_state: Dict, period_id: str, style_reference: Optional[Dict], pack: Dict) -> Dict:
    timestamp = _utc_now()
    return {
        "schema_version": PERIOD_SCHEMA_VERSION,
        "period_id": period_id,
        "workspace_id": workspace_state["workspace_id"],
        "pack_id": workspace_state["pack_id"],
        "created_at": timestamp,
        "updated_at": timestamp,
        "stage": "created",
        "style_reference": style_reference,
        "answers": {},
        "questions": _period_questions(pack),
        "pending_question_ids": [],
        "source_manifest_path": None,
        "source_manifest_hash": None,
        "current_draft": None,
        "drafts": [],
        "approved_outputs": [],
        "latest_question_artifact": None,
        "audit": {"status": "pending", "latest_hash": None, "entries": 0},
        "stage_history": [{"from": None, "to": "created", "at": timestamp}],
    }


def _load_period_state(workspace: Path, period_id: str) -> Dict:
    path = _period_state_path(workspace, period_id)
    if not path.exists():
        raise ValueError("period {} does not exist".format(period_id))
    state = _read_json(path, ".system/periods/{}/state.json".format(period_id))
    required = {
        "schema_version",
        "period_id",
        "workspace_id",
        "pack_id",
        "created_at",
        "updated_at",
        "stage",
        "style_reference",
        "answers",
        "questions",
        "pending_question_ids",
        "source_manifest_path",
        "source_manifest_hash",
        "current_draft",
        "drafts",
        "approved_outputs",
        "latest_question_artifact",
        "audit",
        "stage_history",
    }
    if set(state) != required:
        raise ValueError("period state fields do not match schema version 1")
    if state["schema_version"] != PERIOD_SCHEMA_VERSION:
        raise ValueError("period state schema_version is not supported")
    if state["period_id"] != validate_period_id(period_id):
        raise ValueError("period state belongs to another period")
    if state["stage"] not in PERIOD_STAGES:
        raise ValueError("period stage is invalid")
    if not isinstance(state["answers"], dict):
        raise ValueError("period answers must be an object")
    if not isinstance(state["questions"], list):
        raise ValueError("period questions must be a list")
    if not isinstance(state["pending_question_ids"], list):
        raise ValueError("period pending_question_ids must be a list")
    return state


def _save_period_state(workspace: Path, state: Dict) -> Dict:
    state["updated_at"] = _utc_now()
    _write_json_atomic(_period_state_path(workspace, state["period_id"]), state)
    return state


def _transition_period(state: Dict, target: str) -> None:
    if state["stage"] == target:
        return
    allowed = PERIOD_TRANSITIONS.get(state["stage"], set())
    if target not in allowed:
        raise ValueError("invalid transition from {} to {}".format(state["stage"], target))
    previous = state["stage"]
    state["stage"] = target
    state["stage_history"].append({"from": previous, "to": target, "at": _utc_now()})


def _record_metadata(record: Dict) -> Dict:
    return {key: value for key, value in record.items() if key != "text"}


def _refresh_pending_questions(state: Dict) -> None:
    pending = []
    for question in state["questions"]:
        answer = state["answers"].get(question["id"])
        if isinstance(answer, str) and answer.strip():
            question["status"] = "answered"
            continue
        if question.get("required", True):
            question["status"] = "pending"
            pending.append(question["id"])
        else:
            question["status"] = "answered"
    state["pending_question_ids"] = pending


def _relative_workspace_path(path: Path, root: Path) -> str:
    return str(path.relative_to(root)).replace(os.sep, "/")


def _validated_style_reference(
    workspace: Path,
    period_id: str,
    style_reference: Optional[Dict],
) -> Optional[Dict]:
    if style_reference is None:
        return None
    if not isinstance(style_reference, dict):
        raise ValueError("style_reference must be an object or None")
    relative_path = style_reference.get("relative_path")
    sha256_value = style_reference.get("sha256")
    if not isinstance(relative_path, str) or not isinstance(sha256_value, str):
        raise ValueError("style_reference must include relative_path and sha256")
    candidate = PurePosixPath(relative_path)
    if candidate.is_absolute() or any(part in {"", ".", ".."} for part in candidate.parts):
        raise ValueError("style_reference.relative_path must be a safe relative path")
    if len(candidate.parts) != 3 or candidate.parts[0] != "06_APPROVED_OUTPUTS":
        raise ValueError("style_reference must point at a prior approved output")
    if not HEX_64_RE.fullmatch(sha256_value):
        raise ValueError("style_reference.sha256 must be a lowercase sha256 hex digest")
    root = validate_workspace_root(workspace)
    file_path = _absolute_path(root / relative_path)
    if not str(file_path).startswith(str(root) + os.sep):
        raise ValueError("style_reference must remain inside the workspace")
    referenced_period = validate_period_id(candidate.parts[1])
    workspace_state = _load_workspace_state(workspace)
    if referenced_period >= period_id or referenced_period not in workspace_state["periods"]:
        raise ValueError("style_reference must point at a prior recorded period")
    referenced_state = _load_period_state(workspace, referenced_period)
    approved_output = next(
        (
            item
            for item in referenced_state["approved_outputs"]
            if isinstance(item, dict)
            and item.get("path") == relative_path
            and item.get("sha256") == sha256_value
        ),
        None,
    )
    if referenced_state["stage"] != "approved" or approved_output is None:
        raise ValueError("style_reference must match a recorded approved output")
    if _sha256_file(file_path, "style_reference") != sha256_value:
        raise ValueError("style_reference sha256 does not match the approved output")
    matching_audit = next(
        (
            entry
            for entry in _read_audit_entries(root / "07_AUDIT" / "audit.jsonl")
            if entry.get("audit_hash") == approved_output.get("audit_hash")
        ),
        None,
    )
    if (
        matching_audit is None
        or matching_audit.get("period_id") != referenced_period
        or matching_audit.get("approved_name") != approved_output.get("name")
        or matching_audit.get("approved_sha256") != sha256_value
    ):
        raise ValueError("style_reference approval audit identity does not match")
    return {"relative_path": relative_path, "sha256": sha256_value}


def load_workspace(workspace: Path) -> Dict:
    return _json_copy(_load_workspace_state(workspace))


def create_period(workspace: Path, period_id: str, style_reference: Optional[Dict] = None) -> Dict:
    period_id = validate_period_id(period_id)
    workspace_state = _load_workspace_state(workspace)
    if period_id in workspace_state["periods"]:
        raise ValueError("period {} already exists".format(period_id))
    if workspace_state["periods"] and period_id <= workspace_state["periods"][-1]:
        raise ValueError("period rollover is append-only and must move forward")

    validated_style_reference = _validated_style_reference(workspace, period_id, style_reference)
    pack = load_bundled_pack(workspace_state["pack_id"])
    root = validate_workspace_root(workspace)
    for folder in PERIOD_FOLDERS:
        (root / folder / period_id).mkdir(mode=0o700, parents=True, exist_ok=False)
    period_root = root / ".system" / "periods" / period_id
    period_root.mkdir(mode=0o700, parents=True, exist_ok=False)
    period_state = _period_template(workspace_state, period_id, validated_style_reference, pack)
    _save_period_state(workspace, period_state)

    workspace_state["periods"].append(period_id)
    workspace_state["current_period"] = period_id
    _save_workspace_state(workspace, workspace_state)
    return _json_copy(period_state)


def inspect_period(workspace: Path, period_id: str) -> Dict:
    workspace_state = _load_workspace_state(workspace)
    period_state = _load_period_state(workspace, period_id)
    if period_state["stage"] not in {"created", "questioning", "ready_for_run", "failed", "cancelled"}:
        raise ValueError("inspect_period is not allowed from stage {}".format(period_state["stage"]))
    if period_state["stage"] == "cancelled":
        _transition_period(period_state, "ready_for_run")
    if period_state["stage"] == "failed":
        _transition_period(period_state, "ready_for_run")
    if period_state["stage"] == "questioning":
        pass
    elif period_state["stage"] == "ready_for_run":
        pass
    else:
        _transition_period(period_state, "inputs_ready")

    root = validate_workspace_root(workspace)
    past_root = root / "01_APPROVED_PAST_OUTPUTS"
    supporting_root = root / "02_PAST_SUPPORTING_FILES"
    current_root = root / "03_CURRENT_INPUTS" / period_id
    result = inspect_sources([past_root], [current_root], supporting_paths=[supporting_root])
    manifest = {
        "period_id": period_id,
        "generated_at": _utc_now(),
        "records": [_record_metadata(record) for record in result["records"]],
        "accepted": [_record_metadata(record) for record in result["accepted"]],
        "rejected": [_record_metadata(record) for record in result["rejected"]],
        "skipped": _json_copy(result["skipped"]),
        "counts": _json_copy(result["counts"]),
        "truncated": bool(result["truncated"]),
    }
    manifest_path = _source_manifest_path(workspace, period_id)
    _write_json_atomic(manifest_path, manifest)
    if period_state["stage"] == "inputs_ready":
        _transition_period(period_state, "reviewed")
    elif period_state["stage"] in {"questioning", "ready_for_run"}:
        previous = period_state["stage"]
        period_state["stage_history"].append({"from": previous, "to": previous, "at": _utc_now()})

    period_state["source_manifest_path"] = _relative_workspace_path(manifest_path, root)
    period_state["source_manifest_hash"] = _sha256_file(manifest_path)
    _refresh_pending_questions(period_state)
    if period_state["stage"] == "reviewed":
        _transition_period(period_state, "questioning" if period_state["pending_question_ids"] else "ready_for_run")
    elif period_state["stage"] == "questioning" and not period_state["pending_question_ids"]:
        _transition_period(period_state, "ready_for_run")
    elif period_state["stage"] == "ready_for_run" and period_state["pending_question_ids"]:
        raise ValueError("invalid transition from ready_for_run to questioning")
    _save_period_state(workspace, period_state)

    workspace_state["current_period"] = period_id
    _save_workspace_state(workspace, workspace_state)
    return _json_copy(period_state)


def save_answer(workspace: Path, period_id: str, question_id: str, answer: str) -> Dict:
    period_state = _load_period_state(workspace, period_id)
    if period_state["stage"] != "questioning":
        raise ValueError("save_answer requires questioning stage")
    if not isinstance(question_id, str) or not question_id.strip():
        raise ValueError("question_id must be a non-empty string")
    if not isinstance(answer, str) or not answer.strip():
        raise ValueError("answer must be a non-empty string")

    questions = {item["id"]: item for item in period_state["questions"]}
    question = questions.get(question_id)
    if question is None:
        raise ValueError("unknown question '{}'".format(question_id))
    max_length = question.get("max_length")
    if isinstance(max_length, int) and len(answer) > max_length:
        raise ValueError("answer exceeds the configured max_length")

    period_state["answers"][question_id] = answer.strip()
    _refresh_pending_questions(period_state)
    if not period_state["pending_question_ids"]:
        _transition_period(period_state, "ready_for_run")
    _save_period_state(workspace, period_state)
    return _json_copy(period_state)


def _normalize_missing_questions(value) -> List[Dict]:
    if not isinstance(value, list):
        raise ValueError("missing_questions must be a list")
    normalized = []
    for item in value:
        if isinstance(item, str) and item.strip():
            question_id = re.sub(r"[^A-Za-z0-9._-]+", "_", item.strip().lower())[:64] or "question"
            normalized.append({"id": question_id, "question": item.strip(), "required": True})
            continue
        if not isinstance(item, dict):
            raise ValueError("missing_questions entries must be strings or objects")
        question_id = item.get("id")
        prompt = item.get("question")
        required = item.get("required", True)
        if not isinstance(question_id, str) or not question_id.strip():
            raise ValueError("missing question id must be a non-empty string")
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("missing question prompt must be a non-empty string")
        if not isinstance(required, bool):
            raise ValueError("missing question required must be a boolean")
        normalized.append({"id": question_id.strip(), "question": prompt.strip(), "required": required})
    return normalized


def _draft_output_name(workspace_state: Dict) -> str:
    pack = load_bundled_pack(workspace_state["pack_id"])
    return pack["outputs"][0]["relative_path"]


def promote_run_result(workspace: Path, period_id: str, run_id: str, result: Dict) -> Dict:
    workspace_state = _load_workspace_state(workspace)
    period_state = _load_period_state(workspace, period_id)
    if period_state["stage"] not in {"ready_for_run", "running"}:
        raise ValueError("promote_run_result requires ready_for_run stage")
    if not isinstance(run_id, str) or not RUN_ID_RE.fullmatch(run_id):
        raise ValueError("run_id must be a safe non-empty identifier")
    if not isinstance(result, dict) or set(result) != {"missing_questions", "draft_markdown"}:
        raise ValueError("result must contain only missing_questions and draft_markdown")
    if period_state["stage"] == "ready_for_run":
        _transition_period(period_state, "running")

    missing_questions = _normalize_missing_questions(result["missing_questions"])
    draft_markdown = result["draft_markdown"]
    if not isinstance(draft_markdown, str):
        raise ValueError("draft_markdown must be a string")

    root = validate_workspace_root(workspace)
    if missing_questions:
        artifact = {
            "run_id": run_id,
            "period_id": period_id,
            "created_at": _utc_now(),
            "missing_questions": missing_questions,
        }
        file_name = "{}_missing_questions.json".format(run_id)
        artifact_payload = (json.dumps(artifact, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        artifact_path = _write_bytes_collision_safe(
            root / "04_QUESTIONS" / period_id / file_name,
            artifact_payload,
        )
        known = {item["id"]: item for item in period_state["questions"]}
        for item in missing_questions:
            if item["id"] in known:
                if not period_state["answers"].get(item["id"]):
                    known[item["id"]]["status"] = "pending"
                continue
            period_state["questions"].append(
                {
                    "id": item["id"],
                    "required": item["required"],
                    "status": "pending",
                    "source": "run",
                    "question": item["question"],
                    "max_length": None,
                }
            )
        _refresh_pending_questions(period_state)
        _transition_period(period_state, "questioning")
        period_state["latest_question_artifact"] = {
            "name": artifact_path.name,
            "path": _relative_workspace_path(artifact_path, root),
            "run_id": run_id,
        }
        _save_period_state(workspace, period_state)
        return _json_copy(period_state)

    if not draft_markdown.strip():
        raise ValueError("draft_markdown must be non-empty when no missing questions remain")
    draft_name = _draft_output_name(workspace_state)
    draft_path = _write_bytes_collision_safe(
        root / "05_DRAFTS" / period_id / draft_name,
        draft_markdown.encode("utf-8"),
    )
    draft_hash = _sha256_file(draft_path, "promoted draft")
    current_draft = {
        "name": draft_path.name,
        "path": _relative_workspace_path(draft_path, root),
        "sha256": draft_hash,
        "run_id": run_id,
        "created_at": _utc_now(),
    }
    period_state["current_draft"] = current_draft
    period_state["drafts"].append(_json_copy(current_draft))
    _transition_period(period_state, "ready_for_review")
    _save_period_state(workspace, period_state)
    return _json_copy(period_state)


def _pin_matches(workspace_state: Dict, pin: str) -> bool:
    if not isinstance(pin, str):
        return False
    approval = workspace_state["approval"]
    salt = bytes.fromhex(approval["pin_salt"])
    derived = _derive_scrypt_hex(pin, salt)
    return hmac.compare_digest(derived, approval["pin_hash"])


def _last_audit_hash(audit_path: Path) -> Optional[str]:
    entries = _read_audit_entries(audit_path)
    return entries[-1]["audit_hash"] if entries else None


def _audit_hash(entry: Dict) -> str:
    payload = dict(entry)
    payload.pop("audit_hash", None)
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _read_audit_entries(audit_path: Path) -> List[Dict]:
    try:
        content = _read_text_no_follow(audit_path, "07_AUDIT/audit.jsonl")
    except FileNotFoundError:
        return []
    entries = []
    previous_hash = None
    for line in content.splitlines():
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError("07_AUDIT/audit.jsonl contains invalid JSON") from error
        if not isinstance(entry, dict):
            raise ValueError("07_AUDIT/audit.jsonl entries must be JSON objects")
        if entry.get("previous_audit_hash") != previous_hash or entry.get("audit_hash") != _audit_hash(entry):
            raise ValueError("07_AUDIT/audit.jsonl hash chain is invalid")
        previous_hash = entry["audit_hash"]
        entries.append(entry)
    return entries


def _verified_source_manifest(root: Path, period_id: str, period_state: Dict) -> str:
    expected_path = ".system/periods/{}/source_manifest.json".format(period_id)
    if period_state.get("source_manifest_path") != expected_path:
        raise ValueError("source manifest path does not match the period")
    expected_hash = period_state.get("source_manifest_hash")
    if not isinstance(expected_hash, str) or not HEX_64_RE.fullmatch(expected_hash):
        raise ValueError("source manifest hash is invalid")
    actual_hash = _sha256_file(root / expected_path, "source manifest")
    if actual_hash != expected_hash:
        raise ValueError("source manifest content no longer matches the recorded hash")
    return actual_hash


@contextmanager
def _approval_mutation_lock(root: Path):
    lock_name = "approval.lock"
    lock_label = "approval lock"
    system_descriptor = _open_directory_fd(root / ".system")
    lock_descriptor = None
    lock_identity = None
    try:
        try:
            lock_descriptor = os.open(
                lock_name,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | _no_follow_flag(),
                0o600,
                dir_fd=system_descriptor,
            )
        except FileExistsError as error:
            _entry_identity(system_descriptor, lock_name, lock_label)
            raise ValueError(
                "approval is already in progress, or a stale approval lock remains; "
                "after confirming no approval process is running, remove "
                ".system/approval.lock manually and retry"
            ) from error

        lock_stat = os.fstat(lock_descriptor)
        lock_identity = (lock_stat.st_dev, lock_stat.st_ino)
        metadata = {
            "pid": os.getpid(),
            "created_at": _utc_now(),
            "purpose": "approve_draft",
        }
        _write_all(
            lock_descriptor,
            (json.dumps(metadata, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8"),
        )
        os.fsync(lock_descriptor)
        os.fsync(system_descriptor)
        yield
    finally:
        cleanup_error = None
        if lock_identity is not None:
            try:
                current_identity = _entry_identity(system_descriptor, lock_name, lock_label)
                if current_identity != lock_identity:
                    raise RuntimeError(
                        "approval lock changed unexpectedly; inspect .system/approval.lock before retrying"
                    )
                os.unlink(lock_name, dir_fd=system_descriptor)
                os.fsync(system_descriptor)
            except Exception as error:
                cleanup_error = error
        if lock_descriptor is not None:
            os.close(lock_descriptor)
        os.close(system_descriptor)
        if cleanup_error is not None:
            raise cleanup_error


def approve_draft(workspace: Path, period_id: str, draft_name: str, approver: str, pin: str) -> Dict:
    root = validate_workspace_root(workspace)
    with _approval_mutation_lock(root):
        return _approve_draft_locked(root, workspace, period_id, draft_name, approver, pin)


def _approve_draft_locked(
    root: Path,
    workspace: Path,
    period_id: str,
    draft_name: str,
    approver: str,
    pin: str,
) -> Dict:
    workspace_state = _load_workspace_state(workspace)
    period_state = _load_period_state(workspace, period_id)
    if period_state["stage"] != "ready_for_review":
        raise ValueError("approve_draft requires ready_for_review stage")
    if not isinstance(approver, str) or approver.strip() != workspace_state["approval"]["approver"]:
        raise ValueError("approver must match the configured workspace approver")
    if not _pin_matches(workspace_state, pin):
        raise ValueError("PIN verification failed")
    if not isinstance(draft_name, str) or not draft_name.strip():
        raise ValueError("draft_name must be a non-empty string")
    current_draft = period_state.get("current_draft")
    if not isinstance(current_draft, dict) or current_draft.get("name") != draft_name:
        raise ValueError("draft_name does not match the current draft")

    expected_draft_path = "05_DRAFTS/{}/{}".format(period_id, draft_name)
    if current_draft.get("path") != expected_draft_path:
        raise ValueError("current draft path does not match the period and draft name")
    draft_path = _absolute_path(root / current_draft["path"])
    draft_bytes = _read_bytes_no_follow(draft_path, "current draft")
    if hashlib.sha256(draft_bytes).hexdigest() != current_draft["sha256"]:
        raise ValueError("current draft content no longer matches the recorded hash")

    source_manifest_hash = _verified_source_manifest(root, period_id, period_state)
    audit_path = root / "07_AUDIT" / "audit.jsonl"
    previous_audit_hash = _last_audit_hash(audit_path)

    approved_path = _write_bytes_collision_safe(
        root / "06_APPROVED_OUTPUTS" / period_id / draft_name,
        draft_bytes,
    )
    approved_hash = _sha256_file(approved_path, "approved output")
    if approved_hash != current_draft["sha256"]:
        raise ValueError("approved copy hash verification failed")

    audit_entry = {
        "schema_version": 1,
        "event": "draft_approved",
        "workspace_id": workspace_state["workspace_id"],
        "period_id": period_id,
        "draft_name": draft_name,
        "approved_name": approved_path.name,
        "approver": approver.strip(),
        "os_user": getpass.getuser(),
        "approved_at": _utc_now(),
        "draft_sha256": current_draft["sha256"],
        "approved_sha256": approved_hash,
        "source_manifest_hash": source_manifest_hash,
        "pack_hash": workspace_state["pack_manifest"]["pack_sha256"],
        "previous_audit_hash": previous_audit_hash,
    }
    audit_entry["audit_hash"] = _audit_hash(audit_entry)
    _append_jsonl(audit_path, audit_entry)

    period_state["approved_outputs"].append(
        {
            "name": approved_path.name,
            "path": _relative_workspace_path(approved_path, root),
            "sha256": approved_hash,
            "approved_at": audit_entry["approved_at"],
            "audit_hash": audit_entry["audit_hash"],
        }
    )
    period_state["audit"] = {
        "status": "approved",
        "latest_hash": audit_entry["audit_hash"],
        "entries": int(period_state["audit"]["entries"]) + 1,
    }
    _transition_period(period_state, "approved")
    _save_period_state(workspace, period_state)
    workspace_state["current_period"] = period_id
    _save_workspace_state(workspace, workspace_state)
    return _json_copy(period_state)


__all__ = [
    "approve_draft",
    "create_period",
    "inspect_period",
    "load_workspace",
    "promote_run_result",
    "save_answer",
]
