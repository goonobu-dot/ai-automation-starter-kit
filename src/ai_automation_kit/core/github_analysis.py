from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone
from pathlib import Path

from ai_automation_kit.core.github import GitHubRepo


PERMISSIVE_LICENSES = {"MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "0BSD"}
REVIEW_LICENSES = {"GPL-2.0", "GPL-3.0", "LGPL-2.1", "LGPL-3.0", "MPL-2.0"}
HIGH_RISK_LICENSES = {"AGPL-3.0", "NOASSERTION", "unknown"}
BUSINESS_TERMS = {
    "sales": ["sales", "crm", "lead", "outreach", "pipeline", "customer", "revenue"],
    "support": ["support", "customer", "ticket", "helpdesk", "chat", "faq", "agent"],
    "finance": ["finance", "invoice", "billing", "expense", "accounting", "report", "spreadsheet"],
    "operations": ["workflow", "automation", "orchestration", "integration", "etl", "scheduler", "agent"],
    "marketing": ["marketing", "content", "seo", "campaign", "social", "email", "analytics"],
    "hr": ["hr", "hiring", "recruiting", "onboarding", "employee", "talent", "resume"],
}


def score_github_repo(repo: GitHubRepo, business_area: str | None = None, now: str | None = None) -> dict:
    reference_time = _parse_time(now) if now else datetime.now(timezone.utc)
    updated_at = _parse_time(repo.updated_at)
    days_since_update = max(0, (reference_time - updated_at).days) if updated_at else 9999
    license_risk = _license_risk(repo.license)

    popularity = min(35, int(repo.stars / 1500))
    community = min(20, int(repo.forks / 200))
    activity = _activity_points(days_since_update)
    operability = 10 if repo.language and repo.language != "unknown" else 0
    topic_signal = min(10, len(repo.topics) * 2)
    license_points = {"low": 15, "medium": 7, "high": 0}[license_risk]
    issue_penalty = 5 if repo.open_issues > max(250, int(repo.stars * 0.03)) else 0
    business_fit_score, matched_business_terms = _business_fit(repo, business_area)
    score = max(
        0,
        min(
            100,
            popularity
            + community
            + activity
            + operability
            + topic_signal
            + license_points
            + business_fit_score
            - issue_penalty,
        ),
    )

    automation_fit = "strong" if score >= 80 and license_risk == "low" else "review" if score >= 55 else "avoid"
    rationale_bits = [
        f"{repo.stars} stars",
        f"{repo.forks} forks",
        f"updated {days_since_update} days ago" if updated_at else "missing update timestamp",
    ]
    if license_risk == "low":
        rationale_bits.append("permissive license")
    elif license_risk == "high":
        rationale_bits.append("license review required")
    else:
        rationale_bits.append("license needs review")

    return {
        "full_name": repo.full_name,
        "url": repo.html_url,
        "description": repo.description,
        "score": score,
        "automation_fit": automation_fit,
        "license_risk": license_risk,
        "stars": repo.stars,
        "forks": repo.forks,
        "open_issues": repo.open_issues,
        "updated_at": repo.updated_at,
        "days_since_update": days_since_update,
        "language": repo.language,
        "license": repo.license,
        "topics": repo.topics,
        "business_area": business_area or "general",
        "business_fit_score": business_fit_score,
        "matched_business_terms": matched_business_terms,
        "rationale": "; ".join(rationale_bits),
        "recommended_next_step": _recommended_next_step(automation_fit, license_risk),
    }


def write_github_candidate_artifacts(
    output_dir: Path | str,
    candidates: list[dict],
    business_area: str | None = None,
) -> list[dict]:
    output = Path(output_dir)
    ranked = sorted(candidates, key=lambda item: (-int(item["score"]), -int(item["stars"]), item["full_name"]))

    (output / "github_candidates.json").write_text(
        json.dumps({"candidates": ranked}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output / "github_candidates.csv").write_text(_render_candidates_csv(ranked), encoding="utf-8")
    (output / "github_candidates.md").write_text(_render_candidates_markdown(ranked), encoding="utf-8")

    artifacts = [
        {"kind": "github_candidates_json", "path": "github_candidates.json"},
        {"kind": "github_candidates_csv", "path": "github_candidates.csv"},
        {"kind": "github_candidates_markdown", "path": "github_candidates.md"},
    ]
    if business_area:
        summary = build_business_automation_summary(ranked, business_area)
        (output / "business_automation_summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (output / "business_automation_plan.md").write_text(
            _render_business_automation_plan(summary),
            encoding="utf-8",
        )
        artifacts.extend(
            [
                {"kind": "business_automation_summary", "path": "business_automation_summary.json"},
                {"kind": "business_automation_plan", "path": "business_automation_plan.md"},
            ]
        )
    return artifacts


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


def _render_candidates_csv(candidates: list[dict]) -> str:
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
    ]
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(candidates)
    return buffer.getvalue()


def _render_candidates_markdown(candidates: list[dict]) -> str:
    lines = [
        "# GitHub Candidate Ranking",
        "",
        "| Rank | Repository | Score | Fit | License Risk | Stars | Language | Next Step |",
        "|---:|---|---:|---|---|---:|---|---|",
    ]
    for index, candidate in enumerate(candidates, start=1):
        lines.append(
            "| {rank} | [{name}]({url}) | {score} | {fit} | {risk} | {stars} | {language} | {next_step} |".format(
                rank=index,
                name=candidate["full_name"],
                url=candidate["url"],
                score=candidate["score"],
                fit=candidate["automation_fit"],
                risk=candidate["license_risk"],
                stars=candidate["stars"],
                language=candidate["language"],
                next_step=candidate["recommended_next_step"],
            )
        )
    lines.append("")
    return "\n".join(lines)


def _render_business_automation_plan(summary: dict) -> str:
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
                f"business fit {candidate['business_fit_score']}, next step: {candidate['recommended_next_step']}"
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


def _activity_points(days_since_update: int) -> int:
    if days_since_update <= 30:
        return 20
    if days_since_update <= 180:
        return 15
    if days_since_update <= 365:
        return 8
    return 0


def _license_risk(license_id: str) -> str:
    normalized = license_id or "NOASSERTION"
    if normalized in PERMISSIVE_LICENSES:
        return "low"
    if normalized in REVIEW_LICENSES:
        return "medium"
    if normalized in HIGH_RISK_LICENSES or normalized.startswith("AGPL"):
        return "high"
    return "medium"


def _business_fit(repo: GitHubRepo, business_area: str | None) -> tuple[int, list[str]]:
    if not business_area:
        return 0, []
    terms = BUSINESS_TERMS.get(business_area, [business_area])
    haystack = " ".join([repo.full_name, repo.description, repo.language, " ".join(repo.topics)]).lower()
    matched = sorted({term for term in terms if term.lower() in haystack})
    return min(25, len(matched) * 8), matched


def _recommended_next_step(automation_fit: str, license_risk: str) -> str:
    if license_risk == "high":
        return "Run license review before reuse"
    if automation_fit == "strong":
        return "Prototype an adapter and extract reusable workflow ideas"
    if automation_fit == "review":
        return "Inspect README, examples, and issue health before adoption"
    return "Keep as reference only"


def _parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
