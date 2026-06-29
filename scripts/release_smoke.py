from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / ".tmp" / "release-smoke"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the public-readiness smoke suite.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Directory for smoke outputs.")
    parser.add_argument("--skip-github", action="store_true", help="Skip live GitHub API checks.")
    args = parser.parse_args()

    output = Path(args.output)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)

    env = _env_with_src()
    _run([sys.executable, "scripts/public_release_audit.py"], env=env)
    _run([sys.executable, "-m", "pytest", "-q"], env=env)
    _run([sys.executable, "scripts/run_all_demos.py"], env=env)
    _run([sys.executable, "-m", "ai_automation_kit.cli", "doctor", "--output", str(output / "doctor")], env=env)
    _run_flow_smoke(output, env)
    _run_beginner_sales_smoke(output, env)
    _run_operator_console_smoke(output, env)

    wheelhouse = output / "wheelhouse"
    _run([sys.executable, "-m", "pip", "wheel", ".", "-w", str(wheelhouse)], env=env)
    _verify_wheel_install(wheelhouse, output)

    if not args.skip_github:
        _run_github_smokes(output, env)

    print(f"release smoke passed: {output}")
    return 0


def _run_flow_smoke(output: Path, env: dict[str, str]) -> None:
    flow_output = output / "flow-invoice-document-followup"
    reception_output = output / "flow-ai-reception-line-inquiry"
    admin_output = output / "flow-ai-admin-faq-routing"
    sales_research_output = output / "flow-ai-sales-research-brief"
    _run([sys.executable, "-m", "ai_automation_kit.cli", "flows", "list"], env=env)
    _run([sys.executable, "-m", "ai_automation_kit.cli", "flows", "list", "--industry", "reception"], env=env)
    _run([sys.executable, "-m", "ai_automation_kit.cli", "flows", "list", "--industry", "admin"], env=env)
    _run([sys.executable, "-m", "ai_automation_kit.cli", "flows", "list", "--industry", "sales-research"], env=env)
    _run([sys.executable, "-m", "ai_automation_kit.cli", "flows", "show", "invoice-document-followup"], env=env)
    _run([sys.executable, "-m", "ai_automation_kit.cli", "flows", "show", "ai-reception-line-inquiry"], env=env)
    _run([sys.executable, "-m", "ai_automation_kit.cli", "flows", "show", "ai-admin-faq-routing"], env=env)
    _run([sys.executable, "-m", "ai_automation_kit.cli", "flows", "show", "ai-sales-research-brief"], env=env)
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "flows",
            "install",
            "invoice-document-followup",
            "--output",
            str(flow_output),
        ],
        env=env,
    )
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "flows",
            "install",
            "ai-reception-line-inquiry",
            "--output",
            str(reception_output),
        ],
        env=env,
    )
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "flows",
            "install",
            "ai-admin-faq-routing",
            "--output",
            str(admin_output),
        ],
        env=env,
    )
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "flows",
            "install",
            "ai-sales-research-brief",
            "--output",
            str(sales_research_output),
        ],
        env=env,
    )
    _run([sys.executable, "-m", "ai_automation_kit.cli", "flows", "validate", str(flow_output)], env=env)
    _run([sys.executable, "-m", "ai_automation_kit.cli", "flows", "validate", str(reception_output)], env=env)
    _run([sys.executable, "-m", "ai_automation_kit.cli", "flows", "validate", str(admin_output)], env=env)
    _run([sys.executable, "-m", "ai_automation_kit.cli", "flows", "validate", str(sales_research_output)], env=env)
    _run([sys.executable, "-m", "ai_automation_kit.cli", "flows", "run", str(flow_output)], env=env)
    _run([sys.executable, "-m", "ai_automation_kit.cli", "flows", "approve", str(flow_output), "--approver", "release@example.com"], env=env)
    _run([sys.executable, "scripts/run_dry_run.py"], cwd=flow_output, env=env)
    _run([sys.executable, "scripts/run_automation.py"], cwd=flow_output, env=env)
    _run([sys.executable, "scripts/approve_all.py", "--approver", "release@example.com"], cwd=flow_output, env=env)
    _run([sys.executable, "-m", "pytest", "tests/test_flow_contract.py", "-q"], cwd=flow_output, env=env)
    _require_file(flow_output / ".env.example")
    _require_file(flow_output / "config" / "connectors.json")
    _require_file(flow_output / "docs" / "SYSTEM_RUNBOOK.md")
    _require_file(flow_output / "flow.yaml")
    _require_file(flow_output / "workflow_map.mmd")
    _require_file(flow_output / "ai_action_procedure.md")
    _require_file(flow_output / "setup_requirements.md")
    _require_file(flow_output / "client_setup_request.md")
    _require_file(flow_output / "connector_status.md")
    _require_file(flow_output / "monetization_plan.md")
    _require_file(flow_output / "operator_ui" / "index.html")
    _require_file(flow_output / "scripts" / "run_dry_run.py")
    _require_file(flow_output / "automation_output" / "work_queue.csv")
    _require_file(flow_output / "automation_output" / "draft_outputs.md")
    _require_file(flow_output / "automation_output" / "approval_queue.csv")
    _require_file(flow_output / "automation_output" / "status_report.md")
    _require_file(flow_output / "automation_output" / "run_log.json")
    _require_file(flow_output / "automation_output" / "approved_actions.csv")
    _require_file(flow_output / "local_outbox" / "email_drafts.md")
    _require_file(flow_output / "local_outbox" / "slack_messages.md")
    _require_file(reception_output / "setup_requirements.md")
    _require_file(reception_output / "ai_action_procedure.md")
    _require_file(reception_output / "client_setup_request.md")
    _require_file(reception_output / "connector_status.md")
    _require_file(reception_output / "monetization_plan.md")
    _require_file(reception_output / "operator_ui" / "index.html")
    _require_file(admin_output / "ai_action_procedure.md")
    _require_file(admin_output / "setup_requirements.md")
    _require_file(admin_output / "operator_ui" / "index.html")
    _require_file(sales_research_output / "ai_action_procedure.md")
    _require_file(sales_research_output / "setup_requirements.md")
    _require_file(sales_research_output / "operator_ui" / "index.html")


