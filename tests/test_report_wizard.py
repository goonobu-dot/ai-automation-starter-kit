import hashlib
import json
import os
from pathlib import Path

import pytest

from ai_automation_kit.core import report_wizard
from ai_automation_kit.core.report_wizard import (
    approve_report,
    answer_current_question,
    build_report_workspace,
    confirm_folder_plan,
    create_session,
    inspect_session,
    load_session,
    set_session_goal,
    session_status,
)


def write_source(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def make_inputs(tmp_path, report_type="monthly"):
    past = write_source(
        tmp_path / "past" / "completed.md",
        "# Executive Summary\n売上: 100\n\n# Metrics\n- stable\n\n# Notes\nold narrative\n",
    )
    current = write_source(
        tmp_path / "current" / "metrics.csv",
        "metric,value\nsales,120\n",
    )
    return past, current


def answer_all_questions(workspace):
    while True:
        state = load_session(workspace)
        question = state["current_question"]
        if not question:
            return state
        answer_current_question(workspace, "Owner-confirmed answer")


def test_report_wizard_inspects_inputs_and_persists_folder_plan(tmp_path):
    past, current = make_inputs(tmp_path)
    workspace = tmp_path / "workspace"

    state = create_session(workspace, "monthly", "ja")
    inspected = inspect_session(workspace, [past], [current])
    reloaded = load_session(workspace)

    assert state["stage"] == "created"
    assert inspected["stage"] == "inspection_ready"
    assert reloaded == inspected
    assert inspected["folder_plan"]["past_completed_reports"]
    assert inspected["schema_proposal"]["sections"]
    assert inspected["current_question"]["id"] == "report_audience"
    assert inspected["folder_plan"]["current_materials"][0]["destination"] == "02_current_materials/metrics"


@pytest.mark.parametrize(
    ("report_type", "heading"),
    [("daily", "# Daily Report"), ("weekly", "# Weekly Report"), ("monthly", "# Monthly Report")],
)
def test_build_uses_report_type_specific_path_and_heading(tmp_path, report_type, heading):
    past, current = make_inputs(tmp_path, report_type)
    workspace = tmp_path / report_type
    create_session(workspace, report_type)
    inspect_session(workspace, [past], [current])
    confirm_folder_plan(workspace)
    answer_all_questions(workspace)

    built = build_report_workspace(workspace)

    assert built["artifacts"]["draft"].endswith("06_drafts/{}_report_draft.md".format(report_type))
    assert heading in Path(built["artifacts"]["draft"]).read_text(encoding="utf-8")
    assert (workspace / "03_templates/{}_report_template.md".format(report_type)).exists()


def test_state_persistence_is_atomic_and_resume_does_not_reset(tmp_path):
    workspace = tmp_path / "workspace"
    create_session(workspace, "daily")
    first = load_session(workspace)
    answer = inspect_session(workspace, [], [])
    assert answer["stage"] == "inspection_ready"
    resumed = load_session(workspace)

    assert resumed["created_at"] == first["created_at"]
    assert resumed["updated_at"] != first["updated_at"]
    assert (workspace / "report_wizard_state.json").exists()
    assert not list(workspace.glob("report_wizard_state.json.*.tmp"))


def test_corrupt_or_wrong_version_state_fails_actionably(tmp_path):
    workspace = tmp_path / "workspace"
    create_session(workspace, "daily")
    state_path = workspace / "report_wizard_state.json"
    original = json.loads(state_path.read_text(encoding="utf-8"))
    state_path.write_text("{broken", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid JSON"):
        load_session(workspace)

    payload = original
    payload["schema_version"] = 999
    state_path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="schema_version"):
        load_session(workspace)


def test_schema_uses_headings_and_labels_with_half_threshold_and_references(tmp_path):
    past_a = write_source(tmp_path / "past" / "a.md", "# Common\n# A Only\n売上:\n")
    past_b = write_source(tmp_path / "past" / "b.md", "# Common\n# B Only\n利益：\n")
    past_c = write_source(tmp_path / "past" / "c.md", "# Common\n# A Only\n")
    workspace = tmp_path / "workspace"
    create_session(workspace, "monthly")

    state = inspect_session(workspace, [past_a, past_b, past_c], [])
    sections = {section["name"]: section for section in state["schema_proposal"]["sections"]}
    fields = {field["name"]: field for field in state["schema_proposal"]["fields"]}

    assert sections["Common"]["required"] is True
    assert sections["A Only"]["required"] is True
    assert sections["B Only"]["required"] is False
    assert fields["売上"]["required"] is False
    assert sections["Common"]["source_references"][0]["sha256"] == hashlib.sha256(past_a.read_bytes()).hexdigest()


def test_schema_order_is_normalized_and_current_conflicts_create_question(tmp_path):
    past_a = write_source(tmp_path / "past" / "a.md", "# First\n# Second\n")
    past_b = write_source(tmp_path / "past" / "b.md", "# Second\n# First\n")
    current_a = write_source(tmp_path / "current" / "a.md", "売上: 10\n")
    current_b = write_source(tmp_path / "current" / "b.md", "売上: 20\n")
    workspace = tmp_path / "workspace"
    create_session(workspace, "weekly")

    state = inspect_session(workspace, [past_a, past_b], [current_a, current_b])
    names = [section["name"] for section in state["schema_proposal"]["sections"]]

    assert names == ["First", "Second"]
    assert any(question["id"].startswith("conflict_") for question in state["question_queue"])


def test_folder_correction_rejects_absolute_and_traversal_destinations(tmp_path):
    past, current = make_inputs(tmp_path)
    workspace = tmp_path / "workspace"
    create_session(workspace, "monthly")
    inspect_session(workspace, [past], [current])

    with pytest.raises(ValueError, match="relative destination"):
        confirm_folder_plan(workspace, {str(current): "../outside"})
    with pytest.raises(ValueError, match="relative destination"):
        confirm_folder_plan(workspace, {str(current): "/tmp/outside"})


def test_confirmation_copies_only_accepted_files_and_keeps_copy_rejections_visible(tmp_path):
    past, current = make_inputs(tmp_path)
    workspace = tmp_path / "workspace"
    create_session(workspace, "monthly")
    inspect_session(workspace, [past], [current])
    past.unlink()

    state = confirm_folder_plan(workspace)

    assert state["stage"] == "questioning"
    assert any(item["status"] == "copy_rejected" for item in state["copy_outcomes"])
    assert not (workspace / "00_intake/past/completed.md").exists()


def test_valid_folder_correction_controls_final_copy_destination_and_preserves_source(tmp_path):
    past, current = make_inputs(tmp_path)
    before_bytes = current.read_bytes()
    before_mtime = current.stat().st_mtime_ns
    workspace = tmp_path / "workspace"
    create_session(workspace, "monthly")
    inspect_session(workspace, [past], [current])

    state = confirm_folder_plan(workspace, {str(current): "02_current_materials/notes"})
    final_path = workspace / "02_current_materials/notes" / current.name
    copied = [item for item in state["copy_outcomes"] if item.get("original_path") == str(current)]

    assert final_path.read_bytes() == before_bytes
    assert Path(copied[0]["copied_path"]) == final_path
    assert not (workspace / "00_intake/current" / current.name).exists()
    assert current.read_bytes() == before_bytes
    assert current.stat().st_mtime_ns == before_mtime


def test_confirmation_resumes_partial_and_existing_destination_without_duplicates(tmp_path):
    past, current = make_inputs(tmp_path)
    workspace = tmp_path / "workspace"
    create_session(workspace, "daily")
    inspect_session(workspace, [past], [current])
    state = load_session(workspace)
    destination = workspace / "02_current_materials/metrics"
    final_path = destination / current.name
    destination.mkdir(parents=True)
    final_path.write_bytes(b"partial")
    state["stage"] = "folder_plan_confirmed"
    (workspace / "report_wizard_state.json").write_text(json.dumps(state), encoding="utf-8")

    resumed = confirm_folder_plan(workspace)
    assert resumed["stage"] == "questioning"
    assert final_path.read_bytes() == current.read_bytes()

    resumed["stage"] = "folder_plan_confirmed"
    (workspace / "report_wizard_state.json").write_text(json.dumps(resumed), encoding="utf-8")
    rerun = confirm_folder_plan(workspace)
    assert rerun["stage"] == "questioning"
    assert final_path.read_bytes() == current.read_bytes()
    assert not (destination / "metrics__2" / current.name).exists()
    assert len(list(destination.glob("metrics.csv*"))) == 1


@pytest.mark.parametrize("role", ["past", "current"])
@pytest.mark.parametrize("mutation", ["delete", "change"])
def test_source_integrity_failure_after_inspection_blocks_readiness_and_approval(tmp_path, role, mutation):
    past, current = make_inputs(tmp_path)
    workspace = tmp_path / "workspace-{}-{}".format(role, mutation)
    create_session(workspace, "monthly")
    inspect_session(workspace, [past], [current])
    target = past if role == "past" else current
    if mutation == "delete":
        target.unlink()
    else:
        target.write_text("changed after inspection", encoding="utf-8")

    confirmed = confirm_folder_plan(workspace)
    assert any(item["status"] == "copy_rejected" for item in confirmed["copy_outcomes"])
    answer_all_questions(workspace)
    built = build_report_workspace(workspace)

    assert built["stage"] != "ready_for_human_review"
    assert any(item["id"].startswith("source_copy_") for item in built["unresolved_items"])
    with pytest.raises(ValueError, match="unresolved"):
        approve_report(workspace, "Owner")


@pytest.mark.parametrize(
    ("field", "bad_value"),
    [
        ("schema_version", "one"),
        ("stage", "not-a-stage"),
        ("report_type", "quarterly"),
        ("language", []),
        ("accepted", {}),
        ("rejected", {}),
        ("skipped_inputs", {}),
        ("copy_outcomes", {}),
        ("folder_plan", []),
        ("schema_proposal", []),
        ("question_queue", {}),
        ("answers", []),
        ("unresolved_items", {}),
        ("artifacts", []),
        ("approval", []),
    ],
)
def test_load_rejects_invalid_minimum_state_fields(tmp_path, field, bad_value):
    workspace = tmp_path / field
    create_session(workspace, "daily")
    state_path = workspace / "report_wizard_state.json"
    payload = json.loads(state_path.read_text(encoding="utf-8"))
    payload[field] = bad_value
    state_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="invalid state field.*{}".format(field)):
        load_session(workspace)


