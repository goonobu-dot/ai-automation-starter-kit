# Cloud Deployment Guide

This guide helps people who are new to AI and cloud deployment move from a local automation demo to a safe cloud deployment plan for a small business automation PoC.

You do not need to understand all cloud services first. You need to know what business process you want to improve, what input arrives, where the output should go, who must approve it, and which parts must stay human-controlled.

## What The AI Can Do

- Help choose a workflow.
- Generate a local dry-run workspace.
- Create setup questions for the operator or client.
- Create a `cloud-plan` for a provider, workload, and connector set.
- Write command examples, secret checklists, rollback steps, and review notes.
- Produce an AI agent handoff prompt for Claude Code, Codex, Cursor, or another coding agent.

## What Needs Human Approval

- Cloud account login.
- Billing and budget alerts.
- Real API keys, OAuth grants, webhook URLs, domains, and secrets.
- Data boundary decisions for client information.
- Enabling production traffic, scheduler jobs, queues, or webhooks.
- Rollback ownership and incident response.

## Recommended Beginner Path

1. Pick a simple business workflow with `flows list`.
2. Generate a local workspace with `complete-workspace`.
3. Run dry-run output and review the work queue, draft output, and approval queue.
4. Show the client a no-send demo.
5. Use `guided-setup` to collect required inputs.
6. Use `guided-review` to find missing inputs.
7. Use `cloud-plan` to create deployment documents.
8. Use `deployment-pack` if you want a starter for `Coolify`, `Cloudflare Agents`, or `Supabase`.
9. Use `runtime-safety`, `secrets-bootstrap`, `observability-pack`, and `state-backend` before production.
10. Let a human approve account, billing, secrets, IAM, domain, webhook, scheduler, queue, and rollback steps.
11. Test with one safe event.
12. Decide continue, revise, or stop.

## Example Commands

```bash
ai-automation-kit complete-workspace \
  --flow-id invoice-document-followup \
  --client-type local-business \
  --niche accounting \
  --output .tmp/client-demo
```

```bash
ai-automation-kit cloud-plan \
  --flow-id invoice-document-followup \
  --provider aws \
  --workload scheduled-job \
  --connectors gmail,google-sheets \
  --output .tmp/cloud-plan
```

```bash
ai-automation-kit deployment-pack \
  --flow-id invoice-document-followup \
  --provider coolify \
  --connectors gmail,google-sheets \
  --output .tmp/deployment-coolify
```

```bash
ai-automation-kit runtime-safety --flow-id invoice-document-followup --output .tmp/runtime-safety
ai-automation-kit secrets-bootstrap --flow-id invoice-document-followup --provider infisical --connectors gmail,google-sheets --output .tmp/secrets-bootstrap
ai-automation-kit observability-pack --flow-id invoice-document-followup --output .tmp/observability-pack
ai-automation-kit state-backend --flow-id invoice-document-followup --backend supabase --output .tmp/state-backend
```

## Workload Choices

`webhook-api` is for inbound HTTP events such as forms, LINE, Slack, or external systems.

`scheduled-job` is for daily, weekly, or monthly automation such as invoice follow-up, reminders, reporting, and inventory checks.

`worker-queue` is for retryable backlog processing.

`web-app` is for an operator UI, approval screen, or client-facing demo.

`static-functions` is for a lightweight page plus small API handlers.

`container-service` is for long-running services or custom runtimes.

## Provider Choices

Render, Railway, and Vercel are easier for a first paid PoC.

Google Cloud fits Gmail, Google Sheets, Google Drive, and Google-heavy clients.

AWS fits companies that already use AWS and need Lambda, EventBridge, SQS, Secrets Manager, or CloudWatch.

Azure fits Microsoft 365, Teams, SharePoint, Entra ID, and enterprise IT environments.

Fly.io, DigitalOcean, and Render are useful when a Docker/container path is easier to explain or deploy.

## AI Agent Handoff Prompt

```text
Please inspect this GitHub project: ai-automation-starter-kit.
I am new to AI agents, but I want to offer a small business automation PoC safely.

Read README.md, docs/CLOUD_DEPLOYMENT_GUIDE.md, docs/CLOUD_BEGINNER_PLAYBOOK.md, and docs/CONNECTOR_SETUP_GUIDE.md.

Then guide me step by step through required inputs, missing information, local dry-run, cloud-plan, and client approval items.

Do not ask me to paste real API keys or secrets into chat.
Keep production traffic, real webhooks, schedulers, and queues blocked until human approval is explicit.
```

## Client Explanation

Do not promise full automation at the start. Say this instead:

“First we create a dry-run PoC that does not send real production messages. It reads sample input, creates draft output or a work queue, and keeps human approval in the process. If the value is clear, we prepare a cloud plan with cost, secrets, permissions, logging, and rollback before enabling real traffic.”

That is a realistic and safer way for beginners to start.
