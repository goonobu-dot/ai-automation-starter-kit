# First Client Walkthrough

This page helps a beginner use AI Automation Starter Kit to approach the first business automation client safely.

The goal is not to sell a large production automation system on day one. The goal is to choose one repeated business task, create a dry-run with sample data, and help the client decide whether a small paid PoC is worth doing.

## What You Should Have At The End

For the first client, aim for this:

- one clearly described business pain
- one input source
- one output
- one human approver
- a sample-data dry-run
- a demo or report the client can understand
- a bounded paid PoC scope if the client wants to continue

Do not start with cloud, APIs, payments, or production connectors unless the dry-run already shows value and the client has approved the next step.

## Step 1: Choose A Good First Client

Good first clients often have:

- repeated inquiries
- invoice or missing-document follow-up
- customer data in spreadsheets
- weekly reports created by hand
- email, form, or chat replies handled by one busy person

Avoid first clients where:

- they want company-wide automation immediately
- the workflow requires legal, medical, financial, or HR decisions
- nobody owns approval
- they cannot provide sample data
- they expect full production automation without a test phase

## Step 2: Offer A Small First Product

A good beginner-friendly first offer is:

```text
Business Automation Mini-Diagnosis + Dry-Run PoC
```

Simple explanation:

```text
We choose one repeated workflow, use sample or anonymized data, and create a safe AI automation dry-run.
It will not send real messages or update production systems.
It will create drafts, a work queue, an approval list, and a client-readable report so we can decide whether automation is worth continuing.
```

This keeps the promise realistic and easier for a business owner to trust.

## Step 3: Ask The Client Human Questions First

Do not start by talking about tools. Start with the work.

Ask:

1. What task repeats every week or month?
2. Who handles it today?
3. How long does one item take?
4. Where does the request or file arrive?
5. What output means the task is done?
6. Who should review AI drafts?
7. Can you provide sample or anonymized data?
8. Would you review a dry-run that does not send or update anything for real?

If the client cannot answer these questions, start with workflow mapping instead of automation setup.

## Step 4: Let An AI Agent Interview You

Paste this into ChatGPT, Claude, Gemini, Cursor, Codex, Claude Code, or another AI agent:

```text
I am new to AI automation and want to prepare my first business automation client project.
Please read this GitHub project: ai-automation-starter-kit.
Start with docs/FIRST_CLIENT_WALKTHROUGH.md and docs/USER_MANUAL.md.

Ask me one question at a time.
Ask about the business pain, input source, output, human approver, sample data, tools involved, cloud need, and paid PoC scope.

Do not ask me to paste real API keys, passwords, secrets, or private client data into chat.
If I try to rush into production, guide me back to dry-run first and human approval.
```

## Step 5: Create The First Demo Workspace

Invoice or document follow-up is a good first example because the input, output, and approval points are easy to explain.

```bash
ai-automation-kit complete-workspace \
  --flow-id invoice-document-followup \
  --client-type local-business \
  --niche accounting \
  --output .tmp/first-client
```

Open these first:

- `.tmp/first-client/FINAL_DELIVERY_GUIDE.md`
- `.tmp/first-client/client_command_center.html`
- `.tmp/first-client/demo_site/index.html`
- `.tmp/first-client/client_report/client_report.html`
- `.tmp/first-client/business_launch/START_HERE_BUSINESS_LAUNCH.md`

When showing a client, use the HTML demo and report first. Do not lead with commands.

## Step 6: Explain The Demo

Use this order:

1. Confirm the current manual workflow.
2. Explain that the demo uses sample data.
3. Show the AI-created work queue.
4. Show the draft outputs.
5. Show the approval queue.
6. Explain what must be checked before production.
7. If there is value, define a paid PoC scope.

Useful wording:

```text
This is not production automation yet.
It is a dry-run that makes the workflow visible.
The AI creates drafts and task queues, and a human reviews them before anything moves forward.
```

## Step 7: Scope The Paid PoC

Include:

- one workflow
- sample or anonymized data
- dry-run execution
- work queue
- draft outputs
- approval list
- client report
- cloud-readiness checklist

Do not include:

- production sending
- production database writes
- 24/7 autonomous operation
- income guarantees
- legal, medical, financial, or HR decisions
- managing the client's cloud account as if you owned it

## Step 8: Decide Whether Cloud Is Needed

Move toward cloud only after:

- the client understands the value
- there is a named approver
- the dry-run works with sample data
- the connectors are known
- billing and account ownership are clear
- rollback and stop conditions are documented

Then run:

```bash
ai-automation-kit guided-setup \
  --flow-id invoice-document-followup \
  --mode beginner \
  --deployment undecided \
  --connectors gmail,google-sheets \
  --output .tmp/first-client-guided-setup
```

```bash
ai-automation-kit cloud-plan \
  --flow-id invoice-document-followup \
  --provider aws \
  --workload scheduled-job \
  --connectors gmail,google-sheets \
  --output .tmp/first-client-cloud-plan
```

## First Client Success Criteria

The first project is successful if:

- the client understands what can be automated
- you can show AI-generated drafts or work queues
- the missing production setup items are clear
- risk and approval points are visible
- the client can choose continue, revise, or stop

Trust comes from clear boundaries. This project helps a beginner explain those boundaries while still making automation feel practical and reachable.