@pytest.mark.parametrize("missing_field", ["skipped_inputs", "copy_outcomes"])
def test_load_rejects_missing_state_fields_with_actionable_error(tmp_path, missing_field):
    workspace = tmp_path / "missing-{}".format(missing_field)
    create_session(workspace, "daily")
    state_path = workspace / "report_wizard_state.json"
    payload = json.loads(state_path.read_text(encoding="utf-8"))
    del payload[missing_field]
    state_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="invalid state field.*{}".format(missing_field)):
        load_session(workspace)


def test_load_rejects_non_object_state_root_with_actionable_value_error(tmp_path):
    workspace = tmp_path / "workspace"
    create_session(workspace, "daily")
    (workspace / "report_wizard_state.json").write_text("[]", encoding="utf-8")

    with pytest.raises(ValueError, match="invalid state root"):
        load_session(workspace)


@pytest.mark.parametrize(
    ("change", "pattern"),
    [
        ("not-a-dict", "question_queue\\[0\\].*expected an object"),
        ({"id": None}, "question_queue\\[0\\]\\.id"),
        ({"prompt": 1}, "question_queue\\[0\\]\\.prompt"),
        ({"required": "yes"}, "question_queue\\[0\\]\\.required"),
        ({"status": "unknown"}, "question_queue\\[0\\]\\.status"),
    ],
)
def test_load_rejects_malformed_question_queue_items(tmp_path, change, pattern):
    workspace = tmp_path / "queue-{}".format(len(str(change)))
    create_session(workspace, "daily")
    state_path = workspace / "report_wizard_state.json"
    payload = json.loads(state_path.read_text(encoding="utf-8"))
    if change == "not-a-dict":
        payload["question_queue"] = ["not-a-question"]
    else:
        payload["question_queue"][0].update(change)
    state_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match=pattern):
        load_session(workspace)


