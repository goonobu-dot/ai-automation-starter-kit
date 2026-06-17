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


def write_artifact_index(
    output_dir: Path | str,
    template_name: str,
    artifacts: list[Artifact | dict],
    first_read: list[str] | None = None,
) -> list[Artifact]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    normalized = [_artifact_to_dict(artifact) for artifact in artifacts]
    index_artifacts = [
        {"kind": "artifact_index_json", "path": "artifact_index.json"},
        {"kind": "artifact_index", "path": "artifact_index.md"},
    ]
    indexed_artifacts = normalized + [
        artifact for artifact in index_artifacts if artifact["path"] not in {item["path"] for item in normalized}
    ]
    first_read_paths = first_read or _default_first_read(normalized)
    payload = {
        "template_name": template_name,
        "first_read": first_read_paths,
        "artifacts": [
            {
                **artifact,
                "description": _artifact_description(artifact["path"], artifact["kind"]),
                "first_read": artifact["path"] in first_read_paths,
            }
            for artifact in indexed_artifacts
        ],
    }
    (output / "artifact_index.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "artifact_index.md").write_text(_render_artifact_index(payload), encoding="utf-8")
    return [Artifact(kind=artifact["kind"], path=artifact["path"]) for artifact in index_artifacts]


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


def _artifact_to_dict(artifact: Artifact | dict) -> dict[str, str]:
    if hasattr(artifact, "to_dict"):
        return artifact.to_dict()
    return {"kind": str(artifact["kind"]), "path": str(artifact["path"])}


def _default_first_read(artifacts: list[dict[str, str]]) -> list[str]:
    preferred = [
        "run_summary.md",
        "executive_decision_brief.md",
        "value_realization_plan.md",
        "value_measurement_report.md",
        "stakeholder_rollout_map.md",
        "risk_exception_register.md",
        "operational_audit_plan.md",
        "enterprise_readiness.md",
        "query_recovery.md",
        "manual_review_pack.md",
        "adapter_starter/README.md",
        "adapter_blueprint.md",
        "business_automation_plan.md",
        "artifact_index.md",
        "report.md",
        "answer.md",
        "review-checklist.md",
        "migration-report.md",
        "docs/delivery-checklist.md",
        "README.md",
    ]
    paths = {artifact["path"] for artifact in artifacts}
    selected = [path for path in preferred if path in paths]
    if selected:
        return selected[:10]
    return [artifact["path"] for artifact in artifacts[:3]]


def _artifact_description(path: str, kind: str) -> str:
    descriptions = {
        "run_summary.md": "Shortest status summary with candidate counts and the next file to read.",
        "run_summary.json": "Structured status summary for scripts and downstream automation.",
        "executive_decision_brief.md": "Executive buy-or-wait recommendation with investment case, risks, and approval request.",
        "executive_decision_brief.json": "Structured executive decision brief for downstream reporting and governance.",
        "pilot_scorecard.md": "Pilot value-tracking scorecard with metric owners, fields, targets, evidence, and decision rules.",
        "pilot_scorecard.json": "Structured pilot scorecard for downstream reporting and governance.",
        "pilot_scorecard.csv": "Spreadsheet-ready pilot scorecard for baseline and pilot measurement tracking.",
        "value_realization_plan.md": "Business value, KPI, measurement, rollout, and go/no-go plan for automation adoption.",
        "value_realization_plan.json": "Structured value-realization plan for downstream planning and reporting.",
        "value_measurement_report.md": "Metric cards, baseline requirements, pilot measurements, and value decision thresholds.",
        "value_measurement_report.json": "Structured value measurement report for pilot comparison and reporting.",
        "stakeholder_rollout_map.md": "Role, approval, cadence, and escalation map for enterprise automation rollout.",
        "stakeholder_rollout_map.json": "Structured stakeholder rollout map for governance and project tracking.",
        "risk_exception_register.md": "Open automation rollout risks with owner, evidence, and stop condition.",
        "risk_exception_register.json": "Structured risk exception register for governance and release gates.",
        "operational_audit_plan.md": "Post-pilot audit scope, cadence, evidence requirements, and stop triggers.",
        "operational_audit_plan.json": "Structured operational audit plan for rollout monitoring.",
        "enterprise_readiness.md": "Enterprise control checklist covering production blocks, evidence, and required approvals.",
        "enterprise_readiness.json": "Structured enterprise readiness controls for review and automation.",
        "report.md": "Main source-backed research report.",
        "business_automation_plan.md": "Business-facing implementation plan and success metrics.",
        "github_candidates.md": "Ranked GitHub candidates with fit, gate, license, and next step.",
        "github_candidates.json": "Structured GitHub candidate ranking for downstream automation.",
        "github_candidates.csv": "Spreadsheet-friendly GitHub candidate ranking.",
        "github_searches.json": "Raw GitHub search metadata and returned repositories.",
        "adoption_shortlist.md": "Safest low-risk repositories to prototype first.",
        "adoption_shortlist.json": "Structured shortlist of ready-for-adapter candidates.",
        "manual_review_pack.md": "Review checklist and next actions when no candidate is ready for adapter prototyping.",
        "manual_review_pack.json": "Structured manual-review plan for candidates that need legal or maintenance review.",
        "adapter_blueprint.md": "Adapter-only implementation contract for the safest candidate.",
        "adapter_blueprint.json": "Structured adapter contract for generated or automated use.",
        "adapter_starter/README.md": "Runnable dry-run starter for the selected adapter candidate.",
        "adapter_starter/adapter.py": "Dry-run adapter skeleton with approval and rollback outputs.",
        "adapter_starter/smoke_test.py": "Local smoke test for the generated adapter starter.",
        "adapter_starter/sample_input.json": "Synthetic input payload for the generated adapter starter.",
        "query_recovery.md": "Fallback GitHub searches and next actions when no candidates are found.",
        "query_recovery.json": "Structured fallback queries for rerunning GitHub discovery.",
        "answer.md": "Grounded document answer with usage gate and operator checklist.",
        "review-checklist.md": "Human approval checklist before sending or acting.",
        "migration-report.md": "Spreadsheet migration and data-quality review.",
        "app-spec.md": "Internal app roles, workflow, and validation notes.",
        "docs/delivery-checklist.md": "Delivery readiness checklist.",
        "docs/release-plan.md": "Release steps for safe rollout.",
        "docs/rollback-plan.md": "Rollback triggers and recovery steps.",
        "artifact_index.md": "Human-readable guide to the generated output folder.",
        "artifact_index.json": "Structured guide to the generated output folder.",
    }
    return descriptions.get(path, f"{kind.replace('_', ' ').title()} artifact.")


def _render_artifact_index(payload: dict) -> str:
    lines = [
        f"# Artifact Index: {payload['template_name']}",
        "",
        "## Read First",
        "",
    ]
    lines.extend(f"- `{path}`" for path in payload["first_read"])
    lines.extend(
        [
            "",
            "## All Artifacts",
            "",
            "| Path | Kind | Description |",
            "|---|---|---|",
        ]
    )
    for artifact in payload["artifacts"]:
        lines.append(f"| `{artifact['path']}` | `{artifact['kind']}` | {artifact['description']} |")
    lines.append("")
    return "\n".join(lines)
