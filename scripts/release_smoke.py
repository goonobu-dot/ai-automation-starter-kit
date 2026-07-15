from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import queue
import re
import signal
import shlex
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / ".tmp" / "release-smoke"
OFFICE_WORKSPACE_PACK_IDS = [
    "monthly-report",
    "inquiry-daily",
    "sales-daily",
    "finance-daily",
    "project-daily",
    "attendance-daily",
    "meeting-actions-daily",
    "expense-check-daily",
    "invoice-order-check-daily",
    "internal-requests-daily",
    "executive-digest-daily",
    "handover-deadline-daily",
    "employee-lifecycle-daily",
    "contract-intake-daily",
    "quote-comparison-daily",
    "compliance-deadline-daily",
    "spreadsheet-reconciliation-daily",
    "policy-change-impact-daily",
    "quality-incident-capa-daily",
    "vendor-onboarding-daily",
    "access-review-daily",
    "grant-packet-daily",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the public-readiness smoke suite.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Directory for smoke outputs.")
    parser.add_argument("--skip-github", action="store_true", help="Skip live GitHub API checks.")
    args = parser.parse_args()

    # Installed binaries are invoked while cwd points inside the smoke output.
    # Resolve once so a caller-supplied relative output cannot turn those
    # executable paths into invalid cwd-relative paths.
    output = Path(args.output).resolve()
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
    report_output = output / "flow-daily-monthly-report-automation"
    _run([sys.executable, "-m", "ai_automation_kit.cli", "flows", "list"], env=env)
    _run([sys.executable, "-m", "ai_automation_kit.cli", "flows", "list", "--industry", "reception"], env=env)
    _run([sys.executable, "-m", "ai_automation_kit.cli", "flows", "list", "--industry", "admin"], env=env)
    _run([sys.executable, "-m", "ai_automation_kit.cli", "flows", "list", "--industry", "sales-research"], env=env)
    _run([sys.executable, "-m", "ai_automation_kit.cli", "flows", "show", "invoice-document-followup"], env=env)
    _run([sys.executable, "-m", "ai_automation_kit.cli", "flows", "show", "ai-reception-line-inquiry"], env=env)
    _run([sys.executable, "-m", "ai_automation_kit.cli", "flows", "show", "ai-admin-faq-routing"], env=env)
    _run([sys.executable, "-m", "ai_automation_kit.cli", "flows", "show", "ai-sales-research-brief"], env=env)
    _run([sys.executable, "-m", "ai_automation_kit.cli", "flows", "show", "daily-monthly-report-automation"], env=env)
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
            "daily-monthly-report-automation",
            "--output",
            str(report_output),
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
    _run([sys.executable, "-m", "ai_automation_kit.cli", "flows", "validate", str(report_output)], env=env)
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
    _require_file(report_output / "ai_action_procedure.md")
    _require_file(report_output / "setup_requirements.md")
    _require_file(report_output / "operator_ui" / "index.html")


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
    first_project_output = output / "first-project-source-smoke"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "start",
            "--language",
            "en",
            "--output",
            str(first_project_output),
        ],
        env=env,
    )
    _require_file(first_project_output / "START_HERE.html")
    _require_file(first_project_output / "AI_NEXT_STEP.md")
    _require_file(first_project_output / "01_CLIENT_INPUT" / "README.txt")
    _require_file(first_project_output / "first_project.json")

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

    report_automation_output = output / "report-automation-monthly"
    _run(
        [
            sys.executable,
            "-m",
            "ai_automation_kit.cli",
            "report-automation",
            "--report-type",
            "monthly",
            "--client-type",
            "local-business",
            "--niche",
            "construction",
            "--output",
            str(report_automation_output),
        ],
        env=env,
    )
    _require_file(report_automation_output / "START_HERE_REPORT_AUTOMATION.md")
    _require_file(report_automation_output / "workspace_map.md")
    _require_file(report_automation_output / "ai_agent_prompt.md")
    _require_file(report_automation_output / "grill_me_report_questions.md")
    _require_file(report_automation_output / "demo_report_automation.html")
    _require_file(report_automation_output / "05_grill_me_questions" / "questions.md")
    _require_file(report_automation_output / "06_drafts" / "monthly_report_draft.md")
    _require_file(report_automation_output / "07_approval" / "approval_checklist.md")

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
    wheelhouse = wheelhouse.resolve()
    output = output.resolve()
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
    _run_report_wizard_installed_smoke(cli_bin, python_bin, output)
    _run_office_workspace_installed_smoke(cli_bin, python_bin, output)
    _run_autopilot_proof_lab_installed_smoke(cli_bin, output)
    _run_first_project_installed_smoke(cli_bin, output)


def _venv_python(venv_dir: Path) -> Path:
    posix_python = venv_dir / "bin" / "python"
    if posix_python.exists():
        return posix_python
    return venv_dir / "Scripts" / "python.exe"


def _run_first_project_installed_smoke(cli_bin: Path, output: Path) -> None:
    workspace = output / "installed-first-project"
    _run(
        [
            str(cli_bin),
            "start",
            "--language",
            "en",
            "--output",
            str(workspace),
        ],
        env=_isolated_installed_env(cli_bin),
    )
    _require_file(workspace / "START_HERE.html")
    _require_file(workspace / "AI_NEXT_STEP.md")
    _require_file(workspace / "01_CLIENT_INPUT" / "README.txt")
    _require_file(workspace / "first_project.json")