@pytest.mark.parametrize(
    ("field", "nested_field"),
    [("folder_plan", "current_materials"), ("schema_proposal", "sections")],
)
def test_load_rejects_non_object_nested_records(tmp_path, field, nested_field):
    workspace = tmp_path / "nested-{}".format(field)
    create_session(workspace, "daily")
    state_path = workspace / "report_wizard_state.json"
    payload = json.loads(state_path.read_text(encoding="utf-8"))
    payload[field][nested_field] = [None]
    state_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="invalid state field.*{}.*list of objects".format(nested_field)):
        load_session(workspace)


def test_final_destination_symlink_is_rejected_without_writing_outside_workspace(tmp_path):
    past, current = make_inputs(tmp_path)
    workspace = tmp_path / "workspace"
    outside = tmp_path / "outside"
    outside.mkdir()
    create_session(workspace, "daily")
    inspect_session(workspace, [past], [current])
    destination_root = workspace / "02_current_materials"
    destination_root.mkdir()
    (destination_root / "metrics").symlink_to(outside, target_is_directory=True)

    state = confirm_folder_plan(workspace)

    assert any(item["status"] == "copy_rejected" for item in state["copy_outcomes"])
    assert not (outside / current.name).exists()


def test_ancestor_symlink_swap_before_child_creation_is_rejected(tmp_path, monkeypatch):
    past, current = make_inputs(tmp_path)
    workspace = tmp_path / "workspace"
    outside = tmp_path / "outside"
    outside.mkdir()
    create_session(workspace, "daily")
    inspect_session(workspace, [past], [current])
    destination_root = workspace / "02_current_materials"
    destination_root.mkdir()
    original_mkdir = os.mkdir
    triggered = {"value": False}

    def swap_before_metrics_creation(path, mode=0o777, *, dir_fd=None):
        if Path(str(path)).name == "metrics" and dir_fd is not None and not triggered["value"]:
            triggered["value"] = True
            backup = workspace / "02_current_materials.backup"
            destination_root.rename(backup)
            destination_root.symlink_to(outside, target_is_directory=True)
        return original_mkdir(path, mode, dir_fd=dir_fd)

    monkeypatch.setattr(os, "mkdir", swap_before_metrics_creation)
    state = confirm_folder_plan(workspace)

    assert any(item["status"] == "copy_rejected" for item in state["copy_outcomes"])
    assert not (outside / current.name).exists()


