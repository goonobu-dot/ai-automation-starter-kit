from __future__ import annotations

import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from importlib import resources
from pathlib import Path

import pytest

from ai_automation_kit.core import autopilot_proof_lab
from ai_automation_kit.core.autopilot_proof_lab import (
    CASE_CLASSES,
    HARD_GATES,
    add_evidence,
    add_shadow_case,
    assessment_status,
    create_assessment,
    evaluate_assessment,
    load_assessment,
    set_gate,
)


EXPECTED_HARD_GATES = (
    "input_identifiable",
    "completion_testable",
    "standard_policy_confirmed",
    "exceptions_detectable",
    "exception_owner_assigned",
    "least_privilege_available",
    "idempotency_defined",
    "recovery_defined",
    "kill_switch_owned",
    "data_use_permitted",
    "shadow_test_passed",
)
EXPECTED_CASE_CLASSES = {
    "normal",
    "near_limit",
    "missing_data",
    "duplicate",
    "conflicting",
    "expired",
    "external_failure",
}
REPORT_NAMES = {
    "current_workflow.md",
    "automation_scope.md",
    "source_inventory.csv",
    "decision_table.csv",
    "exception_register.csv",
    "connector_permissions.md",
    "recovery_plan.md",
    "kill_switch_plan.md",
    "shadow_test_cases.csv",
    "comparison_report.md",
    "readiness_decision.json",
    "readiness_report.html",
    "improvement_roadmap.md",
    "proposal_scope.md",
}
DECISIONS = {"ready_unattended", "ready_conditional", "assist_only", "not_ready"}


def write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def bundled_pack_ids():
    payload = resources.files("ai_automation_kit").joinpath("packs", "manifest.json").read_bytes()
    return tuple(json.loads(payload.decode("utf-8")))


def make_assessment(tmp_path, requested_level="L3", pack_id="monthly-report"):
    workspace = tmp_path / "lab"
    result = create_assessment(
        workspace,
        pack_id=pack_id,
        organization="Acme",
        objective="月報作成の自動化可否を判定する",
        requested_level=requested_level,
        language="ja",
    )
    return workspace, result


def pass_all_gates(workspace, evidence_id=None, low_volume=False):
    for gate in EXPECTED_HARD_GATES:
        note = "confirmed"
        if gate == "shadow_test_passed" and low_volume:
            note = (
                "low-volume justification: only seven historical cases exist; "
                "the operations owner requires extended L2 monitoring for 90 days"
            )
        set_gate(
            workspace,
            gate,
            "pass",
            owner="ops-owner",
            evidence_ids=[evidence_id] if evidence_id else None,
            note=note,
        )


def add_case(
    workspace,
    tmp_path,
    case_id,
    expected="approved\namount: 100\n",
    proposed="approved\namount: 100\n",
    risk_tier="medium",
    case_class="normal",
    expected_route="standard",
    proposed_route="standard",
    **kwargs,
):
    input_path = write(tmp_path / f"{case_id}_input.txt", f"input for {case_id}\n")
    expected_path = write(tmp_path / f"{case_id}_expected.txt", expected)
    proposed_path = write(tmp_path / f"{case_id}_proposed.txt", proposed)
    return add_shadow_case(
        workspace,
        case_id,
        input_path,
        expected_path,
        proposed_path,
        risk_tier,
        case_class,
        expected_route,
        proposed_route,
        **kwargs,
    )


def add_required_cases(workspace, tmp_path):
    for index, case_class in enumerate(sorted(EXPECTED_CASE_CLASSES)):
        kwargs = {
            "unsupported_claims": index,
            "elapsed_seconds": 1.5 + index,
            "estimated_cost": 0.01 * index,
            "correction_category": "none" if index == 0 else "formatting",
        }
        if case_class == "duplicate":
            kwargs["duplicate_action_simulations"] = 1
        if case_class == "missing_data":
            kwargs.update(
                expected_route="quarantine",
                proposed_route="quarantine",
                exception_expected=True,
                exception_detected=True,
                quarantine_expected=True,
                quarantine_triggered=True,
            )
        if case_class == "external_failure":
            kwargs.update(recovery_tested=True, recovery_passed=True)
        add_case(workspace, tmp_path, f"case-{case_class}", case_class=case_class, **kwargs)


