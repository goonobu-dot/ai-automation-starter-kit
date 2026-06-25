# AI Automation Starter Kit User Manual

This manual is for people who are new to AI agents, business automation, APIs, or cloud setup. It explains how to move from one business pain to a safe local dry-run, a client demo, and a bounded paid PoC.

You do not need to understand everything first. Start with one workflow, one input source, one output, and one human approver.

This project does not guarantee income. Its purpose is to turn vague AI automation ideas into visible workflows, required inputs, proposal files, dry-run evidence, approval boundaries, and go-live gates.

## First, Feel Safe About The Scope

This project does not send real messages or update production systems by default.

It starts with a dry-run. A dry-run creates draft outputs, work queues, approval lists, reports, and local files without real production sending or production writes.

Do not paste these into chat:

- real API keys
- passwords
- client private data
- production webhook URLs
- cloud administrator credentials
- confidential client documents

It is safe to ask an AI agent about:

- which workflow to choose
- what to ask the client
- which file to read next
- what sample data should look like
- how to run a dry-run
- what to check before cloud setup
- draft proposal wording

## The 5-Minute Mental Model

1. Choose one repeated business pain.
2. Pick one matching workflow from this project.
3. Create a local demo workspace.
4. Run a dry-run with sample or anonymized data.
5. Review drafts, queues, approval lists, and reports.
6. Show the client that it is a demo, not production automation.
7. If the value is clear, list the required APIs, folders, cloud account, and approver.
8. If selling a paid PoC, define scope, timeline, fee, and stop conditions.

The first goal is not "automate everything." The first goal is to help a client understand where manual work can be reduced safely.

## Read These First

If you are not sure where to start, read these in order:

1. [Start Here](START_HERE.md)
2. [AI Beginner Support Map](AI_BEGINNER_SUPPORT_MAP.md)
3. [Beginner Cloud Challenge Playbook](CLOUD_BEGINNER_PLAYBOOK.md)

If you want to use the project for freelance or consulting work, read [First Client Walkthrough](FIRST_CLIENT_WALKTHROUGH.md).

If cloud or API setup feels difficult, read [Cloud Deployment Guide](CLOUD_DEPLOYMENT_GUIDE.md) and [Connector Setup Guide](CONNECTOR_SETUP_GUIDE.md).

## Prompt To Give An AI Agent

Paste this into ChatGPT, Claude, Gemini, Cursor, Codex, Claude Code, or another AI agent:

```text
Please review this GitHub project: ai-automation-starter-kit.
I am new to AI automation and cloud setup.

First read docs/START_HERE.md, docs/USER_MANUAL.md, docs/AI_BEGINNER_SUPPORT_MAP.md, and docs/CLOUD_BEGINNER_PLAYBOOK.md.

Then ask me one question at a time.
Do not ask everything at once.
Please ask in this order:

1. Which business workflow do I want to improve?
2. Where does the input arrive?
3. What output should be created?
4. Who reviews or approves the result?
5. Can I provide sample or anonymized data?
6. Are APIs or cloud services needed?
7. Can we show it as a local dry-run first?
8. What is the safe paid PoC scope for a client?

Do not ask me to paste real API keys, passwords, secrets, or private client data into chat.
Before real sending, production writes, paid cloud usage, or public webhooks, require human approval.
```

## Install

Run:

```bash
git clone https://github.com/goonobu-dot/ai-automation-starter-kit.git
cd ai-automation-starter-kit
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip setuptools
python3 -m pip install -e .
ai-automation-kit doctor --output .tmp/doctor
```

Open `.tmp/doctor/doctor_report.md` if the command reports warnings.

## Easiest First Command

If you are not sure where to start, use:

```bash
ai-automation-kit complete-workspace \
  --flow-id invoice-document-followup \
  --client-type local-business \
  --niche accounting \
  --output .tmp/complete-accounting
```

It creates a first demo workspace around invoice and missing-document follow-up.

Read only these first:

| File | Why it matters |
|---|---|
| `.tmp/complete-accounting/FINAL_DELIVERY_GUIDE.md` | The first guide for the generated workspace. |
| `.tmp/complete-accounting/client_command_center.html` | Browser-friendly map of the generated files. |
| `.tmp/complete-accounting/demo_site/index.html` | Demo page to show what the workflow does. |
| `.tmp/complete-accounting/client_report/client_report.html` | Client-readable dry-run report. |
| `.tmp/complete-accounting/business_launch/START_HERE_BUSINESS_LAUNCH.md` | Entry point for a side-business or consulting offer. |

The folder contains many files, but you do not need to read all of them immediately.

## Choose A Workflow

To find a workflow that is easier to explain to a company:

```bash
ai-automation-kit flow-guide --industry finance --niche accounting --output .tmp/flow-guide
```

Open `recommended_flows.md` and choose one workflow.

Good beginner workflows:

- inquiry reply drafts
- invoice or missing-document follow-up
- appointment pre-checks
- FAQ routing
- weekly reports
- customer list cleanup
- daily work summaries

Avoid these as the first workflow:

- legal, medical, financial, or HR decisions
- automatic contract, payment, refund, cancellation, or discount actions
- production database writes that are hard to reverse
- workflows without a named approver
- workflows where client data rules are unclear

## Create Client-Facing Materials

Use `beginner-sales` when you want to explain one workflow visually:

```bash
ai-automation-kit beginner-sales \
  --flow-id invoice-document-followup \
  --client-type local-business \
  --niche accounting \
  --output .tmp/beginner-sales
```

