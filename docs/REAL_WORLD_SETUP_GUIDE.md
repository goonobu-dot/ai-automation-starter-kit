# Real World Setup Guide

AI Automation Starter Kit starts in safe dry-run mode. It does not automatically send email, post to chat, update spreadsheets, or write to production systems.

## Check Connectors

```bash
ai-automation-kit connector-doctor --project .tmp/flow-project --output .tmp/connector-doctor
```

Open `.tmp/connector-doctor/connector_doctor.md`.

## Before Real Connectors

Confirm:

- the client owns the account
- credentials are stored in `.env` or the client's secret manager
- the human approver is named
- logs do not expose unnecessary sensitive data
- there is a written rollback or stop procedure
- the first production run uses a small amount of data

## Common Connector Paths

| System | First Use | Warning |
|---|---|---|
| Gmail / Outlook | create drafts | keep auto-send disabled until approved |
| Slack / Teams | draft approval messages | confirm channel and webhook ownership |
| Google Sheets | replace CSV input | minimize write permissions |
| Notion / Airtable | task or status tracking | watch for schema changes |
| HubSpot / CRM | lead cleanup or follow-up queue | production updates need approval |
| n8n / Make / Zapier | external workflow runtime | define task limits, credentials, and maintenance scope |

## Go Live Conditions

Do not Go Live until:

- the client reviewed the dry-run output
- the value hypothesis is measurable
- the approval owner is named
- rollback is written
- maintenance ownership is clear
- logs, retries, queues, approval audit, and alerts are documented

## Production Rule

Move one connector at a time. Keep human approval active until the client explicitly accepts the operational risk.