def test_ancestor_symlink_swap_after_traversal_is_rejected(tmp_path, monkeypatch):
    past, current = make_inputs(tmp_path)
    workspace = tmp_path / "workspace"
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "metrics").mkdir()
    create_session(workspace, "daily")
    inspect_session(workspace, [past], [current])
    original_chain = getattr(report_wizard, "_open_destination_chain", None)
    destination_root = workspace / "02_current_materials"
    destination = destination_root / "metrics"
    triggered = {"value": False}

    def swap_after_traversal(workspace_arg, destination_arg, *args, **kwargs):
        if original_chain is None:
            return None
        chain = original_chain(workspace_arg, destination_arg, *args, **kwargs)
        if Path(workspace_arg) / destination_arg == destination and not triggered["value"]:
            triggered["value"] = True
            backup = workspace / "02_current_materials.backup"
            destination_root.rename(backup)
            destination_root.symlink_to(outside, target_is_directory=True)
        return chain

    monkeypatch.setattr(report_wizard, "_open_destination_chain", swap_after_traversal, raising=False)
    state = confirm_folder_plan(workspace)

    assert any(item["status"] == "copy_rejected" for item in state["copy_outcomes"])
    assert not (outside / "metrics" / current.name).exists()


def test_post_publish_identity_race_removes_publication_and_records_rejection(tmp_path, monkeypatch):
    past, current = make_inputs(tmp_path)
    workspace = tmp_path / "workspace"
    create_session(workspace, "daily")
    inspect_session(workspace, [past], [current])
    original_verify = report_wizard._verify_directory_identity

    def fail_after_publish(path, directory_fd, expected_identity, expected_realpath, phase):
        if phase == "after_publish":
            return False
        return original_verify(path, directory_fd, expected_identity, expected_realpath, phase)

    monkeypatch.setattr(report_wizard, "_verify_directory_identity", fail_after_publish, raising=False)
    state = confirm_folder_plan(workspace)

    rejected = [item for item in state["copy_outcomes"] if item["status"] == "copy_rejected"]
    assert rejected
    assert "destination" in rejected[0]["reason"]
    assert not (workspace / "02_current_materials/metrics" / current.name).exists()