def _run_beginner_sales_smoke(output: Path, env: dict[str, str]) -> None:
    beginner_output = output / "beginner-sales-accounting"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "beginner-sales",
            "--flow-id",
            "invoice-document-followup",
            "--client-type",
            "local-business",
            "--niche",
            "accounting",
            "--output",
            str(beginner_output),
        ],
        env=env,
    )
    _require_file(beginner_output / "README.md")
    _require_file(beginner_output / "START_HERE_FOR_SIDE_BUSINESS.md")
    _require_file(beginner_output / "flow_gallery.html")
    _require_file(beginner_output / "selected_flow_demo.html")
    _require_file(beginner_output / "proposal_one_pager.md")
    _require_file(beginner_output / "roi_simple_calculator.csv")
    _require_file(beginner_output / "three_day_poc_plan.md")
    _require_file(beginner_output / "client_delivery_checklist.md")
    _require_file(beginner_output / "differentiation_matrix.md")


def _run_operator_console_smoke(output: Path, env: dict[str, str]) -> None:
    quickstart_output = output / "quickstart-accounting"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "quickstart",
            "--flow-id",
            "invoice-document-followup",
            "--client-type",
            "local-business",
            "--niche",
            "accounting",
            "--output",
            str(quickstart_output),
        ],
        env=env,
    )
    _require_file(quickstart_output / "START_HERE.md")
    _require_file(quickstart_output / "flow_project" / "flow.yaml")
    _require_file(quickstart_output / "beginner_sales" / "selected_flow_demo.html")
    _require_file(quickstart_output / "demo_site" / "index.html")

    guide_output = output / "flow-guide-finance"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "flow-guide",
            "--industry",
            "finance",
            "--niche",
            "accounting",
            "--output",
            str(guide_output),
        ],
        env=env,
    )
    _require_file(guide_output / "recommended_flows.md")

    catalog_output = output / "opportunity-catalog"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "opportunity-catalog",
            "--industry",
            "finance",
            "--output",
            str(catalog_output),
        ],
        env=env,
    )
    _require_file(catalog_output / "opportunity_catalog.html")
    _require_file(catalog_output / "opportunity_catalog.md")

    recommend_output = output / "recommend-flow"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "recommend-flow",
            "--industry",
            "finance",
            "--pain",
            "missing invoice follow up",
            "--tools",
            "Google Sheets Gmail",
            "--monthly-items",
            "80",
            "--output",
            str(recommend_output),
        ],
        env=env,
    )
    _require_file(recommend_output / "recommended_flow.md")
    _require_file(recommend_output / "recommended_poc_scope.md")

    business_launch_output = output / "business-launch"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "business-launch",
            "--industry",
            "finance",
            "--client-type",
            "local-business",
            "--niche",
            "accounting",
            "--output",
            str(business_launch_output),
        ],
        env=env,
    )
    _require_file(business_launch_output / "START_HERE_BUSINESS_LAUNCH.md")
    _require_file(business_launch_output / "first_client_offer.md")
    _require_file(business_launch_output / "risk_boundary_sheet.md")

    side_hustle_blueprints_output = output / "side-hustle-blueprints"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "side-hustle-blueprints",
            "--industry",
            "local-business",
            "--operator-level",
            "beginner",
            "--output",
            str(side_hustle_blueprints_output),
        ],
        env=env,
    )
    _require_file(side_hustle_blueprints_output / "START_HERE_SIDE_HUSTLE_BLUEPRINTS.md")
    _require_file(side_hustle_blueprints_output / "side_hustle_blueprints.md")
    _require_file(side_hustle_blueprints_output / "side_hustle_blueprints.html")
    _require_file(side_hustle_blueprints_output / "first_client_picker.md")
    _require_file(side_hustle_blueprints_output / "client_intake_questions.md")
    _require_file(side_hustle_blueprints_output / "implementation_paths.md")
    _require_file(side_hustle_blueprints_output / "risk_boundaries.md")
    _require_file(side_hustle_blueprints_output / "ai_agent_handoff.md")

    command_center_output = output / "command-center"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "command-center",
            "--language",
            "both",
            "--output",
            str(command_center_output),
        ],
        env=env,
    )
    _require_file(command_center_output / "START_HERE_COMMAND_CENTER.md")
    _require_file(command_center_output / "COMMAND_CENTER.md")
    _require_file(command_center_output / "COMMAND_CENTER.ja.md")
    _require_file(command_center_output / "command_center.html")
    _require_file(command_center_output / "next_step_decision_tree.md")

    skill_pack_output = output / "skill-pack"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "skill-pack",
            "--flow-id",
            "invoice-document-followup",
            "--agent",
            "codex",
            "--output",
            str(skill_pack_output),
        ],
        env=env,
    )
    _require_file(skill_pack_output / "SKILL.md")
    _require_file(skill_pack_output / "agent_usage.md")
    _require_file(skill_pack_output / "agent_team_roles.md")

    approval_gate_output = output / "approval-gate"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "approval-gate",
            "--flow-id",
            "invoice-document-followup",
            "--output",
            str(approval_gate_output),
        ],
        env=env,
    )
    _require_file(approval_gate_output / "approval_gate.json")
    _require_file(approval_gate_output / "approval_policy.md")
    _require_file(approval_gate_output / "human_review_queue.csv")

    mcp_connector_output = output / "mcp-connector-plan"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "mcp-connector-plan",
            "--flow-id",
            "invoice-document-followup",
            "--connectors",
            "gmail,google-sheets,slack",
            "--output",
            str(mcp_connector_output),
        ],
        env=env,
    )
    _require_file(mcp_connector_output / "mcp_connector_plan.md")
    _require_file(mcp_connector_output / "env_request_list.md")
    _require_file(mcp_connector_output / "secrets_boundary.md")

    agent_team_output = output / "agent-team"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "agent-team",
            "--flow-id",
            "invoice-document-followup",
            "--output",
            str(agent_team_output),
        ],
        env=env,
    )
    _require_file(agent_team_output / "agent_team_roles.md")
    _require_file(agent_team_output / "agent_handoff_protocol.md")

    workflow_explainer_output = output / "workflow-explainer"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "workflow-explainer",
            "--flow-id",
            "invoice-document-followup",
            "--audience",
            "client",
            "--output",
            str(workflow_explainer_output),
        ],
        env=env,
    )
    _require_file(workflow_explainer_output / "workflow_explainer.html")
    _require_file(workflow_explainer_output / "workflow_map.mmd")
    _require_file(workflow_explainer_output / "before_after.md")

    eval_loop_output = output / "eval-loop"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "eval-loop",
            "--flow-id",
            "invoice-document-followup",
            "--metric",
            "hours_saved",
            "--output",
            str(eval_loop_output),
        ],
        env=env,
    )
    _require_file(eval_loop_output / "eval_loop.json")
    _require_file(eval_loop_output / "eval_dataset.csv")
    _require_file(eval_loop_output / "improvement_loop.md")

    self_host_output = output / "self-host-pack"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "self-host-pack",
            "--flow-id",
            "invoice-document-followup",
            "--provider",
            "docker",
            "--output",
            str(self_host_output),
        ],
        env=env,
    )
    _require_file(self_host_output / "self_host_runbook.md")
    _require_file(self_host_output / "docker_compose_plan.md")

    connector_catalog_output = output / "connector-catalog"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "connector-catalog",
            "--industry",
            "local-business",
            "--output",
            str(connector_catalog_output),
        ],
        env=env,
    )
    _require_file(connector_catalog_output / "connector_piece_catalog.md")
    _require_file(connector_catalog_output / "connector_selection_matrix.csv")

    script_ui_output = output / "script-ui-pack"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "script-ui-pack",
            "--flow-id",
            "invoice-document-followup",
            "--output",
            str(script_ui_output),
        ],
        env=env,
    )
    _require_file(script_ui_output / "script_to_ui_plan.md")
    _require_file(script_ui_output / "ui_workflow_options.md")

    knowledge_rag_output = output / "knowledge-rag-pack"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "knowledge-rag-pack",
            "--flow-id",
            "ai-admin-faq-routing",
            "--output",
            str(knowledge_rag_output),
        ],
        env=env,
    )
    _require_file(knowledge_rag_output / "knowledge_base_pack.md")
    _require_file(knowledge_rag_output / "rag_answer_policy.md")

    automation_hooks_output = output / "automation-hooks"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "automation-hooks",
            "--flow-id",
            "invoice-document-followup",
            "--output",
            str(automation_hooks_output),
        ],
        env=env,
    )
    _require_file(automation_hooks_output / "automation_hooks.md")
    _require_file(automation_hooks_output / "preflight_checks.md")

    governance_output = output / "governance-pack"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "governance-pack",
            "--flow-id",
            "invoice-document-followup",
            "--output",
            str(governance_output),
        ],
        env=env,
    )
    _require_file(governance_output / "governance_pack.md")
    _require_file(governance_output / "operational_governance.md")
    _require_file(governance_output / "security_review_checklist.md")

    website_side_hustle_output = output / "website-side-hustle"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "website-side-hustle",
            "--industry",
            "hospitality",
            "--client-type",
            "local-business",
            "--niche",
            "tourism-hotel",
            "--output",
            str(website_side_hustle_output),
        ],
        env=env,
    )
    _require_file(website_side_hustle_output / "START_HERE_WEBSITE_SIDE_HUSTLE.md")
    _require_file(website_side_hustle_output / "ai_agent_handoff.md")
    _require_file(website_side_hustle_output / "client_kickoff_questions.md")
    _require_file(website_side_hustle_output / "beginner_human_guide.md")
    _require_file(website_side_hustle_output / "beginner_human_guide.ja.md")
    _require_file(website_side_hustle_output / "reservation_inquiry_system.md")
    _require_file(website_side_hustle_output / "delivery_acceptance_checklist.md")
    _require_file(website_side_hustle_output / "client_handoff_note.md")
    _require_file(website_side_hustle_output / "inquiry_dashboard.html")
    _require_file(website_side_hustle_output / "sample_site" / "index.html")

    guided_setup_output = output / "guided-setup-ai-reception"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
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
            str(guided_setup_output),
        ],
        env=env,
    )
    _require_file(guided_setup_output / "START_HERE_GUIDED_SETUP.md")
    _require_file(guided_setup_output / "guided_setup_questions.md")
    _require_file(guided_setup_output / "guided_setup_answers.example.json")
    _require_file(guided_setup_output / "missing_inputs.md")
    _require_file(guided_setup_output / "local_setup_plan.md")
    _require_file(guided_setup_output / "cloud_setup_plan.md")
    _require_file(guided_setup_output / "env_values_needed.md")
    _require_file(guided_setup_output / "client_request_list.md")
    _require_file(guided_setup_output / "ai_agent_instruction.md")
    _require_file(guided_setup_output / "readiness_score.json")
    _require_file(guided_setup_output / "next_action.md")

    guided_review_output = output / "guided-review-ai-reception"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "guided-review",
            "--answers",
            str(guided_setup_output / "guided_setup_answers.example.json"),
            "--output",
            str(guided_review_output),
        ],
        env=env,
    )
    _require_file(guided_review_output / "START_HERE_GUIDED_REVIEW.md")
    _require_file(guided_review_output / "setup_readiness_report.md")
    _require_file(guided_review_output / "automation_build_plan.md")
    _require_file(guided_review_output / "client_missing_items_email.md")
    _require_file(guided_review_output / "cloud_provider_decision.md")
    _require_file(guided_review_output / "local_vs_cloud_decision.md")
    _require_file(guided_review_output / "ai_agent_handoff_prompt.md")
    _require_file(guided_review_output / "next_commands.md")
    _require_file(guided_review_output / "guided_review.json")

    cloud_plan_output = output / "cloud-plan-aws-scheduled-job"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
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
            str(cloud_plan_output),
        ],
        env=env,
    )
    _require_file(cloud_plan_output / "START_HERE_CLOUD_PLAN.md")
    _require_file(cloud_plan_output / "cloud_provider_matrix.md")
    _require_file(cloud_plan_output / "workload_architecture.md")
    _require_file(cloud_plan_output / "runtime_choice.md")
    _require_file(cloud_plan_output / "secrets_and_env.md")
    _require_file(cloud_plan_output / "network_and_domain.md")
    _require_file(cloud_plan_output / "deploy_runbook.md")
    _require_file(cloud_plan_output / "operations_runbook.md")
    _require_file(cloud_plan_output / "cost_guardrails.md")
    _require_file(cloud_plan_output / "compliance_data_boundary.md")
    _require_file(cloud_plan_output / "incident_rollback.md")
    _require_file(cloud_plan_output / "human_approval_required.md")
    _require_file(cloud_plan_output / "cloud_plan.json")

    grill_me_output = output / "grill-me-invoice-cloud"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
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
            str(grill_me_output),
        ],
        env=env,
    )
    _require_file(grill_me_output / "START_HERE_GRILL_ME.md")
    _require_file(grill_me_output / "questions_to_answer.md")
    _require_file(grill_me_output / "client_interview_grill.md")
    _require_file(grill_me_output / "cloud_readiness_grill.md")
    _require_file(grill_me_output / "risk_grill.md")
    _require_file(grill_me_output / "proposal_grill.md")
    _require_file(grill_me_output / "ai_agent_prompt.md")
    _require_file(grill_me_output / "grill_me.json")

    connector_output = output / "connector-doctor"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "connector-doctor",
            "--project",
            str(quickstart_output / "flow_project"),
            "--output",
            str(connector_output),
        ],
        env=env,
    )
    _require_file(connector_output / "connector_doctor.md")

    _run([sys.executable, "-m", "ai_automation_kit.cli", "flows", "run", str(quickstart_output / "flow_project")], env=env)
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "flows",
            "approve",
            str(quickstart_output / "flow_project"),
            "--approver",
            "release@example.com",
        ],
        env=env,
    )
    report_output = output / "client-report"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "client-report",
            "--flow-project",
            str(quickstart_output / "flow_project"),
            "--output",
            str(report_output),
        ],
        env=env,
    )
    _require_file(report_output / "client_report.md")
    _require_file(report_output / "client_report.html")

    site_output = output / "operator-demo-site"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "demo-site",
            "--source",
            str(quickstart_output),
            "--output",
            str(site_output),
        ],
        env=env,
    )
    _require_file(site_output / "index.html")

    bundle_output = output / "install-bundle"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "install-bundle",
            "--flow-id",
            "invoice-document-followup",
            "--client-type",
            "local-business",
            "--niche",
            "accounting",
            "--output",
            str(bundle_output),
        ],
        env=env,
    )
    _require_file(bundle_output / "bundle_index.md")
    _require_file(bundle_output / "client_ready" / "maintenance_plan.md")

    package_output = output / "client-demo-package"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "package-client-demo",
            "--source",
            str(quickstart_output),
            "--output",
            str(package_output),
        ],
        env=env,
    )
    _require_file(package_output / "client_demo_manifest.json")
    _require_file(package_output / "client_demo_package.zip")

    share_check_output = output / "share-check"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "share-check",
            "--source",
            str(quickstart_output),
            "--output",
            str(share_check_output),
        ],
        env=env,
    )
    _require_file(share_check_output / "share_check.md")
    _require_file(share_check_output / "share_check.json")

    complete_output = output / "complete-accounting"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "complete-workspace",
            "--flow-id",
            "invoice-document-followup",
            "--client-type",
            "local-business",
            "--niche",
            "accounting",
            "--approver",
            "release@example.com",
            "--output",
            str(complete_output),
        ],
        env=env,
    )
    _require_file(complete_output / "FINAL_DELIVERY_GUIDE.md")
    _require_file(complete_output / "completion_checklist.md")
    _require_file(complete_output / "delivery_manifest.json")
    _require_file(complete_output / "revenue_readiness_scorecard.md")
    _require_file(complete_output / "sales_closing_script.md")
    _require_file(complete_output / "paid_poc_scope.md")
    _require_file(complete_output / "value_measurement_sheet.csv")
    _require_file(complete_output / "pre_contract_checklist.md")
    _require_file(complete_output / "client_proposal_email.md")
    _require_file(complete_output / "first_30_days_plan.md")
    _require_file(complete_output / "proof_of_value_template.md")
    _require_file(complete_output / "oss_pattern_benchmark.md")
    _require_file(complete_output / "integration_backlog.md")
    _require_file(complete_output / "deployment_options.md")
    _require_file(complete_output / "production_observability_plan.md")
    _require_file(complete_output / "automation_opportunity_scorecard.csv")
    _require_file(complete_output / "client_onboarding_form.md")
    _require_file(complete_output / "go_live_decision.md")
    _require_file(complete_output / "client_command_center.html")
    _require_file(complete_output / "side_business_starter_10.md")
    _require_file(complete_output / "before_after_demo.html")
    _require_file(complete_output / "business_launch" / "START_HERE_BUSINESS_LAUNCH.md")
    _require_file(complete_output / "business_launch" / "first_client_offer.md")
    _require_file(complete_output / "quickstart" / "flow_project" / "automation_output" / "run_log.json")
    _require_file(complete_output / "quickstart" / "flow_project" / "local_outbox" / "email_drafts.md")
    _require_file(complete_output / "connector_doctor" / "connector_doctor.md")
    _require_file(complete_output / "client_report" / "client_report.html")
    _require_file(complete_output / "client_demo_package" / "client_demo_package.zip")
    _require_file(complete_output / "flow_exports" / "n8n" / "n8n_workflow.json")
    _require_file(complete_output / "flow_exports" / "activepieces" / "activepieces_flow.json")
    _require_file(complete_output / "flow_exports" / "windmill" / "windmill_flow.yaml")
    _require_file(complete_output / "deployment_packs" / "coolify" / "deployment_pack.json")
    _require_file(complete_output / "deployment_packs" / "cloudflare-agents" / "deployment_pack.json")
    _require_file(complete_output / "deployment_packs" / "supabase" / "deployment_pack.json")
    _require_file(complete_output / "runtime_safety" / "runtime_safety.json")
    _require_file(complete_output / "secrets_bootstrap" / "secrets_manifest.json")
    _require_file(complete_output / "document_intake" / "document_pipeline.md")
    _require_file(complete_output / "observability_pack" / "observability_pack.json")
    _require_file(complete_output / "state_backend" / "state_backend.json")

    flow_export_output = output / "flow-export-n8n"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "flow-export",
            "--flow-id",
            "invoice-document-followup",
            "--target",
            "n8n",
            "--output",
            str(flow_export_output),
        ],
        env=env,
    )
    _require_file(flow_export_output / "n8n_workflow.json")

    deployment_pack_output = output / "deployment-coolify"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "deployment-pack",
            "--flow-id",
            "invoice-document-followup",
            "--provider",
            "coolify",
            "--connectors",
            "gmail,google-sheets",
            "--output",
            str(deployment_pack_output),
        ],
        env=env,
    )
    _require_file(deployment_pack_output / "docker-compose.yml")

    runtime_safety_output = output / "runtime-safety"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "runtime-safety",
            "--flow-id",
            "invoice-document-followup",
            "--output",
            str(runtime_safety_output),
        ],
        env=env,
    )
    _require_file(runtime_safety_output / "retry_policy.json")

    secrets_output = output / "secrets-bootstrap"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "secrets-bootstrap",
            "--flow-id",
            "invoice-document-followup",
            "--provider",
            "infisical",
            "--connectors",
            "gmail,google-sheets",
            "--output",
            str(secrets_output),
        ],
        env=env,
    )
    _require_file(secrets_output / "secrets_manifest.json")

    document_output = output / "document-intake"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "document-intake",
            "--flow-id",
            "invoice-document-followup",
            "--mode",
            "advanced",
            "--output",
            str(document_output),
        ],
        env=env,
    )
    _require_file(document_output / "docling_config.json")

    observability_output = output / "observability-pack"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "observability-pack",
            "--flow-id",
            "invoice-document-followup",
            "--output",
            str(observability_output),
        ],
        env=env,
    )
    _require_file(observability_output / "langfuse_env.example")

    state_output = output / "state-backend"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "state-backend",
            "--flow-id",
            "invoice-document-followup",
            "--backend",
            "supabase",
            "--output",
            str(state_output),
        ],
        env=env,
    )
    _require_file(state_output / "supabase_schema.sql")


