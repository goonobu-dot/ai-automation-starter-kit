from __future__ import annotations

from datetime import datetime, timezone

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
    license_risk = license_risk_for(repo.license)

    popularity = min(35, int(repo.stars / 1500))
    community = min(20, int(repo.forks / 200))
    activity = activity_points(days_since_update)
    operability = 10 if repo.language and repo.language != "unknown" else 0
    topic_signal = min(10, len(repo.topics) * 2)
    license_points = {"low": 15, "medium": 7, "high": 0}[license_risk]
    issue_penalty = 5 if repo.open_issues > max(250, int(repo.stars * 0.03)) else 0
    business_fit_score, matched_business_terms = business_fit(repo, business_area)
    score_breakdown = {
        "popularity": popularity,
        "community": community,
        "activity": activity,
        "operability": operability,
        "topic_signal": topic_signal,
        "license": license_points,
        "business_fit": business_fit_score,
        "issue_penalty": issue_penalty,
    }
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

    gate = production_gate(automation_fit, license_risk)
    effort = adoption_effort(repo.language, repo.stars, repo.open_issues, days_since_update)
    shape = deployment_shape(repo.language)
    decision = adoption_decision(gate, effort)
    use_case = business_use_case(repo, business_area)
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
        "score_breakdown": score_breakdown,
        "rationale": "; ".join(rationale_bits),
        "recommended_next_step": recommended_next_step(automation_fit, license_risk),
        "production_gate": gate,
        "adoption_effort": effort,
        "deployment_shape": shape,
        "decision": decision,
        "business_use_case": use_case,
        "implementation_plan": implementation_plan(gate, effort, business_area),
        "risk_register": risk_register(license_risk, days_since_update, repo.open_issues, repo.stars),
    }


def activity_points(days_since_update: int) -> int:
    if days_since_update <= 30:
        return 20
    if days_since_update <= 180:
        return 15
    if days_since_update <= 365:
        return 8
    return 0


def license_risk_for(license_id: str) -> str:
    normalized = license_id or "NOASSERTION"
    if normalized in PERMISSIVE_LICENSES:
        return "low"
    if normalized in REVIEW_LICENSES:
        return "medium"
    if normalized in HIGH_RISK_LICENSES or normalized.startswith("AGPL"):
        return "high"
    return "medium"


def production_gate(automation_fit: str, license_risk: str) -> str:
    if license_risk == "high":
        return "blocked_until_license_review"
    if automation_fit == "strong" and license_risk == "low":
        return "ready_for_adapter"
    if automation_fit == "avoid":
        return "reference_only"
    return "manual_review_required"


def business_fit(repo: GitHubRepo, business_area: str | None) -> tuple[int, list[str]]:
    if not business_area:
        return 0, []
    terms = BUSINESS_TERMS.get(business_area, [business_area])
    haystack = " ".join([repo.full_name, repo.description, repo.language, " ".join(repo.topics)]).lower()
    matched = sorted({term for term in terms if term.lower() in haystack})
    return min(25, len(matched) * 8), matched


def recommended_next_step(automation_fit: str, license_risk: str) -> str:
    if license_risk == "high":
        return "Run license review before reuse"
    if automation_fit == "strong":
        return "Prototype an adapter and extract reusable workflow ideas"
    if automation_fit == "review":
        return "Inspect README, examples, and issue health before adoption"
    return "Keep as reference only"


def adoption_effort(language: str | None, stars: int, open_issues: int, days_since_update: int) -> str:
    normalized = (language or "unknown").lower()
    if days_since_update > 365 or open_issues > max(300, int(stars * 0.05)):
        return "high"
    if normalized in {"python", "typescript", "javascript"}:
        return "medium"
    if normalized in {"unknown", ""}:
        return "high"
    return "medium"


def deployment_shape(language: str | None) -> str:
    normalized = (language or "unknown").lower()
    if normalized == "python":
        return "python_adapter"
    if normalized in {"typescript", "javascript"}:
        return "node_adapter"
    if normalized in {"go", "rust"}:
        return "service_wrapper"
    return "manual_adapter"


def adoption_decision(production_gate: str, adoption_effort: str) -> str:
    if production_gate == "ready_for_adapter" and adoption_effort in {"low", "medium"}:
        return "prototype"
    if production_gate == "blocked_until_license_review":
        return "legal_review"
    if production_gate == "reference_only":
        return "reference"
    return "manual_review"


def business_use_case(repo: GitHubRepo, business_area: str | None) -> str:
    area = business_area or "operations"
    matched_terms = ", ".join(business_fit(repo, area)[1]) or area
    return f"Use {repo.full_name} as a reference or adapter candidate for {area} workflows around {matched_terms}."


def implementation_plan(production_gate: str, adoption_effort: str, business_area: str | None) -> list[str]:
    area = business_area or "business"
    if production_gate == "blocked_until_license_review":
        return [
            "Week 1: complete license review and document whether code reuse is allowed.",
            "Week 2: inspect architecture only if legal review clears a safe reuse path.",
            "Week 3: prototype with synthetic data and no customer-facing actions.",
            "Week 4: decide whether to adapterize, replace, or keep as reference only.",
        ]
    if production_gate == "ready_for_adapter":
        return [
            f"Week 1: run a 30-day adapter prototype for one {area} workflow with synthetic data.",
            "Week 2: map inputs, outputs, approvals, logs, and rollback points.",
            "Week 3: connect one internal data source behind a dry-run mode.",
            "Week 4: review saved time, failure cases, and operator feedback before production rollout.",
        ]
    if adoption_effort == "high":
        return [
            "Week 1: verify the project is still maintained and has usable examples.",
            "Week 2: extract only workflow ideas into a local proof of concept.",
            "Week 3: compare against simpler alternatives from the candidate ranking.",
            "Week 4: keep as reference unless maintenance and integration risks are resolved.",
        ]
    return [
        "Week 1: inspect README, examples, issues, and license.",
        "Week 2: build a narrow dry-run adapter around one repeated workflow.",
        "Week 3: add approvals, logs, and input validation.",
        "Week 4: decide whether to continue, pause, or replace with a stronger candidate.",
    ]


def risk_register(license_risk: str, days_since_update: int, open_issues: int, stars: int) -> list[dict]:
    risks = [
        {
            "risk": "License or attribution mistake",
            "mitigation": "Confirm license obligations before copying code or shipping an adapter.",
        }
    ]
    if days_since_update > 180:
        risks.append(
            {
                "risk": "Maintenance drift",
                "mitigation": "Inspect recent commits and keep the first prototype isolated behind a replaceable adapter.",
            }
        )
    if open_issues > max(250, int(stars * 0.03)):
        risks.append(
            {
                "risk": "High unresolved issue volume",
                "mitigation": "Review open issues for blockers before relying on the project in a production workflow.",
            }
        )
    if license_risk != "low":
        risks.append(
            {
                "risk": "Reuse blocked by license review",
                "mitigation": "Use the repository as reference only until legal and compliance review clears reuse.",
            }
        )
    risks.append(
        {
            "risk": "Unsafe automation rollout",
            "mitigation": "Start in dry-run mode with synthetic data, approvals, run logs, and rollback notes.",
        }
    )
    return risks


def _parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
