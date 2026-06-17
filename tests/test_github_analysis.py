from ai_automation_kit.core.github import GitHubRepo
from ai_automation_kit.core.github_analysis import build_business_automation_summary, score_github_repo


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