def _run_autopilot_proof_lab_installed_smoke(cli_bin: Path, output: Path) -> None:
    env = _isolated_installed_env(cli_bin)
    fixture = output / "installed-proof-lab-fixture"
    fixture.mkdir(parents=True, exist_ok=True)
    workspace = output / "installed-proof-lab"
    evidence = fixture / "approved-policy.md"
    case_input = fixture / "input.json"
    expected = fixture / "expected.json"
    proposed = fixture / "proposed.json"
    evidence.write_text("# Approved policy\nDraft locally and keep human approval.\n", encoding="utf-8")
    case_input.write_text('{"invoice_id":"INV-001","amount":1200}\n', encoding="utf-8")
    expected.write_text('{"route":"standard","decision":"draft"}\n', encoding="utf-8")
    proposed.write_text('{"route":"standard","decision":"draft"}\n', encoding="utf-8")

    commands = [
        [
            str(cli_bin),
            "autopilot-proof-lab",
            "init",
            "--workspace",
            str(workspace),
            "--pack-id",
            "invoice-order-check-daily",
            "--organization",
            "Release Smoke Co",
            "--objective",
            "Verify the installed advisory proof lab",
            "--requested-level",
            "L3",
            "--language",
            "en",
        ],
        [
            str(cli_bin),
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
            "Release QA",
        ],
        [
            str(cli_bin),
            "autopilot-proof-lab",
            "add-case",
            "--workspace",
            str(workspace),
            "--case-id",
            "normal-001",
            "--input",
            str(case_input),
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
        ],
        [str(cli_bin), "autopilot-proof-lab", "evaluate", "--workspace", str(workspace)],
    ]
    for command in commands:
        _run(command, env=env, cwd=output)

    status = json.loads(
        _run_capture(
            [str(cli_bin), "autopilot-proof-lab", "status", "--workspace", str(workspace), "--json"],
            env=env,
            cwd=output,
        ).stdout
    )
    if not str(status.get("assessment_id", "")).startswith("asmt_"):
        raise RuntimeError(f"installed proof lab did not return an assessment id: {status}")
    if status.get("decision") not in {"not_ready", "assist_only"}:
        raise RuntimeError(f"installed proof lab returned an unsafe sample decision: {status}")
    if status.get("external_actions_activated") is not False or status.get("advisory_only") is not True:
        raise RuntimeError(f"installed proof lab crossed its advisory boundary: {status}")

    reports = workspace / "05_REPORTS"
    for name in (
        "current_workflow.md",
        "automation_scope.md",
        "source_inventory.csv",
        "decision_table.csv",
        "exception_register.csv",
        "connector_permissions.md",
        "recovery_plan.md",
        "kill_switch_plan.md",
        "shadow_test_cases.csv",
        "comparison_report.md",
        "readiness_decision.json",
        "readiness_report.html",
        "improvement_roadmap.md",
        "proposal_scope.md",
    ):
        _require_file(reports / name)


def _venv_console_script(venv_dir: Path, name: str) -> Path:
    posix_script = venv_dir / "bin" / name
    if posix_script.exists():
        return posix_script
    return venv_dir / "Scripts" / f"{name}.exe"


def _isolated_installed_env(
    cli_bin: Path,
    extra_path: list[Path] | None = None,
    python_paths: list[Path] | None = None,
) -> dict[str, str]:
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env["PYTHONNOUSERSITE"] = "1"
    path_parts = [str(cli_bin.parent)]
    for path in extra_path or []:
        path_parts.append(str(path))
    if env.get("PATH"):
        path_parts.append(env["PATH"])
    env["PATH"] = os.pathsep.join(path_parts)
    if python_paths:
        env["PYTHONPATH"] = os.pathsep.join(str(path) for path in python_paths)
    return env


def _optional_module_parent(module_name: str) -> Path | None:
    spec = importlib.util.find_spec(module_name)
    if spec is None:
        return None
    locations = spec.submodule_search_locations
    if locations:
        first = next(iter(locations), None)
        if first:
            return Path(first).resolve().parent
    if spec.origin and spec.origin not in {"built-in", "frozen"}:
        return Path(spec.origin).resolve().parent
    return None


def _office_workspace_python_paths() -> list[Path]:
    if hasattr(hashlib, "scrypt"):
        return []
    cryptography_root = _optional_module_parent("cryptography")
    if cryptography_root is None:
        raise RuntimeError(
            "Installed office-workspace smoke requires hashlib.scrypt support or a local cryptography package."
        )
    return [cryptography_root]


def _installed_cli_with_late_python_paths(
    cli_bin: Path,
    python_bin: Path,
    output: Path,
    python_paths: list[Path],
) -> Path:
    if not python_paths:
        return cli_bin
    wrapper = output / "installed-office-cli"
    path_literals = repr([str(path) for path in python_paths])
    bootstrap = (
        "import sys; import ai_automation_kit; "
        "sys.path.extend({}); from ai_automation_kit.cli import main; "
        "raise SystemExit(main(sys.argv[1:]))"
    ).format(path_literals)
    wrapper.write_text(
        "#!/bin/sh\nexec {} -c {} \"$@\"\n".format(
            shlex.quote(str(python_bin)),
            shlex.quote(bootstrap),
        ),
        encoding="utf-8",
    )
    wrapper.chmod(0o700)
    return wrapper


def _parse_workspace_path(stdout: str) -> Path:
    for line in stdout.splitlines():
        if line.startswith("workspace="):
            return Path(line.split("=", 1)[1].strip())
    raise RuntimeError(f"workspace path was not printed:\n{stdout}")


