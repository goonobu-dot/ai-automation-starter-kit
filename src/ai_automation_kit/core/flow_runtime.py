from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


AUTOMATION_OUTPUT_FILES = [
    "work_queue.csv",
    "draft_outputs.md",
    "approval_queue.csv",
    "status_report.md",
    "run_log.json",
]


def run_flow_project(project_dir: Path, mode: str = "dry-run") -> dict:
    flow_path = project_dir / "flow.json"
    input_path = project_dir / "sample_data" / "input.csv"
    output_dir = project_dir / "automation_output"
    if not flow_path.exists():
        raise FileNotFoundError(f"Missing flow definition: {flow_path}")
    if not input_path.exists():
        raise FileNotFoundError(f"Missing sample input: {input_path}")

    flow = json.loads(flow_path.read_text(encoding="utf-8"))
    rows = list(csv.DictReader(input_path.open(newline="", encoding="utf-8")))
    output_dir.mkdir(parents=True, exist_ok=True)

    work_items = _build_work_items(flow, rows)
    approval_items = _build_approval_items(flow, work_items)
    drafts = _build_drafts(flow, work_items, approval_items, mode)
    summary = {
        "status": "succeeded",
        "mode": mode,
        "flow_id": flow["id"],
        "flow_name": flow["name"],
        "rows_processed": len(rows),
        "steps_processed": len(flow["steps"]),
        "approval_items": len(approval_items),
        "outputs": [str(output_dir / name) for name in AUTOMATION_OUTPUT_FILES],
        "safety": "No external messages were sent. No production systems were updated.",
        "finished_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }

    (output_dir / "work_queue.csv").write_text(_render_work_queue(work_items), encoding="utf-8")
    (output_dir / "approval_queue.csv").write_text(_render_approval_queue(approval_items), encoding="utf-8")
    (output_dir / "draft_outputs.md").write_text(_render_drafts(flow, drafts), encoding="utf-8")
    (output_dir / "status_report.md").write_text(_render_status_report(flow, summary, approval_items), encoding="utf-8")
    (output_dir / "run_log.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


def validate_runtime_outputs(project_dir: Path) -> dict:
    output_dir = project_dir / "automation_output"
    missing = [name for name in AUTOMATION_OUTPUT_FILES if not (output_dir / name).exists()]
    return {
        "status": "ready" if not missing else "missing_runtime_outputs",
        "missing": missing,
        "checked_files": AUTOMATION_OUTPUT_FILES,
    }


def _build_work_items(flow: dict, rows: list[dict]) -> list[dict]:
    items = []
    for row_index, row in enumerate(rows, start=1):
        for step_index, step in enumerate(flow["steps"], start=1):
            items.append(
                {
                    "item_id": f"{flow['id']}-{row_index}-{step['id']}",
                    "row_index": row_index,
                    "step_number": step_index,
                    "step_id": step["id"],
                    "step_name": step["name"],
                    "tool": step["tool"],
                    "input": step["input"],
                    "output": step["output"],
                    "human_approval": str(bool(step["human_approval"])).lower(),
                    "status": "needs human approval" if step["human_approval"] else "prepared",
                    "source_preview": _source_preview(row),
                }
            )
    return items


def _build_approval_items(flow: dict, work_items: list[dict]) -> list[dict]:
    return [
        {
            "approval_id": f"approval-{item['item_id']}",
            "step_id": item["step_id"],
            "step_name": item["step_name"],
            "tool": item["tool"],
            "reason": "human approval required before external action or production-impacting update",
            "status": "pending human approval",
            "source_preview": item["source_preview"],
            "flow_id": flow["id"],
        }
        for item in work_items
        if item["human_approval"] == "true"
    ]


def _build_drafts(flow: dict, work_items: list[dict], approval_items: list[dict], mode: str) -> list[dict]:
    approval_step_ids = {item["step_id"] for item in approval_items}
    drafts = []
    for item in work_items:
        if item["step_id"] in approval_step_ids:
            drafts.append(
                {
                    "title": item["step_name"],
                    "body": (
                        f"Draft for {flow['name']} using {item['tool']}.\n"
                        f"Source: {item['source_preview']}.\n"
                        f"Recommended next action: review `{item['output']}` before any external send or update.\n"
                        f"Mode: {mode}."
                    ),
                }
            )
    if not drafts:
        drafts.append(
            {
                "title": "Prepared workflow output",
                "body": f"{flow['name']} prepared {len(work_items)} work items in {mode} mode.",
            }
        )
    return drafts


def _render_work_queue(items: list[dict]) -> str:
    return _write_csv(
        [
            "item_id",
            "row_index",
            "step_number",
            "step_id",
            "step_name",
            "tool",
            "input",
            "output",
            "human_approval",
            "status",
            "source_preview",
        ],
        items,
    )


def _render_approval_queue(items: list[dict]) -> str:
    return _write_csv(
        ["approval_id", "flow_id", "step_id", "step_name", "tool", "reason", "status", "source_preview"],
        items,
    )


def _write_csv(fieldnames: list[str], rows: list[dict]) -> str:
    from io import StringIO

    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow({field: row.get(field, "") for field in fieldnames})
    return buffer.getvalue()


def _render_drafts(flow: dict, drafts: list[dict]) -> str:
    lines = [
        f"# Draft Outputs: {flow['name']}",
        "",
        "These are prepared outputs only. Review and approve before sending or updating production systems.",
        "",
    ]
    for index, draft in enumerate(drafts, start=1):
        lines.extend([f"## Draft {index}: {draft['title']}", "", draft["body"], ""])
    return "\n".join(lines)


def _render_status_report(flow: dict, summary: dict, approval_items: list[dict]) -> str:
    return "\n".join(
        [
            f"# Automation Status Report: {flow['name']}",
            "",
            f"- Flow ID: `{flow['id']}`",
            f"- Mode: `{summary['mode']}`",
            f"- Rows processed: `{summary['rows_processed']}`",
            f"- Steps processed: `{summary['steps_processed']}`",
            f"- Approval items: `{summary['approval_items']}`",
            "",
            "## Safety",
            "",
            summary["safety"],
            "",
            "## Pending Human Approval",
            "",
            *[f"- `{item['step_id']}`: {item['step_name']} ({item['reason']})" for item in approval_items],
            "",
        ]
    )


def _source_preview(row: dict) -> str:
    parts = []
    for key, value in list(row.items())[:4]:
        parts.append(f"{key}={value}")
    return "; ".join(parts)
