from ai_automation_kit.core.github_review import (
    build_enterprise_readiness,
    build_executive_decision_brief,
    build_manual_review_pack,
    build_operational_audit_plan,
    build_pilot_scorecard,
    build_risk_exception_register,
    build_run_summary,
    build_stakeholder_rollout_map,
    build_value_measurement_report,
    build_value_realization_plan,
    render_enterprise_readiness,
    render_executive_decision_brief,
    render_operational_audit_plan,
    render_pilot_scorecard_csv,
    render_pilot_scorecard,
    render_risk_exception_register,
    render_run_summary,
    render_stakeholder_rollout_map,
    render_value_measurement_report,
    render_value_realization_plan,
)


def test_build_run_summary_selects_adapter_next_read():
    candidate = {
        "full_name": "example/ready",
        "score": 91,
        "business_area": "operations",
        "production_gate": "ready_for_adapter",
        "license_risk": "low",
        "recommended_next_step": "Prototype an adapter",
    }

    summary = build_run_summary([candidate], [candidate], business_area="operations")
    markdown = render_run_summary(summary)

    assert summary["status"] == "ready_for_adapter"
    assert summary["next_read"] == "adapter_starter/README.md"
    assert summary["top_candidate"]["full_name"] == "example/ready"
    assert "GitHub Discovery Run Summary" in markdown


def test_build_manual_review_pack_limits_candidates_and_sets_actions():
    candidates = [
        {"full_name": f"example/review-{index}", "business_area": "support"}
        for index in range(8)
    ]

    pack = build_manual_review_pack(candidates, business_area="support")

    assert pack["status"] == "manual_review_required"
    assert pack["candidate_count"] == 8
    assert len(pack["candidates"]) == 5
    assert pack["next_actions"][0].startswith("Review license")


def test_build_enterprise_readiness_blocks_production_until_controls_pass():
    candidate = {
        "full_name": "example/ready",
        "score": 94,
        "production_gate": "ready_for_adapter",
        "license_risk": "low",
        "business_area": "operations",
    }
    summary = build_run_summary([candidate], [candidate], business_area="operations")

    readiness = build_enterprise_readiness(summary, [candidate], [candidate])
    markdown = render_enterprise_readiness(readiness)

    assert readiness["decision"] == "prototype_allowed"
    assert readiness["production_release"] == "blocked_until_controls_complete"
    assert readiness["required_controls"][0]["control"] == "license_review"
    assert readiness["required_controls"][0]["status"] == "required"
    assert readiness["evidence_files"][0] == "run_summary.md"
    assert "Enterprise Readiness" in markdown
    assert "blocked_until_controls_complete" in markdown


def test_build_enterprise_readiness_keeps_manual_review_candidates_out_of_prototype():
    candidate = {
        "full_name": "example/review",
        "score": 80,
        "production_gate": "manual_review_required",
        "license_risk": "medium",
        "business_area": "support",
    }
    summary = build_run_summary([candidate], [], business_area="support")

    readiness = build_enterprise_readiness(summary, [candidate], [])

    assert readiness["decision"] == "review_only"
    assert readiness["production_release"] == "blocked_until_controls_complete"
    assert "manual_review_pack.md" in readiness["evidence_files"]


def test_build_value_realization_plan_translates_candidate_into_business_outcomes():
    candidate = {
        "full_name": "example/ready",
        "score": 94,
        "production_gate": "ready_for_adapter",
        "license_risk": "low",
        "business_area": "operations",
        "business_use_case": "Use example/ready for workflow automation.",
    }
    summary = build_run_summary([candidate], [candidate], business_area="operations")

    plan = build_value_realization_plan(summary, [candidate], [candidate])
    markdown = render_value_realization_plan(plan)

    assert plan["status"] == "prototype_value_test"
    assert plan["business_area"] == "operations"
    assert plan["primary_workflow"]["candidate"] == "example/ready"
    assert plan["value_hypotheses"][0]["metric"] == "manual_handoffs_reduced"
    assert plan["measurement_plan"][0]["baseline"] == "current manual process"
    assert plan["rollout_plan"][0]["phase"] == "days_0_30"
    assert plan["go_no_go_criteria"][0].startswith("Proceed only if")
    assert "Value Realization Plan" in markdown
    assert "manual_handoffs_reduced" in markdown


def test_build_value_realization_plan_handles_no_candidate_recovery():
    summary = build_run_summary([], [], business_area="support")

    plan = build_value_realization_plan(summary, [], [])

    assert plan["status"] == "discovery_recovery"
    assert plan["primary_workflow"]["candidate"] == ""
    assert plan["rollout_plan"][0]["phase"] == "days_0_30"
    assert plan["value_hypotheses"][0]["metric"] == "candidate_quality"


