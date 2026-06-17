import json
from pathlib import Path
from urllib.parse import unquote, urlsplit


def test_research_example_points_to_existing_sources():
    config = Path("examples/research-agent/sample_research.json")
    data = json.loads(config.read_text())
    assert data["topic"]
    for source in data["sources"]:
        parts = urlsplit(source["uri"])
        assert parts.scheme in {"", "file"}
        assert Path(unquote(parts.path)).exists()


def test_all_template_contracts_exist():
    required_sections = [
        "Purpose",
        "Inputs",
        "Outputs",
        "Required Connectors",
        "Safety Defaults",
        "Current Status",
        "Next Implementation Step",
    ]
    for name in ["research-agent", "docs-rag", "internal-ai-workflow", "excel-to-internal-app", "delivery-pipeline"]:
        readme = Path("templates") / name / "README.md"
        assert readme.exists()
        text = readme.read_text()
        for section in required_sections:
            assert section in text


def test_template_readmes_match_current_executable_outputs():
    for name in ["research-agent", "docs-rag", "internal-ai-workflow", "excel-to-internal-app", "delivery-pipeline"]:
        text = (Path("templates") / name / "README.md").read_text()
        assert "artifact_index.md" in text
        assert "Contract only" not in text
        assert "Not executable" not in text

    excel_text = Path("templates/excel-to-internal-app/README.md").read_text()
    assert "app-spec.md" in excel_text
    assert "Executable" in excel_text

    delivery_text = Path("templates/delivery-pipeline/README.md").read_text()
    assert "docs/release-plan.md" in delivery_text
    assert "docs/rollback-plan.md" in delivery_text


def test_oss_integrations_policy_exists():
    text = Path("docs/OSS_INTEGRATIONS.md").read_text()
    assert "adapter-only" in text
    assert "license" in text.lower()


def test_checked_in_expected_report_exists():
    report = Path("examples/research-agent/expected/report.md")
    text = report.read_text()
    assert "Research Report: AI automation starter kit value" in text
    assert "Run Timeline" in text
    assert "Source Table" in text
    assert "Failed URL Log" in text
    assert "Rerun Command" in text


def test_github_research_example_exists():
    config = Path("examples/research-agent/github_repos.json")
    data = json.loads(config.read_text())
    assert data["topic"]
    assert data["github_repositories"] == ["octocat/Hello-World"]


def test_github_search_research_example_exists():
    config = Path("examples/research-agent/github_search.json")
    data = json.loads(config.read_text())
    assert data["topic"]
    assert data["github_searches"][0]["query"]
    assert data["github_searches"][0]["sort"] == "stars"
    assert data["github_searches"][0]["order"] == "desc"


def test_github_readme_research_example_exists():
    config = Path("examples/research-agent/github_repo_with_readme.json")
    data = json.loads(config.read_text())
    assert data["topic"]
    assert data["github_repositories"] == ["octocat/Hello-World"]
    assert data["include_readme"] is True


def test_docs_rag_example_exists():
    config = Path("examples/docs-rag/sample_docs_rag.json")
    data = json.loads(config.read_text())
    assert data["question"]
    for document in data["documents"]:
        assert Path(document["path"]).exists()


def test_docs_rag_expected_answer_exists():
    answer = Path("examples/docs-rag/expected/answer.md")
    text = answer.read_text()
    assert "Docs RAG Answer" in text
    assert "Grounding" in text
    assert "Usage Gate" in text
    assert "Operator Checklist" in text
    assert "30 days" in text


def test_excel_to_internal_app_example_exists():
    config = Path("examples/excel-to-internal-app/sample_app.json")
    data = json.loads(config.read_text())
    assert data["app_name"]
    assert Path(data["csv_path"]).exists()


def test_excel_to_internal_app_expected_report_exists():
    report = Path("examples/excel-to-internal-app/expected/migration-report.md")
    text = report.read_text()
    assert "Migration Report" in text
    assert "Customer CRM" in text
    assert "customer_id" in text
    assert "Permissions" in text
    assert "Suggested App Screens" in text


def test_delivery_pipeline_expected_release_and_rollback_exist():
    release = Path("examples/delivery-pipeline/expected/release-plan.md").read_text()
    rollback = Path("examples/delivery-pipeline/expected/rollback-plan.md").read_text()
    assert "Release Plan" in release
    assert "dry-run or staging" in release
    assert "Rollback Plan" in rollback
    assert "Preserve logs" in rollback
