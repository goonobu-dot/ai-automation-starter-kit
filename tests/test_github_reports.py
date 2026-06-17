from pathlib import Path

from ai_automation_kit.core.github_reports import (
    render_adoption_shortlist,
    render_business_automation_plan,
    render_candidates_csv,
    render_candidates_markdown,
    safe_candidate_filename,
    write_candidate_briefs,
)


def test_github_reports_render_candidate_outputs(tmp_path):
    candidate = {
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
        "production_gate": "ready_for_adapter",
        "source_queries": ["workflow automation stars:>100"],
        "score_breakdown": {
            "popularity": 12,
            "community": 4,
            "activity": 20,
            "operability": 10,
            "topic_signal": 4,
            "license": 15,
            "business_fit": 24,
            "issue_penalty": 0,
        },
    }

    csv_text = render_candidates_csv([candidate])
    markdown = render_candidates_markdown([candidate])
    shortlist = render_adoption_shortlist([candidate])
    write_candidate_briefs(tmp_path, [candidate])

    assert "full_name,score,automation_fit" in csv_text
    assert "GitHub Candidate Ranking" in markdown
    assert "example/strong" in shortlist
    assert safe_candidate_filename("example/strong") == "example__strong"
    assert "## Risk Register" in (tmp_path / "candidate_briefs" / "example__strong.md").read_text()
    assert "## Score Breakdown" in (tmp_path / "candidate_briefs" / "example__strong.md").read_text()
    assert "- Popularity: `12`" in (tmp_path / "candidate_briefs" / "example__strong.md").read_text()


def test_render_business_automation_plan_lists_recommended_templates():
    plan = render_business_automation_plan(
        {
            "business_area": "operations",
            "executive_recommendation": "Start with example/strong.",
            "candidate_count": 1,
            "strong_candidate_count": 1,
            "license_review_count": 0,
            "recommended_projects": [
                {
                    "full_name": "example/strong",
                    "score": 94,
                    "business_fit_score": 24,
                    "adoption_effort": "medium",
                    "decision": "prototype",
                    "recommended_next_step": "Prototype an adapter",
                }
            ],
            "implementation_path": ["Pick one candidate.", "Run dry-run."],
            "recommended_templates": [{"template": "research-agent", "use_for": "cited decision reports"}],
            "success_metrics": ["Manual handoffs reduced"],
        }
    )

    assert "Business Automation Improvement Plan" in plan
    assert "`research-agent`" in plan
    assert "Manual handoffs reduced" in plan
