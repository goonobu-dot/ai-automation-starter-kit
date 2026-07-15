from ai_automation_kit.cli import build_parser
from ai_automation_kit.cli import main
import json
import subprocess
import sys
import types
from pathlib import Path

import pytest


@pytest.fixture
def office_workspace_pack_stubs(monkeypatch):
    packs = {
        "monthly-report": {
            "id": "monthly-report",
            "period_type": "month",
            "questions": [{"id": "audience", "required": True, "type": "short_text", "max_length": 200}],
            "outputs": [{"relative_path": "monthly_report.md"}],
        },
        "inquiry-daily": {
            "id": "inquiry-daily",
            "period_type": "day",
            "questions": [{"id": "audience", "required": True, "type": "short_text", "max_length": 200}],
            "outputs": [{"relative_path": "daily_inquiry.md"}],
        },
    }

    def fake_load_bundled_pack(pack_id):
        try:
            return json.loads(json.dumps(packs[pack_id]))
        except KeyError as exc:
            raise ValueError(f"unknown workflow pack: {pack_id}") from exc

    def fake_pack_manifest_entry(pack_id):
        if pack_id not in packs:
            raise ValueError(f"unknown workflow pack: {pack_id}")
        return {
            "pack_file": f"{pack_id}.json",
            "pack_sha256": "0" * 64,
            "output_schema_file": f"{pack_id}.schema.json",
            "output_schema_sha256": "1" * 64,
        }

    monkeypatch.setattr("ai_automation_kit.core.office_workspace_builder.load_bundled_pack", fake_load_bundled_pack)
    monkeypatch.setattr("ai_automation_kit.core.office_workspace_builder._pack_manifest_entry", fake_pack_manifest_entry)
    monkeypatch.setattr("ai_automation_kit.core.office_workspace_state.load_bundled_pack", fake_load_bundled_pack)


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


def test_parser_accepts_manual_studio_commands():
    parser = build_parser()

    create = parser.parse_args(
        ["manual-studio", "create", "--output", "manual", "--name", "Invoice entry", "--language", "en"]
    )
    assert create.command == "manual-studio"
    assert create.manual_studio_command == "create"
    assert create.output == "manual"
    assert create.name == "Invoice entry"

    prepare = parser.parse_args(
        ["manual-studio", "prepare", "--workspace", "manual", "--transcribe", "--transcription-model", "small"]
    )
    assert prepare.manual_studio_command == "prepare"
    assert prepare.transcribe is True
    assert prepare.transcription_model == "small"

    build = parser.parse_args(
        ["manual-studio", "build", "--workspace", "manual", "--title", "Invoice entry", "--open"]
    )
    assert build.manual_studio_command == "build"
    assert build.open_browser is True

    images = parser.parse_args(
        ["manual-studio", "images", "--workspace", "manual", "--port", "4314", "--no-open"]
    )
    assert images.manual_studio_command == "images"
    assert images.port == 4314
    assert images.open_browser is False

    status = parser.parse_args(["manual-studio", "status", "--workspace", "manual", "--json"])
    assert status.manual_studio_command == "status"
    assert status.as_json is True

    questions = parser.parse_args(["manual-studio", "questions", "--workspace", "manual", "--json"])
    assert questions.manual_studio_command == "questions"
    assert questions.as_json is True

    answer = parser.parse_args(
        [
            "manual-studio",
            "answer",
            "--workspace",
            "manual",
            "--answer",
            "The finance manager",
            "--source",
            "Process owner confirmation",
            "--answered-by",
            "Process owner",
        ]
    )
    assert answer.manual_studio_command == "answer"
    assert answer.source_kind == "operator"

    complete = parser.parse_args(
        ["manual-studio", "complete", "--workspace", "manual", "--title", "Invoice entry"]
    )
    assert complete.manual_studio_command == "complete"

    approve = parser.parse_args(
        ["manual-studio", "approve", "--workspace", "manual", "--approved-by", "Process owner"]
    )
    assert approve.manual_studio_command == "approve"


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


def test_parser_accepts_report_automation_command():
    parser = build_parser()
    args = parser.parse_args(
        [
            "report-automation",
            "--report-type",
            "monthly",
            "--past-outputs",
            "past",
            "--materials",
            "materials",
            "--client-type",
            "local-business",
            "--niche",
            "construction",
            "--output",
            "report-pack",
        ]
    )
    assert args.command == "report-automation"
    assert args.report_type == "monthly"
    assert args.past_outputs == "past"
    assert args.materials == "materials"
    assert args.client_type == "local-business"
    assert args.niche == "construction"
    assert args.output == "report-pack"


def test_parser_accepts_report_wizard_init_defaults():
    parser = build_parser()
    args = parser.parse_args(["report-wizard", "init", "--workspace", "workspace"])

    assert args.command == "report-wizard"
    assert args.report_wizard_command == "init"
    assert args.workspace == "workspace"
    assert args.report_type == "monthly"
    assert args.language == "ja"


