from __future__ import annotations

import json
from pathlib import Path


REQUIRED_PROJECT_FILES = [
    "README.md",
    "flow.yaml",
    "flow.json",
    "workflow_map.mmd",
    "before_after_workflow.md",
    "human_approval_points.md",
    "sample_data/input.csv",
    "scripts/run_dry_run.py",
    "tests/test_flow_contract.py",
]


def _step(step_id: str, name: str, tool: str, input_data: str, output: str, human_approval: bool) -> dict:
    return {
        "id": step_id,
        "name": name,
        "tool": tool,
        "input": input_data,
        "output": output,
        "human_approval": human_approval,
    }


FLOW_CATALOG = [
    {
        "id": "invoice-document-followup",
        "name": "Invoice and Document Follow-up",
        "industry": "finance",
        "genre": "document",
        "summary": "Track missing invoices or documents, draft follow-up messages, and create a weekly status report.",
        "tools": ["Google Sheets", "Gmail / Outlook", "Slack / Teams"],
        "sample_columns": ["client", "missing_document", "due_date", "owner", "status"],
        "steps": [
            _step("intake", "Read missing document list", "Google Sheets", "Spreadsheet rows", "Normalized work queue", False),
            _step("classify", "Prioritize overdue or high-value requests", "Local rules", "Work queue", "Priority labels", False),
            _step("draft", "Create follow-up draft", "Gmail / Outlook", "Priority queue", "Draft message", True),
            _step("notify", "Notify owner for review", "Slack / Teams", "Draft message", "Approval request", True),
            _step("report", "Create weekly collection report", "Google Sheets", "Reviewed statuses", "Status report", False),
        ],
        "success_metrics": ["hours_saved", "fewer_missing_documents", "faster_follow_up"],
    },
    {
        "id": "support-reply-draft",
        "name": "Support Reply Draft",
        "industry": "support",
        "genre": "communication",
        "summary": "Turn inbound customer questions into categorized reply drafts with human approval before sending.",
        "tools": ["Helpdesk export", "Docs", "Gmail / Outlook"],
        "sample_columns": ["ticket_id", "customer", "question", "priority", "status"],
        "steps": [
            _step("intake", "Read new support inquiries", "Helpdesk export", "Ticket rows", "Question queue", False),
            _step("retrieve", "Find likely policy or FAQ context", "Docs", "Question queue", "Context notes", False),
            _step("draft", "Draft customer reply", "AI assistant", "Question and context", "Reply draft", True),
            _step("approve", "Reviewer approves or edits draft", "Human reviewer", "Reply draft", "Approved reply", True),
            _step("log", "Record response status", "Helpdesk export", "Approved reply", "Updated ticket log", False),
        ],
        "success_metrics": ["reply_time", "draft_acceptance_rate", "escalation_rate"],
    },
    {
        "id": "weekly-kpi-report",
        "name": "Weekly KPI Report",
        "industry": "operations",
        "genre": "reporting",
        "summary": "Collect spreadsheet metrics, summarize changes, and produce a weekly operator report.",
        "tools": ["Google Sheets", "Markdown report", "Slack / Teams"],
        "sample_columns": ["metric", "last_week", "this_week", "owner", "note"],
        "steps": [
            _step("collect", "Read KPI rows", "Google Sheets", "Metric table", "Validated metrics", False),
            _step("compare", "Calculate week-over-week changes", "Local rules", "Validated metrics", "Change list", False),
            _step("explain", "Draft short explanations", "AI assistant", "Change list", "Narrative report", True),
            _step("review", "Owner checks claims", "Human reviewer", "Narrative report", "Approved report", True),
            _step("publish", "Post approved summary", "Slack / Teams", "Approved report", "Team update", False),
        ],
        "success_metrics": ["reporting_time", "metric_coverage", "decision_cycle_time"],
    },
    {
        "id": "purchase-approval-routing",
        "name": "Purchase Approval Routing",
        "industry": "operations",
        "genre": "approval",
        "summary": "Route purchase requests to the right approver and keep a decision trail.",
        "tools": ["Form export", "Slack / Teams", "Google Sheets"],
        "sample_columns": ["request_id", "requester", "amount", "category", "approver"],
        "steps": [
            _step("intake", "Read purchase request", "Form export", "Request row", "Request packet", False),
            _step("route", "Select approval owner", "Local rules", "Request packet", "Approver assignment", False),
            _step("request", "Send approval request", "Slack / Teams", "Approver assignment", "Approval message", True),
            _step("record", "Record decision", "Google Sheets", "Approver response", "Decision log", False),
            _step("escalate", "Flag overdue decisions", "Slack / Teams", "Decision log", "Escalation note", True),
        ],
        "success_metrics": ["approval_cycle_time", "overdue_count", "audit_completeness"],
    },
    {
        "id": "github-oss-research",
        "name": "GitHub OSS Research Pack",
        "industry": "operations",
        "genre": "research",
        "summary": "Research public GitHub projects, shortlist candidates, and produce adoption evidence.",
        "tools": ["GitHub API", "Markdown report", "CSV scorecard"],
        "sample_columns": ["query", "repo", "stars", "license", "risk"],
        "steps": [
            _step("search", "Search public repositories", "GitHub API", "Search query", "Candidate list", False),
            _step("score", "Score candidates", "Local rules", "Candidate list", "Ranked shortlist", False),
            _step("review", "Review license and maintenance", "Human reviewer", "Ranked shortlist", "Approved candidate", True),
            _step("plan", "Draft adoption plan", "Markdown report", "Approved candidate", "Pilot plan", True),
            _step("handoff", "Create implementation checklist", "CSV scorecard", "Pilot plan", "Handoff checklist", False),
        ],
        "success_metrics": ["review_time", "candidate_quality", "blocked_risk_count"],
    },
    {
        "id": "crm-lead-cleanup",
        "name": "CRM Lead Cleanup",
        "industry": "sales",
        "genre": "data-cleanup",
        "summary": "Find stale or incomplete leads and generate safe cleanup recommendations.",
        "tools": ["CRM export", "CSV report", "Slack / Teams"],
        "sample_columns": ["lead_id", "company", "last_contacted", "stage", "owner"],
        "steps": [
            _step("export", "Read CRM export", "CRM export", "Lead rows", "Lead queue", False),
            _step("detect", "Find stale or incomplete leads", "Local rules", "Lead queue", "Cleanup candidates", False),
            _step("recommend", "Draft next action", "AI assistant", "Cleanup candidates", "Action recommendations", True),
            _step("approve", "Sales owner approves updates", "Human reviewer", "Action recommendations", "Approved actions", True),
            _step("track", "Write cleanup report", "CSV report", "Approved actions", "Cleanup scorecard", False),
        ],
        "success_metrics": ["stale_lead_reduction", "owner_response_rate", "pipeline_hygiene"],
    },
    {
        "id": "sales-meeting-prep",
        "name": "Sales Meeting Prep",
        "industry": "sales",
        "genre": "research",
        "summary": "Prepare account notes, open questions, and a meeting brief from approved sources.",
        "tools": ["CRM export", "Docs", "Markdown brief"],
        "sample_columns": ["account", "opportunity", "recent_note", "risk", "next_meeting"],
        "steps": [
            _step("collect", "Collect account notes", "CRM export", "Account rows", "Account packet", False),
            _step("summarize", "Summarize recent activity", "AI assistant", "Account packet", "Prep summary", True),
            _step("questions", "Draft discovery questions", "AI assistant", "Prep summary", "Question list", True),
            _step("review", "Rep reviews sensitive claims", "Human reviewer", "Meeting brief", "Approved brief", True),
            _step("archive", "Save prep brief", "Markdown brief", "Approved brief", "Prep artifact", False),
        ],
        "success_metrics": ["prep_time_saved", "meeting_quality", "follow_up_completion"],
    },
    {
        "id": "employee-onboarding-checklist",
        "name": "Employee Onboarding Checklist",
        "industry": "hr",
        "genre": "approval",
        "summary": "Track onboarding tasks, missing setup items, and manager reminders.",
        "tools": ["HR spreadsheet", "Slack / Teams", "Checklist"],
        "sample_columns": ["employee", "start_date", "task", "owner", "status"],
        "steps": [
            _step("intake", "Read onboarding task list", "HR spreadsheet", "Task rows", "Onboarding queue", False),
            _step("detect", "Find missing or overdue tasks", "Local rules", "Onboarding queue", "Reminder list", False),
            _step("draft", "Draft manager reminders", "AI assistant", "Reminder list", "Reminder drafts", True),
            _step("approve", "HR owner approves reminders", "Human reviewer", "Reminder drafts", "Approved reminders", True),
            _step("report", "Create onboarding status report", "Checklist", "Task statuses", "Status report", False),
        ],
        "success_metrics": ["onboarding_completion", "overdue_tasks", "manager_response_time"],
    },
    {
        "id": "recruiting-screen-summary",
        "name": "Recruiting Screen Summary",
        "industry": "hr",
        "genre": "document",
        "summary": "Summarize screening notes and route candidates for human decision.",
        "tools": ["ATS export", "Docs", "Scorecard"],
        "sample_columns": ["candidate", "role", "screen_notes", "stage", "recruiter"],
        "steps": [
            _step("collect", "Read screening notes", "ATS export", "Candidate rows", "Candidate packet", False),
            _step("summarize", "Summarize notes against criteria", "AI assistant", "Candidate packet", "Screen summary", True),
            _step("flag", "Flag missing evidence", "Local rules", "Screen summary", "Review flags", False),
            _step("review", "Recruiter reviews summary", "Human reviewer", "Screen summary", "Approved summary", True),
            _step("handoff", "Create hiring team handoff", "Scorecard", "Approved summary", "Handoff note", False),
        ],
        "success_metrics": ["summary_time", "missing_evidence_rate", "handoff_quality"],
    },
    {
        "id": "campaign-content-review",
        "name": "Campaign Content Review",
        "industry": "marketing",
        "genre": "communication",
        "summary": "Draft campaign variants and route them through brand and legal review.",
        "tools": ["Content brief", "Docs", "Approval tracker"],
        "sample_columns": ["campaign", "channel", "message", "owner", "review_status"],
        "steps": [
            _step("brief", "Read campaign brief", "Content brief", "Brief rows", "Creative packet", False),
            _step("draft", "Draft campaign variants", "AI assistant", "Creative packet", "Message variants", True),
            _step("brand", "Route brand review", "Approval tracker", "Message variants", "Brand decision", True),
            _step("legal", "Route legal review if required", "Approval tracker", "Brand decision", "Legal decision", True),
            _step("publish_plan", "Create approved publishing list", "Docs", "Approved messages", "Publishing plan", False),
        ],
        "success_metrics": ["review_cycle_time", "approved_variant_rate", "revision_count"],
    },
    {
        "id": "expense-policy-check",
        "name": "Expense Policy Check",
        "industry": "finance",
        "genre": "approval",
        "summary": "Check expense rows against policy hints and create reviewer queues without auto-rejecting.",
        "tools": ["Expense export", "Policy docs", "CSV report"],
        "sample_columns": ["expense_id", "employee", "amount", "category", "receipt_status"],
        "steps": [
            _step("export", "Read expense rows", "Expense export", "Expense rows", "Expense queue", False),
            _step("policy", "Match policy hints", "Policy docs", "Expense queue", "Policy notes", False),
            _step("flag", "Flag review-needed items", "Local rules", "Policy notes", "Reviewer queue", False),
            _step("review", "Finance reviews flagged items", "Human reviewer", "Reviewer queue", "Review decisions", True),
            _step("report", "Create audit trail report", "CSV report", "Review decisions", "Audit trail", False),
        ],
        "success_metrics": ["review_time", "policy_exception_rate", "audit_completeness"],
    },
    {
        "id": "it-access-request",
        "name": "IT Access Request",
        "industry": "it",
        "genre": "approval",
        "summary": "Route software or account access requests with owner approval and evidence logs.",
        "tools": ["Form export", "Identity checklist", "Slack / Teams"],
        "sample_columns": ["request_id", "employee", "system", "access_level", "manager"],
        "steps": [
            _step("intake", "Read access request", "Form export", "Request rows", "Access queue", False),
            _step("classify", "Classify system and access level", "Identity checklist", "Access queue", "Risk label", False),
            _step("approve", "Ask manager or system owner approval", "Slack / Teams", "Risk label", "Approval record", True),
            _step("handoff", "Create IT fulfillment note", "Identity checklist", "Approval record", "Fulfillment note", True),
            _step("audit", "Record access evidence", "CSV report", "Fulfillment note", "Audit log", False),
        ],
        "success_metrics": ["request_cycle_time", "approval_traceability", "access_error_rate"],
    },
]


