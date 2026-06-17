import json
import subprocess
import sys

from ai_automation_kit.core.github import GitHubRepo
from ai_automation_kit.core.github_analysis import (
    build_business_automation_summary,
    deduplicate_candidates,
    score_github_repo,
    write_github_candidate_artifacts,
)


def test_score_github_repo_flags_high_fit_permissive_project():
    repo = GitHubRepo(
        full_name="modelcontextprotocol/servers",
        html_url="https://github.com/modelcontextprotocol/servers",
        description="Reference MCP servers",
        stars=50000,
        forks=4000,
        open_issues=120,
        license="MIT",
        topics=["mcp", "automation", "ai"],
        language="Python",
        updated_at="2026-06-10T00:00:00Z",
        rate_limit_remaining="28",
    )

    scored = score_github_repo(repo, now="2026-06-17T00:00:00Z")

    assert scored["full_name"] == "modelcontextprotocol/servers"
    assert scored["license_risk"] == "low"
    assert scored["automation_fit"] == "strong"
    assert scored["score"] >= 80
    assert "permissive license" in scored["rationale"]


def test_score_github_repo_penalizes_restrictive_or_unknown_license():
    repo = GitHubRepo(
        full_name="example/restrictive",
        html_url="https://github.com/example/restrictive",
        description="Demo",
        stars=5000,
        forks=300,
        open_issues=50,
        license="AGPL-3.0",
        topics=["automation"],
        language="TypeScript",
        updated_at="2025-01-01T00:00:00Z",
        rate_limit_remaining="28",
    )

    scored = score_github_repo(repo, now="2026-06-17T00:00:00Z")

    assert scored["license_risk"] == "high"
    assert scored["automation_fit"] in {"review", "avoid"}
    assert "license review" in scored["recommended_next_step"]


def test_score_github_repo_adds_business_area_fit():
    repo = GitHubRepo(
        full_name="example/sales-agent",
        html_url="https://github.com/example/sales-agent",
        description="AI sales outreach CRM workflow automation",
        stars=12000,
        forks=1200,
        open_issues=25,
        license="Apache-2.0",
        topics=["sales", "crm", "automation", "ai-agent"],
        language="Python",
        updated_at="2026-06-15T00:00:00Z",
        rate_limit_remaining="28",
    )

    scored = score_github_repo(repo, business_area="sales", now="2026-06-17T00:00:00Z")

    assert scored["business_area"] == "sales"
    assert scored["business_fit_score"] >= 20
    assert scored["score"] >= 90
    assert "sales" in scored["matched_business_terms"]
    assert scored["adoption_effort"] == "medium"
    assert scored["deployment_shape"] == "python_adapter"
    assert scored["decision"] == "prototype"
    assert "30-day adapter prototype" in scored["implementation_plan"][0]
    assert scored["risk_register"][0]["risk"] == "License or attribution mistake"


def test_build_business_automation_summary_recommends_top_projects():
    candidates = [
        {
            "full_name": "example/sales-agent",
            "score": 96,
            "automation_fit": "strong",
            "license_risk": "low",
            "recommended_next_step": "Prototype an adapter and extract reusable workflow ideas",
            "business_area": "sales",
            "business_fit_score": 24,
        },
        {
            "full_name": "example/agpl-tool",
            "score": 81,
            "automation_fit": "review",
            "license_risk": "high",
            "recommended_next_step": "Run license review before reuse",
            "business_area": "sales",
            "business_fit_score": 16,
        },
    ]

    summary = build_business_automation_summary(candidates, business_area="sales")

    assert summary["business_area"] == "sales"
    assert summary["strong_candidate_count"] == 1
    assert summary["license_review_count"] == 1
    assert summary["recommended_projects"][0]["full_name"] == "example/sales-agent"
    assert "Start with example/sales-agent" in summary["executive_recommendation"]
    assert summary["recommended_templates"][0]["template"] == "research-agent"
    assert summary["recommended_templates"][1]["template"] == "delivery-pipeline"


def test_build_business_automation_summary_is_cautious_without_strong_candidates():
    candidates = [
        {
            "full_name": "example/agpl-tool",
            "score": 81,
            "automation_fit": "review",
            "license_risk": "high",
            "recommended_next_step": "Run license review before reuse",
            "business_area": "sales",
            "business_fit_score": 16,
        }
    ]

    summary = build_business_automation_summary(candidates, business_area="sales")

    assert summary["recommended_projects"] == []
    assert "No low-risk strong candidate" in summary["executive_recommendation"]
    assert summary["implementation_path"][0] == "Broaden the GitHub query or lower the star threshold to find safer candidates."
    assert summary["success_metrics"][0] == "Manual handoffs reduced"