Open these in order:

1. `.tmp/beginner-sales/flow_gallery.html`
2. `.tmp/beginner-sales/selected_flow_demo.html`
3. `.tmp/beginner-sales/client_questions.md`
4. `.tmp/beginner-sales/roi_simple_calculator.csv`
5. `.tmp/beginner-sales/proposal_one_pager.md`
6. `.tmp/beginner-sales/three_day_poc_plan.md`

Client wording:

```text
This will not send real messages at first.
We will use sample data to recreate the workflow, let AI draft tasks or replies, and keep a human approval step.
If the value is clear, we can list the required APIs, folders, cloud setup, cost, and stop procedure before deciding on a small PoC.
```

If you want the business proposal pack as a separate folder, run `business-launch`:

```bash
ai-automation-kit business-launch \
  --industry finance \
  --client-type local-business \
  --niche accounting \
  --output .tmp/business-launch
```

It creates the first offer, discovery script, proposal builder, pricing and scope menu, risk boundary sheet, 30-day plan, and client pitch email.

## Run A Local Dry-Run

```bash
ai-automation-kit flows install invoice-document-followup --output .tmp/flow-project
ai-automation-kit flows run .tmp/flow-project
ai-automation-kit flows approve .tmp/flow-project --approver owner@example.com
```

Main outputs:

| File | Meaning |
|---|---|
| `automation_output/work_queue.csv` | Work items created by the workflow. |
| `automation_output/draft_outputs.md` | Draft replies or draft task outputs. |
| `automation_output/approval_queue.csv` | Items a human must review. |
| `automation_output/status_report.md` | Summary of the run. |
| `local_outbox/email_drafts.md` | Email drafts that are not sent. |

The important point is that the AI does not send on its own. A human reviews and approves first.

## Create A Client Report

```bash
ai-automation-kit client-report --flow-project .tmp/flow-project --output .tmp/client-report
```

It creates `client_report.md` and `client_report.html`.

Use the report to explain:

- how many items were processed
- what the AI drafted
- what humans still need to approve
- what is missing before production
- whether to continue, revise, or stop

## Check Before Sharing

Before sending generated files to a client:

```bash
ai-automation-kit share-check --source .tmp/complete-accounting --output .tmp/share-check
```

If `share_check.md` says `blocked`, remove secret-like values before sharing.

To create a shareable package:

```bash
ai-automation-kit package-client-demo --source .tmp/complete-accounting --output .tmp/client-demo-package
```

## Before Cloud Or APIs

Move to cloud only after the local dry-run shows value.

Collect required inputs:

```bash
ai-automation-kit guided-setup \
  --flow-id invoice-document-followup \
  --mode beginner \
  --deployment undecided \
  --connectors gmail,google-sheets \
  --output .tmp/guided-setup
```

Review the answers:

```bash
ai-automation-kit guided-review \
  --answers .tmp/guided-setup/guided_setup_answers.example.json \
  --output .tmp/guided-review
```

Create a cloud plan:

```bash
ai-automation-kit cloud-plan \
  --flow-id invoice-document-followup \
  --provider aws \
  --workload scheduled-job \
  --connectors gmail,google-sheets \
  --output .tmp/cloud-plan
```

Beginner rules:

- Gmail, Google Sheets, Slack, and LINE are connectors.
- API keys are secret values used to access outside services.
- Real secrets do not belong in chat.
- Cloud billing, permissions, public URLs, and production webhooks need human approval.
- Start with drafts, test folders, and test channels before production.

## Move Toward Real Execution

After local value is clear, create starter files for execution platforms:

```bash
ai-automation-kit flow-export --flow-id invoice-document-followup --target n8n --output .tmp/flow-export-n8n
ai-automation-kit deployment-pack --flow-id invoice-document-followup --provider coolify --connectors gmail,google-sheets --output .tmp/deployment-coolify
ai-automation-kit runtime-safety --flow-id invoice-document-followup --output .tmp/runtime-safety
ai-automation-kit secrets-bootstrap --flow-id invoice-document-followup --provider infisical --connectors gmail,google-sheets --output .tmp/secrets-bootstrap
ai-automation-kit document-intake --flow-id invoice-document-followup --mode advanced --output .tmp/document-intake
ai-automation-kit observability-pack --flow-id invoice-document-followup --output .tmp/observability-pack
ai-automation-kit state-backend --flow-id invoice-document-followup --backend supabase --output .tmp/state-backend
```

The goal here is not instant production. The goal is to prepare execution files, secret ownership, approval rules, logs, state, and rollback before production.

## Turning It Into A Side Business Or Consulting Paid PoC Offer

The safest first offer is not "full automation." It is:

```text
Business Automation Diagnosis + Dry-Run PoC
```

Good first PoC shape:

- 3 days to 2 weeks
- sample data only
- no production sending
- human approval
- before/after explanation
- continue, revise, or stop decision at the end

Before selling, confirm:

- the client really has the repeated pain
- the monthly volume is high enough
- manual time is measurable
- sample data is available
- the approver is named
- production boundaries are clear
- rollback or stop conditions are clear

## Final Checklist

Before showing a company:

- no production sends happened
- no real secrets are in shared files
- client data is sample or anonymized
- the workflow can be explained in one sentence
- input, output, and approver are clear
- dry-run evidence exists
- client questions are ready
- paid PoC scope, timeline, and stop conditions are clear
- missing cloud/API inputs are visible

If this checklist is true, a beginner can explain the opportunity without pretending the system is already fully autonomous.
