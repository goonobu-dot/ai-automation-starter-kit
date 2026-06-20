from __future__ import annotations

import html
import json
import shutil
import zipfile
from pathlib import Path

from ai_automation_kit.core.beginner_sales import generate_beginner_sales_pack
from ai_automation_kit.core.client_ready import generate_client_ready_pack
from ai_automation_kit.core.flow_runtime import approve_all_pending
from ai_automation_kit.core.flow_runtime import run_flow_project
from ai_automation_kit.core.flows import get_flow
from ai_automation_kit.core.flows import install_flow
from ai_automation_kit.core.flows import list_flows


DEMO_EXTENSIONS = {".md", ".html", ".csv", ".json", ".mmd", ".yaml", ".yml", ".txt"}


def generate_flow_guide(industry: str | None, genre: str | None, niche: str, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    candidates = list_flows(industry=industry, genre=genre)
    if not candidates:
        candidates = list_flows()
    ranked = [_ranked_flow(flow, niche, index) for index, flow in enumerate(candidates[:20], start=1)]
    payload = {
        "industry": industry or "any",
        "genre": genre or "any",
        "niche": niche,
        "count": len(ranked),
        "recommended_flows": ranked,
    }
    (output / "recommended_flows.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "recommended_flows.md").write_text(_render_flow_guide(payload), encoding="utf-8")
    return payload


def generate_quickstart_workspace(
    flow_id: str | None,
    industry: str,
    client_type: str,
    niche: str,
    output: Path,
) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    selected_flow = get_flow(flow_id) if flow_id else get_flow(list_flows(industry=industry)[0]["id"])
    flow_dir = output / "flow_project"
    beginner_dir = output / "beginner_sales"
    install_flow(selected_flow["id"], flow_dir)
    generate_beginner_sales_pack(
        flow_id=selected_flow["id"],
        output=beginner_dir,
        client_type=client_type,
        niche=niche,
        industry=selected_flow["industry"],
    )
    generate_demo_site(source=output, output=output / "demo_site", title=f"{selected_flow['name']} Quickstart")
    payload = {
        "status": "ready",
        "flow_id": selected_flow["id"],
        "flow_project": str(flow_dir),
        "beginner_sales": str(beginner_dir),
        "demo_site": str(output / "demo_site" / "index.html"),
    }
    (output / "quickstart.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "START_HERE.md").write_text(_render_quickstart_start(selected_flow, payload), encoding="utf-8")
    return payload


def generate_demo_site(source: Path, output: Path, title: str = "Client Automation Demo") -> dict:
    output.mkdir(parents=True, exist_ok=True)
    assets = _collect_demo_assets(source)
    payload = {"status": "ready", "source": str(source), "output": str(output), "title": title, "asset_count": len(assets)}
    (output / "demo_site.json").write_text(json.dumps({**payload, "assets": assets}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "index.html").write_text(_render_demo_site(title, assets), encoding="utf-8")
    return payload


def generate_install_bundle(flow_id: str, client_type: str, niche: str, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    flow = get_flow(flow_id)
    flow_dir = output / "flow_project"
    beginner_dir = output / "beginner_sales"
    client_ready_dir = output / "client_ready"
    install_flow(flow_id, flow_dir)
    generate_beginner_sales_pack(flow_id=flow_id, output=beginner_dir, client_type=client_type, niche=niche, industry=flow["industry"])
    generate_client_ready_pack(
        source_output=beginner_dir,
        output=client_ready_dir,
        business_area=flow["industry"],
        client_type=client_type,
        niche=niche,
    )
    generate_demo_site(source=output, output=output / "demo_site", title=f"{flow['name']} Client Bundle")
    payload = {
        "status": "ready",
        "flow_id": flow_id,
        "flow_project": str(flow_dir),
        "beginner_sales": str(beginner_dir),
        "client_ready": str(client_ready_dir),
        "demo_site": str(output / "demo_site" / "index.html"),
    }
    (output / "install_bundle.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "bundle_index.md").write_text(_render_bundle_index(flow, payload), encoding="utf-8")
    return payload


def generate_connector_doctor(project: Path, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    config_path = project / "config" / "connectors.json"
    env_path = project / ".env"
    env_example_path = project / ".env.example"
    checks = []
    if config_path.exists():
        config = json.loads(config_path.read_text(encoding="utf-8"))
        for connector in config.get("connectors", []):
            checks.append(
                {
                    "id": connector.get("id"),
                    "type": connector.get("type"),
                    "status": "ready" if connector.get("enabled") and connector.get("production_safe") else "review",
                    "detail": "local dry-run connector",
                }
            )
        for connector in config.get("disabled_external_connectors", []):
            checks.append(
                {
                    "id": connector.get("id"),
                    "type": "external",
                    "status": "needs_setup",
                    "detail": connector.get("reason", "requires setup"),
                }
            )
    else:
        checks.append({"id": "connectors.json", "type": "config", "status": "missing", "detail": str(config_path)})
    checks.append(
        {
            "id": ".env",
            "type": "secrets",
            "status": "ready" if env_path.exists() else "needs_setup",
            "detail": ".env present" if env_path.exists() else f"Create from {env_example_path}",
        }
    )
    status = "ready" if all(check["status"] == "ready" for check in checks) else "needs_setup"
    payload = {"status": status, "project": str(project), "checks": checks}
    (output / "connector_doctor.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "connector_doctor.md").write_text(_render_connector_doctor(payload), encoding="utf-8")
    return payload


def generate_client_report(flow_project: Path, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    automation_dir = flow_project / "automation_output"
    run_log_path = automation_dir / "run_log.json"
    run_log = json.loads(run_log_path.read_text(encoding="utf-8")) if run_log_path.exists() else {}
    files = {
        "work_queue": automation_dir / "work_queue.csv",
        "draft_outputs": automation_dir / "draft_outputs.md",
        "approval_queue": automation_dir / "approval_queue.csv",
        "approved_actions": automation_dir / "approved_actions.csv",
        "status_report": automation_dir / "status_report.md",
    }
    payload = {
        "status": "ready" if run_log_path.exists() else "missing_run",
        "flow_project": str(flow_project),
        "rows_processed": run_log.get("rows_processed", 0),
        "automation_status": run_log.get("status", "unknown"),
        "available_files": {name: str(path) for name, path in files.items() if path.exists()},
    }
    (output / "client_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = _render_client_report(payload)
    (output / "client_report.md").write_text(report, encoding="utf-8")
    (output / "client_report.html").write_text(_markdown_shell_html("Client Automation Report", report), encoding="utf-8")
    return payload


def package_client_demo(source: Path, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    files = _collect_demo_file_paths(source)
    package_path = output / "client_demo_package.zip"
    with zipfile.ZipFile(package_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(source).as_posix())
    payload = {
        "status": "packaged",
        "source": str(source),
        "package": str(package_path),
        "file_count": len(files),
        "files": [path.relative_to(source).as_posix() for path in files],
    }
    (output / "client_demo_manifest.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "README.md").write_text(_render_package_readme(payload), encoding="utf-8")
    return payload


def generate_complete_workspace(
    flow_id: str | None,
    industry: str,
    client_type: str,
    niche: str,
    approver: str,
    output: Path,
) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    quickstart_dir = output / "quickstart"
    quickstart = generate_quickstart_workspace(
        flow_id=flow_id,
        industry=industry,
        client_type=client_type,
        niche=niche,
        output=quickstart_dir,
    )
    flow_project = quickstart_dir / "flow_project"
    run_payload = run_flow_project(flow_project)
    approval_payload = approve_all_pending(flow_project, approver=approver)
    connector = generate_connector_doctor(project=flow_project, output=output / "connector_doctor")
    report = generate_client_report(flow_project=flow_project, output=output / "client_report")
    demo = generate_demo_site(source=quickstart_dir, output=output / "demo_site", title="Ready-To-Share Automation Demo")
    package = package_client_demo(source=quickstart_dir, output=output / "client_demo_package")
    flow = get_flow(quickstart["flow_id"])
    payload = {
        "status": "ready_to_share" if run_payload["status"] == "succeeded" and approval_payload["status"] == "approved" else "needs_attention",
        "flow_id": quickstart["flow_id"],
        "flow_name": flow["name"],
        "industry": flow["industry"],
        "genre": flow["genre"],
        "client_type": client_type,
        "niche": niche,
        "quickstart": str(quickstart_dir),
        "flow_project": str(flow_project),
        "connector_doctor": str(output / "connector_doctor" / "connector_doctor.md"),
        "client_report": str(output / "client_report" / "client_report.md"),
        "demo_site": str(output / "demo_site" / "index.html"),
        "client_demo_package": str(output / "client_demo_package" / "client_demo_package.zip"),
        "rows_processed": run_payload["rows_processed"],
        "approved_items": approval_payload["approved_items"],
        "connector_status": connector["status"],
        "report_status": report["status"],
        "demo_asset_count": demo["asset_count"],
        "package_file_count": package["file_count"],
    }
    payload["revenue_score"] = _revenue_readiness_score(payload)
    (output / "delivery_manifest.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "FINAL_DELIVERY_GUIDE.md").write_text(_render_complete_delivery_guide(payload), encoding="utf-8")
    (output / "completion_checklist.md").write_text(_render_completion_checklist(payload), encoding="utf-8")
    (output / "revenue_readiness_scorecard.md").write_text(_render_revenue_scorecard(payload), encoding="utf-8")
    (output / "sales_closing_script.md").write_text(_render_sales_closing_script(payload), encoding="utf-8")
    (output / "paid_poc_scope.md").write_text(_render_paid_poc_scope(payload), encoding="utf-8")
    (output / "value_measurement_sheet.csv").write_text(_render_value_measurement_csv(payload), encoding="utf-8")
    (output / "pre_contract_checklist.md").write_text(_render_pre_contract_checklist(payload), encoding="utf-8")
    (output / "client_proposal_email.md").write_text(_render_client_proposal_email(payload), encoding="utf-8")
    (output / "first_30_days_plan.md").write_text(_render_first_30_days_plan(payload), encoding="utf-8")
    (output / "proof_of_value_template.md").write_text(_render_proof_of_value_template(payload), encoding="utf-8")
    return payload


def _ranked_flow(flow: dict, niche: str, index: int) -> dict:
    score = max(60, 101 - index * 3)
    if niche.lower() in {flow["industry"].lower(), flow["genre"].lower()}:
        score += 5
    return {**flow, "rank": index, "score": min(100, score)}


def _render_flow_guide(payload: dict) -> str:
    lines = [
        "# Flow Selection Guide",
        "",
        f"- Industry: `{payload['industry']}`",
        f"- Genre: `{payload['genre']}`",
        f"- Niche: `{payload['niche']}`",
        "",
        "| Rank | Score | Flow ID | Industry | Genre | Name |",
        "|---:|---:|---|---|---|---|",
    ]
    for flow in payload["recommended_flows"]:
        lines.append(
            f"| {flow['rank']} | {flow['score']} | `{flow['id']}` | {flow['industry']} | {flow['genre']} | {flow['name']} |"
        )
    lines.extend(
        [
            "",
            "## How To Choose",
            "",
            "- Start with a flow the client already understands.",
            "- Prefer workflows with clear input, approval owner, and measurable output.",
            "- Avoid production connectors until a dry-run proves value.",
            "",
        ]
    )
    return "\n".join(lines)


def _render_quickstart_start(flow: dict, payload: dict) -> str:
    return "\n".join(
        [
            f"# Quickstart Workspace: {flow['name']}",
            "",
            "## Run Order",
            "",
            "1. Open `beginner_sales/selected_flow_demo.html`.",
            "2. Read `beginner_sales/client_questions.md`.",
            "3. Run the local automation dry-run:",
            "",
            "```bash",
            "cd flow_project",
            "python3 scripts/run_automation.py",
            "python3 scripts/approve_all.py --approver owner@example.com",
            "```",
            "",
            "4. Open `flow_project/automation_output/status_report.md`.",
            "5. Open `demo_site/index.html` for the client-facing overview.",
            "",
            "## Generated Paths",
            "",
            f"- Flow project: `{payload['flow_project']}`",
            f"- Beginner sales: `{payload['beginner_sales']}`",
            f"- Demo site: `{payload['demo_site']}`",
            "",
        ]
    )


def _render_bundle_index(flow: dict, payload: dict) -> str:
    return "\n".join(
        [
            f"# Client Automation Bundle: {flow['name']}",
            "",
            "This folder combines the runnable dry-run flow, beginner sales materials, client-ready delivery assets, and demo site.",
            "",
            "## Contents",
            "",
            f"- `flow_project/`: local dry-run automation system for `{payload['flow_id']}`.",
            "- `beginner_sales/`: pitch, proposal, ROI calculator, and visual demo.",
            "- `client_ready/`: intake, pricing, security, maintenance, and handoff assets.",
            "- `demo_site/index.html`: browser-friendly overview for a client conversation.",
            "",
            "## Safety",
            "",
            "The default system writes local files only. Real connectors require separate approval, credentials, and data review.",
            "",
        ]
    )


def _render_connector_doctor(payload: dict) -> str:
    lines = ["# Connector Doctor", "", f"- Status: `{payload['status']}`", f"- Project: `{payload['project']}`", "", "| ID | Type | Status | Detail |", "|---|---|---|---|"]
    for check in payload["checks"]:
        lines.append(f"| `{check['id']}` | {check['type']} | `{check['status']}` | {check['detail']} |")
    lines.extend(
        [
            "",
            "## Next Step",
            "",
            "Keep local dry-run connectors enabled until the client approves data handling, credentials, rollback, and human approval rules.",
            "",
        ]
    )
    return "\n".join(lines)


def _render_client_report(payload: dict) -> str:
    lines = [
        "# Client Automation Report",
        "",
        f"- Status: `{payload['status']}`",
        f"- Automation status: `{payload['automation_status']}`",
        f"- Rows processed: `{payload['rows_processed']}`",
        "",
        "## Available Evidence",
        "",
    ]
    if payload["available_files"]:
        lines.extend(f"- `{name}`: `{path}`" for name, path in payload["available_files"].items())
    else:
        lines.append("- No automation output files were found. Run the flow before sharing this report.")
    lines.extend(
        [
            "",
            "## Client Review Questions",
            "",
            "- Is the queue understandable?",
            "- Are the drafts useful enough to revise?",
            "- Is the approval point correct?",
            "- Should this pilot continue, revise, or stop?",
            "",
        ]
    )
    return "\n".join(lines)


def _render_package_readme(payload: dict) -> str:
    return "\n".join(
        [
            "# Client Demo Package",
            "",
            f"- Status: `{payload['status']}`",
            f"- Files packaged: `{payload['file_count']}`",
            f"- Zip: `{payload['package']}`",
            "",
            "This package is for client review. Check that no private credentials or client secrets are included before sharing.",
            "",
        ]
    )


def _render_complete_delivery_guide(payload: dict) -> str:
    return "\n".join(
        [
            f"# Final Delivery Guide: {payload['flow_name']}",
            "",
            f"- Status: `{payload['status']}`",
            f"- Flow ID: `{payload['flow_id']}`",
            f"- Rows processed in dry-run: `{payload['rows_processed']}`",
            f"- Approved draft items: `{payload['approved_items']}`",
            f"- Connector status: `{payload['connector_status']}`",
            "",
            "## Open These Files In This Order",
            "",
            f"1. `{payload['quickstart']}/START_HERE.md`",
            f"2. `{payload['quickstart']}/beginner_sales/selected_flow_demo.html`",
            f"3. `{payload['client_report']}`",
            f"4. `{payload['demo_site']}`",
            f"5. `{payload['client_demo_package']}`",
            "6. `revenue_readiness_scorecard.md`",
            "7. `sales_closing_script.md`",
            "8. `paid_poc_scope.md`",
            "9. `value_measurement_sheet.csv`",
            "10. `pre_contract_checklist.md`",
            "11. `client_proposal_email.md`",
            "12. `first_30_days_plan.md`",
            "13. `proof_of_value_template.md`",
            "",
            "## What To Tell The Client",
            "",
            "- The first version runs locally and writes files only.",
            "- The workflow already produced a queue, drafts, approval records, and a readable report.",
            "- Real external sends, production updates, payments, access grants, and sensitive-data actions stay blocked until the client approves connectors and rollback rules.",
            "",
            "## Handoff Decision",
            "",
            "No next recommendation is required before review. The client can now choose one of three decisions: continue the pilot, revise the flow, or stop.",
            "",
        ]
    )


def _render_completion_checklist(payload: dict) -> str:
    checks = [
        ("Quickstart workspace created", payload["quickstart"]),
        ("Dry-run executed", f"rows_processed={payload['rows_processed']}"),
        ("Draft approvals exported", f"approved_items={payload['approved_items']}"),
        ("Connector setup checked", payload["connector_doctor"]),
        ("Client report generated", payload["client_report"]),
        ("Demo site generated", payload["demo_site"]),
        ("Client demo zip packaged", payload["client_demo_package"]),
        ("Revenue readiness scored", f"score={payload['revenue_score']['total']}"),
        ("Paid PoC scope prepared", "paid_poc_scope.md"),
        ("Value measurement sheet prepared", "value_measurement_sheet.csv"),
        ("Pre-contract checklist prepared", "pre_contract_checklist.md"),
        ("Client proposal email prepared", "client_proposal_email.md"),
        ("First 30 days plan prepared", "first_30_days_plan.md"),
        ("Proof of value template prepared", "proof_of_value_template.md"),
    ]
    lines = ["# Completion Checklist", ""]
    for label, detail in checks:
        lines.append(f"- [x] {label}: `{detail}`")
    lines.extend(
        [
            "",
            "## Before Sharing Outside Your Machine",
            "",
            "- [ ] Confirm the zip contains no secrets or client private data.",
            "- [ ] Confirm the client understands this is a dry-run until real connectors are approved.",
            "- [ ] Confirm the client has one named approval owner.",
            "",
        ]
    )
    return "\n".join(lines)


def _revenue_readiness_score(payload: dict) -> dict:
    criteria = [
        ("visible_demo", 15, payload["demo_asset_count"] > 0, "Demo site and visual flow assets exist."),
        ("working_dry_run", 20, payload["rows_processed"] > 0, "The local flow produced dry-run evidence."),
        ("approval_evidence", 15, payload["approved_items"] > 0, "Approval records and local outbox files exist."),
        ("client_report", 15, payload["report_status"] == "ready", "Client-readable report exists."),
        ("safe_boundary", 15, payload["connector_status"] in {"needs_setup", "ready"}, "Production connectors are explicitly gated."),
        ("share_package", 10, payload["package_file_count"] > 0, "Shareable demo package exists."),
        ("paid_scope", 10, True, "Paid PoC scope, closing script, and value sheet are generated."),
    ]
    items = [
        {"id": item_id, "points": points if passed else 0, "max_points": points, "passed": passed, "evidence": evidence}
        for item_id, points, passed, evidence in criteria
    ]
    total = sum(item["points"] for item in items)
    level = "sellable_poc" if total >= 85 else "review_before_selling" if total >= 70 else "not_ready"
    return {"total": total, "level": level, "items": items}


def _render_revenue_scorecard(payload: dict) -> str:
    score = payload["revenue_score"]
    lines = [
        "# Revenue Readiness Scorecard",
        "",
        f"- Flow: `{payload['flow_name']}`",
        f"- Niche: `{payload['niche']}`",
        f"- Score: `{score['total']}/100`",
        f"- Level: `{score['level']}`",
        "",
        "## Score Detail",
        "",
        "| Item | Points | Evidence |",
        "|---|---:|---|",
    ]
    for item in score["items"]:
        lines.append(f"| `{item['id']}` | {item['points']}/{item['max_points']} | {item['evidence']} |")
    lines.extend(
        [
            "",
            "## Paid PoC Positioning",
            "",
            "This is ready to sell as a bounded Paid PoC when the client accepts three limits: local dry-run first, human approval before external actions, and measurable baseline comparison.",
            "",
            "## Do Not Sell As",
            "",
            "- Fully autonomous production automation.",
            "- Guaranteed income system.",
            "- A replacement for client approval, credentials review, or legal/security review.",
            "",
        ]
    )
    return "\n".join(lines)


def _render_sales_closing_script(payload: dict) -> str:
    return "\n".join(
        [
            f"# Sales Closing Script: {payload['flow_name']}",
            "",
            "## Opening",
            "",
            f"I prepared a local dry-run for your {payload['niche']} workflow. It does not send messages or update production systems, but it shows the queue, draft outputs, approval points, and report evidence.",
            "",
            "## Proof To Show",
            "",
            f"- Demo site: `{payload['demo_site']}`",
            f"- Client report: `{payload['client_report']}`",
            f"- Approval evidence: `{payload['quickstart']}/flow_project/automation_output/approved_actions.csv`",
            f"- Local outbox: `{payload['quickstart']}/flow_project/local_outbox/email_drafts.md`",
            "",
            "## Close",
            "",
            "If this matches the real workflow, the next paid step is a small PoC: we connect one approved sample data source, keep human approval, measure time saved, and decide whether to continue.",
            "",
            "## Buyer Questions",
            "",
            "- Who owns this workflow today?",
            "- How many items are processed each week?",
            "- What mistakes or delays are most expensive?",
            "- Who must approve before anything reaches a customer or production system?",
            "- What result would make a paid PoC worth continuing?",
            "",
        ]
    )


def _render_paid_poc_scope(payload: dict) -> str:
    return "\n".join(
        [
            f"# Paid PoC Scope: {payload['flow_name']}",
            "",
            "## Objective",
            "",
            f"Validate whether `{payload['flow_id']}` can reduce repeated manual work for a {payload['client_type']} without bypassing human approval.",
            "",
            "## Included",
            "",
            "- One workflow map and before/after explanation.",
            "- One approved sample input source or CSV export.",
            "- Local dry-run automation with queue, drafts, approval list, and report.",
            "- Connector readiness review.",
            "- One value measurement sheet.",
            "- One handoff call or written handoff note.",
            "",
            "## Excluded Until Separate Approval",
            "",
            "- Production sends or writes.",
            "- Payment, hiring, access, or legal decisions.",
            "- Handling secrets or regulated personal data without a data review.",
            "- Ongoing monitoring beyond the PoC window.",
            "",
            "## Acceptance Criteria",
            "",
            "- The client can identify the queue and approval owner.",
            "- The dry-run output is useful enough to revise rather than discard.",
            "- The value sheet has baseline time, pilot time, and decision notes.",
            "- The client chooses continue, revise, or stop.",
            "",
        ]
    )


def _render_value_measurement_csv(payload: dict) -> str:
    rows = [
        ["metric", "example_value", "owner", "notes"],
        ["manual_items_per_month", "80", "client", "Ask for current monthly volume."],
        ["manual_minutes_per_item", "8", "client", "Baseline before automation."],
        ["pilot_minutes_per_item", "4", "operator", "Measured during dry-run PoC."],
        ["loaded_hourly_cost", "35", "client", "Use realistic labor cost."],
        ["monthly_tool_cost", "0", "operator", "Local dry-run starts at zero tool cost."],
        ["estimated_monthly_hours_saved", "=manual_items_per_month*(manual_minutes_per_item-pilot_minutes_per_item)/60", "sheet", "Formula for spreadsheet users."],
        ["estimated_monthly_savings", "=estimated_monthly_hours_saved*loaded_hourly_cost-monthly_tool_cost", "sheet", "Use as directional estimate, not guarantee."],
        ["pilot_fee_floor", "=estimated_monthly_savings*1.5", "operator", "Sanity check for PoC pricing discussion."],
        ["continue_threshold", "client says output is useful and measurable", "client", "Continue only if value and safety are visible."],
    ]
    return "\n".join(",".join(str(cell) for cell in row) for row in rows) + "\n"


def _render_pre_contract_checklist(payload: dict) -> str:
    return "\n".join(
        [
            f"# Pre-Contract Checklist: {payload['flow_name']}",
            "",
            "## Do Not Start Paid Work Until",
            "",
            "- [ ] The client has named a workflow owner.",
            "- [ ] The client has approved a sample data source or anonymized export.",
            "- [ ] The client understands the first version is a dry-run.",
            "- [ ] The client agrees that external sends, production writes, payments, hiring, access, and legal decisions are excluded.",
            "- [ ] Success metrics are written in `value_measurement_sheet.csv`.",
            "- [ ] The paid PoC boundary in `paid_poc_scope.md` is accepted.",
            "- [ ] A stop condition is agreed before work starts.",
            "",
            "## Minimum Paid PoC Evidence",
            "",
            f"- Revenue score: `{payload['revenue_score']['total']}/100`",
            f"- Demo site: `{payload['demo_site']}`",
            f"- Client report: `{payload['client_report']}`",
            f"- Connector review: `{payload['connector_doctor']}`",
            "",
        ]
    )


def _render_client_proposal_email(payload: dict) -> str:
    return "\n".join(
        [
            f"# Client Proposal Email: {payload['flow_name']}",
            "",
            f"Subject: Small dry-run PoC for your {payload['niche']} workflow",
            "",
            "Hi {{client_name}},",
            "",
            f"I prepared a safe local demo for a `{payload['flow_name']}` workflow. It shows the queue, draft outputs, approval point, and report without sending external messages or updating production systems.",
            "",
            "The useful next step is a small paid PoC with clear limits:",
            "",
            "- use one approved sample data source,",
            "- keep human approval before any external action,",
            "- measure baseline time vs pilot time,",
            "- decide continue, revise, or stop.",
            "",
            "I would suggest reviewing the demo first, then confirming whether this workflow is worth a short PoC.",
            "",
            "Best,",
            "{{your_name}}",
            "",
        ]
    )


def _render_first_30_days_plan(payload: dict) -> str:
    return "\n".join(
        [
            f"# First 30 Days Plan: {payload['flow_name']}",
            "",
            "## Day 1",
            "",
            "- Confirm workflow owner, sample data, excluded actions, and success metrics.",
            "- Review `pre_contract_checklist.md` and `paid_poc_scope.md`.",
            "",
            "## Days 2-5",
            "",
            "- Adapt sample columns to the client workflow.",
            "- Run dry-run output and review drafts with the owner.",
            "- Update approval point and stop condition.",
            "",
            "## Days 6-14",
            "",
            "- Compare baseline and pilot timing in `value_measurement_sheet.csv`.",
            "- Fix obvious workflow mismatches.",
            "- Keep all production connectors disabled unless separately approved.",
            "",
            "## Days 15-30",
            "",
            "- Produce `proof_of_value_template.md` with before/after evidence.",
            "- Decide continue, revise, or stop.",
            "- If continuing, write the maintenance and connector approval plan.",
            "",
        ]
    )


def _render_proof_of_value_template(payload: dict) -> str:
    return "\n".join(
        [
            f"# Proof Of Value Template: {payload['flow_name']}",
            "",
            "## Before / After",
            "",
            "| Metric | Before | After Dry-Run | Evidence |",
            "|---|---:|---:|---|",
            "| Items processed |  |  | `automation_output/run_log.json` |",
            "| Minutes per item |  |  | `value_measurement_sheet.csv` |",
            "| Approval completeness |  |  | `automation_output/approved_actions.csv` |",
            "| Draft usefulness |  |  | owner review notes |",
            "",
            "## Client Decision",
            "",
            "- [ ] Continue to a revised dry-run.",
            "- [ ] Continue to connector approval planning.",
            "- [ ] Stop because value or safety is not clear enough.",
            "",
            "## Evidence Links",
            "",
            f"- Client report: `{payload['client_report']}`",
            f"- Demo site: `{payload['demo_site']}`",
            f"- Connector doctor: `{payload['connector_doctor']}`",
            "",
        ]
    )


def _collect_demo_assets(source: Path) -> list[dict]:
    assets = []
    for path in _collect_demo_file_paths(source):
        rel = path.relative_to(source).as_posix()
        assets.append({"path": rel, "title": _title_from_path(path), "kind": path.suffix.lstrip(".") or "file"})
    return assets[:200]


def _collect_demo_file_paths(source: Path) -> list[Path]:
    if not source.exists():
        return []
    paths = []
    for path in sorted(source.rglob("*")):
        if not path.is_file():
            continue
        if any(part.startswith(".") for part in path.relative_to(source).parts):
            continue
        if path.suffix.lower() in DEMO_EXTENSIONS and path.name not in {"client_demo_package.zip"}:
            paths.append(path)
    return paths


def _title_from_path(path: Path) -> str:
    if path.suffix.lower() in {".md", ".html"}:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return path.name
        for line in text.splitlines():
            stripped = line.strip().strip("#").strip()
            if stripped and not stripped.startswith("<"):
                return stripped[:80]
    return path.name


def _render_demo_site(title: str, assets: list[dict]) -> str:
    rows = "\n".join(
        f"<tr><td>{html.escape(asset['title'])}</td><td><code>{html.escape(asset['kind'])}</code></td><td><a href='../{html.escape(asset['path'])}'>{html.escape(asset['path'])}</a></td></tr>"
        for asset in assets
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    body {{ margin: 0; font-family: Arial, sans-serif; color: #172033; background: #f7f8fa; }}
    header {{ background: #ffffff; border-bottom: 1px solid #d9dee7; padding: 28px; }}
    main {{ max-width: 1080px; margin: 0 auto; padding: 24px; }}
    table {{ width: 100%; border-collapse: collapse; background: #ffffff; border: 1px solid #d9dee7; }}
    th, td {{ padding: 12px; border-bottom: 1px solid #e6e9ef; text-align: left; vertical-align: top; }}
    th {{ background: #eef2f7; }}
    code {{ background: #eef2f7; padding: 2px 5px; border-radius: 4px; }}
  </style>
</head>
<body>
  <header>
    <h1>{html.escape(title)}</h1>
    <p>Open these assets during a client conversation. Keep production actions behind human approval.</p>
  </header>
  <main>
    <table>
      <thead><tr><th>Asset</th><th>Type</th><th>Path</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </main>
</body>
</html>
"""


def _markdown_shell_html(title: str, markdown: str) -> str:
    escaped = html.escape(markdown)
    return f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{html.escape(title)}</title></head>
<body><pre>{escaped}</pre></body>
</html>
"""
