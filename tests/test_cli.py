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


def test_parser_accepts_website_side_hustle_command():
    parser = build_parser()
    args = parser.parse_args(
        [
            "website-side-hustle",
            "--industry",
            "hospitality",
            "--client-type",
            "local-business",
            "--niche",
            "tourism-hotel",
            "--output",
            "website-pack",
        ]
    )
    assert args.command == "website-side-hustle"
    assert args.industry == "hospitality"
    assert args.client_type == "local-business"
    assert args.niche == "tourism-hotel"
    assert args.output == "website-pack"


def test_parser_accepts_guided_setup_command():
    parser = build_parser()
    args = parser.parse_args(
        [
            "guided-setup",
            "--flow-id",
            "ai-reception-line-inquiry",
            "--mode",
            "operator",
            "--deployment",
            "cloud",
            "--connectors",
            "line,gmail,google-sheets",
            "--output",
            "guided",
        ]
    )

    assert args.command == "guided-setup"
    assert args.flow_id == "ai-reception-line-inquiry"
    assert args.mode == "operator"
    assert args.deployment == "cloud"
    assert args.connectors == "line,gmail,google-sheets"
    assert args.output == "guided"


def test_parser_accepts_guided_review_command():
    parser = build_parser()
    args = parser.parse_args(
        [
            "guided-review",
            "--answers",
            "guided_setup_answers.json",
            "--output",
            "setup-review",
        ]
    )

    assert args.command == "guided-review"
    assert args.answers == "guided_setup_answers.json"
    assert args.output == "setup-review"


def test_parser_accepts_cloud_plan_command():
    parser = build_parser()
    args = parser.parse_args(
        [
            "cloud-plan",
            "--flow-id",
            "invoice-document-followup",
            "--provider",
            "aws",
            "--workload",
            "scheduled-job",
            "--connectors",
            "gmail,google-sheets",
            "--output",
            "cloud-plan",
        ]
    )

    assert args.command == "cloud-plan"
    assert args.flow_id == "invoice-document-followup"
    assert args.provider == "aws"
    assert args.workload == "scheduled-job"
    assert args.connectors == "gmail,google-sheets"
    assert args.output == "cloud-plan"


def test_parser_accepts_grill_me_command():
    parser = build_parser()
    args = parser.parse_args(
        [
            "grill-me",
            "--flow-id",
            "invoice-document-followup",
            "--mode",
            "beginner",
            "--client-type",
            "local-business",
            "--deployment",
            "cloud",
            "--connectors",
            "gmail,google-sheets",
            "--output",
            "grill-me",
        ]
    )

    assert args.command == "grill-me"
    assert args.flow_id == "invoice-document-followup"
    assert args.mode == "beginner"
    assert args.client_type == "local-business"
    assert args.deployment == "cloud"
    assert args.connectors == "gmail,google-sheets"
    assert args.output == "grill-me"


def test_parser_accepts_flow_export_command():
    parser = build_parser()
    args = parser.parse_args(
        [
            "flow-export",
            "--flow-id",
            "invoice-document-followup",
            "--target",
            "n8n",
            "--output",
            "exports",
        ]
    )

    assert args.command == "flow-export"
    assert args.flow_id == "invoice-document-followup"
    assert args.target == "n8n"
    assert args.output == "exports"


def test_parser_accepts_deployment_pack_command():
    parser = build_parser()
    args = parser.parse_args(
        [
            "deployment-pack",
            "--flow-id",
            "invoice-document-followup",
            "--provider",
            "coolify",
            "--connectors",
            "gmail,google-sheets",
            "--output",
            "deploy",
        ]
    )

    assert args.command == "deployment-pack"
    assert args.flow_id == "invoice-document-followup"
    assert args.provider == "coolify"
    assert args.connectors == "gmail,google-sheets"
    assert args.output == "deploy"


def test_parser_accepts_runtime_safety_command():
    parser = build_parser()
    args = parser.parse_args(["runtime-safety", "--flow-id", "invoice-document-followup", "--output", "ops"])

    assert args.command == "runtime-safety"
    assert args.flow_id == "invoice-document-followup"
    assert args.output == "ops"


def test_parser_accepts_secrets_bootstrap_command():
    parser = build_parser()
    args = parser.parse_args(
        [
            "secrets-bootstrap",
            "--flow-id",
            "invoice-document-followup",
            "--provider",
            "infisical",
            "--connectors",
            "gmail,google-sheets",
            "--output",
            "secrets",
        ]
    )

    assert args.command == "secrets-bootstrap"
    assert args.flow_id == "invoice-document-followup"
    assert args.provider == "infisical"
    assert args.connectors == "gmail,google-sheets"
    assert args.output == "secrets"


