from __future__ import annotations

import csv
import io
from datetime import datetime, timezone
from pathlib import Path

from ai_automation_kit.core.github_scoring import (
    adoption_decision as decide_adoption,
    adoption_effort as estimate_adoption_effort,
    deployment_shape as infer_deployment_shape,
    implementation_plan as fallback_implementation_plan,
    risk_register as build_risk_register,
)


def render_candidates_csv(candidates: list[dict]) -> str:
    fields = [
        "full_name",
        "score",
        "automation_fit",
        "license_risk",
        "stars",
        "forks",
        "open_issues",
        "updated_at",
        "language",
        "license",
        "url",
        "production_gate",
    ]
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(candidates)
    return buffer.getvalue()


def render_candidates_markdown(candidates: list[dict]) -> str:
    lines = [
        "# GitHub Candidate Ranking",
        "",
        "| Rank | Repository | Score | Fit | Gate | License Risk | Stars | Language | Next Step |",
        "|---:|---|---:|---|---|---|---:|---|---|",
    ]
    for index, candidate in enumerate(candidates, start=1):
        lines.append(
            "| {rank} | [{name}]({url}) | {score} | {fit} | {gate} | {risk} | {stars} | {language} | {next_step} |".format(
                rank=index,
                name=candidate["full_name"],
                url=candidate["url"],
                score=candidate["score"],
                fit=candidate["automation_fit"],
                gate=candidate.get("production_gate", "manual_review_required"),
                risk=candidate["license_risk"],
                stars=candidate["stars"],
                language=candidate["language"],
                next_step=candidate["recommended_next_step"],
            )
        )
    lines.append("")
    return "\n".join(lines)


def render_adoption_shortlist(candidates: list[dict]) -> str:
    lines = [
        "# Adoption Shortlist",
        "",
        "Only candidates with a low license risk and strong automation fit are listed here.",
        "",
    ]
    if not candidates:
        lines.append("- No candidate is ready for adapter prototyping yet.")
        lines.append("")
        return "\n".join(lines)
    for candidate in candidates:
        adoption_effort = candidate.get("adoption_effort") or estimate_adoption_effort(
            candidate.get("language", "unknown"),
            int(candidate.get("stars", 0)),
            int(candidate.get("open_issues", 0)),
            _candidate_days_since_update(candidate),
        )
        decision = candidate.get("decision") or decide_adoption(
            candidate.get("production_gate", "ready_for_adapter"),
            adoption_effort,
        )
        lines.extend(
            [
                f"## {candidate['full_name']}",
                "",
                f"- Score: `{candidate['score']}`",
                f"- Gate: `{candidate.get('production_gate', 'ready_for_adapter')}`",
                f"- Business fit: `{candidate.get('business_fit_score', 0)}`",
                f"- Adoption effort: `{adoption_effort}`",
                f"- Decision: `{decision}`",
                f"- License: `{candidate['license']}`",
                f"- Next step: {candidate['recommended_next_step']}",
                "",
            ]
        )
    return "\n".join(lines)


def write_candidate_briefs(output: Path, candidates: list[dict]) -> None:
    brief_dir = output / "candidate_briefs"
    brief_dir.mkdir(parents=True, exist_ok=True)
    for candidate in candidates:
        (brief_dir / f"{safe_candidate_filename(candidate['full_name'])}.md").write_text(
            render_candidate_brief(candidate),
            encoding="utf-8",
        )


def render_candidate_brief(candidate: dict) -> str:
    source_lines = candidate.get("source_queries") or ([candidate["source_query"]] if candidate.get("source_query") else [])
    production_gate = candidate.get("production_gate", "manual_review_required")
    license_risk = candidate.get("license_risk", "medium")
    days_since_update = _candidate_days_since_update(candidate)
    adoption_effort = candidate.get("adoption_effort") or estimate_adoption_effort(
        candidate.get("language", "unknown"),
        int(candidate.get("stars", 0)),
        int(candidate.get("open_issues", 0)),
        days_since_update,
    )
    decision = candidate.get("decision") or decide_adoption(production_gate, adoption_effort)
    implementation_plan = candidate.get("implementation_plan") or fallback_implementation_plan(
        production_gate,
        adoption_effort,
        candidate.get("business_area"),
    )
    risk_register = candidate.get("risk_register") or build_risk_register(
        license_risk,
        days_since_update,
        int(candidate.get("open_issues", 0)),
        int(candidate.get("stars", 0)),
    )
    lines = [
        f"# Candidate Brief: {candidate['full_name']}",
        "",
        f"- URL: {candidate['url']}",
        f"- Score: `{candidate['score']}`",
        f"- Fit: `{candidate['automation_fit']}`",
        f"- Production gate: `{production_gate}`",
        f"- License risk: `{license_risk}`",
        f"- Adoption effort: `{adoption_effort}`",
        f"- Deployment shape: `{candidate.get('deployment_shape') or infer_deployment_shape(candidate.get('language', 'unknown'))}`",
        f"- Language: `{candidate.get('language', 'unknown')}`",
        f"- Stars: `{candidate['stars']}`",
        "",
        "## Why It Matched",
        "",
        candidate.get("description") or "No description was available.",
        "",
        "## Adoption Decision",
        "",
        f"- Decision: `{decision}`",
        f"- Business use case: {candidate.get('business_use_case') or _fallback_business_use_case(candidate)}",
        f"- Recommended next step: {candidate.get('recommended_next_step', 'Inspect manually before reuse')}",
        "",
        "## Source Queries",
        "",
    ]
    if source_lines:
        lines.extend(f"- `{query}`" for query in source_lines)
    else:
        lines.append("- Direct repository input")
    lines.extend(
        [
            "",
            "## Score Breakdown",
            "",
        ]
    )
    score_breakdown = candidate.get("score_breakdown") or {}
    if score_breakdown:
        for key in [
            "popularity",
            "community",
            "activity",
            "operability",
            "topic_signal",
            "license",
            "business_fit",
            "issue_penalty",
        ]:
            label = key.replace("_", " ").title()
            lines.append(f"- {label}: `{score_breakdown.get(key, 0)}`")
    else:
        lines.append("- Score breakdown was not available for this candidate.")
    lines.extend(
        [
            "",
            "## First Safe Prototype",
            "",
            "1. Inspect README, examples, license, and recent issues.",
            "2. Prototype with synthetic or non-customer data first.",
            "3. Build a thin adapter around the useful workflow instead of copying internals.",
            "4. Record run evidence and approval decisions before production use.",
            "",
            "## 30-Day Implementation Plan",
            "",
        ]
    )
    lines.extend(f"{index}. {step}" for index, step in enumerate(implementation_plan, start=1))
    lines.extend(["", "## Risk Register", ""])
    for risk in risk_register:
        lines.append(f"- {risk['risk']}: {risk['mitigation']}")
    lines.append("")
    return "\n".join(lines)


