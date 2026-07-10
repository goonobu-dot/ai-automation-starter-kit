from __future__ import annotations

import argparse
import importlib
import json
import os
import shutil
import sys
from pathlib import Path

from ai_automation_kit import __version__
from ai_automation_kit.core.beginner_guide import render_beginner_overview
from ai_automation_kit.core.beginner_guide import render_beginner_step
from ai_automation_kit.core.beginner_sales import generate_beginner_sales_pack
from ai_automation_kit.core.client_ready import generate_client_ready_pack
from ai_automation_kit.core.execution_expansion import generate_deployment_pack
from ai_automation_kit.core.execution_expansion import generate_document_intake_pack
from ai_automation_kit.core.execution_expansion import generate_flow_export
from ai_automation_kit.core.execution_expansion import generate_observability_pack
from ai_automation_kit.core.execution_expansion import generate_runtime_safety_pack
from ai_automation_kit.core.execution_expansion import generate_secrets_bootstrap
from ai_automation_kit.core.execution_expansion import generate_state_backend_pack
from ai_automation_kit.core.flow_diagram import write_flow_diagram
from ai_automation_kit.core.flows import get_flow
from ai_automation_kit.core.flows import install_flow
from ai_automation_kit.core.flows import list_flows
from ai_automation_kit.core.flows import validate_flow_project
from ai_automation_kit.core.flow_runtime import approve_all_pending
from ai_automation_kit.core.flow_runtime import run_flow_project
from ai_automation_kit.core.automation_expansion import generate_agent_team
from ai_automation_kit.core.automation_expansion import generate_approval_gate
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
from ai_automation_kit.core.offer_pack import generate_offer_pack
from ai_automation_kit.core.operator_console import generate_client_report
from ai_automation_kit.core.operator_console import generate_cloud_plan
from ai_automation_kit.core.operator_console import generate_complete_workspace
from ai_automation_kit.core.operator_console import generate_connector_doctor
from ai_automation_kit.core.operator_console import generate_demo_site
from ai_automation_kit.core.operator_console import generate_flow_guide
from ai_automation_kit.core.operator_console import generate_grill_me_pack
from ai_automation_kit.core.operator_console import generate_guided_review
from ai_automation_kit.core.operator_console import generate_guided_setup
from ai_automation_kit.core.operator_console import generate_install_bundle
from ai_automation_kit.core.operator_console import generate_business_launch_pack
from ai_automation_kit.core.operator_console import generate_opportunity_catalog
from ai_automation_kit.core.operator_console import generate_quickstart_workspace
from ai_automation_kit.core.operator_console import generate_recommended_flow_from_intake
from ai_automation_kit.core.operator_console import generate_share_check
from ai_automation_kit.core.operator_console import generate_website_side_hustle_pack
from ai_automation_kit.core.operator_console import package_client_demo
from ai_automation_kit.core.report_automation import generate_report_automation_pack
from ai_automation_kit.core.report_wizard import answer_current_question
from ai_automation_kit.core.report_wizard import approve_report
from ai_automation_kit.core.report_wizard import build_report_workspace
from ai_automation_kit.core.report_wizard import confirm_folder_plan
from ai_automation_kit.core.report_wizard import create_session
from ai_automation_kit.core.report_wizard import inspect_session
from ai_automation_kit.core.report_wizard import session_status
from ai_automation_kit.core.side_hustle_blueprints import generate_side_hustle_blueprints
from ai_automation_kit.templates.docs_rag import run_docs_rag
from ai_automation_kit.templates.delivery_pipeline import run_delivery_pipeline
from ai_automation_kit.templates.excel_to_internal_app import run_excel_to_internal_app
from ai_automation_kit.templates.internal_ai_workflow import run_internal_ai_workflow
from ai_automation_kit.templates.research_agent import run_research_agent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-automation-kit")
    subparsers = parser.add_subparsers(dest="command", required=True)

    research = subparsers.add_parser("research-agent")
    research.add_argument("--config", required=True)
    research.add_argument("--output", required=True)

    discover = subparsers.add_parser("github-discover")
    discover.add_argument("--business-area", default="operations")
    discover.add_argument("--query")
    discover.add_argument("--limit", type=int, default=5)
    discover.add_argument("--output", required=True)
    discover.add_argument("--include-readme", action="store_true")

    onboard = subparsers.add_parser("onboard")
    onboard.add_argument("--business-area", default="operations")
    onboard.add_argument("--query")
    onboard.add_argument("--limit", type=int, default=2)
    onboard.add_argument("--output", required=True)
    onboard.add_argument("--include-readme", action="store_true")
    onboard.add_argument("--check-github", action="store_true")
    onboard.add_argument("--create-offer-pack", action="store_true")
    onboard.add_argument("--client-type", default="small-business")

    offer_pack = subparsers.add_parser("offer-pack")
    offer_pack.add_argument("--business-area", default="operations")
    offer_pack.add_argument("--client-type", default="small-business")
    offer_pack.add_argument("--source-output", required=True)
    offer_pack.add_argument("--output", required=True)

    client_ready = subparsers.add_parser("client-ready")
    client_ready.add_argument("--business-area", default="operations")
    client_ready.add_argument("--client-type", default="small-business")
    client_ready.add_argument("--niche", default="local-business")
    client_ready.add_argument("--source-output", required=True)
    client_ready.add_argument("--output", required=True)

    beginner_sales = subparsers.add_parser("beginner-sales")
    beginner_sales.add_argument("--flow-id")
    beginner_sales.add_argument("--industry", default="operations")
    beginner_sales.add_argument("--client-type", default="small-business")
    beginner_sales.add_argument("--niche", default="local-business")
    beginner_sales.add_argument("--output", required=True)

    flow_guide = subparsers.add_parser("flow-guide")
    flow_guide.add_argument("--industry")
    flow_guide.add_argument("--genre")
    flow_guide.add_argument("--niche", default="local-business")
    flow_guide.add_argument("--output", required=True)

    quickstart = subparsers.add_parser("quickstart")
    quickstart.add_argument("--flow-id")
    quickstart.add_argument("--industry", default="finance")
    quickstart.add_argument("--client-type", default="local-business")
    quickstart.add_argument("--niche", default="accounting")
    quickstart.add_argument("--output", required=True)

    demo_site = subparsers.add_parser("demo-site")
    demo_site.add_argument("--source", required=True)
    demo_site.add_argument("--output", required=True)
    demo_site.add_argument("--title", default="Client Automation Demo")

    install_bundle = subparsers.add_parser("install-bundle")
    install_bundle.add_argument("--flow-id", required=True)
    install_bundle.add_argument("--client-type", default="local-business")
    install_bundle.add_argument("--niche", default="accounting")
    install_bundle.add_argument("--output", required=True)

    connector_doctor = subparsers.add_parser("connector-doctor")
    connector_doctor.add_argument("--project", required=True)
    connector_doctor.add_argument("--output", required=True)

    client_report = subparsers.add_parser("client-report")
    client_report.add_argument("--flow-project", required=True)
    client_report.add_argument("--output", required=True)

    package_demo = subparsers.add_parser("package-client-demo")
    package_demo.add_argument("--source", required=True)
    package_demo.add_argument("--output", required=True)

    complete_workspace = subparsers.add_parser("complete-workspace")
    complete_workspace.add_argument("--flow-id")
    complete_workspace.add_argument("--industry", default="finance")
    complete_workspace.add_argument("--client-type", default="local-business")
    complete_workspace.add_argument("--niche", default="accounting")
    complete_workspace.add_argument("--approver", default="local-operator")
    complete_workspace.add_argument("--output", required=True)

    opportunity_catalog = subparsers.add_parser("opportunity-catalog")
    opportunity_catalog.add_argument("--industry")
    opportunity_catalog.add_argument("--output", required=True)

    recommend_flow = subparsers.add_parser("recommend-flow")
    recommend_flow.add_argument("--industry")
    recommend_flow.add_argument("--pain", required=True)
    recommend_flow.add_argument("--tools", default="")
    recommend_flow.add_argument("--monthly-items", type=int, default=40)
    recommend_flow.add_argument("--output", required=True)

    share_check = subparsers.add_parser("share-check")
    share_check.add_argument("--source", required=True)
    share_check.add_argument("--output", required=True)

    business_launch = subparsers.add_parser("business-launch")
    business_launch.add_argument("--industry", default="finance")
    business_launch.add_argument("--client-type", default="local-business")
    business_launch.add_argument("--niche", default="accounting")
    business_launch.add_argument("--operator-level", default="beginner")
    business_launch.add_argument("--output", required=True)

    website_side_hustle = subparsers.add_parser("website-side-hustle")
    website_side_hustle.add_argument("--industry", default="hospitality")
    website_side_hustle.add_argument("--client-type", default="local-business")
    website_side_hustle.add_argument("--niche", default="tourism-hotel")
    website_side_hustle.add_argument("--operator-level", default="beginner")
    website_side_hustle.add_argument("--output", required=True)

    side_hustle_blueprints = subparsers.add_parser("side-hustle-blueprints")
    side_hustle_blueprints.add_argument("--industry", default="local-business")
    side_hustle_blueprints.add_argument("--operator-level", default="beginner")
    side_hustle_blueprints.add_argument("--output", required=True)

    command_center = subparsers.add_parser("command-center")
    command_center.add_argument("--language", default="both", choices=["both", "en", "ja"])
    command_center.add_argument("--output", required=True)

    skill_pack = subparsers.add_parser("skill-pack")
    skill_pack.add_argument("--flow-id", required=True)
    skill_pack.add_argument("--agent", default="codex", choices=["codex", "claude-code", "cursor", "chatgpt"])
    skill_pack.add_argument("--output", required=True)

    approval_gate = subparsers.add_parser("approval-gate")
    approval_gate.add_argument("--flow-id", required=True)
    approval_gate.add_argument("--output", required=True)

    mcp_connector_plan = subparsers.add_parser("mcp-connector-plan")
    mcp_connector_plan.add_argument("--flow-id", required=True)
    mcp_connector_plan.add_argument("--connectors", default="gmail,google-sheets,slack")
    mcp_connector_plan.add_argument("--output", required=True)

    agent_team = subparsers.add_parser("agent-team")
    agent_team.add_argument("--flow-id", required=True)
    agent_team.add_argument("--output", required=True)

    workflow_explainer = subparsers.add_parser("workflow-explainer")
    workflow_explainer.add_argument("--flow-id", required=True)
    workflow_explainer.add_argument("--audience", default="client", choices=["client", "operator", "developer"])
    workflow_explainer.add_argument("--output", required=True)

    eval_loop = subparsers.add_parser("eval-loop")
    eval_loop.add_argument("--flow-id", required=True)
    eval_loop.add_argument("--metric", default="hours_saved")
    eval_loop.add_argument("--output", required=True)

    self_host_pack = subparsers.add_parser("self-host-pack")
    self_host_pack.add_argument("--flow-id", required=True)
    self_host_pack.add_argument("--provider", default="docker", choices=["docker", "vps", "cloud-run", "render", "railway"])
    self_host_pack.add_argument("--output", required=True)

    connector_catalog = subparsers.add_parser("connector-catalog")
    connector_catalog.add_argument("--industry", default="local-business")
    connector_catalog.add_argument("--output", required=True)

    script_ui_pack = subparsers.add_parser("script-ui-pack")
    script_ui_pack.add_argument("--flow-id", required=True)
    script_ui_pack.add_argument("--output", required=True)

    knowledge_rag_pack = subparsers.add_parser("knowledge-rag-pack")
    knowledge_rag_pack.add_argument("--flow-id", required=True)
    knowledge_rag_pack.add_argument("--output", required=True)

    automation_hooks = subparsers.add_parser("automation-hooks")
    automation_hooks.add_argument("--flow-id", required=True)
    automation_hooks.add_argument("--output", required=True)

    governance_pack = subparsers.add_parser("governance-pack")
    governance_pack.add_argument("--flow-id", required=True)
    governance_pack.add_argument("--output", required=True)

    guided_setup = subparsers.add_parser("guided-setup")
    guided_setup.add_argument("--flow-id", required=True)
    guided_setup.add_argument("--mode", default="beginner", choices=["beginner", "operator", "client"])
    guided_setup.add_argument(
        "--deployment",
        default="undecided",
        choices=["undecided", "local", "cloud", "render", "railway", "cloud-run", "vps"],
    )
    guided_setup.add_argument("--connectors", default="local-folder")
    guided_setup.add_argument("--output", required=True)

    guided_review = subparsers.add_parser("guided-review")
    guided_review.add_argument("--answers", required=True)
    guided_review.add_argument("--output", required=True)

    cloud_plan = subparsers.add_parser("cloud-plan")
    cloud_plan.add_argument("--flow-id", required=True)
    cloud_plan.add_argument(
        "--provider",
        required=True,
        choices=["google-cloud", "aws", "azure", "render", "railway", "vercel", "digitalocean", "fly"],
    )
    cloud_plan.add_argument(
        "--workload",
        default="webhook-api",
        choices=["webhook-api", "scheduled-job", "worker-queue", "web-app", "static-functions", "container-service"],
    )
    cloud_plan.add_argument("--connectors", default="local-folder")
    cloud_plan.add_argument("--output", required=True)

    grill_me = subparsers.add_parser("grill-me")
    grill_me.add_argument("--flow-id", required=True)
    grill_me.add_argument("--mode", default="beginner", choices=["beginner", "operator", "consultant"])
    grill_me.add_argument("--client-type", default="local-business")
    grill_me.add_argument(
        "--deployment",
        default="undecided",
        choices=["undecided", "local", "cloud", "render", "railway", "cloud-run", "vps"],
    )
    grill_me.add_argument("--connectors", default="local-folder")
    grill_me.add_argument("--output", required=True)

    report_automation = subparsers.add_parser("report-automation")
    report_automation.add_argument("--report-type", default="monthly", choices=["daily", "weekly", "monthly"])
    report_automation.add_argument("--past-outputs")
    report_automation.add_argument("--materials")
    report_automation.add_argument("--client-type", default="local-business")
    report_automation.add_argument("--niche", default="operations")
    report_automation.add_argument("--output", required=True)

    report_wizard = subparsers.add_parser("report-wizard")
    report_wizard_subparsers = report_wizard.add_subparsers(dest="report_wizard_command", required=True)

    report_wizard_init = report_wizard_subparsers.add_parser("init")
    report_wizard_init.add_argument("--workspace", required=True)
    report_wizard_init.add_argument("--report-type", default="monthly", choices=["daily", "weekly", "monthly"])
    report_wizard_init.add_argument("--language", default="ja", choices=["ja", "en"])

    report_wizard_inspect = report_wizard_subparsers.add_parser("inspect")
    report_wizard_inspect.add_argument("--workspace", required=True)
    report_wizard_inspect.add_argument("--past-outputs", nargs="+", default=[])
    report_wizard_inspect.add_argument("--materials", nargs="+", default=[])

    report_wizard_confirm = report_wizard_subparsers.add_parser("confirm")
    report_wizard_confirm.add_argument("--workspace", required=True)
    report_wizard_confirm.add_argument("--correction", action="append", default=[])

    report_wizard_answer = report_wizard_subparsers.add_parser("answer")
    report_wizard_answer.add_argument("--workspace", required=True)
    report_wizard_answer.add_argument("--answer")
    report_wizard_answer.add_argument("--skip", action="store_true")

    report_wizard_status = report_wizard_subparsers.add_parser("status")
    report_wizard_status.add_argument("--workspace", required=True)
    report_wizard_status.add_argument("--json", action="store_true")

    report_wizard_build = report_wizard_subparsers.add_parser("build")
    report_wizard_build.add_argument("--workspace", required=True)

    report_wizard_approve = report_wizard_subparsers.add_parser("approve")
    report_wizard_approve.add_argument("--workspace", required=True)
    report_wizard_approve.add_argument("--approver", required=True)

    report_wizard_serve = report_wizard_subparsers.add_parser("serve")
    report_wizard_serve.add_argument("--workspace", required=True)
    report_wizard_serve.add_argument("--language", default="ja", choices=["ja", "en"])
    report_wizard_serve.add_argument("--port", type=int, default=0)
    report_wizard_serve.add_argument("--no-open", action="store_true")

    flow_export = subparsers.add_parser("flow-export")
    flow_export.add_argument("--flow-id", required=True)
    flow_export.add_argument("--target", required=True, choices=["n8n", "activepieces", "windmill"])
    flow_export.add_argument("--output", required=True)

    deployment_pack = subparsers.add_parser("deployment-pack")
    deployment_pack.add_argument("--flow-id", required=True)
    deployment_pack.add_argument("--provider", required=True, choices=["coolify", "cloudflare-agents", "supabase"])
    deployment_pack.add_argument("--connectors", default="local-folder")
    deployment_pack.add_argument("--output", required=True)

    runtime_safety = subparsers.add_parser("runtime-safety")
    runtime_safety.add_argument("--flow-id", required=True)
    runtime_safety.add_argument("--output", required=True)

    secrets_bootstrap = subparsers.add_parser("secrets-bootstrap")
    secrets_bootstrap.add_argument("--flow-id", required=True)
    secrets_bootstrap.add_argument("--provider", required=True, choices=["infisical"])
    secrets_bootstrap.add_argument("--connectors", default="local-folder")
    secrets_bootstrap.add_argument("--output", required=True)

    document_intake = subparsers.add_parser("document-intake")
    document_intake.add_argument("--flow-id", required=True)
    document_intake.add_argument("--mode", default="fast", choices=["fast", "advanced"])
    document_intake.add_argument("--output", required=True)

    observability_pack = subparsers.add_parser("observability-pack")
    observability_pack.add_argument("--flow-id", required=True)
    observability_pack.add_argument("--output", required=True)

    state_backend = subparsers.add_parser("state-backend")
    state_backend.add_argument("--flow-id", required=True)
    state_backend.add_argument("--backend", required=True, choices=["supabase", "cloudflare-agents"])
    state_backend.add_argument("--output", required=True)

    flows = subparsers.add_parser("flows")
    flow_subparsers = flows.add_subparsers(dest="flow_command", required=True)

    flow_list = flow_subparsers.add_parser("list")
    flow_list.add_argument("--industry")
    flow_list.add_argument("--genre")

    flow_show = flow_subparsers.add_parser("show")
    flow_show.add_argument("flow_id")

    flow_install = flow_subparsers.add_parser("install")
    flow_install.add_argument("flow_id")
    flow_install.add_argument("--output", required=True)

    flow_diagram = flow_subparsers.add_parser("diagram")
    flow_diagram.add_argument("flow_id")
    flow_diagram.add_argument("--output", required=True)

    flow_validate = flow_subparsers.add_parser("validate")
    flow_validate.add_argument("path")

    flow_run = flow_subparsers.add_parser("run")
    flow_run.add_argument("path")
    flow_run.add_argument("--mode", default="dry-run", choices=["dry-run"])

    flow_approve = flow_subparsers.add_parser("approve")
    flow_approve.add_argument("path")
    flow_approve.add_argument("--approver", default="local-operator")

    docs_rag = subparsers.add_parser("docs-rag")
    docs_rag.add_argument("--config", required=True)
    docs_rag.add_argument("--output", required=True)

    internal = subparsers.add_parser("internal-ai-workflow")
    internal.add_argument("--config", required=True)
    internal.add_argument("--output", required=True)

    excel = subparsers.add_parser("excel-to-internal-app")
    excel.add_argument("--config", required=True)
    excel.add_argument("--output", required=True)

    delivery = subparsers.add_parser("delivery-pipeline")
    delivery.add_argument("--config", required=True)
    delivery.add_argument("--output", required=True)

    beginner = subparsers.add_parser("beginner")
    beginner.add_argument("--step", type=int, choices=[1, 2, 3, 4, 5], default=None)

    doctor = subparsers.add_parser("doctor")
    doctor.add_argument("--output", required=True)
    doctor.add_argument("--check-github", action="store_true")

    return parser