def test_parser_accepts_document_intake_command():
    parser = build_parser()
    args = parser.parse_args(
        ["document-intake", "--flow-id", "invoice-document-followup", "--mode", "fast", "--output", "docs"]
    )

    assert args.command == "document-intake"
    assert args.flow_id == "invoice-document-followup"
    assert args.mode == "fast"
    assert args.output == "docs"


def test_parser_accepts_observability_pack_command():
    parser = build_parser()
    args = parser.parse_args(["observability-pack", "--flow-id", "invoice-document-followup", "--output", "obs"])

    assert args.command == "observability-pack"
    assert args.flow_id == "invoice-document-followup"
    assert args.output == "obs"


def test_parser_accepts_state_backend_command():
    parser = build_parser()
    args = parser.parse_args(
        ["state-backend", "--flow-id", "invoice-document-followup", "--backend", "supabase", "--output", "state"]
    )

    assert args.command == "state-backend"
    assert args.flow_id == "invoice-document-followup"
    assert args.backend == "supabase"
    assert args.output == "state"


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


def test_main_runs_guided_setup(tmp_path):
    output = tmp_path / "guided-setup"

    exit_code = main(
        [
            "guided-setup",
            "--flow-id",
            "ai-reception-line-inquiry",
            "--mode",
            "beginner",
            "--deployment",
            "undecided",
            "--connectors",
            "line,gmail,google-sheets",
            "--output",
            str(output),
        ]
    )

    assert exit_code == 0
    assert (output / "START_HERE_GUIDED_SETUP.md").exists()
    assert (output / "guided_setup_questions.md").exists()
    assert (output / "guided_setup_answers.example.json").exists()
    assert (output / "missing_inputs.md").exists()
    assert (output / "local_setup_plan.md").exists()
    assert (output / "cloud_setup_plan.md").exists()
    assert (output / "env_values_needed.md").exists()
    assert (output / "client_request_list.md").exists()
    assert (output / "ai_agent_instruction.md").exists()
    assert (output / "readiness_score.json").exists()
    assert (output / "next_action.md").exists()

    questions = (output / "guided_setup_questions.md").read_text()
    agent_instruction = (output / "ai_agent_instruction.md").read_text()
    score = json.loads((output / "readiness_score.json").read_text())

    assert "reception source" in questions
    assert "deployment target" in questions
    assert "Ask the user one question at a time" in agent_instruction
    assert score["status"] == "needs_input"
    assert "missing_required_inputs" in score