def test_reused_hash_rechecks_ancestor_identity_and_recovers_on_retry(tmp_path, monkeypatch):
    past, current = make_inputs(tmp_path)
    workspace = tmp_path / "workspace"
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "metrics").mkdir()
    create_session(workspace, "daily")
    inspect_session(workspace, [past], [current])
    destination_root = workspace / "02_current_materials"
    destination = destination_root / "metrics"
    destination.mkdir(parents=True)
    final_path = destination / current.name
    final_path.write_bytes(current.read_bytes())
    state = load_session(workspace)
    state["stage"] = "folder_plan_confirmed"
    state["operation_journal"] = {
        "operation_id": "retry-test",
        "operation": "confirm_copy",
        "status": "in_progress",
        "current_item": None,
        "completed_items": [],
        "outcomes": [],
    }
    (workspace / "report_wizard_state.json").write_text(json.dumps(state), encoding="utf-8")
    original_hash = report_wizard._hash_at_dirfd
    triggered = {"value": False}

    def swap_after_matching_hash(directory_fd, name):
        result = original_hash(directory_fd, name)
        if name == current.name and not triggered["value"]:
            triggered["value"] = True
            backup = workspace / "02_current_materials.backup"
            destination_root.rename(backup)
            destination_root.symlink_to(outside, target_is_directory=True)
        return result

    monkeypatch.setattr(report_wizard, "_hash_at_dirfd", swap_after_matching_hash)
    first = confirm_folder_plan(workspace)
    assert first["stage"] == "folder_plan_confirmed"
    assert any(item["status"] == "copy_rejected" for item in first["copy_outcomes"])
    assert any(item["id"].startswith("source_copy_") for item in first["unresolved_items"])
    assert (workspace / "00_intake/current" / current.name).exists()
    assert not (outside / "metrics" / current.name).exists()

    destination_root.unlink()
    (workspace / "02_current_materials.backup").rename(destination_root)
    monkeypatch.setattr(report_wizard, "_hash_at_dirfd", original_hash)
    recovered = confirm_folder_plan(workspace)

    assert recovered["stage"] == "questioning"
    assert final_path.read_bytes() == current.read_bytes()
    assert not any(item["id"].startswith("source_copy_") for item in recovered["unresolved_items"])
    assert not list((workspace / "00_intake/current").glob("metrics*.csv"))


def test_skipped_required_question_is_represented_and_can_recover_to_approval(tmp_path):
    past, current = make_inputs(tmp_path)
    workspace = tmp_path / "workspace"
    create_session(workspace, "monthly")
    inspect_session(workspace, [past], [current])
    confirm_folder_plan(workspace)
    first_id = load_session(workspace)["current_question"]["id"]

    skipped = answer_current_question(workspace, "", skipped=True)
    assert skipped["current_question"]["id"] != first_id
    while load_session(workspace)["current_question"]["id"] != first_id:
        answer_current_question(workspace, "confirmed answer")
    recovered = load_session(workspace)
    assert recovered["stage"] == "questioning"
    assert recovered["current_question"]["id"] == first_id
    assert any(item["id"] == first_id for item in recovered["unresolved_items"])

    answered = answer_current_question(workspace, "confirmed audience")
    assert answered["current_question"] is None
    assert not any(item["id"] == first_id for item in answered["unresolved_items"])
    built = build_report_workspace(workspace)
    approved = approve_report(workspace, "Owner")
    assert built["stage"] == "ready_for_human_review"
    assert approved["stage"] == "approved"


