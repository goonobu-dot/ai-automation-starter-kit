# FAQ

## Is this a real automation system?

Yes, but it starts as a safe dry-run. It creates local work queues, draft outputs, approval queues, reports, and local outbox files. It does not send external messages or update production systems by default.

## How is this different from asking an AI chat tool?

AI chat often ends as a conversation. This project creates reusable files: workflows, proposals, ROI sheets, run logs, approval queues, client reports, and go-live decisions.

## Can this help with a side business?

It can help package the work responsibly. It does not guarantee income. The goal is to help users find repeated business tasks, propose a small dry-run PoC, and show evidence before discussing production automation.

## Can someone new to AI propose this to a company?

Yes. Use `business-launch` to create the target industry playbook, first offer, discovery script, proposal builder, pricing menu, risk boundaries, 30-day launch plan, and pitch email.

```bash
ai-automation-kit business-launch --industry finance --client-type local-business --niche accounting --output .tmp/business-launch
```

The first offer should be a paid dry-run PoC using sample data, not a promise of fully autonomous production automation.

## What should I run first?

```bash
ai-automation-kit complete-workspace --flow-id invoice-document-followup --output .tmp/complete
```

This creates the final delivery guide, checklist, client report, demo site, shareable package, revenue readiness scorecard, Paid PoC scope, value sheet, pre-contract checklist, proposal email, 30-day plan, proof-of-value template, OSS benchmark, integration backlog, deployment options, observability plan, opportunity scorecard, onboarding form, go-live decision, command center, and `business_launch/` proposal pack.

## What should I show a company?

Start with `demo_site/index.html` and `beginner_sales/selected_flow_demo.html`. Then use `client_questions.md` or `discovery_call_script.md` to ask about the real workflow. Finish with a small proposal, not a production promise.

## What if I do not know what to sell?

Use `opportunity-catalog` to create a sales catalog, then use `recommend-flow` to turn the client's pain into one recommended flow. Run `share-check` before sending generated files to a client.

## Can it connect to production systems?

Yes, but production is intentionally gated. Use `connector-doctor`, `client_onboarding_form.md`, `deployment_options.md`, `production_observability_plan.md`, and `go_live_decision.md` before enabling real connectors, webhooks, retries, queues, or production writes.