def test_main_runs_guided_review_from_answer_file(tmp_path):
    answers = tmp_path / "guided_setup_answers.json"
    answers.write_text(
        json.dumps(
            {
                "flow_id": "ai-reception-line-inquiry",
                "mode": "beginner",
                "deployment": "cloud",
                "connectors": ["line", "gmail", "google-sheets"],
                "answers": {
                    "business_goal": "Reduce missed LINE inquiries and reply faster.",
                    "reception_source": "LINE official account and web form.",
                    "knowledge_source": "FAQ, price list, and approved reply examples.",
                    "output_destination": "Google Sheets and local approval queue.",
                    "human_approval_rules": "Complaints, refunds, bookings, and price changes require approval.",
                    "deployment_target": "cloud",
                    "client_data_boundary": "Masked sample inquiries only.",
                    "success_metric": "First response time and missed inquiries.",
                    "connector_owner": "Client owns LINE and Google accounts.",
                    "cloud_operator": "",
                },
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "setup-review"

    exit_code = main(["guided-review", "--answers", str(answers), "--output", str(output)])

    assert exit_code == 0
    assert (output / "START_HERE_GUIDED_REVIEW.md").exists()
    assert (output / "setup_readiness_report.md").exists()
    assert (output / "automation_build_plan.md").exists()
    assert (output / "client_missing_items_email.md").exists()
    assert (output / "cloud_provider_decision.md").exists()
    assert (output / "local_vs_cloud_decision.md").exists()
    assert (output / "ai_agent_handoff_prompt.md").exists()
    assert (output / "next_commands.md").exists()
    assert (output / "guided_review.json").exists()

    report = (output / "setup_readiness_report.md").read_text()
    email = (output / "client_missing_items_email.md").read_text()
    commands = (output / "next_commands.md").read_text()
    review = json.loads((output / "guided_review.json").read_text())

    assert review["status"] == "needs_client_input"
    assert "cloud_operator" in review["missing_inputs"]
    assert "Ready now for local dry-run" in report
    assert "cloud_operator" in email
    assert "ai-automation-kit flows install ai-reception-line-inquiry" in commands


def test_main_runs_cloud_plan_for_general_cloud_workload(tmp_path):
    output = tmp_path / "cloud-plan-aws"

    exit_code = main(
        [
            "cloud-plan",
            "--flow-id",
            "invoice-document-followup",
            "--provider",
            "aws",
            "--workload",
            "scheduled-job",
            "--connectors",
            "gmail,google-sheets,storage-folder",
            "--output",
            str(output),
        ]
    )

    assert exit_code == 0
    assert (output / "START_HERE_CLOUD_PLAN.md").exists()
    assert (output / "cloud_provider_matrix.md").exists()
    assert (output / "workload_architecture.md").exists()
    assert (output / "runtime_choice.md").exists()
    assert (output / "secrets_and_env.md").exists()
    assert (output / "network_and_domain.md").exists()
    assert (output / "deploy_runbook.md").exists()
    assert (output / "operations_runbook.md").exists()
    assert (output / "cost_guardrails.md").exists()
    assert (output / "compliance_data_boundary.md").exists()
    assert (output / "incident_rollback.md").exists()
    assert (output / "human_approval_required.md").exists()
    assert (output / "cloud_plan.json").exists()

    architecture = (output / "workload_architecture.md").read_text()
    commands = (output / "deploy_runbook.md").read_text()
    secrets = (output / "secrets_and_env.md").read_text()
    plan = json.loads((output / "cloud_plan.json").read_text())

    assert plan["provider"] == "aws"
    assert plan["workload"] == "scheduled-job"
    assert plan["connectors"] == ["gmail", "google-sheets", "storage-folder"]
    assert "EventBridge" in architecture
    assert "Secrets Manager" in architecture
    assert "aws events" in commands
    assert "GMAIL_CLIENT_ID" in secrets
    assert "GOOGLE_SHEETS_SPREADSHEET_ID" in secrets
    assert "LINE Developers" not in (output / "human_approval_required.md").read_text()
    assert plan["human_steps_required"]


def test_main_runs_cloud_plan_for_major_providers(tmp_path):
    providers = ["google-cloud", "azure", "render", "railway", "vercel", "digitalocean", "fly"]
    for provider in providers:
        output = tmp_path / f"cloud-plan-{provider}"

        exit_code = main(
            [
                "cloud-plan",
                "--flow-id",
                "ai-reception-line-inquiry",
                "--provider",
                provider,
                "--output",
                str(output),
            ]
        )

        assert exit_code == 0
        plan = json.loads((output / "cloud_plan.json").read_text())
        assert plan["provider"] == provider
        assert (output / "deploy_commands.md").exists()
        assert (output / "human_approval_required.md").exists()


def test_main_runs_grill_me_for_beginner_flow_review(tmp_path):
    output = tmp_path / "grill-me"

    exit_code = main(
        [
            "grill-me",
            "--flow-id",
            "invoice-document-followup",
            "--mode",
            "beginner",
            "--client-type",
            "local-business",
            "--deployment",
            "cloud",
            "--connectors",
            "gmail,google-sheets",
            "--output",
            str(output),
        ]
    )

    assert exit_code == 0
    assert (output / "START_HERE_GRILL_ME.md").exists()
    assert (output / "questions_to_answer.md").exists()
    assert (output / "client_interview_grill.md").exists()
    assert (output / "cloud_readiness_grill.md").exists()
    assert (output / "risk_grill.md").exists()
    assert (output / "proposal_grill.md").exists()
    assert (output / "ai_agent_prompt.md").exists()
    assert (output / "grill_me.json").exists()

    start = (output / "START_HERE_GRILL_ME.md").read_text()
    questions = (output / "questions_to_answer.md").read_text()
    prompt = (output / "ai_agent_prompt.md").read_text()
    payload = json.loads((output / "grill_me.json").read_text())

    assert payload["flow_id"] == "invoice-document-followup"
    assert payload["mode"] == "beginner"
    assert payload["deployment"] == "cloud"
    assert payload["connectors"] == ["gmail", "google-sheets"]
    assert "one question at a time" in start
    assert "Do not ask for real API keys or secrets in chat" in prompt
    assert "What business pain" in questions
    assert "human approval" in questions


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


def test_main_runs_website_side_hustle_and_prints_key_files(tmp_path, capsys):
    output = tmp_path / "website-pack"

    exit_code = main(
        [
            "website-side-hustle",
            "--industry",
            "hospitality",
            "--client-type",
            "local-business",
            "--niche",
            "tourism-hotel",
            "--output",
            str(output),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "website_side_hustle=" in captured.out
    assert "proposal=" in captured.out
    assert "sample_site=" in captured.out
    assert (output / "START_HERE_WEBSITE_SIDE_HUSTLE.md").exists()
    assert (output / "proposal_one_pager.md").exists()
    assert (output / "sample_site" / "index.html").exists()


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
