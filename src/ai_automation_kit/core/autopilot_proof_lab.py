from __future__ import annotations

import csv
import hashlib
import html
import io
import json
import math
import os
import re
import secrets
import shutil
import stat
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from importlib import resources
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Optional, Tuple

from ai_automation_kit.core.workflow_pack import load_bundled_pack


SCHEMA_VERSION = 2
POLICY_VERSION = 1
MAX_FILE_BYTES = 5 * 1024 * 1024
MAX_PERSISTED_BYTES = 20 * 1024 * 1024
REQUESTED_LEVELS = {"L0", "L1", "L2", "L3", "L4"}
GATE_STATUSES = {"pass", "fail", "unknown"}
DECISIONS = {"ready_unattended", "ready_conditional", "assist_only", "not_ready"}
HARD_GATES = (
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
CASE_CLASSES = {
    "normal",
    "near_limit",
    "missing_data",
    "duplicate",
    "conflicting",
    "expired",
    "external_failure",
}
RISK_TIERS = {"low", "medium", "high", "critical"}
ROUTES = {"standard", "quarantine"}
SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
HEX_64_RE = re.compile(r"^[0-9a-f]{64}$")
SCRIPT_EXTENSIONS = {
    ".bat",
    ".cmd",
    ".com",
    ".exe",
    ".js",
    ".mjs",
    ".ps1",
    ".py",
    ".rb",
    ".sh",
    ".zsh",
}
REPORT_NAMES = (
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
)
SAFETY_NOTICE = (
    "Readiness is advisory only; it does not activate external actions and "
    "does not remove current human approval."
)


def create_assessment(
    workspace,
    pack_id,
    organization,
    objective,
    requested_level="L3",
    language="ja",
):
    workspace_path = _workspace(workspace, create=True)
    _require_level(requested_level)
    if language not in {"ja", "en"}:
        raise ValueError("language must be ja or en")
    organization = _require_text(organization, "organization", 500)
    objective = _require_text(objective, "objective", 2000)
    pack_id = str(pack_id)
    _require_safe_id(pack_id, "pack_id")
    pack = load_bundled_pack(pack_id)
    manifest_entry = _load_manifest_entry(pack_id)

    lab = _lab_root(workspace_path)
    _ensure_directory(lab)
    _ensure_directory(lab / "evidence")
    _ensure_directory(lab / "cases")
    with _mutation_lock(workspace_path):
        if _state_path(workspace_path).exists() or _audit_path(workspace_path).exists():
            raise ValueError("assessment workspace has already been created")
        timestamp = _utc_now()
        assessment_id = "asmt_{}".format(secrets.token_hex(12))
        state = {
            "schema_version": SCHEMA_VERSION,
            "assessment_id": assessment_id,
            "pack_id": pack_id,
            "pack_snapshot": pack,
            "pack_manifest": manifest_entry,
            "organization": organization,
            "objective": objective,
            "requested_level": requested_level,
            "language": language,
            "policy_version": POLICY_VERSION,
            "created_at": timestamp,
            "updated_at": timestamp,
            "status": "created",
            "stage": "created",
            "decision": "not_ready",
            "current_level": "L0",
            "maximum_level": "L0",
            "next_action": "Add current-work evidence and accountable owners.",
            "evidence": [],
            "shadow_cases": [],
            "gates": {
                gate: {
                    "status": "unknown",
                    "owner": None,
                    "evidence_ids": [],
                    "note": "",
                    "updated_at": None,
                }
                for gate in HARD_GATES
            },
            "transitions": [],
            "last_decision": {
                "decision": "not_ready",
                "maximum_level": "L0",
                "evaluated_at": None,
                "evidence_snapshot_hash": None,
                "stale": False,
            },
            "audit": {"entry_count": 0, "head_hash": None},
        }
        _transition(state, "created", "system", "assessment created", prior_stage=None, force=True)
        _write_json_atomic(_pack_manifest_path(workspace_path), manifest_entry)
        _commit_state(
            workspace_path,
            state,
            "create_assessment",
            {"pack_id": pack_id, "requested_level": requested_level},
        )
    return _public_summary(state)


def load_assessment(workspace):
    workspace_path = _workspace(workspace)
    state = _read_verified_state(workspace_path)
    freshness = _freshness(state, workspace_path)
    loaded = _json_copy(state)
    _apply_derived_freshness(loaded, freshness)
    loaded.update(_safety_fields())
    return loaded


def add_evidence(workspace, source_path, role, classification, provided_by):
    workspace_path = _workspace(workspace)
    role = _require_text(role, "role", 200)
    classification = _require_text(classification, "classification", 100)
    provided_by = _require_text(provided_by, "provided_by", 200)
    with _mutation_lock(workspace_path):
        state = _load_verified_state(workspace_path)
        evidence_id = _next_id("ev", len(state["evidence"]) + 1)
        copied = _copy_intake_file(
            workspace_path,
            source_path,
            _lab_root(workspace_path) / "evidence",
            evidence_id,
            "evidence source",
        )
        record = {
            "id": evidence_id,
            "evidence_id": evidence_id,
            "source_name": copied["source_name"],
            "stored_path": copied["stored_path"],
            "sha256": copied["sha256"],
            "bytes": copied["bytes"],
            "role": role,
            "classification": classification,
            "provided_by": provided_by,
            "added_at": _utc_now(),
            "verified_at": None,
            "status": "present",
        }
        state["evidence"].append(record)
        _mark_mutation(state, "evidence_waiting", "add_evidence")
        try:
            _commit_state(
                workspace_path,
                state,
                "add_evidence",
                {"evidence_id": evidence_id, "sha256": record["sha256"]},
            )
        except Exception:
            _unlink_stored_file(workspace_path, record["stored_path"])
            raise
    return _json_copy(record)


def add_shadow_case(
    workspace,
    case_id,
    input_path,
    expected_path,
    proposed_path,
    risk_tier,
    case_class,
    expected_route,
    proposed_route,
    exception_expected=False,
    exception_detected=False,
    recovery_tested=False,
    recovery_passed=False,
    unsupported_claims=0,
    duplicate_action_simulations=0,
    quarantine_expected=None,
    quarantine_triggered=None,
    elapsed_seconds=0.0,
    estimated_cost=0.0,
    correction_category="",
):
    workspace_path = _workspace(workspace)
    case_id = str(case_id)
    _require_safe_id(case_id, "case_id")
    if risk_tier not in RISK_TIERS:
        raise ValueError("risk_tier must be one of {}".format(", ".join(sorted(RISK_TIERS))))
    if case_class not in CASE_CLASSES:
        raise ValueError("case_class must be one of {}".format(", ".join(sorted(CASE_CLASSES))))
    if expected_route not in ROUTES or proposed_route not in ROUTES:
        raise ValueError("routes must be standard or quarantine")
    exception_expected = _require_bool(exception_expected, "exception_expected")
    exception_detected = _require_bool(exception_detected, "exception_detected")
    recovery_tested = _require_bool(recovery_tested, "recovery_tested")
    recovery_passed = _require_bool(recovery_passed, "recovery_passed")
    unsupported_claims = _require_nonnegative_int(unsupported_claims, "unsupported_claims")
    duplicate_action_simulations = _require_nonnegative_int(
        duplicate_action_simulations, "duplicate_action_simulations"
    )
    elapsed_seconds = _require_nonnegative_number(elapsed_seconds, "elapsed_seconds")
    estimated_cost = _require_nonnegative_number(estimated_cost, "estimated_cost")
    correction_category = _optional_text(correction_category, "correction_category", 128)
    if quarantine_expected is None:
        quarantine_expected = expected_route == "quarantine"
    else:
        quarantine_expected = _require_bool(quarantine_expected, "quarantine_expected")
    if quarantine_triggered is None:
        quarantine_triggered = proposed_route == "quarantine"
    else:
        quarantine_triggered = _require_bool(quarantine_triggered, "quarantine_triggered")

    with _mutation_lock(workspace_path):
        state = _load_verified_state(workspace_path)
        if any(case["case_id"] == case_id for case in state["shadow_cases"]):
            raise ValueError("duplicate case_id: {}".format(case_id))
        case_root = _lab_root(workspace_path) / "cases" / case_id
        if case_root.exists() or case_root.is_symlink():
            raise ValueError("case storage already exists for {}".format(case_id))
        case_root.mkdir(mode=0o700)
        try:
            input_record = _copy_intake_file(
                workspace_path, input_path, case_root, "input", "case input"
            )
            expected_record = _copy_intake_file(
                workspace_path, expected_path, case_root, "expected", "expected output"
            )
            proposed_record = _copy_intake_file(
                workspace_path, proposed_path, case_root, "proposed", "proposed output"
            )
            comparison = _compare_files(
                workspace_path / expected_record["stored_path"],
                workspace_path / proposed_record["stored_path"],
            )
            record = {
                "case_id": case_id,
                "risk_tier": risk_tier,
                "case_class": case_class,
                "expected_route": expected_route,
                "proposed_route": proposed_route,
                "exception_expected": exception_expected,
                "exception_detected": exception_detected,
                "recovery_tested": recovery_tested,
                "recovery_passed": recovery_passed,
                "unsupported_claims": unsupported_claims,
                "duplicate_action_simulations": duplicate_action_simulations,
                "quarantine_expected": quarantine_expected,
                "quarantine_triggered": quarantine_triggered,
                "elapsed_seconds": elapsed_seconds,
                "estimated_cost": estimated_cost,
                "correction_category": correction_category,
                "files": {
                    "input": _without_source_name(input_record),
                    "expected": _without_source_name(expected_record),
                    "proposed": _without_source_name(proposed_record),
                },
                "comparison": comparison,
                "added_at": _utc_now(),
            }
            state["shadow_cases"].append(record)
            _mark_mutation(state, "ready_for_shadow", "add_shadow_case")
            _commit_state(
                workspace_path,
                state,
                "add_shadow_case",
                {"case_id": case_id, "comparison": comparison["result"]},
            )
        except Exception:
            _remove_case_directory(case_root)
            raise
    return _json_copy(record)


def set_gate(workspace, gate, status, owner, evidence_ids=None, note=""):
    workspace_path = _workspace(workspace)
    if gate not in HARD_GATES:
        raise ValueError("unknown hard gate: {}".format(gate))
    if status not in GATE_STATUSES:
        raise ValueError("gate status must be pass, fail, or unknown")
    owner = _require_text(owner, "owner", 200)
    note = _optional_text(note, "note", 500)
    if not isinstance(evidence_ids or [], (list, tuple)):
        raise ValueError("evidence_ids must be a list")
    normalized_ids = [str(item) for item in (evidence_ids or [])]
    if len(normalized_ids) != len(set(normalized_ids)):
        raise ValueError("evidence_ids cannot contain duplicates")
    with _mutation_lock(workspace_path):
        state = _load_verified_state(workspace_path)
        known_ids = {item["id"] for item in state["evidence"]}
        missing = [item for item in normalized_ids if item not in known_ids]
        if missing:
            raise ValueError("unknown evidence_ids: {}".format(", ".join(missing)))
        record = {
            "status": status,
            "owner": owner,
            "evidence_ids": normalized_ids,
            "note": note,
            "updated_at": _utc_now(),
        }
        state["gates"][gate] = record
        _mark_mutation(state, "gap_resolution", "set_gate")
        _commit_state(
            workspace_path,
            state,
            "set_gate",
            {"gate": gate, "status": status, "owner": owner},
        )
    return _json_copy(record)


def evaluate_assessment(workspace):
    workspace_path = _workspace(workspace)
    with _mutation_lock(workspace_path):
        state = _load_verified_state(workspace_path)
        freshness = _freshness(state, workspace_path)
        if freshness["integrity_reasons"]:
            _transition(
                state,
                "stale_decision",
                "system",
                "copied evidence or pack manifest changed",
            )
            state["decision"] = "not_ready"
            state["current_level"] = "L0"
            state["maximum_level"] = "L0"
            state["next_action"] = "Restore or replace stale evidence, then reassess."
            state["last_decision"]["stale"] = True
            snapshot_hash = _evidence_snapshot_hash(state)
            generated_at = _utc_now()
            result = _decision_result(
                state,
                decision="not_ready",
                maximum_level="L0",
                blocking_gates=_blocking_gates(state),
                readiness_gaps=["stale_evidence"],
                metrics=_shadow_metrics(state["shadow_cases"]),
                freshness=freshness,
                snapshot_hash=snapshot_hash,
                generated_at=generated_at,
            )
            _commit_state(
                workspace_path,
                state,
                "detect_stale_evidence",
                {"reasons": freshness["integrity_reasons"]},
            )
            _write_reports(workspace_path, state, result)
            return _json_copy(result)

        _transition(state, "comparison_review", "system", "shadow cases compared")
        metrics = _shadow_metrics(state["shadow_cases"])
        blocking_gates = _blocking_gates(state)
        readiness_gaps = _readiness_gaps(state, metrics)
        decision, maximum_level = _derive_decision(state, blocking_gates, readiness_gaps)
        _transition(state, "decision_ready", "system", "deterministic gate evaluation complete")
        snapshot_hash = _evidence_snapshot_hash(state)
        generated_at = _utc_now()
        state["decision"] = decision
        state["current_level"] = maximum_level
        state["maximum_level"] = maximum_level
        state["next_action"] = _next_action_for_decision(decision)
        state["last_decision"] = {
            "decision": decision,
            "maximum_level": maximum_level,
            "evaluated_at": generated_at,
            "evidence_snapshot_hash": snapshot_hash,
            "stale": False,
        }
        _transition(state, decision, "system", "advisory readiness decision generated")
        result = _decision_result(
            state,
            decision=decision,
            maximum_level=maximum_level,
            blocking_gates=blocking_gates,
            readiness_gaps=readiness_gaps,
            metrics=metrics,
            freshness={"stale": False, "stale_reasons": [], "integrity_reasons": []},
            snapshot_hash=snapshot_hash,
            generated_at=generated_at,
        )
        _commit_state(
            workspace_path,
            state,
            "evaluate_assessment",
            {
                "decision": decision,
                "maximum_level": maximum_level,
                "evidence_snapshot_hash": snapshot_hash,
            },
        )
        _write_reports(workspace_path, state, result)
    return _json_copy(result)


def assessment_status(workspace):
    workspace_path = _workspace(workspace)
    state = _read_verified_state(workspace_path)
    freshness = _freshness(state, workspace_path)
    view = _json_copy(state)
    _apply_derived_freshness(view, freshness)
    return {
        "success": True,
        "assessment_id": view["assessment_id"],
        "pack_id": view["pack_id"],
        "policy_version": view["policy_version"],
        "status": view["status"],
        "stage": view["stage"],
        "decision": view["decision"],
        "current_level": view["current_level"],
        "maximum_level": view["maximum_level"],
        "next_action": view["next_action"],
        "stale": freshness["stale"],
        "stale_reasons": freshness["stale_reasons"],
        "evidence_count": len(state["evidence"]),
        "shadow_case_count": len(state["shadow_cases"]),
        "blocking_gates": _blocking_gates(state),
        **_safety_fields(),
    }


def _derive_decision(state, blocking_gates, readiness_gaps):
    if state["gates"]["input_identifiable"]["status"] != "pass":
        return "not_ready", "L0"
    if state["gates"]["completion_testable"]["status"] != "pass":
        return "not_ready", "L0"
    requested = state["requested_level"]
    if requested == "L0":
        return "not_ready", "L0"
    if requested == "L1":
        return "assist_only", "L1"
    if requested == "L2":
        return "assist_only", "L2"
    if blocking_gates or readiness_gaps:
        return "assist_only", "L1"
    if requested == "L4":
        return "ready_unattended", "L4"
    return "ready_conditional", "L3"


def _blocking_gates(state):
    return [
        gate
        for gate in HARD_GATES
        if state["gates"][gate]["status"] != "pass" or not state["gates"][gate]["owner"]
    ]


def _readiness_gaps(state, metrics):
    if state["requested_level"] not in {"L3", "L4"}:
        return []
    gaps = []
    if metrics["case_count"] < 100 and not _has_low_volume_justification(state):
        gaps.append("minimum_100_cases")
    if set(metrics["case_classes"]) != CASE_CLASSES:
        gaps.append("required_case_classes")
    if metrics["critical_false_negatives"]:
        gaps.append("critical_false_negatives")
    if metrics["exception_expected"] == 0 or metrics["exception_detected"] < metrics["exception_expected"]:
        gaps.append("exception_coverage")
    if metrics["route_mismatches"] or metrics["content_mismatches"]:
        gaps.append("route_or_content_mismatch")
    if metrics["unsupported_claims"]:
        gaps.append("unsupported_claims")
    if metrics["duplicate_action_simulations"] == 0:
        gaps.append("duplicate_action_simulation")
    if (
        metrics["recovery_tested"] == 0
        or metrics["recovery_passed"] < metrics["recovery_tested"]
        or metrics["recovery_failed"]
    ):
        gaps.append("recovery_evidence")
    return gaps


def _has_low_volume_justification(state):
    gate = state["gates"]["shadow_test_passed"]
    note = gate["note"].lower()
    return (
        gate["status"] == "pass"
        and bool(gate["owner"])
        and 20 <= len(note) <= 500
        and "low-volume justification" in note
    )


def _shadow_metrics(cases):
    metrics = {
        "case_count": len(cases),
        "case_classes": sorted({case["case_class"] for case in cases}),
        "exact_matches": 0,
        "material_matches": 0,
        "content_mismatches": 0,
        "route_mismatches": 0,
        "exception_expected": 0,
        "exception_detected": 0,
        "critical_false_negatives": 0,
        "unsupported_claims": 0,
        "duplicate_action_simulations": 0,
        "quarantine_expected": 0,
        "quarantine_triggered": 0,
        "quarantine_true_positives": 0,
        "quarantine_false_positives": 0,
        "quarantine_precision": None,
        "elapsed_seconds": 0.0,
        "estimated_cost": 0.0,
        "correction_categories": {},
        "recovery_tested": 0,
        "recovery_passed": 0,
        "recovery_failed": 0,
    }
    for case in cases:
        comparison = case["comparison"]["result"]
        if comparison == "exact_match":
            metrics["exact_matches"] += 1
        elif comparison == "material_match":
            metrics["material_matches"] += 1
        else:
            metrics["content_mismatches"] += 1
        route_mismatch = case["expected_route"] != case["proposed_route"]
        if route_mismatch:
            metrics["route_mismatches"] += 1
        if case["exception_expected"]:
            metrics["exception_expected"] += 1
            if case["exception_detected"]:
                metrics["exception_detected"] += 1
            elif case["risk_tier"] == "critical":
                metrics["critical_false_negatives"] += 1
        if (
            case["risk_tier"] == "critical"
            and case["expected_route"] == "quarantine"
            and case["proposed_route"] != "quarantine"
        ):
            metrics["critical_false_negatives"] += 1
        metrics["unsupported_claims"] += case["unsupported_claims"]
        metrics["duplicate_action_simulations"] += case["duplicate_action_simulations"]
        expected = case["quarantine_expected"]
        triggered = case["quarantine_triggered"]
        metrics["quarantine_expected"] += int(expected)
        metrics["quarantine_triggered"] += int(triggered)
        metrics["quarantine_true_positives"] += int(expected and triggered)
        metrics["quarantine_false_positives"] += int(triggered and not expected)
        metrics["elapsed_seconds"] += case["elapsed_seconds"]
        metrics["estimated_cost"] += case["estimated_cost"]
        category = case["correction_category"]
        if category:
            metrics["correction_categories"][category] = (
                metrics["correction_categories"].get(category, 0) + 1
            )
        if case["recovery_tested"]:
            metrics["recovery_tested"] += 1
            if case["recovery_passed"]:
                metrics["recovery_passed"] += 1
            else:
                metrics["recovery_failed"] += 1
    if metrics["quarantine_triggered"]:
        metrics["quarantine_precision"] = round(
            metrics["quarantine_true_positives"] / metrics["quarantine_triggered"], 6
        )
    metrics["elapsed_seconds"] = round(metrics["elapsed_seconds"], 6)
    metrics["estimated_cost"] = round(metrics["estimated_cost"], 6)
    return metrics


def _compare_files(expected, proposed):
    expected_text = _read_text_no_follow(expected, "expected output", MAX_FILE_BYTES)
    proposed_text = _read_text_no_follow(proposed, "proposed output", MAX_FILE_BYTES)
    kind = _file_kind(expected)
    if expected_text == proposed_text:
        if kind == "json":
            _parse_json_comparison(expected_text)
        elif kind == "csv":
            _canonical_csv(expected_text)
        return {
            "kind": kind,
            "result": "exact_match",
            "changed_lines": 0,
            "summary": "files are exactly equal",
        }
    if kind == "json":
        expected_value = _parse_json_comparison(expected_text)
        proposed_value = _parse_json_comparison(proposed_text)
        if _canonical_json(expected_value) == _canonical_json(proposed_value):
            return {
                "kind": "json",
                "result": "material_match",
                "changed_lines": 0,
                "summary": "JSON values match after canonical ordering",
            }
    elif kind == "csv":
        if _canonical_csv(expected_text) == _canonical_csv(proposed_text):
            return {
                "kind": "csv",
                "result": "material_match",
                "changed_lines": 0,
                "summary": "CSV rows match after canonical ordering",
            }
    changed_lines = _changed_line_count(expected_text, proposed_text)
    return {
        "kind": kind,
        "result": "mismatch",
        "changed_lines": changed_lines,
        "summary": "{} changed line(s) require human review".format(changed_lines),
    }


def _parse_json_comparison(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError as error:
        raise ValueError("comparison file contains invalid JSON") from error


def _canonical_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _canonical_csv(text):
    try:
        rows = list(csv.reader(io.StringIO(text, newline=""), strict=True))
    except csv.Error as error:
        raise ValueError("comparison file contains invalid CSV") from error
    if not rows or not rows[0] or any(not column for column in rows[0]):
        raise ValueError("comparison file contains invalid CSV header")
    header = rows[0]
    if len(header) != len(set(header)):
        raise ValueError("comparison file contains invalid CSV duplicate columns")
    if any(len(row) != len(header) for row in rows[1:]):
        raise ValueError("comparison file contains invalid CSV row width")
    normalized = [dict(zip(header, row)) for row in rows[1:]]
    return sorted(
        [{key: row[key] for key in sorted(row)} for row in normalized],
        key=lambda row: json.dumps(row, ensure_ascii=False, sort_keys=True),
    )


def _file_kind(path):
    suffix = Path(path).suffix.lower()
    if suffix == ".json":
        return "json"
    if suffix == ".csv":
        return "csv"
    return "text"


def _changed_line_count(left, right):
    left_lines = left.splitlines()
    right_lines = right.splitlines()
    return sum(
        1
        for index in range(max(len(left_lines), len(right_lines)))
        if (left_lines[index] if index < len(left_lines) else None)
        != (right_lines[index] if index < len(right_lines) else None)
    )


def _freshness(state, workspace):
    integrity_reasons = []
    for evidence in state["evidence"]:
        reason = _stored_hash_reason(
            workspace,
            evidence["stored_path"],
            evidence["sha256"],
            "evidence {}".format(evidence["id"]),
        )
        if reason:
            integrity_reasons.append(reason)
    for case in state["shadow_cases"]:
        for role, record in case["files"].items():
            reason = _stored_hash_reason(
                workspace,
                record["stored_path"],
                record["sha256"],
                "case {} {}".format(case["case_id"], role),
            )
            if reason:
                integrity_reasons.append(reason)
    integrity_reasons.extend(_pack_freshness_reasons(state, workspace))

    decision_reasons = []
    last = state["last_decision"]
    if last["evaluated_at"] is not None:
        if last["stale"] or last["evidence_snapshot_hash"] != _evidence_snapshot_hash(state):
            decision_reasons.append("assessment changed after evaluation")
    reasons = integrity_reasons + decision_reasons
    return {
        "stale": bool(reasons),
        "stale_reasons": reasons,
        "integrity_reasons": integrity_reasons,
    }


def _stored_hash_reason(workspace, relative_path, expected_hash, label):
    path = workspace / relative_path
    try:
        actual = _sha256_file_no_follow(path, label, MAX_FILE_BYTES)
    except FileNotFoundError:
        return "{} missing".format(label)
    except (OSError, ValueError):
        return "{} no longer points to a regular copied file".format(label)
    if actual != expected_hash:
        return "{} changed after it was copied".format(label)
    return None


def _pack_freshness_reasons(state, workspace):
    reasons = []
    try:
        persisted = _read_json_no_follow(
            _pack_manifest_path(workspace), "pack manifest snapshot", MAX_PERSISTED_BYTES
        )
        if persisted != state["pack_manifest"]:
            reasons.append("pack manifest snapshot changed")
    except (OSError, ValueError):
        reasons.append("pack manifest snapshot missing or invalid")
    try:
        load_bundled_pack(state["pack_id"])
        current = _load_manifest_entry(state["pack_id"])
        if current != state["pack_manifest"]:
            reasons.append("bundled pack manifest changed")
    except (OSError, ValueError, json.JSONDecodeError):
        reasons.append("bundled pack manifest validation failed")
    return reasons


def _apply_derived_freshness(view, freshness):
    view["stale"] = freshness["stale"]
    view["stale_reasons"] = freshness["stale_reasons"]
    if freshness["stale"]:
        view["stage"] = "stale_decision"
        view["status"] = "stale_decision"
        view["decision"] = "not_ready"
        view["current_level"] = "L0"
        view["maximum_level"] = "L0"
        view["next_action"] = "Restore changed evidence or reassess the changed configuration."


def _decision_result(
    state,
    decision,
    maximum_level,
    blocking_gates,
    readiness_gaps,
    metrics,
    freshness,
    snapshot_hash,
    generated_at,
):
    return {
        "success": True,
        "assessment_id": state["assessment_id"],
        "pack_id": state["pack_id"],
        "policy_version": state["policy_version"],
        "organization": state["organization"],
        "objective": state["objective"],
        "requested_level": state["requested_level"],
        "status": state["status"],
        "stage": state["stage"],
        "decision": decision,
        "current_level": maximum_level,
        "maximum_level": maximum_level,
        "next_action": state["next_action"],
        "blocking_gates": blocking_gates,
        "hard_gate_results": {
            gate: state["gates"][gate]["status"] for gate in HARD_GATES
        },
        "readiness_gaps": readiness_gaps,
        "metrics": metrics,
        "stale": freshness["stale"],
        "stale_reasons": freshness["stale_reasons"],
        "evidence_snapshot_hash": snapshot_hash,
        "generated_at": generated_at,
        "decided_at": generated_at,
        **_safety_fields(),
    }


def _write_reports(workspace, state, result):
    reports = workspace / "05_REPORTS"
    _ensure_directory(reports)
    metadata = _report_metadata(state, result)
    markdown_metadata = _markdown_metadata(metadata)
    csv_metadata = [(key, value) for key, value in metadata.items()]

    markdown_reports = {
        "current_workflow.md": (
            "# Current Workflow\n\n{}\n\nObjective: {}\n\nAll current outputs remain drafts for human approval.\n".format(
                markdown_metadata, state["objective"]
            )
        ),
        "automation_scope.md": (
            "# Automation Scope\n\n{}\n\n{}\n\nNo external action is enabled by this assessment.\n".format(
                markdown_metadata, SAFETY_NOTICE
            )
        ),
        "connector_permissions.md": (
            "# Connector Permissions\n\n{}\n\nNo connector or external write permission is activated.\n".format(
                markdown_metadata
            )
        ),
        "recovery_plan.md": (
            "# Recovery Plan\n\n{}\n\nRecovery evidence: {} passed of {} tested.\n".format(
                markdown_metadata,
                result["metrics"]["recovery_passed"],
                result["metrics"]["recovery_tested"],
            )
        ),
        "kill_switch_plan.md": (
            "# Kill Switch Plan\n\n{}\n\nOwner status: {}. This report does not operate a kill switch.\n".format(
                markdown_metadata, state["gates"]["kill_switch_owned"]["status"]
            )
        ),
        "comparison_report.md": _comparison_markdown(state, result, markdown_metadata),
        "improvement_roadmap.md": _roadmap_markdown(result, markdown_metadata),
        "proposal_scope.md": (
            "# Proposal Scope\n\n{}\n\nDecision: `{}` / `{}`.\n\n{}\n".format(
                markdown_metadata, result["decision"], result["maximum_level"], SAFETY_NOTICE
            )
        ),
    }
    for name, content in markdown_reports.items():
        _write_text_atomic(reports / name, content)

    source_rows = [
        [item["id"], item["role"], item["classification"], item["provided_by"], item["sha256"]]
        for item in state["evidence"]
    ]
    _write_text_atomic(
        reports / "source_inventory.csv",
        _csv_report(csv_metadata, ["evidence_id", "role", "classification", "provided_by", "sha256"], source_rows),
    )
    gate_rows = [
        [gate, state["gates"][gate]["status"], state["gates"][gate]["owner"] or "", state["gates"][gate]["note"]]
        for gate in HARD_GATES
    ]
    _write_text_atomic(
        reports / "decision_table.csv",
        _csv_report(csv_metadata, ["gate", "status", "owner", "note"], gate_rows),
    )
    exception_rows = [
        [
            case["case_id"],
            case["case_class"],
            case["expected_route"],
            case["proposed_route"],
            case["exception_detected"],
        ]
        for case in state["shadow_cases"]
        if case["exception_expected"] or case["expected_route"] == "quarantine"
    ]
    _write_text_atomic(
        reports / "exception_register.csv",
        _csv_report(
            csv_metadata,
            ["case_id", "case_class", "expected_route", "proposed_route", "exception_detected"],
            exception_rows,
        ),
    )
    case_rows = [
        [
            case["case_id"],
            case["case_class"],
            case["risk_tier"],
            case["comparison"]["result"],
            case["expected_route"],
            case["proposed_route"],
            case["unsupported_claims"],
            case["elapsed_seconds"],
            case["estimated_cost"],
            case["correction_category"],
        ]
        for case in state["shadow_cases"]
    ]
    _write_text_atomic(
        reports / "shadow_test_cases.csv",
        _csv_report(
            csv_metadata,
            [
                "case_id",
                "case_class",
                "risk_tier",
                "comparison",
                "expected_route",
                "proposed_route",
                "unsupported_claims",
                "elapsed_seconds",
                "estimated_cost",
                "correction_category",
            ],
            case_rows,
        ),
    )
    _write_json_atomic(reports / "readiness_decision.json", result)
    _write_text_atomic(reports / "readiness_report.html", _readiness_html(state, result, metadata))

    actual = {path.name for path in reports.iterdir() if path.is_file() and not path.name.startswith(".")}
    missing = set(REPORT_NAMES) - actual
    if missing:
        raise RuntimeError("report generation incomplete: {}".format(", ".join(sorted(missing))))
    unexpected = actual - set(REPORT_NAMES)
    if unexpected:
        raise RuntimeError(
            "unexpected report artifacts: {}".format(", ".join(sorted(unexpected)))
        )


def _report_metadata(state, result):
    return {
        "assessment_id": state["assessment_id"],
        "pack_id": state["pack_id"],
        "policy_version": str(state["policy_version"]),
        "generated_at": result["generated_at"],
        "evidence_snapshot_hash": result["evidence_snapshot_hash"],
    }


def _markdown_metadata(metadata):
    return "\n".join("- {}: `{}`".format(key, value) for key, value in metadata.items())


def _csv_report(metadata, headers, rows):
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    for key, value in metadata:
        writer.writerow([key, value])
    writer.writerow([])
    writer.writerow(headers)
    writer.writerows(rows)
    return output.getvalue()


def _comparison_markdown(state, result, metadata):
    lines = [
        "# Automation Proof Lab Comparison Report",
        "",
        metadata,
        "",
        SAFETY_NOTICE,
        "",
        "| Case | Class | Risk | Route | Content |",
        "|---|---|---|---|---|",
    ]
    for case in state["shadow_cases"]:
        route = "match" if case["expected_route"] == case["proposed_route"] else "mismatch"
        lines.append(
            "| {} | {} | {} | {} | {} |".format(
                case["case_id"],
                case["case_class"],
                case["risk_tier"],
                route,
                case["comparison"]["result"],
            )
        )
    lines.extend(["", "Decision: `{}`".format(result["decision"]), ""])
    return "\n".join(lines)


def _roadmap_markdown(result, metadata):
    lines = ["# Improvement Roadmap", "", metadata, "", SAFETY_NOTICE, ""]
    if not result["blocking_gates"] and not result["readiness_gaps"]:
        lines.append("- No blocking gaps were found for the requested advisory level.")
    for gate in result["blocking_gates"]:
        lines.append("- Pass `{}` with an accountable owner and evidence.".format(gate))
    for gap in result["readiness_gaps"]:
        lines.append("- Resolve `{}` before L3/L4 can be recommended.".format(gap))
    lines.append("")
    return "\n".join(lines)


def _readiness_html(state, result, metadata):
    metadata_html = "".join(
        "<li>{}: {}</li>".format(html.escape(key), html.escape(str(value)))
        for key, value in metadata.items()
    )
    gaps = result["blocking_gates"] + result["readiness_gaps"] + result["stale_reasons"]
    gap_html = "".join("<li>{}</li>".format(html.escape(item)) for item in gaps)
    if not gap_html:
        gap_html = "<li>No blocking gaps for the requested advisory level.</li>"
    return """<!doctype html>
<html lang="{lang}">
<meta charset="utf-8">
<title>Automation Proof Lab Readiness</title>
<body>
<h1>Automation Proof Lab Readiness</h1>
<ul>{metadata}</ul>
<p>{notice}</p>
<p><strong>Decision:</strong> {decision} ({level})</p>
<p><strong>Organization:</strong> {organization}</p>
<h2>Remaining work</h2><ul>{gaps}</ul>
</body></html>
""".format(
        lang=html.escape(state["language"]),
        metadata=metadata_html,
        notice=html.escape(SAFETY_NOTICE),
        decision=html.escape(result["decision"]),
        level=html.escape(result["maximum_level"]),
        organization=html.escape(state["organization"]),
        gaps=gap_html,
    )


def _load_verified_state(workspace):
    path = _state_path(workspace)
    try:
        state = _read_json_no_follow(path, "assessment state", MAX_PERSISTED_BYTES)
    except FileNotFoundError as error:
        if _lab_root(workspace).exists():
            _manual_recovery("assessment state is missing")
        raise ValueError("assessment workspace has not been created") from error
    except (KeyError, OSError, TypeError, ValueError, UnicodeDecodeError) as error:
        _manual_recovery("assessment state is unreadable or invalid", error)
    try:
        _validate_state(state)
        entries = _read_audit_entries(_audit_path(workspace))
        audit = state["audit"]
        if len(entries) != audit["entry_count"]:
            raise ValueError("audit history count does not match state")
        if not entries or entries[-1]["entry_hash"] != audit["head_hash"]:
            raise ValueError("audit history head does not match state")
        if entries[-1]["state_snapshot_hash"] != _state_snapshot_hash(state):
            raise ValueError("state does not match the latest audit snapshot")
        if entries[-1]["evidence_snapshot_hash"] != _evidence_snapshot_hash(state):
            raise ValueError("evidence does not match the latest audit snapshot")
        if any(entry["assessment_id"] != state["assessment_id"] for entry in entries):
            raise ValueError("audit assessment identity changed")
        if any(entry["pack_id"] != state["pack_id"] for entry in entries):
            raise ValueError("audit pack identity changed")
    except (KeyError, OSError, TypeError, ValueError, UnicodeDecodeError) as error:
        _manual_recovery("audit or persisted state integrity check failed", error)
    return state


def _read_verified_state(workspace, timeout_seconds=5.0):
    deadline = time.monotonic() + timeout_seconds
    while True:
        try:
            with _mutation_lock(workspace):
                return _load_verified_state(workspace)
        except ValueError as error:
            if "proof lab mutation is already in progress" not in str(error):
                raise
            if time.monotonic() >= deadline:
                raise
            time.sleep(0.01)


def _validate_state(state):
    required = {
        "schema_version",
        "assessment_id",
        "pack_id",
        "pack_snapshot",
        "pack_manifest",
        "organization",
        "objective",
        "requested_level",
        "language",
        "policy_version",
        "created_at",
        "updated_at",
        "status",
        "stage",
        "decision",
        "current_level",
        "maximum_level",
        "next_action",
        "evidence",
        "shadow_cases",
        "gates",
        "transitions",
        "last_decision",
        "audit",
    }
    if not isinstance(state, dict) or set(state) != required:
        raise ValueError("assessment state fields do not match schema version 2")
    if state["schema_version"] != SCHEMA_VERSION:
        raise ValueError("assessment state schema_version is not supported")
    if not isinstance(state["assessment_id"], str) or not state["assessment_id"].startswith("asmt_"):
        raise ValueError("assessment_id is invalid")
    _require_safe_id(state["pack_id"], "pack_id")
    if state["requested_level"] not in REQUESTED_LEVELS:
        raise ValueError("requested_level is invalid")
    if state["language"] not in {"ja", "en"}:
        raise ValueError("language is invalid")
    if type(state["policy_version"]) is not int or state["policy_version"] < 1:
        raise ValueError("policy_version is invalid")
    if state["decision"] not in DECISIONS:
        raise ValueError("decision is invalid")
    if state["current_level"] not in REQUESTED_LEVELS or state["maximum_level"] not in REQUESTED_LEVELS:
        raise ValueError("automation level is invalid")
    if state["status"] != state["stage"] or not isinstance(state["stage"], str):
        raise ValueError("assessment status and stage are invalid")
    if not isinstance(state["next_action"], str) or not state["next_action"]:
        raise ValueError("next_action is invalid")
    if set(state["gates"]) != set(HARD_GATES):
        raise ValueError("assessment hard gates do not match schema version 2")
    if not isinstance(state["evidence"], list) or not isinstance(state["shadow_cases"], list):
        raise ValueError("assessment evidence and cases must be lists")
    evidence_ids = set()
    for item in state["evidence"]:
        if not isinstance(item, dict) or set(item) != {
            "id",
            "evidence_id",
            "source_name",
            "stored_path",
            "sha256",
            "bytes",
            "role",
            "classification",
            "provided_by",
            "added_at",
            "verified_at",
            "status",
        }:
            raise ValueError("evidence record fields are invalid")
        if item["id"] != item["evidence_id"]:
            raise ValueError("evidence record identity is invalid")
        _require_safe_id(item["id"], "evidence id")
        if item["id"] in evidence_ids:
            raise ValueError("duplicate evidence id")
        evidence_ids.add(item["id"])
        _validate_file_record(item, ".proof_lab/evidence/")
    case_ids = set()
    for case in state["shadow_cases"]:
        if not isinstance(case, dict) or set(case) != {
            "case_id",
            "risk_tier",
            "case_class",
            "expected_route",
            "proposed_route",
            "exception_expected",
            "exception_detected",
            "recovery_tested",
            "recovery_passed",
            "unsupported_claims",
            "duplicate_action_simulations",
            "quarantine_expected",
            "quarantine_triggered",
            "elapsed_seconds",
            "estimated_cost",
            "correction_category",
            "files",
            "comparison",
            "added_at",
        }:
            raise ValueError("shadow case record fields are invalid")
        _require_safe_id(case["case_id"], "case_id")
        if case["case_id"] in case_ids:
            raise ValueError("duplicate case_id")
        case_ids.add(case["case_id"])
        if case.get("case_class") not in CASE_CLASSES or case.get("risk_tier") not in RISK_TIERS:
            raise ValueError("shadow case class or risk tier is invalid")
        if case.get("expected_route") not in ROUTES or case.get("proposed_route") not in ROUTES:
            raise ValueError("shadow case route is invalid")
        for field in (
            "exception_expected",
            "exception_detected",
            "recovery_tested",
            "recovery_passed",
            "quarantine_expected",
            "quarantine_triggered",
        ):
            _require_bool(case[field], field)
        _require_nonnegative_int(case["unsupported_claims"], "unsupported_claims")
        _require_nonnegative_int(
            case["duplicate_action_simulations"], "duplicate_action_simulations"
        )
        _require_nonnegative_number(case["elapsed_seconds"], "elapsed_seconds")
        _require_nonnegative_number(case["estimated_cost"], "estimated_cost")
        _optional_text(case["correction_category"], "correction_category", 128)
        if set(case.get("files", {})) != {"input", "expected", "proposed"}:
            raise ValueError("shadow case files are invalid")
        for record in case["files"].values():
            _validate_file_record(record, ".proof_lab/cases/{}/".format(case["case_id"]))
        comparison = case["comparison"]
        if not isinstance(comparison, dict) or set(comparison) != {
            "kind", "result", "changed_lines", "summary"
        }:
            raise ValueError("shadow case comparison is invalid")
        if comparison["kind"] not in {"text", "json", "csv"}:
            raise ValueError("shadow case comparison kind is invalid")
        if comparison["result"] not in {"exact_match", "material_match", "mismatch"}:
            raise ValueError("shadow case comparison result is invalid")
    for gate in HARD_GATES:
        record = state["gates"][gate]
        if not isinstance(record, dict) or set(record) != {
            "status", "owner", "evidence_ids", "note", "updated_at"
        }:
            raise ValueError("gate record is invalid")
        if record["status"] not in GATE_STATUSES:
            raise ValueError("gate status is invalid")
        if record["owner"] is not None and not isinstance(record["owner"], str):
            raise ValueError("gate owner is invalid")
        if not isinstance(record["evidence_ids"], list) or any(
            evidence_id not in evidence_ids for evidence_id in record["evidence_ids"]
        ):
            raise ValueError("gate evidence references are invalid")
    if not isinstance(state["transitions"], list) or not state["transitions"]:
        raise ValueError("transition history is invalid")
    for transition in state["transitions"]:
        if not isinstance(transition, dict) or set(transition) != {
            "actor",
            "timestamp",
            "prior_stage",
            "new_stage",
            "evidence_snapshot_hash",
            "reason",
        }:
            raise ValueError("transition record is invalid")
        if not isinstance(transition["actor"], str) or not transition["actor"]:
            raise ValueError("transition actor is invalid")
        if not isinstance(transition["new_stage"], str) or not transition["new_stage"]:
            raise ValueError("transition stage is invalid")
        if not HEX_64_RE.fullmatch(transition["evidence_snapshot_hash"]):
            raise ValueError("transition snapshot hash is invalid")
    last_decision = state["last_decision"]
    if not isinstance(last_decision, dict) or set(last_decision) != {
        "decision", "maximum_level", "evaluated_at", "evidence_snapshot_hash", "stale"
    }:
        raise ValueError("last decision record is invalid")
    if last_decision["decision"] not in DECISIONS:
        raise ValueError("last decision value is invalid")
    if last_decision["maximum_level"] not in REQUESTED_LEVELS:
        raise ValueError("last decision level is invalid")
    if type(last_decision["stale"]) is not bool:
        raise ValueError("last decision stale flag is invalid")
    if last_decision["evaluated_at"] is None:
        if last_decision["evidence_snapshot_hash"] is not None:
            raise ValueError("unevaluated decision snapshot is invalid")
    elif not isinstance(last_decision["evidence_snapshot_hash"], str) or not HEX_64_RE.fullmatch(
        last_decision["evidence_snapshot_hash"]
    ):
        raise ValueError("last decision snapshot hash is invalid")
    audit = state["audit"]
    if not isinstance(audit, dict) or set(audit) != {"entry_count", "head_hash"}:
        raise ValueError("audit state is invalid")
    if type(audit["entry_count"]) is not int or audit["entry_count"] < 1:
        raise ValueError("audit entry count is invalid")
    if not isinstance(audit["head_hash"], str) or not HEX_64_RE.fullmatch(audit["head_hash"]):
        raise ValueError("audit head hash is invalid")


def _validate_file_record(record, prefix):
    if not isinstance(record, dict):
        raise ValueError("file record is invalid")
    for field in ("stored_path", "sha256", "bytes"):
        if field not in record:
            raise ValueError("file record is incomplete")
    path = record["stored_path"]
    _validate_relative_path(path)
    if not path.startswith(prefix):
        raise ValueError("stored file path has an invalid location")
    if not isinstance(record["sha256"], str) or not HEX_64_RE.fullmatch(record["sha256"]):
        raise ValueError("stored file hash is invalid")
    if type(record["bytes"]) is not int or not 0 <= record["bytes"] <= MAX_FILE_BYTES:
        raise ValueError("stored file size is invalid")


def _read_audit_entries(path):
    try:
        text = _read_text_no_follow(path, "audit history", MAX_PERSISTED_BYTES)
    except FileNotFoundError as error:
        raise ValueError("audit history is missing") from error
    if not text or not text.endswith("\n"):
        raise ValueError("audit history is missing or truncated")
    entries = []
    previous_hash = None
    for sequence, line in enumerate(text.splitlines(), start=1):
        if not line:
            raise ValueError("audit history contains an empty record")
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError("audit history contains invalid JSON") from error
        if not isinstance(entry, dict):
            raise ValueError("audit history entry must be an object")
        if entry.get("sequence") != sequence:
            raise ValueError("audit history sequence is broken")
        if entry.get("previous_hash") != previous_hash:
            raise ValueError("audit history previous hash is broken")
        entry_hash = entry.get("entry_hash")
        if not isinstance(entry_hash, str) or not HEX_64_RE.fullmatch(entry_hash):
            raise ValueError("audit history hash is invalid")
        if entry_hash != _audit_hash(entry):
            raise ValueError("audit history hash mismatch")
        for field in (
            "assessment_id",
            "pack_id",
            "policy_version",
            "stage",
            "evidence_snapshot_hash",
            "state_snapshot_hash",
        ):
            if field not in entry:
                raise ValueError("audit history context is incomplete")
        previous_hash = entry_hash
        entries.append(entry)
    return entries


def _commit_state(workspace, state, action, payload):
    state["updated_at"] = _utc_now()
    entry = _append_audit(workspace, state, action, payload)
    state["audit"] = {
        "entry_count": entry["sequence"],
        "head_hash": entry["entry_hash"],
    }
    _write_json_atomic(_state_path(workspace), state)


def _append_audit(workspace, state, action, payload):
    audit = state["audit"]
    entry = {
        "sequence": audit["entry_count"] + 1,
        "timestamp": _utc_now(),
        "action": action,
        "payload": _json_copy(payload),
        "previous_hash": audit["head_hash"],
        "assessment_id": state["assessment_id"],
        "pack_id": state["pack_id"],
        "policy_version": state["policy_version"],
        "stage": state["stage"],
        "evidence_snapshot_hash": _evidence_snapshot_hash(state),
        "state_snapshot_hash": _state_snapshot_hash(state),
    }
    entry["entry_hash"] = _audit_hash(entry)
    data = (json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    directory_fd = _open_directory_fd(_lab_root(workspace), "proof lab directory")
    descriptor = None
    try:
        descriptor = os.open(
            "audit.jsonl",
            os.O_WRONLY | os.O_APPEND | os.O_CREAT | _no_follow_flag(),
            0o600,
            dir_fd=directory_fd,
        )
        file_stat = os.fstat(descriptor)
        if not stat.S_ISREG(file_stat.st_mode):
            raise ValueError("audit history must be a regular file")
        _write_all(descriptor, data)
        os.fsync(descriptor)
        os.fsync(directory_fd)
    except OSError as error:
        _manual_recovery("cannot append audit history safely", error)
    finally:
        if descriptor is not None:
            os.close(descriptor)
        os.close(directory_fd)
    return entry


def _audit_hash(entry):
    payload = dict(entry)
    payload.pop("entry_hash", None)
    return _hash_json(payload)


def _state_snapshot_hash(state):
    snapshot = _json_copy(state)
    snapshot.pop("audit", None)
    return _hash_json(snapshot)


def _evidence_snapshot_hash(state):
    snapshot = {
        "assessment_id": state["assessment_id"],
        "pack_id": state["pack_id"],
        "pack_manifest": state["pack_manifest"],
        "policy_version": state["policy_version"],
        "evidence": state["evidence"],
        "shadow_cases": state["shadow_cases"],
        "gates": state["gates"],
    }
    return _hash_json(snapshot)


def _hash_json(payload):
    encoded = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _transition(state, new_stage, actor, reason, prior_stage=None, force=False):
    if prior_stage is None and not force:
        prior_stage = state["stage"]
    if not force and prior_stage == new_stage:
        return
    transition = {
        "actor": actor,
        "timestamp": _utc_now(),
        "prior_stage": prior_stage,
        "new_stage": new_stage,
        "evidence_snapshot_hash": _evidence_snapshot_hash(state),
        "reason": reason,
    }
    state["transitions"].append(transition)
    state["stage"] = new_stage
    state["status"] = new_stage


def _mark_mutation(state, pre_evaluation_stage, reason):
    if state["last_decision"]["evaluated_at"] is not None:
        state["last_decision"]["stale"] = True
        state["decision"] = "not_ready"
        state["current_level"] = "L0"
        state["maximum_level"] = "L0"
        state["next_action"] = "Re-evaluate the changed assessment."
        _transition(state, "stale_decision", "operator", reason)
    else:
        state["next_action"] = "Complete hard gates and shadow evidence, then evaluate."
        _transition(state, pre_evaluation_stage, "operator", reason)


@contextmanager
def _mutation_lock(workspace):
    lab_fd = _open_directory_fd(_lab_root(workspace), "proof lab directory")
    lock_fd = None
    identity = None
    try:
        try:
            lock_fd = os.open(
                "mutation.lock",
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | _no_follow_flag(),
                0o600,
                dir_fd=lab_fd,
            )
        except FileExistsError as error:
            raise ValueError(
                "proof lab mutation is already in progress, or a stale mutation lock remains; "
                "confirm no process is running before removing .proof_lab/mutation.lock"
            ) from error
        lock_stat = os.fstat(lock_fd)
        identity = (lock_stat.st_dev, lock_stat.st_ino)
        metadata = json.dumps(
            {"pid": os.getpid(), "created_at": _utc_now(), "purpose": "proof_lab_mutation"},
            sort_keys=True,
        ).encode("utf-8") + b"\n"
        _write_all(lock_fd, metadata)
        os.fsync(lock_fd)
        os.fsync(lab_fd)
        yield
    finally:
        cleanup_error = None
        if identity is not None:
            try:
                current = os.stat("mutation.lock", dir_fd=lab_fd, follow_symlinks=False)
                if (current.st_dev, current.st_ino) != identity:
                    raise RuntimeError("manual_recovery_required: mutation lock changed unexpectedly")
                os.unlink("mutation.lock", dir_fd=lab_fd)
                os.fsync(lab_fd)
            except Exception as error:
                cleanup_error = error
        if lock_fd is not None:
            os.close(lock_fd)
        os.close(lab_fd)
        if cleanup_error is not None:
            raise cleanup_error


def _copy_intake_file(workspace, source_path, destination_root, prefix, label):
    source = _validate_source_path(source_path, label)
    suffix = source.suffix.lower()
    destination_name = "{}-{}{}".format(prefix, secrets.token_hex(8), suffix)
    source_parent_fd = None
    source_fd = None
    destination_fd = None
    destination_dir_fd = None
    destination_created = False
    try:
        source_parent_fd = _open_directory_fd(source.parent, "{} parent".format(label))
        before = os.stat(source.name, dir_fd=source_parent_fd, follow_symlinks=False)
        if stat.S_ISLNK(before.st_mode):
            raise ValueError("{} cannot be a symlink".format(label))
        source_fd = os.open(
            source.name, os.O_RDONLY | _no_follow_flag(), dir_fd=source_parent_fd
        )
        opened = os.fstat(source_fd)
        if not stat.S_ISREG(opened.st_mode):
            raise ValueError("{} must be a regular file".format(label))
        if opened.st_size > MAX_FILE_BYTES:
            raise ValueError("{} is larger than the {} byte limit".format(label, MAX_FILE_BYTES))
        source_identity = (opened.st_dev, opened.st_ino)
        if source_identity != (before.st_dev, before.st_ino):
            raise ValueError("{} changed before copy".format(label))

        destination_dir_fd = _open_directory_fd(destination_root, "intake destination")
        destination_fd = os.open(
            destination_name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | _no_follow_flag(),
            0o600,
            dir_fd=destination_dir_fd,
        )
        destination_created = True
        digest, size = _copy_open_descriptor(source_fd, destination_fd, label)
        os.fsync(destination_fd)
        after = os.stat(source.name, dir_fd=source_parent_fd, follow_symlinks=False)
        if stat.S_ISLNK(after.st_mode) or (after.st_dev, after.st_ino) != source_identity:
            raise ValueError("{} changed during copy".format(label))
        os.fsync(destination_dir_fd)
        stored = destination_root / destination_name
        return {
            "source_name": source.name,
            "stored_path": _relative(workspace, stored),
            "sha256": digest,
            "bytes": size,
        }
    except OSError as error:
        if error.errno in {getattr(os, "ELOOP", 62)}:
            raise ValueError("{} cannot be a symlink".format(label)) from error
        raise ValueError("{} cannot be copied safely".format(label)) from error
    finally:
        if destination_fd is not None:
            os.close(destination_fd)
        if destination_created and destination_dir_fd is not None:
            active_exception = __import__("sys").exc_info()[0] is not None
            if active_exception:
                try:
                    os.unlink(destination_name, dir_fd=destination_dir_fd)
                    os.fsync(destination_dir_fd)
                except FileNotFoundError:
                    pass
        if destination_dir_fd is not None:
            os.close(destination_dir_fd)
        if source_fd is not None:
            os.close(source_fd)
        if source_parent_fd is not None:
            os.close(source_parent_fd)


def _copy_open_descriptor(source_fd, destination_fd, label):
    digest = hashlib.sha256()
    total = 0
    while True:
        chunk = os.read(source_fd, 65536)
        if not chunk:
            break
        total += len(chunk)
        if total > MAX_FILE_BYTES:
            raise ValueError("{} is larger than the {} byte limit".format(label, MAX_FILE_BYTES))
        digest.update(chunk)
        _write_all(destination_fd, chunk)
    return digest.hexdigest(), total


def _validate_source_path(source_path, label):
    source = Path(source_path).expanduser()
    if any(part in {"..", ""} for part in source.parts):
        raise ValueError("{} path cannot contain traversal".format(label))
    source = source.absolute()
    if source.suffix.lower() in SCRIPT_EXTENSIONS:
        raise ValueError("{} cannot be a script or executable file".format(label))
    try:
        file_stat = source.lstat()
    except OSError as error:
        raise ValueError("{} cannot be read".format(label)) from error
    if stat.S_ISLNK(file_stat.st_mode):
        raise ValueError("{} cannot be a symlink".format(label))
    if not stat.S_ISREG(file_stat.st_mode):
        raise ValueError("{} must be a regular file".format(label))
    if file_stat.st_size > MAX_FILE_BYTES:
        raise ValueError("{} is larger than the {} byte limit".format(label, MAX_FILE_BYTES))
    _reject_symlink_parents(source, label)
    return source


def _reject_symlink_parents(path, label):
    current = Path(path.anchor)
    for part in path.parts[1:-1]:
        current = current / part
        try:
            if current.is_symlink():
                raise ValueError("{} parent cannot be a symlink".format(label))
        except OSError as error:
            raise ValueError("{} parent cannot be inspected".format(label)) from error


def _without_source_name(record):
    result = dict(record)
    result.pop("source_name", None)
    return result


def _unlink_stored_file(workspace, relative_path):
    path = workspace / relative_path
    try:
        if path.is_symlink():
            raise ValueError("stored file changed unexpectedly")
        path.unlink()
    except FileNotFoundError:
        pass


def _remove_case_directory(case_root):
    if not case_root.exists() and not case_root.is_symlink():
        return
    if case_root.is_symlink() or not case_root.is_dir():
        raise RuntimeError("manual_recovery_required: case storage changed unexpectedly")
    shutil.rmtree(case_root)


def _pack_manifest_path(workspace):
    return _lab_root(workspace) / "pack_manifest.json"


def _state_path(workspace):
    return _lab_root(workspace) / "state.json"


def _audit_path(workspace):
    return _lab_root(workspace) / "audit.jsonl"


def _lab_root(workspace):
    return workspace / ".proof_lab"


def _load_manifest_entry(pack_id):
    payload = resources.files("ai_automation_kit").joinpath("packs", "manifest.json").read_bytes()
    try:
        manifest = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("bundled workflow pack manifest is invalid") from error
    entry = manifest.get(pack_id)
    if not isinstance(entry, dict):
        raise ValueError("unknown workflow pack: {}".format(pack_id))
    return {
        "pack_id": pack_id,
        "manifest_sha256": hashlib.sha256(payload).hexdigest(),
        "entry": _json_copy(entry),
    }


def _read_json_no_follow(path, label, limit):
    text = _read_text_no_follow(path, label, limit)
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as error:
        raise ValueError("{} contains invalid JSON".format(label)) from error
    if not isinstance(payload, dict):
        raise ValueError("{} must contain a JSON object".format(label))
    return payload


def _read_text_no_follow(path, label, limit):
    try:
        return _read_bytes_no_follow(path, label, limit).decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("{} must be UTF-8 text".format(label)) from error


def _read_bytes_no_follow(path, label, limit):
    path = Path(path)
    parent_fd = _open_directory_fd(path.parent, "{} parent".format(label))
    descriptor = None
    try:
        descriptor = os.open(path.name, os.O_RDONLY | _no_follow_flag(), dir_fd=parent_fd)
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode):
            raise ValueError("{} must be a regular file".format(label))
        if opened.st_size > limit:
            raise ValueError("{} exceeds the size limit".format(label))
        chunks = []
        total = 0
        while True:
            chunk = os.read(descriptor, 65536)
            if not chunk:
                break
            total += len(chunk)
            if total > limit:
                raise ValueError("{} exceeds the size limit".format(label))
            chunks.append(chunk)
        current = os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
        if stat.S_ISLNK(current.st_mode) or (current.st_dev, current.st_ino) != (
            opened.st_dev,
            opened.st_ino,
        ):
            raise ValueError("{} changed while being read".format(label))
        return b"".join(chunks)
    finally:
        if descriptor is not None:
            os.close(descriptor)
        os.close(parent_fd)


def _sha256_file_no_follow(path, label, limit):
    return hashlib.sha256(_read_bytes_no_follow(path, label, limit)).hexdigest()


def _write_json_atomic(path, payload):
    _write_text_atomic(
        path, json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    )


def _write_text_atomic(path, text):
    path = Path(path)
    _ensure_directory(path.parent)
    directory_fd = _open_directory_fd(path.parent, "write destination")
    temp_name = ".{}.{}.tmp".format(path.name, secrets.token_hex(8))
    descriptor = None
    try:
        descriptor = os.open(
            temp_name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | _no_follow_flag(),
            0o600,
            dir_fd=directory_fd,
        )
        _write_all(descriptor, text.encode("utf-8"))
        os.fsync(descriptor)
        os.rename(temp_name, path.name, src_dir_fd=directory_fd, dst_dir_fd=directory_fd)
        os.fsync(directory_fd)
    finally:
        if descriptor is not None:
            os.close(descriptor)
        try:
            os.unlink(temp_name, dir_fd=directory_fd)
        except FileNotFoundError:
            pass
        os.close(directory_fd)


def _write_all(descriptor, data):
    view = memoryview(data)
    while view:
        written = os.write(descriptor, view)
        if written <= 0:
            raise OSError("short write")
        view = view[written:]


def _open_directory_fd(path, label):
    try:
        descriptor = os.open(
            Path(path), os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | _no_follow_flag()
        )
    except OSError as error:
        raise ValueError("{} must be a trusted directory".format(label)) from error
    opened = os.fstat(descriptor)
    if not stat.S_ISDIR(opened.st_mode):
        os.close(descriptor)
        raise ValueError("{} must be a directory".format(label))
    return descriptor


def _no_follow_flag():
    return getattr(os, "O_NOFOLLOW", 0)


def _ensure_directory(path):
    path = Path(path)
    if path.is_symlink():
        raise ValueError("directory cannot be a symlink: {}".format(path))
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    if not path.is_dir() or path.is_symlink():
        raise ValueError("path must be a regular directory: {}".format(path))


def _workspace(workspace, create=False):
    raw = Path(workspace).expanduser()
    if any(part in {"..", ""} for part in raw.parts):
        raise ValueError("workspace path cannot contain traversal")
    path = raw.absolute()
    if create:
        _ensure_directory(path)
    elif not path.exists():
        raise ValueError("assessment workspace has not been created")
    if path.is_symlink() or not path.is_dir():
        raise ValueError("workspace must be a regular directory")
    return path


def _relative(workspace, path):
    try:
        relative = Path(path).relative_to(workspace).as_posix()
    except ValueError as error:
        raise ValueError("stored file escaped assessment workspace") from error
    _validate_relative_path(relative)
    return relative


def _validate_relative_path(value):
    if not isinstance(value, str):
        raise ValueError("stored path must be a string")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError("stored path is unsafe")


def _public_summary(state):
    return {
        "assessment_id": state["assessment_id"],
        "pack_id": state["pack_id"],
        "policy_version": state["policy_version"],
        "organization": state["organization"],
        "requested_level": state["requested_level"],
        "status": state["status"],
        "stage": state["stage"],
        "decision": state["decision"],
        "current_level": state["current_level"],
        "maximum_level": state["maximum_level"],
        "next_action": state["next_action"],
        **_safety_fields(),
    }


def _safety_fields():
    return {
        "advisory_only": True,
        "external_actions_activated": False,
        "human_approval_removed": False,
        "safety_notice": SAFETY_NOTICE,
    }


def _next_action_for_decision(decision):
    if decision == "not_ready":
        return "Resolve the blocking input or completion definition before automation."
    if decision == "assist_only":
        return "Keep human approval and resolve the listed gates and shadow-test gaps."
    return "Review the advisory report; keep current human approval and external actions disabled."


def _next_id(prefix, number):
    return "{}-{:04d}".format(prefix, number)


def _require_level(value):
    if value not in REQUESTED_LEVELS:
        raise ValueError("requested_level must be one of L0, L1, L2, L3, L4")


def _require_safe_id(value, label):
    if not isinstance(value, str) or not SAFE_ID_RE.fullmatch(value):
        raise ValueError("{} must be a safe non-empty identifier".format(label))


def _require_text(value, label, maximum):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("{} must be a non-empty string".format(label))
    value = value.strip()
    if len(value) > maximum:
        raise ValueError("{} exceeds the {} character limit".format(label, maximum))
    return value


def _optional_text(value, label, maximum):
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ValueError("{} must be a string".format(label))
    value = value.strip()
    if len(value) > maximum:
        raise ValueError("{} exceeds the {} character limit".format(label, maximum))
    return value


def _require_bool(value, label):
    if type(value) is not bool:
        raise ValueError("{} must be a boolean".format(label))
    return value


def _require_nonnegative_int(value, label):
    if type(value) is not int or value < 0:
        raise ValueError("{} must be a non-negative integer".format(label))
    return value


def _require_nonnegative_number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("{} must be a non-negative number".format(label))
    value = float(value)
    if value < 0 or not math.isfinite(value):
        raise ValueError("{} must be a finite non-negative number".format(label))
    return value


def _manual_recovery(message, cause=None):
    error = ValueError("manual_recovery_required: {}".format(message))
    if cause is None:
        raise error
    raise error from cause


def _json_copy(value):
    return json.loads(json.dumps(value, ensure_ascii=False))


def _utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
