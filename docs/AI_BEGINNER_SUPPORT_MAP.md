# AI Beginner Support Map

This map explains what AI can do now for a beginner who wants to use this project for business automation, and what a human must still do. It is designed for people who are comfortable asking an AI agent questions but are not yet comfortable with APIs, folders, cloud settings, deployment, or client delivery.

## Main Principle

AI can guide, draft, check, classify, generate files, explain errors, and prepare safe commands. A human must still approve accounts, billing, client access, secrets, production traffic, legal boundaries, and client promises.

Use this map before selling, building, or deploying anything.

## what AI can do now

| Area | AI can help with | Human still owns |
|---|---|---|
| Workflow choice | Compare candidate flows, ask one question at a time, recommend a small first PoC. | Confirm the client actually has the pain. |
| Client interview | Draft questions, turn vague answers into missing-input lists, prepare follow-up emails. | Speak with the client and confirm business facts. |
| Input design | Identify whether the input is email, form, LINE, Slack, spreadsheet, CRM, webhook, local folder, or storage bucket. | Grant access to the real system. |
| Sample data | Create fake sample data, redact real examples, define required columns. | Remove personal data and approve what can be shared. |
| API keys | Explain where keys are usually created and which values are needed. | Create accounts, enter billing, generate keys, and store them outside chat. |
| reception folder | Decide where incoming files should land and what naming rules are needed. | Create the actual folder and set permissions. |
| Output design | Draft approval queues, reports, reply drafts, spreadsheet rows, ticket summaries, or local outbox files. | Approve any message that affects a customer or business record. |
| Local dry-run | Generate a safe local test plan and checklist. | Run it on the user's machine or approve an operator to run it. |
| Cloud account | Compare AWS, Google Cloud, Azure, Render, Railway, Vercel, DigitalOcean, and Fly.io at a high level. | Create/select the cloud account, billing, IAM, domain, and production settings. |
| Troubleshooting | Interpret redacted errors, suggest likely causes, propose next checks. | Decide whether to change production settings. |
| rollback | Draft rollback steps and incident notes. | Approve rollback and notify stakeholders. |
| Client proposal | Turn the workflow into a small paid dry-run PoC offer. | Set price, sign agreement, and manage client expectations. |

## what a human must still do

The project should never imply that AI can fully replace account owners, admins, or client decision makers. A human must still:

- choose or approve the client workflow
- confirm that the task is legal and appropriate to automate
- create cloud and SaaS accounts
- create API keys and OAuth apps
- store secrets in `.env`, a secret manager, or the provider console
- approve folder, inbox, sheet, CRM, and webhook access
- check whether client data may be used
- approve messages before real sending
- approve billing
- approve go-live
- approve rollback
- accept or reject the paid dry-run PoC scope

## Beginner Flow

1. Read the README.
2. Open `docs/AI_AGENT_GRILL_ME_SKILL.md`.
3. Paste the skill into an AI agent.
4. Ask the AI to interview you one question at a time.
5. Choose one workflow, not many.
6. Identify the input source: inbox, form, LINE, spreadsheet, folder, webhook, or CRM.
7. Identify the output: draft reply, report, checklist, approval queue, local outbox, ticket, or spreadsheet row.
8. Identify the human approver.
9. Prepare fake or redacted sample data.
10. Run or plan a local dry-run.
11. Use `cloud-plan` only after local value is clear.
12. Offer a paid dry-run PoC only when scope, approval, and stop conditions are clear.

## Minimum Inputs For Automation

Every automation idea should answer these before implementation:

- Business pain: what problem happens repeatedly?
- Owner: who handles it today?
- Input: where does the request or file arrive?
- Output: what should be created?
- Approver: who must check it?
- Volume: how many items happen per week or month?
- Tools: which apps or services are involved?
- Data boundary: what must not be sent to AI?
- Production boundary: what must not run without approval?
- Success metric: what makes the PoC worth continuing?

## Good First Projects

Good first projects are small and visible:

- invoice follow-up draft queue
- missing document reminder queue
- support reply draft review
- daily inquiry summary
- appointment precheck list
- FAQ routing
- lead research brief
- weekly KPI report
- expense policy check

Avoid first projects that require high-risk decisions, regulated advice, large migrations, live customer sending, payment actions, or irreversible database writes.

## Stop Conditions

Stop and redesign when:

- there is no clear approver
- the client cannot provide sample data
- the workflow requires legal, medical, financial, or HR judgment
- the project needs real sending before dry-run evidence exists
- the cloud account owner is unknown
- the user wants to paste real secrets into chat
- the proposal promises guaranteed revenue or full automation

## Recommended AI Prompt

```text
Read the AI Beginner Support Map and interview me one question at a time.
Help me identify the workflow, input source, output, approval gate, missing accounts, API keys, reception folder, cloud account, rollback plan, and paid dry-run PoC boundary.
Do not ask for real secrets in chat.
```
