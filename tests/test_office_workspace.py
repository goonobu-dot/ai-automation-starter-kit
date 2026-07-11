import hashlib
import json
import os
import subprocess
import threading
from pathlib import Path

import pytest

from ai_automation_kit.core import office_workspace_builder
from ai_automation_kit.core import office_workspace_state
from ai_automation_kit.core.office_workspace_builder import create_office_workspace
from ai_automation_kit.core.office_workspace_state import (
    approve_draft,
    create_period,
    inspect_period,
    load_workspace,
    promote_run_result,
    save_answer,
)


def write_text(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def setup_ready_for_run(tmp_path: Path, period_id: str = "2026-07") -> Path:
    root = create_office_workspace(tmp_path, name="Monthly", approver="Owner", pin="482913")
    create_period(root, period_id)
    write_text(root / "01_APPROVED_PAST_OUTPUTS" / "approved.md", "# Past\n売上: 100\n")
    write_text(root / "03_CURRENT_INPUTS" / period_id / "current.md", "# Current\n売上: 120\n")
    inspect_period(root, period_id)
    save_answer(root, period_id, "audience", "Owner team")
    return root


def audit_entry_hash(entry):
    payload = dict(entry)
    payload.pop("audit_hash", None)
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def test_create_monthly_workspace_has_beginner_folders_and_private_state(tmp_path):
    root = create_office_workspace(
        tmp_path, name="Okinawa Monthly", approver="Owner", pin="482913", language="ja"
    )

    for relative in (
        "00_START_HERE",
        "01_APPROVED_PAST_OUTPUTS",
        "02_PAST_SUPPORTING_FILES",
        "03_CURRENT_INPUTS",
        "04_QUESTIONS",
        "05_DRAFTS",
        "06_APPROVED_OUTPUTS",
        "07_AUDIT",
        ".system/workspace.json",
        ".system/pack-manifest.json",
    ):
        assert (root / relative).exists()

    state = load_workspace(root)
    assert state["name"] == "Okinawa Monthly"
    assert "pin" not in state
    assert "pin_hash" in state["approval"]


def test_workspace_creation_fails_closed_before_partial_creation_without_no_follow(tmp_path, monkeypatch):
    monkeypatch.delattr(os, "O_NOFOLLOW")

    with pytest.raises(RuntimeError, match="macOS or Linux"):
        create_office_workspace(tmp_path, name="Monthly", approver="Owner", pin="482913")

    assert not (tmp_path / "Monthly").exists()


def test_in_process_scrypt_fallback_matches_known_answer_without_subprocess(monkeypatch):
    pin = "482913"
    salt = bytes(range(16))
    # Cross-checked independently with Node crypto.scryptSync and OpenSSL kdf SCRYPT.
    expected = (
        "e2750fffae7aea453863bbfad19964fef55d91b853179575ad17b6610a9609c5"
        "b1f9f66af8b3abcdaa08e89f64e73cf4c8c58e13760b637f3c1c98f80c05aa30"
    )

    monkeypatch.delattr(hashlib, "scrypt", raising=False)

    def reject_subprocess(*args, **kwargs):
        raise AssertionError("scrypt fallback must not start an external process")

    monkeypatch.setattr(subprocess, "run", reject_subprocess)

    assert office_workspace_builder._derive_scrypt_hex(pin, salt) == expected


def test_scrypt_fallback_fails_closed_without_exposing_pin(monkeypatch):
    pin = "739104-secret-sentinel"
    monkeypatch.delattr(hashlib, "scrypt", raising=False)
    monkeypatch.setattr(
        office_workspace_builder,
        "_load_in_process_scrypt",
        lambda: None,
        raising=False,
    )

    with pytest.raises(RuntimeError, match="Python runtime with hashlib.scrypt") as error:
        office_workspace_builder._derive_scrypt_hex(pin, bytes(range(16)))

    assert pin not in str(error.value)


def test_monthly_rollover_is_append_only_and_rejects_prior_period(tmp_path):
    root = create_office_workspace(tmp_path, name="Monthly", approver="Owner", pin="482913")

    create_period(root, "2026-07")
    create_period(root, "2026-08", style_reference=None)

    assert (root / "03_CURRENT_INPUTS/2026-07").is_dir()
    assert (root / "03_CURRENT_INPUTS/2026-08").is_dir()
    with pytest.raises(ValueError, match="already exists"):
        create_period(root, "2026-08")
    with pytest.raises(ValueError, match="append-only"):
        create_period(root, "2026-06")


@pytest.mark.parametrize("period_id", ["2026-13", "2026-7", "July-2026"])
def test_invalid_period_ids_are_rejected(tmp_path, period_id):
    root = create_office_workspace(tmp_path, name="Monthly", approver="Owner", pin="482913")

    with pytest.raises(ValueError, match="YYYY-MM"):
        create_period(root, period_id)


def test_symlinked_workspace_components_are_rejected(tmp_path):
    root = create_office_workspace(tmp_path, name="Monthly", approver="Owner", pin="482913")
    target = root / "03_CURRENT_INPUTS"
    relocated = root / "03_CURRENT_INPUTS_REAL"
    target.rename(relocated)
    os.symlink(relocated, target)

    with pytest.raises(ValueError, match="symlink"):
        create_period(root, "2026-07")


def test_inspect_period_writes_source_manifest_and_moves_to_questioning(tmp_path):
    root = create_office_workspace(tmp_path, name="Monthly", approver="Owner", pin="482913")
    create_period(root, "2026-07")
    write_text(root / "01_APPROVED_PAST_OUTPUTS" / "approved.md", "# Past\n売上: 100\n")
    write_text(root / "03_CURRENT_INPUTS/2026-07" / "current.md", "# Current\n売上: 120\n")

    period = inspect_period(root, "2026-07")

    manifest_path = root / ".system/periods/2026-07/source_manifest.json"
    assert period["stage"] == "questioning"
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["counts"]["accepted"] == 2
    assert period["pending_question_ids"] == ["audience"]


def test_inspect_period_persists_supporting_manifest_metadata_without_text_leaks(tmp_path):
    root = create_office_workspace(tmp_path, name="Monthly", approver="Owner", pin="482913")
    create_period(root, "2026-07")
    supporting_text = "- Vendor escalation is reviewed every Tuesday.\n"
    write_text(root / "01_APPROVED_PAST_OUTPUTS" / "approved.md", "# Past\n売上: 100\n")
    write_text(root / "02_PAST_SUPPORTING_FILES" / "recurring-notes.md", supporting_text)
    write_text(root / "03_CURRENT_INPUTS/2026-07" / "current.md", "# Current\n売上: 120\n")

    period = inspect_period(root, "2026-07")

    manifest_path = root / ".system/periods/2026-07/source_manifest.json"
    manifest_text = manifest_path.read_text(encoding="utf-8")
    manifest = json.loads(manifest_text)
    supporting = next(
        item for item in manifest["accepted"] if item["source_role"] == "past_supporting"
    )

    assert period["stage"] == "questioning"
    assert manifest["counts"]["accepted"] == 3
    assert [item["source_role"] for item in manifest["accepted"]] == [
        "past_output",
        "past_supporting",
        "current_material",
    ]
    assert supporting["name"] == "recurring-notes.md"
    assert "text" not in supporting
    assert supporting_text not in manifest_text


def test_state_machine_and_question_validation_are_enforced(tmp_path):
    root = create_office_workspace(tmp_path, name="Monthly", approver="Owner", pin="482913")
    create_period(root, "2026-07")

    with pytest.raises(ValueError, match="questioning"):
        save_answer(root, "2026-07", "audience", "Owner team")
    with pytest.raises(ValueError, match="ready_for_review"):
        approve_draft(root, "2026-07", "monthly_report.md", "Owner", "482913")

    write_text(root / "03_CURRENT_INPUTS/2026-07" / "current.md", "# Current\n売上: 120\n")
    inspect_period(root, "2026-07")

    with pytest.raises(ValueError, match="unknown question"):
        save_answer(root, "2026-07", "unknown", "nope")

    saved = save_answer(root, "2026-07", "audience", "Owner team")
    assert saved["stage"] == "ready_for_run"


def test_promote_run_result_writes_missing_question_artifacts_without_overwriting(tmp_path):
    root = setup_ready_for_run(tmp_path)

    first = promote_run_result(
        root,
        "2026-07",
        "run-1",
        {
            "missing_questions": [{"id": "totals", "question": "What is the final total?", "required": True}],
            "draft_markdown": "# ignored draft\n",
        },
    )
    save_answer(root, "2026-07", "totals", "220")
    second = promote_run_result(
        root,
        "2026-07",
        "run-2",
        {
            "missing_questions": [{"id": "totals", "question": "What is the final total?", "required": True}],
            "draft_markdown": "",
        },
    )

    question_dir = root / "04_QUESTIONS/2026-07"
    question_files = sorted(path.name for path in question_dir.glob("*.json"))
    assert first["stage"] == "questioning"
    assert second["stage"] == "questioning"
    assert question_files == ["run-1_missing_questions.json", "run-2_missing_questions.json"]


def test_question_json_publication_is_atomic_and_collision_safe(tmp_path, monkeypatch):
    root = setup_ready_for_run(tmp_path)
    question_dir = root / "04_QUESTIONS/2026-07"
    intended = question_dir / "run-race_missing_questions.json"
    raced_content = "raced destination\n"
    write_started = threading.Event()
    release_write = threading.Event()
    original_write_all = office_workspace_builder._write_all
    result = []
    errors = []

    def pause_question_write(descriptor, payload):
        if b'"run_id": "run-race"' not in payload:
            return original_write_all(descriptor, payload)
        midpoint = len(payload) // 2
        original_write_all(descriptor, payload[:midpoint])
        write_started.set()
        if not release_write.wait(timeout=5):
            raise RuntimeError("test timed out waiting to resume question publication")
        original_write_all(descriptor, payload[midpoint:])

    def promote_questions():
        try:
            result.append(
                promote_run_result(
                    root,
                    "2026-07",
                    "run-race",
                    {
                        "missing_questions": [
                            {"id": "totals", "question": "What is the final total?", "required": True}
                        ],
                        "draft_markdown": "",
                    },
                )
            )
        except Exception as error:
            errors.append(error)

    monkeypatch.setattr(office_workspace_builder, "_write_all", pause_question_write)
    worker = threading.Thread(target=promote_questions)
    worker.start()
    assert write_started.wait(timeout=5)
    visible_during_write = intended.exists()
    racer = write_text(question_dir / "racer.tmp", raced_content)
    os.replace(racer, intended)
    release_write.set()
    worker.join(timeout=5)

    assert not worker.is_alive()
    assert errors == []
    assert visible_during_write is False
    assert intended.read_text(encoding="utf-8") == raced_content
    artifact = result[0]["latest_question_artifact"]
    assert artifact["name"] == "run-race_missing_questions__2.json"
    published = json.loads((question_dir / artifact["name"]).read_text(encoding="utf-8"))
    assert published["run_id"] == "run-race"
    assert not any(path.name.endswith(".tmp") for path in question_dir.iterdir())


def test_promote_run_result_uses_collision_safe_draft_names(tmp_path):
    root = setup_ready_for_run(tmp_path)
    existing = root / "05_DRAFTS/2026-07/monthly_report.md"
    existing.write_text("existing", encoding="utf-8")

    promoted = promote_run_result(
        root,
        "2026-07",
        "run-1",
        {"missing_questions": [], "draft_markdown": "# Draft\nhello\n"},
    )

    assert promoted["stage"] == "ready_for_review"
    assert existing.read_text(encoding="utf-8") == "existing"
    assert promoted["current_draft"]["name"] == "monthly_report__2.md"
    assert (root / "05_DRAFTS/2026-07/monthly_report__2.md").read_text(encoding="utf-8") == "# Draft\nhello\n"


def test_inspect_period_rejects_symlinked_source_manifest(tmp_path):
    root = create_office_workspace(tmp_path, name="Monthly", approver="Owner", pin="482913")
    create_period(root, "2026-07")
    write_text(root / "03_CURRENT_INPUTS/2026-07/current.md", "# Current\n")
    outside = write_text(tmp_path / "outside-manifest.json", "outside\n")
    os.symlink(outside, root / ".system/periods/2026-07/source_manifest.json")

    with pytest.raises(ValueError, match="symlink"):
        inspect_period(root, "2026-07")

    assert outside.read_text(encoding="utf-8") == "outside\n"


def test_inspect_period_rejects_symlinked_period_state_component(tmp_path):
    root = create_office_workspace(tmp_path, name="Monthly", approver="Owner", pin="482913")
    create_period(root, "2026-07")
    period_root = root / ".system/periods/2026-07"
    relocated = root / ".system/periods/2026-07-real"
    period_root.rename(relocated)
    os.symlink(relocated, period_root)

    with pytest.raises(ValueError, match="symlink"):
        inspect_period(root, "2026-07")


def test_approve_draft_rejects_symlinked_draft(tmp_path):
    root = setup_ready_for_run(tmp_path)
    promoted = promote_run_result(
        root,
        "2026-07",
        "run-1",
        {"missing_questions": [], "draft_markdown": "# Draft\nJuly\n"},
    )
    draft_path = root / promoted["current_draft"]["path"]
    outside = write_text(tmp_path / "outside-draft.md", draft_path.read_text(encoding="utf-8"))
    draft_path.unlink()
    os.symlink(outside, draft_path)

    with pytest.raises(ValueError, match="symlink"):
        approve_draft(root, "2026-07", promoted["current_draft"]["name"], "Owner", "482913")

    assert not (root / "06_APPROVED_OUTPUTS/2026-07" / promoted["current_draft"]["name"]).exists()


def test_approve_draft_rejects_symlinked_audit_file_without_escape(tmp_path):
    root = setup_ready_for_run(tmp_path)
    promoted = promote_run_result(
        root,
        "2026-07",
        "run-1",
        {"missing_questions": [], "draft_markdown": "# Draft\nJuly\n"},
    )
    outside = write_text(tmp_path / "outside-audit.jsonl", "outside\n")
    os.symlink(outside, root / "07_AUDIT/audit.jsonl")

    with pytest.raises(ValueError, match="symlink"):
        approve_draft(root, "2026-07", promoted["current_draft"]["name"], "Owner", "482913")

    assert outside.read_text(encoding="utf-8") == "outside\n"
    assert not (root / "06_APPROVED_OUTPUTS/2026-07" / promoted["current_draft"]["name"]).exists()


def test_approve_draft_rejects_symlinked_approval_lock(tmp_path):
    root = setup_ready_for_run(tmp_path)
    promoted = promote_run_result(
        root,
        "2026-07",
        "run-1",
        {"missing_questions": [], "draft_markdown": "# Draft\nJuly\n"},
    )
    outside = write_text(tmp_path / "outside-lock", "outside\n")
    os.symlink(outside, root / ".system/approval.lock")

    with pytest.raises(ValueError, match="lock.*symlink"):
        approve_draft(root, "2026-07", promoted["current_draft"]["name"], "Owner", "482913")

    assert outside.read_text(encoding="utf-8") == "outside\n"
    assert list((root / "06_APPROVED_OUTPUTS/2026-07").iterdir()) == []


def test_approve_draft_preserves_stale_lock_for_manual_recovery(tmp_path):
    root = setup_ready_for_run(tmp_path)
    promoted = promote_run_result(
        root,
        "2026-07",
        "run-1",
        {"missing_questions": [], "draft_markdown": "# Draft\nJuly\n"},
    )
    lock_path = write_text(root / ".system/approval.lock", '{"pid": 999999}\n')

    with pytest.raises(ValueError, match="remove.*manually"):
        approve_draft(root, "2026-07", promoted["current_draft"]["name"], "Owner", "482913")

    assert lock_path.read_text(encoding="utf-8") == '{"pid": 999999}\n'
    assert list((root / "06_APPROVED_OUTPUTS/2026-07").iterdir()) == []


def test_concurrent_approval_allows_exactly_one_mutation(tmp_path, monkeypatch):
    root = setup_ready_for_run(tmp_path)
    promoted = promote_run_result(
        root,
        "2026-07",
        "run-1",
        {"missing_questions": [], "draft_markdown": "# Draft\nJuly\n"},
    )
    entered_pin_check = threading.Event()
    release_first = threading.Event()
    original_pin_matches = office_workspace_state._pin_matches
    call_count = 0
    first_results = []
    first_errors = []

    def pause_first_pin_check(workspace_state, pin):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            entered_pin_check.set()
            if not release_first.wait(timeout=5):
                raise RuntimeError("test timed out waiting to resume approval")
        return original_pin_matches(workspace_state, pin)

    def first_approval():
        try:
            first_results.append(
                approve_draft(root, "2026-07", promoted["current_draft"]["name"], "Owner", "482913")
            )
        except Exception as error:
            first_errors.append(error)

    monkeypatch.setattr(office_workspace_state, "_pin_matches", pause_first_pin_check)
    worker = threading.Thread(target=first_approval)
    worker.start()
    assert entered_pin_check.wait(timeout=5)
    second_error = None
    try:
        approve_draft(root, "2026-07", promoted["current_draft"]["name"], "Owner", "482913")
    except Exception as error:
        second_error = error
    finally:
        release_first.set()
        worker.join(timeout=5)

    assert not worker.is_alive()
    assert first_errors == []
    assert len(first_results) == 1
    assert isinstance(second_error, ValueError)
    assert "approval is already in progress" in str(second_error)
    approved_files = list((root / "06_APPROVED_OUTPUTS/2026-07").iterdir())
    assert len(approved_files) == 1
    audit_path = root / "07_AUDIT/audit.jsonl"
    entries = [json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines()]
    assert len(entries) == 1
    assert entries[0]["previous_audit_hash"] is None
    assert entries[0]["audit_hash"] == audit_entry_hash(entries[0])
    assert not (root / ".system/approval.lock").exists()


def test_style_reference_rejects_planted_unapproved_output(tmp_path):
    root = create_office_workspace(tmp_path, name="Monthly", approver="Owner", pin="482913")
    create_period(root, "2026-07")
    planted = write_text(root / "06_APPROVED_OUTPUTS/2026-07/planted.md", "# Planted\n")

    with pytest.raises(ValueError, match="recorded approved output"):
        create_period(
            root,
            "2026-08",
            style_reference={
                "relative_path": "06_APPROVED_OUTPUTS/2026-07/planted.md",
                "sha256": hashlib.sha256(planted.read_bytes()).hexdigest(),
            },
        )


def test_style_reference_rejects_symlinked_approved_output(tmp_path):
    root = setup_ready_for_run(tmp_path)
    promoted = promote_run_result(
        root,
        "2026-07",
        "run-1",
        {"missing_questions": [], "draft_markdown": "# Draft\nJuly\n"},
    )
    approved = approve_draft(root, "2026-07", promoted["current_draft"]["name"], "Owner", "482913")
    approved_output = approved["approved_outputs"][0]
    approved_path = root / approved_output["path"]
    outside = write_text(tmp_path / "outside-approved.md", approved_path.read_text(encoding="utf-8"))
    approved_path.unlink()
    os.symlink(outside, approved_path)

    with pytest.raises(ValueError, match="symlink"):
        create_period(
            root,
            "2026-08",
            style_reference={
                "relative_path": approved_output["path"],
                "sha256": approved_output["sha256"],
            },
        )


def test_approve_draft_checks_pin_and_appends_hash_chained_audit(tmp_path):
    root = setup_ready_for_run(tmp_path, "2026-07")
    promoted = promote_run_result(
        root,
        "2026-07",
        "run-1",
        {"missing_questions": [], "draft_markdown": "# Draft\nJuly\n"},
    )

    with pytest.raises(ValueError, match="PIN"):
        approve_draft(root, "2026-07", promoted["current_draft"]["name"], "Owner", "000000")

    approved = approve_draft(root, "2026-07", promoted["current_draft"]["name"], "Owner", "482913")
    approved_path = root / "06_APPROVED_OUTPUTS/2026-07" / promoted["current_draft"]["name"]
    audit_path = root / "07_AUDIT/audit.jsonl"

    assert approved["stage"] == "approved"
    assert approved_path.exists()
    assert hashlib.sha256(approved_path.read_bytes()).hexdigest() == approved["current_draft"]["sha256"]

    create_period(
        root,
        "2026-08",
        style_reference={
            "relative_path": "06_APPROVED_OUTPUTS/2026-07/{}".format(promoted["current_draft"]["name"]),
            "sha256": approved["current_draft"]["sha256"],
        },
    )
    write_text(root / "03_CURRENT_INPUTS/2026-08" / "current.md", "# Current\n売上: 150\n")
    inspect_period(root, "2026-08")
    save_answer(root, "2026-08", "audience", "Owner team")
    august = promote_run_result(
        root,
        "2026-08",
        "run-2",
        {"missing_questions": [], "draft_markdown": "# Draft\nAugust\n"},
    )
    approve_draft(root, "2026-08", august["current_draft"]["name"], "Owner", "482913")

    entries = [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(entries) == 2
    assert entries[0]["previous_audit_hash"] is None
    assert entries[0]["audit_hash"] == audit_entry_hash(entries[0])
    assert entries[1]["previous_audit_hash"] == entries[0]["audit_hash"]
    assert entries[1]["audit_hash"] == audit_entry_hash(entries[1])
