import json
import zipfile

import pytest

import ai_automation_kit.cli as cli_module
from ai_automation_kit.cli import build_parser
from ai_automation_kit.cli import main
from ai_automation_kit.core.operator_console import generate_client_report
from ai_automation_kit.core.operator_console import generate_connector_doctor
from ai_automation_kit.core.operator_console import generate_demo_site
from ai_automation_kit.core.operator_console import generate_flow_guide
from ai_automation_kit.core.operator_console import generate_install_bundle
from ai_automation_kit.core.operator_console import generate_business_launch_pack
from ai_automation_kit.core.operator_console import generate_complete_workspace
from ai_automation_kit.core.operator_console import generate_first_project_workspace
from ai_automation_kit.core.operator_console import generate_opportunity_catalog
from ai_automation_kit.core.operator_console import generate_quickstart_workspace
from ai_automation_kit.core.operator_console import generate_recommended_flow_from_intake
from ai_automation_kit.core.operator_console import generate_share_check
from ai_automation_kit.core.operator_console import generate_website_side_hustle_pack
from ai_automation_kit.core.operator_console import package_client_demo
from ai_automation_kit.core.side_hustle_blueprints import generate_side_hustle_blueprints
from ai_automation_kit.core.automation_expansion import generate_approval_gate
from ai_automation_kit.core.automation_expansion import generate_agent_team
from ai_automation_kit.core.automation_expansion import generate_automation_hooks
from ai_automation_kit.core.automation_expansion import generate_command_center
from ai_automation_kit.core.automation_expansion import generate_connector_catalog
from ai_automation_kit.core.automation_expansion import generate_eval_loop
from ai_automation_kit.core.automation_expansion import generate_governance_pack
from ai_automation_kit.core.automation_expansion import generate_knowledge_rag_pack
from ai_automation_kit.core.automation_expansion import generate_mcp_connector_plan
from ai_automation_kit.core.automation_expansion import generate_script_ui_pack
from ai_automation_kit.core.automation_expansion import generate_self_host_pack
from ai_automation_kit.core.automation_expansion import generate_skill_pack
from ai_automation_kit.core.automation_expansion import generate_workflow_explainer
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
    assert (output / "client_command_center.html").exists()
    assert (output / "side_business_starter_10.md").exists()
    assert (output / "before_after_demo.html").exists()
    assert (output / "business_launch" / "START_HERE_BUSINESS_LAUNCH.md").exists()
    assert (output / "business_launch" / "first_client_offer.md").exists()
    guide = (output / "FINAL_DELIVERY_GUIDE.md").read_text()
    assert "Open These Files In This Order" in guide
    assert "revenue_readiness_scorecard.md" in guide
    assert "pre_contract_checklist.md" in guide
    assert "oss_pattern_benchmark.md" in guide
    assert "production_observability_plan.md" in guide
    assert "automation_opportunity_scorecard.csv" in guide
    assert "go_live_decision.md" in guide
    assert "client_command_center.html" in guide
    assert "side_business_starter_10.md" in guide
    assert "before_after_demo.html" in guide
    assert "business_launch/START_HERE_BUSINESS_LAUNCH.md" in guide
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
    command_center = (output / "client_command_center.html").read_text()
    assert "Start Here" in command_center
    assert "Sellable PoC" in command_center
    assert "Go-Live Gate" in command_center
    assert "FINAL_DELIVERY_GUIDE.md" in command_center
    assert "Before / After Demo" in (output / "before_after_demo.html").read_text()
    assert "Starter 10" in (output / "side_business_starter_10.md").read_text()
    assert "企業向け自動化導入" in (output / "business_launch" / "first_client_offer.md").read_text()


def test_generate_first_project_workspace_creates_one_entrance_for_beginner(tmp_path):
    output = tmp_path / "my-first-automation"

    payload = generate_first_project_workspace(
        flow_id="invoice-document-followup",
        industry="finance",
        client_type="local-business",
        niche="accounting",
        approver="local-operator",
        language="ja",
        output=output,
    )

    assert payload["status"] == "ready_to_try"
    assert payload["safe_mode"] == "local_dry_run"
    assert payload["external_actions"] == "blocked"
    assert (output / "START_HERE.html").exists()
    assert (output / "AI_NEXT_STEP.md").exists()
    assert (output / "01_CLIENT_INPUT" / "README.txt").exists()
    assert (output / "first_project.json").exists()
    assert (output / "client_command_center.html").exists()
    assert (output / "quickstart" / "flow_project" / "automation_output" / "run_log.json").exists()

    start = (output / "START_HERE.html").read_text()
    assert '<html lang="ja">' in start
    assert "まず、この見本を見る" in start
    assert "顧客データはまだ入れない" in start
    assert "副業の最初の一件" in start
    assert "次はこれだけ" in start
    assert "AI_NEXT_STEP.md をCodexへドラッグ" in start
    assert "client_command_center.html" in start
    assert "AI_NEXT_STEP.md" in start


