# Changelog

## Unreleased

### Recording-to-manual studio (2026-07)

- Added the local-first `manual-studio` workflow to create a guided workspace, inspect recordings, extract scene-change screenshots with FFmpeg, and ask Codex to produce an evidence-linked illustrated HTML draft.
- Spread screenshot candidates across the full recording while retaining meaningful scene changes, preventing early UI animation bursts from consuming the complete 40-frame budget.
- Added opt-in local speech transcription with whisper.cpp, verified multilingual model downloads, preserved user-edited transcripts, failure-safe staging, and source/model provenance.
- Added recording, transcript, and frame integrity checks; safe workspace-relative paths; bounded structured AI output; HTML escaping; read-only Codex analysis; and explicit human-review boundaries.
- Added separate Japanese and English browser guides plus generated review checklists, Mermaid workflow diagrams, open-question lists, and automation-candidate notes. Screenshot annotation, production actions, and external sending remain out of scope for this first stage.
- Added a one-question-at-a-time completion loop with provenance-bound answers, explicit deferral, AI regeneration without unsupported guessing, side-by-side review, and approval-recorded promotion into `06_APPROVED_MANUAL`.
- Added a secure localhost image picker that shows every verified candidate frame for each recorded step, lets the operator replace weak AI selections, regenerates the draft manual without losing recorded answers, and keeps a bounded local selection history.

### One-paste beginner start (2026-07)

- Added `ai-automation-kit start`, which creates a safe working sample, browser start page, client-input boundary, AI handoff prompt, sales assets, and delivery evidence with no required options.
- Added `scripts/first_start.py` so a fresh clone can create an isolated local environment and the first project without API keys or a package-install step.
- Added separate Japanese and English browser guides, a one-line README entrance, overwrite protection, and release checks. External actions remain blocked and income is not guaranteed.
- Added double-click launchers for macOS and Windows, plain-language prompts that can be handed directly to Codex, automatic browser opening, and safe reopening of an already-created first project.
- Simplified the generated start screen to one recommended next action while retaining the deeper demo and sales materials as optional links.

### Autopilot readiness design (2026-07)

- Implemented the local-only `autopilot-proof-lab` command and browser UI for historical replay, seven required shadow-case classes, 11 hard readiness gates, tamper-evident audit verification, stale-decision detection, and 14 bilingual review artifacts under `05_REPORTS/`.
- Added Japanese and English beginner manuals plus a privacy-safe runnable example. All readiness results remain advisory and never activate external actions or remove the current human approval boundary.
- Added a human-first Japanese design and an English technical design for assessing whether any of the 22 office packs can progress from assisted drafting to shadow mode, conditional automation, or an evidence-backed `not_ready` decision.
- Defined hard readiness gates, one-question-at-a-time discovery, rule confirmation, gap remediation, shadow comparison, honest refusal, generated delivery artifacts, and a separate trust boundary for any future external-action runtime.
- Added a complete human-first English design with the same readiness levels, refusal rules, shadow-test minimums, decision expiration, and current-product approval boundaries as the Japanese design.

### Control workflow manuals and research (2026-07)

- Added `docs/control-workflows.ja.html` and `docs/control-workflows.html`: separate Japanese and English beginner manuals for six daily control packs: `spreadsheet-reconciliation-daily`, `policy-change-impact-daily`, `quality-incident-capa-daily`, `vendor-onboarding-daily`, `access-review-daily`, and `grant-packet-daily`.
- Added `docs/research/OFFICE_CONTROL_AUTOMATION_RESEARCH_2026-07.md` with July 2026 selection evidence, public links, X research signal labeled anecdotal, GitHub pattern snapshot, license notes, no-vendoring/no-dependency-adoption notes, risks, and rejected high-liability ideas.
- Linked the new manuals from `README.md`, `START_WITH_CODEX.md`, `START_WITH_CODEX.ja.md`, and `docs/INDEX.md`.
- Updated the public office-workspace status from one monthly pack plus 15 daily packs to one monthly pack plus 21 daily packs.
- Stated explicitly that email automation is out of scope and that the control packs create local drafts for human review, not full automation.

### Work relief workflow manuals (2026-07)

- Added `docs/work-relief-workflows.ja.html` and `docs/work-relief-workflows.html`: separate Japanese and English manuals for five email-free packs covering install and login, pack choice, exact folder inputs, localhost UI workflow, AI questions, draft review, PIN approval, next-day reuse, trusted prior outputs, troubleshooting, safety boundaries, and a bounded side-business delivery route.
- Linked the new manuals from `README.md`, `START_WITH_CODEX.md`, `START_WITH_CODEX.ja.md`, and `docs/INDEX.md`.
- Stated explicitly that Gmail and email automation are out of scope for these packs and will be handled as a separate project.

### Daily office workflow packs (2026-07)

- Expanded the hardened monthly office workspace into a cadence-aware pack system while preserving the existing monthly default.
- Added ten daily packs in a guided order: inquiries, sales, finance, projects, attendance, meeting actions, expenses, invoice/order checks, internal requests, and executive digest.
- Added strict real-date validation, pack selection and first-period creation in the browser UI and CLI, local draft/PIN approval coverage for every pack, and cleanup of failed first-period setup.
- Added separate Japanese and English beginner HTML guides plus installed-wheel checks for the pack catalog, packaged resources, daily creation, invalid dates, and monthly compatibility.
- Made daily reuse operational rather than metadata-only: a confirmed prior approved output is hash-verified again at run start, copied into the next Codex input snapshot, shown in the UI, and covered by next-day end-to-end tests. The UI now suggests the next calendar date and selects approved-style reuse by default.
- Rebuilt the English daily-workflow manual as a complete beginner operating guide covering installation, all ten packs, folder placement, UI operation, next-day reuse, trusted-example checks, troubleshooting, approval boundaries, and a bounded side-business delivery route; linked it from the documentation index and added release assertions for required content.