def audit_path(workspace):
    return workspace / ".proof_lab" / "audit.jsonl"


def state_path(workspace):
    return workspace / ".proof_lab" / "state.json"


def test_status_waits_for_in_progress_mutation_instead_of_reporting_corruption(tmp_path, monkeypatch):
    workspace, _ = make_assessment(tmp_path)
    source = write(tmp_path / "concurrent-policy.md", "approved")
    appended = threading.Event()
    release = threading.Event()
    original_append = autopilot_proof_lab._append_audit

    def paused_append(*args, **kwargs):
        entry = original_append(*args, **kwargs)
        appended.set()
        assert release.wait(timeout=2)
        return entry

    monkeypatch.setattr(autopilot_proof_lab, "_append_audit", paused_append)
    with ThreadPoolExecutor(max_workers=2) as executor:
        writer = executor.submit(add_evidence, workspace, source, "policy", "internal", "Owner")
        assert appended.wait(timeout=2)
        reader = executor.submit(assessment_status, workspace)
        time.sleep(0.05)
        assert not reader.done()
        release.set()
        writer.result(timeout=2)
        status = reader.result(timeout=2)

    assert status["evidence_count"] == 1


def test_exact_design_gate_and_case_contracts_are_exported():
    assert HARD_GATES == EXPECTED_HARD_GATES
    assert CASE_CLASSES == EXPECTED_CASE_CLASSES


def test_create_assessment_exposes_identity_stage_level_and_advisory_contract(tmp_path):
    workspace, result = make_assessment(tmp_path)

    assert result["assessment_id"].startswith("asmt_")
    assert result["pack_id"] == "monthly-report"
    assert result["policy_version"] == 1
    assert result["stage"] == result["status"] == "created"
    assert result["decision"] == "not_ready"
    assert result["current_level"] == result["maximum_level"] == "L0"
    assert result["next_action"]
    assert result["advisory_only"] is True
    assert result["external_actions_activated"] is False
    assert result["human_approval_removed"] is False
    assert "does not activate external actions" in result["safety_notice"]

    state = json.loads(state_path(workspace).read_text(encoding="utf-8"))
    assert state["transitions"][0]["prior_stage"] is None
    assert state["transitions"][0]["new_stage"] == "created"
    assert state["transitions"][0]["actor"] == "system"
    audit = json.loads(audit_path(workspace).read_text(encoding="utf-8"))
    assert audit["assessment_id"] == result["assessment_id"]
    assert audit["pack_id"] == "monthly-report"
    assert audit["policy_version"] == 1
    assert audit["stage"] == "created"
    assert len(audit["state_snapshot_hash"]) == 64


def test_create_assessment_rejects_unknown_pack_and_invalid_level(tmp_path):
    with pytest.raises(ValueError, match="unknown workflow pack"):
        create_assessment(tmp_path / "bad-pack", "missing", "Org", "Goal")
    with pytest.raises(ValueError, match="requested_level"):
        create_assessment(tmp_path / "bad-level", "monthly-report", "Org", "Goal", requested_level="L5")


@pytest.mark.parametrize("pack_id", bundled_pack_ids())
def test_every_bundled_pack_can_create_and_evaluate_locally(tmp_path, pack_id):
    workspace, created = make_assessment(tmp_path / pack_id, pack_id=pack_id)
    result = evaluate_assessment(workspace)

    assert created["pack_id"] == pack_id
    assert result["assessment_id"] == created["assessment_id"]
    assert result["decision"] in DECISIONS
    assert result["maximum_level"] in {"L0", "L1", "L2", "L3", "L4"}
    assert result["stage"] == result["decision"]
    reports = workspace / "05_REPORTS"
    assert {path.name for path in reports.iterdir()} == REPORT_NAMES


def test_report_generation_rejects_unexpected_regular_files(tmp_path):
    workspace, _ = make_assessment(tmp_path)
    reports = workspace / "05_REPORTS"
    reports.mkdir()
    (reports / "old-report.txt").write_text("stale", encoding="utf-8")

    with pytest.raises(RuntimeError, match="unexpected report artifacts"):
        evaluate_assessment(workspace)


