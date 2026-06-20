from __future__ import annotations

import html
import json
import shutil
import zipfile
from pathlib import Path

from ai_automation_kit.core.beginner_sales import generate_beginner_sales_pack
from ai_automation_kit.core.client_ready import generate_client_ready_pack
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