def list_flows(industry: str | None = None, genre: str | None = None) -> list[dict]:
    flows = FLOW_CATALOG
    if industry:
        flows = [flow for flow in flows if flow["industry"] == industry]
    if genre:
        flows = [flow for flow in flows if flow["genre"] == genre]
    return [_flow_summary(flow) for flow in flows]


def get_flow(flow_id: str) -> dict:
    for flow in FLOW_CATALOG:
        if flow["id"] == flow_id:
            return {**flow, "risk_policy": _risk_policy(flow)}
    raise KeyError(f"Unknown flow: {flow_id}")


def install_flow(flow_id: str, output: Path) -> dict:
    flow = get_flow(flow_id)
    output.mkdir(parents=True, exist_ok=True)
    (output / "sample_data").mkdir(exist_ok=True)
    (output / "scripts").mkdir(exist_ok=True)
    (output / "tests").mkdir(exist_ok=True)

    payload = {
        "flow_id": flow["id"],
        "name": flow["name"],
        "industry": flow["industry"],
        "genre": flow["genre"],
        "status": "installed",
        "required_files": REQUIRED_PROJECT_FILES,
    }
    (output / "README.md").write_text(_render_project_readme(flow), encoding="utf-8")
    (output / "flow.yaml").write_text(_render_flow_yaml(flow), encoding="utf-8")
    (output / "flow.json").write_text(json.dumps(flow, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "workflow_map.mmd").write_text(_render_mermaid(flow), encoding="utf-8")
    (output / "before_after_workflow.md").write_text(_render_before_after(flow), encoding="utf-8")
    (output / "human_approval_points.md").write_text(_render_approval_points(flow), encoding="utf-8")
    (output / "sample_data" / "input.csv").write_text(_render_sample_csv(flow), encoding="utf-8")
    (output / "scripts" / "run_dry_run.py").write_text(_render_dry_run_script(flow), encoding="utf-8")
    (output / "tests" / "test_flow_contract.py").write_text(_render_contract_test(flow), encoding="utf-8")
    return payload


def validate_flow_project(output: Path) -> dict:
    missing = [path for path in REQUIRED_PROJECT_FILES if not (output / path).exists()]
    return {
        "status": "ready" if not missing else "missing_files",
        "missing": missing,
        "checked_files": REQUIRED_PROJECT_FILES,
    }


def _flow_summary(flow: dict) -> dict:
    return {
        "id": flow["id"],
        "name": flow["name"],
        "industry": flow["industry"],
        "genre": flow["genre"],
        "summary": flow["summary"],
    }


def _risk_policy(flow: dict) -> dict:
    return {
        "production_guardrail": "Keep external sends, production updates, payments, hiring decisions, and access grants behind human approval.",
        "dry_run_first": True,
        "human_approval_steps": [step["id"] for step in flow["steps"] if step["human_approval"]],
    }


def _render_project_readme(flow: dict) -> str:
    return "\n".join(
        [
            f"# {flow['name']}",
            "",
            flow["summary"],
            "",
            f"- Industry: `{flow['industry']}`",
            f"- Genre: `{flow['genre']}`",
            f"- Flow ID: `{flow['id']}`",
            "",
            "## Files",
            "",
            "- `flow.yaml` - editable flow definition.",
            "- `workflow_map.mmd` - Mermaid workflow diagram.",
            "- `before_after_workflow.md` - before/after business explanation.",
            "- `human_approval_points.md` - steps that require human review.",
            "- `sample_data/input.csv` - safe sample input data.",
            "- `scripts/run_dry_run.py` - local dry-run script.",
            "",
            "## Run The Dry Run",
            "",
            "```bash",
            "python3 scripts/run_dry_run.py",
            "python3 -m pytest tests/test_flow_contract.py -q",
            "```",
            "",
            "This scaffold is safe-by-default. It does not send external messages or update production systems.",
            "",
        ]
    )


def _render_flow_yaml(flow: dict) -> str:
    lines = [
        f"id: {flow['id']}",
        f"name: {flow['name']}",
        f"industry: {flow['industry']}",
        f"genre: {flow['genre']}",
        f"summary: {flow['summary']}",
        "tools:",
    ]
    lines.extend(f"  - {tool}" for tool in flow["tools"])
    lines.append("steps:")
    for index, step in enumerate(flow["steps"], start=1):
        lines.extend(
            [
                f"  - number: {index}",
                f"    id: {step['id']}",
                f"    name: {step['name']}",
                f"    tool: {step['tool']}",
                f"    input: {step['input']}",
                f"    output: {step['output']}",
                f"    human_approval: {str(step['human_approval']).lower()}",
            ]
        )
    lines.append("success_metrics:")
    lines.extend(f"  - {metric}" for metric in flow["success_metrics"])
    lines.append("risk_policy:")
    lines.append(f"  production_guardrail: {_risk_policy(flow)['production_guardrail']}")
    lines.append("  dry_run_first: true")
    return "\n".join(lines) + "\n"


def _render_mermaid(flow: dict) -> str:
    lines = ["flowchart TD"]
    previous = None
    for index, step in enumerate(flow["steps"], start=1):
        node = f"S{index}"
        label = f"{index}. {step['name']}\\n{step['tool']}"
        if step["human_approval"]:
            label += "\\nHuman approval"
        lines.append(f'  {node}["{label}"]')
        if previous:
            lines.append(f"  {previous} --> {node}")
        previous = node
    return "\n".join(lines) + "\n"


def _render_before_after(flow: dict) -> str:
    return "\n".join(
        [
            f"# Before / After: {flow['name']}",
            "",
            "## Before",
            "",
            "- Work is tracked manually across inboxes, spreadsheets, or chat.",
            "- Status is hard to audit.",
            "- Follow-up depends on individual memory.",
            "- Reporting requires repeated copy and paste.",
            "",
            "## After",
            "",
            "- Work enters a visible queue.",
            "- Safe steps run in dry-run mode first.",
            "- Human approval is preserved where decisions affect customers, money, hiring, access, or production data.",
            "- Output files and logs provide evidence for client review.",
            "",
        ]
    )


def _render_approval_points(flow: dict) -> str:
    lines = [f"# Human Approval Points: {flow['name']}", ""]
    approval_steps = [step for step in flow["steps"] if step["human_approval"]]
    for step in approval_steps:
        lines.extend(
            [
                f"## {step['id']}: {step['name']}",
                "",
                f"- Tool: {step['tool']}",
                f"- Input: {step['input']}",
                f"- Output: {step['output']}",
                "- Rule: do not send, update production, approve, reject, grant access, or make irreversible changes without named owner review.",
                "",
            ]
        )
    return "\n".join(lines)


def _render_sample_csv(flow: dict) -> str:
    header = ",".join(flow["sample_columns"])
    sample = ",".join(_sample_value(column) for column in flow["sample_columns"])
    return f"{header}\n{sample}\n"


def _sample_value(column: str) -> str:
    samples = {
        "client": "Acme Co",
        "missing_document": "June invoice",
        "due_date": "2026-06-30",
        "owner": "ops@example.com",
        "status": "open",
        "ticket_id": "T-1001",
        "customer": "Avery",
        "question": "Can you confirm the next step?",
        "priority": "normal",
        "metric": "open_tasks",
        "last_week": "42",
        "this_week": "31",
        "note": "sample",
    }
    return samples.get(column, f"sample_{column}")


def _render_dry_run_script(flow: dict) -> str:
    return f'''from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "sample_data" / "input.csv"
OUTPUT = ROOT / "dry_run_output.md"


def main() -> int:
    rows = list(csv.DictReader(INPUT.open(newline="", encoding="utf-8")))
    lines = [
        "# Dry Run Output",
        "",
        "Flow: {flow['name']}",
        "Mode: dry-run only",
        "",
        f"Rows processed: {{len(rows)}}",
        "",
        "No external messages were sent. No production systems were updated.",
    ]
    OUTPUT.write_text("\\n".join(lines) + "\\n", encoding="utf-8")
    print(f"dry_run_output={{OUTPUT}}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def _render_contract_test(flow: dict) -> str:
    return f'''from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_flow_contract_files_exist():
    assert (ROOT / "flow.yaml").exists()
    assert (ROOT / "workflow_map.mmd").exists()
    assert (ROOT / "sample_data" / "input.csv").exists()


def test_flow_stays_dry_run_first():
    text = (ROOT / "flow.yaml").read_text(encoding="utf-8")
    assert "id: {flow['id']}" in text
    assert "dry_run_first: true" in text
    assert "human_approval: true" in text
'''