def test_mutations_use_meaningful_stages_and_invalidate_prior_decision(tmp_path):
    workspace, created = make_assessment(tmp_path)
    evidence = add_evidence(
        workspace,
        write(tmp_path / "policy.md", "policy v1"),
        role="policy",
        classification="internal",
        provided_by="Yamada",
    )
    assert load_assessment(workspace)["stage"] == "evidence_waiting"
    add_case(workspace, tmp_path, "normal-1")
    assert load_assessment(workspace)["stage"] == "ready_for_shadow"
    first = evaluate_assessment(workspace)
    assert first["stage"] in DECISIONS
    assert first["evidence_snapshot_hash"]

    gate = set_gate(workspace, "input_identifiable", "pass", owner="new-owner", evidence_ids=[evidence["id"]])
    assert gate["owner"] == "new-owner"
    stale = assessment_status(workspace)
    assert stale["assessment_id"] == created["assessment_id"]
    assert stale["stage"] == stale["status"] == "stale_decision"
    assert stale["stale"] is True
    assert "assessment changed after evaluation" in stale["stale_reasons"]

    refreshed = evaluate_assessment(workspace)
    assert refreshed["stage"] in DECISIONS
    assert refreshed["stale"] is False
    assert refreshed["evidence_snapshot_hash"] != first["evidence_snapshot_hash"]
    assert load_assessment(workspace)["transitions"][-1]["new_stage"] == refreshed["decision"]


def test_any_added_evidence_or_case_after_evaluation_makes_decision_stale(tmp_path):
    workspace, _ = make_assessment(tmp_path)
    evaluate_assessment(workspace)
    add_evidence(workspace, write(tmp_path / "new.md", "new"), "policy", "internal", "owner")
    assert assessment_status(workspace)["stage"] == "stale_decision"

    evaluate_assessment(workspace)
    add_case(workspace, tmp_path, "post-evaluation")
    assert assessment_status(workspace)["stage"] == "stale_decision"


def test_changed_or_missing_copied_files_make_prior_decision_stale(tmp_path):
    workspace, _ = make_assessment(tmp_path)
    evidence = add_evidence(workspace, write(tmp_path / "evidence.md", "evidence"), "policy", "internal", "owner")
    case = add_case(workspace, tmp_path, "normal-1")
    evaluate_assessment(workspace)

    (workspace / evidence["stored_path"]).write_text("tampered", encoding="utf-8")
    (workspace / case["files"]["input"]["stored_path"]).unlink()
    status = assessment_status(workspace)

    assert status["stage"] == "stale_decision"
    assert status["decision"] == "not_ready"
    assert any("changed" in reason for reason in status["stale_reasons"])
    assert any("missing" in reason for reason in status["stale_reasons"])


def test_gate_failures_cap_decision_with_only_design_decision_values(tmp_path):
    workspace, _ = make_assessment(tmp_path)
    for gate in EXPECTED_HARD_GATES:
        if gate != "least_privilege_available":
            set_gate(workspace, gate, "pass", owner="owner")
    result = evaluate_assessment(workspace)
    assert result["decision"] == "assist_only"
    assert result["maximum_level"] == "L1"
    assert "least_privilege_available" in result["blocking_gates"]

    workspace2, _ = make_assessment(tmp_path / "not-ready")
    set_gate(workspace2, "input_identifiable", "fail", owner="owner")
    result2 = evaluate_assessment(workspace2)
    assert result2["decision"] == "not_ready"
    assert result2["maximum_level"] == "L0"
    assert {result["decision"], result2["decision"]}.issubset(DECISIONS)


