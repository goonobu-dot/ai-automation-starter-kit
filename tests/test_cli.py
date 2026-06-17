from ai_automation_kit.cli import build_parser
from ai_automation_kit.cli import main
import json


def test_parser_accepts_research_agent_command():
    parser = build_parser()
    args = parser.parse_args(["research-agent", "--config", "sample.json", "--output", "out"])
    assert args.command == "research-agent"
    assert args.config == "sample.json"
    assert args.output == "out"


def test_parser_accepts_docs_rag_command():
    parser = build_parser()
    args = parser.parse_args(["docs-rag", "--config", "sample.json", "--output", "out"])
    assert args.command == "docs-rag"
    assert args.config == "sample.json"
    assert args.output == "out"


def test_parser_accepts_remaining_template_commands():
    parser = build_parser()
    for command in ["internal-ai-workflow", "excel-to-internal-app", "delivery-pipeline"]:
        args = parser.parse_args([command, "--config", "sample.json", "--output", "out"])
        assert args.command == command
        assert args.config == "sample.json"
        assert args.output == "out"


def test_parser_accepts_github_discover_command():
    parser = build_parser()
    args = parser.parse_args(
        [
            "github-discover",
            "--business-area",
            "sales",
            "--limit",
            "7",
            "--output",
            "out",
            "--include-readme",
        ]
    )
    assert args.command == "github-discover"
    assert args.business_area == "sales"
    assert args.limit == 7
    assert args.output == "out"
    assert args.include_readme is True


def test_main_runs_research_agent(tmp_path):
    source = tmp_path / "source.html"
    source.write_text("<html><head><title>CLI Source</title></head><body><p>Research output works.</p></body></html>")
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"topic": "CLI research", "sources": [{"uri": source.as_uri()}]}))
    output = tmp_path / "out"

    exit_code = main(["research-agent", "--config", str(config), "--output", str(output)])

    assert exit_code == 0
    assert (output / "report.md").exists()


def test_main_runs_docs_rag(tmp_path):
    doc = tmp_path / "policy.md"
    doc.write_text("# Return Policy\n\nCustomers can return unopened items within 30 days.\n")
    config = tmp_path / "docs_config.json"
    config.write_text(
        json.dumps(
            {
                "question": "How long can customers return unopened items?",
                "documents": [{"path": str(doc), "title": "Return Policy"}],
            }
        )
    )
    output = tmp_path / "docs-out"

    exit_code = main(["docs-rag", "--config", str(config), "--output", str(output)])

    assert exit_code == 0
    assert (output / "answer.md").exists()


def test_main_runs_internal_ai_workflow(tmp_path):
    config = tmp_path / "internal_config.json"
    config.write_text(json.dumps({"inquiry_text": "Can you share pricing?", "customer_name": "Avery"}))
    output = tmp_path / "internal-out"

    exit_code = main(["internal-ai-workflow", "--config", str(config), "--output", str(output)])

    assert exit_code == 0
    assert (output / "draft_reply.md").exists()
    assert (output / "approval_request.json").exists()


def test_main_runs_excel_to_internal_app(tmp_path):
    csv_file = tmp_path / "customers.csv"
    csv_file.write_text("id,name\n1,Ada\n")
    config = tmp_path / "excel_config.json"
    config.write_text(json.dumps({"app_name": "Customer CRM", "csv_path": str(csv_file)}))
    output = tmp_path / "excel-out"

    exit_code = main(["excel-to-internal-app", "--config", str(config), "--output", str(output)])

    assert exit_code == 0
    assert (output / "schema.sql").exists()


def test_main_runs_delivery_pipeline(tmp_path):
    config = tmp_path / "delivery_config.json"
    config.write_text(
        json.dumps(
            {
                "project_name": "Example Delivery",
                "template_name": "research-agent",
                "env_vars": ["OPENAI_API_KEY"],
                "services": ["app"],
            }
        )
    )
    output = tmp_path / "delivery-out"

    exit_code = main(["delivery-pipeline", "--config", str(config), "--output", str(output)])

    assert exit_code == 0
    assert (output / "docs" / "delivery-checklist.md").exists()


def test_main_runs_github_discover_without_config(tmp_path, monkeypatch):
    captured = {}

    def fake_run(config_path, output_dir):
        captured["config_path"] = config_path
        captured["output_dir"] = output_dir
        data = json.loads(config_path.read_text())
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "report.md").write_text("# Report\n")
        from ai_automation_kit.core.models import RunRecord

        return RunRecord(
            run_id="run-test",
            template_name="research-agent",
            input=data,
            started_at="2026-06-17T00:00:00Z",
            finished_at="2026-06-17T00:00:01Z",
            status="succeeded",
            errors=[],
            artifacts=[],
            source_ids=[],
            failed_fetches=[],
        )

    monkeypatch.setattr("ai_automation_kit.cli.run_research_agent", fake_run)

    exit_code = main(["github-discover", "--business-area", "sales", "--limit", "3", "--output", str(tmp_path / "out")])

    generated_config = json.loads(captured["config_path"].read_text())
    assert exit_code == 0
    assert generated_config["topic"] == "GitHub discovery for sales automation"
    assert generated_config["github_searches"][0]["per_page"] == 3
    assert len(generated_config["github_searches"]) >= 2
    assert "sales" in generated_config["business_context"]["business_area"]
    assert captured["output_dir"] == tmp_path / "out"
