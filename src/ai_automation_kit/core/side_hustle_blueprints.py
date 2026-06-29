from __future__ import annotations

import csv
import html
import json
from io import StringIO
from pathlib import Path


BLUEPRINTS: list[dict[str, object]] = [
    {
        "name": "Website + Inquiry Operations",
        "buyer": "hotels, clinics, salons, restaurants, local services",
        "pain": "The website exists, but inquiries are scattered and follow-up is inconsistent.",
        "inputs": "business facts, photos, contact destination, inquiry fields, approval owner",
        "deliverables": "homepage structure, inquiry form plan, response templates, handoff note, acceptance checklist",
        "tools": "website-side-hustle, Google Forms, Google Sheets, static HTML, optional Tally or Netlify Forms",
        "price": "300-1500 USD setup, optional 100-500 USD monthly maintenance",
        "human_approval": "launch, public claims, prices, booking confirmation, privacy text",
        "first_offer": "I will turn your homepage into a clearer inquiry path and give your team a simple daily inquiry workflow.",
    },
    {
        "name": "AI Reception And First Reply",
        "buyer": "clinics, hotels, schools, agencies, local service teams",
        "pain": "New inquiries wait too long before someone sorts them.",
        "inputs": "FAQ, service menu, business hours, contact rules, escalation owner, sample inquiries",
        "deliverables": "intake form, classification rules, draft replies, approval queue, daily runbook",
        "tools": "flows install ai-reception-line-inquiry, Gmail, LINE, Google Sheets, Slack",
        "price": "500-2500 USD setup, optional 200-800 USD monthly operation support",
        "human_approval": "final replies, appointment confirmation, complaints, refunds, legal or medical advice",
        "first_offer": "I will create a safe first-response system that drafts replies and shows staff what needs approval.",
    },
    {
        "name": "Invoice And Document Follow-Up",
        "buyer": "accounting offices, construction firms, agencies, back-office teams",
        "pain": "Documents arrive by email but missing items are chased manually.",
        "inputs": "sample emails, document checklist, due dates, client list, approved follow-up wording",
        "deliverables": "document tracker, missing-item checklist, follow-up drafts, approval queue, status report",
        "tools": "complete-workspace invoice-document-followup, Gmail, Google Sheets, local folders",
        "price": "700-3000 USD setup, optional 300-1000 USD monthly support",
        "human_approval": "external sends, deadline exceptions, invoice/payment claims, private document handling",
        "first_offer": "I will reduce missing-document follow-up work by creating a tracker and draft reminder workflow.",
    },
    {
        "name": "Internal FAQ Assistant",
        "buyer": "small companies, schools, clinics, agencies, field teams",
        "pain": "Staff ask the same questions and knowledge is hidden in PDFs or chat.",
        "inputs": "approved documents, policies, FAQ, escalation contacts, update owner",
        "deliverables": "document index, answer draft process, source citation rule, update checklist",
        "tools": "docs-rag, local folder, Notion, Google Drive export",
        "price": "500-2500 USD setup, optional 150-700 USD monthly content update",
        "human_approval": "policy interpretation, HR/legal/medical/financial answers, source changes",
        "first_offer": "I will organize your approved documents into a searchable internal FAQ with source-backed draft answers.",
    },
    {
        "name": "Sales Research Brief",
        "buyer": "B2B sales teams, consultants, agencies, local service providers",
        "pain": "Prospect research is slow and inconsistent before outreach.",
        "inputs": "target industry, region, ideal customer profile, disallowed sources, outreach angle",
        "deliverables": "prospect brief, qualification checklist, personalization notes, outreach draft",
        "tools": "github-discover, research-agent, browser research, spreadsheet",
        "price": "300-1500 USD per list, optional monthly research retainer",
        "human_approval": "final outreach, claims, pricing, contact compliance, do-not-contact rules",
        "first_offer": "I will create researched prospect briefs so your outreach starts with real context instead of generic messages.",
    },
    {
        "name": "Review And Reputation Response Desk",
        "buyer": "restaurants, hotels, clinics, salons, local services",
        "pain": "Reviews are not answered quickly or consistently.",
        "inputs": "brand tone, review policy, escalation rules, sample good and bad reviews",
        "deliverables": "review categories, response templates, escalation list, weekly improvement report",
        "tools": "spreadsheet, Gmail, Google Business Profile export, optional manual copy workflow",
        "price": "300-1200 USD setup, optional 200-900 USD monthly monitoring",
        "human_approval": "public replies, complaints, refunds, legal claims, private customer details",
        "first_offer": "I will build a review response workflow that drafts consistent replies and flags risky cases for staff.",
    },
    {
        "name": "Appointment Reminder And No-Show Reducer",
        "buyer": "clinics, salons, repair shops, schools, lesson businesses",
        "pain": "Appointments are missed because reminders are manual or inconsistent.",
        "inputs": "appointment export, reminder timing, cancellation rules, approved message templates",
        "deliverables": "reminder schedule, message drafts, cancellation handling, no-show scorecard",
        "tools": "Google Sheets, calendar export, email or SMS draft workflow",
        "price": "500-2000 USD setup, optional 150-600 USD monthly support",
        "human_approval": "production sends, medical or legal wording, cancellation fees, account settings",
        "first_offer": "I will set up a reminder workflow that helps staff review and send appointment reminders safely.",
    },
    {
        "name": "Lead Routing And Follow-Up",
        "buyer": "real estate, agencies, B2B services, repair businesses",
        "pain": "Leads come from forms, email, and chat but owners are unclear.",
        "inputs": "lead sources, assignment rules, SLA, owners, status definitions",
        "deliverables": "lead table, routing rules, first reply drafts, SLA report, dashboard",
        "tools": "Google Sheets, forms, Slack, Gmail, flows catalog",
        "price": "700-3500 USD setup, optional 300-1200 USD monthly ops",
        "human_approval": "quotes, contracts, final sales emails, CRM production changes",
        "first_offer": "I will make sure every inbound lead gets an owner, status, and next action before it goes cold.",
    },
    {
        "name": "Report-To-Dashboard Pack",
        "buyer": "owners, store managers, agencies, finance teams",
        "pain": "Weekly numbers are copied manually into reports.",
        "inputs": "CSV exports, KPI definitions, reporting cadence, decision owner",
        "deliverables": "KPI table, HTML dashboard, weekly summary draft, anomaly checklist",
        "tools": "Excel/CSV, Google Sheets, static HTML, local Python",
        "price": "500-2500 USD setup, optional 200-800 USD monthly reporting",
        "human_approval": "financial interpretation, investor/client sends, KPI definition changes",
        "first_offer": "I will turn your repeated spreadsheet report into a simple dashboard and weekly review routine.",
    },
    {
        "name": "Document Intake And Filing Desk",
        "buyer": "law offices, accounting offices, clinics, real estate, construction",
        "pain": "Files arrive with unclear names, missing metadata, and no status.",
        "inputs": "folder structure, document types, naming rules, required fields, privacy boundary",
        "deliverables": "intake checklist, rename plan, missing metadata queue, filing runbook",
        "tools": "document-intake, local folders, Google Drive, spreadsheet",
        "price": "700-3000 USD setup, optional 300-1000 USD monthly support",
        "human_approval": "deleting files, legal interpretation, sensitive data sharing, final filing policy",
        "first_offer": "I will create a safer document intake workflow so files are named, checked, and routed consistently.",
    },
    {
        "name": "Inventory And Reorder Alert",
        "buyer": "restaurants, retail shops, clinics, salons, workshops",
        "pain": "Stock problems are noticed too late.",
        "inputs": "item list, reorder threshold, supplier contact, review cadence, sample stock count",
        "deliverables": "stock sheet, reorder alerts, supplier draft messages, weekly review checklist",
        "tools": "Google Sheets, email drafts, local scripts",
        "price": "400-1800 USD setup, optional 150-600 USD monthly support",
        "human_approval": "purchases, supplier sends, price changes, inventory write-offs",
        "first_offer": "I will create a simple stock alert workflow so staff know what needs review before it runs out.",
    },
    {
        "name": "Client Onboarding Portal Lite",
        "buyer": "consultants, agencies, coaches, studios, B2B services",
        "pain": "New clients do not know what to send, and projects start messy.",
        "inputs": "service steps, required documents, welcome message, milestone owners, FAQ",
        "deliverables": "onboarding checklist, intake form, welcome email drafts, milestone tracker",
        "tools": "Google Forms, Notion, Google Sheets, static handoff page",
        "price": "500-2500 USD setup, optional 200-700 USD monthly improvement",
        "human_approval": "contract terms, payment requests, scope changes, client promises",
        "first_offer": "I will turn your client onboarding into a simple checklist and intake workflow that reduces back-and-forth.",
    },
]