def test_deduplicate_candidates_merges_sources_and_keeps_best_score():
    candidates = [
        {
            "full_name": "example/workflow",
            "score": 71,
            "stars": 1000,
            "source_query": "workflow automation stars:>100",
            "automation_fit": "review",
        },
        {
            "full_name": "example/workflow",
            "score": 91,
            "stars": 1000,
            "source_query": "business process automation stars:>100",
            "automation_fit": "strong",
        },
    ]

    deduped = deduplicate_candidates(candidates)

    assert len(deduped) == 1
    assert deduped[0]["score"] == 91
    assert deduped[0]["automation_fit"] == "strong"
    assert deduped[0]["source_queries"] == [
        "business process automation stars:>100",
        "workflow automation stars:>100",
    ]


def test_write_github_candidate_artifacts_writes_adoption_shortlist_and_candidate_briefs(tmp_path):
    candidates = [
        {
            "full_name": "example/strong",
            "url": "https://github.com/example/strong",
            "description": "Workflow automation",
            "score": 94,
            "automation_fit": "strong",
            "license_risk": "low",
            "stars": 1200,
            "forks": 80,
            "open_issues": 12,
            "updated_at": "2026-06-10T00:00:00Z",
            "language": "Python",
            "license": "MIT",
            "business_area": "operations",
            "business_fit_score": 24,
            "matched_business_terms": ["automation", "workflow"],
            "recommended_next_step": "Prototype an adapter and extract reusable workflow ideas",
            "source_query": "workflow automation stars:>100",
        },
        {
            "full_name": "example/agpl",
            "url": "https://github.com/example/agpl",
            "description": "Useful but restrictive",
            "score": 88,
            "automation_fit": "review",
            "license_risk": "high",
            "stars": 2200,
            "forks": 120,
            "open_issues": 20,
            "updated_at": "2026-06-10T00:00:00Z",
            "language": "TypeScript",
            "license": "AGPL-3.0",
            "business_area": "operations",
            "business_fit_score": 16,
            "matched_business_terms": ["automation"],
            "recommended_next_step": "Run license review before reuse",
            "source_query": "business process automation stars:>100",
        },
    ]

    artifacts = write_github_candidate_artifacts(tmp_path, candidates, business_area="operations")

    shortlist = (tmp_path / "adoption_shortlist.md").read_text()
    shortlist_json = (tmp_path / "adoption_shortlist.json").read_text()
    brief = (tmp_path / "candidate_briefs" / "example__strong.md").read_text()
    adapter_blueprint = (tmp_path / "adapter_blueprint.md").read_text()
    adapter_blueprint_json = json.loads((tmp_path / "adapter_blueprint.json").read_text())
    adapter_readme = (tmp_path / "adapter_starter" / "README.md").read_text()
    adapter_code = (tmp_path / "adapter_starter" / "adapter.py").read_text()
    adapter_smoke = (tmp_path / "adapter_starter" / "smoke_test.py").read_text()
    adapter_sample = json.loads((tmp_path / "adapter_starter" / "sample_input.json").read_text())
    run_summary = (tmp_path / "run_summary.md").read_text()
    run_summary_json = json.loads((tmp_path / "run_summary.json").read_text())
    enterprise_readiness = (tmp_path / "enterprise_readiness.md").read_text()
    enterprise_readiness_json = json.loads((tmp_path / "enterprise_readiness.json").read_text())
    value_plan = (tmp_path / "value_realization_plan.md").read_text()
    value_plan_json = json.loads((tmp_path / "value_realization_plan.json").read_text())
    stakeholder_map = (tmp_path / "stakeholder_rollout_map.md").read_text()
    stakeholder_map_json = json.loads((tmp_path / "stakeholder_rollout_map.json").read_text())
    risk_register = (tmp_path / "risk_exception_register.md").read_text()
    risk_register_json = json.loads((tmp_path / "risk_exception_register.json").read_text())
    audit_plan = (tmp_path / "operational_audit_plan.md").read_text()
    audit_plan_json = json.loads((tmp_path / "operational_audit_plan.json").read_text())
    measurement_report = (tmp_path / "value_measurement_report.md").read_text()
    measurement_report_json = json.loads((tmp_path / "value_measurement_report.json").read_text())
    executive_brief = (tmp_path / "executive_decision_brief.md").read_text()
    executive_brief_json = json.loads((tmp_path / "executive_decision_brief.json").read_text())
    pilot_scorecard = (tmp_path / "pilot_scorecard.md").read_text()
    pilot_scorecard_json = json.loads((tmp_path / "pilot_scorecard.json").read_text())
    pilot_scorecard_csv = (tmp_path / "pilot_scorecard.csv").read_text()
    assert {"kind": "adoption_shortlist", "path": "adoption_shortlist.md"} in artifacts
    assert {"kind": "run_summary", "path": "run_summary.md"} in artifacts
    assert {"kind": "run_summary_json", "path": "run_summary.json"} in artifacts
    assert {"kind": "enterprise_readiness", "path": "enterprise_readiness.md"} in artifacts
    assert {"kind": "enterprise_readiness_json", "path": "enterprise_readiness.json"} in artifacts
    assert {"kind": "value_realization_plan", "path": "value_realization_plan.md"} in artifacts
    assert {"kind": "value_realization_plan_json", "path": "value_realization_plan.json"} in artifacts
    assert {"kind": "stakeholder_rollout_map", "path": "stakeholder_rollout_map.md"} in artifacts
    assert {"kind": "stakeholder_rollout_map_json", "path": "stakeholder_rollout_map.json"} in artifacts
    assert {"kind": "risk_exception_register", "path": "risk_exception_register.md"} in artifacts
    assert {"kind": "risk_exception_register_json", "path": "risk_exception_register.json"} in artifacts
    assert {"kind": "operational_audit_plan", "path": "operational_audit_plan.md"} in artifacts
    assert {"kind": "operational_audit_plan_json", "path": "operational_audit_plan.json"} in artifacts
    assert {"kind": "value_measurement_report", "path": "value_measurement_report.md"} in artifacts
    assert {"kind": "value_measurement_report_json", "path": "value_measurement_report.json"} in artifacts
    assert {"kind": "executive_decision_brief", "path": "executive_decision_brief.md"} in artifacts
    assert {"kind": "executive_decision_brief_json", "path": "executive_decision_brief.json"} in artifacts
    assert {"kind": "pilot_scorecard", "path": "pilot_scorecard.md"} in artifacts
    assert {"kind": "pilot_scorecard_json", "path": "pilot_scorecard.json"} in artifacts
    assert {"kind": "pilot_scorecard_csv", "path": "pilot_scorecard.csv"} in artifacts
    assert {"kind": "adapter_blueprint", "path": "adapter_blueprint.md"} in artifacts
    assert {"kind": "adapter_starter", "path": "adapter_starter/README.md"} in artifacts
    assert "GitHub Discovery Run Summary" in run_summary
    assert "ready_for_adapter" in run_summary
    assert run_summary_json["status"] == "ready_for_adapter"
    assert run_summary_json["next_read"] == "adapter_starter/README.md"
    assert run_summary_json["candidate_count"] == 2
    assert run_summary_json["ready_candidate_count"] == 1
    assert "Enterprise Readiness" in enterprise_readiness
    assert enterprise_readiness_json["decision"] == "prototype_allowed"
    assert enterprise_readiness_json["production_release"] == "blocked_until_controls_complete"
    assert enterprise_readiness_json["required_controls"][0]["control"] == "license_review"
    assert "Value Realization Plan" in value_plan
    assert value_plan_json["status"] == "prototype_value_test"
    assert value_plan_json["primary_workflow"]["candidate"] == "example/strong"
    assert value_plan_json["value_hypotheses"][0]["metric"] == "manual_handoffs_reduced"
    assert "Stakeholder Rollout Map" in stakeholder_map
    assert stakeholder_map_json["status"] == "prototype_governance"
    assert stakeholder_map_json["primary_candidate"] == "example/strong"
    assert stakeholder_map_json["roles"][0]["role"] == "executive_sponsor"
    assert "Risk Exception Register" in risk_register
    assert risk_register_json["status"] == "pilot_controls_open"
    assert risk_register_json["exceptions"][0]["risk"] == "dry_run_evidence_missing"
    assert "Operational Audit Plan" in audit_plan
    assert audit_plan_json["status"] == "pilot_audit_required"
    assert audit_plan_json["audit_scope"][0]["area"] == "approval_integrity"
    assert "Value Measurement Report" in measurement_report
    assert measurement_report_json["status"] == "pilot_measurement_required"
    assert measurement_report_json["metric_cards"][0]["metric"] == "manual_handoffs_reduced"
    assert "Executive Decision Brief" in executive_brief
    assert executive_brief_json["decision"] == "approve_controlled_pilot"
    assert executive_brief_json["investment_case"]["pilot_scope"] == "one narrow operations workflow"
    assert "Pilot Scorecard" in pilot_scorecard
    assert pilot_scorecard_json["status"] == "pilot_scorecard_required"
    assert "metric,owner,baseline_field,pilot_field,target,evidence_file,decision_rule" in pilot_scorecard_csv
    assert "example/strong" in shortlist
    assert "example/agpl" not in shortlist
    assert '"production_gate": "ready_for_adapter"' in shortlist_json
    assert "## First Safe Prototype" in brief
    assert "Prototype with synthetic or non-customer data first." in brief
    assert "## Adoption Decision" in brief
    assert "Decision: `prototype`" in brief
    assert "## 30-Day Implementation Plan" in brief
    assert "Week 1:" in brief
    assert "## Risk Register" in brief
    assert "Adapter Blueprint: example/strong" in adapter_blueprint
    assert "## Adapter Contract" in adapter_blueprint
    assert "dry-run mode" in adapter_blueprint
    assert adapter_blueprint_json["candidate"]["full_name"] == "example/strong"
    assert adapter_blueprint_json["contract"]["mode"] == "adapter_only"
    assert "Adapter Starter: example/strong" in adapter_readme
    assert "def run_adapter" in adapter_code
    assert "dry_run" in adapter_code
    assert "approval_request" in adapter_code
    assert "run_adapter" in adapter_smoke
    assert adapter_sample["workflow_request"]["business_area"] == "operations"
    smoke_result = subprocess.run(
        [sys.executable, str(tmp_path / "adapter_starter" / "smoke_test.py")],
        cwd=tmp_path,
        check=True,
        text=True,
        capture_output=True,
    )
    assert "adapter smoke test passed" in smoke_result.stdout


