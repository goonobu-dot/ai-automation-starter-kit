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


def test_parser_accepts_onboard_command():
    parser = build_parser()
    args = parser.parse_args(
        [
            "onboard",
            "--business-area",
            "support",
            "--limit",
            "3",
            "--output",
            "out",
            "--include-readme",
        ]
    )
    assert args.command == "onboard"
    assert args.business_area == "support"
    assert args.limit == 3
    assert args.output == "out"
    assert args.include_readme is True


def test_parser_accepts_offer_pack_command():
    parser = build_parser()
    args = parser.parse_args(
        [
            "offer-pack",
            "--business-area",
            "operations",
            "--client-type",
            "small-business",
            "--source-output",
            "discovery",
            "--output",
            "offer",
        ]
    )
    assert args.command == "offer-pack"
    assert args.business_area == "operations"
    assert args.client_type == "small-business"
    assert args.source_output == "discovery"
    assert args.output == "offer"


def test_parser_accepts_client_ready_command():
    parser = build_parser()
    args = parser.parse_args(
        [
            "client-ready",
            "--business-area",
            "operations",
            "--client-type",
            "local-business",
            "--niche",
            "accounting",
            "--source-output",
            "onboarding",
            "--output",
            "client-ready",
        ]
    )
    assert args.command == "client-ready"
    assert args.business_area == "operations"
    assert args.client_type == "local-business"
    assert args.niche == "accounting"
    assert args.source_output == "onboarding"
    assert args.output == "client-ready"


def test_parser_accepts_beginner_sales_command():
    parser = build_parser()
    args = parser.parse_args(
        [
            "beginner-sales",
            "--flow-id",
            "invoice-document-followup",
            "--client-type",
            "local-business",
            "--niche",
            "accounting",
            "--output",
            "beginner-sales",
        ]
    )
    assert args.command == "beginner-sales"
    assert args.flow_id == "invoice-document-followup"
    assert args.client_type == "local-business"
    assert args.niche == "accounting"
    assert args.output == "beginner-sales"


def test_parser_accepts_flows_commands():
    parser = build_parser()

    list_args = parser.parse_args(["flows", "list"])
    show_args = parser.parse_args(["flows", "show", "invoice-document-followup"])
    install_args = parser.parse_args(["flows", "install", "invoice-document-followup", "--output", "out"])
    run_args = parser.parse_args(["flows", "run", "out"])
    approve_args = parser.parse_args(["flows", "approve", "out", "--approver", "owner@example.com"])
    validate_args = parser.parse_args(["flows", "validate", "out"])

    assert list_args.command == "flows"
    assert list_args.flow_command == "list"
    assert show_args.flow_command == "show"
    assert show_args.flow_id == "invoice-document-followup"
    assert install_args.flow_command == "install"
    assert install_args.flow_id == "invoice-document-followup"
    assert install_args.output == "out"
    assert run_args.flow_command == "run"
    assert run_args.path == "out"
    assert approve_args.flow_command == "approve"
    assert approve_args.path == "out"
    assert approve_args.approver == "owner@example.com"
    assert validate_args.flow_command == "validate"
    assert validate_args.path == "out"


def test_parser_accepts_doctor_command():
    parser = build_parser()
    args = parser.parse_args(["doctor", "--output", "out", "--check-github"])
    assert args.command == "doctor"
    assert args.output == "out"
    assert args.check_github is True


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


def test_main_github_discover_prints_next_read_for_adapter_output(tmp_path, monkeypatch, capsys):
    def fake_run(config_path, output_dir):
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "report.md").write_text("# Report\n")
        (output_dir / "artifact_index.md").write_text("# Artifact Index\n")
        (output_dir / "adapter_starter").mkdir()
        (output_dir / "adapter_starter" / "README.md").write_text("# Adapter\n")
        from ai_automation_kit.core.models import RunRecord

        return RunRecord(
            run_id="run-adapter",
            template_name="research-agent",
            input=json.loads(config_path.read_text()),
            started_at="2026-06-17T00:00:00Z",
            finished_at="2026-06-17T00:00:01Z",
            status="succeeded",
            errors=[],
            artifacts=[],
            source_ids=[],
            failed_fetches=[],
        )

    monkeypatch.setattr("ai_automation_kit.cli.run_research_agent", fake_run)

    exit_code = main(["github-discover", "--business-area", "operations", "--output", str(tmp_path / "out")])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert f"next_read={tmp_path / 'out' / 'adapter_starter' / 'README.md'}" in captured.out
    assert f"artifact_index={tmp_path / 'out' / 'artifact_index.md'}" in captured.out


def test_main_github_discover_prints_manual_review_next_read(tmp_path, monkeypatch, capsys):
    def fake_run(config_path, output_dir):
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "report.md").write_text("# Report\n")
        (output_dir / "manual_review_pack.md").write_text("# Manual Review Pack\n")
        from ai_automation_kit.core.models import RunRecord

        return RunRecord(
            run_id="run-review",
            template_name="research-agent",
            input=json.loads(config_path.read_text()),
            started_at="2026-06-17T00:00:00Z",
            finished_at="2026-06-17T00:00:01Z",
            status="succeeded",
            errors=[],
            artifacts=[],
            source_ids=[],
            failed_fetches=[],
        )

    monkeypatch.setattr("ai_automation_kit.cli.run_research_agent", fake_run)

    exit_code = main(["github-discover", "--business-area", "support", "--output", str(tmp_path / "out")])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert f"next_read={tmp_path / 'out' / 'manual_review_pack.md'}" in captured.out


