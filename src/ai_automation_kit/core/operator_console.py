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
SHARE_CHECK_SECRET_MARKERS = ["sk-", "ghp_", "BEGIN PRIVATE KEY", "AWS_SECRET_ACCESS_KEY=", "token=", "password="]
STARTER_FLOW_IDS = [
    "invoice-document-followup",
    "support-reply-draft",
    "weekly-kpi-report",
    "crm-lead-cleanup",
    "lead-routing-followup",
    "appointment-reminder",
    "order-shipping-status",
    "inventory-reorder-alert",
    "candidate-interview-scheduling",
    "field-service-dispatch",
]


def generate_opportunity_catalog(industry: str | None, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    flows = list_flows(industry=industry) if industry else _starter_flows()
    if not flows:
        flows = _starter_flows()
    rows = [_catalog_row(flow, index) for index, flow in enumerate(flows[:24], start=1)]
    payload = {"status": "ready", "industry": industry or "starter", "count": len(rows), "opportunities": rows}
    (output / "opportunity_catalog.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "opportunity_catalog.md").write_text(_render_opportunity_catalog_md(payload), encoding="utf-8")
    (output / "opportunity_catalog.html").write_text(_render_opportunity_catalog_html(payload), encoding="utf-8")
    return payload


def generate_recommended_flow_from_intake(
    industry: str | None,
    pain: str,
    tools: str,
    monthly_items: int,
    output: Path,
) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    candidates = list_flows(industry=industry) if industry else list_flows()
    if not candidates:
        candidates = list_flows()
    scored = sorted(
        (_intake_score(flow, pain=pain, tools=tools, monthly_items=monthly_items) for flow in candidates),
        key=lambda item: item["score"],
        reverse=True,
    )
    recommended = scored[0]
    payload = {
        "status": "ready",
        "industry": industry or "any",
        "pain": pain,
        "tools": tools,
        "monthly_items": monthly_items,
        "recommended_flow": recommended,
        "alternatives": scored[1:4],
    }
    (output / "recommended_flow.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "recommended_flow.md").write_text(_render_recommended_flow(payload), encoding="utf-8")
    (output / "recommended_poc_scope.md").write_text(_render_recommended_poc_scope(payload), encoding="utf-8")
    return payload


def generate_share_check(source: Path, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    findings = []
    for path in _collect_demo_file_paths(source):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError as exc:
            findings.append({"path": path.relative_to(source).as_posix(), "severity": "warning", "marker": "read_error", "detail": str(exc)})
            continue
        for marker in SHARE_CHECK_SECRET_MARKERS:
            if marker in text:
                findings.append({"path": path.relative_to(source).as_posix(), "severity": "blocked", "marker": marker, "detail": "Secret-like marker found."})
        if "/Users/" in text or "file:///Users/" in text:
            findings.append({"path": path.relative_to(source).as_posix(), "severity": "warning", "marker": "local_path", "detail": "Local machine path found; review before sharing."})
    status = "blocked" if any(item["severity"] == "blocked" for item in findings) else "warning" if findings else "ready"
    payload = {"status": status, "source": str(source), "findings": findings, "files_scanned": len(_collect_demo_file_paths(source))}
    (output / "share_check.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "share_check.md").write_text(_render_share_check(payload), encoding="utf-8")
    return payload


def generate_business_launch_pack(
    industry: str | None,
    client_type: str,
    niche: str,
    operator_level: str,
    output: Path,
) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    flows = list_flows(industry=industry) if industry else _starter_flows()
    if not flows:
        flows = _starter_flows()
    recommended_flow = _business_launch_flow_choice(flows, niche)
    starter_offers = [_business_launch_offer_row(flow, index) for index, flow in enumerate(flows[:10], start=1)]
    payload = {
        "status": "ready",
        "industry": industry or "starter",
        "client_type": client_type,
        "niche": niche,
        "operator_level": operator_level,
        "recommended_flow": recommended_flow,
        "starter_offers": starter_offers,
        "positioning": "企業向け自動化導入の小さなPaid PoCを安全に提案するための事業化パック",
    }
    (output / "business_launch.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "START_HERE_BUSINESS_LAUNCH.md").write_text(_render_business_launch_start(payload), encoding="utf-8")
    (output / "target_industry_playbook.md").write_text(_render_target_industry_playbook(payload), encoding="utf-8")
    (output / "first_client_offer.md").write_text(_render_first_client_offer(payload), encoding="utf-8")
    (output / "discovery_call_script.md").write_text(_render_discovery_call_script(payload), encoding="utf-8")
    (output / "proposal_builder.md").write_text(_render_proposal_builder(payload), encoding="utf-8")
    (output / "pricing_and_scope_menu.md").write_text(_render_pricing_and_scope_menu(payload), encoding="utf-8")
    (output / "risk_boundary_sheet.md").write_text(_render_risk_boundary_sheet(payload), encoding="utf-8")
    (output / "30_day_business_launch_plan.md").write_text(_render_30_day_business_launch_plan(payload), encoding="utf-8")
    (output / "client_pitch_email.md").write_text(_render_client_pitch_email(payload), encoding="utf-8")
    return payload


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
    business_launch = generate_business_launch_pack(
        industry=flow["industry"],
        client_type=client_type,
        niche=niche,
        operator_level="beginner",
        output=output / "business_launch",
    )
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
        "business_launch": str(output / "business_launch" / "START_HERE_BUSINESS_LAUNCH.md"),
        "rows_processed": run_payload["rows_processed"],
        "approved_items": approval_payload["approved_items"],
        "connector_status": connector["status"],
        "report_status": report["status"],
        "demo_asset_count": demo["asset_count"],
        "package_file_count": package["file_count"],
        "business_launch_status": business_launch["status"],
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
    (output / "oss_pattern_benchmark.md").write_text(_render_oss_pattern_benchmark(payload), encoding="utf-8")
    (output / "integration_backlog.md").write_text(_render_integration_backlog(payload), encoding="utf-8")
    (output / "deployment_options.md").write_text(_render_deployment_options(payload), encoding="utf-8")
    (output / "production_observability_plan.md").write_text(_render_production_observability_plan(payload), encoding="utf-8")
    (output / "automation_opportunity_scorecard.csv").write_text(_render_automation_opportunity_scorecard(payload), encoding="utf-8")
    (output / "client_onboarding_form.md").write_text(_render_client_onboarding_form(payload), encoding="utf-8")
    (output / "go_live_decision.md").write_text(_render_go_live_decision(payload), encoding="utf-8")
    (output / "client_command_center.html").write_text(_render_client_command_center(payload), encoding="utf-8")
    (output / "side_business_starter_10.md").write_text(_render_side_business_starter_10(payload), encoding="utf-8")
    (output / "before_after_demo.html").write_text(_render_before_after_demo(payload), encoding="utf-8")
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


def _starter_flows() -> list[dict]:
    return [get_flow(flow_id) for flow_id in STARTER_FLOW_IDS]


def _catalog_row(flow: dict, index: int) -> dict:
    base_price = 500 + index * 150
    return {
        "rank": index,
        "flow_id": flow["id"],
        "name": flow["name"],
        "industry": flow["industry"],
        "genre": flow["genre"],
        "summary": flow["summary"],
        "price_range": f"${base_price}-${base_price + 1200}",
        "delivery_days": "3-10 days",
        "proof_metric": flow["success_metrics"][0] if flow.get("success_metrics") else "hours_saved",
        "safe_first_step": "Local dry-run with human approval before external actions.",
    }


def _render_opportunity_catalog_md(payload: dict) -> str:
    lines = [
        "# Automation Opportunity Catalog",
        "",
        f"- Industry: `{payload['industry']}`",
        f"- Opportunities: `{payload['count']}`",
        "",
        "| Rank | Flow | Industry | Price Range | Delivery | Proof Metric |",
        "|---:|---|---|---|---|---|",
    ]
    for item in payload["opportunities"]:
        lines.append(
            f"| {item['rank']} | `{item['flow_id']}` {item['name']} | {item['industry']} | {item['price_range']} | {item['delivery_days']} | {item['proof_metric']} |"
        )
    lines.extend(
        [
            "",
            "## How To Sell",
            "",
            "- Pick one workflow the client already understands.",
            "- Show the before/after demo before discussing tools.",
            "- Sell a bounded dry-run PoC first, not a production automation promise.",
            "",
        ]
    )
    return "\n".join(lines)


def _render_opportunity_catalog_html(payload: dict) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td>{item['rank']}</td>"
        f"<td><strong>{html.escape(item['name'])}</strong><br><code>{html.escape(item['flow_id'])}</code></td>"
        f"<td>{html.escape(item['summary'])}</td>"
        f"<td>{html.escape(item['price_range'])}</td>"
        f"<td>{html.escape(item['delivery_days'])}</td>"
        f"<td>{html.escape(item['proof_metric'])}</td>"
        "</tr>"
        for item in payload["opportunities"]
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Automation Opportunity Catalog</title>
  <style>
    body {{ margin: 0; font-family: Arial, sans-serif; color: #172033; background: #f7f8fa; }}
    header {{ background: #ffffff; border-bottom: 1px solid #d9dee7; padding: 28px; }}
    main {{ max-width: 1180px; margin: 0 auto; padding: 24px; }}
    table {{ width: 100%; border-collapse: collapse; background: #ffffff; border: 1px solid #d9dee7; }}
    th, td {{ padding: 12px; border-bottom: 1px solid #e6e9ef; text-align: left; vertical-align: top; }}
    th {{ background: #eef2f7; }}
    code {{ background: #eef2f7; padding: 2px 5px; border-radius: 4px; }}
  </style>
</head>
<body>
  <header>
    <h1>Automation Opportunity Catalog</h1>
    <p>Use this catalog to pick one sellable dry-run PoC before proposing production automation.</p>
  </header>
  <main>
    <table>
      <thead><tr><th>Rank</th><th>Flow</th><th>Client Problem</th><th>Price Range</th><th>Delivery</th><th>Proof Metric</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </main>
</body>
</html>
"""


def _intake_score(flow: dict, pain: str, tools: str, monthly_items: int) -> dict:
    text = " ".join([flow["id"], flow["name"], flow["summary"], flow["industry"], flow["genre"], " ".join(flow.get("tools", []))]).lower()
    pain_terms = [term for term in pain.lower().replace("-", " ").split() if len(term) >= 4]
    tool_terms = [term for term in tools.lower().replace("/", " ").split() if len(term) >= 3]
    score = 50
    score += sum(8 for term in pain_terms if term in text)
    score += sum(5 for term in tool_terms if term in text)
    score += min(20, max(0, monthly_items // 10))
    if "approval" in text or "draft" in text:
        score += 8
    return {**flow, "score": min(100, score), "why": _intake_reason(flow, pain_terms, tool_terms)}


def _intake_reason(flow: dict, pain_terms: list[str], tool_terms: list[str]) -> str:
    matched = [term for term in pain_terms + tool_terms if term in " ".join([flow["id"], flow["name"], flow["summary"], " ".join(flow.get("tools", []))]).lower()]
    if matched:
        return "Matched intake terms: " + ", ".join(sorted(set(matched))[:8])
    return "Best available workflow by industry and safe dry-run fit."


def _render_recommended_flow(payload: dict) -> str:
    flow = payload["recommended_flow"]
    lines = [
        "# Recommended Flow From Client Intake",
        "",
        f"- Recommended flow: `{flow['id']}`",
        f"- Name: {flow['name']}",
        f"- Score: `{flow['score']}/100`",
        f"- Why: {flow['why']}",
        f"- Client pain: {payload['pain']}",
        f"- Tools mentioned: {payload['tools']}",
        f"- Monthly items: `{payload['monthly_items']}`",
        "",
        "## First Action",
        "",
        f"Run `ai-automation-kit complete-workspace --flow-id {flow['id']} --output .tmp/{flow['id']}-workspace` and open `client_command_center.html`.",
        "",
        "## Alternatives",
        "",
    ]
    lines.extend(f"- `{item['id']}` {item['name']} - score `{item['score']}/100`" for item in payload["alternatives"])
    lines.append("")
    return "\n".join(lines)


def _render_recommended_poc_scope(payload: dict) -> str:
    flow = payload["recommended_flow"]
    return "\n".join(
        [
            f"# Paid PoC Recommendation: {flow['name']}",
            "",
            "## Offer",
            "",
            f"Create a safe dry-run for `{flow['id']}` using one approved sample data source, human approval, and a before/after report.",
            "",
            "## Scope",
            "",
            "- Confirm workflow owner and approval owner.",
            "- Import or paste one sample data export.",
            "- Generate queue, draft output, approval list, report, and demo.",
            "- Measure baseline minutes per item against dry-run minutes per item.",
            "- Decide continue, revise, or stop.",
            "",
            "## Do Not Include Yet",
            "",
            "- Production sends or writes.",
            "- Payment, access, legal, hiring, or regulated decisions.",
            "- Unreviewed client secrets or sensitive data.",
            "",
        ]
    )


def _render_share_check(payload: dict) -> str:
    lines = [
        "# Share Check",
        "",
        f"- Status: `{payload['status']}`",
        f"- Source: `{payload['source']}`",
        f"- Files scanned: `{payload['files_scanned']}`",
        "",
    ]
    if payload["findings"]:
        lines.extend(["## Findings", "", "| Severity | File | Marker | Detail |", "|---|---|---|---|"])
        for item in payload["findings"]:
            lines.append(f"| `{item['severity']}` | `{item['path']}` | `{item['marker']}` | {item['detail']} |")
    else:
        lines.extend(["## Findings", "", "No secret-like markers or local machine paths were found in shareable text assets."])
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `ready`: share after normal client review.",
            "- `warning`: review findings, remove local paths if needed, then share.",
            "- `blocked`: do not share until secret-like markers are removed.",
            "",
        ]
    )
    return "\n".join(lines)


def _business_launch_flow_choice(flows: list[dict], niche: str) -> dict:
    niche_terms = {term for term in niche.lower().replace("-", " ").split() if len(term) >= 4}
    best = None
    best_score = -1
    for index, flow in enumerate(flows):
        text = " ".join([flow["id"], flow["name"], flow["summary"], flow["industry"], flow["genre"]]).lower()
        score = 100 - index * 2
        score += sum(6 for term in niche_terms if term in text)
        if flow["id"] in STARTER_FLOW_IDS:
            score += 8
        if flow["genre"] in {"document", "communication", "reporting", "approval"}:
            score += 5
        if score > best_score:
            best = flow
            best_score = score
    selected = dict(best or flows[0])
    selected["business_launch_score"] = max(0, min(100, best_score))
    selected["why_beginner_friendly"] = "入力、承認者、成果物、測定指標を説明しやすく、最初は本番送信なしのdry-runで提案できます。"
    return selected


def _business_launch_offer_row(flow: dict, index: int) -> dict:
    entry_price = 30000 + index * 5000
    return {
        "rank": index,
        "flow_id": flow["id"],
        "name": flow["name"],
        "industry": flow["industry"],
        "client_pain": flow["summary"],
        "first_offer": "3日間の業務自動化dry-run診断",
        "price_jpy": f"{entry_price:,}円-{entry_price + 70000:,}円",
        "proof": flow.get("success_metrics", ["hours_saved"])[0],
    }


def _render_business_launch_start(payload: dict) -> str:
    flow = payload["recommended_flow"]
    return "\n".join(
        [
            "# Business Launch Start Guide",
            "",
            "このフォルダは、AIに慣れていない人が企業向け自動化導入を小さく事業化提案するための実行パックです。",
            "",
            "## 最初に読む順番",
            "",
            "1. `target_industry_playbook.md` で狙う企業と困りごとを決める。",
            "2. `first_client_offer.md` で最初の商品を確認する。",
            "3. `discovery_call_script.md` を見ながらヒアリングする。",
            "4. `proposal_builder.md` で提案書を作る。",
            "5. `pricing_and_scope_menu.md` で価格と範囲を選ぶ。",
            "6. `risk_boundary_sheet.md` で保証しないことと禁止事項を説明する。",
            "7. `client_pitch_email.md` を送る。",
            "",
            "## 推奨する最初の提案",
            "",
            f"- Flow: `{flow['id']}`",
            f"- Name: {flow['name']}",
            f"- Industry: {flow['industry']}",
            f"- Why: {flow['why_beginner_friendly']}",
            "",
            "## 守ること",
            "",
            "- 最初はPaid PoCとして売る。",
            "- 本番送信、顧客データの自動更新、支払い、採用、法務判断は含めない。",
            "- 成果保証ではなく、業務の見える化、dry-run、時間削減の測定を提供する。",
            "",
        ]
    )


def _render_target_industry_playbook(payload: dict) -> str:
    lines = [
        "# Target Industry Playbook",
        "",
        f"- Target industry: `{payload['industry']}`",
        f"- Niche: `{payload['niche']}`",
        f"- Client type: `{payload['client_type']}`",
        "",
        "## 狙いやすい企業",
        "",
        "- 毎週同じ確認、転記、返信、集計、督促が発生している。",
        "- 担当者がスプレッドシート、メール、チャット、CSVで業務を回している。",
        "- いきなり本番自動化は怖いが、業務の見える化と試作には興味がある。",
        "- 社内にAI担当者がいない、またはAIを使い始めたばかり。",
        "",
        "## 売り込みやすい切り口",
        "",
        "| Rank | Flow | 初回提案 | 価格目安 | 測定指標 |",
        "|---:|---|---|---|---|",
    ]
    for offer in payload["starter_offers"]:
        lines.append(
            f"| {offer['rank']} | `{offer['flow_id']}` {offer['name']} | {offer['first_offer']} | {offer['price_jpy']} | {offer['proof']} |"
        )
    lines.extend(
        [
            "",
            "## 最初の判断基準",
            "",
            "- 月30件以上ある業務を優先する。",
            "- 1件あたり5分以上かかる業務を優先する。",
            "- 承認者が1人に決まる業務を優先する。",
            "- 個人情報、決済、法務、採用判断は初回PoCから外す。",
            "",
        ]
    )
    return "\n".join(lines)


def _render_first_client_offer(payload: dict) -> str:
    flow = payload["recommended_flow"]
    return "\n".join(
        [
            f"# First Client Offer: {flow['name']}",
            "",
            "## 商品名",
            "",
            "企業向け自動化導入 dry-run 診断 + Paid PoC 設計",
            "",
            "## 何を提供するか",
            "",
            f"`{flow['id']}` の業務を対象に、現在の手作業を整理し、AIとローカル自動化でどこまで短縮できるかを本番送信なしで確認します。",
            "",
            "## 納品物",
            "",
            "- 業務フロー図",
            "- before/after説明",
            "- サンプルデータでのdry-run出力",
            "- 承認ポイント一覧",
            "- 時間削減の測定シート",
            "- 次に本番化する場合の安全条件",
            "",
            "## 提案価格",
            "",
            "- 初回診断: 30,000円-50,000円",
            "- Paid PoC: 80,000円-200,000円",
            "- 月次改善支援: 30,000円-100,000円/月",
            "",
            "## 売り文句",
            "",
            "いきなり社内システムを変えるのではなく、まず手作業を見える化し、サンプルデータで自動化の効果を確認します。安全に試して、続けるか止めるかを判断できます。",
            "",
        ]
    )


def _render_discovery_call_script(payload: dict) -> str:
    flow = payload["recommended_flow"]
    return "\n".join(
        [
            f"# Discovery Call Script: {flow['name']}",
            "",
            "## 1. 最初の説明",
            "",
            "今日は自動化を売り込む前に、今どこで時間がかかっているか、どこなら安全に試せるかを確認します。最初から本番システムには触りません。",
            "",
            "## 2. 質問",
            "",
            "- 毎週または毎月、繰り返している作業は何ですか。",
            "- その作業は月に何件ありますか。",
            "- 1件あたり何分かかりますか。",
            "- どのツールを使っていますか。例: Excel, Google Sheets, Gmail, Slack, LINE, Notion",
            "- ミスや遅れが起きると、何が困りますか。",
            "- 最終確認する人は誰ですか。",
            "- 自動送信してはいけないものは何ですか。",
            "- サンプルデータや匿名化したCSVは出せますか。",
            "",
            "## 3. 締め方",
            "",
            "この内容なら、まず3日程度のdry-runで、手作業の流れ、AIが作る下書き、承認ポイント、時間削減の見込みを確認できます。結果を見て、本番化するか止めるかを決めましょう。",
            "",
        ]
    )


def _render_proposal_builder(payload: dict) -> str:
    flow = payload["recommended_flow"]
    return "\n".join(
        [
            f"# Proposal Builder: {flow['name']}",
            "",
            "## 提案書テンプレート",
            "",
            "### 目的",
            "",
            f"{payload['niche']} の繰り返し業務を対象に、AIとローカル自動化で作業時間、確認漏れ、返信遅れを減らせるか検証します。",
            "",
            "### 対象業務",
            "",
            f"- 推奨フロー: `{flow['id']}` {flow['name']}",
            f"- 業務内容: {flow['summary']}",
            "",
            "### 実施内容",
            "",
            "- 現在の作業手順を整理",
            "- サンプルデータでdry-run",
            "- AI下書き、確認リスト、承認キューを作成",
            "- before/afterをレポート化",
            "- 本番化する場合の条件を整理",
            "",
            "### 成功条件",
            "",
            "- 担当者が出力を理解できる",
            "- 手作業より短い、または確認漏れが減る見込みがある",
            "- 承認者と禁止事項が明確",
            "- 継続、修正、停止の判断ができる",
            "",
        ]
    )


def _render_pricing_and_scope_menu(payload: dict) -> str:
    return "\n".join(
        [
            "# Pricing And Scope Menu",
            "",
            "| Plan | Price | Best For | Includes | Not Included |",
            "|---|---:|---|---|---|",
            "| 初回診断 | 30,000円-50,000円 | 初めてAI自動化を試す企業 | ヒアリング、業務整理、改善候補1件、簡易提案 | 実装、本番接続 |",
            "| Paid PoC | 80,000円-200,000円 | 効果を見て判断したい企業 | サンプルデータdry-run、下書き、承認キュー、測定シート、報告 | 本番送信、常時運用 |",
            "| 月次改善 | 30,000円-100,000円/月 | 小さく継続改善したい企業 | 月1-2回の改善、レポート、追加フロー相談 | 24時間監視、重い開発 |",
            "| 本番化支援 | 個別見積 | PoCで価値が確認できた企業 | connector設定、承認ルール、運用設計、監視計画 | 法務/セキュリティ責任の代行 |",
            "",
            "## 初心者向けの価格ルール",
            "",
            "- 最初から大きく売らない。",
            "- 成果保証ではなく、検証、見える化、改善提案として売る。",
            "- 安すぎると責任範囲が曖昧になるので、無料相談の次は小さな有料診断にする。",
            "- 本番化はPoC後に別契約にする。",
            "",
        ]
    )


def _render_risk_boundary_sheet(payload: dict) -> str:
    return "\n".join(
        [
            "# Risk Boundary Sheet",
            "",
            "## 保証しないこと",
            "",
            "- 売上増加や利益増加を保証しない。",
            "- 完全自動化を保証しない。",
            "- 人間の確認なしで正しい判断ができることを保証しない。",
            "- 既存システムに必ず接続できることを保証しない。",
            "",
            "## 初回PoCでやらないこと",
            "",
            "- 本番送信",
            "- 本番データの更新",
            "- 支払い、返金、採用、契約、法務判断",
            "- パスワードやAPIキーの預かり",
            "- 個人情報や機密情報を含むデータ処理",
            "",
            "## 必ず確認すること",
            "",
            "- 業務オーナー",
            "- 承認者",
            "- 使ってよいサンプルデータ",
            "- 出力を確認する人",
            "- stop条件",
            "- 本番化する場合の責任範囲",
            "",
        ]
    )


def _render_30_day_business_launch_plan(payload: dict) -> str:
    return "\n".join(
        [
            "# 30 Day Business Launch Plan",
            "",
            "## Week 1: 提案の型を作る",
            "",
            "- `first_client_offer.md` を自分の言葉に直す。",
            "- 10社の候補企業をリスト化する。",
            "- 1つの業種、1つの業務だけに絞る。",
            "",
            "## Week 2: ヒアリングを取る",
            "",
            "- `client_pitch_email.md` を送る。",
            "- 返信があった企業に `discovery_call_script.md` で聞く。",
            "- 無料相談で終わらせず、小さな有料診断を提案する。",
            "",
            "## Week 3: Paid PoCを実施する",
            "",
            "- サンプルデータだけでdry-runを作る。",
            "- before/afterと承認ポイントを見せる。",
            "- 測定シートで時間削減の可能性を確認する。",
            "",
            "## Week 4: 継続提案に進む",
            "",
            "- 継続、修正、停止をクライアントに選んでもらう。",
            "- 本番化する場合は別契約にする。",
            "- 月次改善支援を小さく提案する。",
            "",
        ]
    )


def _render_client_pitch_email(payload: dict) -> str:
    flow = payload["recommended_flow"]
    return "\n".join(
        [
            f"# Client Pitch Email: {flow['name']}",
            "",
            f"Subject: {payload['niche']}業務の手作業を小さく自動化検証しませんか",
            "",
            "{{会社名}}",
            "{{担当者名}} 様",
            "",
            "突然のご連絡失礼します。",
            "",
            f"{payload['niche']}まわりの繰り返し業務について、いきなり本番システムを変えるのではなく、サンプルデータでAI自動化の効果を確認する小さな診断を行っています。",
            "",
            f"最初の対象としては `{flow['name']}` のような業務が向いています。",
            "",
            "初回は以下だけを確認します。",
            "",
            "- どの作業に時間がかかっているか",
            "- 月に何件あるか",
            "- どこで確認漏れや遅れが起きるか",
            "- 本番送信せずに試せるサンプルデータがあるか",
            "",
            "もし合いそうであれば、3日程度のPaid PoCとして、業務フロー、AI下書き、承認ポイント、before/afterレポートまで作れます。",
            "",
            "一度15分ほど、対象になりそうな業務があるかだけ確認できればと思います。",
            "",
            "{{あなたの名前}}",
            "",
        ]
    )


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
            "14. `oss_pattern_benchmark.md`",
            "15. `integration_backlog.md`",
            "16. `deployment_options.md`",
            "17. `production_observability_plan.md`",
            "18. `automation_opportunity_scorecard.csv`",
            "19. `client_onboarding_form.md`",
            "20. `go_live_decision.md`",
            "21. `client_command_center.html`",
            "22. `side_business_starter_10.md`",
            "23. `before_after_demo.html`",
            "24. `business_launch/START_HERE_BUSINESS_LAUNCH.md`",
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
        ("OSS pattern benchmark prepared", "oss_pattern_benchmark.md"),
        ("Integration backlog prepared", "integration_backlog.md"),
        ("Deployment options prepared", "deployment_options.md"),
        ("Production observability plan prepared", "production_observability_plan.md"),
        ("Automation opportunity scorecard prepared", "automation_opportunity_scorecard.csv"),
        ("Client onboarding form prepared", "client_onboarding_form.md"),
        ("Go-live decision gate prepared", "go_live_decision.md"),
        ("Client command center prepared", "client_command_center.html"),
        ("Side business starter 10 prepared", "side_business_starter_10.md"),
        ("Before/after demo prepared", "before_after_demo.html"),
        ("Business launch proposal pack prepared", payload["business_launch"]),
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


def _render_oss_pattern_benchmark(payload: dict) -> str:
    return "\n".join(
        [
            f"# OSS Pattern Benchmark: {payload['flow_name']}",
            "",
            "This benchmark translates proven public automation patterns into this sellable local-first workspace.",
            "",
            "## Patterns To Imitate",
            "",
            "| Source | Public pattern | What this workspace should copy |",
            "|---|---|---|",
            "| n8n | Visual workflow templates, self-hosted AI starter kits, many integrations | Keep flows visible, template-driven, and easy to adapt before production connectors are enabled. |",
            "| Activepieces | Type-safe pieces and integrations that can become MCP servers for AI tools | Treat every connector as a reusable piece with a clear schema, permission boundary, and MCP-ready future path. |",
            "| Windmill | Scripts can become webhooks, workflows, schedules, and auto-generated UIs | Keep each flow scriptable first, then expose it as a webhook or simple UI only after the dry-run works. |",
            "| Trigger.dev | Long-running AI workflows with retries, queues, observability, and human approval | Add production execution rules before any client workflow moves beyond a local dry-run. |",
            "| Community template libraries | Large ready-to-import workflow examples | Convert common templates into reviewed business flows instead of copying unknown automation blindly. |",
            "",
            "## Design Rule",
            "",
            "Copy patterns, not code. Keep this project adapter-only unless a license review explicitly approves importing third-party code.",
            "",
            "## Next Product Standard",
            "",
            "- Every flow has a dry-run path, approval point, connector boundary, and measurable report.",
            "- Every external integration has a setup checklist and stop condition.",
            "- Every production candidate has retries, queues, logs, approval audit, and rollback notes.",
            "",
        ]
    )


def _render_integration_backlog(payload: dict) -> str:
    return "\n".join(
        [
            f"# Integration Backlog: {payload['flow_name']}",
            "",
            "Prioritize integrations that make the first paid PoC easier to sell, safer to run, and easier to measure.",
            "",
            "## Priority 1: Common Business Data",
            "",
            "- Google Sheets adapter: import/export queues, status, and value measurement rows.",
            "- CSV folder adapter: keep the zero-credential dry-run path for cautious clients.",
            "- Gmail or Outlook draft adapter: create drafts only until the client approves sending.",
            "- Slack or Teams draft adapter: write approval-ready messages before posting is enabled.",
            "- Webhook input adapter: receive form, CRM, or support payloads behind a validation step.",
            "",
            "## Priority 2: Sales And Operations Systems",
            "",
            "- CRM adapter for HubSpot, Salesforce, or Pipedrive field updates after approval.",
            "- Airtable or Notion adapter for lightweight client databases.",
            "- Calendar adapter for follow-up scheduling and missed-response reminders.",
            "- File storage adapter for Google Drive, OneDrive, or Dropbox document handoff.",
            "",
            "## Priority 3: OSS Platform Bridges",
            "",
            "- n8n import notes for converting a flow into a visual workflow.",
            "- Activepieces piece notes with MCP compatibility targets.",
            "- Windmill deployment notes for script-to-webhook and script-to-UI delivery.",
            "- Trigger.dev-style worker notes for long-running queues and retries.",
            "",
            "## Connector Acceptance Criteria",
            "",
            "- Includes `.env.example` keys and a no-secret sample.",
            "- Supports dry-run mode and approval-only mode.",
            "- Writes run logs and error states.",
            "- Documents required scopes, data touched, and rollback.",
            "- Can be explained to a non-programmer in one paragraph.",
            "",
        ]
    )


def _render_deployment_options(payload: dict) -> str:
    return "\n".join(
        [
            f"# Deployment Options: {payload['flow_name']}",
            "",
            "Choose the smallest deployment that proves value without creating hidden maintenance risk.",
            "",
            "## Option 1: Local dry-run",
            "",
            "- Best for first meetings, PoCs, and clients who cannot approve credentials yet.",
            "- Runs on local files and produces reports, drafts, approval CSVs, and demo assets.",
            "- Stop if the client cannot name the owner, sample data, or approval rule.",
            "",
            "## Option 2: Client machine or VPS self-host",
            "",
            "- Best when the client wants data control and predictable cost.",
            "- Use Docker or a managed VPS only after backup, update, and access rules are written.",
            "- Stop if there is no owner for uptime, backups, and credential rotation.",
            "",
            "## Option 3: n8n or Activepieces visual workflow",
            "",
            "- Best when the client wants a low-code operations team to inspect and adjust steps.",
            "- Keep the generated flow as the source explanation, then rebuild the approved steps visually.",
            "- Stop if the visual workflow cannot preserve approval and dry-run boundaries.",
            "",
            "## Option 4: Windmill-style script, webhook, or UI",
            "",
            "- Best when the client wants code-first scripts exposed as internal tools.",
            "- Promote only one stable script at a time into a webhook or UI.",
            "- Stop if inputs are not validated or the output cannot be rolled back.",
            "",
            "## Option 5: Durable worker or Trigger.dev-style queue",
            "",
            "- Best for long-running automations, retries, queues, scheduled tasks, and AI steps.",
            "- Add explicit retry limits, queue ownership, observability, and dead-letter handling.",
            "- Stop if failures would be invisible to the client or operator.",
            "",
        ]
    )


def _render_production_observability_plan(payload: dict) -> str:
    return "\n".join(
        [
            f"# Production Observability Plan: {payload['flow_name']}",
            "",
            "Do not move from dry-run to production until the operator can see what happened, why it happened, and what to do next.",
            "",
            "## Required Signals",
            "",
            "- Run history: start time, end time, status, rows processed, and operator.",
            "- retries: attempt count, last error, next retry time, and retry limit.",
            "- queues: pending, running, succeeded, failed, and dead-letter item counts.",
            "- approval audit: who approved, what was approved, when it was approved, and where the evidence is stored.",
            "- Connector health: credential present, scope reviewed, last successful call, and disabled state.",
            "- Value tracking: baseline time, pilot time, avoided manual steps, and client decision.",
            "",
            "## Alert Rules",
            "",
            "- Alert the operator when any production write fails.",
            "- Alert the approval owner when queue age exceeds the agreed service window.",
            "- Pause external actions when connector health changes from ready to review.",
            "- Escalate dead-letter items before the next scheduled run.",
            "",
            "## Monthly Review",
            "",
            "- Review top errors and remove brittle steps.",
            "- Confirm credentials, scopes, and approval owners are still current.",
            "- Compare measured value against the paid PoC assumptions.",
            "- Decide continue, revise, reduce scope, or retire the automation.",
            "",
        ]
    )


def _render_automation_opportunity_scorecard(payload: dict) -> str:
    rows = [
        ["metric", "score_0_to_5", "evidence_needed", "sellable_now"],
        ["pain_frequency", "4", "How often this workflow happens each month.", "yes if weekly or higher"],
        ["manual_time_cost", "4", "Minutes per item and loaded hourly cost.", "yes if savings can fund a small PoC"],
        ["data_access_clarity", "3", "Sample CSV, spreadsheet, or export approved by the client.", "yes if sample data is approved"],
        ["approval_owner_clarity", "5", "Named person who approves drafts or production actions.", "yes if one owner is named"],
        ["risk_boundary_clarity", "4", "Excluded actions, sensitive data, and stop condition.", "yes if excluded actions are written"],
        ["dry_run_evidence", "5", "Queue, drafts, approval records, report, and demo assets.", "yes if generated files are reviewable"],
        ["workflow_fit_score", "=SUM(B2:B7)", "Score 22+ is a good paid PoC candidate.", "sellable_now"],
    ]
    return "\n".join(",".join(str(cell) for cell in row) for row in rows) + "\n"


def _render_client_onboarding_form(payload: dict) -> str:
    return "\n".join(
        [
            f"# Client Onboarding Form: {payload['flow_name']}",
            "",
            "Use this before touching real accounts, client data, or production connectors.",
            "",
            "## Client Basics",
            "",
            "- Company:",
            "- Department:",
            "- Main contact:",
            "- Billing contact:",
            "- Workflow owner:",
            "- Approval Owner:",
            "",
            "## Workflow Facts",
            "",
            f"- Proposed workflow: `{payload['flow_name']}`",
            f"- Niche: `{payload['niche']}`",
            "- Current manual process:",
            "- Monthly item volume:",
            "- Minutes per item:",
            "- Current tools used:",
            "- Most expensive delay or mistake:",
            "",
            "## Data And Access",
            "",
            "- Approved sample data source:",
            "- Data fields included:",
            "- Sensitive data excluded:",
            "- Credentials owner:",
            "- Systems that must never be changed without approval:",
            "",
            "## Approval And Stop Rules",
            "",
            "- Who reviews drafts:",
            "- Who approves external sends or production writes:",
            "- Stop condition:",
            "- Rollback contact:",
            "- Review cadence:",
            "",
            "## Paid PoC Decision",
            "",
            "- Budget range:",
            "- Expected decision date:",
            "- Continue criteria:",
            "- Revise criteria:",
            "- Stop criteria:",
            "",
        ]
    )


def _render_go_live_decision(payload: dict) -> str:
    return "\n".join(
        [
            f"# Go-Live Decision: {payload['flow_name']}",
            "",
            "This gate decides whether the dry-run can become a production automation.",
            "",
            "## Current Recommendation",
            "",
            "Do Not Go Live until every required checkbox below is complete. Keep using local dry-run output for client review.",
            "",
            "## Required Before Go-Live",
            "",
            "- [ ] `client_onboarding_form.md` is complete.",
            "- [ ] `automation_opportunity_scorecard.csv` shows a strong paid PoC fit.",
            "- [ ] Client has approved data source, fields, credentials owner, and excluded data.",
            "- [ ] Approval Owner is named for drafts and production actions.",
            "- [ ] Connector scopes and rollback steps are documented.",
            "- [ ] `production_observability_plan.md` has run history, retries, queues, approval audit, alerts, and monthly review owner.",
            "- [ ] A final dry-run report was reviewed by the client.",
            "- [ ] First production run has a human operator watching it.",
            "",
            "## Go-Live Choices",
            "",
            "- Continue dry-run: value is promising but production safety is incomplete.",
            "- Limited go-live: one connector, one workflow owner, one rollback path, and human approval.",
            "- Stop: value, safety, or ownership is not clear enough.",
            "",
            "## First Production Run Notes",
            "",
            "- Date:",
            "- Operator:",
            "- Approval Owner:",
            "- Connector enabled:",
            "- Items processed:",
            "- Errors:",
            "- Decision after first run:",
            "",
        ]
    )


def _render_client_command_center(payload: dict) -> str:
    cards = [
        (
            "Start Here",
            "Open the final guide, demo site, and client report before reading the deeper files.",
            [
                ("Final delivery guide", "FINAL_DELIVERY_GUIDE.md"),
                ("Demo site", "demo_site/index.html"),
                ("Client report", "client_report/client_report.html"),
            ],
        ),
        (
            "Sellable PoC",
            "Use these files to decide whether the workflow is worth pitching as a bounded paid pilot.",
            [
                ("Revenue readiness", "revenue_readiness_scorecard.md"),
                ("Opportunity scorecard", "automation_opportunity_scorecard.csv"),
                ("Paid PoC scope", "paid_poc_scope.md"),
                ("Proposal email", "client_proposal_email.md"),
            ],
        ),
        (
            "Client Intake",
            "Capture the owner, approval rules, data source, exclusions, and stop condition.",
            [
                ("Client onboarding form", "client_onboarding_form.md"),
                ("Pre-contract checklist", "pre_contract_checklist.md"),
                ("Value measurement sheet", "value_measurement_sheet.csv"),
            ],
        ),
        (
            "Production Path",
            "Keep production blocked until deployment, connectors, monitoring, and approval audit are clear.",
            [
                ("Deployment options", "deployment_options.md"),
                ("Integration backlog", "integration_backlog.md"),
                ("Observability plan", "production_observability_plan.md"),
                ("Go-Live Gate", "go_live_decision.md"),
            ],
        ),
    ]
    card_html = "\n".join(_command_center_card(title, body, links) for title, body, links in cards)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Client Command Center - {html.escape(payload['flow_name'])}</title>
  <style>
    body {{ margin: 0; font-family: Arial, sans-serif; color: #182235; background: #f6f7f9; }}
    header {{ padding: 28px; background: #ffffff; border-bottom: 1px solid #d9dee7; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 24px; }}
    .summary {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin: 20px 0; }}
    .stat, .card {{ background: #ffffff; border: 1px solid #d9dee7; border-radius: 8px; padding: 16px; }}
    .stat strong {{ display: block; font-size: 22px; margin-bottom: 4px; }}
    .grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }}
    h1, h2 {{ margin-top: 0; }}
    a {{ color: #1659b7; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    ul {{ padding-left: 20px; }}
    code {{ background: #eef2f7; padding: 2px 5px; border-radius: 4px; }}
    @media (max-width: 820px) {{ .summary, .grid {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <header>
    <h1>Client Command Center</h1>
    <p>{html.escape(payload['flow_name'])} for {html.escape(payload['client_type'])} / {html.escape(payload['niche'])}</p>
  </header>
  <main>
    <section class="summary" aria-label="Workspace summary">
      <div class="stat"><strong>{html.escape(str(payload['rows_processed']))}</strong>rows processed</div>
      <div class="stat"><strong>{html.escape(str(payload['approved_items']))}</strong>approved drafts</div>
      <div class="stat"><strong>{html.escape(str(payload['revenue_score']['total']))}/100</strong>revenue readiness</div>
      <div class="stat"><strong>{html.escape(payload['connector_status'])}</strong>connector status</div>
    </section>
    <section class="grid">
      {card_html}
    </section>
  </main>
</body>
</html>
"""


def _command_center_card(title: str, body: str, links: list[tuple[str, str]]) -> str:
    items = "\n".join(f"<li><a href='{html.escape(path)}'>{html.escape(label)}</a> <code>{html.escape(path)}</code></li>" for label, path in links)
    return f"""<article class="card">
  <h2>{html.escape(title)}</h2>
  <p>{html.escape(body)}</p>
  <ul>{items}</ul>
</article>"""


def _render_side_business_starter_10(payload: dict) -> str:
    lines = [
        "# Side Business Starter 10",
        "",
        "These are the easiest workflows to explain, demo, and sell as bounded dry-run PoCs. Start here before browsing the full catalog.",
        "",
        "| Rank | Flow ID | Buyer | Why It Sells | First Proof |",
        "|---:|---|---|---|---|",
    ]
    buyers = {
        "invoice-document-followup": "accounting teams",
        "support-reply-draft": "support teams",
        "weekly-kpi-report": "operations managers",
        "crm-lead-cleanup": "sales teams",
        "lead-routing-followup": "local service businesses",
        "appointment-reminder": "clinics and salons",
        "order-shipping-status": "ecommerce shops",
        "inventory-reorder-alert": "retail and ecommerce teams",
        "candidate-interview-scheduling": "small HR teams",
        "field-service-dispatch": "field service teams",
    }
    for index, flow in enumerate(_starter_flows(), start=1):
        lines.append(
            f"| {index} | `{flow['id']}` | {buyers.get(flow['id'], flow['industry'])} | {flow['summary']} | `{flow['success_metrics'][0]}` |"
        )
    lines.extend(
        [
            "",
            "## Rule",
            "",
            "Sell one visible workflow, run one dry-run, measure one before/after metric, then decide continue, revise, or stop.",
            "",
        ]
    )
    return "\n".join(lines)


def _render_before_after_demo(payload: dict) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Before / After Demo - {html.escape(payload['flow_name'])}</title>
  <style>
    body {{ margin: 0; font-family: Arial, sans-serif; background: #f7f8fa; color: #172033; }}
    header {{ background: #ffffff; border-bottom: 1px solid #d9dee7; padding: 28px; }}
    main {{ max-width: 1060px; margin: 0 auto; padding: 24px; }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
    section {{ background: #ffffff; border: 1px solid #d9dee7; border-radius: 8px; padding: 18px; }}
    .metric {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 16px; }}
    .metric div {{ background: #eef2f7; padding: 14px; border-radius: 8px; }}
    code {{ background: #eef2f7; padding: 2px 5px; border-radius: 4px; }}
    @media (max-width: 760px) {{ .grid, .metric {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <header>
    <h1>Before / After Demo</h1>
    <p>{html.escape(payload['flow_name'])} for {html.escape(payload['niche'])}</p>
  </header>
  <main>
    <div class="grid">
      <section>
        <h2>Before</h2>
        <ul>
          <li>Manual queue review across spreadsheets, email, and chat.</li>
          <li>Follow-up drafts are written from scratch.</li>
          <li>Approval evidence is scattered or missing.</li>
          <li>Value is hard to prove after the work is done.</li>
        </ul>
      </section>
      <section>
        <h2>After Dry-Run</h2>
        <ul>
          <li>Work queue, drafts, approval list, and report are generated locally.</li>
          <li>Human approval remains required before any external action.</li>
          <li>Client can inspect evidence before committing to production.</li>
          <li>Value is measured in the generated scorecards.</li>
        </ul>
      </section>
    </div>
    <section>
      <h2>Proof From This Workspace</h2>
      <div class="metric">
        <div><strong>{html.escape(str(payload['rows_processed']))}</strong><br>rows processed</div>
        <div><strong>{html.escape(str(payload['approved_items']))}</strong><br>approved drafts</div>
        <div><strong>{html.escape(str(payload['revenue_score']['total']))}/100</strong><br>sellable PoC score</div>
      </div>
      <p>Open <code>client_command_center.html</code> to navigate the full delivery pack.</p>
    </section>
  </main>
</body>
</html>
"""


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
