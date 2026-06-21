# Changelog

## Unreleased

- Added `complete-workspace` to generate a ready-to-review local delivery folder in one command.
- Added final delivery guide, completion checklist, connector report, client report, demo site, and demo zip packaging to the operator workflow.
- Added revenue readiness scoring, sales closing script, paid PoC scope, and value measurement sheet to the complete workspace.
- Added pre-contract checklist, proposal email, first 30 days plan, and proof-of-value template to reduce gaps between demo, paid PoC, and measurable follow-through.
- Added OSS pattern benchmark, integration backlog, deployment options, and production observability plan to align generated workspaces with public automation patterns from n8n, Activepieces, Windmill, and Trigger.dev-style systems.
- Added automation opportunity scorecard, client onboarding form, and go-live decision gate to close the gap between sales discovery, client approval, and production readiness.
- Added a browser-friendly client command center so non-technical users can navigate the generated delivery workspace without guessing which file to open first.
- Added `opportunity-catalog`, `recommend-flow`, and `share-check` so users can choose sellable work, turn client pain into a recommended flow, and review generated files before sharing.
- Added `business-launch` and `business_launch/` complete-workspace outputs so AI beginners can create a target industry playbook, first client offer, discovery script, proposal builder, pricing menu, risk boundary sheet, 30-day launch plan, and pitch email for enterprise automation proposals.
- Added `guided-setup` to generate beginner/operator/client intake questions, local and cloud setup plans, environment-value explanations, client request lists, AI-agent instructions, and readiness scoring before real automation setup.
- Added `guided-review` to turn completed setup answers into a readiness report, build plan, client missing-items email, cloud decision guide, AI handoff prompt, and next CLI commands.
- Added `cloud-plan` for Google Cloud, AWS, Azure, Render, Railway, Vercel, DigitalOcean, and Fly.io deployment planning across webhook/API, scheduled job, worker queue, web app, static functions, and container service workloads with connector-aware secrets, runtime choice, network/domain, operations, cost, compliance, rollback, and human approval files.
- Added beginner-focused cloud manuals so AI beginners can understand what to prepare, what AI can do, what humans must approve, how connectors such as Gmail, Google Sheets, Slack, and LINE fit, and how to troubleshoot deployment, secrets, webhooks, schedulers, queues, and rollback.
- Added `grill-me` and bilingual Grill Me guides/prompts/checklists so AI beginners can ask an AI agent to interview them one question at a time, challenge vague answers, avoid secrets in chat, and move toward a safe dry-run and bounded paid PoC.
- Repositioned Grill Me as a reusable AI agent skill that works in ChatGPT, Claude, Gemini, Cursor, Codex, Claude Code, or other assistants without requiring a CLI-based AI agent.
- Added English manuals matching the Japanese business proposal docs: user manual, selling guide, flow selection guide, client demo script, real-world setup guide, and FAQ.
- Added AI reception employee flows and setup artifacts so beginners can see required API keys, reception folders, sample data, operator UI, approval ownership, and paid dry-run PoC boundaries before client delivery.
- Added AI employee roadmap, AI action procedures, internal FAQ/admin flows, and sales research flows based on the report's recommended expansion order.
- Added side-business starter 10 and before/after demo outputs to the complete workspace.
- Updated CI to use minimal read permissions and Node 24-compatible GitHub Actions.
- Added Dependabot coverage for non-major GitHub Actions and Python packaging updates.
- Removed local absolute paths from checked-in research examples.
- Fixed CI release smoke setup by installing `pytest` before running the smoke suite.
- Added public release audit coverage for local `/Users/` paths in public examples and docs.
- Hardened public release audit checks for GitHub publishing readiness.

## 0.1.0 - 2026-06-17

- Added five executable starter templates:
  - `research-agent`
  - `docs-rag`
  - `internal-ai-workflow`
  - `excel-to-internal-app`
  - `delivery-pipeline`
- Added run/source/artifact core records.
- Added safe fetch defaults for explicit URLs and local files.
- Added checked-in examples and expected outputs.
- Added one-command demo runner.
- Added public-readiness docs and CI workflow.
