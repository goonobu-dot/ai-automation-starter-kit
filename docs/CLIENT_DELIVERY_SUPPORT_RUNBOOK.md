# Client Delivery Support Runbook

This runbook explains how a beginner can use AI support before, during, and after a client automation project. The goal is to make the work sellable without exaggerating what the system can do.

## Plain client explanation

Do not sound like a developer manual. The client should understand the before and after without knowing APIs, cloud, or automation tools.

Use this shape:

- Before: your team manually checks incoming work, writes drafts, and remembers follow-up.
- After: the automation prepares a queue, draft, checklist, or report.
- Human approval: a person still checks important outputs before they affect customers or business records.
- First test: we start with fake or redacted data in a dry-run.

## Operating Principle

Use AI to prepare, question, draft, check, and document. Use humans to approve client facts, accounts, secrets, production changes, legal boundaries, and money.

Do not promise revenue, full automation, or hands-free operation. The offer should be a bounded paid dry-run PoC.

Practical rule: do not promise revenue; promise a measurable, reviewable dry-run test.

## before the sales call

Ask an AI agent to prepare:

- one industry pain hypothesis
- one recommended workflow
- a before/after explanation
- a short client question list
- a fake sample input
- a fake sample output
- what will stay human-approved
- what is not included
- what a paid dry-run PoC could test

Minimum preparation:

- choose one workflow from the catalog
- know the likely input source
- know the likely output
- prepare a simple explanation in client language
- prepare a stop condition

## during the discovery call

Use the AI-generated question list, but the human should ask the questions.

Confirm:

- current manual process
- frequency and volume
- current tools
- owner and approver
- input examples
- output examples
- client restrictions
- data sensitivity
- acceptable dry-run test
- success metric

Do not ask the client for real API keys during the sales call. Ask who owns the systems and whether they can provide access later if a paid PoC starts.

## after the first demo

Ask the AI to turn notes into:

- summary of client pain
- proposed workflow
- required sample data
- connector/account request list
- approval queue design
- dry-run test plan
- risks and exclusions
- paid PoC scope
- follow-up email

The first demo should use fake or redacted data. It should show the work queue, draft output, approval queue, and report. It should not send real customer messages.

## implementation support

When the PoC starts, the AI can help the operator:

- create a project checklist
- validate sample data columns
- draft `.env.example`
- explain where API keys are created
- generate folder naming rules
- create test cases
- create rollback notes
- review redacted errors
- produce a client status report

The human must:

- create accounts
- approve billing
- create API keys
- store secrets safely
- approve read/write permissions
- run or approve the dry-run
- approve any production traffic

## go-live gate

Do not go live until these are true:

- dry-run output was reviewed
- human approver is named
- rollback owner is named
- logging is visible
- error handling is explained
- secret storage is outside chat
- production sending is intentionally enabled
- client has accepted the scope
- risky cases have a manual fallback

If any item is missing, stay in dry-run.

## monthly operation

For an ongoing support relationship, AI can help prepare:

- monthly automation report
- failed item summary
- approval queue summary
- time saved estimate
- missed input list
- new workflow candidates
- risk review
- client follow-up email

The operator should review the report before sending it.

## Client-Facing Promise

Use this promise:

> We will test one specific workflow in a safe dry-run. The goal is to see whether AI can reduce manual preparation work while a human keeps approval over important outputs.

Avoid:

- "This will fully automate your company."
- "This guarantees revenue."
- "No human review is needed."
- "The AI can manage all cloud and API settings automatically."

## AI Prompt For Delivery Support

```text
Read the Client Delivery Support Runbook.
Help me prepare this client automation project one step at a time.
Separate before the sales call, during the discovery call, after the first demo, implementation support, go-live gate, and monthly operation.
Do not promise revenue or full automation.
Do not ask for real secrets in chat.
```