def test_generate_first_project_workspace_refuses_to_overwrite_existing_files(tmp_path):
    output = tmp_path / "existing"
    output.mkdir()
    marker = output / "keep.txt"
    marker.write_text("do not replace")

    with pytest.raises(FileExistsError, match="not empty"):
        generate_first_project_workspace(
            flow_id=None,
            industry="finance",
            client_type="local-business",
            niche="accounting",
            approver="local-operator",
            language="en",
            output=output,
        )

    assert marker.read_text() == "do not replace"


def test_generate_first_project_workspace_refuses_file_output_and_unknown_industry(tmp_path):
    output_file = tmp_path / "already-a-file"
    output_file.write_text("keep me")

    with pytest.raises(FileExistsError, match="not a directory"):
        generate_first_project_workspace(
            flow_id=None,
            industry="finance",
            client_type="local-business",
            niche="accounting",
            approver="local-operator",
            language="ja",
            output=output_file,
        )

    with pytest.raises(ValueError, match="No automation flow"):
        generate_first_project_workspace(
            flow_id=None,
            industry="not-a-real-industry",
            client_type="local-business",
            niche="accounting",
            approver="local-operator",
            language="ja",
            output=tmp_path / "unknown-industry",
        )

    assert output_file.read_text() == "keep me"


def test_generate_website_side_hustle_pack_creates_public_side_hustle_assets(tmp_path):
    output = tmp_path / "website-pack"

    payload = generate_website_side_hustle_pack(
        industry="hospitality",
        client_type="local-business",
        niche="tourism-hotel",
        operator_level="beginner",
        output=output,
    )

    assert payload["status"] == "ready"
    assert (output / "START_HERE_WEBSITE_SIDE_HUSTLE.md").exists()
    assert (output / "commercial_use_sources.md").exists()
    assert (output / "proposal_one_pager.md").exists()
    assert (output / "maintenance_plan.md").exists()
    assert (output / "ai_agent_handoff.md").exists()
    assert (output / "designer_grade_agent_playbook.md").exists()
    assert (output / "public_ai_design_sources.md").exists()
    assert (output / "website_quality_gate.md").exists()
    assert (output / "homepage_review_scorecard.csv").exists()
    assert (output / "agent_design_review_prompt.md").exists()
    assert (output / "beginner_human_guide.md").exists()
    assert (output / "beginner_human_guide.ja.md").exists()
    assert (output / "reservation_inquiry_system.md").exists()
    assert (output / "client_kickoff_questions.md").exists()
    assert (output / "delivery_acceptance_checklist.md").exists()
    assert (output / "client_handoff_note.md").exists()
    assert (output / "inquiry_intake_schema.csv").exists()
    assert (output / "reservation_pipeline.csv").exists()
    assert (output / "response_templates.md").exists()
    assert (output / "operator_runbook.md").exists()
    assert (output / "integration_options.md").exists()
    assert (output / "privacy_and_consent.md").exists()
    assert (output / "sla_and_followup.md").exists()
    assert (output / "inquiry_dashboard.html").exists()
    assert (output / "sample_site" / "index.html").exists()
    assert "shadcn/ui" in (output / "commercial_use_sources.md").read_text()
    assert "Google Search SEO Starter Guide" in (output / "commercial_use_sources.md").read_text()
    assert "direct competitor clone" in (output / "originality_and_license_rules.md").read_text()
    assert "Codex, Claude Code, Cursor" in (output / "ai_agent_handoff.md").read_text()
    assert "designer-grade" in (output / "designer_grade_agent_playbook.md").read_text()
    assert "Anthropic Claude Skills" in (output / "public_ai_design_sources.md").read_text()
    assert "Core Web Vitals" in (output / "website_quality_gate.md").read_text()
    assert '"criterion","pass_threshold"' in (output / "homepage_review_scorecard.csv").read_text()
    assert "senior website quality reviewer" in (output / "agent_design_review_prompt.md").read_text()
    assert "Beginner Human Guide" in (output / "beginner_human_guide.md").read_text()
    assert "初心者向け" in (output / "beginner_human_guide.ja.md").read_text()
    assert "Do not auto-confirm" in (output / "reservation_inquiry_system.md").read_text()
    assert "What is the first action you want visitors to take?" in (output / "client_kickoff_questions.md").read_text()
    assert "Human approval" in (output / "delivery_acceptance_checklist.md").read_text()
    assert "What the client receives" in (output / "client_handoff_note.md").read_text()
    assert "lead_id" in (output / "inquiry_intake_schema.csv").read_text()
    assert "Google Forms + Google Sheets" in (output / "integration_options.md").read_text()
    assert "Reservation Inbox" in (output / "inquiry_dashboard.html").read_text()