def _run_github_smokes(output: Path, env: dict[str, str]) -> None:
    onboard_output = output / "onboard-operations"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "onboard",
            "--business-area",
            "operations",
            "--limit",
            "1",
            "--output",
            str(onboard_output),
            "--create-offer-pack",
        ],
        env=env,
    )
    _require_file(onboard_output / "onboarding_summary.md")
    _require_file(onboard_output / "onboarding_summary.json")
    _require_file(onboard_output / "doctor" / "doctor_report.md")
    _require_file(onboard_output / "github_discover_config.json")
    _require_file(onboard_output / "offer_pack" / "README.md")
    _require_file(onboard_output / "offer_pack" / "proposal.md")
    _require_file(onboard_output / "offer_pack" / "statement_of_work.md")
    _require_file(onboard_output / "offer_pack" / "pricing_model.md")

    offer_output = output / "offer-pack-operations"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "offer-pack",
            "--business-area",
            "operations",
            "--client-type",
            "small-business",
            "--source-output",
            str(onboard_output),
            "--output",
            str(offer_output),
        ],
        env=env,
    )
    _require_file(offer_output / "README.md")
    _require_file(offer_output / "service_catalog.md")
    _require_file(offer_output / "client_discovery_questions.md")
    _require_file(offer_output / "proposal.md")
    _require_file(offer_output / "statement_of_work.md")
    _require_file(offer_output / "pricing_model.md")
    _require_file(offer_output / "risk_boundaries.md")

    client_ready_output = output / "client-ready-accounting"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "client-ready",
            "--business-area",
            "operations",
            "--client-type",
            "local-business",
            "--niche",
            "accounting",
            "--source-output",
            str(onboard_output),
            "--output",
            str(client_ready_output),
        ],
        env=env,
    )
    _require_file(client_ready_output / "README.md")
    _require_file(client_ready_output / "client_intake.md")
    _require_file(client_ready_output / "roi_calculator.csv")
    _require_file(client_ready_output / "proposal_tiers.md")
    _require_file(client_ready_output / "implementation_readiness_score.json")
    _require_file(client_ready_output / "security_review.md")
    _require_file(client_ready_output / "tool_stack_recommendation.md")
    _require_file(client_ready_output / "maintenance_plan.md")
    _require_file(client_ready_output / "marketplace_profile.md")
    _require_file(client_ready_output / "case_study_template.md")

    adapter_output = output / "github-operations"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "github-discover",
            "--business-area",
            "operations",
            "--limit",
            "2",
            "--output",
            str(adapter_output),
        ],
        env=env,
    )
    _require_file(adapter_output / "run_summary.md")
    _require_file(adapter_output / "run_summary.json")
    _require_file(adapter_output / "executive_decision_brief.md")
    _require_file(adapter_output / "executive_decision_brief.json")
    _require_file(adapter_output / "pilot_scorecard.md")
    _require_file(adapter_output / "pilot_scorecard.json")
    _require_file(adapter_output / "pilot_scorecard.csv")
    _require_file(adapter_output / "enterprise_readiness.md")
    _require_file(adapter_output / "enterprise_readiness.json")
    _require_file(adapter_output / "value_realization_plan.md")
    _require_file(adapter_output / "value_realization_plan.json")
    _require_file(adapter_output / "value_measurement_report.md")
    _require_file(adapter_output / "value_measurement_report.json")
    _require_file(adapter_output / "stakeholder_rollout_map.md")
    _require_file(adapter_output / "stakeholder_rollout_map.json")
    _require_file(adapter_output / "risk_exception_register.md")
    _require_file(adapter_output / "risk_exception_register.json")
    _require_file(adapter_output / "operational_audit_plan.md")
    _require_file(adapter_output / "operational_audit_plan.json")
    _run([sys.executable, "adapter_starter/smoke_test.py"], cwd=adapter_output, env=env)

    review_output = output / "github-support"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "github-discover",
            "--business-area",
            "support",
            "--limit",
            "2",
            "--output",
            str(review_output),
        ],
        env=env,
    )
    _require_file(review_output / "run_summary.md")
    _require_file(review_output / "run_summary.json")
    _require_file(review_output / "executive_decision_brief.md")
    _require_file(review_output / "executive_decision_brief.json")
    _require_file(review_output / "pilot_scorecard.md")
    _require_file(review_output / "pilot_scorecard.json")
    _require_file(review_output / "pilot_scorecard.csv")
    _require_file(review_output / "enterprise_readiness.md")
    _require_file(review_output / "enterprise_readiness.json")
    _require_file(review_output / "value_realization_plan.md")
    _require_file(review_output / "value_realization_plan.json")
    _require_file(review_output / "value_measurement_report.md")
    _require_file(review_output / "value_measurement_report.json")
    _require_file(review_output / "stakeholder_rollout_map.md")
    _require_file(review_output / "stakeholder_rollout_map.json")
    _require_file(review_output / "risk_exception_register.md")
    _require_file(review_output / "risk_exception_register.json")
    _require_file(review_output / "operational_audit_plan.md")
    _require_file(review_output / "operational_audit_plan.json")
    _require_file(review_output / "manual_review_pack.md")
    _require_file(review_output / "manual_review_pack.json")


