from __future__ import annotations

import json
from pathlib import Path

from ai_automation_kit.core.adapter_artifacts import write_adapter_artifacts
from ai_automation_kit.core.github_reports import (
    render_adoption_shortlist,
    render_business_automation_plan,
    render_candidates_csv,
    render_candidates_markdown,
    render_manual_review_pack,
    safe_candidate_filename,
    write_candidate_briefs,
)
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
    render_pilot_scorecard,
    render_pilot_scorecard_csv,
    render_risk_exception_register,
    render_run_summary,
    render_stakeholder_rollout_map,
    render_value_measurement_report,
    render_value_realization_plan,
)
from ai_automation_kit.core.github_scoring import production_gate, score_github_repo


def write_github_candidate_artifacts(
    output_dir: Path | str,
    candidates: list[dict],
    business_area: str | None = None,
) -> list[dict]:
    output = Path(output_dir)
    ranked = sorted(deduplicate_candidates(candidates), key=lambda item: (-int(item["score"]), -int(item["stars"]), item["full_name"]))
    shortlist = [candidate for candidate in ranked if candidate.get("production_gate") == "ready_for_adapter"]

    (output / "github_candidates.json").write_text(
        json.dumps({"candidates": ranked}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output / "github_candidates.csv").write_text(render_candidates_csv(ranked), encoding="utf-8")
    (output / "github_candidates.md").write_text(render_candidates_markdown(ranked), encoding="utf-8")
    (output / "adoption_shortlist.json").write_text(
        json.dumps({"candidates": shortlist}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output / "adoption_shortlist.md").write_text(render_adoption_shortlist(shortlist), encoding="utf-8")
    adapter_artifacts = write_adapter_artifacts(output, shortlist[0], business_area) if shortlist else []
    write_candidate_briefs(output, ranked[:5])
    manual_review_artifacts = []
    if ranked and not shortlist:
        manual_review_pack = build_manual_review_pack(ranked, business_area)
        (output / "manual_review_pack.json").write_text(
            json.dumps(manual_review_pack, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (output / "manual_review_pack.md").write_text(render_manual_review_pack(manual_review_pack), encoding="utf-8")
        manual_review_artifacts.extend(
            [
                {"kind": "manual_review_pack_json", "path": "manual_review_pack.json"},
                {"kind": "manual_review_pack", "path": "manual_review_pack.md"},
            ]
        )
    run_summary = build_run_summary(ranked, shortlist, business_area)
    (output / "run_summary.json").write_text(
        json.dumps(run_summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output / "run_summary.md").write_text(render_run_summary(run_summary), encoding="utf-8")
    enterprise_readiness = build_enterprise_readiness(run_summary, ranked, shortlist)
    (output / "enterprise_readiness.json").write_text(
        json.dumps(enterprise_readiness, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output / "enterprise_readiness.md").write_text(render_enterprise_readiness(enterprise_readiness), encoding="utf-8")
    value_plan = build_value_realization_plan(run_summary, ranked, shortlist)
    (output / "value_realization_plan.json").write_text(
        json.dumps(value_plan, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output / "value_realization_plan.md").write_text(render_value_realization_plan(value_plan), encoding="utf-8")
    stakeholder_map = build_stakeholder_rollout_map(run_summary, ranked, shortlist)
    (output / "stakeholder_rollout_map.json").write_text(
        json.dumps(stakeholder_map, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output / "stakeholder_rollout_map.md").write_text(
        render_stakeholder_rollout_map(stakeholder_map),
        encoding="utf-8",
    )
    risk_register = build_risk_exception_register(run_summary, ranked, shortlist)
    (output / "risk_exception_register.json").write_text(
        json.dumps(risk_register, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output / "risk_exception_register.md").write_text(
        render_risk_exception_register(risk_register),
        encoding="utf-8",
    )
    audit_plan = build_operational_audit_plan(run_summary, ranked, shortlist)
    (output / "operational_audit_plan.json").write_text(
        json.dumps(audit_plan, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output / "operational_audit_plan.md").write_text(
        render_operational_audit_plan(audit_plan),
        encoding="utf-8",
    )
    measurement_report = build_value_measurement_report(run_summary, ranked, shortlist)
    (output / "value_measurement_report.json").write_text(
        json.dumps(measurement_report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output / "value_measurement_report.md").write_text(
        render_value_measurement_report(measurement_report),
        encoding="utf-8",
    )
    executive_brief = build_executive_decision_brief(run_summary, ranked, shortlist)
    (output / "executive_decision_brief.json").write_text(
        json.dumps(executive_brief, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output / "executive_decision_brief.md").write_text(
        render_executive_decision_brief(executive_brief),
        encoding="utf-8",
    )
    pilot_scorecard = build_pilot_scorecard(run_summary, ranked, shortlist)
    (output / "pilot_scorecard.json").write_text(
        json.dumps(pilot_scorecard, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output / "pilot_scorecard.md").write_text(render_pilot_scorecard(pilot_scorecard), encoding="utf-8")
    (output / "pilot_scorecard.csv").write_text(render_pilot_scorecard_csv(pilot_scorecard), encoding="utf-8")

    artifacts = [
        {"kind": "run_summary_json", "path": "run_summary.json"},
        {"kind": "run_summary", "path": "run_summary.md"},
        {"kind": "executive_decision_brief_json", "path": "executive_decision_brief.json"},
        {"kind": "executive_decision_brief", "path": "executive_decision_brief.md"},
        {"kind": "pilot_scorecard_json", "path": "pilot_scorecard.json"},
        {"kind": "pilot_scorecard", "path": "pilot_scorecard.md"},
        {"kind": "pilot_scorecard_csv", "path": "pilot_scorecard.csv"},
        {"kind": "enterprise_readiness_json", "path": "enterprise_readiness.json"},
        {"kind": "enterprise_readiness", "path": "enterprise_readiness.md"},
        {"kind": "value_realization_plan_json", "path": "value_realization_plan.json"},
        {"kind": "value_realization_plan", "path": "value_realization_plan.md"},
        {"kind": "stakeholder_rollout_map_json", "path": "stakeholder_rollout_map.json"},
        {"kind": "stakeholder_rollout_map", "path": "stakeholder_rollout_map.md"},
        {"kind": "risk_exception_register_json", "path": "risk_exception_register.json"},
        {"kind": "risk_exception_register", "path": "risk_exception_register.md"},
        {"kind": "operational_audit_plan_json", "path": "operational_audit_plan.json"},
        {"kind": "operational_audit_plan", "path": "operational_audit_plan.md"},
        {"kind": "value_measurement_report_json", "path": "value_measurement_report.json"},
        {"kind": "value_measurement_report", "path": "value_measurement_report.md"},
        {"kind": "github_candidates_json", "path": "github_candidates.json"},
        {"kind": "github_candidates_csv", "path": "github_candidates.csv"},
        {"kind": "github_candidates_markdown", "path": "github_candidates.md"},
        {"kind": "adoption_shortlist_json", "path": "adoption_shortlist.json"},
        {"kind": "adoption_shortlist", "path": "adoption_shortlist.md"},
    ]
    artifacts.extend(adapter_artifacts)
    artifacts.extend(manual_review_artifacts)
    artifacts.extend(
        {"kind": "candidate_brief", "path": f"candidate_briefs/{safe_candidate_filename(candidate['full_name'])}.md"}
        for candidate in ranked[:5]
    )
    if business_area:
        summary = build_business_automation_summary(ranked, business_area)
        (output / "business_automation_summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (output / "business_automation_plan.md").write_text(
            render_business_automation_plan(summary),
            encoding="utf-8",
        )
        artifacts.extend(
            [
                {"kind": "business_automation_summary", "path": "business_automation_summary.json"},
                {"kind": "business_automation_plan", "path": "business_automation_plan.md"},
            ]
        )
    return artifacts


def deduplicate_candidates(candidates: list[dict]) -> list[dict]:
    by_name: dict[str, dict] = {}
    source_queries: dict[str, set[str]] = {}
    for candidate in candidates:
        full_name = candidate["full_name"]
        query = candidate.get("source_query")
        source_queries.setdefault(full_name, set())
        if query:
            source_queries[full_name].add(query)
        current = by_name.get(full_name)
        if current is None or int(candidate.get("score", 0)) > int(current.get("score", 0)):
            by_name[full_name] = dict(candidate)
    deduped = []
    for full_name, candidate in by_name.items():
        candidate["source_queries"] = sorted(source_queries.get(full_name, set()))
        candidate.setdefault(
            "production_gate",
            production_gate(candidate.get("automation_fit", "review"), candidate.get("license_risk", "medium")),
        )
        deduped.append(candidate)
    return deduped


def build_business_automation_summary(candidates: list[dict], business_area: str) -> dict:
    recommended = [
        candidate
        for candidate in candidates
        if candidate.get("automation_fit") == "strong" and candidate.get("license_risk") == "low"
    ][:5]
    review = [candidate for candidate in candidates if candidate.get("license_risk") != "low"]
    if recommended:
        executive_recommendation = (
            f"Start with {recommended[0]['full_name']} as the first adapter prototype, "
            "then review the next two candidates for reusable workflow patterns."
        )
        implementation_path = [
            "Pick one strong candidate and inspect README, examples, and license.",
            "Build a thin adapter around the useful workflow instead of copying project internals.",
            "Run one business process through the adapter with dry-run outputs.",
            "Add approvals, logs, and rollback notes before production use.",
            "Measure saved time, reduced manual handoffs, and avoided response delays.",
        ]
    else:
        executive_recommendation = (
            "No low-risk strong candidate was found. Broaden the query, inspect review candidates manually, "
            "and avoid production reuse until license and maintenance risks are resolved."
        )
        implementation_path = [
            "Broaden the GitHub query or lower the star threshold to find safer candidates.",
            "Inspect review candidates manually for license, maintenance, examples, and security posture.",
            "Use high-risk projects as idea references only until legal and technical review clears reuse.",
            "Prototype with synthetic data and dry-run outputs before touching real business processes.",
            "Measure candidate usefulness by saved time, fewer handoffs, and clearer audit trails.",
        ]
    return {
        "business_area": business_area,
        "candidate_count": len(candidates),
        "strong_candidate_count": len([c for c in candidates if c.get("automation_fit") == "strong"]),
        "license_review_count": len(review),
        "recommended_projects": recommended,
        "review_projects": review[:5],
        "recommended_templates": _recommended_templates(business_area),
        "success_metrics": _success_metrics(),
        "executive_recommendation": executive_recommendation,
        "implementation_path": implementation_path,
    }


def _recommended_templates(business_area: str) -> list[dict]:
    return [
        {"template": "research-agent", "use_for": "turn candidate repositories and source material into cited decision reports"},
        {"template": "delivery-pipeline", "use_for": "package the selected automation as an installable, auditable handoff"},
        {"template": "internal-ai-workflow", "use_for": f"draft approved internal or customer responses for {business_area} workflows"},
        {"template": "docs-rag", "use_for": "answer operational questions from policy, runbook, or product documents with citations"},
        {"template": "excel-to-internal-app", "use_for": "convert spreadsheet-driven operations into a typed internal app schema"},
    ]


def _success_metrics() -> list[str]:
    return [
        "Manual handoffs reduced",
        "Time saved per repeated workflow",
        "Decision evidence captured in run records",
        "Approvals completed before external actions",
        "Production rollout blocked until license and secret checks pass",
    ]
