from __future__ import annotations

import html
import json
from pathlib import Path

from ai_automation_kit.core.models import Artifact


def write_research_artifacts(
    output_dir: Path | str,
    topic: str,
    findings: list[dict],
    run: dict,
    rerun_command: str,
) -> list[Artifact]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    markdown = _render_markdown(topic, findings, run, rerun_command)
    html_report = _render_html(markdown)
    json_report = {"topic": topic, "run": run, "findings": findings}
    failed_fetches = run.get("failed_fetches") or []

    (output / "report.md").write_text(markdown, encoding="utf-8")
    (output / "report.html").write_text(html_report, encoding="utf-8")
    (output / "report.json").write_text(json.dumps(json_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "failed_fetches.json").write_text(
        json.dumps({"failed_fetches": failed_fetches}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    return [
        Artifact(kind="markdown", path="report.md"),
        Artifact(kind="html", path="report.html"),
        Artifact(kind="json", path="report.json"),
        Artifact(kind="failed_fetches", path="failed_fetches.json"),
    ]


def _render_markdown(topic: str, findings: list[dict], run: dict, rerun_command: str) -> str:
    lines = [
        f"# Research Report: {topic}",
        "",
        "## Run Timeline",
        "",
        f"- Run ID: `{run.get('run_id', '')}`",
        f"- Started: `{run.get('started_at', '')}`",
        f"- Finished: `{run.get('finished_at', '')}`",
        "",
        "## Source Table",
        "",
        "| # | Title | URI | Summary |",
        "|---:|---|---|---|",
    ]
    for index, finding in enumerate(findings, start=1):
        lines.append(
            f"| {index} | {finding.get('title', '')} | {finding.get('uri', '')} | {finding.get('summary', '')} |"
        )

    lines.extend(["", "## Failed URL Log", ""])
    failed_fetches = run.get("failed_fetches") or []
    if failed_fetches:
        for failed in failed_fetches:
            lines.append(f"- {failed.get('uri', '')}: {failed.get('reason', '')}")
    else:
        lines.append("- None")

    lines.extend(["", "## Rerun Command", "", "```bash", rerun_command, "```", ""])
    return "\n".join(lines)


def _render_html(markdown: str) -> str:
    escaped = html.escape(markdown)
    return f"<html><head><title>Research Report</title></head><body><pre>{escaped}</pre></body></html>\n"
