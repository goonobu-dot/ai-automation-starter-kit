from __future__ import annotations

import csv
import html
import io
import json
from pathlib import Path

from ai_automation_kit.core.flows import get_flow
from ai_automation_kit.core.flows import list_flows


ARTIFACTS = [
    "README.md",
    "START_HERE_FOR_SIDE_BUSINESS.md",
    "flow_gallery.html",
    "selected_flow_demo.html",
    "proposal_one_pager.md",
    "beginner_pitch_script.md",
    "client_questions.md",
    "roi_simple_calculator.csv",
    "three_day_poc_plan.md",
    "price_menu.md",
    "outreach_messages.md",
    "objection_handling.md",
    "demo_walkthrough.md",
    "client_delivery_checklist.md",
    "positioning.md",
    "differentiation_matrix.md",
    "beginner_sales.json",
]


def generate_beginner_sales_pack(
    flow_id: str | None,
    output: Path,
    client_type: str,
    niche: str,
    industry: str = "operations",
) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    selected_flow = _select_flow(flow_id=flow_id, industry=industry)
    gallery_flows = _gallery_flows(selected_flow["industry"])
    payload = {
        "client_type": client_type,
        "niche": niche,
        "industry": selected_flow["industry"],
        "flow": selected_flow,
        "gallery_count": len(gallery_flows),
        "artifacts": ARTIFACTS,
        "beginner_score": _score_beginner_pack(selected_flow, gallery_flows),
        "research_positioning": _research_positioning(),
    }
    renderers = {
        "README.md": _render_readme,
        "START_HERE_FOR_SIDE_BUSINESS.md": _render_start_here,
        "proposal_one_pager.md": _render_proposal,
        "beginner_pitch_script.md": _render_pitch_script,
        "client_questions.md": _render_client_questions,
        "three_day_poc_plan.md": _render_three_day_poc,
        "price_menu.md": _render_price_menu,
        "outreach_messages.md": _render_outreach_messages,
        "objection_handling.md": _render_objection_handling,
        "demo_walkthrough.md": _render_demo_walkthrough,
        "client_delivery_checklist.md": _render_delivery_checklist,
        "positioning.md": _render_positioning,
        "differentiation_matrix.md": _render_differentiation_matrix,
    }
    for filename, renderer in renderers.items():
        (output / filename).write_text(renderer(payload), encoding="utf-8")
    (output / "flow_gallery.html").write_text(_render_flow_gallery(payload, gallery_flows), encoding="utf-8")
    (output / "selected_flow_demo.html").write_text(_render_selected_flow_demo(payload), encoding="utf-8")
    (output / "roi_simple_calculator.csv").write_text(_render_roi_csv(payload), encoding="utf-8")
    (output / "beginner_sales.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def _select_flow(flow_id: str | None, industry: str) -> dict:
    if flow_id:
        return get_flow(flow_id)
    candidates = list_flows(industry=industry)
    if not candidates:
        candidates = list_flows()
    return get_flow(candidates[0]["id"])


def _gallery_flows(industry: str) -> list[dict]:
    industry_flows = list_flows(industry=industry)
    seen = {flow["id"] for flow in industry_flows}
    broader_flows = [flow for flow in list_flows() if flow["id"] not in seen]
    return (industry_flows + broader_flows)[:18]


def _score_beginner_pack(flow: dict, gallery_flows: list[dict]) -> dict:
    categories = {
        "visual_flow_gallery": 15 if gallery_flows else 0,
        "selected_demo": 15,
        "client_discovery": 15,
        "proposal_and_pitch": 15,
        "roi_and_pricing": 15,
        "poc_delivery": 15,
        "risk_boundaries": 10,
    }
    return {
        "total": sum(categories.values()),
        "label": "side_business_ready",
        "categories": categories,
        "notes": [
            "No income is guaranteed.",
            "Use this as a beginner operating system for finding, explaining, scoping, and safely piloting automation work.",
            "Production connectors still require client approval, credentials, and data review.",
        ],
    }


def _research_positioning() -> list[str]:
    return [
        "Open-source automation tools are strong at workflow execution and integrations.",
        "Template libraries are strong at fast starts, but often weak at client discovery, pricing, and delivery packaging.",
        "Agent frameworks are strong for developers, but beginners need visible flows, safe local dry-runs, and sales-ready artifacts.",
        "This pack combines workflow selection, client explanation, proposal assets, ROI framing, and approval-first delivery.",
    ]


def _render_readme(payload: dict) -> str:
    flow = payload["flow"]
    return "\n".join(
        [
            f"# Beginner Sales Pack: {flow['name']}",
            "",
            f"This pack helps a new AI-agent user explain, demo, scope, and sell a safe {flow['industry']} automation pilot for {payload['niche']} {payload['client_type']} clients.",
            "",
            "No income is guaranteed. The goal is to make the first client conversation more concrete, safer, and easier to understand.",
            "",
            "## Start Here",
            "",
            "1. Read `START_HERE_FOR_SIDE_BUSINESS.md`.",
            "2. Open `flow_gallery.html` to choose a workflow category.",
            "3. Open `selected_flow_demo.html` to explain what the automation does.",
            "4. Use `client_questions.md` during discovery.",
            "5. Fill `roi_simple_calculator.csv` with conservative numbers.",
            "6. Send `proposal_one_pager.md` only after the client confirms the workflow.",
            "7. Deliver the first proof with `three_day_poc_plan.md` and `client_delivery_checklist.md`.",
            "",
            "## Score",
            "",
            f"- Total: `{payload['beginner_score']['total']}/100`",
            f"- Label: `{payload['beginner_score']['label']}`",
            "",
            "## Why This Exists",
            "",
        ]
        + [f"- {item}" for item in payload["research_positioning"]]
        + [""]
    )


def _render_start_here(payload: dict) -> str:
    flow = payload["flow"]
    return "\n".join(
        [
            "# Start Here For Side Business",
            "",
            "No income is guaranteed. This kit helps you move from vague AI automation talk to a concrete, reviewable pilot offer.",
            "",
            "## The Simple Path",
            "",
            f"1. Pick one repeated workflow: `{flow['name']}`.",
            "2. Ask the client how the work happens today.",
            "3. Show the visual demo and before/after explanation.",
            "4. Estimate time saved with conservative numbers.",
            "5. Offer a small dry-run pilot using sample or approved exported data.",
            "6. Keep human approval before external sends, record updates, money movement, access grants, hiring decisions, or regulated work.",
            "7. Convert the pilot into maintenance only when the client can see measured value.",
            "",
            "## Beginner Rule",
            "",
            "Do not sell a giant system first. Sell one narrow workflow, one visible demo, one approval point, and one measurable result.",
            "",
        ]
    )


def _render_proposal(payload: dict) -> str:
    flow = payload["flow"]
    metrics = ", ".join(flow["success_metrics"])
    return "\n".join(
        [
            f"# One-Page Proposal: {flow['name']}",
            "",
            f"Client type: `{payload['client_type']}`",
            f"Niche: `{payload['niche']}`",
            "",
            "## Problem",
            "",
            f"The client repeats a {flow['genre']} workflow manually across {', '.join(flow['tools'])}. This creates delays, status gaps, and repeated follow-up work.",
            "",
            "## Pilot",
            "",
            "Build a safe local dry-run that reads approved sample data, creates a work queue, drafts recommended outputs, preserves human approval, and writes an audit-ready status report.",
            "",
            "## Success Metrics",
            "",
            metrics,
            "",
            "## Boundaries",
            "",
            "The pilot does not send messages, update production records, move money, grant access, or make regulated decisions without named human approval.",
            "",
        ]
    )


def _render_pitch_script(payload: dict) -> str:
    flow = payload["flow"]
    return "\n".join(
        [
            "# Beginner Pitch Script",
            "",
            f"I help {payload['niche']} teams turn one repeated {flow['industry']} workflow into a small automation pilot.",
            "",
            f"For example, `{flow['name']}` takes the existing spreadsheet, inbox, or export, turns it into a visible queue, drafts the next action, and keeps human approval before anything external happens.",
            "",
            "The first step is not a big system build. It is a short workflow map, conservative ROI estimate, and a dry-run demo using safe data.",
            "",
        ]
    )


def _render_client_questions(payload: dict) -> str:
    flow = payload["flow"]
    return "\n".join(
        [
            f"# Client Questions: {flow['name']}",
            "",
            "- What work do you repeat every week in this area?",
            "- Where does the work start today?",
            "- Which spreadsheet, inbox, form, CRM, or system contains the source data?",
            "- Who checks the result before it affects a customer, employee, vendor, or record?",
            "- How many times per month does this happen?",
            "- How many minutes does one item take manually?",
            "- What goes wrong most often?",
            "- What would make a 3-day dry-run obviously useful?",
            "- Which data must not leave your approved systems?",
            "- Who owns the final approval?",
            "",
        ]
    )


def _render_roi_csv(payload: dict) -> str:
    rows = [
        ["field", "example_value", "notes"],
        ["monthly_items", "80", "How many times this workflow happens per month."],
        ["minutes_per_item_before", "8", "Current manual time per item."],
        ["minutes_per_item_after", "3", "Conservative pilot estimate after automation support."],
        ["loaded_hourly_cost", "35", "Use local labor cost or client estimate."],
        ["monthly_tool_cost", "50", "Hosting, SaaS, or API cost estimate."],
        ["estimated_hours_saved", "=(monthly_items*(minutes_per_item_before-minutes_per_item_after))/60", "Spreadsheet formula placeholder."],
        ["estimated_monthly_value", "=estimated_hours_saved*loaded_hourly_cost-monthly_tool_cost", "Value estimate, not a guarantee."],
        ["pilot_fee_floor", "=estimated_monthly_value*1.5", "Use judgment and risk review."],
        ["monthly_maintenance_floor", "=estimated_monthly_value*0.15", "Only sell maintenance with concrete monitoring tasks."],
    ]
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerows(rows)
    return buffer.getvalue()


def _render_three_day_poc(payload: dict) -> str:
    flow = payload["flow"]
    return "\n".join(
        [
            f"# Three-Day PoC Plan: {flow['name']}",
            "",
            "## Day 1: Map And Prepare",
            "",
            "- Confirm source data, approval owner, and success metric.",
            "- Use exported sample data or anonymized rows.",
            "- Write the before/after workflow.",
            "",
            "## Day 2: Build Dry-Run",
            "",
            "- Install the selected flow.",
            "- Run local automation against sample data.",
            "- Generate queue, drafts, approval list, and status report.",
            "",
            "## Day 3: Review And Decide",
            "",
            "- Review outputs with the client.",
            "- Compare against ROI estimate.",
            "- Decide continue, revise, or stop.",
            "- If continuing, scope production connectors and monthly maintenance separately.",
            "",
        ]
    )


def _render_price_menu(payload: dict) -> str:
    return "\n".join(
        [
            "# Price Menu",
            "",
            "Use local market judgment. These are packaging shapes, not guaranteed prices.",
            "",
            "| Offer | What It Includes | When To Sell |",
            "|---|---|---|",
            "| Workflow Audit | questions, flow map, ROI estimate, risk notes | client is curious but not ready for build |",
            "| Dry-Run Pilot | local demo, sample data run, approval queue, report | client has one repeated workflow |",
            "| Production Connector Scope | credential plan, data policy, rollback plan | dry-run proved useful |",
            "| Monthly Maintenance | run review, small fixes, KPI note, improvement backlog | client depends on the workflow |",
            "",
        ]
    )


def _render_outreach_messages(payload: dict) -> str:
    flow = payload["flow"]
    return "\n".join(
        [
            "# Outreach Messages",
            "",
            "## Short DM",
            "",
            f"I am mapping repeated {flow['industry']} workflows for {payload['niche']} teams and turning one into a safe dry-run automation demo. Is there a workflow your team repeats every week?",
            "",
            "## Follow-Up",
            "",
            "The first step is small: workflow map, conservative ROI estimate, and a local demo that creates drafts and approval queues without touching production systems.",
            "",
            "## After Interest",
            "",
            "I can send a one-page pilot scope showing the workflow, approval point, expected value, and maintenance option.",
            "",
        ]
    )


def _render_objection_handling(payload: dict) -> str:
    return "\n".join(
        [
            "# Objection Handling",
            "",
            "## We already use ChatGPT",
            "",
            "That helps with one-off answers. This pilot turns a repeated business workflow into a visible queue, approval process, and measurable report.",
            "",
            "## We are worried about data",
            "",
            "The first pilot can run on sample or exported approved data. No external sends or production updates happen by default.",
            "",
            "## We tried automation before",
            "",
            "This starts smaller: one workflow, one approval owner, one metric, one stop/revise/continue decision.",
            "",
            "## We do not know what to automate",
            "",
            "Start with the workflow that repeats weekly, has clear input/output, and causes follow-up delays.",
            "",
        ]
    )


def _render_demo_walkthrough(payload: dict) -> str:
    flow = payload["flow"]
    return "\n".join(
        [
            f"# Demo Walkthrough: {flow['name']}",
            "",
            "1. Show the current manual workflow and ask the client to correct it.",
            "2. Show `selected_flow_demo.html` and explain each step.",
            "3. Run `ai-automation-kit flows install` for the selected flow.",
            "4. Run the dry-run on sample data.",
            "5. Open the generated work queue, drafts, approval queue, and status report.",
            "6. Ask whether the output is useful enough to pilot with approved client data.",
            "",
        ]
    )


def _render_delivery_checklist(payload: dict) -> str:
    return "\n".join(
        [
            "# Client Delivery Checklist",
            "",
            "- [ ] One workflow selected.",
            "- [ ] Source data owner named.",
            "- [ ] Approval owner named.",
            "- [ ] Sensitive data classified.",
            "- [ ] ROI baseline captured.",
            "- [ ] Dry-run output reviewed.",
            "- [ ] Stop/revise/continue decision recorded.",
            "- [ ] Production connector scope separated from dry-run scope.",
            "- [ ] Maintenance tasks defined before offering a retainer.",
            "",
        ]
    )


def _render_positioning(payload: dict) -> str:
    flow = payload["flow"]
    return "\n".join(
        [
            "# Positioning",
            "",
            f"Audience: new AI-agent users who want to sell practical automation pilots to {payload['niche']} {payload['client_type']} clients.",
            "",
            f"Lead offer: `{flow['name']}`.",
            "",
            "Core promise: make one repeated workflow visible, safer, easier to review, and easier to measure.",
            "",
            "Avoid saying: guaranteed income, fully autonomous business, replace every employee, or production-ready without client review.",
            "",
            "Say instead: small dry-run pilot, human approval, measurable workflow, conservative ROI, monthly maintenance if value is proven.",
            "",
        ]
    )


def _render_differentiation_matrix(payload: dict) -> str:
    return "\n".join(
        [
            "# Differentiation Matrix",
            "",
            "| Category | Strong Public Tools | What They Are Great At | This Kit Adds For Beginners |",
            "|---|---|---|---|",
            "| Visual automation | n8n, Activepieces, Make, Zapier | integrations and workflow execution | client discovery, proposal, ROI, dry-run safety, delivery checklist |",
            "| AI agent builders | Dify, Flowise, LangGraph, CrewAI | agent logic and model orchestration | business-flow packaging and non-technical sales assets |",
            "| Template libraries | n8n template collections, workflow galleries | fast examples | niche positioning, objections, price menu, PoC plan |",
            "| Production starters | Google agent starter packs, Cloudflare agents | deployment and infra patterns | beginner client path before production |",
            "| Chat-only AI | ChatGPT, Claude, Codex | flexible reasoning and drafting | repeatable files, commands, flow maps, and approval evidence |",
            "",
        ]
    )


def _render_flow_gallery(payload: dict, flows: list[dict]) -> str:
    cards = []
    for flow in flows:
        cards.append(
            "\n".join(
                [
                    '<article class="card">',
                    f"<h2>{html.escape(flow['name'])}</h2>",
                    f"<p>{html.escape(flow['summary'])}</p>",
                    f"<dl><dt>Industry</dt><dd>{html.escape(flow['industry'])}</dd><dt>Genre</dt><dd>{html.escape(flow['genre'])}</dd><dt>Flow ID</dt><dd><code>{html.escape(flow['id'])}</code></dd></dl>",
                    "</article>",
                ]
            )
        )
    body = "\n".join(cards)
    return _html_page(
        title="Automation Flow Gallery",
        heading="Automation Flow Gallery",
        intro="Choose a workflow that is easy for a client to understand, demo, and measure.",
        body=f'<section class="grid">{body}</section>',
    )


def _render_selected_flow_demo(payload: dict) -> str:
    flow = payload["flow"]
    steps = []
    for index, step in enumerate(flow["steps"], start=1):
        approval = "<strong>Human approval</strong>" if step["human_approval"] else "Automated dry-run"
        steps.append(
            "\n".join(
                [
                    '<article class="step">',
                    f"<span>{index}</span>",
                    f"<h2>{html.escape(step['name'])}</h2>",
                    f"<p>{html.escape(step['tool'])}: {html.escape(step['input'])} -> {html.escape(step['output'])}</p>",
                    f"<p>{approval}</p>",
                    "</article>",
                ]
            )
        )
    metrics = "".join(f"<li>{html.escape(metric)}</li>" for metric in flow["success_metrics"])
    return _html_page(
        title=f"{flow['name']} Demo",
        heading=flow["name"],
        intro=flow["summary"],
        body=f'<section class="steps">{"".join(steps)}</section><section><h2>Success Metrics</h2><ul>{metrics}</ul></section>',
    )


def _html_page(title: str, heading: str, intro: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    body {{ margin: 0; font-family: Arial, sans-serif; color: #1d2430; background: #f6f7f9; }}
    header {{ padding: 32px; background: #ffffff; border-bottom: 1px solid #d9dee7; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 24px; }}
    h1 {{ margin: 0 0 8px; font-size: 34px; letter-spacing: 0; }}
    h2 {{ font-size: 18px; letter-spacing: 0; }}
    p {{ line-height: 1.6; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; }}
    .card, .step {{ background: #ffffff; border: 1px solid #d9dee7; border-radius: 8px; padding: 16px; }}
    .steps {{ display: grid; gap: 14px; }}
    .step span {{ display: inline-grid; place-items: center; width: 28px; height: 28px; border-radius: 999px; background: #0f766e; color: white; font-weight: 700; }}
    dt {{ font-weight: 700; margin-top: 10px; }}
    code {{ background: #eef2f7; padding: 2px 5px; border-radius: 4px; }}
  </style>
</head>
<body>
  <header>
    <h1>{html.escape(heading)}</h1>
    <p>{html.escape(intro)}</p>
  </header>
  <main>
    {body}
  </main>
</body>
</html>
"""
