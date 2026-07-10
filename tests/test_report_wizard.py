import hashlib
import json
from pathlib import Path

import pytest

from ai_automation_kit.core.report_wizard import (
    approve_report,
    answer_current_question,
    build_report_workspace,
    confirm_folder_plan,
    create_session,
    inspect_session,
    load_session,
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
