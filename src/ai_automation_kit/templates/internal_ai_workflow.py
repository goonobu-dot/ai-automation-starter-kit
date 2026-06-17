from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from ai_automation_kit.core.artifacts import write_artifact_index
from ai_automation_kit.core.models import ApprovalRequest, Artifact, RunRecord
from ai_automation_kit.core.store import JsonRunStore


def run_internal_ai_workflow(config_path: Path | str, output_dir: Path | str) -> RunRecord:
    config_file = Path(config_path)
    output = Path(output_dir)
    config = json.loads(config_file.read_text(encoding="utf-8"))
    inquiry_text = config["inquiry_text"]
    customer_name = config.get("customer_name")

    started_at = _now()
    run_id = f"run-{uuid4().hex[:12]}"
    draft = _build_draft(inquiry_text=inquiry_text, customer_name=customer_name)
    approval = ApprovalRequest(
        action_id=f"{run_id}-send-reply",
        action_type="send_reply",
        payload={
            "draft_path": "draft_reply.md",
            "draft_json_path": "draft_reply.json",
            "customer_name": customer_name,
        },
    )
    artifacts = _write_internal_workflow_artifacts(output, draft, approval)
    artifacts.extend(
        write_artifact_index(
            output,
            "internal-ai-workflow",
            artifacts,
            first_read=["review-checklist.md", "draft_reply.md", "approval_request.json"],
        )
    )
    finished_at = _now()
    run = RunRecord(
        run_id=run_id,
        template_name="internal-ai-workflow",
        input={"inquiry_text": inquiry_text, "customer_name": customer_name},
        started_at=started_at,
        finished_at=finished_at,
        status="succeeded",
        errors=[],
        artifacts=artifacts,
    )
    JsonRunStore(output).save_run(run)
    return run


def _build_draft(inquiry_text: str, customer_name: str | None) -> dict:
    greeting = f"Hi {customer_name}," if customer_name else "Hi there,"
    body = (
        f"{greeting}\n\n"
        "Thanks for reaching out. We can help with this request.\n\n"
        f"You asked: \"{inquiry_text}\"\n\n"
        "Here is a suggested next step: share the current pricing overview, confirm the onboarding goal, "
        "and offer a short call if they want help mapping the workflow.\n\n"
        "Best,\nAI Automation Team\n"
    )
    return {
        "customer_name": customer_name,
        "inquiry_text": inquiry_text,
        "reply_markdown": body,
        "risk_level": _risk_level(inquiry_text),
        "approval_checks": _approval_checks(inquiry_text),
        "sla": _sla(inquiry_text),
        "owner_role": _owner_role(inquiry_text),
        "escalation_path": _escalation_path(inquiry_text),
    }


def _write_internal_workflow_artifacts(output: Path, draft: dict, approval: ApprovalRequest) -> list[Artifact]:
    output.mkdir(parents=True, exist_ok=True)
    (output / "draft_reply.md").write_text(draft["reply_markdown"], encoding="utf-8")
    (output / "draft_reply.json").write_text(json.dumps(draft, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "review-checklist.md").write_text(_render_review_checklist(draft), encoding="utf-8")
    (output / "approval_request.json").write_text(
        json.dumps(approval.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return [
        Artifact(kind="markdown", path="draft_reply.md"),
        Artifact(kind="json", path="draft_reply.json"),
        Artifact(kind="markdown", path="review-checklist.md"),
        Artifact(kind="approval_request", path="approval_request.json"),
    ]


def _risk_level(inquiry_text: str) -> str:
    text = inquiry_text.lower()
    if any(term in text for term in ["refund", "legal", "contract", "security", "delete", "cancel"]):
        return "high"
    if any(term in text for term in ["pricing", "onboarding", "integration", "customer", "account"]):
        return "medium"
    return "low"


def _approval_checks(inquiry_text: str) -> list[str]:
    checks = [
        "Confirm the reply does not include secrets, credentials, or private customer data.",
        "Confirm the suggested next step matches the current product or service policy.",
    ]
    if "pricing" in inquiry_text.lower():
        checks.insert(0, "Confirm pricing is current before sending.")
    return checks


def _render_review_checklist(draft: dict) -> str:
    lines = [
        "# Review Checklist",
        "",
        f"- Risk level: `{draft['risk_level']}`",
        "",
        "## Approval Checks",
        "",
    ]
    lines.extend(f"- [ ] {check}" for check in draft["approval_checks"])
    lines.extend(
        [
            "",
            "## SLA And Ownership",
            "",
            f"- Owner role: {draft['owner_role']}",
            f"- SLA: {draft['sla']}",
            "",
            "## Escalation Path",
            "",
        ]
    )
    lines.extend(f"- {step}" for step in draft["escalation_path"])
    lines.extend(["", "## Decision", "", "- [ ] Approve and send", "- [ ] Revise draft", "- [ ] Escalate to owner", ""])
    return "\n".join(lines)


def _sla(inquiry_text: str) -> str:
    risk = _risk_level(inquiry_text)
    if risk == "high":
        return "Respond only after owner review; target same business day triage."
    if risk == "medium":
        return "Respond within 1 business day after approval."
    return "Respond within 2 business days after approval."


def _owner_role(inquiry_text: str) -> str:
    text = inquiry_text.lower()
    if any(term in text for term in ["pricing", "onboarding", "account", "customer"]):
        return "Customer success or sales owner"
    if any(term in text for term in ["security", "legal", "contract", "delete"]):
        return "Compliance or account owner"
    return "Workflow owner"


def _escalation_path(inquiry_text: str) -> list[str]:
    if _risk_level(inquiry_text) == "high":
        return [
            "Escalate to the account owner before sending.",
            "Attach the original inquiry and draft reply.",
            "Wait for explicit approval in the run record.",
        ]
    return [
        "Escalate to the account owner if pricing, policy, or timeline is uncertain.",
        "Attach the draft reply and review checklist.",
    ]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
