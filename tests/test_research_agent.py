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
    run_summary = (output / "run_summary.md").read_text()
    run_summary_json = json.loads((output / "run_summary.json").read_text())
    shortlist = (output / "adoption_shortlist.md").read_text()
    candidate_brief = (output / "candidate_briefs" / "modelcontextprotocol__servers.md").read_text()
    adapter_blueprint = (output / "adapter_blueprint.md").read_text()
    adapter_starter = (output / "adapter_starter" / "README.md").read_text()
    artifact_index = (output / "artifact_index.md").read_text()
    artifact_index_json = json.loads((output / "artifact_index.json").read_text())
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
    assert "ready_for_adapter" in shortlist
    assert "GitHub Discovery Run Summary" in run_summary
    assert run_summary_json["status"] == "ready_for_adapter"
    assert run_summary_json["next_read"] == "adapter_starter/README.md"
    assert "First Safe Prototype" in candidate_brief
    assert "Adapter Blueprint" in adapter_blueprint
    assert "adapter_only" in adapter_blueprint
    assert "Adapter Starter" in adapter_starter
    assert (output / "adapter_starter" / "smoke_test.py").exists()
    assert "Artifact Index: research-agent" in artifact_index
    assert "adapter_starter/README.md" in artifact_index
    assert "Ranked GitHub candidates with fit, gate, license, and next step." in artifact_index
    assert "Local smoke test for the generated adapter starter." in artifact_index
    assert artifact_index_json["template_name"] == "research-agent"
    assert "run_summary.md" in artifact_index_json["first_read"]
    assert artifact_index_json["first_read"][1] == "executive_decision_brief.md"
    assert "adapter_starter/README.md" in artifact_index_json["first_read"]
    assert any(
        (artifact.path if hasattr(artifact, "path") else artifact["path"]) == "adapter_blueprint.md"
        for artifact in run.artifacts
    )
    assert any(
        (artifact.path if hasattr(artifact, "path") else artifact["path"]) == "adapter_starter/README.md"
        for artifact in run.artifacts
    )
    assert business_summary["business_area"] == "sales"
    assert "Business Automation Improvement Plan" in business_plan


def test_research_agent_writes_query_recovery_when_github_search_has_no_candidates(tmp_path, monkeypatch):
    def fake_search(query, sort="stars", order="desc", per_page=10, token=None):
        return {
            "query": query,
            "sort": sort,
            "order": order,
            "per_page": per_page,
            "total_count": 0,
            "incomplete_results": False,
            "rate_limit_remaining": "28",
            "repositories": [],
        }

    monkeypatch.setattr("ai_automation_kit.templates.research_agent.search_github_repositories", fake_search)
    config = tmp_path / "config.json"
    config.write_text(
        json.dumps(
            {
                "topic": "GitHub trend research",
                "business_context": {"business_area": "support"},
                "github_searches": [
                    {
                        "query": "too-specific-impossible-query stars:>999999",
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

    recovery_md = (output / "query_recovery.md").read_text()
    recovery_json = json.loads((output / "query_recovery.json").read_text())
    run_summary = (output / "run_summary.md").read_text()
    run_summary_json = json.loads((output / "run_summary.json").read_text())
    enterprise_readiness_json = json.loads((output / "enterprise_readiness.json").read_text())
    value_plan_json = json.loads((output / "value_realization_plan.json").read_text())
    stakeholder_map_json = json.loads((output / "stakeholder_rollout_map.json").read_text())
    risk_register_json = json.loads((output / "risk_exception_register.json").read_text())
    audit_plan_json = json.loads((output / "operational_audit_plan.json").read_text())
    measurement_report_json = json.loads((output / "value_measurement_report.json").read_text())
    pilot_scorecard_json = json.loads((output / "pilot_scorecard.json").read_text())
    pilot_scorecard_csv = (output / "pilot_scorecard.csv").read_text()
    artifact_index_json = json.loads((output / "artifact_index.json").read_text())
    assert run.status == "succeeded"
    assert "No GitHub candidates were found" in recovery_md
    assert "support automation stars:>50" in recovery_md
    assert recovery_json["business_area"] == "support"
    assert recovery_json["suggested_queries"][0] == "support automation stars:>50"
    assert "query_recovery_required" in run_summary
    assert run_summary_json["status"] == "query_recovery_required"
    assert run_summary_json["candidate_count"] == 0
    assert run_summary_json["next_read"] == "query_recovery.md"
    assert enterprise_readiness_json["decision"] == "query_recovery_required"
    assert enterprise_readiness_json["production_release"] == "blocked_until_controls_complete"
    assert value_plan_json["status"] == "discovery_recovery"
    assert value_plan_json["value_hypotheses"][0]["metric"] == "candidate_quality"
    assert stakeholder_map_json["status"] == "discovery_governance"
    assert stakeholder_map_json["approval_matrix"][0]["decision"] == "search_recovery_start"
    assert risk_register_json["status"] == "exceptions_open"
    assert risk_register_json["exceptions"][0]["risk"] == "candidate_discovery_empty"
    assert audit_plan_json["status"] == "discovery_audit_required"
    assert audit_plan_json["audit_scope"][0]["area"] == "query_recovery_trace"
    assert measurement_report_json["status"] == "discovery_measurement_required"
    assert measurement_report_json["metric_cards"][0]["metric"] == "candidate_quality"
    assert pilot_scorecard_json["status"] == "discovery_scorecard_required"
    assert pilot_scorecard_json["rows"][0]["metric"] == "candidate_quality"
    assert "metric,owner,baseline_field,pilot_field,target,evidence_file,decision_rule" in pilot_scorecard_csv
    assert artifact_index_json["first_read"][0] == "run_summary.md"
    assert artifact_index_json["first_read"][1] == "executive_decision_brief.md"
    assert "value_realization_plan.md" in artifact_index_json["first_read"]
    assert "stakeholder_rollout_map.md" in artifact_index_json["first_read"]
    assert "risk_exception_register.md" in artifact_index_json["first_read"]
    assert "operational_audit_plan.md" in artifact_index_json["first_read"]
    assert "value_measurement_report.md" in artifact_index_json["first_read"]
    assert "enterprise_readiness.md" in artifact_index_json["first_read"]
    assert "query_recovery.md" in artifact_index_json["first_read"]
    assert any(item["path"] == "value_realization_plan.md" for item in artifact_index_json["artifacts"])
    assert any(item["path"] == "stakeholder_rollout_map.md" for item in artifact_index_json["artifacts"])
    assert any(item["path"] == "risk_exception_register.md" for item in artifact_index_json["artifacts"])
    assert any(item["path"] == "operational_audit_plan.md" for item in artifact_index_json["artifacts"])
    assert any(item["path"] == "value_measurement_report.md" for item in artifact_index_json["artifacts"])
    assert any(item["path"] == "pilot_scorecard.csv" for item in artifact_index_json["artifacts"])
    assert any(item["path"] == "enterprise_readiness.md" for item in artifact_index_json["artifacts"])
    assert any(item["path"] == "run_summary.md" for item in artifact_index_json["artifacts"])
    assert any(item["path"] == "executive_decision_brief.md" for item in artifact_index_json["artifacts"])
    assert any(item["path"] == "query_recovery.md" for item in artifact_index_json["artifacts"])