def _parse_report_wizard_corrections(values: list[str]) -> dict[str, str]:
    corrections = {}
    for value in values:
        if "=" not in value:
            raise ValueError("each --correction must use SOURCE=DEST")
        source, destination = value.split("=", 1)
        if not source or not destination:
            raise ValueError("each --correction must use SOURCE=DEST")
        corrections[source] = destination
    return corrections


def _print_report_wizard_state(state: dict, *, as_json: bool = False) -> None:
    if as_json:
        print(json.dumps(state, ensure_ascii=False, indent=2))
        return
    print(f"stage={state['stage']}")
    print(f"next_action={state['next_action']}")
    current_question = state.get("current_question")
    print("current_question_id={}".format(current_question["id"] if current_question else ""))
    for name, path in sorted(state.get("artifacts", {}).items()):
        print(f"artifact_{name}={path}")


def _run_report_wizard_command(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace)
    command = args.report_wizard_command

    try:
        if command == "init":
            state = create_session(workspace, args.report_type, args.language)
            _print_report_wizard_state(state)
            return 0
        if command == "inspect":
            state = inspect_session(
                workspace,
                [Path(path) for path in args.past_outputs],
                [Path(path) for path in args.materials],
            )
            _print_report_wizard_state(state)
            return 0
        if command == "confirm":
            corrections = _parse_report_wizard_corrections(args.correction)
            state = confirm_folder_plan(workspace, corrections or None)
            _print_report_wizard_state(state)
            return 0
        if command == "answer":
            if not args.skip and args.answer is None:
                print("provide --answer TEXT or use --skip", file=sys.stderr)
                return 2
            state = answer_current_question(workspace, args.answer or "", skipped=args.skip)
            _print_report_wizard_state(state)
            return 0
        if command == "status":
            state = session_status(workspace)
            _print_report_wizard_state(state, as_json=args.json)
            return 0
        if command == "build":
            state = build_report_workspace(workspace)
            _print_report_wizard_state(state)
            return 0 if state["stage"] == "ready_for_human_review" else 1
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if command == "approve":
        try:
            state = approve_report(workspace, args.approver)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        _print_report_wizard_state(state)
        return 0 if state["stage"] == "approved" else 1

    if command == "serve":
        try:
            module = importlib.import_module("ai_automation_kit.core.report_wizard_server")
            run_server = getattr(module, "run_report_wizard_server")
        except (ImportError, AttributeError) as exc:
            print(str(exc), file=sys.stderr)
            return 1
        run_server(workspace, args.language, args.port, open_browser=not args.no_open)
        return 0

    print("unknown report-wizard command", file=sys.stderr)
    return 2


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if argv == ["--version"]:
        print(f"ai-automation-kit {__version__}")
        return 0
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "report-wizard":
        return _run_report_wizard_command(args)
    if args.command == "research-agent":
        run = run_research_agent(config_path=args.config, output_dir=args.output)
        print(f"run_id={run.run_id}")
        print(f"status={run.status}")
        print(f"report={args.output}/report.md")
        return 0 if run.status == "succeeded" else 1
    if args.command == "github-discover":
        output = Path(args.output)
        output.mkdir(parents=True, exist_ok=True)
        config_path = output / "github_discover_config.json"
        config = _build_github_discover_config(
            business_area=args.business_area,
            query=args.query,
            limit=args.limit,
            include_readme=args.include_readme,
        )
        config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        run = run_research_agent(config_path=config_path, output_dir=output)
        print(f"run_id={run.run_id}")
        print(f"status={run.status}")
        print(f"report={output}/report.md")
        for label, path in [
            ("candidates", output / "github_candidates.md"),
            ("business_plan", output / "business_automation_plan.md"),
        ]:
            if path.exists():
                print(f"{label}={path}")
        for line in _github_discover_output_hints(output):
            print(line)
        return 0 if run.status == "succeeded" else 1
    if args.command == "onboard":
        payload = _run_onboard(
            output=Path(args.output),
            business_area=args.business_area,
            query=args.query,
            limit=args.limit,
            include_readme=args.include_readme,
            check_github=args.check_github,
            create_offer_pack=args.create_offer_pack,
            client_type=args.client_type,
        )
        print(f"status={payload['run_status']}")
        print(f"onboarding_summary={Path(args.output) / 'onboarding_summary.md'}")
        if payload.get("offer_pack_dir"):
            print(f"offer_pack={payload['offer_pack_dir']}")
        for path in payload["next_read"]:
            print(f"next_read={Path(args.output) / path}")
        return 0 if payload["run_status"] == "succeeded" else 1
    if args.command == "offer-pack":
        payload = generate_offer_pack(
            source_output=Path(args.source_output),
            output=Path(args.output),
            business_area=args.business_area,
            client_type=args.client_type,
        )
        print(f"offer_pack={args.output}/README.md")
        print(f"proposal={args.output}/proposal.md")
        print(f"statement_of_work={args.output}/statement_of_work.md")
        print(f"status={payload['source_status']}")
        return 0
    if args.command == "client-ready":
        payload = generate_client_ready_pack(
            source_output=Path(args.source_output),
            output=Path(args.output),
            business_area=args.business_area,
            client_type=args.client_type,
            niche=args.niche,
        )
        print(f"client_ready={args.output}/README.md")
        print(f"roi_calculator={args.output}/roi_calculator.csv")
        print(f"maintenance_plan={args.output}/maintenance_plan.md")
        print(f"score={payload['score']['total']}")
        return 0
    if args.command == "beginner-sales":
        payload = generate_beginner_sales_pack(
            flow_id=args.flow_id,
            output=Path(args.output),
            client_type=args.client_type,
            niche=args.niche,
            industry=args.industry,
        )
        print(f"beginner_sales={args.output}/README.md")
        print(f"flow_gallery={args.output}/flow_gallery.html")
        print(f"selected_demo={args.output}/selected_flow_demo.html")
        print(f"proposal={args.output}/proposal_one_pager.md")
        print(f"score={payload['beginner_score']['total']}")
        return 0
    if args.command == "flow-guide":
        payload = generate_flow_guide(industry=args.industry, genre=args.genre, niche=args.niche, output=Path(args.output))
        print(f"flow_guide={args.output}/recommended_flows.md")
        print(f"count={payload['count']}")
        return 0
    if args.command == "quickstart":
        payload = generate_quickstart_workspace(
            flow_id=args.flow_id,
            industry=args.industry,
            client_type=args.client_type,
            niche=args.niche,
            output=Path(args.output),
        )
        print(f"quickstart={args.output}/START_HERE.md")
        print(f"flow_project={payload['flow_project']}")
        print(f"demo_site={payload['demo_site']}")
        return 0
    if args.command == "demo-site":
        payload = generate_demo_site(source=Path(args.source), output=Path(args.output), title=args.title)
        print(f"demo_site={args.output}/index.html")
        print(f"asset_count={payload['asset_count']}")
        return 0
    if args.command == "install-bundle":
        payload = generate_install_bundle(
            flow_id=args.flow_id,
            client_type=args.client_type,
            niche=args.niche,
            output=Path(args.output),
        )
        print(f"bundle={args.output}/bundle_index.md")
        print(f"flow_project={payload['flow_project']}")
        print(f"demo_site={payload['demo_site']}")
        return 0
    if args.command == "connector-doctor":
        payload = generate_connector_doctor(project=Path(args.project), output=Path(args.output))
        print(f"connector_doctor={args.output}/connector_doctor.md")
        print(f"status={payload['status']}")
        return 0 if payload["status"] in {"ready", "needs_setup"} else 1
    if args.command == "client-report":
        payload = generate_client_report(flow_project=Path(args.flow_project), output=Path(args.output))
        print(f"client_report={args.output}/client_report.md")
        print(f"status={payload['status']}")
        return 0 if payload["status"] == "ready" else 1
    if args.command == "package-client-demo":
        payload = package_client_demo(source=Path(args.source), output=Path(args.output))
        print(f"client_demo_package={args.output}/client_demo_package.zip")
        print(f"file_count={payload['file_count']}")
        return 0
    if args.command == "complete-workspace":
        payload = generate_complete_workspace(
            flow_id=args.flow_id,
            industry=args.industry,
            client_type=args.client_type,
            niche=args.niche,
            approver=args.approver,
            output=Path(args.output),
        )
        print(f"final_delivery_guide={args.output}/FINAL_DELIVERY_GUIDE.md")
        print(f"completion_checklist={args.output}/completion_checklist.md")
        print(f"client_demo_package={payload['client_demo_package']}")
        print(f"status={payload['status']}")
        return 0 if payload["status"] == "ready_to_share" else 1
    if args.command == "opportunity-catalog":
        payload = generate_opportunity_catalog(industry=args.industry, output=Path(args.output))
        print(f"opportunity_catalog={args.output}/opportunity_catalog.html")
        print(f"count={payload['count']}")
        return 0
    if args.command == "recommend-flow":
        payload = generate_recommended_flow_from_intake(
            industry=args.industry,
            pain=args.pain,
            tools=args.tools,
            monthly_items=args.monthly_items,
            output=Path(args.output),
        )
        print(f"recommended_flow={args.output}/recommended_flow.md")
        print(f"flow_id={payload['recommended_flow']['id']}")
        return 0
    if args.command == "share-check":
        payload = generate_share_check(source=Path(args.source), output=Path(args.output))
        print(f"share_check={args.output}/share_check.md")
        print(f"status={payload['status']}")
        return 0 if payload["status"] in {"ready", "warning"} else 1
    if args.command == "business-launch":
        payload = generate_business_launch_pack(
            industry=args.industry,
            client_type=args.client_type,
            niche=args.niche,
            operator_level=args.operator_level,
            output=Path(args.output),
        )
        print(f"business_launch={args.output}/START_HERE_BUSINESS_LAUNCH.md")
        print(f"first_client_offer={args.output}/first_client_offer.md")
        print(f"recommended_flow={payload['recommended_flow']['id']}")
        print(f"status={payload['status']}")
        return 0
    if args.command == "website-side-hustle":
        payload = generate_website_side_hustle_pack(
            industry=args.industry,
            client_type=args.client_type,
            niche=args.niche,
            operator_level=args.operator_level,
            output=Path(args.output),
        )
        print(f"website_side_hustle={args.output}/START_HERE_WEBSITE_SIDE_HUSTLE.md")
        print(f"proposal={args.output}/proposal_one_pager.md")
        print(f"sample_site={args.output}/sample_site/index.html")
        print(f"status={payload['status']}")
        return 0
    if args.command == "side-hustle-blueprints":
        payload = generate_side_hustle_blueprints(
            industry=args.industry,
            operator_level=args.operator_level,
            output=Path(args.output),
        )
        print(f"side_hustle_blueprints={args.output}/START_HERE_SIDE_HUSTLE_BLUEPRINTS.md")
        print(f"first_client_picker={args.output}/first_client_picker.md")
        print(f"catalog={args.output}/side_hustle_blueprints.html")
        print(f"count={payload['count']}")
        print(f"status={payload['status']}")
        return 0
    if args.command == "command-center":
        payload = generate_command_center(output=Path(args.output), language=args.language)
        print(f"command_center={args.output}/START_HERE_COMMAND_CENTER.md")
        print(f"menu={args.output}/command_center.html")
        print(f"status={payload['status']}")
        return 0
    if args.command == "skill-pack":
        payload = generate_skill_pack(flow_id=args.flow_id, agent=args.agent, output=Path(args.output))
        print(f"skill_pack={args.output}/SKILL.md")
        print(f"agent_usage={args.output}/agent_usage.md")
        print(f"status={payload['status']}")
        return 0
    if args.command == "approval-gate":
        payload = generate_approval_gate(flow_id=args.flow_id, output=Path(args.output))
        print(f"approval_gate={args.output}/approval_gate.json")
        print(f"approval_policy={args.output}/approval_policy.md")
        print(f"status={payload['status']}")
        return 0
    if args.command == "mcp-connector-plan":
        payload = generate_mcp_connector_plan(flow_id=args.flow_id, connectors=args.connectors, output=Path(args.output))
        print(f"mcp_connector_plan={args.output}/mcp_connector_plan.md")
        print(f"env_request_list={args.output}/env_request_list.md")
        print(f"status={payload['status']}")
        return 0
    if args.command == "agent-team":
        payload = generate_agent_team(flow_id=args.flow_id, output=Path(args.output))
        print(f"agent_team={args.output}/agent_team_roles.md")
        print(f"handoff={args.output}/agent_handoff_protocol.md")
        print(f"status={payload['status']}")
        return 0
    if args.command == "workflow-explainer":
        payload = generate_workflow_explainer(flow_id=args.flow_id, audience=args.audience, output=Path(args.output))
        print(f"workflow_explainer={args.output}/workflow_explainer.html")
        print(f"workflow_map={args.output}/workflow_map.mmd")
        print(f"status={payload['status']}")
        return 0
    if args.command == "eval-loop":
        payload = generate_eval_loop(flow_id=args.flow_id, metric=args.metric, output=Path(args.output))
        print(f"eval_loop={args.output}/eval_loop.json")
        print(f"eval_dataset={args.output}/eval_dataset.csv")
        print(f"status={payload['status']}")
        return 0
    if args.command == "self-host-pack":
        payload = generate_self_host_pack(flow_id=args.flow_id, provider=args.provider, output=Path(args.output))
        print(f"self_host_pack={args.output}/self_host_runbook.md")
        print(f"docker_compose_plan={args.output}/docker_compose_plan.md")
        print(f"status={payload['status']}")
        return 0
    if args.command == "connector-catalog":
        payload = generate_connector_catalog(industry=args.industry, output=Path(args.output))
        print(f"connector_catalog={args.output}/connector_piece_catalog.md")
        print(f"connector_matrix={args.output}/connector_selection_matrix.csv")
        print(f"status={payload['status']}")
        return 0
    if args.command == "script-ui-pack":
        payload = generate_script_ui_pack(flow_id=args.flow_id, output=Path(args.output))
        print(f"script_ui_pack={args.output}/script_to_ui_plan.md")
        print(f"operator_form_schema={args.output}/operator_form_schema.json")
        print(f"status={payload['status']}")
        return 0
    if args.command == "knowledge-rag-pack":
        payload = generate_knowledge_rag_pack(flow_id=args.flow_id, output=Path(args.output))
        print(f"knowledge_rag_pack={args.output}/knowledge_base_pack.md")
        print(f"rag_answer_policy={args.output}/rag_answer_policy.md")
        print(f"status={payload['status']}")
        return 0
    if args.command == "automation-hooks":
        payload = generate_automation_hooks(flow_id=args.flow_id, output=Path(args.output))
        print(f"automation_hooks={args.output}/automation_hooks.md")
        print(f"preflight_checks={args.output}/preflight_checks.md")
        print(f"status={payload['status']}")
        return 0
    if args.command == "governance-pack":
        payload = generate_governance_pack(flow_id=args.flow_id, output=Path(args.output))
        print(f"governance_pack={args.output}/governance_pack.md")
        print(f"security_review={args.output}/security_review_checklist.md")
        print(f"status={payload['status']}")
        return 0
    if args.command == "guided-setup":
        payload = generate_guided_setup(
            flow_id=args.flow_id,
            mode=args.mode,
            deployment=args.deployment,
            connectors=args.connectors,
            output=Path(args.output),
        )
        print(f"guided_setup={args.output}/START_HERE_GUIDED_SETUP.md")
        print(f"questions={args.output}/guided_setup_questions.md")
        print(f"ai_agent_instruction={args.output}/ai_agent_instruction.md")
        print(f"status={payload['status']}")
        return 0
    if args.command == "guided-review":
        payload = generate_guided_review(answers=Path(args.answers), output=Path(args.output))
        print(f"guided_review={args.output}/START_HERE_GUIDED_REVIEW.md")
        print(f"setup_readiness_report={args.output}/setup_readiness_report.md")
        print(f"next_commands={args.output}/next_commands.md")
        print(f"status={payload['status']}")
        return 0
    if args.command == "cloud-plan":
        payload = generate_cloud_plan(
            flow_id=args.flow_id,
            provider=args.provider,
            workload=args.workload,
            connectors=args.connectors,
            output=Path(args.output),
        )
        print(f"cloud_plan={args.output}/START_HERE_CLOUD_PLAN.md")
        print(f"architecture={args.output}/workload_architecture.md")
        print(f"deploy_runbook={args.output}/deploy_runbook.md")
        print(f"provider={payload['provider']}")
        print(f"workload={payload['workload']}")
        print(f"status={payload['status']}")
        return 0
    if args.command == "grill-me":
        payload = generate_grill_me_pack(
            flow_id=args.flow_id,
            mode=args.mode,
            client_type=args.client_type,
            deployment=args.deployment,
            connectors=args.connectors,
            output=Path(args.output),
        )
        print(f"grill_me={args.output}/START_HERE_GRILL_ME.md")
        print(f"questions={args.output}/questions_to_answer.md")
        print(f"ai_agent_prompt={args.output}/ai_agent_prompt.md")
        print(f"flow_id={payload['flow_id']}")
        print(f"status={payload['status']}")
        return 0
    if args.command == "report-automation":
        payload = generate_report_automation_pack(
            report_type=args.report_type,
            past_outputs=Path(args.past_outputs) if args.past_outputs else None,
            materials=Path(args.materials) if args.materials else None,
            client_type=args.client_type,
            niche=args.niche,
            output=Path(args.output),
        )
        print(f"report_automation={args.output}/START_HERE_REPORT_AUTOMATION.md")
        print(f"ai_agent_prompt={args.output}/ai_agent_prompt.md")
        print(f"grill_me_questions={args.output}/05_grill_me_questions/questions.md")
        print(f"approval_checklist={args.output}/07_approval/approval_checklist.md")
        print(f"status={payload['status']}")
        return 0
    if args.command == "flow-export":
        payload = generate_flow_export(flow_id=args.flow_id, target=args.target, output=Path(args.output))
        print(f"flow_export={args.output}/START_HERE_FLOW_EXPORT.md")
        print(f"target={payload['target']}")
        return 0
    if args.command == "deployment-pack":
        payload = generate_deployment_pack(
            flow_id=args.flow_id,
            provider=args.provider,
            connectors=args.connectors,
            output=Path(args.output),
        )
        print(f"deployment_pack={args.output}/START_HERE_DEPLOYMENT_PACK.md")
        print(f"provider={payload['provider']}")
        return 0
    if args.command == "runtime-safety":
        payload = generate_runtime_safety_pack(flow_id=args.flow_id, output=Path(args.output))
        print(f"runtime_safety={args.output}/approval_policy.md")
        print(f"status={payload['status']}")
        return 0
    if args.command == "secrets-bootstrap":
        payload = generate_secrets_bootstrap(
            flow_id=args.flow_id,
            provider=args.provider,
            connectors=args.connectors,
            output=Path(args.output),
        )
        print(f"secrets_bootstrap={args.output}/secrets_manifest.json")
        print(f"provider={payload['provider']}")
        return 0
    if args.command == "document-intake":
        payload = generate_document_intake_pack(flow_id=args.flow_id, mode=args.mode, output=Path(args.output))
        print(f"document_intake={args.output}/START_HERE_DOCUMENT_INTAKE.md")
        print(f"mode={payload['mode']}")
        return 0
    if args.command == "observability-pack":
        payload = generate_observability_pack(flow_id=args.flow_id, output=Path(args.output))
        print(f"observability_pack={args.output}/observability_pack.json")
        print(f"status={payload['status']}")
        return 0
    if args.command == "state-backend":
        payload = generate_state_backend_pack(flow_id=args.flow_id, backend=args.backend, output=Path(args.output))
        print(f"state_backend={args.output}/START_HERE_STATE_BACKEND.md")
        print(f"backend={payload['backend']}")
        return 0
    if args.command == "flows":
        if args.flow_command == "list":
            flows = list_flows(industry=args.industry, genre=args.genre)
            for flow in flows:
                print(f"{flow['id']}\t{flow['industry']}\t{flow['genre']}\t{flow['name']}")
            print(f"count={len(flows)}")
            return 0
        if args.flow_command == "show":
            try:
                flow = get_flow(args.flow_id)
            except KeyError as exc:
                print(str(exc), file=sys.stderr)
                return 1
            print(json.dumps(flow, ensure_ascii=False, indent=2))
            return 0
        if args.flow_command == "install":
            try:
                payload = install_flow(args.flow_id, Path(args.output))
            except KeyError as exc:
                print(str(exc), file=sys.stderr)
                return 1
            diagram_path = write_flow_diagram(get_flow(args.flow_id), Path(args.output))
            print(f"flow_project={args.output}")
            print(f"flow_id={payload['flow_id']}")
            print(f"workflow_map={Path(args.output) / 'workflow_map.mmd'}")
            print(f"flow_yaml={Path(args.output) / 'flow.yaml'}")
            print(f"flow_diagram={diagram_path}")
            return 0
        if args.flow_command == "diagram":
            try:
                flow = get_flow(args.flow_id)
            except KeyError as exc:
                print(str(exc), file=sys.stderr)
                return 1
            diagram_path = write_flow_diagram(flow, Path(args.output))
            print(f"flow_diagram={diagram_path}")
            return 0
        if args.flow_command == "validate":
            result = validate_flow_project(Path(args.path))
            print(f"status={result['status']}")
            for missing in result["missing"]:
                print(f"missing={missing}")
            return 0 if result["status"] == "ready" else 1
        if args.flow_command == "run":
            payload = run_flow_project(Path(args.path), mode=args.mode)
            output_dir = Path(args.path) / "automation_output"
            print(f"automation_status={payload['status']}")
            print(f"rows_processed={payload['rows_processed']}")
            print(f"work_queue={output_dir / 'work_queue.csv'}")
            print(f"draft_outputs={output_dir / 'draft_outputs.md'}")
            print(f"approval_queue={output_dir / 'approval_queue.csv'}")
            print(f"status_report={output_dir / 'status_report.md'}")
            return 0 if payload["status"] == "succeeded" else 1
        if args.flow_command == "approve":
            payload = approve_all_pending(Path(args.path), approver=args.approver)
            print(f"approval_status={payload['status']}")
            print(f"approved_items={payload['approved_items']}")
            for path in payload["outbox"]:
                print(f"outbox={path}")
            return 0 if payload["status"] == "approved" else 1
    if args.command == "docs-rag":
        run = run_docs_rag(config_path=args.config, output_dir=args.output)
        print(f"run_id={run.run_id}")
        print(f"status={run.status}")
        print(f"answer={args.output}/answer.md")
        return 0 if run.status == "succeeded" else 1
    if args.command == "internal-ai-workflow":
        run = run_internal_ai_workflow(config_path=args.config, output_dir=args.output)
        print(f"run_id={run.run_id}")
        print(f"status={run.status}")
        print(f"draft={args.output}/draft_reply.md")
        return 0 if run.status == "succeeded" else 1
    if args.command == "excel-to-internal-app":
        run = run_excel_to_internal_app(config_path=args.config, output_dir=args.output)
        print(f"run_id={run.run_id}")
        print(f"status={run.status}")
        print(f"schema={args.output}/schema.sql")
        return 0 if run.status == "succeeded" else 1
    if args.command == "delivery-pipeline":
        run = run_delivery_pipeline(config_path=args.config, output_dir=args.output)
        print(f"run_id={run.run_id}")
        print(f"status={run.status}")
        print(f"checklist={args.output}/docs/delivery-checklist.md")
        return 0 if run.status == "succeeded" else 1
    if args.command == "beginner":
        if args.step is None:
            print(render_beginner_overview())
        else:
            print(render_beginner_step(args.step))
        return 0
    if args.command == "doctor":
        payload = _run_doctor(output_dir=Path(args.output), check_github=args.check_github)
        print(f"status={payload['status']}")
        print(f"report={args.output}/doctor_report.md")
        return 0 if payload["status"] in {"ready", "warning"} else 1
    return 0