def test_generate_side_hustle_blueprints_creates_sellable_automation_catalog(tmp_path):
    output = tmp_path / "side-hustle-blueprints"

    payload = generate_side_hustle_blueprints(
        industry="local-business",
        operator_level="beginner",
        output=output,
    )

    assert payload["status"] == "ready"
    assert payload["count"] >= 12
    assert (output / "START_HERE_SIDE_HUSTLE_BLUEPRINTS.md").exists()
    assert (output / "side_hustle_blueprints.md").exists()
    assert (output / "side_hustle_blueprints.csv").exists()
    assert (output / "first_client_picker.md").exists()
    assert (output / "offer_scripts.md").exists()
    assert (output / "implementation_paths.md").exists()
    assert (output / "risk_boundaries.md").exists()
    assert (output / "ai_agent_handoff.md").exists()
    assert (output / "client_intake_questions.md").exists()
    assert (output / "side_hustle_blueprints.html").exists()
    assert "Website + Inquiry Operations" in (output / "side_hustle_blueprints.md").read_text()
    assert "AI Reception And First Reply" in (output / "side_hustle_blueprints.md").read_text()
    assert "Do not promise guaranteed revenue" in (output / "risk_boundaries.md").read_text()
    assert "Ask one question at a time" in (output / "ai_agent_handoff.md").read_text()


def test_generate_command_center_creates_beginner_menu(tmp_path):
    output = tmp_path / "command-center"

    payload = generate_command_center(output=output, language="both")

    assert payload["status"] == "ready"
    assert (output / "START_HERE_COMMAND_CENTER.md").exists()
    assert (output / "COMMAND_CENTER.ja.md").exists()
    assert (output / "COMMAND_CENTER.md").exists()
    assert (output / "command_center.html").exists()
    assert (output / "next_step_decision_tree.md").exists()
    assert "迷子にならない" in (output / "COMMAND_CENTER.ja.md").read_text()
    assert "Side-hustle entry" in (output / "COMMAND_CENTER.md").read_text()
    assert "side-hustle-blueprints" in (output / "command_center.html").read_text()