def test_build_stakeholder_rollout_map_assigns_enterprise_owners():
    candidate = {
        "full_name": "example/ready",
        "score": 94,
        "production_gate": "ready_for_adapter",
        "license_risk": "low",
        "business_area": "operations",
        "recommended_next_step": "Prototype an adapter.",
    }
    summary = build_run_summary([candidate], [candidate], business_area="operations")

    rollout_map = build_stakeholder_rollout_map(summary, [candidate], [candidate])
    markdown = render_stakeholder_rollout_map(rollout_map)

    assert rollout_map["status"] == "prototype_governance"
    assert rollout_map["primary_candidate"] == "example/ready"
    assert rollout_map["roles"][0]["role"] == "executive_sponsor"
    assert rollout_map["roles"][0]["accountable_for"] == "business outcome and adoption funding"
    assert rollout_map["approval_matrix"][0]["decision"] == "prototype_start"
    assert rollout_map["approval_matrix"][0]["required_approvers"] == ["process_owner", "security_owner"]
    assert rollout_map["operating_cadence"][0]["cadence"] == "weekly"
    assert "Stakeholder Rollout Map" in markdown
    assert "executive_sponsor" in markdown


def test_build_stakeholder_rollout_map_handles_discovery_recovery():
    summary = build_run_summary([], [], business_area="support")

    rollout_map = build_stakeholder_rollout_map(summary, [], [])

    assert rollout_map["status"] == "discovery_governance"
    assert rollout_map["primary_candidate"] == ""
    assert rollout_map["approval_matrix"][0]["decision"] == "search_recovery_start"
    assert rollout_map["roles"][0]["role"] == "process_owner"


def test_build_risk_exception_register_records_open_enterprise_risks():
    candidate = {
        "full_name": "example/review",
        "score": 86,
        "production_gate": "manual_review_required",
        "license_risk": "medium",
        "business_area": "support",
        "open_issues": 180,
        "updated_at": "2025-01-01T00:00:00Z",
        "license": "MPL-2.0",
    }
    summary = build_run_summary([candidate], [], business_area="support")

    register = build_risk_exception_register(summary, [candidate], [])
    markdown = render_risk_exception_register(register)

    assert register["status"] == "exceptions_open"
    assert register["business_area"] == "support"
    assert register["exceptions"][0]["risk"] == "prototype_not_allowed"
    assert register["exceptions"][0]["owner"] == "process_owner"
    assert any(item["risk"] == "license_review_required" for item in register["exceptions"])
    assert any(item["risk"] == "maintenance_review_required" for item in register["exceptions"])
    assert register["promotion_rule"].startswith("Do not promote")
    assert "Risk Exception Register" in markdown
    assert "license_review_required" in markdown


def test_build_risk_exception_register_tracks_ready_candidate_controls():
    candidate = {
        "full_name": "example/ready",
        "score": 94,
        "production_gate": "ready_for_adapter",
        "license_risk": "low",
        "business_area": "operations",
        "open_issues": 12,
        "updated_at": "2026-06-10T00:00:00Z",
        "license": "MIT",
    }
    summary = build_run_summary([candidate], [candidate], business_area="operations")

    register = build_risk_exception_register(summary, [candidate], [candidate])

    assert register["status"] == "pilot_controls_open"
    assert register["exceptions"][0]["risk"] == "dry_run_evidence_missing"
    assert register["exceptions"][0]["owner"] == "automation_operator"
    assert register["exceptions"][1]["risk"] == "approval_log_missing"


def test_build_operational_audit_plan_defines_post_pilot_evidence():
    candidate = {
        "full_name": "example/ready",
        "score": 94,
        "production_gate": "ready_for_adapter",
        "license_risk": "low",
        "business_area": "operations",
        "open_issues": 12,
        "updated_at": "2026-06-10T00:00:00Z",
    }
    summary = build_run_summary([candidate], [candidate], business_area="operations")

    plan = build_operational_audit_plan(summary, [candidate], [candidate])
    markdown = render_operational_audit_plan(plan)

    assert plan["status"] == "pilot_audit_required"
    assert plan["primary_candidate"] == "example/ready"
    assert plan["audit_scope"][0]["area"] == "approval_integrity"
    assert plan["audit_scope"][0]["required_evidence"] == "approval_request, approval_decision, reviewer, timestamp, rejection reason when applicable"
    assert plan["cadence"][0]["frequency"] == "per_run"
    assert plan["stop_triggers"][0].startswith("Stop promotion")
    assert "Operational Audit Plan" in markdown
    assert "approval_integrity" in markdown