### Office workspace public release integration (2026-07)

- Published `docs/office-workspace.ja.html` and `docs/office-workspace.html`: separate Japanese and English monthly office workspace manuals with install/login, ask Codex setup, folder map, three file types, inspect, answer, generate, cancel/retry, approve, rollover, local/AI/human boundaries, troubleshooting, and matching `START_WITH_CODEX` links.
- Surfaced the Phase 1A monthly office workspace route in `README.md` and `docs/INDEX.md`, with honest scope notes that it is monthly-report only, local-only, and macOS or Linux only for workspace mutation.
- Extended public release audit and release smoke to require the office-workspace manuals, `START_WITH_CODEX.md`, `START_WITH_CODEX.ja.md`, `AGENTS.md`, bundled monthly-report pack resources, and an installed-wheel office-workspace flow that verifies the approved hash and localhost server lifecycle.

### Report wizard public release integration (2026-07)

- Added public navigation for the resumable `report-wizard` workflow across `README.md`, `docs/INDEX.md`, `docs/USER_MANUAL.md`, `docs/USER_MANUAL.ja.md`, `docs/manual.html`, and `docs/manual.ja.html`, with language-separated links to `docs/report-automation-wizard.html` and `docs/report-automation-wizard.ja.html`.
- Added short `report-wizard` handoff pointers to `docs/REPORT_AUTOMATION_GUIDE.md` and `docs/REPORT_AUTOMATION_GUIDE.ja.md` so the conceptual folder-based offer and the step-by-step local review flow stay separate.
- Expanded public release audit and release smoke coverage for the report wizard state, source manifest, schema proposal, provenance, AI review instructions, question session, draft, approval hash, and localhost server lifecycle.

### Beginner side-business overhaul (2026-07)

- Added `beginner` command: a Japanese 5-stage navigator (environment setup, first demo, sales preparation, first client project, delivery and invoicing) so beginners always know the next step toward their first paid project.
- Added `flows diagram <flow_id>` and automatic `flow_diagram.html` generation on `flows install`: a client-facing, single-file Japanese HTML diagram of the automation flow with step cards, human-approval badges, before/after comparison, and safety notes (no CDN, printable).
- Strengthened `doctor` with a `package_installed` check and Japanese remediation guidance for failed checks.
- Restructured documentation entrances: rewrote `README.md` around a 3-step start, added `docs/GETTING_STARTED.ja.md` (single entry point) and `docs/INDEX.md` (categorized index), and moved 28 legacy documents to `docs/archive/` with all internal links repaired.
- Rewrote the Japanese sales templates in `beginner-sales` and `offer-pack` to real-negotiation quality: price range guidance, read-aloud hearing questions, and a fill-in proposal letter with scope, schedule, and disclaimer (API and file names unchanged).
- Added `docs/TUTORIAL_SME_PROPOSAL.ja.md`: an end-to-end tutorial for the SME automation-proposal side business (finding clients, hearing, demo, proposal, execution, delivery, invoicing) with real command outputs.
- Added `docs/AI_PROMPTS.ja.md`: copy-paste prompts for finishing generated assets with an AI assistant.
- Rewrote `docs/USER_MANUAL.ja.md` / `docs/USER_MANUAL.md` and rebuilt `docs/manual.ja.html` / `docs/manual.html`: full command walkthroughs with real outputs and system-overview, 5-stage roadmap, and project-flow diagrams (Mermaid in Markdown, dependency-free CSS diagrams in HTML).

- Added `flow-export` starters for `n8n`, `Activepieces`, and `Windmill` so a local dry-run workflow can move into a real execution tool without rebuilding the flow from scratch.
- Added `deployment-pack` starters for `Coolify`, `Cloudflare Agents`, and `Supabase` so operators can generate practical deployment files after the cloud planning phase.
- Added `runtime-safety`, `secrets-bootstrap`, `document-intake`, `observability-pack`, and `state-backend` so teams can generate approval policy, retry and rollback rules, secret ownership, document conversion paths, Langfuse-style tracing, and lightweight approval history storage.
- Added English and Japanese guides for execution bridges and operations expansion, plus manual updates so beginners can understand how to move from local dry-run to a safer production path.
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
- Added beginner support map, setup assistant playbook, and client delivery runbook so AI agents can guide users through intake, connectors, cloud setup, troubleshooting, client delivery, go-live gates, rollback, and monthly operation without collecting secrets in chat.
- Added English manuals matching the Japanese business proposal docs: user manual, selling guide, flow selection guide, client demo script, real-world setup guide, and FAQ.
- Added AI reception employee flows and setup artifacts so beginners can see required API keys, reception folders, sample data, operator UI, approval ownership, and paid dry-run PoC boundaries before client delivery.
- Added AI employee roadmap, AI action procedures, internal FAQ/admin flows, and sales research flows based on the report's recommended expansion order.
- Added side-business starter 10 and before/after demo outputs to the complete workspace.
- Added `docs/SIDE_HUSTLE_MARKET_UPDATE_2026.ja.md`: a research-backed Japanese market update that turns current GitHub signals from n8n, Dify, browser-use, Activepieces, Skyvern, MCP servers, and GitHub MCP Server into five sellable beginner-safe side-hustle offers.
- Added `report-automation` and the `daily-monthly-report-automation` flow: a folder-based daily/weekly/monthly report drafting pack with past completed reports, current materials, GrillMe-style missing-information questions, local drafts, human approval, and bilingual guides.
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