def render_business_automation_plan(summary: dict) -> str:
    lines = [
        f"# Business Automation Improvement Plan: {summary['business_area']}",
        "",
        f"Executive recommendation: {summary['executive_recommendation']}",
        "",
        "## Snapshot",
        "",
        f"- Candidates reviewed: {summary['candidate_count']}",
        f"- Strong candidates: {summary['strong_candidate_count']}",
        f"- License review needed: {summary['license_review_count']}",
        "",
        "## Recommended Projects",
        "",
    ]
    if summary["recommended_projects"]:
        for candidate in summary["recommended_projects"]:
            lines.append(
                f"- {candidate['full_name']}: score {candidate['score']}, "
                f"business fit {candidate['business_fit_score']}, "
                f"effort {candidate.get('adoption_effort', 'review')}, "
                f"decision {candidate.get('decision', 'prototype')}, "
                f"next step: {candidate['recommended_next_step']}"
            )
    else:
        lines.append("- No low-risk strong candidate found. Broaden the query or review medium-risk candidates manually.")

    lines.extend(["", "## Implementation Path", ""])
    for index, step in enumerate(summary["implementation_path"], start=1):
        lines.append(f"{index}. {step}")
    lines.extend(["", "## Recommended Starter Kit Templates", ""])
    for template in summary["recommended_templates"]:
        lines.append(f"- `{template['template']}`: {template['use_for']}")
    lines.extend(["", "## Success Metrics", ""])
    for metric in summary["success_metrics"]:
        lines.append(f"- {metric}")
    lines.append("")
    return "\n".join(lines)


def render_manual_review_pack(pack: dict) -> str:
    lines = [
        f"# Manual Review Pack: {pack['business_area']}",
        "",
        "No candidate met the ready-for-adapter gate. Use this pack to decide whether to review, replace, or keep candidates as references.",
        "",
        "## Next Actions",
        "",
    ]
    lines.extend(f"{index}. {action}" for index, action in enumerate(pack["next_actions"], start=1))
    lines.extend(["", "## Review Candidates", ""])
    for candidate in pack["candidates"]:
        lines.extend(
            [
                f"### {candidate['full_name']}",
                "",
                f"- URL: {candidate['url']}",
                f"- Score: `{candidate['score']}`",
                f"- Gate: `{candidate.get('production_gate', 'manual_review_required')}`",
                f"- License risk: `{candidate.get('license_risk', 'medium')}`",
                f"- License: `{candidate.get('license', 'unknown')}`",
                f"- Language: `{candidate.get('language', 'unknown')}`",
                f"- Recommended next step: {candidate.get('recommended_next_step', 'Inspect manually before reuse')}",
                "",
                "#### Required Checks",
                "",
                "- [ ] License and attribution review",
                "- [ ] README and examples review",
                "- [ ] Recent issue and maintenance review",
                "- [ ] Dry-run prototype plan with synthetic data only",
                "",
            ]
        )
    lines.extend(
        [
            "## Stop Conditions",
            "",
            "- Do not copy code or examples until license review is complete.",
            "- Do not run customer-facing automation without owner approval and rollback notes.",
            "- Replace the candidate if maintenance or issue health blocks a safe prototype.",
            "",
        ]
    )
    return "\n".join(lines)


def safe_candidate_filename(full_name: str) -> str:
    return full_name.replace("/", "__").replace(" ", "_")


def _fallback_business_use_case(candidate: dict) -> str:
    area = candidate.get("business_area") or "operations"
    terms = ", ".join(candidate.get("matched_business_terms", [])) or area
    return f"Use this project as an adapter candidate for {area} workflows around {terms}."


def _candidate_days_since_update(candidate: dict) -> int:
    if "days_since_update" in candidate:
        return int(candidate["days_since_update"])
    updated_at = _parse_time(candidate.get("updated_at"))
    if not updated_at:
        return 9999
    return max(0, (datetime.now(timezone.utc) - updated_at).days)


def _parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
