# Flow Selection Guide

AI Automation Starter Kit includes 60+ business automation flows. For the first client conversation, choose a flow that a company can understand quickly.

## Recommended Command

```bash
ai-automation-kit flow-guide --industry finance --niche accounting --output .tmp/flow-guide
```

Open `.tmp/flow-guide/recommended_flows.md`.

## Good First Flows

- invoice and missing document follow-up
- support reply draft
- weekly KPI report
- approval request routing
- CRM lead cleanup
- appointment reminders
- inventory reorder alerts
- order or shipping status updates

These are good first flows because the input, output, and human approver are easy to explain.

## What To avoid For The First Project

- automatic payment or refund execution
- hiring, firing, credit, or legal decisions
- medical, legal, tax, or regulated advice
- direct writes to sensitive production systems
- workflows where nobody can name the approval owner

## Selection Criteria

A strong first flow has:

- clear input data
- output that can stay as a draft, report, or queue
- a named human approver
- monthly volume that can be counted
- value that can be measured through time saved, delay reduction, fewer missed follow-ups, or better audit evidence

## Practical Rule

If the client can understand the workflow in two minutes, it is probably a better first proposal than a technically impressive but confusing automation.
