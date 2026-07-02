# AI Employee Roadmap

This roadmap explains which AI employee ideas should be included in this project first, which should be delayed, and how users should package them for safer client work.

The project goal is not to claim that AI can replace a full department. The goal is to help a beginner choose one concrete workflow, prepare the required inputs, generate a local dry-run workspace, show a client-facing UI, and package the result as a bounded paid proof of concept.

## Priority 1: AI Reception Employee

Start here.

The AI Reception Employee is the strongest first offer because it solves a visible small-business problem:

- missed inquiries,
- slow first response,
- incomplete booking or estimate information,
- manual FAQ replies,
- owner follow-up overload,
- lack of daily reception reporting.

Use:

```bash
ai-automation-kit flows list --industry reception
ai-automation-kit flows install ai-reception-line-inquiry --output .tmp/ai-reception-line-inquiry
```

Review:

- `setup_requirements.md`
- `client_setup_request.md`
- `ai_action_procedure.md`
- `operator_ui/index.html`
- `monetization_plan.md`

This is the recommended path for a first Paid dry-run PoC.

## Priority 2: Internal FAQ / Admin Employee

Internal FAQ and admin routing are the next practical category.

These flows help a business route internal questions, policy requests, HR/admin/IT requests, and missing knowledge-base topics. They are safer than customer-facing production automation because the first users are internal employees, and answers can remain drafts until the owner reviews them.

Use:

```bash
ai-automation-kit flows list --industry admin
ai-automation-kit flows install ai-admin-faq-routing --output .tmp/ai-admin-faq-routing
```

Good first use cases:

- internal FAQ routing,
- general affairs request intake,
- policy request routing,
- missing knowledge-base detection,
- owner review packet generation.

Do not let the AI decide exceptions, employee rights, access grants, legal interpretations, or compensation rules without human approval.

## Priority 3: Sales Research Employee

Sales Research is useful, but it should start as preparation work, not autonomous outreach.

Use:

```bash
ai-automation-kit flows list --industry sales-research
ai-automation-kit flows install ai-sales-research-brief --output .tmp/ai-sales-research-brief
```

Good first use cases:

- account research briefs,
- meeting preparation,
- follow-up draft preparation,
- CRM update drafts,
- proposal input extraction.

Do not start with outbound sales automation. Do not mass-send cold emails, scrape personal data carelessly, or let the AI make claims that the sales owner has not reviewed.

## What To Delay

Delay these until there is evidence from successful dry-runs:

- broad multi-department AI employee bundles,
- autonomous outbound sales,
- autonomous contract review,
- medical or legal advice,
- payment, refund, or financial decisions,
- hiring decisions,
- production database updates,
- access grants.

The multi-department AI employee idea is useful as a future roadmap, but it is too broad for the first sellable workflow. Build trust with one workflow first, then expand.

## Required Operating Procedure

Every installed flow includes `ai_action_procedure.md`.

That file defines:

- Allowed Actions,
- Forbidden Actions,
- Escalation Rules,
- Human Approval Steps,
- Production Gate.

This is important because a sellable AI employee is not just a prompt. It needs a clear job description, allowed actions, forbidden actions, and escalation rules.

## Recommended Expansion Order

1. AI Reception Employee.
2. Internal FAQ / Admin Employee.
3. Sales Research Employee.
4. Client-specific connector setup.
5. Reusable case studies.
6. Multi-department package only after there is proof from multiple safe workflows.

This keeps the project commercially useful without overpromising.