def test_conflicting_values_are_redacted_from_state_questions_and_artifacts(tmp_path):
    past = write_source(tmp_path / "past" / "past.md", "# Metrics\nRevenue: 1\n")
    current_a = write_source(tmp_path / "current" / "a.md", "Revenue: confidential-A\n")
    current_b = write_source(tmp_path / "current" / "b.md", "Revenue: confidential-B\n")
    workspace = tmp_path / "workspace"
    create_session(workspace, "weekly")
    inspected = inspect_session(workspace, [past], [current_a, current_b])
    serialized_state = json.dumps(inspected, ensure_ascii=False)
    assert "confidential-A" not in serialized_state
    assert "confidential-B" not in serialized_state
    conflict = inspected["schema_proposal"]["conflicts"][0]
    assert "value_hashes" in conflict
    assert "source_references" in conflict
    assert "values" not in conflict

    confirm_folder_plan(workspace)
    answer_all_questions(workspace)
    build_report_workspace(workspace)
    generated_roots = ["03_templates", "04_ai_analysis", "05_grill_me_questions", "06_drafts", "07_approval"]
    for root in generated_roots:
        for path in (workspace / root).rglob("*"):
            if path.is_file():
                content = path.read_text(encoding="utf-8")
                assert "confidential-A" not in content
                assert "confidential-B" not in content


def test_confirmation_journal_resumes_after_interruption_without_staging_duplicates(tmp_path, monkeypatch):
    past, current = make_inputs(tmp_path)
    second = write_source(tmp_path / "current" / "notes.md", "note for the current period")
    workspace = tmp_path / "workspace"
    create_session(workspace, "daily")
    inspect_session(workspace, [past], [current, second])
    original_organize = report_wizard._organize_copy_outcomes
    calls = {"count": 0}

    def interrupt_once(outcomes, state, root):
        calls["count"] += 1
        if calls["count"] == 1:
            raise RuntimeError("simulated organizer interruption")
        return original_organize(outcomes, state, root)

    monkeypatch.setattr(report_wizard, "_organize_copy_outcomes", interrupt_once)
    with pytest.raises(RuntimeError, match="simulated"):
        confirm_folder_plan(workspace)
    interrupted = json.loads((workspace / "report_wizard_state.json").read_text(encoding="utf-8"))
    assert interrupted["operation_journal"]["status"] == "in_progress"
    assert interrupted["operation_journal"]["current_item"]

    monkeypatch.setattr(report_wizard, "_organize_copy_outcomes", original_organize)
    resumed = confirm_folder_plan(workspace)
    assert resumed["stage"] == "questioning"
    assert resumed["operation_journal"]["status"] == "complete"
    staging_files = list((workspace / "00_intake").rglob("*"))
    assert not [path for path in staging_files if path.is_file()]


def test_build_repairs_artifacts_after_interrupted_write(tmp_path, monkeypatch):
    past, current = make_inputs(tmp_path)
    workspace = tmp_path / "workspace"
    create_session(workspace, "daily")
    inspect_session(workspace, [past], [current])
    confirm_folder_plan(workspace)
    answer_all_questions(workspace)
    original_write = report_wizard._write_artifact
    calls = {"count": 0}

    def interrupt_after_first(path, content):
        calls["count"] += 1
        original_write(path, content)
        if calls["count"] == 1:
            raise RuntimeError("simulated artifact interruption")

    monkeypatch.setattr(report_wizard, "_write_artifact", interrupt_after_first)
    with pytest.raises(RuntimeError, match="artifact"):
        build_report_workspace(workspace)
    monkeypatch.setattr(report_wizard, "_write_artifact", original_write)

    repaired = build_report_workspace(workspace)
    assert repaired["stage"] == "ready_for_human_review"
    assert all(path.exists() for path in [
        workspace / "04_ai_analysis/source_manifest.json",
        workspace / "04_ai_analysis/provenance.json",
        workspace / "06_drafts/daily_report_draft.md",
        workspace / "07_approval/approval.json",
    ])