@pytest.mark.parametrize(
    ("requested_level", "expected_decision", "expected_level"),
    [("L3", "ready_conditional", "L3"), ("L4", "ready_unattended", "L4")],
)
def test_l3_l4_require_all_case_classes_and_accept_bounded_owner_justification(
    tmp_path, requested_level, expected_decision, expected_level
):
    workspace, _ = make_assessment(tmp_path, requested_level=requested_level)
    pass_all_gates(workspace, low_volume=True)
    add_required_cases(workspace, tmp_path)

    result = evaluate_assessment(workspace)

    assert result["decision"] == "assist_only"  # unsupported claims are content failures
    assert "unsupported_claims" in result["readiness_gaps"]
    assert result["metrics"]["case_classes"] == sorted(EXPECTED_CASE_CLASSES)
    assert result["metrics"]["duplicate_action_simulations"] == 1
    assert result["metrics"]["quarantine_true_positives"] == 1
    assert result["metrics"]["quarantine_false_positives"] == 0
    assert result["metrics"]["quarantine_precision"] == 1.0
    assert result["metrics"]["elapsed_seconds"] == pytest.approx(31.5)
    assert result["metrics"]["estimated_cost"] == pytest.approx(0.21)
    assert result["metrics"]["correction_categories"] == {"formatting": 6, "none": 1}

    # Recreate clean cases because registered historical records are immutable.
    clean_workspace, _ = make_assessment(tmp_path / "clean", requested_level=requested_level)
    pass_all_gates(clean_workspace, low_volume=True)
    for case_class in sorted(EXPECTED_CASE_CLASSES):
        kwargs = {"duplicate_action_simulations": 1} if case_class == "duplicate" else {}
        if case_class == "missing_data":
            kwargs.update(
                expected_route="quarantine",
                proposed_route="quarantine",
                exception_expected=True,
                exception_detected=True,
            )
        if case_class == "external_failure":
            kwargs.update(recovery_tested=True, recovery_passed=True)
        add_case(clean_workspace, tmp_path / "clean-cases", case_class, case_class=case_class, **kwargs)

    clean = evaluate_assessment(clean_workspace)
    assert clean["decision"] == expected_decision
    assert clean["maximum_level"] == expected_level
    assert clean["current_level"] == expected_level
    assert clean["readiness_gaps"] == []


def test_l3_without_all_classes_volume_exception_recovery_and_correct_routes_is_assist_only(tmp_path):
    workspace, _ = make_assessment(tmp_path)
    pass_all_gates(workspace)
    add_case(
        workspace,
        tmp_path,
        "critical-miss",
        risk_tier="critical",
        case_class="normal",
        expected_route="quarantine",
        proposed_route="standard",
        exception_expected=True,
        exception_detected=False,
    )
    result = evaluate_assessment(workspace)

    assert result["decision"] == "assist_only"
    assert {
        "minimum_100_cases",
        "required_case_classes",
        "critical_false_negatives",
        "exception_coverage",
        "route_or_content_mismatch",
        "recovery_evidence",
    }.issubset(result["readiness_gaps"])


def test_all_fourteen_reports_use_canonical_directory_and_metadata(tmp_path):
    workspace, created = make_assessment(tmp_path)
    result = evaluate_assessment(workspace)
    reports = workspace / "05_REPORTS"

    assert {path.name for path in reports.iterdir()} == REPORT_NAMES
    decision = json.loads((reports / "readiness_decision.json").read_text(encoding="utf-8"))
    assert decision["assessment_id"] == created["assessment_id"]
    assert decision["pack_id"] == "monthly-report"
    assert decision["policy_version"] == 1
    assert decision["generated_at"] == result["generated_at"]
    assert decision["evidence_snapshot_hash"] == result["evidence_snapshot_hash"]
    for path in reports.iterdir():
        text = path.read_text(encoding="utf-8")
        assert created["assessment_id"] in text
        assert "monthly-report" in text
        assert result["evidence_snapshot_hash"] in text


@pytest.mark.parametrize("api_name", ["load", "status", "evaluate"])
@pytest.mark.parametrize("corruption", ["invalid_json", "hash_mismatch", "broken_previous", "truncated", "missing"])
def test_audit_corruption_fails_closed_for_all_read_apis(tmp_path, api_name, corruption):
    workspace, _ = make_assessment(tmp_path)
    add_evidence(workspace, write(tmp_path / "e.md", "e"), "policy", "internal", "owner")
    path = audit_path(workspace)
    lines = path.read_text(encoding="utf-8").splitlines()
    entries = [json.loads(line) for line in lines]

    if corruption == "invalid_json":
        lines[-1] = "{not-json"
    elif corruption == "hash_mismatch":
        entries[-1]["entry_hash"] = "0" * 64
        lines[-1] = json.dumps(entries[-1], sort_keys=True)
    elif corruption == "broken_previous":
        entries[-1]["previous_hash"] = "f" * 64
        lines[-1] = json.dumps(entries[-1], sort_keys=True)
    elif corruption == "truncated":
        lines = lines[:-1]
    else:
        path.unlink()
    if corruption != "missing":
        path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")

    call = {
        "load": lambda: load_assessment(workspace),
        "status": lambda: assessment_status(workspace),
        "evaluate": lambda: evaluate_assessment(workspace),
    }[api_name]
    with pytest.raises(ValueError, match="manual_recovery_required"):
        call()