def test_main_github_discover_only_prints_existing_optional_outputs(tmp_path, monkeypatch, capsys):
    def fake_run(config_path, output_dir):
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "report.md").write_text("# Report\n")
        (output_dir / "artifact_index.md").write_text("# Artifact Index\n")
        (output_dir / "query_recovery.md").write_text("# Query Recovery\n")
        from ai_automation_kit.core.models import RunRecord

        return RunRecord(
            run_id="run-empty",
            template_name="research-agent",
            input=json.loads(config_path.read_text()),
            started_at="2026-06-17T00:00:00Z",
            finished_at="2026-06-17T00:00:01Z",
            status="succeeded",
            errors=[],
            artifacts=[],
            source_ids=[],
            failed_fetches=[],
        )

    monkeypatch.setattr("ai_automation_kit.cli.run_research_agent", fake_run)

    exit_code = main(["github-discover", "--business-area", "support", "--output", str(tmp_path / "out")])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert f"report={tmp_path / 'out' / 'report.md'}" in captured.out
    assert f"artifact_index={tmp_path / 'out' / 'artifact_index.md'}" in captured.out
    assert f"next_read={tmp_path / 'out' / 'query_recovery.md'}" in captured.out
    assert "candidates=" not in captured.out
    assert "business_plan=" not in captured.out


def test_main_runs_onboard_and_writes_summary(tmp_path, monkeypatch, capsys):
    def fake_doctor(output_dir, check_github=False):
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "doctor_report.md").write_text("# Doctor\n")
        return {"status": "warning", "checks": [], "next_actions": ["Set GITHUB_TOKEN for higher limits."]}

    def fake_run(config_path, output_dir):
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "run_summary.md").write_text("# Run Summary\n")
        (output_dir / "executive_decision_brief.md").write_text("# Executive Decision Brief\n")
        (output_dir / "pilot_scorecard.csv").write_text("metric,owner\n")
        (output_dir / "artifact_index.md").write_text("# Artifact Index\n")
        (output_dir / "manual_review_pack.md").write_text("# Manual Review Pack\n")
        from ai_automation_kit.core.models import RunRecord

        return RunRecord(
            run_id="run-onboard",
            template_name="research-agent",
            input=json.loads(config_path.read_text()),
            started_at="2026-06-17T00:00:00Z",
            finished_at="2026-06-17T00:00:01Z",
            status="succeeded",
            errors=[],
            artifacts=[],
            source_ids=[],
            failed_fetches=[],
        )

    monkeypatch.setattr("ai_automation_kit.cli._run_doctor", fake_doctor)
    monkeypatch.setattr("ai_automation_kit.cli.run_research_agent", fake_run)

    output = tmp_path / "onboard"
    exit_code = main(["onboard", "--business-area", "support", "--limit", "3", "--output", str(output)])

    captured = capsys.readouterr()
    summary = (output / "onboarding_summary.md").read_text()
    payload = json.loads((output / "onboarding_summary.json").read_text())
    generated_config = json.loads((output / "github_discover_config.json").read_text())
    assert exit_code == 0
    assert "onboarding_summary=" in captured.out
    assert "next_read=" in captured.out
    assert "AI Automation Starter Kit Onboarding Summary" in summary
    assert "support" in summary
    assert payload["business_area"] == "support"
    assert payload["doctor_status"] == "warning"
    assert payload["run_status"] == "succeeded"
    assert payload["next_read"][0] == "run_summary.md"
    assert generated_config["business_context"]["business_area"] == "support"
    assert generated_config["github_searches"][0]["per_page"] == 3