def test_write_github_candidate_artifacts_writes_manual_review_pack_without_shortlist(tmp_path):
    candidates = [
        {
            "full_name": "example/manual",
            "url": "https://github.com/example/manual",
            "description": "Useful project that needs review",
            "score": 86,
            "automation_fit": "review",
            "license_risk": "medium",
            "stars": 3200,
            "forks": 250,
            "open_issues": 70,
            "updated_at": "2026-06-10T00:00:00Z",
            "language": "Ruby",
            "license": "MPL-2.0",
            "business_area": "support",
            "business_fit_score": 16,
            "matched_business_terms": ["support"],
            "recommended_next_step": "Inspect README, examples, and issue health before adoption",
            "source_query": "support automation stars:>100",
        }
    ]

    artifacts = write_github_candidate_artifacts(tmp_path, candidates, business_area="support")

    review_pack = (tmp_path / "manual_review_pack.md").read_text()
    review_pack_json = json.loads((tmp_path / "manual_review_pack.json").read_text())
    run_summary = (tmp_path / "run_summary.md").read_text()
    run_summary_json = json.loads((tmp_path / "run_summary.json").read_text())
    enterprise_readiness_json = json.loads((tmp_path / "enterprise_readiness.json").read_text())
    value_plan_json = json.loads((tmp_path / "value_realization_plan.json").read_text())
    stakeholder_map_json = json.loads((tmp_path / "stakeholder_rollout_map.json").read_text())
    risk_register_json = json.loads((tmp_path / "risk_exception_register.json").read_text())
    audit_plan_json = json.loads((tmp_path / "operational_audit_plan.json").read_text())
    measurement_report_json = json.loads((tmp_path / "value_measurement_report.json").read_text())
    assert {"kind": "manual_review_pack", "path": "manual_review_pack.md"} in artifacts
    assert {"kind": "manual_review_pack_json", "path": "manual_review_pack.json"} in artifacts
    assert {"kind": "run_summary", "path": "run_summary.md"} in artifacts
    assert not (tmp_path / "adapter_starter").exists()
    assert "manual_review_required" in run_summary
    assert run_summary_json["status"] == "manual_review_required"
    assert run_summary_json["next_read"] == "manual_review_pack.md"
    assert run_summary_json["ready_candidate_count"] == 0
    assert enterprise_readiness_json["decision"] == "review_only"
    assert enterprise_readiness_json["production_release"] == "blocked_until_controls_complete"
    assert value_plan_json["status"] == "manual_value_review"
    assert value_plan_json["primary_workflow"]["candidate"] == "example/manual"
    assert stakeholder_map_json["status"] == "manual_review_governance"
    assert stakeholder_map_json["primary_candidate"] == "example/manual"
    assert risk_register_json["status"] == "exceptions_open"
    assert risk_register_json["exceptions"][0]["risk"] == "prototype_not_allowed"
    assert audit_plan_json["status"] == "manual_review_audit_required"
    assert audit_plan_json["primary_candidate"] == "example/manual"
    assert measurement_report_json["status"] == "manual_measurement_required"
    assert measurement_report_json["primary_candidate"] == "example/manual"
    assert "Manual Review Pack" in review_pack
    assert "example/manual" in review_pack
    assert "License and attribution review" in review_pack
    assert review_pack_json["status"] == "manual_review_required"
    assert review_pack_json["next_actions"][0].startswith("Review license")
