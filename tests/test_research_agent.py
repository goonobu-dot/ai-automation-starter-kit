import json

from ai_automation_kit.core.github import GitHubRepo
from ai_automation_kit.templates.research_agent import run_research_agent


def test_research_agent_generates_cited_report_from_local_sources(tmp_path):
    source = tmp_path / "source.html"
    source.write_text(
        "<html><head><title>Source A</title></head><body><p>AI automation saves time.</p></body></html>"
    )
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"topic": "AI automation", "sources": [{"uri": source.as_uri()}]}))
    output = tmp_path / "out"

    run = run_research_agent(config_path=config, output_dir=output)

    report = output / "report.md"
    assert run.status == "succeeded"
    assert report.exists()
    assert "Source A" in report.read_text()
    assert source.as_uri() in report.read_text()
    assert "PYTHONPATH=src python3 -m ai_automation_kit.cli research-agent" in report.read_text()
    assert (output / "runs" / f"{run.run_id}.json").exists()


def test_research_agent_accepts_github_repositories(tmp_path, monkeypatch):
    def fake_fetch(repo_name, token=None):
        assert repo_name == "octocat/Hello-World"
        return GitHubRepo(
            full_name="octocat/Hello-World",
            html_url="https://github.com/octocat/Hello-World",
            description="Example repo",
            stars=42,
            forks=7,
            open_issues=3,
            license="MIT",
            topics=["example"],
            language="Python",
            updated_at="2026-06-17T00:00:00Z",
            rate_limit_remaining="59",
        )

    monkeypatch.setattr("ai_automation_kit.templates.research_agent.fetch_github_repo", fake_fetch)
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"topic": "GitHub repo research", "github_repositories": ["octocat/Hello-World"]}))
    output = tmp_path / "out"

    run = run_research_agent(config_path=config, output_dir=output)

    report = (output / "report.md").read_text()
    assert run.status == "succeeded"
    assert "octocat/Hello-World" in report
    assert "42 stars" in report
    assert (output / "github_repositories.json").exists()


def test_research_agent_logs_readme_failure_without_dropping_repo(tmp_path, monkeypatch):
    def fake_fetch(repo_name, token=None):
        return GitHubRepo(
            full_name="octocat/Hello-World",
            html_url="https://github.com/octocat/Hello-World",
            description="Example repo",
            stars=42,
            forks=7,
            open_issues=3,
            license="MIT",
            topics=["example"],
            language="Python",
            updated_at="2026-06-17T00:00:00Z",
            rate_limit_remaining="59",
        )

    def fake_readme(repo_name, token=None):
        raise RuntimeError("README missing")

    monkeypatch.setattr("ai_automation_kit.templates.research_agent.fetch_github_repo", fake_fetch)
    monkeypatch.setattr("ai_automation_kit.templates.research_agent.fetch_github_readme", fake_readme)
    config = tmp_path / "config.json"
    config.write_text(
        json.dumps(
            {
                "topic": "GitHub repo research",
                "github_repositories": ["octocat/Hello-World"],
                "include_readme": True,
            }
        )
    )
    output = tmp_path / "out"

    run = run_research_agent(config_path=config, output_dir=output)

    assert run.status == "succeeded"
    assert "octocat/Hello-World" in (output / "report.md").read_text()
    assert run.failed_fetches[0].uri == "https://api.github.com/repos/octocat/Hello-World/readme"


def test_research_agent_accepts_github_searches(tmp_path, monkeypatch):
    def fake_search(query, sort="stars", order="desc", per_page=10, token=None):
        assert query == "topic:ai-agents stars:>1000"
        assert sort == "stars"
        assert order == "desc"
        assert per_page == 2
        return {
            "query": query,
            "sort": sort,
            "order": order,
            "per_page": per_page,
            "total_count": 2,
            "incomplete_results": False,
            "rate_limit_remaining": "28",
            "repositories": [
                GitHubRepo(
                    full_name="modelcontextprotocol/servers",
                    html_url="https://github.com/modelcontextprotocol/servers",
                    description="MCP servers",
                    stars=50000,
                    forks=4000,
                    open_issues=120,
                    license="MIT",
                    topics=["mcp", "automation"],
                    language="Python",
                    updated_at="2026-06-17T00:00:00Z",
                    rate_limit_remaining="28",
                )
            ],
        }

    monkeypatch.setattr("ai_automation_kit.templates.research_agent.search_github_repositories", fake_search)
    config = tmp_path / "config.json"
    config.write_text(
        json.dumps(
            {
                "topic": "GitHub trend research",
                "business_context": {"business_area": "sales"},
                "github_searches": [
                    {
                        "query": "topic:ai-agents stars:>1000",
                        "sort": "stars",
                        "order": "desc",
                        "per_page": 2,
                    }
                ],
            }
        )
    )
    output = tmp_path / "out"

    run = run_research_agent(config_path=config, output_dir=output)

    report = (output / "report.md").read_text()
    search_payload = json.loads((output / "github_searches.json").read_text())
    candidates = json.loads((output / "github_candidates.json").read_text())
    candidate_csv = (output / "github_candidates.csv").read_text()
    candidate_markdown = (output / "github_candidates.md").read_text()
    business_summary = json.loads((output / "business_automation_summary.json").read_text())
    business_plan = (output / "business_automation_plan.md").read_text()
    assert run.status == "succeeded"
    assert "modelcontextprotocol/servers" in report
    assert "50000 stars" in report
    assert search_payload["searches"][0]["query"] == "topic:ai-agents stars:>1000"
    assert search_payload["searches"][0]["repositories"][0]["full_name"] == "modelcontextprotocol/servers"
    assert candidates["candidates"][0]["full_name"] == "modelcontextprotocol/servers"
    assert candidates["candidates"][0]["automation_fit"] == "strong"
    assert candidates["candidates"][0]["business_area"] == "sales"
    assert "full_name,score,automation_fit,license_risk,stars,forks,open_issues,updated_at,language,license,url" in candidate_csv
    assert "GitHub Candidate Ranking" in candidate_markdown
    assert business_summary["business_area"] == "sales"
    assert "Business Automation Improvement Plan" in business_plan