def test_malformed_state_fails_closed(tmp_path):
    workspace, _ = make_assessment(tmp_path)
    state_path(workspace).write_text("{broken", encoding="utf-8")
    with pytest.raises(ValueError, match="manual_recovery_required"):
        load_assessment(workspace)


def test_structurally_damaged_nested_state_fails_closed(tmp_path):
    workspace, _ = make_assessment(tmp_path)
    add_case(workspace, tmp_path, "damaged-case")
    state = json.loads(state_path(workspace).read_text(encoding="utf-8"))
    del state["shadow_cases"][0]["unsupported_claims"]
    audit_entries = [json.loads(line) for line in audit_path(workspace).read_text(encoding="utf-8").splitlines()]
    audit_entries[-1]["evidence_snapshot_hash"] = autopilot_proof_lab._evidence_snapshot_hash(state)
    audit_entries[-1]["state_snapshot_hash"] = autopilot_proof_lab._state_snapshot_hash(state)
    audit_entries[-1]["entry_hash"] = autopilot_proof_lab._audit_hash(audit_entries[-1])
    state["audit"]["head_hash"] = audit_entries[-1]["entry_hash"]
    state_path(workspace).write_text(json.dumps(state), encoding="utf-8")
    audit_path(workspace).write_text(
        "\n".join(json.dumps(entry, sort_keys=True) for entry in audit_entries) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="manual_recovery_required"):
        evaluate_assessment(workspace)


def test_malformed_json_and_csv_cases_are_rejected_and_cleaned_up(tmp_path):
    workspace, _ = make_assessment(tmp_path)
    input_path = write(tmp_path / "input.txt", "input")

    with pytest.raises(ValueError, match="invalid JSON"):
        add_shadow_case(
            workspace,
            "bad-json",
            input_path,
            write(tmp_path / "expected.json", "{bad"),
            write(tmp_path / "proposed.json", "{}"),
            "medium",
            "normal",
            "standard",
            "standard",
        )
    assert not (workspace / ".proof_lab" / "cases" / "bad-json").exists()

    with pytest.raises(ValueError, match="invalid CSV"):
        add_shadow_case(
            workspace,
            "bad-csv",
            input_path,
            write(tmp_path / "expected.csv", 'a,b\n"unterminated,1\n'),
            write(tmp_path / "proposed.csv", "a,b\nx,1\n"),
            "medium",
            "normal",
            "standard",
            "standard",
        )
    assert not (workspace / ".proof_lab" / "cases" / "bad-csv").exists()
    assert assessment_status(workspace)["shadow_case_count"] == 0


def test_evidence_rejects_symlink_script_oversize_and_traversal(tmp_path):
    workspace, _ = make_assessment(tmp_path)
    source = write(tmp_path / "policy.md", "policy")
    symlink = tmp_path / "link.md"
    symlink.symlink_to(source)
    with pytest.raises(ValueError, match="symlink"):
        add_evidence(workspace, symlink, "policy", "internal", "owner")
    with pytest.raises(ValueError, match="script"):
        add_evidence(workspace, write(tmp_path / "run.sh", "exit 0"), "policy", "internal", "owner")
    large = tmp_path / "large.txt"
    large.write_bytes(b"x" * (5 * 1024 * 1024 + 1))
    with pytest.raises(ValueError, match="larger"):
        add_evidence(workspace, large, "policy", "internal", "owner")
    nested = tmp_path / "nested"
    nested.mkdir()
    with pytest.raises(ValueError, match="traversal"):
        add_evidence(workspace, nested / ".." / "policy.md", "policy", "internal", "owner")