def _require_office_workspace_pack_resources() -> None:
    manifest_path = ROOT / "src" / "ai_automation_kit" / "packs" / "manifest.json"
    _require_file(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if list(manifest) != OFFICE_WORKSPACE_PACK_IDS:
        raise RuntimeError(f"unexpected office workspace pack manifest order: {list(manifest)}")

    packs_root = manifest_path.parent
    for pack_id in OFFICE_WORKSPACE_PACK_IDS:
        entry = manifest.get(pack_id)
        if not isinstance(entry, dict):
            raise RuntimeError(f"office workspace pack manifest entry is missing for {pack_id}")
        for key in ("pack_file", "output_schema_file", "prompt_template_file"):
            value = entry.get(key)
            if not isinstance(value, str) or not value:
                raise RuntimeError(f"office workspace pack manifest entry is missing {key} for {pack_id}")
            _require_file(packs_root / value)


def _assert_installed_office_pack_catalog(cli_bin: Path, env: dict[str, str], cwd: Path) -> None:
    payload = json.loads(
        _run_capture([str(cli_bin), "office-workspace", "packs", "--json"], env=env, cwd=cwd).stdout
    )
    actual_ids = [pack.get("id") for pack in payload]
    if actual_ids != OFFICE_WORKSPACE_PACK_IDS:
        raise RuntimeError(f"unexpected installed office-workspace pack order: {actual_ids}")
    for index, pack in enumerate(payload):
        expected_period_type = "month" if index == 0 else "day"
        if pack.get("period_type") != expected_period_type:
            raise RuntimeError(f"unexpected period_type for {pack.get('id')}: {pack.get('period_type')}")


def _assert_installed_office_pack_resources_load(python_bin: Path, env: dict[str, str], cwd: Path) -> None:
    code = """
import json
import sys
from pathlib import Path

repo_root = Path(sys.argv[1]).resolve()
expected_ids = json.loads(sys.argv[2])

import ai_automation_kit

package_path = Path(ai_automation_kit.__file__).resolve()
source_tree_package = (repo_root / "src" / "ai_automation_kit").resolve()
if source_tree_package in package_path.parents:
    raise RuntimeError("source-tree import leakage")

from ai_automation_kit.core.workflow_pack import (
    list_bundled_packs,
    load_bundled_output_schema,
    load_bundled_prompt_template,
)

packs = list_bundled_packs()
actual_ids = [pack["id"] for pack in packs]
if actual_ids != expected_ids:
    raise RuntimeError(f"unexpected bundled office pack ids: {actual_ids}")

loaded_resources = []
for pack in packs:
    pack_id = pack["id"]
    schema = load_bundled_output_schema(pack_id)
    prompt = load_bundled_prompt_template(pack_id)
    loaded_resources.append(
        {
            "id": pack_id,
            "output_keys": sorted(schema["properties"]),
            "prompt_template_id": prompt["template_id"],
            "output_paths": [item["relative_path"] for item in pack["outputs"]],
        }
    )

print(json.dumps({"pack_ids": actual_ids, "loaded_resources": loaded_resources}, ensure_ascii=False))
"""
    payload = json.loads(
        _run_capture(
            [str(python_bin), "-c", code, str(ROOT), json.dumps(OFFICE_WORKSPACE_PACK_IDS)],
            env=env,
            cwd=cwd,
        ).stdout
    )
    if payload.get("pack_ids") != OFFICE_WORKSPACE_PACK_IDS:
        raise RuntimeError(f"unexpected installed packaged office resources: {payload}")


def _assert_installed_daily_workspace_create(cli_bin: Path, env: dict[str, str], office_root: Path, cwd: Path) -> None:
    created = _run_capture(
        [
            str(cli_bin),
            "office-workspace",
            "create",
            "--root",
            str(office_root),
            "--name",
            "Daily Reconciliation",
            "--approver",
            "Release QA",
            "--pin",
            "482913",
            "--pack",
            "spreadsheet-reconciliation-daily",
            "--period",
            "2026-07-12",
            "--language",
            "en",
        ],
        env=env,
        cwd=cwd,
    )
    if "2026-07-12" not in created.stdout:
        raise RuntimeError(f"unexpected daily office workspace create output:\n{created.stdout}")
    workspace = _parse_workspace_path(created.stdout)
    status = json.loads(
        _run_capture(
            [str(cli_bin), "office-workspace", "status", "--workspace", str(workspace), "--json"],
            env=env,
            cwd=cwd,
        ).stdout
    )
    if status.get("pack_id") != "spreadsheet-reconciliation-daily":
        raise RuntimeError(f"unexpected daily office workspace pack: {status}")
    if status.get("current_period") != "2026-07-12" or status.get("current_stage") != "created":
        raise RuntimeError(f"unexpected daily office workspace status: {status}")
    _require_file(workspace / "03_CURRENT_INPUTS" / "2026-07-12")


def _assert_installed_daily_workspace_rejects_invalid_period(
    cli_bin: Path, env: dict[str, str], office_root: Path, cwd: Path
) -> None:
    command = [
        str(cli_bin),
        "office-workspace",
        "create",
        "--root",
        str(office_root),
        "--name",
        "Broken Daily Inquiry",
        "--approver",
        "Release QA",
        "--pin",
        "482913",
        "--pack",
        "inquiry-daily",
        "--period",
        "2026-07",
        "--language",
        "en",
    ]
    print("$ " + " ".join(command))
    failed = subprocess.run(command, cwd=cwd, env=env, check=False, text=True, capture_output=True)
    if failed.returncode == 0:
        raise RuntimeError("invalid daily office workspace period unexpectedly succeeded")
    error_text = "\n".join(part for part in [failed.stdout, failed.stderr] if part).strip()
    if "YYYY-MM-DD" not in error_text:
        raise RuntimeError(f"invalid daily office workspace error did not mention YYYY-MM-DD:\n{error_text}")


def _write_fake_office_codex(path: Path, exact_draft: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """#!/usr/bin/env python3
import json
import sys
from pathlib import Path

EXACT_DRAFT = {exact_draft}

argv = sys.argv[1:]
if argv[:2] == ["login", "status"]:
    raise SystemExit(0)
if not argv or argv[0] != "exec":
    raise SystemExit(91)
sys.stdin.read()
print(json.dumps({{"event": "run.started", "status": "running"}}), flush=True)
output_path = Path(argv[argv.index("--output-last-message") + 1])
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(
    json.dumps({{"missing_questions": [], "draft_markdown": EXACT_DRAFT}}),
    encoding="utf-8",
)
print(json.dumps({{"event": "run.finished", "status": "completed"}}), flush=True)
""".format(exact_draft=json.dumps(exact_draft)),
        encoding="utf-8",
    )
    path.chmod(0o755)
    return path


def _run_installed_office_internal_flow(
    python_bin: Path,
    env: dict[str, str],
    *,
    workspace: Path,
    fake_codex: Path,
    expected_hash: str,
) -> dict:
    code = """
import json
import os
import sys
from pathlib import Path

repo_root = Path(sys.argv[1]).resolve()
workspace = Path(sys.argv[2]).resolve()
fake_codex = Path(sys.argv[3]).resolve()
expected_hash = sys.argv[4]

# Keep fallback dependency paths available, but make the installed wheel win over
# any user-site copy of ai_automation_kit that may live on PYTHONPATH.
for entry in [item for item in os.environ.get("PYTHONPATH", "").split(os.pathsep) if item]:
    while entry in sys.path:
        sys.path.remove(entry)
    sys.path.append(entry)

import ai_automation_kit

package_path = Path(ai_automation_kit.__file__).resolve()
source_tree_package = (repo_root / "src" / "ai_automation_kit").resolve()
if source_tree_package in package_path.parents:
    raise RuntimeError("source-tree import leakage")

from ai_automation_kit.core.codex_runner import start_codex_run, wait_for_run
from ai_automation_kit.core.office_workspace_state import approve_draft, create_period, inspect_period, save_answer

inspect_period(workspace, "2026-07")
save_answer(workspace, "2026-07", "audience", "Operations board and finance lead")
run = start_codex_run(workspace, "2026-07", executable=str(fake_codex), timeout_seconds=60)
completed = wait_for_run(workspace, run["run_id"], timeout_seconds=10)
if completed["status"] != "ready_for_review":
    raise RuntimeError(f"unexpected installed run status: {completed}")
if not completed.get("source_manifest_hash") or not completed.get("snapshot_manifest_hash"):
    raise RuntimeError("installed office workspace run did not record source evidence hashes")

manifest_path = workspace / ".system" / "periods" / "2026-07" / "source_manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
supporting_manifest = [
    item for item in manifest.get("accepted", []) if item.get("source_role") == "past_supporting"
]
if len(supporting_manifest) != 1 or supporting_manifest[0].get("name") != "recurring-notes.md":
    raise RuntimeError("installed office workspace source manifest did not retain supporting evidence metadata")

snapshot_manifest_path = (
    workspace
    / ".system"
    / "runs"
    / run["run_id"]
    / "sandbox"
    / "input_snapshot"
    / "source_manifest.json"
)
snapshot_manifest = json.loads(snapshot_manifest_path.read_text(encoding="utf-8"))
supporting_snapshot = [
    item
    for item in snapshot_manifest.get("records", [])
    if item.get("provenance", {}).get("source_role") == "past_supporting"
]
if (
    len(supporting_snapshot) != 1
    or supporting_snapshot[0].get("relative_path") != "input_snapshot/past_supporting/recurring-notes.md"
):
    raise RuntimeError("installed office workspace snapshot did not retain supporting evidence metadata")

period = approve_draft(workspace, "2026-07", "monthly_report.md", "Release QA", "482913")
approved = period["approved_outputs"][-1]
if approved["sha256"] != expected_hash:
    raise RuntimeError("approved_sha256 mismatch")

create_period(
    workspace,
    "2026-08",
    style_reference={"relative_path": approved["path"], "sha256": approved["sha256"]},
)

print(
    json.dumps(
        {
            "run_id": run["run_id"],
            "approved_sha256": approved["sha256"],
            "approved_path": approved["path"],
            "audit_hash": approved["audit_hash"],
            "supporting_evidence": {
                "manifest_name": supporting_manifest[0]["name"],
                "snapshot_path": supporting_snapshot[0]["relative_path"],
                "source_role": supporting_snapshot[0]["provenance"]["source_role"],
            },
        },
        ensure_ascii=False,
    )
)
"""
    completed = _run_capture(
        [str(python_bin), "-c", code, str(ROOT), str(workspace), str(fake_codex), expected_hash],
        env=env,
        cwd=workspace.parent,
    )
    return json.loads(completed.stdout)


def _run_office_workspace_installed_smoke(cli_bin: Path, python_bin: Path, output: Path) -> None:
    _require_file(ROOT / "docs/office-workspace.html")
    _require_file(ROOT / "docs/office-workspace.ja.html")
    _require_file(ROOT / "START_WITH_CODEX.md")
    _require_file(ROOT / "START_WITH_CODEX.ja.md")
    _require_file(ROOT / "AGENTS.md")
    _require_office_workspace_pack_resources()

    exact_draft = (
        "# Monthly Draft\n"
        "Revenue: 128000\n"
        "Open issues: 2\n"
        "Decision: Hold vendor escalation until Tuesday.\n"
    )
    expected_hash = hashlib.sha256(exact_draft.encode("utf-8")).hexdigest()
    fake_codex = _write_fake_office_codex(output / "fake-codex-bin" / "codex", exact_draft)
    python_paths = _office_workspace_python_paths()
    cli_bin = _installed_cli_with_late_python_paths(cli_bin, python_bin, output, python_paths)
    env = _isolated_installed_env(cli_bin, extra_path=[fake_codex.parent])

    office_root = output / "installed-office-workspaces"
    office_root.mkdir(parents=True, exist_ok=True)

    _assert_installed_office_pack_catalog(cli_bin, env, output)
    _assert_installed_office_pack_resources_load(python_bin, env, output)
    _assert_installed_daily_workspace_rejects_invalid_period(cli_bin, env, office_root, output)
    _assert_installed_daily_workspace_create(cli_bin, env, office_root, output)

    # office-workspace create
    created = _run_capture(
        [
            str(cli_bin),
            "office-workspace",
            "create",
            "--root",
            str(office_root),
            "--name",
            "Construction Monthly",
            "--approver",
            "Release QA",
            "--pin",
            "482913",
            "--period",
            "2026-07",
            "--language",
            "en",
        ],
        env=env,
        cwd=output,
    )
    workspace = _parse_workspace_path(created.stdout)
    status_before = json.loads(
        _run_capture(
            [str(cli_bin), "office-workspace", "status", "--workspace", str(workspace), "--json"],
            env=env,
            cwd=output,
        ).stdout
    )
    if status_before["current_period"] != "2026-07" or status_before["current_stage"] != "created":
        raise RuntimeError(f"unexpected office workspace status after create: {status_before}")

    (workspace / "01_APPROVED_PAST_OUTPUTS" / "2026-06-monthly-report.md").write_text(
        "# Approved Monthly Report\nRevenue: 120000\n",
        encoding="utf-8",
    )
    (workspace / "02_PAST_SUPPORTING_FILES" / "recurring-notes.md").write_text(
        "- Vendor escalation is reviewed every Tuesday.\n",
        encoding="utf-8",
    )
    (workspace / "03_CURRENT_INPUTS" / "2026-07" / "labor_hours.csv").write_text(
        "metric,value\nrevenue,128000\nopen_issues,2\n",
        encoding="utf-8",
    )
    (workspace / "03_CURRENT_INPUTS" / "2026-07" / "meeting-notes.md").write_text(
        "# Current notes\nDecision remains pending until Tuesday.\n",
        encoding="utf-8",
    )

    # office-workspace inspect
    inspected = _run_capture(
        [
            str(cli_bin),
            "office-workspace",
            "inspect",
            "--workspace",
            str(workspace),
            "--period",
            "2026-07",
        ],
        env=env,
        cwd=output,
    )
    if "stage=questioning" not in inspected.stdout:
        raise RuntimeError(f"unexpected office workspace inspect output:\n{inspected.stdout}")

    internal_env = dict(env)
    if python_paths:
        internal_env["PYTHONPATH"] = os.pathsep.join(str(path) for path in python_paths)
    internal = _run_installed_office_internal_flow(
        python_bin,
        internal_env,
        workspace=workspace,
        fake_codex=fake_codex,
        expected_hash=expected_hash,
    )
    approved_path = workspace / internal["approved_path"]
    _require_file(approved_path)
    if approved_path.read_text(encoding="utf-8") != exact_draft:
        raise RuntimeError("installed office workspace approved draft content did not match the exact known draft")
    supporting_evidence = internal.get("supporting_evidence", {})
    if supporting_evidence != {
        "manifest_name": "recurring-notes.md",
        "snapshot_path": "input_snapshot/past_supporting/recurring-notes.md",
        "source_role": "past_supporting",
    }:
        raise RuntimeError(f"installed office workspace supporting evidence metadata was incomplete: {supporting_evidence}")

    status_after = json.loads(
        _run_capture(
            [str(cli_bin), "office-workspace", "status", "--workspace", str(workspace), "--json"],
            env=env,
            cwd=output,
        ).stdout
    )
    if status_after["current_period"] != "2026-08" or status_after["current_stage"] != "created":
        raise RuntimeError(f"unexpected office workspace status after rollover: {status_after}")

    # office-workspace serve
    _assert_office_workspace_cli_serve(
        cli_bin=cli_bin,
        root=office_root,
        workspace=workspace,
        workspace_name="Construction Monthly",
        env=env,
        expected_hash=expected_hash,
    )


def _run_report_wizard_installed_smoke(cli_bin: Path, python_bin: Path, output: Path) -> None:
    _require_file(ROOT / "docs" / "report-automation-wizard.html")
    _require_file(ROOT / "docs" / "report-automation-wizard.ja.html")
    _require_file(ROOT / "docs" / "report-automation-wizard-flow.mmd")

    report_wizard_output = output / "report-wizard-weekly"
    report_wizard_output.mkdir(parents=True, exist_ok=True)
    past = output / "report-wizard-past.md"
    current = output / "report-wizard-current.csv"
    past.write_text(
        "# Executive Summary\n"
        "Weekly revenue stayed on plan.\n"
        "\n"
        "# Risks\n"
        "- Waiting on one vendor response.\n",
        encoding="utf-8",
    )
    current.write_text(
        "metric,value\n"
        "revenue,128000\n"
        "open_issues,2\n"
        "site_visits,43\n",
        encoding="utf-8",
    )

    env = os.environ.copy()
    _run(
        [
            str(cli_bin),
            "report-wizard",
            "init",
            "--workspace",
            str(report_wizard_output),
            "--report-type",
            "weekly",
            "--language",
            "en",
        ],
        env=env,
    )
    _run(
        [
            str(cli_bin),
            "report-wizard",
            "inspect",
            "--workspace",
            str(report_wizard_output),
            "--past-outputs",
            str(past),
            "--materials",
            str(current),
        ],
        env=env,
    )
    _run([str(cli_bin), "report-wizard", "confirm", "--workspace", str(report_wizard_output)], env=env)
    for answer in [
        "Operations manager",
        "report-wizard-past.md",
        "Executive Summary, Risks, Next Actions",
        "2026-W27",
        "Finance director",
        "01_past_outputs/weekly_reports",
    ]:
        _run(
            [str(cli_bin), "report-wizard", "answer", "--workspace", str(report_wizard_output), "--answer", answer],
            env=env,
        )
    _run([str(cli_bin), "report-wizard", "build", "--workspace", str(report_wizard_output)], env=env)
    status = _run_capture(
        [str(cli_bin), "report-wizard", "status", "--workspace", str(report_wizard_output), "--json"],
        env=env,
    )
    payload = json.loads(status.stdout)
    if payload["stage"] != "ready_for_human_review":
        raise RuntimeError(f"unexpected report wizard stage before approval: {payload['stage']}")

    state_path = report_wizard_output / "report_wizard_state.json"
    template_path = report_wizard_output / "03_templates" / "weekly_report_template.md"
    source_manifest_path = report_wizard_output / "04_ai_analysis" / "source_manifest.json"
    schema_proposal_path = report_wizard_output / "04_ai_analysis" / "schema_proposal.json"
    provenance_path = report_wizard_output / "04_ai_analysis" / "provenance.json"
    instructions_path = report_wizard_output / "04_ai_analysis" / "ai_agent_review_instructions.md"
    question_session_path = report_wizard_output / "05_grill_me_questions" / "session.json"
    draft_path = report_wizard_output / "06_drafts" / "weekly_report_draft.md"
    approval_path = report_wizard_output / "07_approval" / "approval.json"
    for required in [
        state_path,
        template_path,
        source_manifest_path,
        schema_proposal_path,
        provenance_path,
        instructions_path,
        question_session_path,
        draft_path,
        approval_path,
    ]:
        _require_file(required)

    pending_approval = json.loads(approval_path.read_text(encoding="utf-8"))
    if pending_approval.get("status") != "pending":
        raise RuntimeError(f"unexpected pre-approval status: {pending_approval}")

    _run(
        [str(cli_bin), "report-wizard", "approve", "--workspace", str(report_wizard_output), "--approver", "Release QA"],
        env=env,
    )
    approved = json.loads(approval_path.read_text(encoding="utf-8"))
    state_record = json.loads(state_path.read_text(encoding="utf-8"))
    state_after_approval = json.loads(
        _run_capture([str(cli_bin), "report-wizard", "status", "--workspace", str(report_wizard_output), "--json"], env=env).stdout
    )
    expected_hash = hashlib.sha256(draft_path.read_bytes()).hexdigest()
    if approved.get("status") != "approved":
        raise RuntimeError(f"unexpected report wizard approval status: {approved}")
    if approved.get("report_sha256") != expected_hash:
        raise RuntimeError("report wizard approval hash did not match the built draft")
    if state_record.get("approval", {}).get("report_sha256") != expected_hash:
        raise RuntimeError("report wizard state hash did not match the built draft")
    if state_after_approval["stage"] != "approved":
        raise RuntimeError(f"unexpected report wizard stage after approval: {state_after_approval['stage']}")
    _assert_report_wizard_cli_serve(
        cli_bin=cli_bin,
        workspace=report_wizard_output,
        expected_hash=expected_hash,
    )


def _assert_office_workspace_cli_serve(
    *,
    cli_bin: Path,
    root: Path,
    workspace: Path,
    workspace_name: str,
    env: dict[str, str],
    expected_hash: str,
) -> None:
    port = _reserve_local_port()
    base_url = f"http://127.0.0.1:{port}"
    command = [
        str(cli_bin),
        "office-workspace",
        "serve",
        "--root",
        str(root),
        "--language",
        "en",
        "--port",
        str(port),
        "--no-open",
    ]
    print("$ " + " ".join(command))
    process = None
    events: queue.Queue[tuple[str, str]] = queue.Queue()
    readers: list[threading.Thread] = []
    stdout_lines: list[str] = []
    stderr_lines: list[str] = []
    killed = False
    returncode = None
    failure = None
    try:
        process = subprocess.Popen(
            command,
            cwd=root.parent,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        readers = [
            threading.Thread(target=_pump_stream_lines, args=("stdout", process.stdout, events), daemon=True),
            threading.Thread(target=_pump_stream_lines, args=("stderr", process.stderr, events), daemon=True),
        ]
        for reader in readers:
            reader.start()

        root_html = _wait_for_http_ready(
            process,
            events,
            stdout_lines,
            stderr_lines,
            url=base_url + "/",
            deadline_seconds=10.0,
            label="office workspace",
        )
        if "<!doctype html>" not in root_html.lower():
            raise RuntimeError("office workspace serve root did not return an HTML document")

        token_match = re.search(r'const SESSION_TOKEN = "([0-9a-f]{64})"', root_html)
        if token_match is None:
            raise RuntimeError("office workspace root did not expose a session token")
        token = token_match.group(1)
        list_payload = _http_get_json(
            base_url + "/api/workspaces",
            headers={"X-Office-Workspace-Token": token, "Accept": "application/json"},
        )
        if list_payload.get("ok") is not True:
            raise RuntimeError(f"office workspace /api/workspaces did not return ok=true: {list_payload}")
        if list_payload["data"]["preflight"]["ok"] is not True:
            raise RuntimeError(f"office workspace preflight was not ready: {list_payload['data']['preflight']}")
        summaries = list_payload["data"]["workspaces"]
        matching = [item for item in summaries if item.get("name") == workspace_name]
        if len(matching) != 1:
            raise RuntimeError(f"expected exactly one matching office workspace: {summaries}")
        summary = matching[0]
        if summary["current_period"] != "2026-08":
            raise RuntimeError(f"office workspace rollover did not persist in summary: {summary}")

        detail_payload = _http_get_json(
            base_url + "/api/workspaces/" + summary["id"],
            headers={"X-Office-Workspace-Token": token, "Accept": "application/json"},
        )
        if detail_payload.get("ok") is not True:
            raise RuntimeError(f"office workspace detail did not return ok=true: {detail_payload}")
        detail = detail_payload["data"]["workspace"]
        if Path(detail["root"]).resolve() != workspace.resolve():
            raise RuntimeError(f"office workspace detail returned the wrong root: {detail}")
        style_reference = detail["period"]["style_reference"]
        if style_reference["sha256"] != expected_hash:
            raise RuntimeError("office workspace style reference hash did not match the approved draft hash")
        if detail["period"]["period_id"] != "2026-08":
            raise RuntimeError(f"office workspace detail did not expose the rolled period: {detail['period']}")
    except Exception as exc:  # pragma: no cover - exercised by smoke execution
        failure = exc
    finally:
        if process is not None:
            if process.poll() is None:
                process.send_signal(signal.SIGINT)
                try:
                    returncode = process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    killed = True
                    process.kill()
                    returncode = process.wait(timeout=5)
            else:
                returncode = process.returncode
            if process.stdout is not None:
                process.stdout.close()
            if process.stderr is not None:
                process.stderr.close()
        for reader in readers:
            reader.join(timeout=1)
        _drain_stream_events(events, stdout_lines, stderr_lines)
    if failure is not None:
        raise RuntimeError(
            "office workspace CLI serve smoke failed:\n"
            f"stdout={''.join(stdout_lines)}\n"
            f"stderr={''.join(stderr_lines)}"
        ) from failure
    if killed:
        raise RuntimeError(
            "office workspace CLI serve required kill fallback:\n"
            f"stdout={''.join(stdout_lines)}\n"
            f"stderr={''.join(stderr_lines)}"
        )
    if returncode != 0:
        raise RuntimeError(
            "office workspace CLI serve exited with code {}:\nstdout={}\nstderr={}".format(
                returncode,
                "".join(stdout_lines),
                "".join(stderr_lines),
            )
        )


def _assert_report_wizard_cli_serve(cli_bin: Path, workspace: Path, expected_hash: str) -> None:
    # Use installed ai-automation-kit report-wizard serve so smoke exercises the real CLI entrypoint.
    # Require a clean serve exit after SIGINT; kill only as fallback.
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    command = [
        str(cli_bin),
        "report-wizard",
        "serve",
        "--workspace",
        str(workspace),
        "--language",
        "en",
        "--port",
        "0",
        "--no-open",
    ]
    print("$ " + " ".join(command))
    process = None
    events: queue.Queue[tuple[str, str]] = queue.Queue()
    readers: list[threading.Thread] = []
    stdout_lines: list[str] = []
    stderr_lines: list[str] = []
    killed = False
    returncode = None
    failure = None
    try:
        process = subprocess.Popen(
            command,
            cwd=ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        readers = [
            threading.Thread(target=_pump_stream_lines, args=("stdout", process.stdout, events), daemon=True),
            threading.Thread(target=_pump_stream_lines, args=("stderr", process.stderr, events), daemon=True),
        ]
        for reader in readers:
            reader.start()

        url = _wait_for_report_wizard_url(process, events, stdout_lines, stderr_lines, deadline_seconds=10.0)
        root_html = _http_get_text(url)
        if "<!doctype html>" not in root_html.lower():
            raise RuntimeError("report wizard serve root did not return an HTML document")

        token = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query).get("token", [None])[0]
        if not token:
            raise RuntimeError("report wizard serve URL did not include a session token")
        api_state_url = "{}/api/state".format(url.split("/?", 1)[0].rstrip("/"))
        payload = _http_get_json(api_state_url, headers={"X-Report-Wizard-Token": token})
        if payload.get("ok") is not True:
            raise RuntimeError(f"report wizard /api/state did not return ok=true: {payload}")
        if payload.get("stage") != "approved":
            raise RuntimeError(f"report wizard /api/state stage was not approved: {payload}")
        if payload["data"]["state"]["approval"]["report_sha256"] != expected_hash:
            raise RuntimeError("report wizard HTTP approval hash did not match the approved draft hash")
    except Exception as exc:  # pragma: no cover - exercised by smoke execution
        failure = exc
    finally:
        if process is not None:
            if process.poll() is None:
                process.send_signal(signal.SIGINT)
                try:
                    returncode = process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    killed = True
                    process.kill()
                    returncode = process.wait(timeout=5)
            else:
                returncode = process.returncode
            if process.stdout is not None:
                process.stdout.close()
            if process.stderr is not None:
                process.stderr.close()
        for reader in readers:
            reader.join(timeout=1)
        _drain_stream_events(events, stdout_lines, stderr_lines)
    if failure is not None:
        raise RuntimeError(
            "report wizard CLI serve smoke failed:\n"
            f"stdout={''.join(stdout_lines)}\n"
            f"stderr={''.join(stderr_lines)}"
        ) from failure
    if killed:
        raise RuntimeError(
            "report wizard CLI serve required kill fallback:\n"
            f"stdout={''.join(stdout_lines)}\n"
            f"stderr={''.join(stderr_lines)}"
        )
    if returncode != 0:
        raise RuntimeError(
            "report wizard CLI serve exited with code {}:\nstdout={}\nstderr={}".format(
                returncode,
                "".join(stdout_lines),
                "".join(stderr_lines),
            )
        )


def _pump_stream_lines(name: str, stream, events: queue.Queue[tuple[str, str]]) -> None:
    if stream is None:
        return
    try:
        for line in iter(stream.readline, ""):
            events.put((name, line))
    finally:
        events.put((name, ""))


def _drain_stream_events(
    events: queue.Queue[tuple[str, str]],
    stdout_lines: list[str],
    stderr_lines: list[str],
) -> None:
    while True:
        try:
            name, line = events.get_nowait()
        except queue.Empty:
            return
        if not line:
            continue
        if name == "stdout":
            stdout_lines.append(line)
        else:
            stderr_lines.append(line)


def _wait_for_report_wizard_url(
    process: subprocess.Popen[str],
    events: queue.Queue[tuple[str, str]],
    stdout_lines: list[str],
    stderr_lines: list[str],
    *,
    deadline_seconds: float,
) -> str:
    return _wait_for_local_url(
        process,
        events,
        stdout_lines,
        stderr_lines,
        deadline_seconds=deadline_seconds,
        label="report wizard",
    )


def _wait_for_local_url(
    process: subprocess.Popen[str],
    events: queue.Queue[tuple[str, str]],
    stdout_lines: list[str],
    stderr_lines: list[str],
    *,
    deadline_seconds: float,
    label: str,
) -> str:
    deadline = time.monotonic() + deadline_seconds
    while time.monotonic() < deadline:
        if process.poll() is not None:
            _drain_stream_events(events, stdout_lines, stderr_lines)
            raise RuntimeError(
                f"{label} CLI serve exited before printing its URL:\n"
                f"stdout={''.join(stdout_lines)}\n"
                f"stderr={''.join(stderr_lines)}"
            )
        timeout = max(0.0, min(0.25, deadline - time.monotonic()))
        try:
            name, line = events.get(timeout=timeout)
        except queue.Empty:
            continue
        if not line:
            continue
        target = stdout_lines if name == "stdout" else stderr_lines
        target.append(line)
        candidate = line.strip()
        if candidate.startswith("http://127.0.0.1:") or candidate.startswith("http://localhost:"):
            return candidate
    raise RuntimeError(
        f"timed out waiting for {label} serve URL:\n"
        f"stdout={''.join(stdout_lines)}\n"
        f"stderr={''.join(stderr_lines)}"
    )


def _reserve_local_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_for_http_ready(
    process: subprocess.Popen[str],
    events: queue.Queue[tuple[str, str]],
    stdout_lines: list[str],
    stderr_lines: list[str],
    *,
    url: str,
    deadline_seconds: float,
    label: str,
) -> str:
    deadline = time.monotonic() + deadline_seconds
    last_error = ""
    while time.monotonic() < deadline:
        _drain_stream_events(events, stdout_lines, stderr_lines)
        if process.poll() is not None:
            raise RuntimeError(
                f"{label} CLI serve exited before responding at {url}:\n"
                f"stdout={''.join(stdout_lines)}\n"
                f"stderr={''.join(stderr_lines)}"
            )
        try:
            return _http_get_text(url)
        except Exception as exc:  # pragma: no cover - exercised by smoke execution
            last_error = str(exc)
            time.sleep(0.1)
    raise RuntimeError(
        f"timed out waiting for {label} serve HTTP at {url}: {last_error}\n"
        f"stdout={''.join(stdout_lines)}\n"
        f"stderr={''.join(stderr_lines)}"
    )


def _http_get_text(url: str, headers: dict[str, str] | None = None) -> str:
    request = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(request, timeout=5) as response:
        return response.read().decode("utf-8")


def _http_get_json(url: str, headers: dict[str, str] | None = None) -> dict:
    return json.loads(_http_get_text(url, headers=headers))


def _run_capture(command: list[str], env: dict[str, str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    print("$ " + " ".join(command))
    return subprocess.run(command, cwd=cwd or ROOT, env=env, check=True, text=True, capture_output=True)


def _run(command: list[str], env: dict[str, str], cwd: Path | None = None) -> None:
    print("$ " + " ".join(command))
    subprocess.run(command, cwd=cwd or ROOT, env=env, check=True)


def _require_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Expected release smoke artifact was not created: {path}")


if __name__ == "__main__":
    raise SystemExit(main())
