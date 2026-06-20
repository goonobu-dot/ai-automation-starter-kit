import json
import zipfile

from ai_automation_kit.cli import build_parser
from ai_automation_kit.cli import main
from ai_automation_kit.core.operator_console import generate_client_report
from ai_automation_kit.core.operator_console import generate_connector_doctor
from ai_automation_kit.core.operator_console import generate_demo_site
from ai_automation_kit.core.operator_console import generate_flow_guide
from ai_automation_kit.core.operator_console import generate_install_bundle
from ai_automation_kit.core.operator_console import generate_complete_workspace
from ai_automation_kit.core.operator_console import generate_quickstart_workspace
from ai_automation_kit.core.operator_console import package_client_demo
from ai_automation_kit.core.flows import install_flow
from ai_automation_kit.core.flow_runtime import run_flow_project
from ai_automation_kit.core.flow_runtime import approve_all_pending


def test_generate_flow_guide_recommends_flows_for_industry_and_niche(tmp_path):
    output = tmp_path / "flow-guide"

    payload = generate_flow_guide(industry="finance", genre=None, niche="accounting", output=output)

    assert payload["count"] >= 1
    assert (output / "recommended_flows.md").exists()
    assert (output / "recommended_flows.json").exists()
    assert "invoice-document-followup" in (output / "recommended_flows.md").read_text()


def test_generate_quickstart_workspace_creates_user_ready_folder(tmp_path):
    output = tmp_path / "quickstart"

    payload = generate_quickstart_workspace(
        flow_id="invoice-document-followup",
        industry="finance",
        client_type="local-business",
        niche="accounting",
        output=output,
    )

    assert payload["flow_id"] == "invoice-document-followup"
    assert (output / "START_HERE.md").exists()
    assert (output / "flow_project" / "scripts" / "run_automation.py").exists()
    assert (output / "beginner_sales" / "selected_flow_demo.html").exists()
    assert (output / "demo_site" / "index.html").exists()
    assert "Run Order" in (output / "START_HERE.md").read_text()


def test_generate_demo_site_collects_existing_assets(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "README.md").write_text("# Demo Source\n")
    (source / "selected_flow_demo.html").write_text("<html><body>Flow Demo</body></html>")
    output = tmp_path / "demo-site"

    payload = generate_demo_site(source=source, output=output, title="Client Demo")

    assert payload["asset_count"] >= 2
    html = (output / "index.html").read_text()
    assert "Client Demo" in html
    assert "selected_flow_demo.html" in html


def test_generate_install_bundle_creates_flow_sales_and_readiness_assets(tmp_path):
    output = tmp_path / "bundle"

    payload = generate_install_bundle(
        flow_id="invoice-document-followup",
        client_type="local-business",
        niche="accounting",
        output=output,
    )

    assert payload["status"] == "ready"
    assert (output / "flow_project" / "flow.yaml").exists()
    assert (output / "beginner_sales" / "proposal_one_pager.md").exists()
    assert (output / "client_ready" / "maintenance_plan.md").exists()
    assert (output / "bundle_index.md").exists()


def test_connector_doctor_reports_missing_optional_connectors(tmp_path):
    flow_project = tmp_path / "flow"
    install_flow("invoice-document-followup", flow_project)
    output = tmp_path / "doctor"

    payload = generate_connector_doctor(project=flow_project, output=output)

    assert payload["status"] in {"ready", "needs_setup"}
    assert (output / "connector_doctor.md").exists()
    assert "gmail_send" in (output / "connector_doctor.md").read_text()


def test_client_report_uses_flow_runtime_outputs(tmp_path):
    flow_project = tmp_path / "flow"
    install_flow("invoice-document-followup", flow_project)
    run_flow_project(flow_project)
    approve_all_pending(flow_project, approver="owner@example.com")
    output = tmp_path / "client-report"

    payload = generate_client_report(flow_project=flow_project, output=output)

    assert payload["status"] == "ready"
    assert (output / "client_report.md").exists()
    assert (output / "client_report.html").exists()
    assert "Rows processed" in (output / "client_report.md").read_text()


def test_package_client_demo_writes_manifest_and_zip(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "README.md").write_text("# Demo\n")
    (source / "proposal_one_pager.md").write_text("# Proposal\n")
    output = tmp_path / "package"

    payload = package_client_demo(source=source, output=output)

    assert payload["status"] == "packaged"
    assert (output / "client_demo_manifest.json").exists()
    assert (output / "client_demo_package.zip").exists()
    with zipfile.ZipFile(output / "client_demo_package.zip") as archive:
        assert "README.md" in archive.namelist()
        assert "proposal_one_pager.md" in archive.namelist()


