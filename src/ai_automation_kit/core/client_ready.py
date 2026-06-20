from __future__ import annotations

import csv
import io
import json
from pathlib import Path


ARTIFACTS = [
    "README.md",
    "client_intake.md",
    "client_intake.json",
    "roi_calculator.csv",
    "pricing_recommendation.md",
    "proposal_tiers.md",
    "implementation_readiness_score.json",
    "implementation_readiness_score.md",
    "security_review.md",
    "prompt_injection_checklist.md",
    "approval_map.md",
    "data_classification.md",
    "tool_stack_recommendation.md",
    "maintenance_plan.md",
    "retainer_offer.md",
    "monthly_review.md",
    "case_study_template.md",
    "before_after_report.md",
    "marketplace_profile.md",
    "outreach_sequence.md",
    "handoff_training.md",
    "tool_comparison.md",
    "template_adaptation_guide.md",
    "compliance_boundaries.md",
    "niche_playbook.md",
    "connector_blueprints.md",
    "demo_inputs.csv",
    "client_ready.json",
]


def generate_client_ready_pack(
    source_output: Path,
    output: Path,
    business_area: str,
    client_type: str,
    niche: str,
) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    source_summary = _load_source_summary(source_output)
    source_status = "ready" if source_output.exists() else "missing"
    score = _score_pack(source_status, source_summary)
    payload = {
        "business_area": business_area,
        "client_type": client_type,
        "niche": niche,
        "source_output": str(source_output),
        "source_status": source_status,
        "source_summary": source_summary,
        "score": score,
        "artifacts": ARTIFACTS,
        "positioning": _positioning(business_area, client_type, niche),
    }
    renderers = {
        "README.md": _render_readme,
        "client_intake.md": _render_client_intake,
        "pricing_recommendation.md": _render_pricing_recommendation,
        "proposal_tiers.md": _render_proposal_tiers,
        "implementation_readiness_score.md": _render_readiness_score,
        "security_review.md": _render_security_review,
        "prompt_injection_checklist.md": _render_prompt_injection_checklist,
        "approval_map.md": _render_approval_map,
        "data_classification.md": _render_data_classification,
        "tool_stack_recommendation.md": _render_tool_stack_recommendation,
        "maintenance_plan.md": _render_maintenance_plan,
        "retainer_offer.md": _render_retainer_offer,
        "monthly_review.md": _render_monthly_review,
        "case_study_template.md": _render_case_study_template,
        "before_after_report.md": _render_before_after_report,
        "marketplace_profile.md": _render_marketplace_profile,
        "outreach_sequence.md": _render_outreach_sequence,
        "handoff_training.md": _render_handoff_training,
        "tool_comparison.md": _render_tool_comparison,
        "template_adaptation_guide.md": _render_template_adaptation_guide,
        "compliance_boundaries.md": _render_compliance_boundaries,
        "niche_playbook.md": _render_niche_playbook,
        "connector_blueprints.md": _render_connector_blueprints,
    }
    for filename, renderer in renderers.items():
        (output / filename).write_text(renderer(payload), encoding="utf-8")
    (output / "client_intake.json").write_text(json.dumps(_client_intake_payload(payload), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "implementation_readiness_score.json").write_text(json.dumps(score, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "roi_calculator.csv").write_text(_render_roi_calculator(payload), encoding="utf-8")
    (output / "demo_inputs.csv").write_text(_render_demo_inputs(payload), encoding="utf-8")
    (output / "client_ready.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def _load_source_summary(source_output: Path) -> dict:
    if not source_output.exists():
        return {
            "executive_recommendation": "Run `onboard --create-offer-pack` before final client delivery.",
            "recommended_projects": [],
        }
    for name in ["business_automation_summary.json", "onboarding_summary.json", "offer_pack.json", "run_summary.json"]:
        path = source_output / name
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return data
            except json.JSONDecodeError:
                continue
    return {
        "executive_recommendation": "Source output exists, but no structured summary was found.",
        "recommended_projects": [],
    }


def _score_pack(source_status: str, summary: dict) -> dict:
    categories = {
        "client_intake": 10,
        "roi_pricing": 10,
        "proposal_scope": 10,
        "implementation_readiness": 10,
        "security_data": 10,
        "tool_selection": 10,
        "maintenance_retainer": 10,
        "marketplace_outreach": 10,
        "case_study_reporting": 10,
        "source_grounding": 10 if source_status == "ready" else 5,
    }
    total = sum(categories.values())
    if summary.get("recommended_projects"):
        total = min(100, total + 2)
    return {
        "total": total,
        "label": "client_ready" if total >= 85 else "starter_ready",
        "categories": categories,
        "notes": [
            "No income is guaranteed.",
            "Score measures delivery preparedness, not sales certainty.",
            "Use real client data only after approval and data classification.",
        ],
    }


def _positioning(business_area: str, client_type: str, niche: str) -> str:
    return (
        f"A scoped {business_area} automation offer for {client_type} clients in the {niche} niche, "
        "packaged for diagnosis, proposal, safe pilot delivery, and monthly maintenance."
    )


def _recommendation(payload: dict) -> str:
    summary = payload["source_summary"]
    return summary.get("executive_recommendation") or "Start with one measurable workflow and a dry-run pilot."


def _project_lines(payload: dict) -> list[str]:
    projects = payload["source_summary"].get("recommended_projects") or []
    if not projects:
        return ["- No specific OSS candidate is locked yet. Use the tool-stack recommendation and client intake to choose safely."]
    lines = []
    for project in projects[:5]:
        name = project.get("full_name", "unnamed project")
        url = project.get("url", "")
        score = project.get("score")
        suffix = f" score {score}" if score is not None else ""
        lines.append(f"- {name}{suffix}: {url or 'review source output for URL'}")
    return lines


def _render_readme(payload: dict) -> str:
    source_hint = ""
    if payload["source_status"] == "missing":
        source_hint = "\nRun `onboard --create-offer-pack` before final client delivery.\n"
    lines = [
        f"# Client-Ready Automation Pack: {payload['niche']} {payload['business_area']}",
        "",
        payload["positioning"],
        "",
        "No income is guaranteed. This pack helps you diagnose, sell, deliver, and maintain a bounded automation pilot responsibly.",
        source_hint.strip(),
        "## Score",
        "",
        f"- Total: `{payload['score']['total']}/100`",
        f"- Label: `{payload['score']['label']}`",
        "",
        "## Read First",
        "",
        "1. `client_intake.md`",
        "2. `roi_calculator.csv`",
        "3. `proposal_tiers.md`",
        "4. `implementation_readiness_score.md`",
        "5. `security_review.md`",
        "6. `maintenance_plan.md`",
        "7. `marketplace_profile.md`",
        "",
        "## Source Recommendation",
        "",
        _recommendation(payload),
        "",
    ]
    return "\n".join(line for line in lines if line is not None) + "\n"


def _client_intake_payload(payload: dict) -> dict:
    area = payload["business_area"]
    niche = payload["niche"]
    return {
        "business_area": area,
        "niche": niche,
        "questions": [
            f"Which {area} workflow in your {niche} operation repeats every week?",
            "How many people touch it today?",
            "How many times per month does it happen?",
            "What tool starts the workflow?",
            "What tool receives the final output?",
            "Where is human approval required?",
            "Which data fields are sensitive?",
            "What would make the first pilot obviously successful?",
        ],
        "required_baselines": ["hours_per_month", "error_rate", "handoffs", "tool_cost", "response_time"],
    }


def _render_client_intake(payload: dict) -> str:
    intake = _client_intake_payload(payload)
    lines = [
        f"# Client Intake: {payload['niche']} {payload['business_area']} Automation",
        "",
        "Use this before quoting implementation work.",
        "",
        "## Questions",
        "",
    ]
    lines.extend(f"- {question}" for question in intake["questions"])
    lines.extend(["", "## Baselines To Collect", ""])
    lines.extend(f"- `{field}`" for field in intake["required_baselines"])
    lines.append("")
    return "\n".join(lines)


def _render_roi_calculator(payload: dict) -> str:
    rows = [
        ["field", "example_value", "notes"],
        ["manual_hours_per_month", "20", "Ask the client for the current baseline."],
        ["loaded_hourly_cost", "40", "Use local labor cost or internal estimate."],
        ["monthly_tool_cost", "50", "Include n8n/Make/Zapier/API hosting where relevant."],
        ["expected_hours_saved_percent", "40", "Keep the first pilot conservative."],
        ["estimated_monthly_savings", "=manual_hours_per_month*loaded_hourly_cost*expected_hours_saved_percent/100-monthly_tool_cost", "Spreadsheet formula placeholder."],
        ["recommended_pilot_fee_floor", "=estimated_monthly_savings*1.5", "Use with judgment; not a guarantee."],
        ["recommended_monthly_retainer_floor", "=estimated_monthly_savings*0.15", "Retainer must include monitoring scope."],
    ]
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerows(rows)
    return buffer.getvalue()


def _render_pricing_recommendation(payload: dict) -> str:
    return "\n".join(
        [
            "# Pricing Recommendation",
            "",
            "No income is guaranteed. Price only after intake, data review, and risk classification.",
            "",
            "## Suggested Shapes",
            "",
            "- Discovery audit: fixed fee for workflow map, ROI estimate, and pilot scope.",
            "- Dry-run prototype: fixed project fee for one narrow workflow using sample or approved exported data.",
            "- Production handoff: separate fee after dry-run approval.",
            "- Monthly maintenance: retainer for monitoring, fixes, API drift, and improvement review.",
            "",
            "## Quote Guardrails",
            "",
            "- Do not quote production integration before credentials, data shape, and approval owners are known.",
            "- Keep the first pilot small enough to demo in days.",
            "- Separate implementation from monitoring.",
            "",
        ]
    )


def _render_proposal_tiers(payload: dict) -> str:
    area = payload["business_area"]
    return "\n".join(
        [
            f"# Proposal Tiers: {area.title()} Automation",
            "",
            "| Tier | Best For | Deliverables | Risk |",
            "|---|---|---|---|",
            "| Starter Audit | Client is unsure what to automate | intake, workflow map, ROI estimate, pilot recommendation | low |",
            "| Dry-Run Pilot | Client has one clear repeated workflow | sample-data prototype, scorecard, approval map, handoff notes | medium |",
            "| Production Handoff | Dry-run has been approved | deployment runbook, monitoring plan, rollback plan, training | higher |",
            "| Monthly Improvement | Client wants ongoing reliability | monthly review, incident log, small improvements, KPI report | controlled recurring |",
            "",
        ]
    )


def _render_readiness_score(payload: dict) -> str:
    lines = ["# Implementation Readiness Score", "", f"Total: `{payload['score']['total']}/100`", ""]
    for key, value in payload["score"]["categories"].items():
        lines.append(f"- {key.replace('_', ' ').title()}: `{value}`")
    lines.extend(["", "## Notes", ""])
    lines.extend(f"- {note}" for note in payload["score"]["notes"])
    lines.append("")
    return "\n".join(lines)


def _render_security_review(payload: dict) -> str:
    return "\n".join(
        [
            "# Security Review",
            "",
            "- [ ] Secrets are not stored in generated files.",
            "- [ ] Client data is classified before use.",
            "- [ ] Public webhooks require authentication or allowlist controls.",
            "- [ ] Workflow editors are limited to trusted users.",
            "- [ ] AI outputs cannot trigger external actions without human approval.",
            "- [ ] OSS license review is complete before copying or deploying code.",
            "- [ ] Logs avoid sensitive customer data.",
            "- [ ] Rollback and stop conditions are written down.",
            "",
        ]
    )


def _render_prompt_injection_checklist(payload: dict) -> str:
    return "\n".join(
        [
            "# Prompt Injection Checklist",
            "",
            "- [ ] Treat external text as untrusted input.",
            "- [ ] Do not place untrusted customer text inside system instructions.",
            "- [ ] Keep tool permissions narrow.",
            "- [ ] Require human approval before sending messages, changing records, payments, or account actions.",
            "- [ ] Log model decisions and tool calls for review.",
            "- [ ] Test malicious examples before production.",
            "",
        ]
    )


def _render_approval_map(payload: dict) -> str:
    return "\n".join(
        [
            "# Approval Map",
            "",
            "Every first pilot must preserve human approval before production-impacting actions.",
            "",
            "| Step | Automation Role | Human Approval | Evidence |",
            "|---|---|---|---|",
            "| Intake | collect workflow facts | client confirms scope | signed scope note |",
            "| Dry-run | process sample data | operator reviews output | run log and scorecard |",
            "| External action | draft message or update | owner approves before send/update | approval record |",
            "| Production | scheduled execution | named owner monitors | monthly review |",
            "",
        ]
    )


def _render_data_classification(payload: dict) -> str:
    return "\n".join(
        [
            "# Data Classification",
            "",
            "| Class | Examples | Allowed In First Pilot | Handling |",
            "|---|---|---|---|",
            "| Public | website URLs, public docs | yes | cite sources |",
            "| Internal | SOPs, non-sensitive workflow notes | yes with approval | store locally or approved client system |",
            "| Confidential | customer records, invoices, contracts | only if exported and approved | minimize, mask, log access |",
            "| Restricted | credentials, payment data, regulated records | no by default | require formal review |",
            "",
        ]
    )


def _render_tool_stack_recommendation(payload: dict) -> str:
    lines = [
        "# Tool Stack Recommendation",
        "",
        "Choose the smallest stack that can be maintained by the client or retainer owner.",
        "",
        "## Source Candidates",
        "",
    ]
    lines.extend(_project_lines(payload))
    lines.extend(
        [
            "",
            "## Decision Guide",
            "",
            "- Use Zapier or Make when the client needs familiar SaaS automation and low infrastructure burden.",
            "- Use n8n when the workflow needs self-hosting, code, many integrations, or lower task-volume cost.",
            "- Use Python when logic, data cleanup, or custom APIs are the real value.",
            "- Use Windmill when scripts must become webhooks, workflows, or internal UIs.",
            "- Use Appsmith or Budibase when the automation needs a client-facing internal app or dashboard.",
            "- Use Dify or Flowise when the core deliverable is an AI agent workflow with model/provider abstraction.",
            "",
        ]
    )
    return "\n".join(lines)


def _render_maintenance_plan(payload: dict) -> str:
    return "\n".join(
        [
            "# Maintenance Plan",
            "",
            "Recurring revenue should be tied to concrete reliability work, not vague support.",
            "",
            "## Monthly Tasks",
            "",
            "- Review failed runs and edge cases.",
            "- Check API credentials and rate limits.",
            "- Update workflow documentation.",
            "- Compare KPI movement against `roi_calculator.csv`.",
            "- Propose one small improvement or stop the automation if value is not proven.",
            "",
            "## Incident Response",
            "",
            "- Stop workflow.",
            "- Notify owner.",
            "- Preserve logs.",
            "- Re-run on sample data.",
            "- Document root cause and prevention.",
            "",
        ]
    )


def _render_retainer_offer(payload: dict) -> str:
    return "\n".join(
        [
            "# Retainer Offer",
            "",
            "| Plan | Includes | Excludes |",
            "|---|---|---|",
            "| Monitor | monthly run review, basic fixes, KPI note | new integrations |",
            "| Improve | monitor plan plus one small monthly improvement | large rebuilds |",
            "| Operator | monitor, improvements, client training, quarterly roadmap | regulated decisions without review |",
            "",
        ]
    )


def _render_monthly_review(payload: dict) -> str:
    return "\n".join(
        [
            "# Monthly Review",
            "",
            "- Reporting month:",
            "- Workflow owner:",
            "- Runs completed:",
            "- Failed runs:",
            "- Estimated hours saved:",
            "- Issues found:",
            "- Changes made:",
            "- Recommended next improvement:",
            "- Continue / revise / stop decision:",
            "",
        ]
    )


def _render_case_study_template(payload: dict) -> str:
    return "\n".join(
        [
            "# Case Study Template",
            "",
            "## Client Context",
            "",
            f"- Niche: `{payload['niche']}`",
            f"- Business area: `{payload['business_area']}`",
            "",
            "## Before",
            "",
            "- Manual workflow:",
            "- Monthly volume:",
            "- Pain:",
            "",
            "## After",
            "",
            "- Automated step:",
            "- Human approval point:",
            "- Measured result:",
            "",
            "## Evidence",
            "",
            "- Run log:",
            "- Scorecard:",
            "- Client quote:",
            "",
        ]
    )


def _render_before_after_report(payload: dict) -> str:
    return "\n".join(
        [
            "# Before / After Report",
            "",
            "| Metric | Before | After Pilot | Evidence |",
            "|---|---:|---:|---|",
            "| Monthly manual hours |  |  | timesheet or estimate |",
            "| Average response time |  |  | ticket/report export |",
            "| Error rate |  |  | sample QA |",
            "| Handoffs |  |  | workflow map |",
            "| Tool cost |  |  | invoice or estimate |",
            "",
        ]
    )


def _render_marketplace_profile(payload: dict) -> str:
    niche = payload["niche"]
    area = payload["business_area"]
    return "\n".join(
        [
            "# Marketplace Profile",
            "",
            f"I help {niche} teams automate repeated {area} workflows with a safe, measurable pilot: intake, ROI estimate, dry-run prototype, approval map, and monthly maintenance plan.",
            "",
            "## Services",
            "",
            "- Workflow automation audit",
            "- Dry-run automation prototype",
            "- n8n / Make / Zapier / Python tool-stack selection",
            "- AI workflow safety review",
            "- Monthly automation maintenance",
            "",
        ]
    )


def _render_outreach_sequence(payload: dict) -> str:
    return "\n".join(
        [
            "# Outreach Sequence",
            "",
            "## Message 1",
            "",
            f"I am mapping repeated {payload['business_area']} workflows for {payload['niche']} teams and turning one of them into a small dry-run automation pilot. Is there one workflow your team repeats every week?",
            "",
            "## Message 2",
            "",
            "The first step is not a big implementation. It is a short workflow audit, ROI estimate, and a safe sample-data demo.",
            "",
            "## Message 3",
            "",
            "If it helps, I can send a one-page pilot scope showing the workflow, approval point, expected savings, and monthly maintenance option.",
            "",
        ]
    )


def _render_handoff_training(payload: dict) -> str:
    return "\n".join(
        [
            "# Handoff Training",
            "",
            "- Explain what the automation does.",
            "- Explain what it does not do.",
            "- Show how to run a dry-run.",
            "- Show where approvals happen.",
            "- Show how to stop the workflow.",
            "- Show how to report a failure.",
            "- Review monthly maintenance expectations.",
            "",
        ]
    )


def _render_tool_comparison(payload: dict) -> str:
    return "\n".join(
        [
            "# Tool Comparison",
            "",
            "| Tool | Best Fit | Watch Out |",
            "|---|---|---|",
            "| Zapier | simple SaaS automations | task cost and limited custom logic |",
            "| Make | visual multi-step SaaS flows | scenario complexity and task usage |",
            "| n8n | self-hosted, code-friendly, AI workflows | security, hosting, maintenance |",
            "| Python | custom logic and data cleanup | requires developer ownership |",
            "| Windmill | scripts as workflows/UIs | needs technical setup |",
            "| Appsmith/Budibase | internal apps and dashboards | app design and permissions |",
            "",
        ]
    )


def _render_template_adaptation_guide(payload: dict) -> str:
    return "\n".join(
        [
            "# Template Adaptation Guide",
            "",
            "- Treat public templates as references, not client-ready systems.",
            "- Review license before reuse.",
            "- Replace credentials with client-owned secrets.",
            "- Remove unused nodes and actions.",
            "- Add human approval before external actions.",
            "- Test on demo data first.",
            "- Document every changed assumption.",
            "",
        ]
    )


def _render_compliance_boundaries(payload: dict) -> str:
    return "\n".join(
        [
            "# Compliance Boundaries",
            "",
            "This pack is not legal, tax, medical, HR, or financial advice.",
            "",
            "- Regulated decisions require qualified review.",
            "- Customer data requires client-approved handling.",
            "- Payment, health, employment, and legal workflows need extra controls.",
            "- The first pilot should avoid restricted data unless the client has approved a formal process.",
            "",
        ]
    )


def _render_niche_playbook(payload: dict) -> str:
    niche = payload["niche"]
    area = payload["business_area"]
    return "\n".join(
        [
            f"# Niche Playbook: {niche} {area} Automation",
            "",
            "## Likely Pain Points",
            "",
            "- Repeated manual data entry.",
            "- Slow follow-up.",
            "- Inconsistent status tracking.",
            "- Spreadsheet drift.",
            "- Missing handoff evidence.",
            "",
            "## First Pilot Ideas",
            "",
            f"- Intake-to-follow-up automation for {niche}.",
            f"- Weekly {area} status report.",
            "- Document collection reminder workflow.",
            "- CRM or spreadsheet cleanup assistant.",
            "",
            "## Avoid First",
            "",
            "- Regulated decisions.",
            "- Payment movement.",
            "- Fully autonomous customer-impacting actions.",
            "",
        ]
    )


def _render_connector_blueprints(payload: dict) -> str:
    return "\n".join(
        [
            "# Connector Blueprints",
            "",
            "| Connector | Use | First Safe Test |",
            "|---|---|---|",
            "| Google Sheets | lightweight CRM, scorecard, intake tracking | read sample sheet |",
            "| Gmail / Outlook | draft replies and routing | create drafts only |",
            "| Slack / Teams | internal notifications | post to test channel |",
            "| Notion / Airtable | knowledge base and workflow tracking | create test record |",
            "| HubSpot / CRM | lead and customer updates | read-only export first |",
            "| Webhooks | connect forms and apps | signed test endpoint |",
            "| n8n / Make / Zapier | orchestration | dry-run scenario |",
            "",
        ]
    )


def _render_demo_inputs(payload: dict) -> str:
    rows = [
        ["record_id", "customer_name", "request_type", "status", "sensitive_data_removed"],
        ["demo-001", "Example Client", payload["business_area"], "new", "yes"],
        ["demo-002", "Sample Company", "follow_up", "waiting", "yes"],
    ]
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerows(rows)
    return buffer.getvalue()
