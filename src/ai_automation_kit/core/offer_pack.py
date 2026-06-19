from __future__ import annotations

import json
from pathlib import Path


ARTIFACTS = [
    "README.md",
    "service_catalog.md",
    "client_discovery_questions.md",
    "proposal.md",
    "statement_of_work.md",
    "pricing_model.md",
    "demo_script.md",
    "outreach_messages.md",
    "delivery_checklist.md",
    "risk_boundaries.md",
    "offer_pack.json",
]


def generate_offer_pack(source_output: Path, output: Path, business_area: str, client_type: str) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    source_summary = _load_source_summary(source_output)
    payload = {
        "business_area": business_area,
        "client_type": client_type,
        "source_output": str(source_output),
        "source_status": "ready" if source_output.exists() else "missing",
        "source_summary": source_summary,
        "artifacts": ARTIFACTS,
        "positioning": _positioning(business_area, client_type),
    }
    renderers = {
        "README.md": _render_readme,
        "service_catalog.md": _render_service_catalog,
        "client_discovery_questions.md": _render_discovery_questions,
        "proposal.md": _render_proposal,
        "statement_of_work.md": _render_statement_of_work,
        "pricing_model.md": _render_pricing_model,
        "demo_script.md": _render_demo_script,
        "outreach_messages.md": _render_outreach_messages,
        "delivery_checklist.md": _render_delivery_checklist,
        "risk_boundaries.md": _render_risk_boundaries,
    }
    for filename, renderer in renderers.items():
        (output / filename).write_text(renderer(payload), encoding="utf-8")
    (output / "offer_pack.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def _load_source_summary(source_output: Path) -> dict:
    if not source_output.exists():
        return {
            "executive_recommendation": "Run discovery or use this starter pack to scope a first automation pilot.",
            "recommended_projects": [],
        }
    for name in ["business_automation_summary.json", "onboarding_summary.json", "run_summary.json"]:
        path = source_output / name
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return data
            except json.JSONDecodeError:
                continue
    return {
        "executive_recommendation": "Discovery artifacts were found, but no structured summary was available.",
        "recommended_projects": [],
    }


def _positioning(business_area: str, client_type: str) -> str:
    return (
        f"A practical {business_area} automation pilot for a {client_type} client, "
        "delivered as a small paid discovery-to-prototype engagement with human approval and measurable outcomes."
    )


def _recommendation(payload: dict) -> str:
    summary = payload["source_summary"]
    return summary.get("executive_recommendation") or summary.get("status") or "Start with one low-risk automation pilot."


def _project_lines(payload: dict) -> list[str]:
    projects = payload["source_summary"].get("recommended_projects") or []
    if not projects:
        return ["- No specific OSS candidate is locked yet. Use discovery notes and client data to choose a safe prototype."]
    lines = []
    for project in projects[:5]:
        name = project.get("full_name", "unnamed project")
        url = project.get("url", "")
        lines.append(f"- {name}: {url or 'review source output for URL'}")
    return lines


def _render_readme(payload: dict) -> str:
    lines = [
        f"# Offer Pack: {payload['business_area']} Automation",
        "",
        payload["positioning"],
        "",
        "## Read First",
        "",
        "1. `service_catalog.md` to choose a sellable package.",
        "2. `client_discovery_questions.md` before the first call.",
        "3. `proposal.md` and `statement_of_work.md` for the client-facing offer.",
        "4. `pricing_model.md` to choose a responsible price range.",
        "5. `risk_boundaries.md` before handling client data.",
        "",
        "## Source Recommendation",
        "",
        _recommendation(payload),
        "",
    ]
    return "\n".join(lines)


def _render_service_catalog(payload: dict) -> str:
    area = payload["business_area"]
    lines = [
        f"# Service Catalog: {area} Automation",
        "",
        "Use these as small, paid pilot offers. Keep the first scope narrow enough to deliver in days, not months.",
        "",
        "| Offer | Client Pain | Deliverable | Good First Price Shape |",
        "|---|---|---|---|",
        f"| {area.title()} Workflow Audit | Team does not know what to automate first | automation map, risk list, 30-day pilot plan | fixed-fee discovery |",
        f"| {area.title()} Dry-Run Prototype | Team wants proof before production | local dry-run adapter, demo script, scorecard | fixed-fee prototype |",
        f"| {area.title()} Reporting Pack | Team lacks visibility | dashboard plan, CSV scorecard, weekly report template | setup fee plus monthly reporting |",
        "| Automation Maintenance | Existing workflows break or drift | monitoring checklist, change log, monthly review | monthly retainer |",
        "",
        "## Candidate OSS References",
        "",
    ]
    lines.extend(_project_lines(payload))
    lines.append("")
    return "\n".join(lines)


def _render_discovery_questions(payload: dict) -> str:
    area = payload["business_area"]
    lines = [
        f"# Client Discovery Questions: {area} Automation",
        "",
        "## Business Outcome",
        "",
        f"- Which {area} task consumes the most repeated human time each week?",
        "- What happens when this task is late, skipped, or done incorrectly?",
        "- What metric would prove the automation helped?",
        "",
        "## Current Workflow",
        "",
        "- Which tools are involved today?",
        "- Where does the workflow start and end?",
        "- Which step requires human approval?",
        "- Which data is sensitive, private, or regulated?",
        "",
        "## Pilot Boundary",
        "",
        "- Can the first version run on sample or exported data only?",
        "- Who approves the dry-run result before production use?",
        "- What is the stop condition if quality is not high enough?",
        "",
    ]
    return "\n".join(lines)


def _render_proposal(payload: dict) -> str:
    area = payload["business_area"]
    client_type = payload["client_type"]
    lines = [
        f"# Proposal: {area.title()} Automation Pilot",
        "",
        f"Prepared for: `{client_type}`",
        "",
        "## Executive Summary",
        "",
        _recommendation(payload),
        "",
        "This proposal starts with a controlled pilot. The goal is to reduce repeated manual work while keeping approval, data handling, and rollback clear.",
        "",
        "## Proposed Scope",
        "",
        f"1. Map one {area} workflow.",
        "2. Identify the lowest-risk automation step.",
        "3. Build a dry-run prototype using sample or exported data.",
        "4. Measure results with a pilot scorecard.",
        "5. Decide whether to promote, revise, or stop.",
        "",
        "## Relevant OSS Signals",
        "",
    ]
    lines.extend(_project_lines(payload))
    lines.extend(
        [
            "",
            "## Success Metrics",
            "",
            "- Manual handoffs reduced.",
            "- Time-to-complete reduced.",
            "- Error rate reduced or unchanged.",
            "- Human approval remains visible.",
            "- Client can explain the workflow after handoff.",
            "",
        ]
    )
    return "\n".join(lines)


def _render_statement_of_work(payload: dict) -> str:
    area = payload["business_area"]
    lines = [
        f"# Statement of Work: {area.title()} Automation Pilot",
        "",
        "## Deliverables",
        "",
        "- Workflow map and automation opportunity summary.",
        "- Dry-run prototype or adapter plan.",
        "- Pilot scorecard and measurement notes.",
        "- Delivery checklist and client handoff notes.",
        "- Risk boundary document.",
        "",
        "## Out of Scope",
        "",
        "- Production access to private systems without written approval.",
        "- Legal, tax, HR, medical, or financial advice.",
        "- Secret handling outside approved client infrastructure.",
        "- Guaranteed revenue, guaranteed savings, or guaranteed lead volume.",
        "",
        "## Acceptance Criteria",
        "",
        "- Prototype runs on sample or approved exported data.",
        "- Client can review inputs, outputs, and failure cases.",
        "- A human approval step is defined before production use.",
        "- Open risks are listed with owners and stop conditions.",
        "",
    ]
    return "\n".join(lines)


def _render_pricing_model(payload: dict) -> str:
    lines = [
        "# Pricing Model",
        "",
        "No income is guaranteed. Pricing depends on client urgency, scope, risk, and the developer's ability to deliver and support the work.",
        "",
        "| Package | Typical Scope | Pricing Shape |",
        "|---|---|---|",
        "| Automation Audit | interviews, workflow map, pilot recommendation | small fixed fee |",
        "| Dry-Run Prototype | one workflow, sample data, demo, scorecard | fixed project fee |",
        "| Production Handoff | approval gates, docs, deployment checklist | larger fixed fee after prototype |",
        "| Monthly Maintenance | monitoring, fixes, minor improvements | monthly retainer |",
        "",
        "## Pricing Rules",
        "",
        "- Charge for diagnosis before promising implementation.",
        "- Keep the first paid pilot narrow.",
        "- Separate one-time setup from monthly support.",
        "- Do not price risky integrations before access, data shape, and approval owners are clear.",
        "",
    ]
    return "\n".join(lines)


def _render_demo_script(payload: dict) -> str:
    lines = [
        "# Demo Script",
        "",
        "1. Explain the current manual workflow in one sentence.",
        "2. Show the input data using sample or approved exported data.",
        "3. Run the dry-run automation.",
        "4. Show the generated output and the human approval point.",
        "5. Open the pilot scorecard and explain how success will be measured.",
        "6. Explain what is intentionally not automated yet.",
        "",
        "Close with: `If this dry-run result is useful, the next step is a limited pilot with approval and monitoring.`",
        "",
    ]
    return "\n".join(lines)


def _render_outreach_messages(payload: dict) -> str:
    area = payload["business_area"]
    lines = [
        "# Outreach Messages",
        "",
        "## Short DM",
        "",
        f"I help teams turn repeated {area} work into small, measurable automation pilots. I start with a workflow audit and dry-run prototype, so you can review value and risk before production. Is there one repetitive workflow you want mapped?",
        "",
        "## Email",
        "",
        f"Subject: Small {area} automation pilot",
        "",
        f"I am putting together small {area} automation pilots for teams that want practical improvements without risky big-bang automation. The first step is a workflow map, a dry-run prototype, and a scorecard that shows whether the automation is worth expanding.",
        "",
        "If useful, I can review one repeated workflow and send a short pilot plan.",
        "",
        "## X Post",
        "",
        f"I am testing a practical {area} automation offer: workflow audit -> dry-run prototype -> pilot scorecard -> safe handoff. Built for teams that want measurable automation without handing private systems to an unreviewed script.",
        "",
    ]
    return "\n".join(lines)


def _render_delivery_checklist(payload: dict) -> str:
    lines = [
        "# Delivery Checklist",
        "",
        "- [ ] Client workflow owner is named.",
        "- [ ] Input data source is approved.",
        "- [ ] Sensitive fields are removed or masked for dry-run.",
        "- [ ] Prototype has a human approval step.",
        "- [ ] Pilot scorecard has baseline and target fields.",
        "- [ ] Failure cases are documented.",
        "- [ ] Rollback or stop condition is documented.",
        "- [ ] Client receives proposal, SOW, demo script, and risk boundaries.",
        "",
    ]
    return "\n".join(lines)


def _render_risk_boundaries(payload: dict) -> str:
    lines = [
        "# Risk Boundaries",
        "",
        "This offer pack is for scoped business automation pilots. It is not a promise of income, lead generation, compliance, or production safety.",
        "",
        "## Required Boundaries",
        "",
        "- Use sample or approved exported data first.",
        "- Keep human approval before external messages, payments, account changes, or customer-impacting actions.",
        "- Do not store secrets in generated files.",
        "- Do not copy third-party OSS code into client systems without license review.",
        "- Do not automate regulated decisions without qualified review.",
        "- Document who owns monitoring and maintenance after handoff.",
        "",
        "## Human Approval",
        "",
        "Every first pilot should preserve human approval before production use. Approval should be visible in the workflow, not implied by a chat message.",
        "",
    ]
    return "\n".join(lines)
