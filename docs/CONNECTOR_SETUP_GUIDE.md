# Connector Setup Guide

This guide explains connector setup for `guided-setup` and `cloud-plan`. A connector is an input source, output destination, notification channel, or storage location used by an automation workflow.

Most beginners do not get stuck because of the cloud provider itself. They get stuck because they do not know which API key, folder, sheet, mailbox, or owner is required. This guide gives a practical checklist.

## Common Rules

- Do not paste real secrets into chat.
- Put names only in `.env.example`.
- Put real values in the cloud secrets manager or provider dashboard.
- If the client account owns the connector, the client must approve access.
- Confirm how to revoke access before production use.

## Gmail

Use for inquiry sorting, reply drafts, invoice follow-up, and client notification drafts.

Common values:

- `GMAIL_CLIENT_ID`
- `GMAIL_CLIENT_SECRET`
- `GMAIL_REFRESH_TOKEN`
- mailbox or label name
- send permission or draft-only rule

Beginner rule: start with draft-only output or a local outbox.

## Google Sheets

Use for input rows, work queues, KPI reports, lead cleanup, and tracking.

Common values:

- `GOOGLE_SHEETS_SPREADSHEET_ID`
- `GOOGLE_SERVICE_ACCOUNT_JSON`
- source sheet name
- destination sheet name

Beginner rule: use a copied test spreadsheet before writing to production.

## Slack

Use for internal notifications, approval requests, and escalation.

Common values:

- `SLACK_BOT_TOKEN`
- `SLACK_SIGNING_SECRET`
- target channel
- approved posting language

Beginner rule: use a test channel first.

## LINE

Use for store inquiries, school/class inquiries, appointment prechecks, and customer reply drafts.

Common values:

- `LINE_CHANNEL_SECRET`
- `LINE_CHANNEL_ACCESS_TOKEN`
- webhook URL
- LINE Developers channel

Beginner rule: keep an approval queue before replying to real customers. LINE is one example; this project supports cloud-wide deployment planning.

## CRM

Use for lead cleanup, customer updates, sales notes, and follow-up tasks.

Common values:

- `CRM_BASE_URL`
- `CRM_API_TOKEN`
- allowed update fields
- blocked update fields

Beginner rule: output proposed updates to CSV or an approval queue before writing to CRM.

## storage-folder / local-folder

Use for CSV intake, reception folders, output folders, and temporary client files.

Common values:

- `INPUT_FOLDER_PATH`
- `OUTPUT_FOLDER_PATH`
- filename rules
- processed-file folder

Beginner rule: local folders are enough for the first dry-run.

## Client Questions

- What data is the input?
- Who owns that data?
- What is the AI allowed to read?
- Where may the AI write output?
- Are sending, posting, or updating allowed automatically, or only after approval?
- Who stops the workflow if something goes wrong?

If you can answer these questions, you can move a connector discussion forward even as an AI beginner.