def test_source_symlink_swap_is_detected_and_partial_copy_is_removed(tmp_path, monkeypatch):
    workspace, _ = make_assessment(tmp_path)
    source = write(tmp_path / "source.txt", "trusted")
    outside = write(tmp_path / "outside.txt", "outside")
    opened = threading.Event()
    resume = threading.Event()
    original_copy = autopilot_proof_lab._copy_open_descriptor

    def pause_copy(*args, **kwargs):
        opened.set()
        assert resume.wait(timeout=5)
        return original_copy(*args, **kwargs)

    monkeypatch.setattr(autopilot_proof_lab, "_copy_open_descriptor", pause_copy)
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(add_evidence, workspace, source, "policy", "internal", "owner")
        assert opened.wait(timeout=5)
        source.unlink()
        source.symlink_to(outside)
        resume.set()
        with pytest.raises(ValueError, match="changed during copy"):
            future.result(timeout=5)
    assert list((workspace / ".proof_lab" / "evidence").iterdir()) == []


def test_mutation_lock_rejects_concurrent_write_and_preserves_first_record(tmp_path, monkeypatch):
    workspace, _ = make_assessment(tmp_path)
    first_source = write(tmp_path / "first.txt", "first")
    second_source = write(tmp_path / "second.txt", "second")
    entered = threading.Event()
    resume = threading.Event()
    original_copy = autopilot_proof_lab._copy_open_descriptor

    def pause_first(source_fd, destination_fd, label):
        if not entered.is_set():
            entered.set()
            assert resume.wait(timeout=5)
        return original_copy(source_fd, destination_fd, label)

    monkeypatch.setattr(autopilot_proof_lab, "_copy_open_descriptor", pause_first)
    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(add_evidence, workspace, first_source, "policy", "internal", "one")
        assert entered.wait(timeout=5)
        second = pool.submit(add_evidence, workspace, second_source, "policy", "internal", "two")
        with pytest.raises(ValueError, match="mutation.*in progress"):
            second.result(timeout=5)
        resume.set()
        assert first.result(timeout=5)["provided_by"] == "one"

    status = assessment_status(workspace)
    assert status["evidence_count"] == 1
    assert not (workspace / ".proof_lab" / "mutation.lock").exists()


def test_existing_mutation_lock_fails_closed_without_copying(tmp_path):
    workspace, _ = make_assessment(tmp_path)
    lock = workspace / ".proof_lab" / "mutation.lock"
    lock.write_text("stale", encoding="utf-8")
    with pytest.raises(ValueError, match="mutation.*in progress"):
        add_evidence(workspace, write(tmp_path / "e.txt", "e"), "policy", "internal", "owner")
    assert list((workspace / ".proof_lab" / "evidence").iterdir()) == []


def test_json_csv_and_text_comparisons_are_deterministic(tmp_path):
    workspace, _ = make_assessment(tmp_path)
    input_path = write(tmp_path / "input.txt", "input")
    json_case = add_shadow_case(
        workspace,
        "json",
        input_path,
        write(tmp_path / "expected.json", json.dumps({"a": 1, "b": 2}, indent=2)),
        write(tmp_path / "proposed.json", json.dumps({"b": 2, "a": 1})),
        "medium",
        "normal",
        "standard",
        "standard",
    )
    csv_case = add_shadow_case(
        workspace,
        "csv",
        input_path,
        write(tmp_path / "expected.csv", "name,amount\nA,1\nB,2\n"),
        write(tmp_path / "proposed.csv", "amount,name\n2,B\n1,A\n"),
        "medium",
        "normal",
        "standard",
        "standard",
    )
    text_case = add_case(workspace, tmp_path, "text", expected="A\nB\n", proposed="A\nC\n")

    assert json_case["comparison"]["result"] == "material_match"
    assert csv_case["comparison"]["result"] == "material_match"
    assert text_case["comparison"]["result"] == "mismatch"
    assert text_case["comparison"]["changed_lines"] == 1


def test_duplicate_case_ids_fail_without_leaving_extra_files(tmp_path):
    workspace, _ = make_assessment(tmp_path)
    add_case(workspace, tmp_path, "duplicate-id")
    with pytest.raises(ValueError, match="duplicate case_id"):
        add_case(workspace, tmp_path / "again", "duplicate-id")
    assert assessment_status(workspace)["shadow_case_count"] == 1
