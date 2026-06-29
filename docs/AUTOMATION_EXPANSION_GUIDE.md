# Automation Expansion Guide

This guide explains the expanded business automation packs inspired by public patterns from OpenAI, Anthropic, n8n, Activepieces, Windmill, Dify, Flowise, CrewAI, GitHub Actions, and related open-source automation projects.

The goal is not to copy those projects. The goal is to learn useful structures and turn them into beginner-friendly delivery packs for small business automation work.

## Start With The Command Center

```bash
ai-automation-kit command-center --language both --output .tmp/command-center
```

Open:

- `START_HERE_COMMAND_CENTER.md`
- `COMMAND_CENTER.md`
- `COMMAND_CENTER.ja.md`
- `command_center.html`
- `next_step_decision_tree.md`

Use this when the project feels too large and you need a clear next step.

## The 12 Expansion Packs

| Pack | Command | Inspired by | Use it when |
|---|---|---|---|
| AI agent skill pack | `skill-pack` | Anthropic Skills, Codex skills, Cursor rules | You want to give an AI agent reusable instructions. |
| Human approval gate | `approval-gate` | OpenAI guardrails and human-in-the-loop patterns | You need to separate drafts from real-world actions. |
| MCP connector plan | `mcp-connector-plan` | OpenAI/Anthropic MCP connector patterns | You need Gmail, Sheets, Slack, Drive, LINE, or webhook setup guidance. |
| Agent team roles | `agent-team` | Claude subagents and CrewAI-style teams | You want roles for sales, intake, build, QA, and delivery. |
| Evaluation loop | `eval-loop` | OpenAI and Anthropic eval practices | You need to measure whether the automation actually helps. |
| Workflow explainer | `workflow-explainer` | n8n, Flowise, Windmill visual workflows | You need a client-friendly before/after explanation. |
| Self-host pack | `self-host-pack` | n8n self-host kits and Docker runbooks | You need deployment, rollback, and operations planning. |
| Connector catalog | `connector-catalog` | Activepieces pieces, n8n integrations, MCP catalogs | You need to choose practical connector pieces. |
| Script UI pack | `script-ui-pack` | Windmill script-to-UI patterns | You want to turn scripts into forms, jobs, webhooks, or dashboards. |
| Knowledge RAG pack | `knowledge-rag-pack` | Dify, Flowise, docs RAG patterns | You want internal FAQ or document Q&A with source rules. |
| Automation hooks | `automation-hooks` | Claude Code hooks and CI checks | You want automatic checks before sharing or deployment. |
| Governance pack | `governance-pack` | GitHub Actions and enterprise governance | You need security, audit, incident, and monthly review rules. |

## Recommended Beginner Path

1. `command-center`
2. `side-hustle-blueprints`
3. `skill-pack`
4. `approval-gate`
5. `mcp-connector-plan`
6. `workflow-explainer`
7. `eval-loop`
8. `governance-pack`

This keeps the work practical: choose an offer, prepare an AI agent, define approval boundaries, plan connectors, explain the workflow, measure value, and add governance.

## Safety Rule

AI can draft, classify, summarize, explain, and prepare. A responsible human approves customer-facing sends, booking confirmation, price changes, refunds, legal or regulated decisions, production connector changes, cloud billing, and public claims.