def _env_with_src() -> dict[str, str]:
    env = os.environ.copy()
    src_path = str(ROOT / "src")
    env["PYTHONPATH"] = src_path if not env.get("PYTHONPATH") else f"{src_path}{os.pathsep}{env['PYTHONPATH']}"
    return env


def _verify_wheel_install(wheelhouse: Path, output: Path) -> None:
    wheels = sorted(wheelhouse.glob("ai_automation_starter_kit-*.whl"))
    if not wheels:
        raise FileNotFoundError(f"No ai_automation_starter_kit wheel found in {wheelhouse}")

    venv_dir = output / "install-venv"
    _run([sys.executable, "-m", "venv", str(venv_dir)], env=os.environ.copy())
    python_bin = _venv_python(venv_dir)
    _run([str(python_bin), "-m", "pip", "install", str(wheels[-1])], env=os.environ.copy())
    cli_bin = _venv_console_script(venv_dir, "ai-automation-kit")
    _run([str(cli_bin), "--version"], env=os.environ.copy())
    _run([str(cli_bin), "doctor", "--output", str(output / "installed-doctor")], env=os.environ.copy())


def _venv_python(venv_dir: Path) -> Path:
    posix_python = venv_dir / "bin" / "python"
    if posix_python.exists():
        return posix_python
    return venv_dir / "Scripts" / "python.exe"


def _venv_console_script(venv_dir: Path, name: str) -> Path:
    posix_script = venv_dir / "bin" / name
    if posix_script.exists():
        return posix_script
    return venv_dir / "Scripts" / f"{name}.exe"


def _run(command: list[str], env: dict[str, str], cwd: Path | None = None) -> None:
    print("$ " + " ".join(command))
    subprocess.run(command, cwd=cwd or ROOT, env=env, check=True)


def _require_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Expected release smoke artifact was not created: {path}")


if __name__ == "__main__":
    raise SystemExit(main())