def test_approval_state_is_saved_before_artifact_and_already_approved_repairs_artifact(tmp_path, monkeypatch):
    past, current = make_inputs(tmp_path)
    workspace = tmp_path / "workspace"
    create_session(workspace, "daily")
    inspect_session(workspace, [past], [current])
    confirm_folder_plan(workspace)
    answer_all_questions(workspace)
    build_report_workspace(workspace)
    original_write = report_wizard._write_artifact

    def fail_approval_artifact(path, content):
        if Path(path).name == "approval.json":
            raise RuntimeError("simulated approval artifact interruption")
        return original_write(path, content)

    monkeypatch.setattr(report_wizard, "_write_artifact", fail_approval_artifact)
    with pytest.raises(RuntimeError, match="approval artifact"):
        approve_report(workspace, "Owner")
    assert load_session(workspace)["stage"] == "approved"
    monkeypatch.setattr(report_wizard, "_write_artifact", original_write)
    approval_path = workspace / "07_approval/approval.json"
    approval_path.write_text("stale", encoding="utf-8")
    repaired = approve_report(workspace, "Owner")
    assert repaired["stage"] == "approved"
    assert json.loads(approval_path.read_text(encoding="utf-8"))["status"] == "approved"


@pytest.mark.parametrize(
    ("report_type", "section_heading"),
    [("daily", "# Daily Report"), ("weekly", "# Weekly Report"), ("monthly", "# Monthly Report")],
)
def test_schema_derived_template_and_draft_render_required_optional_evidence(tmp_path, report_type, section_heading):
    past_a = write_source(
        tmp_path / "past" / "a.md",
        "# Common\n# Optional Context\nRevenue: 100\nOptional Label: old\n",
    )
    past_b = write_source(
        tmp_path / "past" / "b.md",
        "# Optional Context\n# Common\nRevenue: 110\n",
    )
    past_c = write_source(tmp_path / "past" / "c.md", "# Common\nRevenue: 120\n")
    current = write_source(tmp_path / "current" / "metrics.csv", "metric,value\nsales,120\n")
    workspace = tmp_path / report_type
    create_session(workspace, report_type)
    inspected = inspect_session(workspace, [past_a, past_b, past_c], [current])
    sections = {item["name"]: item for item in inspected["schema_proposal"]["sections"]}
    fields = {item["name"]: item for item in inspected["schema_proposal"]["fields"]}
    assert sections["Common"]["required"] is True
    assert sections["Optional Context"]["required"] is True
    assert fields["Optional Label"]["required"] is False

    confirm_folder_plan(workspace)
    answer_all_questions(workspace)
    built = build_report_workspace(workspace)
    template = (workspace / "03_templates" / "{}_report_template.md".format(report_type)).read_text(encoding="utf-8")
    draft = Path(built["artifacts"]["draft"]).read_text(encoding="utf-8")

    assert section_heading in template
    for rendered in (template, draft):
        assert "## Common" in rendered
        assert "## Optional Context" in rendered
        assert "Revenue" in rendered
        assert "Optional Label" in rendered
        assert "evidence:" in rendered.lower()
        assert "100" not in rendered
        assert "110" not in rendered


def test_one_question_persists_answer_skip_and_rejects_secret_like_values(tmp_path):
    workspace = tmp_path / "workspace"
    create_session(workspace, "daily")
    inspect_session(workspace, [], [])
    confirm_folder_plan(workspace)

    first = load_session(workspace)["current_question"]
    with pytest.raises(ValueError, match="secret"):
        answer_current_question(workspace, "api_key=sk-test-secret-value")
    assert load_session(workspace)["current_question"]["id"] == first["id"]

    skipped = answer_current_question(workspace, "", skipped=True)
    assert skipped["answers"][first["id"]]["skipped"] is True
    assert skipped["current_question"]["id"] != first["id"]
    first_status = next(item["status"] for item in skipped["question_queue"] if item["id"] == first["id"])
    assert first_status == "skipped"
    with pytest.raises(ValueError, match="empty"):
        answer_current_question(workspace, "   ")