def test_generate_public_pattern_packs_create_agent_ready_assets(tmp_path):
    skill_output = tmp_path / "skill"
    approval_output = tmp_path / "approval"
    mcp_output = tmp_path / "mcp"
    team_output = tmp_path / "team"
    workflow_output = tmp_path / "workflow"
    eval_output = tmp_path / "eval"
    self_host_output = tmp_path / "self-host"
    connector_catalog_output = tmp_path / "connector-catalog"
    script_ui_output = tmp_path / "script-ui"
    rag_output = tmp_path / "rag"
    hooks_output = tmp_path / "hooks"
    governance_output = tmp_path / "governance"

    skill_payload = generate_skill_pack(flow_id="invoice-document-followup", agent="claude-code", output=skill_output)
    approval_payload = generate_approval_gate(flow_id="invoice-document-followup", output=approval_output)
    mcp_payload = generate_mcp_connector_plan(
        flow_id="invoice-document-followup",
        connectors="gmail,google-sheets,slack",
        output=mcp_output,
    )
    team_payload = generate_agent_team(flow_id="invoice-document-followup", output=team_output)
    workflow_payload = generate_workflow_explainer(
        flow_id="invoice-document-followup",
        audience="client",
        output=workflow_output,
    )
    eval_payload = generate_eval_loop(
        flow_id="invoice-document-followup",
        metric="hours_saved",
        output=eval_output,
    )
    self_host_payload = generate_self_host_pack(flow_id="invoice-document-followup", provider="docker", output=self_host_output)
    connector_catalog_payload = generate_connector_catalog(industry="local-business", output=connector_catalog_output)
    script_ui_payload = generate_script_ui_pack(flow_id="invoice-document-followup", output=script_ui_output)
    rag_payload = generate_knowledge_rag_pack(flow_id="ai-admin-faq-routing", output=rag_output)
    hooks_payload = generate_automation_hooks(flow_id="invoice-document-followup", output=hooks_output)
    governance_payload = generate_governance_pack(flow_id="invoice-document-followup", output=governance_output)

    assert skill_payload["status"] == "ready"
    assert (skill_output / "SKILL.md").exists()
    assert "Human approval" in (skill_output / "SKILL.md").read_text()
    assert (skill_output / "agent_team_roles.md").exists()
    assert "Claude Code" in (skill_output / "agent_usage.md").read_text()

    assert approval_payload["status"] == "ready"
    assert (approval_output / "approval_gate.json").exists()
    assert (approval_output / "human_review_queue.csv").exists()
    assert "booking confirmation" in (approval_output / "approval_policy.md").read_text()

    assert mcp_payload["status"] == "ready"
    assert (mcp_output / "mcp_connector_plan.md").exists()
    assert (mcp_output / "env_request_list.md").exists()
    assert "Do not paste secrets" in (mcp_output / "secrets_boundary.md").read_text()

    assert team_payload["status"] == "ready"
    assert (team_output / "agent_team_roles.md").exists()
    assert "sales scout" in (team_output / "agent_team_roles.md").read_text().lower()
    assert "handoff" in (team_output / "agent_handoff_protocol.md").read_text().lower()

    assert workflow_payload["status"] == "ready"
    assert (workflow_output / "workflow_explainer.html").exists()
    assert (workflow_output / "workflow_map.mmd").exists()
    assert "Before" in (workflow_output / "before_after.md").read_text()

    assert eval_payload["status"] == "ready"
    assert (eval_output / "eval_dataset.csv").exists()
    assert (eval_output / "improvement_loop.md").exists()
    assert "failure_modes" in (eval_output / "eval_loop.json").read_text()

    assert self_host_payload["status"] == "ready"
    assert (self_host_output / "docker_compose_plan.md").exists()
    assert "rollback" in (self_host_output / "self_host_runbook.md").read_text().lower()

    assert connector_catalog_payload["status"] == "ready"
    assert (connector_catalog_output / "connector_piece_catalog.md").exists()
    assert "Google Sheets" in (connector_catalog_output / "connector_piece_catalog.md").read_text()

    assert script_ui_payload["status"] == "ready"
    assert (script_ui_output / "script_to_ui_plan.md").exists()
    assert "webhook" in (script_ui_output / "ui_workflow_options.md").read_text().lower()

    assert rag_payload["status"] == "ready"
    assert (rag_output / "knowledge_base_pack.md").exists()
    assert "source citation" in (rag_output / "rag_answer_policy.md").read_text().lower()

    assert hooks_payload["status"] == "ready"
    assert (hooks_output / "automation_hooks.md").exists()
    assert "secret scan" in (hooks_output / "preflight_checks.md").read_text().lower()

    assert governance_payload["status"] == "ready"
    assert (governance_output / "governance_pack.md").exists()
    assert "approval audit" in (governance_output / "operational_governance.md").read_text().lower()


def test_generate_opportunity_catalog_creates_sales_catalog(tmp_path):
    output = tmp_path / "catalog"

    payload = generate_opportunity_catalog(industry="finance", output=output)

    assert payload["count"] >= 1
    assert (output / "opportunity_catalog.html").exists()
    assert (output / "opportunity_catalog.md").exists()
    html = (output / "opportunity_catalog.html").read_text()
    assert "Automation Opportunity Catalog" in html
    assert "Price Range" in html


def test_generate_recommended_flow_from_intake_creates_actionable_recommendation(tmp_path):
    output = tmp_path / "recommend"

    payload = generate_recommended_flow_from_intake(
        industry="finance",
        pain="missing invoice follow up takes too long",
        tools="Google Sheets Gmail Slack",
        monthly_items=80,
        output=output,
    )

    assert payload["recommended_flow"]["id"] == "invoice-document-followup"
    assert (output / "recommended_flow.md").exists()
    assert (output / "recommended_poc_scope.md").exists()
    assert "invoice-document-followup" in (output / "recommended_flow.md").read_text()
    assert "Paid PoC" in (output / "recommended_poc_scope.md").read_text()