def test_parser_accepts_report_wizard_nested_commands():
    parser = build_parser()

    inspect_args = parser.parse_args(
        [
            "report-wizard",
            "inspect",
            "--workspace",
            "workspace",
            "--past-outputs",
            "past-a.md",
            "past-b.md",
            "--materials",
            "notes.md",
            "metrics.csv",
        ]
    )
    assert inspect_args.report_wizard_command == "inspect"
    assert inspect_args.past_outputs == ["past-a.md", "past-b.md"]
    assert inspect_args.materials == ["notes.md", "metrics.csv"]

    confirm_args = parser.parse_args(
        [
            "report-wizard",
            "confirm",
            "--workspace",
            "workspace",
            "--correction",
            "a=b=c",
            "--correction",
            "notes=02_current_materials/notes",
        ]
    )
    assert confirm_args.report_wizard_command == "confirm"
    assert confirm_args.correction == ["a=b=c", "notes=02_current_materials/notes"]

    answer_args = parser.parse_args(["report-wizard", "answer", "--workspace", "workspace", "--answer", "done"])
    assert answer_args.report_wizard_command == "answer"
    assert answer_args.answer == "done"
    assert answer_args.skip is False

    skip_args = parser.parse_args(["report-wizard", "answer", "--workspace", "workspace", "--skip"])
    assert skip_args.skip is True

    status_args = parser.parse_args(["report-wizard", "status", "--workspace", "workspace", "--json"])
    assert status_args.report_wizard_command == "status"
    assert status_args.json is True

    build_args = parser.parse_args(["report-wizard", "build", "--workspace", "workspace"])
    assert build_args.report_wizard_command == "build"

    approve_args = parser.parse_args(["report-wizard", "approve", "--workspace", "workspace", "--approver", "Owner"])
    assert approve_args.report_wizard_command == "approve"
    assert approve_args.approver == "Owner"

    serve_args = parser.parse_args(
        ["report-wizard", "serve", "--workspace", "workspace", "--language", "en", "--port", "8080", "--no-open"]
    )
    assert serve_args.report_wizard_command == "serve"
    assert serve_args.language == "en"
    assert serve_args.port == 8080
    assert serve_args.no_open is True


def test_parser_supports_office_workspace_create_status_inspect_and_serve():
    parser = build_parser()

    create_args = parser.parse_args(
        [
            "office-workspace",
            "create",
            "--root",
            "work",
            "--name",
            "Monthly",
            "--approver",
            "Owner",
            "--pin",
            "482913",
            "--period",
            "2026-07",
            "--language",
            "en",
        ]
    )
    assert create_args.command == "office-workspace"
    assert create_args.office_workspace_command == "create"
    assert create_args.root == "work"
    assert create_args.pack == "monthly-report"
    assert create_args.period == "2026-07"
    assert create_args.language == "en"

    daily_create_args = parser.parse_args(
        [
            "office-workspace",
            "create",
            "--root",
            "work",
            "--name",
            "Daily",
            "--approver",
            "Owner",
            "--pin",
            "482913",
            "--pack",
            "inquiry-daily",
            "--period",
            "2026-07-12",
        ]
    )
    assert daily_create_args.office_workspace_command == "create"
    assert daily_create_args.pack == "inquiry-daily"
    assert daily_create_args.period == "2026-07-12"

    packs_args = parser.parse_args(["office-workspace", "packs", "--json"])
    assert packs_args.office_workspace_command == "packs"
    assert packs_args.json is True

    status_args = parser.parse_args(["office-workspace", "status", "--workspace", "workspace", "--json"])
    assert status_args.office_workspace_command == "status"
    assert status_args.json is True

    inspect_args = parser.parse_args(["office-workspace", "inspect", "--workspace", "workspace", "--period", "2026-07"])
    assert inspect_args.office_workspace_command == "inspect"
    assert inspect_args.period == "2026-07"

    serve_args = parser.parse_args(
        ["office-workspace", "serve", "--root", "work", "--language", "en", "--port", "8081", "--no-open"]
    )
    assert serve_args.office_workspace_command == "serve"
    assert serve_args.root == "work"
    assert serve_args.language == "en"
    assert serve_args.port == 8081
    assert serve_args.no_open is True


@pytest.mark.parametrize(
    "argv",
    [
        [
            "office-workspace",
            "create",
            "--root",
            "work",
            "--name",
            "Monthly",
            "--approver",
            "Owner",
            "--pin",
            "482913",
            "--period",
            "2026-07",
            "--shell",
            "bash",
        ],
        ["office-workspace", "serve", "--root", "work", "--sandbox", "workspace-write"],
        ["office-workspace", "serve", "--root", "work", "--api-key", "test-key"],
    ],
)
def test_parser_rejects_unsafe_office_workspace_flags(argv):
    parser = build_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(argv)


@pytest.mark.parametrize(
    "argv",
    [
        ["report-wizard", "init", "--workspace", "workspace", "--report-type", "quarterly"],
        ["report-wizard", "init", "--workspace", "workspace", "--language", "fr"],
        ["report-wizard", "serve", "--workspace", "workspace", "--language", "fr"],
    ],
)
def test_parser_rejects_invalid_report_wizard_choice_values(argv):
    parser = build_parser()

    with pytest.raises(SystemExit) as exc:
        parser.parse_args(argv)

    assert exc.value.code == 2