def generate_side_hustle_blueprints(
    industry: str,
    operator_level: str,
    output: Path,
) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    filtered = _filter_blueprints(industry)
    payload = {
        "status": "ready",
        "industry": industry,
        "operator_level": operator_level,
        "count": len(filtered),
        "blueprints": filtered,
        "source_patterns": [
            "workflow automation platforms such as n8n, Activepieces, and Windmill",
            "AI app and agent builders such as Dify, Flowise, LangGraph, and CrewAI",
            "browser and task automation projects such as browser-use and Skyvern",
            "local-first approval and dry-run patterns used by this starter kit",
        ],
    }
    (output / "side_hustle_blueprints.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "START_HERE_SIDE_HUSTLE_BLUEPRINTS.md").write_text(_render_start(payload), encoding="utf-8")
    (output / "side_hustle_blueprints.md").write_text(_render_catalog_md(payload), encoding="utf-8")
    (output / "side_hustle_blueprints.csv").write_text(_render_catalog_csv(filtered), encoding="utf-8")
    (output / "first_client_picker.md").write_text(_render_first_client_picker(payload), encoding="utf-8")
    (output / "offer_scripts.md").write_text(_render_offer_scripts(payload), encoding="utf-8")
    (output / "implementation_paths.md").write_text(_render_implementation_paths(payload), encoding="utf-8")
    (output / "risk_boundaries.md").write_text(_render_risk_boundaries(payload), encoding="utf-8")
    (output / "client_intake_questions.md").write_text(_render_client_intake_questions(payload), encoding="utf-8")
    (output / "ai_agent_handoff.md").write_text(_render_ai_agent_handoff(payload), encoding="utf-8")
    (output / "side_hustle_blueprints.html").write_text(_render_catalog_html(payload), encoding="utf-8")
    return payload


def _filter_blueprints(industry: str) -> list[dict[str, object]]:
    normalized = (industry or "").strip().lower()
    if not normalized or normalized in {"all", "local-business", "small-business"}:
        return BLUEPRINTS
    selected = [
        blueprint
        for blueprint in BLUEPRINTS
        if normalized in str(blueprint["buyer"]).lower()
        or normalized in str(blueprint["name"]).lower()
        or normalized in str(blueprint["pain"]).lower()
    ]
    return selected or BLUEPRINTS


def _render_start(payload: dict) -> str:
    return "\n".join(
        [
            "# Start Here: Side Hustle Blueprints",
            "",
            "This pack helps a beginner choose a sellable automation offer before writing code or promising a custom system.",
            "",
            "## Recommended Order",
            "",
            "1. Read `side_hustle_blueprints.md` and pick three offers you understand.",
            "2. Use `first_client_picker.md` to choose the easiest first client.",
            "3. Use `client_intake_questions.md` to collect facts, sample data, tools, and approval owners.",
            "4. Use `implementation_paths.md` to choose local dry-run, spreadsheet-first, cloud-assisted, or workflow-platform delivery.",
            "5. Use `offer_scripts.md` for the first outreach or discovery call.",
            "6. Use `risk_boundaries.md` before sending any proposal.",
            "7. Give `ai_agent_handoff.md` to Codex, Claude Code, Cursor, ChatGPT, Claude, or another AI agent.",
            "",
            "The goal is not to promise full automation. The goal is to sell a bounded proof of value with human approval.",
            "",
        ]
    )


def _render_catalog_md(payload: dict) -> str:
    lines = [
        "# Side Hustle Automation Blueprints",
        "",
        "Each blueprint is designed as a small paid proof-of-value offer, not a risky full automation promise.",
        "",
        "| Offer | Buyer | Pain | Inputs | Deliverables | Tools | Price | Human approval |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for item in payload["blueprints"]:
        lines.append(
            "| {name} | {buyer} | {pain} | {inputs} | {deliverables} | {tools} | {price} | {human_approval} |".format(
                **{key: str(value).replace("|", "/") for key, value in item.items()}
            )
        )
    lines.extend(
        [
            "",
            "## Pattern Sources",
            "",
            "This catalog is inspired by public workflow automation, AI app builder, agent, browser automation, and local dry-run patterns. Treat public projects as design references and integration targets, not as permission to copy private data, brands, or proprietary workflows.",
            "",
        ]
    )
    for pattern in payload["source_patterns"]:
        lines.append(f"- {pattern}")
    lines.append("")
    return "\n".join(lines)


def _render_catalog_csv(blueprints: list[dict[str, object]]) -> str:
    output = StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["name", "buyer", "pain", "inputs", "deliverables", "tools", "price", "human_approval", "first_offer"],
    )
    writer.writeheader()
    for blueprint in blueprints:
        writer.writerow({key: blueprint[key] for key in writer.fieldnames})
    return output.getvalue()


def _render_first_client_picker(payload: dict) -> str:
    lines = [
        "# First Client Picker",
        "",
        "Choose the first paid offer by scoring each candidate from 1 to 5.",
        "",
        "| Question | Score |",
        "|---|---|",
        "| Do I understand the business process without specialist knowledge? |  |",
        "| Can the first version run with sample data or a dry-run? |  |",
        "| Can a human approve every external send or customer-facing action? |  |",
        "| Can I explain the outcome in one sentence? |  |",
        "| Can I deliver something useful in 3 to 7 days? |  |",
        "| Does the client already feel the pain weekly? |  |",
        "| Can success be measured with time saved, faster reply, fewer misses, or clearer status? |  |",
        "",
        "Start with the highest score. If two offers tie, choose the one with the least sensitive data.",
        "",
        "## Good First Picks",
        "",
    ]
    for item in payload["blueprints"][:5]:
        lines.append(f"- {item['name']}: {item['first_offer']}")
    lines.append("")
    return "\n".join(lines)


def _render_offer_scripts(payload: dict) -> str:
    lines = [
        "# Offer Scripts",
        "",
        "Use these as starting points. Keep the promise narrow and concrete.",
        "",
    ]
    for item in payload["blueprints"]:
        lines.extend(
            [
                f"## {item['name']}",
                "",
                f"Short pitch: {item['first_offer']}",
                "",
                "Discovery question:",
                f"- Where does this work happen today, and what gets missed when the team is busy?",
                "",
                "Proof-of-value promise:",
                f"- I will create a small reviewed workflow using your approved sample data so you can see whether it saves time before any production automation.",
                "",
            ]
        )
    return "\n".join(lines)


def _render_implementation_paths(payload: dict) -> str:
    return "\n".join(
        [
            "# Implementation Paths",
            "",
            "Choose the smallest path that proves value.",
            "",
            "## 1. Local Dry-Run",
            "",
            "Use local folders, sample CSV files, generated scripts, and approval queues. Best for sensitive data, first clients, and beginners.",
            "",
            "## 2. Spreadsheet-First",
            "",
            "Use Google Sheets, Airtable, or Notion as the operating table. Best when staff need to see and correct every row.",
            "",
            "## 3. Website Or Form Front Door",
            "",
            "Use a website, Google Form, Tally, Typeform, or Netlify Form to collect clean inputs. Best for inquiry, booking, onboarding, and document intake.",
            "",
            "## 4. Workflow Platform Bridge",
            "",
            "Use n8n, Activepieces, Windmill, or similar tools only after the manual workflow and approval points are clear.",
            "",
            "## 5. AI App Or Agent Layer",
            "",
            "Use Dify, Flowise, LangGraph, CrewAI, or a coding agent for classification, drafting, summarizing, and routing. Keep final sends behind human approval.",
            "",
            "## 6. Cloud-Assisted Production",
            "",
            "Move to Render, Railway, Cloud Run, AWS, Azure, or another cloud only after local dry-run, secret handling, logs, rollback, and cost owner are clear.",
            "",
        ]
    )


def _render_risk_boundaries(payload: dict) -> str:
    return "\n".join(
        [
            "# Risk Boundaries",
            "",
            "Do not promise guaranteed revenue, guaranteed rankings, guaranteed bookings, or fully hands-free operation.",
            "",
            "Keep human approval for:",
            "",
            "- external email, SMS, LINE, CRM, or social posting",
            "- booking confirmation",
            "- price changes, refunds, discounts, and contract terms",
            "- legal, medical, financial, HR, or safety advice",
            "- deletion of files or records",
            "- production credentials, webhooks, cloud billing, and domain changes",
            "- public claims, testimonials, before/after claims, and regulated wording",
            "",
            "Beginner rule: automation may sort, draft, summarize, and prepare. A responsible human approves commitments.",
            "",
        ]
    )


def _render_client_intake_questions(payload: dict) -> str:
    return "\n".join(
        [
            "# Client Intake Questions",
            "",
            "Ask these before choosing a blueprint.",
            "",
            "1. What repetitive work takes time every week?",
            "2. Where does the work start: email, form, chat, phone note, folder, spreadsheet, website, or system export?",
            "3. What is the current step-by-step process?",
            "4. What sample data can be safely shared after redaction?",
            "5. What tools does the business already use?",
            "6. Who approves customer-facing messages or decisions?",
            "7. What should never be automated?",
            "8. What would prove value in 7 days?",
            "9. What data is sensitive, regulated, or private?",
            "10. Who owns accounts, cloud settings, domain, forms, and billing?",
            "",
            "If the client cannot answer these, start with a workflow map and manual checklist before building anything.",
            "",
        ]
    )


def _render_ai_agent_handoff(payload: dict) -> str:
    return "\n".join(
        [
            "# AI Agent Handoff: Side Hustle Blueprints",
            "",
            "You are helping a beginner choose and package a sellable business automation side-hustle offer.",
            "",
            "## Rules",
            "",
            "- Ask one question at a time.",
            "- Do not ask for secrets, passwords, API keys, real customer records, or payment data in chat.",
            "- Pick a small proof-of-value before proposing full automation.",
            "- Keep human approval boundaries visible.",
            "- Prefer local dry-run or spreadsheet-first delivery for the first client.",
            "- Explain what the user must prepare: sample data, folder names, form fields, approval owner, and existing tools.",
            "",
            "## Files To Read",
            "",
            "1. `START_HERE_SIDE_HUSTLE_BLUEPRINTS.md`",
            "2. `side_hustle_blueprints.md`",
            "3. `first_client_picker.md`",
            "4. `client_intake_questions.md`",
            "5. `implementation_paths.md`",
            "6. `risk_boundaries.md`",
            "",
            "## Output To Produce For The Human",
            "",
            "- recommended first offer",
            "- what to prepare",
            "- what can be automated now",
            "- what requires human approval",
            "- first 3-day proof-of-value plan",
            "- simple client pitch",
            "",
        ]
    )


def _render_catalog_html(payload: dict) -> str:
    cards = []
    for item in payload["blueprints"]:
        cards.append(
            """
            <article class="card">
              <h2>{name}</h2>
              <p class="buyer">{buyer}</p>
              <p>{pain}</p>
              <dl>
                <dt>Inputs</dt><dd>{inputs}</dd>
                <dt>Deliverables</dt><dd>{deliverables}</dd>
                <dt>Tools</dt><dd>{tools}</dd>
                <dt>Price</dt><dd>{price}</dd>
                <dt>Human approval</dt><dd>{human_approval}</dd>
              </dl>
              <p class="offer">{first_offer}</p>
            </article>
            """.format(**{key: html.escape(str(value)) for key, value in item.items()})
        )
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Side Hustle Automation Blueprints</title>
  <style>
    :root {{ color-scheme: light; font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    body {{ margin: 0; background: #f7f8fa; color: #111827; }}
    header {{ padding: 32px 24px 16px; max-width: 1180px; margin: 0 auto; }}
    h1 {{ margin: 0 0 8px; font-size: 34px; line-height: 1.1; letter-spacing: 0; }}
    .summary {{ max-width: 760px; color: #4b5563; font-size: 16px; line-height: 1.6; }}
    main {{ max-width: 1180px; margin: 0 auto; padding: 16px 24px 40px; display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; }}
    .card {{ background: white; border: 1px solid #d8dee8; border-radius: 8px; padding: 18px; box-shadow: 0 1px 2px rgba(15, 23, 42, .05); }}
    h2 {{ font-size: 19px; margin: 0 0 6px; letter-spacing: 0; }}
    .buyer {{ color: #2563eb; font-weight: 700; margin: 0 0 12px; }}
    p {{ line-height: 1.5; }}
    dl {{ display: grid; grid-template-columns: 110px 1fr; gap: 8px 12px; margin: 14px 0; }}
    dt {{ color: #6b7280; font-weight: 700; }}
    dd {{ margin: 0; }}
    .offer {{ border-top: 1px solid #e5e7eb; padding-top: 12px; font-weight: 700; }}
  </style>
</head>
<body>
  <header>
    <h1>Side Hustle Automation Blueprints</h1>
    <p class="summary">A practical catalog of bounded automation offers a beginner can package, demo, and sell with human approval boundaries.</p>
  </header>
  <main>
    {cards}
  </main>
</body>
</html>
""".format(cards="\n".join(cards))