def test_generate_share_check_blocks_secret_like_content(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "README.md").write_text("# Demo\n")
    (source / "secret.txt").write_text("token=sk-test-secret\n")
    output = tmp_path / "share-check"

    payload = generate_share_check(source=source, output=output)

    assert payload["status"] == "blocked"
    assert (output / "share_check.md").exists()
    assert "sk-" in (output / "share_check.md").read_text()


def test_generate_business_launch_pack_creates_beginner_business_proposal_system(tmp_path):
    output = tmp_path / "business-launch"

    payload = generate_business_launch_pack(
        industry="finance",
        client_type="local-business",
        niche="accounting",
        operator_level="beginner",
        output=output,
    )

    assert payload["status"] == "ready"
    assert payload["recommended_flow"]["id"] == "invoice-document-followup"
    assert payload["operator_level"] == "beginner"
    expected_files = [
        "START_HERE_BUSINESS_LAUNCH.md",
        "target_industry_playbook.md",
        "first_client_offer.md",
        "discovery_call_script.md",
        "proposal_builder.md",
        "pricing_and_scope_menu.md",
        "risk_boundary_sheet.md",
        "30_day_business_launch_plan.md",
        "client_pitch_email.md",
        "business_launch.json",
    ]
    for name in expected_files:
        assert (output / name).exists()
    start = (output / "START_HERE_BUSINESS_LAUNCH.md").read_text()
    assert "AIに慣れていない人" in start
    assert "first_client_offer.md" in start
    offer = (output / "first_client_offer.md").read_text()
    assert "企業向け自動化導入" in offer
    assert "Paid PoC" in offer
    risk = (output / "risk_boundary_sheet.md").read_text()
    assert "保証しないこと" in risk
    assert "本番送信" in risk


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
    start = parser.parse_args(["start"])
    assert start.command == "start"
    assert start.output == "my-first-automation"
    assert start.language == "ja"
    assert start.open_browser is False
    assert parser.parse_args(["start", "--open"]).open_browser is True
    assert parser.parse_args(["opportunity-catalog", "--output", "out"]).command == "opportunity-catalog"
    assert parser.parse_args(["recommend-flow", "--pain", "late invoices", "--output", "out"]).command == "recommend-flow"
    assert parser.parse_args(["share-check", "--source", "src", "--output", "out"]).command == "share-check"
    assert parser.parse_args(["business-launch", "--output", "out"]).command == "business-launch"


def test_main_runs_operator_commands(tmp_path, capsys):
    first_project = tmp_path / "first-project"
    assert main(["start", "--output", str(first_project)]) == 0
    assert (first_project / "START_HERE.html").exists()

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

    catalog = tmp_path / "catalog"
    assert main(["opportunity-catalog", "--industry", "finance", "--output", str(catalog)]) == 0

    recommend = tmp_path / "recommend"
    assert main(["recommend-flow", "--industry", "finance", "--pain", "missing invoice follow up", "--tools", "Google Sheets Gmail", "--output", str(recommend)]) == 0

    share_check = tmp_path / "share-check"
    assert main(["share-check", "--source", str(quickstart), "--output", str(share_check)]) == 0

    business_launch = tmp_path / "business-launch"
    assert main(["business-launch", "--industry", "finance", "--niche", "accounting", "--output", str(business_launch)]) == 0

    captured = capsys.readouterr()
    assert "start_here=" in captured.out
    assert "quickstart=" in captured.out
    assert "client_demo_package=" in captured.out
    assert "final_delivery_guide=" in captured.out
    assert "opportunity_catalog=" in captured.out
    assert "recommended_flow=" in captured.out
    assert "share_check=" in captured.out
    assert "business_launch=" in captured.out
    assert json.loads((package / "client_demo_manifest.json").read_text())["file_count"] >= 1


def test_main_start_can_open_generated_beginner_page(tmp_path, monkeypatch):
    opened = []
    output = tmp_path / "open-first-project"
    monkeypatch.setattr(cli_module.webbrowser, "open", lambda url: opened.append(url) or True)

    assert main(["start", "--open", "--output", str(output)]) == 0

    assert opened == [(output / "START_HERE.html").resolve().as_uri()]