def test_parser_keeps_report_automation_compatibility_alongside_report_wizard():
    parser = build_parser()

    automation = parser.parse_args(["report-automation", "--output", "automation-pack"])
    wizard = parser.parse_args(["report-wizard", "status", "--workspace", "workspace"])

    assert automation.command == "report-automation"
    assert wizard.command == "report-wizard"


def test_parser_accepts_public_pattern_expansion_commands():
    parser = build_parser()

    command_center = parser.parse_args(["command-center", "--language", "both", "--output", "menu"])
    assert command_center.command == "command-center"
    assert command_center.language == "both"

    skill = parser.parse_args(["skill-pack", "--flow-id", "invoice-document-followup", "--agent", "codex", "--output", "skill"])
    assert skill.command == "skill-pack"
    assert skill.flow_id == "invoice-document-followup"
    assert skill.agent == "codex"

    approval = parser.parse_args(["approval-gate", "--flow-id", "invoice-document-followup", "--output", "approval"])
    assert approval.command == "approval-gate"
    assert approval.flow_id == "invoice-document-followup"

    mcp = parser.parse_args(
        [
            "mcp-connector-plan",
            "--flow-id",
            "invoice-document-followup",
            "--connectors",
            "gmail,google-sheets",
            "--output",
            "mcp",
        ]
    )
    assert mcp.command == "mcp-connector-plan"
    assert mcp.connectors == "gmail,google-sheets"

    workflow = parser.parse_args(
        ["workflow-explainer", "--flow-id", "invoice-document-followup", "--audience", "client", "--output", "workflow"]
    )
    assert workflow.command == "workflow-explainer"
    assert workflow.audience == "client"

    eval_loop = parser.parse_args(
        ["eval-loop", "--flow-id", "invoice-document-followup", "--metric", "hours_saved", "--output", "eval"]
    )
    assert eval_loop.command == "eval-loop"
    assert eval_loop.metric == "hours_saved"

    agent_team = parser.parse_args(["agent-team", "--flow-id", "invoice-document-followup", "--output", "team"])
    assert agent_team.command == "agent-team"

    self_host = parser.parse_args(["self-host-pack", "--flow-id", "invoice-document-followup", "--provider", "docker", "--output", "self-host"])
    assert self_host.command == "self-host-pack"
    assert self_host.provider == "docker"

    connector_catalog = parser.parse_args(["connector-catalog", "--industry", "local-business", "--output", "catalog"])
    assert connector_catalog.command == "connector-catalog"

    script_ui = parser.parse_args(["script-ui-pack", "--flow-id", "invoice-document-followup", "--output", "script-ui"])
    assert script_ui.command == "script-ui-pack"

    rag = parser.parse_args(["knowledge-rag-pack", "--flow-id", "ai-admin-faq-routing", "--output", "rag"])
    assert rag.command == "knowledge-rag-pack"

    hooks = parser.parse_args(["automation-hooks", "--flow-id", "invoice-document-followup", "--output", "hooks"])
    assert hooks.command == "automation-hooks"

    governance = parser.parse_args(["governance-pack", "--flow-id", "invoice-document-followup", "--output", "governance"])
    assert governance.command == "governance-pack"


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


def test_main_runs_report_automation_with_grill_me_questions(tmp_path):
    output = tmp_path / "report-automation"

    exit_code = main(
        [
            "report-automation",
            "--report-type",
            "monthly",
            "--client-type",
            "local-business",
            "--niche",
            "construction",
            "--output",
            str(output),
        ]
    )

    assert exit_code == 0
    expected_files = [
        "START_HERE_REPORT_AUTOMATION.md",
        "workspace_map.md",
        "ai_agent_prompt.md",
        "grill_me_report_questions.md",
        "missing_info_policy.md",
        "proposal_one_pager.md",
        "demo_report_automation.html",
        "report_automation.json",
        "03_templates/monthly_report_template.md",
        "04_ai_analysis/required_fields.json",
        "05_grill_me_questions/questions.md",
        "06_drafts/monthly_report_draft.md",
        "07_approval/approval_checklist.md",
        "scripts/run_report_dry_run.py",
    ]
    for relative_path in expected_files:
        assert (output / relative_path).exists(), relative_path

    (output / "01_past_outputs/monthly_reports/last_month.md").write_text("# Last Month\n\n売上は安定しました。\n", encoding="utf-8")
    (output / "02_current_materials/sales_csv/current.csv").write_text("metric,value\nsales,120\n", encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, "scripts/run_report_dry_run.py"],
        cwd=output,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "past_files=1" in completed.stdout
    assert "material_files=1" in completed.stdout
    questions = (output / "05_grill_me_questions/questions.md").read_text()
    draft = (output / "06_drafts/monthly_report_draft.md").read_text()
    prompt = (output / "ai_agent_prompt.md").read_text()
    payload = json.loads((output / "report_automation.json").read_text())
    assert payload["report_type"] == "monthly"
    assert "one GrillMe question at a time" in prompt
    assert "Which reporting period" in questions
    assert "current.csv" in draft


