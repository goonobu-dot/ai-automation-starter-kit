# AI Reception Employee Pack

The AI Reception Employee Pack is the recommended first business offer in this project.

It is designed for people who are new to AI agents and want a concrete way to help a small business automate one visible workflow. The target is not a broad AI platform. The target is first response work: incoming inquiries, booking requests, estimate requests, missing information, owner escalation, and daily reports.

This pack turns the project from "many automation templates" into a clearer service path:

1. Choose an AI reception flow.
2. Prepare the minimum input and output settings.
3. Run a local dry-run.
4. Review drafts and the approval queue.
5. Show the operator UI to the client.
6. Package the result as a Paid dry-run PoC.

## What This Helps Automate

The reception flows are built around practical small-business work:

- LINE, web form, or email inquiry intake.
- FAQ-based first response drafts.
- Appointment precheck and missing-information questions.
- Estimate request intake before a human prepares a final quote.
- Google Sheets style reception logs.
- Human escalation for complaints, sensitive questions, money, contracts, medical/legal/financial questions, or anything outside the approved script.
- Daily reception reports for the business owner.

The goal is to reduce missed inquiries and manual follow-up time while keeping a human in control.

## What The User Must Prepare

Before a real client deployment, the operator needs these items:

- API keys or OAuth access for any real connector that will be enabled later.
- A reception folder or source export folder for CSV, email, LINE, form, or spreadsheet input.
- A safe sample dataset for the first dry-run.
- An output folder for work queues, draft replies, approval records, reports, and local outbox files.
- A standard FAQ, service menu, reply rules, or intake checklist.
- A named human approval owner.
- Clear escalation rules.
- A rollback or stop condition before production use.

If a user does not know how to prepare these, they can ask Claude Code, Codex, Cursor, or another AI agent to read this GitHub repository and help them create the setup step by step.

Useful AI-agent prompts:

```text
Read this GitHub project and explain how to install the AI reception flow.
Choose the best flow for a small business that receives LINE inquiries.
Create a setup checklist for my client using docs/AI_RECEPTION_EMPLOYEE_PACK.md.
Explain what API keys, folders, and sample data I need before dry-run.
Help me modify ai-reception-line-inquiry for a beauty salon / school / legal office / renovation company.
```

## Recommended Command

```bash
ai-automation-kit flows install ai-reception-line-inquiry --output .tmp/ai-reception-line-inquiry
```

Then review:

- `setup_requirements.md`
- `client_setup_request.md`
- `connector_status.md`
- `operator_ui/index.html`
- `monetization_plan.md`
- `workflow_map.mmd`
- `human_approval_points.md`

Run the safe local dry-run:

```bash
cd .tmp/ai-reception-line-inquiry
python3 scripts/run_automation.py
python3 scripts/approve_all.py --approver owner@example.com
python3 -m pytest tests/test_flow_contract.py -q
```

The generated project does not send real messages, update production systems, or connect to live client accounts by default.

## What The Operator UI Shows

`operator_ui/index.html` is a local browser page for explaining the flow to a client. It shows:

- what the workflow automates,
- each step in the workflow,
- where human approval is required,
- success metrics,
- which files to review before a paid PoC.

This is important for users who are not technical. They should not have to inspect Python code to understand the business value.

## Paid Dry-Run PoC

The first monetizable offer should be a Paid dry-run PoC, not a promise of full automation.

A practical scope is:

- one workflow,
- one source export or reception folder,
- one output folder,
- one approval owner,
- sample data only,
- three to five business days,
- no production sending,
- no irreversible updates,
- no medical, legal, financial, hiring, refund, payment, or contract decision by AI.

Suggested price ranges:

- Starter dry-run PoC: 50,000 to 150,000 JPY.
- Setup plus first month support: 100,000 to 300,000 JPY.
- Monthly maintenance after approval: 30,000 to 100,000 JPY.

These are planning ranges, not income guarantees. Do not promise income. Do not promise guaranteed savings. Show the client dry-run evidence and let them decide whether to continue, revise, or stop.

## Why Reception First

Reception and first response work is a strong first category because:

- the pain is easy to understand,
- missed inquiries have visible business cost,
- the workflow can be shown with sample data,
- the client can review drafts before sending,
- LINE, form, email, and spreadsheet exports are familiar,
- high-risk actions can be escalated to humans.

Sales outreach, legal decisions, medical advice, financial decisions, refunds, payments, and hiring decisions should not be the first automation offer.

## Production Boundary

Use this project as a setup and dry-run system first. Before production:

- confirm the client owns the data,
- review credentials and API scopes,
- define human approval rules,
- define forbidden actions,
- define rollback steps,
- test with sample data,
- run `connector_status.md` and `share-check`,
- get written client approval for go-live.

The project is strongest when it helps a beginner explain the workflow clearly, prepare the required inputs, run safely, and package the evidence into a realistic paid PoC.