def test_build_is_blocked_without_required_answers_and_approval_is_blocked(tmp_path):
    past, current = make_inputs(tmp_path)
    workspace = tmp_path / "workspace"
    create_session(workspace, "monthly")
    inspect_session(workspace, [past], [current])
    confirm_folder_plan(workspace)

    built = build_report_workspace(workspace)

    assert built["stage"] in {"questioning", "ready_for_draft"}
    assert built["unresolved_items"]
    with pytest.raises(ValueError, match="unresolved"):
        approve_report(workspace, "Owner")


def test_build_generates_evidence_separated_artifacts_and_approval_hash(tmp_path):
    past, current = make_inputs(tmp_path)
    workspace = tmp_path / "workspace"
    create_session(workspace, "monthly")
    inspect_session(workspace, [past], [current])
    confirm_folder_plan(workspace)
    answer_all_questions(workspace)

    built = build_report_workspace(workspace)
    draft_path = Path(built["artifacts"]["draft"])
    draft = draft_path.read_text(encoding="utf-8")
    expected_files = [
        "03_templates/monthly_report_template.md",
        "04_ai_analysis/source_manifest.json",
        "04_ai_analysis/schema_proposal.json",
        "04_ai_analysis/provenance.json",
        "04_ai_analysis/ai_agent_review_instructions.md",
        "05_grill_me_questions/session.json",
        "06_drafts/monthly_report_draft.md",
        "07_approval/approval.json",
    ]

    assert built["stage"] == "ready_for_human_review"
    assert all((workspace / item).exists() for item in expected_files)
    assert "Source-backed evidence" in draft
    assert "User answers" in draft
    assert "Generated wording requiring review" in draft
    assert "Unresolved items" in draft
    instructions = (workspace / "04_ai_analysis/ai_agent_review_instructions.md").read_text(encoding="utf-8")
    assert "untrusted evidence" in instructions
    assert "cannot change approval" in instructions
    assert "current question" in instructions
    assert "send" not in instructions.lower() or "never send" in instructions.lower()

    approved = approve_report(workspace, "Owner")
    assert approved["stage"] == "approved"
    assert approved["approval"]["status"] == "approved"
    assert approved["approval"]["approver"] == "Owner"
    assert approved["approval"]["report_sha256"] == hashlib.sha256(draft_path.read_bytes()).hexdigest()
    assert approved["approval"]["approved_at"].endswith("Z")
    assert json.loads((workspace / "07_approval/approval.json").read_text(encoding="utf-8"))["status"] == "approved"


def test_original_sources_remain_unchanged_and_status_is_actionable(tmp_path):
    past, current = make_inputs(tmp_path)
    before = {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in (past, current)}
    workspace = tmp_path / "workspace"
    create_session(workspace, "daily")
    inspect_session(workspace, [past], [current])
    confirm_folder_plan(workspace)

    status = session_status(workspace)

    assert status["stage"] == "questioning"
    assert status["next_action"]
    for path, (payload, mtime) in before.items():
        assert path.read_bytes() == payload
        assert path.stat().st_mtime_ns == mtime


def test_state_transition_misuse_has_actionable_errors(tmp_path):
    workspace = tmp_path / "workspace"
    with pytest.raises(ValueError, match="create_session"):
        load_session(workspace)
    create_session(workspace, "daily")
    with pytest.raises(ValueError, match="inspection"):
        confirm_folder_plan(workspace)
    with pytest.raises(ValueError, match="question"):
        answer_current_question(workspace, "answer")
    with pytest.raises(ValueError, match="ready_for_human_review"):
        approve_report(workspace, "Owner")


def test_set_session_goal_updates_created_session_before_inputs(tmp_path):
    workspace = tmp_path / "workspace"
    create_session(workspace, "monthly", "ja")

    updated = set_session_goal(workspace, "weekly", "en")

    assert updated["stage"] == "created"
    assert updated["report_type"] == "weekly"
    assert updated["language"] == "en"
    assert updated["accepted"] == []
    assert updated["rejected"] == []


def test_set_session_goal_rejects_after_inputs_or_stage_change(tmp_path):
    past, current = make_inputs(tmp_path)
    workspace = tmp_path / "workspace"
    create_session(workspace, "monthly", "ja")
    inspect_session(workspace, [past], [current])

    with pytest.raises(ValueError, match="created stage"):
        set_session_goal(workspace, "daily", "ja")