def test_main_runs_offer_pack_and_prints_key_files(tmp_path, capsys):
    source = tmp_path / "discovery"
    source.mkdir()
    (source / "business_automation_summary.json").write_text(
        json.dumps(
            {
                "business_area": "operations",
                "executive_recommendation": "Start with a workflow automation pilot.",
                "recommended_projects": [{"full_name": "n8n-io/n8n", "url": "https://github.com/n8n-io/n8n"}],
            }
        )
    )
    (source / "pilot_scorecard.csv").write_text("metric,owner\nmanual_handoffs,ops\n")
    output = tmp_path / "offer"

    exit_code = main(
        [
            "offer-pack",
            "--business-area",
            "operations",
            "--client-type",
            "small-business",
            "--source-output",
            str(source),
            "--output",
            str(output),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "offer_pack=" in captured.out
    assert "proposal=" in captured.out
    assert "statement_of_work=" in captured.out
    assert (output / "README.md").exists()
    assert (output / "proposal.md").exists()
    assert (output / "pricing_model.md").exists()
    assert "small-business" in (output / "offer_pack.json").read_text()


def test_main_runs_client_ready_and_prints_key_files(tmp_path, capsys):
    source = tmp_path / "onboarding"
    source.mkdir()
    (source / "business_automation_summary.json").write_text(
        json.dumps(
            {
                "business_area": "operations",
                "executive_recommendation": "Start with an accounting workflow pilot.",
                "recommended_projects": [{"full_name": "n8n-io/n8n", "url": "https://github.com/n8n-io/n8n"}],
            }
        )
    )
    output = tmp_path / "client-ready"

    exit_code = main(
        [
            "client-ready",
            "--business-area",
            "operations",
            "--client-type",
            "local-business",
            "--niche",
            "accounting",
            "--source-output",
            str(source),
            "--output",
            str(output),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "client_ready=" in captured.out
    assert "roi_calculator=" in captured.out
    assert "maintenance_plan=" in captured.out
    assert (output / "README.md").exists()
    assert (output / "implementation_readiness_score.json").exists()
    assert (output / "marketplace_profile.md").exists()


def test_main_runs_beginner_sales_and_prints_key_files(tmp_path, capsys):
    output = tmp_path / "beginner-sales"

    exit_code = main(
        [
            "beginner-sales",
            "--flow-id",
            "invoice-document-followup",
            "--client-type",
            "local-business",
            "--niche",
            "accounting",
            "--output",
            str(output),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "beginner_sales=" in captured.out
    assert "flow_gallery=" in captured.out
    assert "proposal=" in captured.out
    assert (output / "START_HERE_FOR_SIDE_BUSINESS.md").exists()
    assert (output / "selected_flow_demo.html").exists()
    assert (output / "proposal_one_pager.md").exists()


def test_main_runs_flows_list_show_install_and_validate(tmp_path, capsys):
    exit_code = main(["flows", "list", "--industry", "finance"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "invoice-document-followup" in captured.out

    exit_code = main(["flows", "show", "invoice-document-followup"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Invoice and Document Follow-up" in captured.out
    assert "human_approval" in captured.out

    output = tmp_path / "invoice-project"
    exit_code = main(["flows", "install", "invoice-document-followup", "--output", str(output)])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "flow_project=" in captured.out
    assert (output / "flow.yaml").exists()
    assert (output / "workflow_map.mmd").exists()

    exit_code = main(["flows", "validate", str(output)])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "status=ready" in captured.out

    exit_code = main(["flows", "run", str(output)])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "automation_status=succeeded" in captured.out
    assert "draft_outputs=" in captured.out
    assert (output / "automation_output" / "draft_outputs.md").exists()
    assert (output / "automation_output" / "approval_queue.csv").exists()

    exit_code = main(["flows", "approve", str(output), "--approver", "owner@example.com"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "approval_status=approved" in captured.out
    assert (output / "local_outbox" / "email_drafts.md").exists()


def test_onboard_can_create_offer_pack(tmp_path, monkeypatch, capsys):
    def fake_doctor(output_dir, check_github=False):
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "doctor_report.md").write_text("# Doctor\n")
        return {"status": "warning", "checks": [], "next_actions": []}

    def fake_run(config_path, output_dir):
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "run_summary.md").write_text("# Run Summary\n")
        (output_dir / "executive_decision_brief.md").write_text("# Executive Decision Brief\n")
        (output_dir / "pilot_scorecard.csv").write_text("metric,owner\n")
        (output_dir / "business_automation_summary.json").write_text(
            json.dumps({"business_area": "support", "executive_recommendation": "Start with support triage."})
        )
        from ai_automation_kit.core.models import RunRecord

        return RunRecord(
            run_id="run-onboard-offer",
            template_name="research-agent",
            input=json.loads(config_path.read_text()),
            started_at="2026-06-17T00:00:00Z",
            finished_at="2026-06-17T00:00:01Z",
            status="succeeded",
            errors=[],
            artifacts=[],
            source_ids=[],
            failed_fetches=[],
        )

    monkeypatch.setattr("ai_automation_kit.cli._run_doctor", fake_doctor)
    monkeypatch.setattr("ai_automation_kit.cli.run_research_agent", fake_run)

    output = tmp_path / "onboard"
    exit_code = main(
        [
            "onboard",
            "--business-area",
            "support",
            "--output",
            str(output),
            "--create-offer-pack",
            "--client-type",
            "local-business",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads((output / "onboarding_summary.json").read_text())
    assert exit_code == 0
    assert "offer_pack=" in captured.out
    assert (output / "offer_pack" / "proposal.md").exists()
    assert "offer_pack/README.md" in payload["next_read"]


def test_main_runs_doctor_without_network(tmp_path):
    output = tmp_path / "doctor"

    exit_code = main(["doctor", "--output", str(output)])

    assert exit_code == 0
    report = (output / "doctor_report.md").read_text()
    payload = json.loads((output / "doctor_report.json").read_text())
    assert "AI Automation Starter Kit Doctor" in report
    assert payload["status"] in {"ready", "warning"}
    assert payload["checks"][0]["name"] == "python_version"
    check_names = [check["name"] for check in payload["checks"]]
    assert "package_metadata" in check_names
    assert "console_script" in check_names
    assert (output / "doctor_report.json").exists()