def test_build_operational_audit_plan_handles_discovery_recovery():
    summary = build_run_summary([], [], business_area="support")

    plan = build_operational_audit_plan(summary, [], [])

    assert plan["status"] == "discovery_audit_required"
    assert plan["primary_candidate"] == ""
    assert plan["audit_scope"][0]["area"] == "query_recovery_trace"
    assert plan["cadence"][0]["frequency"] == "per_query_batch"


def test_build_value_measurement_report_defines_pilot_metrics():
    candidate = {
        "full_name": "example/ready",
        "score": 94,
        "production_gate": "ready_for_adapter",
        "license_risk": "low",
        "business_area": "operations",
    }
    summary = build_run_summary([candidate], [candidate], business_area="operations")

    report = build_value_measurement_report(summary, [candidate], [candidate])
    markdown = render_value_measurement_report(report)

    assert report["status"] == "pilot_measurement_required"
    assert report["primary_candidate"] == "example/ready"
    assert report["metric_cards"][0]["metric"] == "manual_handoffs_reduced"
    assert report["metric_cards"][0]["baseline_required"] == "handoff_count_per_case"
    assert report["decision_thresholds"][0].startswith("Continue only if")
    assert "Value Measurement Report" in markdown
    assert "manual_handoffs_reduced" in markdown


def test_build_value_measurement_report_handles_discovery_recovery():
    summary = build_run_summary([], [], business_area="support")

    report = build_value_measurement_report(summary, [], [])

    assert report["status"] == "discovery_measurement_required"
    assert report["primary_candidate"] == ""
    assert report["metric_cards"][0]["metric"] == "candidate_quality"
    assert report["decision_thresholds"][0].startswith("Continue discovery")


def test_build_executive_decision_brief_turns_discovery_into_buying_decision():
    candidate = {
        "full_name": "example/ready",
        "score": 94,
        "production_gate": "ready_for_adapter",
        "license_risk": "low",
        "business_area": "operations",
        "business_use_case": "Use example/ready for workflow automation.",
        "adoption_effort": "medium",
        "decision": "prototype",
    }
    summary = build_run_summary([candidate], [candidate], business_area="operations")

    brief = build_executive_decision_brief(summary, [candidate], [candidate])
    markdown = render_executive_decision_brief(brief)

    assert brief["decision"] == "approve_controlled_pilot"
    assert brief["primary_candidate"] == "example/ready"
    assert brief["investment_case"]["pilot_scope"] == "one narrow operations workflow"
    assert brief["investment_case"]["expected_return_signals"][0] == "manual handoffs reduced by 30% or more"
    assert brief["board_level_risks"][0]["risk"] == "automation_without_controls"
    assert brief["approval_request"]["decision_needed"] == "approve a 30-day controlled pilot"
    assert "Executive Decision Brief" in markdown
    assert "approve_controlled_pilot" in markdown


def test_build_executive_decision_brief_blocks_spend_when_discovery_is_empty():
    summary = build_run_summary([], [], business_area="finance")

    brief = build_executive_decision_brief(summary, [], [])

    assert brief["decision"] == "do_not_fund_implementation_yet"
    assert brief["primary_candidate"] == ""
    assert brief["approval_request"]["decision_needed"] == "approve another discovery batch"
    assert brief["investment_case"]["pilot_scope"] == "discovery recovery only"


def test_build_pilot_scorecard_creates_spreadsheet_ready_value_tracking():
    candidate = {
        "full_name": "example/ready",
        "score": 94,
        "production_gate": "ready_for_adapter",
        "license_risk": "low",
        "business_area": "operations",
    }
    summary = build_run_summary([candidate], [candidate], business_area="operations")

    scorecard = build_pilot_scorecard(summary, [candidate], [candidate])
    markdown = render_pilot_scorecard(scorecard)
    csv_text = render_pilot_scorecard_csv(scorecard)

    assert scorecard["status"] == "pilot_scorecard_required"
    assert scorecard["primary_candidate"] == "example/ready"
    assert scorecard["rows"][0]["metric"] == "manual_handoffs_reduced"
    assert scorecard["rows"][0]["baseline_field"] == "baseline_handoff_count"
    assert scorecard["rows"][0]["target"] == ">=30% reduction"
    assert "Pilot Scorecard" in markdown
    assert "metric,owner,baseline_field,pilot_field,target,evidence_file,decision_rule" in csv_text


def test_build_pilot_scorecard_handles_discovery_recovery():
    summary = build_run_summary([], [], business_area="support")

    scorecard = build_pilot_scorecard(summary, [], [])

    assert scorecard["status"] == "discovery_scorecard_required"
    assert scorecard["rows"][0]["metric"] == "candidate_quality"
    assert scorecard["rows"][0]["target"] == ">=1 reviewable candidate"