def test_generate_complete_workspace_creates_done_for_you_delivery(tmp_path):
    output = tmp_path / "complete"

    payload = generate_complete_workspace(
        flow_id="invoice-document-followup",
        industry="finance",
        client_type="local-business",
        niche="accounting",
        approver="owner@example.com",
        output=output,
    )

    assert payload["status"] == "ready_to_share"
    assert payload["flow_id"] == "invoice-document-followup"
    assert (output / "FINAL_DELIVERY_GUIDE.md").exists()
    assert (output / "completion_checklist.md").exists()
    assert (output / "delivery_manifest.json").exists()
    assert (output / "quickstart" / "flow_project" / "automation_output" / "run_log.json").exists()
    assert (output / "quickstart" / "flow_project" / "local_outbox" / "email_drafts.md").exists()
    assert (output / "connector_doctor" / "connector_doctor.md").exists()
    assert (output / "client_report" / "client_report.html").exists()
    assert (output / "client_demo_package" / "client_demo_package.zip").exists()
    assert (output / "revenue_readiness_scorecard.md").exists()
    assert (output / "sales_closing_script.md").exists()
    assert (output / "paid_poc_scope.md").exists()
    assert (output / "value_measurement_sheet.csv").exists()
    assert (output / "pre_contract_checklist.md").exists()
    assert (output / "client_proposal_email.md").exists()
    assert (output / "first_30_days_plan.md").exists()
    assert (output / "proof_of_value_template.md").exists()
    assert (output / "oss_pattern_benchmark.md").exists()
    assert (output / "integration_backlog.md").exists()
    assert (output / "deployment_options.md").exists()
    assert (output / "production_observability_plan.md").exists()
    assert (output / "automation_opportunity_scorecard.csv").exists()
    assert (output / "client_onboarding_form.md").exists()
    assert (output / "go_live_decision.md").exists()
    guide = (output / "FINAL_DELIVERY_GUIDE.md").read_text()
    assert "Open These Files In This Order" in guide
    assert "revenue_readiness_scorecard.md" in guide
    assert "pre_contract_checklist.md" in guide
    assert "oss_pattern_benchmark.md" in guide
    assert "production_observability_plan.md" in guide
    assert "automation_opportunity_scorecard.csv" in guide
    assert "go_live_decision.md" in guide
    assert "No next recommendation is required" in guide
    scorecard = (output / "revenue_readiness_scorecard.md").read_text()
    assert "Revenue Readiness Scorecard" in scorecard
    assert "Paid PoC" in scorecard
    assert "pilot_fee_floor" in (output / "value_measurement_sheet.csv").read_text()
    assert "Do Not Start Paid Work Until" in (output / "pre_contract_checklist.md").read_text()
    assert "Subject:" in (output / "client_proposal_email.md").read_text()
    assert "Day 1" in (output / "first_30_days_plan.md").read_text()
    assert "Before / After" in (output / "proof_of_value_template.md").read_text()
    benchmark = (output / "oss_pattern_benchmark.md").read_text()
    assert "n8n" in benchmark
    assert "Activepieces" in benchmark
    assert "Windmill" in benchmark
    assert "Trigger.dev" in benchmark
    backlog = (output / "integration_backlog.md").read_text()
    assert "MCP" in backlog
    assert "Google Sheets" in backlog
    deployment = (output / "deployment_options.md").read_text()
    assert "self-host" in deployment
    assert "dry-run" in deployment
    observability = (output / "production_observability_plan.md").read_text()
    assert "retries" in observability
    assert "queues" in observability
    assert "approval audit" in observability
    opportunity = (output / "automation_opportunity_scorecard.csv").read_text()
    assert "workflow_fit_score" in opportunity
    assert "sellable_now" in opportunity
    onboarding = (output / "client_onboarding_form.md").read_text()
    assert "Client Onboarding Form" in onboarding
    assert "Approval Owner" in onboarding
    go_live = (output / "go_live_decision.md").read_text()
    assert "Go-Live Decision" in go_live
    assert "Do Not Go Live" in go_live


def test_parser_accepts_operator_commands():
    parser = build_parser()

    assert parser.parse_args(["flow-guide", "--industry", "finance", "--output", "out"]).command == "flow-guide"
    assert parser.parse_args(["quickstart", "--output", "out"]).command == "quickstart"
    assert parser.parse_args(["demo-site", "--source", "src", "--output", "out"]).command == "demo-site"
    assert parser.parse_args(["install-bundle", "--flow-id", "invoice-document-followup", "--output", "out"]).command == "install-bundle"
    assert parser.parse_args(["connector-doctor", "--project", "flow", "--output", "out"]).command == "connector-doctor"
    assert parser.parse_args(["client-report", "--flow-project", "flow", "--output", "out"]).command == "client-report"
    assert parser.parse_args(["package-client-demo", "--source", "src", "--output", "out"]).command == "package-client-demo"
    assert parser.parse_args(["complete-workspace", "--output", "out"]).command == "complete-workspace"


def test_main_runs_operator_commands(tmp_path, capsys):
    quickstart = tmp_path / "quickstart"
    assert main(["quickstart", "--flow-id", "invoice-document-followup", "--output", str(quickstart)]) == 0
    assert (quickstart / "START_HERE.md").exists()

    flow_guide = tmp_path / "guide"
    assert main(["flow-guide", "--industry", "finance", "--output", str(flow_guide)]) == 0

    demo_site = tmp_path / "site"
    assert main(["demo-site", "--source", str(quickstart), "--output", str(demo_site)]) == 0

    connector = tmp_path / "connector"
    assert main(["connector-doctor", "--project", str(quickstart / "flow_project"), "--output", str(connector)]) == 0

    report = tmp_path / "report"
    main(["flows", "run", str(quickstart / "flow_project")])
    main(["flows", "approve", str(quickstart / "flow_project")])
    assert main(["client-report", "--flow-project", str(quickstart / "flow_project"), "--output", str(report)]) == 0

    package = tmp_path / "package"
    assert main(["package-client-demo", "--source", str(quickstart), "--output", str(package)]) == 0

    complete = tmp_path / "complete"
    assert main(["complete-workspace", "--flow-id", "invoice-document-followup", "--output", str(complete)]) == 0

    captured = capsys.readouterr()
    assert "quickstart=" in captured.out
    assert "client_demo_package=" in captured.out
    assert "final_delivery_guide=" in captured.out
    assert json.loads((package / "client_demo_manifest.json").read_text())["file_count"] >= 1