def _build_github_discover_config(
    business_area: str,
    query: str | None,
    limit: int,
    include_readme: bool,
) -> dict:
    safe_limit = max(1, min(25, limit))
    search_queries = [query] if query else _default_business_queries(business_area)
    return {
        "topic": f"GitHub discovery for {business_area} automation",
        "business_context": {"business_area": business_area},
        "github_searches": [
            {
                "query": search_query,
                "sort": "stars",
                "order": "desc",
                "per_page": safe_limit,
            }
            for search_query in search_queries
        ],
        "include_readme": include_readme,
    }


def _github_discover_output_hints(output: Path) -> list[str]:
    hints = []
    artifact_index = output / "artifact_index.md"
    if artifact_index.exists():
        hints.append(f"artifact_index={artifact_index}")

    candidates = [
        output / "adapter_starter" / "README.md",
        output / "manual_review_pack.md",
        output / "query_recovery.md",
        output / "business_automation_plan.md",
        output / "report.md",
    ]
    for path in candidates:
        if path.exists():
            hints.append(f"next_read={path}")
            break
    return hints


def _run_onboard(
    output: Path,
    business_area: str,
    query: str | None,
    limit: int,
    include_readme: bool,
    check_github: bool,
    create_offer_pack: bool = False,
    client_type: str = "small-business",
) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    doctor_payload = _run_doctor(output_dir=output / "doctor", check_github=check_github)
    config = _build_github_discover_config(
        business_area=business_area,
        query=query,
        limit=limit,
        include_readme=include_readme,
    )
    config_path = output / "github_discover_config.json"
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    run = run_research_agent(config_path=config_path, output_dir=output)
    offer_pack_dir = None
    if create_offer_pack:
        offer_pack_dir = output / "offer_pack"
        generate_offer_pack(
            source_output=output,
            output=offer_pack_dir,
            business_area=business_area,
            client_type=client_type,
        )
    payload = {
        "status": "ready" if run.status == "succeeded" and doctor_payload["status"] in {"ready", "warning"} else "needs_attention",
        "business_area": business_area,
        "output_dir": str(output),
        "doctor_status": doctor_payload["status"],
        "run_status": run.status,
        "run_id": run.run_id,
        "next_read": _onboarding_next_read(output),
        "next_actions": _onboarding_next_actions(output, run.status, doctor_payload),
        "rerun_command": _onboarding_rerun_command(business_area, query, limit, output, include_readme, check_github),
    }
    if offer_pack_dir:
        payload["offer_pack_dir"] = str(offer_pack_dir)
    (output / "onboarding_summary.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "onboarding_summary.md").write_text(_render_onboarding_summary(payload), encoding="utf-8")
    return payload


def _onboarding_next_read(output: Path) -> list[str]:
    priority = [
        "run_summary.md",
        "executive_decision_brief.md",
        "pilot_scorecard.csv",
        "artifact_index.md",
        "adapter_starter/README.md",
        "manual_review_pack.md",
        "query_recovery.md",
        "business_automation_plan.md",
        "offer_pack/README.md",
        "report.md",
        "doctor/doctor_report.md",
    ]
    return [path for path in priority if (output / path).exists()]


def _onboarding_next_actions(output: Path, run_status: str, doctor_payload: dict) -> list[str]:
    actions = []
    if run_status != "succeeded":
        actions.append("Open `query_recovery.md` or `run_summary.md`, then rerun with a narrower `--query`.")
    if (output / "pilot_scorecard.csv").exists():
        actions.append("Use `pilot_scorecard.csv` to choose one workflow for a small internal pilot.")
    if (output / "adapter_starter" / "README.md").exists():
        actions.append("Open `adapter_starter/README.md` and connect the generated adapter to one real business data source.")
    actions.extend(doctor_payload.get("next_actions", []))
    if not actions:
        actions.append("Open `artifact_index.md` and choose the first workflow to test with real business data.")
    return actions


def _onboarding_rerun_command(
    business_area: str,
    query: str | None,
    limit: int,
    output: Path,
    include_readme: bool,
    check_github: bool,
) -> str:
    parts = [
        "ai-automation-kit",
        "onboard",
        "--business-area",
        business_area,
        "--limit",
        str(max(1, min(25, limit))),
        "--output",
        str(output),
    ]
    if query:
        parts.extend(["--query", query])
    if include_readme:
        parts.append("--include-readme")
    if check_github:
        parts.append("--check-github")
    return " ".join(parts)


def _render_onboarding_summary(payload: dict) -> str:
    lines = [
        "# AI Automation Starter Kit Onboarding Summary",
        "",
        f"- Status: `{payload['status']}`",
        f"- Business area: `{payload['business_area']}`",
        f"- Doctor status: `{payload['doctor_status']}`",
        f"- Research run status: `{payload['run_status']}`",
        f"- Run ID: `{payload['run_id']}`",
        "",
        "## What Happened",
        "",
        "The onboarding command checked the local environment, generated a GitHub discovery configuration, ran the discovery workflow, and collected the first files to read.",
        "",
        "## Read Next",
        "",
    ]
    if payload["next_read"]:
        lines.extend(f"- `{path}`" for path in payload["next_read"])
    else:
        lines.append("- No readable output files were generated. Check the run status and recovery notes.")
    lines.extend(["", "## Recommended Next Actions", ""])
    lines.extend(f"- {action}" for action in payload["next_actions"])
    lines.extend(["", "## Rerun Command", "", "```bash", payload["rerun_command"], "```", ""])
    return "\n".join(lines)


def _default_business_queries(business_area: str) -> list[str]:
    terms = {
        "sales": ["sales automation crm stars:>100", "crm workflow automation stars:>100", "lead generation automation stars:>100"],
        "support": ["customer support helpdesk stars:>100", "support chatbot automation stars:>100", "ticket automation ai stars:>100"],
        "finance": ["invoice accounting finance automation stars:>100", "expense report automation stars:>100", "spreadsheet finance automation stars:>100"],
        "operations": ["workflow automation orchestration stars:>100", "business process automation stars:>100", "agent orchestration automation stars:>100"],
        "marketing": ["marketing automation content stars:>100", "seo content automation stars:>100", "email campaign automation stars:>100"],
        "hr": ["recruiting onboarding hr automation stars:>100", "resume screening automation stars:>100", "employee onboarding automation stars:>100"],
    }
    return terms.get(business_area, [f"{business_area} automation stars:>100", f"{business_area} ai-agent stars:>100"])


def _run_doctor(output_dir: Path, check_github: bool) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    checks = [
        _doctor_check("python_version", sys.version_info >= (3, 9), f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"),
        _doctor_check("pip_available", shutil.which("pip") is not None or shutil.which("pip3") is not None, "pip or pip3 on PATH"),
        _doctor_check("output_writable", _can_write(output_dir), str(output_dir)),
        _doctor_check("git_available", shutil.which("git") is not None, "git on PATH"),
        _doctor_check("package_metadata", _package_metadata_ready(), "pyproject.toml, README.md, and LICENSE are present"),
        _doctor_check("console_script", _console_script_ready(), "ai-automation-kit console script is declared"),
        {
            "name": "github_token",
            "status": "pass" if os.environ.get("GITHUB_TOKEN") else "warn",
            "detail": "GITHUB_TOKEN is set" if os.environ.get("GITHUB_TOKEN") else "GITHUB_TOKEN is not set; public unauthenticated GitHub requests still work with lower limits.",
        },
        _doctor_check("env_files_ignored", Path(".gitignore").exists() and ".env" in Path(".gitignore").read_text(encoding="utf-8"), ".gitignore protects local env files"),
        _doctor_check("package_installed", _package_installed(), "ai_automation_kit package is importable"),
    ]
    if check_github:
        checks.append(_github_doctor_check())
    for check in checks:
        if check["status"] != "pass":
            remedy = _DOCTOR_REMEDIES_JA.get(check["name"])
            if remedy:
                check["remedy_ja"] = remedy
    status = "ready"
    if any(check["status"] == "fail" for check in checks):
        status = "blocked"
    elif any(check["status"] == "warn" for check in checks):
        status = "warning"
    payload = {
        "status": status,
        "checks": checks,
        "next_actions": _doctor_next_actions(checks),
    }
    (output_dir / "doctor_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_dir / "doctor_report.md").write_text(_render_doctor_report(payload), encoding="utf-8")
    return payload


def _doctor_check(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "status": "pass" if passed else "fail", "detail": detail}


# NG 項目ごとの日本語の対処法（初心者向け。専門用語には一言説明を添える）。
_DOCTOR_REMEDIES_JA: dict = {
    "python_version": "Python（このキットを動かす実行環境）のバージョンが古いです。https://www.python.org/ から 3.9 以上をインストールし直してください。",
    "pip_available": "pip（Python 用のアプリ追加コマンド）が見つかりません。ターミナルで `python3 -m ensurepip --upgrade` を実行してください。",
    "output_writable": "出力先フォルダに書き込みできません。別のフォルダを --output に指定するか、フォルダの権限（書き込み許可）を確認してください。",
    "git_available": "git（ファイルの変更履歴を管理するツール）が見つかりません。macOS はターミナルで `xcode-select --install`、Windows は https://git-scm.com/ からインストールしてください。",
    "package_metadata": "パッケージ情報（pyproject.toml / README.md / LICENSE）が見つかりません。このキットのリポジトリ（プロジェクトのフォルダ）の直下で実行してください。",
    "console_script": "コマンド登録の設定が見つかりません。リポジトリ直下で `pip install -e .`（開発モードでのインストール）を実行し直してください。",
    "github_token": "GITHUB_TOKEN（GitHub 用の認証キー）が未設定です。無くても動きますが、たくさん検索する場合は `export GITHUB_TOKEN=...` で設定してください。",
    "env_files_ignored": ".gitignore（Git に含めないファイルの一覧）に `.env` がありません。認証情報の誤コミットを防ぐため、.gitignore に `.env` の行を追加してください。",
    "package_installed": "本パッケージ（ai-automation-kit）がまだインストールされていません。リポジトリ直下で `pip install -e .` を実行してください。",
    "github_api": "GitHub への接続に失敗しました。インターネット接続を確認し、社内ネットワークの場合はプロキシ（中継サーバー）の設定を確認してください。",
}


def _package_installed() -> bool:
    try:
        import importlib.util

        return importlib.util.find_spec("ai_automation_kit") is not None
    except (ImportError, ValueError):
        return False


def _github_doctor_check() -> dict:
    try:
        from ai_automation_kit.core.github import search_github_repositories

        result = search_github_repositories(
            query="workflow automation stars:>100",
            sort="stars",
            order="desc",
            per_page=1,
            token=os.environ.get("GITHUB_TOKEN"),
        )
        return {
            "name": "github_api",
            "status": "pass" if result.get("repositories") else "warn",
            "detail": f"GitHub search returned {len(result.get('repositories', []))} repositories; rate remaining {result.get('rate_limit_remaining')}.",
        }
    except Exception as exc:  # noqa: BLE001 - doctor reports the problem instead of hiding it.
        return {"name": "github_api", "status": "fail", "detail": str(exc)}


def _can_write(path: Path) -> bool:
    try:
        probe = path / ".doctor-write-test"
        probe.write_text("ok\n", encoding="utf-8")
        probe.unlink()
        return True
    except OSError:
        return False


def _package_metadata_ready() -> bool:
    pyproject = Path("pyproject.toml")
    return (
        pyproject.exists()
        and Path("README.md").exists()
        and Path("LICENSE").exists()
        and 'readme = "README.md"' in pyproject.read_text(encoding="utf-8")
    )


def _console_script_ready() -> bool:
    pyproject = Path("pyproject.toml")
    setup_py = Path("setup.py")
    pyproject_ready = pyproject.exists() and 'ai-automation-kit = "ai_automation_kit.cli:main"' in pyproject.read_text(encoding="utf-8")
    setup_ready = setup_py.exists() and "ai-automation-kit=ai_automation_kit.cli:main" in setup_py.read_text(encoding="utf-8")
    return pyproject_ready and setup_ready


def _doctor_next_actions(checks: list[dict]) -> list[str]:
    actions = []
    for check in checks:
        if check["status"] == "fail":
            actions.append(f"Fix `{check['name']}` before running business automation workflows.")
        if check["name"] == "github_token" and check["status"] == "warn":
            actions.append("Set `GITHUB_TOKEN` when running many GitHub discovery searches.")
        if check["status"] != "pass" and check.get("remedy_ja"):
            actions.append(check["remedy_ja"])
    if not actions:
        actions.append("Run `ai-automation-kit github-discover --business-area operations --limit 2 --output .tmp/doctor-smoke` next.")
    return actions


def _render_doctor_report(payload: dict) -> str:
    lines = [
        "# AI Automation Starter Kit Doctor",
        "",
        f"- Status: `{payload['status']}`",
        "",
        "## Checks",
        "",
        "| Check | Status | Detail |",
        "|---|---|---|",
    ]
    for check in payload["checks"]:
        lines.append(f"| `{check['name']}` | `{check['status']}` | {check['detail']} |")
    remedies = [check for check in payload["checks"] if check["status"] != "pass" and check.get("remedy_ja")]
    if remedies:
        lines.extend(["", "## 対処法（日本語）", ""])
        for check in remedies:
            lines.append(f"- `{check['name']}`: {check['remedy_ja']}")
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- {action}" for action in payload["next_actions"])
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
