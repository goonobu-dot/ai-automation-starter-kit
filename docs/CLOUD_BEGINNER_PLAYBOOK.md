# Beginner Cloud Challenge Playbook

This playbook is for people who are new to AI agents but want to try a realistic business automation offer. The goal is not to build a large production system first. The goal is to create a small, safe first paid PoC around one workflow, one input source, one output destination, and one human approver.

## Target Outcome

You should be able to:

- Choose one business pain.
- Pick one matching flow.
- Create a local dry-run demo.
- Explain before/after value to a client.
- List what to prepare for cloud deployment.
- Separate what the AI can do from what the human must approve.
- Offer a bounded paid PoC without overpromising.

## What To Prepare

- A computer that can run this project.
- A short description of the business process.
- Sample input data such as CSV rows, example emails, form submissions, or spreadsheet rows.
- The desired output destination.
- The human approver.
- The client tools involved: Gmail, Google Sheets, Slack, LINE, CRM, shared folders, webhooks, or email.
- A rule for when production sending is allowed.

Do not paste real API keys, secrets, or sensitive client data into chat.

## What The AI Can Do

- Help choose a workflow.
- Generate a complete local workspace.
- Create setup questions.
- Review missing setup items.
- Generate a cloud-plan.
- Draft client explanations, PoC scope, pricing notes, and rollback steps.

## What The Human Must Approve

- Whether client data may be used.
- Which cloud account is allowed.
- Who owns billing.
- Which API permissions are allowed.
- Whether production webhooks, schedulers, queues, or public traffic may be enabled.
- Who stops the system if something goes wrong.

## First Paid PoC Shape

Keep the first offer simple:

1. Ask about the current manual workflow.
2. Choose one automation flow.
3. Use sample data only.
4. Show the work queue, draft output, and approval queue.
5. Explain what manual work may be reduced.
6. Offer a 3-day to 2-week paid PoC.
7. Treat production deployment as a separate decision.

Do not promise full automation, guaranteed revenue, or unsupervised production operations.

## Good First Workflows

- Invoice and document follow-up.
- Support reply draft.
- Appointment reminders.
- Weekly KPI reports.
- CRM lead cleanup.
- Inventory reorder alerts.
- Interview scheduling.
- Internal FAQ routing.

These are easier because the input and output are understandable, and human approval can remain in the loop.

## Workflows To Avoid First

- Medical, legal, financial, or regulated decisions.
- Automatic contracts, refunds, payments, discounts, cancellations, or promises.
- Large volumes of sensitive personal data.
- Cross-department enterprise deployments.
- Any workflow without a rollback owner.

## One-Week Plan

Day 1: Choose one workflow and collect sample data.

Day 2: Run `complete-workspace`.

Day 3: Review dry-run output and prepare the client demo.

Day 4: Explain before/after value and collect missing information.

Day 5: Run `guided-setup` and `guided-review`.

Day 6: Run `cloud-plan`.

Day 7: Propose a paid PoC with scope, fee, duration, approver, and stop condition.

## Success Definition

The beginner win is not memorizing every cloud service. The win is helping a client understand what to prepare, what the automation can do safely, what still needs human approval, and what must be true before production deployment.

