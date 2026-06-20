from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

from ai_automation_kit import __version__
from ai_automation_kit.core.beginner_sales import generate_beginner_sales_pack
from ai_automation_kit.core.client_ready import generate_client_ready_pack
from ai_automation_kit.core.flows import get_flow
from ai_automation_kit.core.flows import install_flow
from ai_automation_kit.core.flows import list_flows
from ai_automation_kit.core.flows import validate_flow_project
from ai_automation_kit.core.flow_runtime import approve_all_pending
from ai_automation_kit.core.flow_runtime import run_flow_project
from ai_automation_kit.core.offer_pack import generate_offer_pack
from ai_automation_kit.core.operator_console import generate_client_report
from ai_automation_kit.core.operator_console import generate_complete_workspace
from ai_automation_kit.core.operator_console import generate_connector_doctor
from ai_automation_kit.core.operator_console import generate_demo_site
from ai_automation_kit.core.operator_console import generate_flow_guide
from ai_automation_kit.core.operator_console import generate_install_bundle
from ai_automation_kit.core.operator_console import generate_business_launch_pack
from ai_automation_kit.core.operator_console import generate_opportunity_catalog
from ai_automation_kit.core.operator_console import generate_quickstart_workspace
from ai_automation_kit.core.operator_console import generate_recommended_flow_from_intake
from ai_automation_kit.core.operator_console import generate_share_check
from ai_automation_kit.core.operator_console import package_client_demo
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

    doctor = subparsers.add_parser("doctor")
    doctor.add_argument("--output", required=True)
    doctor.add_argument("--check-github", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if argv == ["--version"]:
        print(f"ai-automation-kit {__version__}")
        return 0
    parser = build_parser()
    args = parser.parse_args(argv)
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
            print(f"flow_project={args.output}")
            print(f"flow_id={payload['flow_id']}")
            print(f"workflow_map={Path(args.output) / 'workflow_map.mmd'}")
            print(f"flow_yaml={Path(args.output) / 'flow.yaml'}")
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
    ]
    if check_github:
        checks.append(_github_doctor_check())
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
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- {action}" for action in payload["next_actions"])
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