def test_main_runs_report_automation_weekly_with_type_specific_artifacts(tmp_path):
    output = tmp_path / "report-automation-weekly"

    exit_code = main(
        [
            "report-automation",
            "--report-type",
            "weekly",
            "--client-type",
            "local-business",
            "--niche",
            "construction",
            "--output",
            str(output),
        ]
    )

    assert exit_code == 0
    expected_files = [
        "03_templates/daily_report_template.md",
        "03_templates/weekly_report_template.md",
        "03_templates/monthly_report_template.md",
        "06_drafts/daily_report_draft.md",
        "06_drafts/weekly_report_draft.md",
        "06_drafts/monthly_report_draft.md",
        "scripts/run_report_dry_run.py",
    ]
    for relative_path in expected_files:
        assert (output / relative_path).exists(), relative_path

    (output / "01_past_outputs/weekly_reports/last_week.md").write_text("# Last Week\n\n案件は順調でした。\n", encoding="utf-8")
    (output / "02_current_materials/sales_csv/current.csv").write_text("metric,value\nsales,120\n", encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, "scripts/run_report_dry_run.py"],
        cwd=output,
        check=True,
        capture_output=True,
        text=True,
    )

    weekly_template = (output / "03_templates/weekly_report_template.md").read_text(encoding="utf-8")
    weekly_draft = (output / "06_drafts/weekly_report_draft.md").read_text(encoding="utf-8")
    prompt = (output / "ai_agent_prompt.md").read_text(encoding="utf-8")
    payload = json.loads((output / "report_automation.json").read_text(encoding="utf-8"))

    assert payload["report_type"] == "weekly"
    assert "weekly business reports" in prompt
    assert "06_drafts/weekly_report_draft.md" in prompt
    assert "# Weekly Report" in weekly_template
    assert "# Weekly Report Draft" in weekly_draft
    assert "current.csv" in weekly_draft
    assert "draft=06_drafts/weekly_report_draft.md" in completed.stdout


