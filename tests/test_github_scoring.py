from ai_automation_kit.core.github import GitHubRepo
from ai_automation_kit.core.github_scoring import production_gate, score_github_repo


def test_scoring_module_marks_adapter_ready_business_fit():
    repo = GitHubRepo(
        full_name="example/ops-agent",
        html_url="https://github.com/example/ops-agent",
        description="Workflow automation orchestration agent for operations teams",
        stars=60000,
        forks=5000,
        open_issues=80,
        license="MIT",
        topics=["workflow", "automation", "agent"],
        language="Python",
        updated_at="2026-06-15T00:00:00Z",
        rate_limit_remaining="42",
    )

    scored = score_github_repo(repo, business_area="operations", now="2026-06-17T00:00:00Z")

    assert scored["score"] >= 90
    assert scored["production_gate"] == "ready_for_adapter"
    assert scored["decision"] == "prototype"
    assert scored["deployment_shape"] == "python_adapter"
    assert {"workflow", "automation", "agent"}.issubset(set(scored["matched_business_terms"]))
    assert scored["score_breakdown"]["popularity"] == 35
    assert scored["score_breakdown"]["community"] == 20
    assert scored["score_breakdown"]["license"] == 15
    assert scored["score_breakdown"]["issue_penalty"] == 0
    assert scored["score_breakdown"]["business_fit"] == scored["business_fit_score"]


def test_production_gate_blocks_high_risk_license():
    assert production_gate("strong", "high") == "blocked_until_license_review"
    assert production_gate("avoid", "low") == "reference_only"