def test_main_report_wizard_rejects_malformed_correction_without_traceback(tmp_path, capsys):
    workspace = tmp_path / "workspace"

    exit_code = main(["report-wizard", "init", "--workspace", str(workspace)])
    assert exit_code == 0
    capsys.readouterr()

    exit_code = main(
        [
            "report-wizard",
            "confirm",
            "--workspace",
            str(workspace),
            "--correction",
            "missing-equals",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "SOURCE=DEST" in captured.err
    assert "Traceback" not in captured.err
    assert captured.out == ""


def test_main_report_wizard_answer_requires_text_unless_skip(tmp_path, capsys):
    workspace = tmp_path / "workspace"
    past = tmp_path / "past.md"
    material = tmp_path / "material.csv"
    past.write_text("# Summary\n", encoding="utf-8")
    material.write_text("metric,value\nsales,10\n", encoding="utf-8")

    assert main(["report-wizard", "init", "--workspace", str(workspace)]) == 0
    capsys.readouterr()
    assert (
        main(
            [
                "report-wizard",
                "inspect",
                "--workspace",
                str(workspace),
                "--past-outputs",
                str(past),
                "--materials",
                str(material),
            ]
        )
        == 0
    )
    capsys.readouterr()
    assert main(["report-wizard", "confirm", "--workspace", str(workspace)]) == 0
    capsys.readouterr()

    exit_code = main(["report-wizard", "answer", "--workspace", str(workspace)])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "provide --answer TEXT or use --skip" in captured.err
    assert "Traceback" not in captured.err

    exit_code = main(["report-wizard", "answer", "--workspace", str(workspace), "--skip"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "stage=questioning" in captured.out
    assert captured.err == ""


def test_main_report_wizard_full_loop_build_status_json_and_approve(tmp_path, capsys):
    workspace = tmp_path / "workspace"
    past = tmp_path / "past.md"
    material = tmp_path / "material.csv"
    past.write_text("# Executive Summary\n# Metrics\n", encoding="utf-8")
    material.write_text("metric,value\nsales,120\n", encoding="utf-8")

    assert (
        main(
            [
                "report-wizard",
                "init",
                "--workspace",
                str(workspace),
                "--report-type",
                "weekly",
                "--language",
                "en",
            ]
        )
        == 0
    )
    captured = capsys.readouterr()
    assert "stage=created" in captured.out
    assert "next_action=Inspect approved past reports and current materials" in captured.out

    assert (
        main(
            [
                "report-wizard",
                "inspect",
                "--workspace",
                str(workspace),
                "--past-outputs",
                str(past),
                "--materials",
                str(material),
            ]
        )
        == 0
    )
    captured = capsys.readouterr()
    assert "stage=inspection_ready" in captured.out
    assert "current_question_id=report_audience" in captured.out

    assert main(["report-wizard", "confirm", "--workspace", str(workspace)]) == 0
    captured = capsys.readouterr()
    assert "stage=questioning" in captured.out

    question_ids = [
        "report_audience",
        "best_style_reference",
        "mandatory_sections",
        "reporting_period",
        "final_approver",
        "save_destination",
    ]
    for question_id in question_ids:
        exit_code = main(
            [
                "report-wizard",
                "answer",
                "--workspace",
                str(workspace),
                "--answer",
                f"answer for {question_id}",
            ]
        )
        captured = capsys.readouterr()
        assert exit_code == 0
        if question_id != question_ids[-1]:
            assert "stage=questioning" in captured.out
        else:
            assert "stage=ready_for_draft" in captured.out

    exit_code = main(["report-wizard", "build", "--workspace", str(workspace)])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "stage=ready_for_human_review" in captured.out
    assert f"artifact_draft={workspace / '06_drafts/weekly_report_draft.md'}" in captured.out
    assert f"artifact_template={workspace / '03_templates/weekly_report_template.md'}" in captured.out
    assert captured.err == ""

    exit_code = main(["report-wizard", "status", "--workspace", str(workspace), "--json"])
    captured = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["stage"] == "ready_for_human_review"
    assert payload["report_type"] == "weekly"
    assert payload["language"] == "en"
    assert captured.err == ""

    exit_code = main(["report-wizard", "approve", "--workspace", str(workspace), "--approver", "Owner"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "stage=approved" in captured.out
    assert f"artifact_approval={workspace / '07_approval/approval.json'}" in captured.out


def test_main_report_wizard_build_and_status_exit_contract(tmp_path, capsys):
    workspace = tmp_path / "workspace"
    past = tmp_path / "past.md"
    material = tmp_path / "material.csv"
    past.write_text("# Summary\n", encoding="utf-8")
    material.write_text("metric,value\nsales,10\n", encoding="utf-8")

    assert main(["report-wizard", "init", "--workspace", str(workspace)]) == 0
    capsys.readouterr()
    assert (
        main(
            [
                "report-wizard",
                "inspect",
                "--workspace",
                str(workspace),
                "--past-outputs",
                str(past),
                "--materials",
                str(material),
            ]
        )
        == 0
    )
    capsys.readouterr()
    assert main(["report-wizard", "confirm", "--workspace", str(workspace)]) == 0
    capsys.readouterr()

    exit_code = main(["report-wizard", "build", "--workspace", str(workspace)])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "stage=questioning" in captured.out
    assert "next_action=Resolve unresolved items before approval" in captured.out
    assert captured.err == ""

    exit_code = main(["report-wizard", "status", "--workspace", str(workspace)])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "stage=questioning" in captured.out

    exit_code = main(["report-wizard", "approve", "--workspace", str(workspace), "--approver", "Owner"])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "ready_for_human_review" in captured.err or "unresolved" in captured.err
    assert "Traceback" not in captured.err


def test_main_report_wizard_serve_lazy_imports_server_only_when_needed(tmp_path, monkeypatch, capsys):
    workspace = tmp_path / "workspace"
    imported = {"names": []}
    called = {}

    def fake_import_module(name):
        imported["names"].append(name)
        return types.SimpleNamespace(
            run_report_wizard_server=lambda workspace, language, port, open_browser: called.update(
                {
                    "workspace": workspace,
                    "language": language,
                    "port": port,
                    "open_browser": open_browser,
                }
            )
        )

    monkeypatch.setattr("ai_automation_kit.cli.importlib.import_module", fake_import_module)

    exit_code = main(["report-wizard", "init", "--workspace", str(workspace)])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert imported["names"] == []
    assert "stage=created" in captured.out

    exit_code = main(
        [
            "report-wizard",
            "serve",
            "--workspace",
            str(workspace),
            "--language",
            "en",
            "--port",
            "4310",
            "--no-open",
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert imported["names"] == ["ai_automation_kit.core.report_wizard_server"]
    assert called == {
        "workspace": Path(workspace),
        "language": "en",
        "port": 4310,
        "open_browser": False,
    }
    assert captured.out == ""
    assert captured.err == ""


def test_main_runs_office_workspace_create_status_and_inspect(tmp_path, capsys, office_workspace_pack_stubs):
    root = tmp_path / "workspaces"
    workspace = root / "Monthly"

    exit_code = main(
        [
            "office-workspace",
            "create",
            "--root",
            str(root),
            "--name",
            "Monthly",
            "--approver",
            "Owner",
            "--pin",
            "482913",
            "--period",
            "2026-07",
            "--language",
            "en",
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "workspace=" in captured.out
    assert str(workspace) in captured.out
    assert "next_action=Put this month's files into 03_CURRENT_INPUTS/2026-07." in captured.out

    (workspace / "01_APPROVED_PAST_OUTPUTS" / "approved.md").write_text("# Past\nRevenue 100\n", encoding="utf-8")
    (workspace / "03_CURRENT_INPUTS" / "2026-07" / "current.md").write_text("# Current\nRevenue 120\n", encoding="utf-8")

    exit_code = main(["office-workspace", "status", "--workspace", str(workspace), "--json"])
    first_status = capsys.readouterr()
    assert exit_code == 0
    first_payload = json.loads(first_status.out)
    assert first_payload["workspace"] == str(workspace)
    assert first_payload["current_period"] == "2026-07"
    assert first_payload["current_stage"] == "created"
    assert first_payload["next_action"].startswith("Put this month's files")

    exit_code = main(["office-workspace", "status", "--workspace", str(workspace), "--json"])
    second_status = capsys.readouterr()
    assert exit_code == 0
    assert second_status.out == first_status.out

    exit_code = main(["office-workspace", "inspect", "--workspace", str(workspace), "--period", "2026-07"])
    inspect_output = capsys.readouterr()
    assert exit_code == 0
    assert "stage=questioning" in inspect_output.out
    assert "accepted=2" in inspect_output.out
    assert "pending_questions=audience" in inspect_output.out


def test_main_runs_office_workspace_create_with_daily_pack(tmp_path, capsys, office_workspace_pack_stubs):
    root = tmp_path / "workspaces"
    workspace = root / "Daily_Support"

    exit_code = main(
        [
            "office-workspace",
            "create",
            "--root",
            str(root),
            "--name",
            "Daily Support",
            "--approver",
            "Owner",
            "--pin",
            "482913",
            "--pack",
            "inquiry-daily",
            "--period",
            "2026-07-12",
            "--language",
            "en",
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "workspace=" in captured.out
    assert str(workspace) in captured.out
    assert "next_action=Put this month's files into 03_CURRENT_INPUTS/2026-07-12." in captured.out

    exit_code = main(["office-workspace", "status", "--workspace", str(workspace), "--json"])
    status_output = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(status_output.out)
    assert payload["workspace"] == str(workspace)
    assert payload["pack_id"] == "inquiry-daily"
    assert payload["current_period"] == "2026-07-12"
    assert payload["current_stage"] == "created"


def test_main_removes_partial_workspace_when_first_daily_period_is_invalid(tmp_path, capsys):
    exit_code = main(
        [
            "office-workspace",
            "create",
            "--root",
            str(tmp_path),
            "--name",
            "Broken Daily",
            "--approver",
            "Owner",
            "--pin",
            "482913",
            "--pack",
            "inquiry-daily",
            "--period",
            "2026-07",
        ]
    )

    assert exit_code == 2
    assert "YYYY-MM-DD" in capsys.readouterr().err
    assert not (tmp_path / "Broken_Daily").exists()


def test_main_runs_office_workspace_packs(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "ai_automation_kit.cli.list_bundled_packs",
        lambda: [
            {
                "id": "monthly-report",
                "display_name": {"ja": "月次レポート", "en": "Monthly Report"},
                "period_type": "month",
                "risk_tier": "medium",
            },
            {
                "id": "inquiry-daily",
                "display_name": {"ja": "日次問い合わせ", "en": "Daily Inquiry"},
                "period_type": "day",
                "risk_tier": "low",
            },
        ],
    )

    exit_code = main(["office-workspace", "packs"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == (
        "id=monthly-report\n"
        "name_ja=月次レポート\n"
        "name_en=Monthly Report\n"
        "period_type=month\n"
        "risk_tier=medium\n"
        "\n"
        "id=inquiry-daily\n"
        "name_ja=日次問い合わせ\n"
        "name_en=Daily Inquiry\n"
        "period_type=day\n"
        "risk_tier=low\n"
    )
    assert captured.err == ""

    exit_code = main(["office-workspace", "packs", "--json"])
    json_output = capsys.readouterr()
    assert exit_code == 0
    assert json.loads(json_output.out) == [
        {
            "id": "monthly-report",
            "display_name": {"ja": "月次レポート", "en": "Monthly Report"},
            "period_type": "month",
            "risk_tier": "medium",
        },
        {
            "id": "inquiry-daily",
            "display_name": {"ja": "日次問い合わせ", "en": "Daily Inquiry"},
            "period_type": "day",
            "risk_tier": "low",
        },
    ]
    assert json_output.err == ""


def test_main_office_workspace_create_rejects_symlink_root_without_target_writes(tmp_path, capsys):
    target = tmp_path / "target"
    target.mkdir()
    symlink_root = tmp_path / "linked-root"
    symlink_root.symlink_to(target, target_is_directory=True)

    exit_code = main(
        [
            "office-workspace",
            "create",
            "--root",
            str(symlink_root),
            "--name",
            "Monthly",
            "--approver",
            "Owner",
            "--pin",
            "482913",
            "--period",
            "2026-07",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "symlink" in captured.err.lower()
    assert list(target.iterdir()) == []


@pytest.mark.parametrize("command", ["status", "inspect", "serve"])
def test_main_office_workspace_commands_reject_symlink_workspace_path(tmp_path, capsys, command, office_workspace_pack_stubs):
    root = tmp_path / "workspaces"
    assert (
        main(
            [
                "office-workspace",
                "create",
                "--root",
                str(root),
                "--name",
                "Monthly",
                "--approver",
                "Owner",
                "--pin",
                "482913",
                "--period",
                "2026-07",
            ]
        )
        == 0
    )
    capsys.readouterr()
    linked_workspace = tmp_path / "linked-workspace"
    linked_workspace.symlink_to(root / "Monthly", target_is_directory=True)
    argv = ["office-workspace", command]
    if command == "serve":
        argv.extend(["--root", str(linked_workspace), "--no-open"])
    else:
        argv.extend(["--workspace", str(linked_workspace)])
        if command == "inspect":
            argv.extend(["--period", "2026-07"])

    exit_code = main(argv)

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "symlink" in captured.err.lower()


def test_main_office_workspace_create_accepts_relative_and_absolute_roots(tmp_path, monkeypatch, capsys, office_workspace_pack_stubs):
    monkeypatch.chdir(tmp_path)
    roots = [Path("relative-root"), tmp_path / "absolute-root"]

    for index, root in enumerate(roots, start=1):
        exit_code = main(
            [
                "office-workspace",
                "create",
                "--root",
                str(root),
                "--name",
                "Monthly{}".format(index),
                "--approver",
                "Owner",
                "--pin",
                "482913",
                "--period",
                "2026-07",
            ]
        )
        captured = capsys.readouterr()
        expected = tmp_path / root / "Monthly{}".format(index) if not root.is_absolute() else root / "Monthly{}".format(index)
        assert exit_code == 0
        assert "workspace={}".format(expected) in captured.out
        assert expected.is_dir()


def test_main_office_workspace_serve_lazy_imports_server_only_when_needed(tmp_path, monkeypatch, capsys, office_workspace_pack_stubs):
    root = tmp_path / "workspaces"
    imported = {"names": []}
    called = {}

    def fake_import_module(name):
        imported["names"].append(name)
        return types.SimpleNamespace(
            run_office_workspace_server=lambda root, language, port, open_browser: called.update(
                {
                    "root": root,
                    "language": language,
                    "port": port,
                    "open_browser": open_browser,
                }
            )
        )

    monkeypatch.setattr("ai_automation_kit.cli.importlib.import_module", fake_import_module)

    exit_code = main(
        [
            "office-workspace",
            "create",
            "--root",
            str(root),
            "--name",
            "Monthly",
            "--approver",
            "Owner",
            "--pin",
            "482913",
            "--period",
            "2026-07",
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert imported["names"] == []
    assert "workspace=" in captured.out

    exit_code = main(
        [
            "office-workspace",
            "serve",
            "--root",
            str(root),
            "--language",
            "en",
            "--port",
            "4311",
            "--no-open",
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert imported["names"] == ["ai_automation_kit.core.office_workspace_server"]
    assert called == {
        "root": Path(root),
        "language": "en",
        "port": 4311,
        "open_browser": False,
    }
    assert captured.out == ""
    assert captured.err == ""


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


def test_main_runs_side_hustle_blueprints_and_prints_key_files(tmp_path, capsys):
    output = tmp_path / "side-hustle-blueprints"

    exit_code = main(
        [
            "side-hustle-blueprints",
            "--industry",
            "local-business",
            "--operator-level",
            "beginner",
            "--output",
            str(output),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "side_hustle_blueprints=" in captured.out
    assert "first_client_picker=" in captured.out
    assert "count=" in captured.out
    assert (output / "START_HERE_SIDE_HUSTLE_BLUEPRINTS.md").exists()
    assert (output / "side_hustle_blueprints.html").exists()


def test_main_runs_public_pattern_expansion_commands(tmp_path, capsys):
    commands = [
        (["command-center", "--language", "both"], "command_center=", "START_HERE_COMMAND_CENTER.md"),
        (["skill-pack", "--flow-id", "invoice-document-followup", "--agent", "codex"], "skill_pack=", "SKILL.md"),
        (["approval-gate", "--flow-id", "invoice-document-followup"], "approval_gate=", "approval_gate.json"),
        (
            ["mcp-connector-plan", "--flow-id", "invoice-document-followup", "--connectors", "gmail,google-sheets"],
            "mcp_connector_plan=",
            "mcp_connector_plan.md",
        ),
        (["agent-team", "--flow-id", "invoice-document-followup"], "agent_team=", "agent_team_roles.md"),
        (["workflow-explainer", "--flow-id", "invoice-document-followup"], "workflow_explainer=", "workflow_explainer.html"),
        (["eval-loop", "--flow-id", "invoice-document-followup", "--metric", "hours_saved"], "eval_loop=", "eval_loop.json"),
        (["self-host-pack", "--flow-id", "invoice-document-followup"], "self_host_pack=", "self_host_runbook.md"),
        (["connector-catalog", "--industry", "local-business"], "connector_catalog=", "connector_piece_catalog.md"),
        (["script-ui-pack", "--flow-id", "invoice-document-followup"], "script_ui_pack=", "script_to_ui_plan.md"),
        (["knowledge-rag-pack", "--flow-id", "ai-admin-faq-routing"], "knowledge_rag_pack=", "knowledge_base_pack.md"),
        (["automation-hooks", "--flow-id", "invoice-document-followup"], "automation_hooks=", "automation_hooks.md"),
        (["governance-pack", "--flow-id", "invoice-document-followup"], "governance_pack=", "governance_pack.md"),
    ]
    for index, (base_args, expected_print, expected_file) in enumerate(commands):
        output = tmp_path / f"pack-{index}"
        exit_code = main([*base_args, "--output", str(output)])
        captured = capsys.readouterr()
        assert exit_code == 0
        assert expected_print in captured.out
        assert (output / expected_file).exists()


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


def test_parser_accepts_beginner_command():
    parser = build_parser()
    args = parser.parse_args(["beginner"])
    assert args.command == "beginner"
    assert args.step is None

    args = parser.parse_args(["beginner", "--step", "3"])
    assert args.step == 3


def test_main_runs_beginner_overview(capsys):
    exit_code = main(["beginner"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "環境準備" in captured.out
    assert "納品と請求" in captured.out
    assert "ai-automation-kit beginner --step 1" in captured.out


def test_main_runs_beginner_step_detail(capsys):
    exit_code = main(["beginner", "--step", "2"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "最初のデモ" in captured.out
    assert "complete-workspace" in captured.out
    assert "この段階でやること" in captured.out
    assert "次の一歩" in captured.out


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


def test_doctor_diagnoses_environment_basics(tmp_path):
    output = tmp_path / "doctor"

    exit_code = main(["doctor", "--output", str(output)])

    assert exit_code == 0
    payload = json.loads((output / "doctor_report.json").read_text())
    check_names = [check["name"] for check in payload["checks"]]
    # Python バージョン / 書き込み権限 / git / パッケージ導入状態が診断対象に含まれる。
    assert "python_version" in check_names
    assert "output_writable" in check_names
    assert "git_available" in check_names
    assert "package_installed" in check_names


def test_doctor_reports_japanese_remedy_when_git_is_missing(tmp_path, monkeypatch):
    monkeypatch.setattr("ai_automation_kit.cli.shutil.which", lambda name: None)
    output = tmp_path / "doctor"

    exit_code = main(["doctor", "--output", str(output)])

    assert exit_code == 1
    payload = json.loads((output / "doctor_report.json").read_text())
    report = (output / "doctor_report.md").read_text()
    git_check = next(check for check in payload["checks"] if check["name"] == "git_available")
    assert git_check["status"] == "fail"
    assert "remedy_ja" in git_check
    assert "git" in git_check["remedy_ja"]
    # NG 項目の日本語対処法が next_actions とレポート本文の両方に出る。
    assert any("git" in action and "ください" in action for action in payload["next_actions"])
    assert "対処法" in report


def test_doctor_keeps_existing_output_contract(tmp_path):
    output = tmp_path / "doctor"

    exit_code = main(["doctor", "--output", str(output)])

    assert exit_code == 0
    payload = json.loads((output / "doctor_report.json").read_text())
    # 後方互換: 先頭チェックは python_version、status は従来の 3 値のまま。
    assert payload["checks"][0]["name"] == "python_version"
    assert payload["status"] in {"ready", "warning", "blocked"}
    assert (output / "doctor_report.md").exists()


def test_autopilot_proof_lab_cli_runs_local_assessment_loop(tmp_path, capsys):
    workspace = tmp_path / "proof-lab"
    evidence = tmp_path / "policy.md"
    input_path = tmp_path / "input.json"
    expected = tmp_path / "expected.json"
    proposed = tmp_path / "proposed.json"
    evidence.write_text("approved policy", encoding="utf-8")
    input_path.write_text('{"amount": 10}', encoding="utf-8")
    expected.write_text('{"route": "standard"}', encoding="utf-8")
    proposed.write_text('{"route": "standard"}', encoding="utf-8")

    exit_code = main(
        [
            "autopilot-proof-lab",
            "init",
            "--workspace",
            str(workspace),
            "--pack-id",
            "monthly-report",
            "--organization",
            "Example Co",
            "--objective",
            "Test monthly report preparation",
            "--requested-level",
            "L3",
            "--language",
            "en",
        ]
    )
    assert exit_code == 0
    assert "assessment_id=" in capsys.readouterr().out

    assert main(
        [
            "autopilot-proof-lab",
            "add-evidence",
            "--workspace",
            str(workspace),
            "--source",
            str(evidence),
            "--role",
            "approved_policy",
            "--classification",
            "internal",
            "--provided-by",
            "Operations owner",
        ]
    ) == 0
    assert "evidence_id=ev-0001" in capsys.readouterr().out
    assert main(
        [
            "autopilot-proof-lab",
            "add-case",
            "--workspace",
            str(workspace),
            "--case-id",
            "case-001",
            "--input",
            str(input_path),
            "--expected",
            str(expected),
            "--proposed",
            str(proposed),
            "--risk-tier",
            "low",
            "--case-class",
            "normal",
            "--expected-route",
            "standard",
            "--proposed-route",
            "standard",
            "--duplicate-action-simulations",
            "1",
            "--elapsed-seconds",
            "0.25",
            "--estimated-cost",
            "0.01",
            "--correction-category",
            "none",
        ]
    ) == 0
    assert "case_id=case-001" in capsys.readouterr().out

    exit_code = main(["autopilot-proof-lab", "evaluate", "--workspace", str(workspace)])
    output = capsys.readouterr().out
    decision = json.loads((workspace / "05_REPORTS" / "readiness_decision.json").read_text(encoding="utf-8"))

    assert exit_code == 0
    assert decision["decision"] in {"not_ready", "assist_only", "ready_conditional", "ready_unattended"}
    assert decision["metrics"]["duplicate_action_simulations"] == 1
    assert "decision=" in output
    assert "external_actions_enabled=false" in output
