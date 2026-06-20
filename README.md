# AI Automation Starter Kit

GitHub-data-driven AI automation starter kit for developers, AI agent builders, and automation consultants.

It finds promising public OSS projects for a business area, ranks them, and turns the result into practical adoption artifacts: executive decisions, value scorecards, rollout maps, risk registers, audit plans, dry-run adapter starters, client-ready offer packs, and full sales-to-delivery automation packs.

## What Is This?

AI Automation Starter Kit is a local Python CLI for turning public GitHub signals into repeatable business automation plans.

Instead of stopping at "this repository looks interesting", it creates the files a team needs before trying automation in a real company:

- what to try first
- why it is worth trying
- what blocks production use
- who must approve the pilot
- how to measure whether it worked
- how to keep the first prototype in dry-run mode
- how to turn a safe pilot into a responsible consulting or freelance offer

The project also includes five reusable workflow templates for research, document Q&A, approved replies, spreadsheet-to-app migration, and delivery packaging.

For monetization work, `offer-pack` creates proposal assets, `client-ready` creates the deeper sales-to-delivery pack, and `beginner-sales` creates the first side-business operating pack: visual flow gallery, selected-flow demo, proposal one-pager, pitch script, client questions, ROI calculator, price menu, outreach copy, objection handling, 3-day PoC plan, and delivery checklist.

For the easiest hands-on path, `complete-workspace` creates the full local delivery folder in one command: quickstart workspace, dry-run execution, approval export, connector check, client report, demo site, shareable demo zip, and final checklist. `quickstart` remains useful when you want only the workspace, while `install-bundle`, `client-report`, `connector-doctor`, and `package-client-demo` are available as separate steps.

For hands-on automation work, `flows` gives users a research-backed catalog of 60+ ready-made business automation flows. A user can choose a flow by industry or genre, install it into a local project folder, inspect `flow.yaml`, view `workflow_map.mmd`, and run the local automation runtime to generate a work queue, draft outputs, an approval queue, connector tasks, a status report, and a run log. The installed project also includes `.env.example`, `config/connectors.json`, a system runbook, approval scripts, and local outbox files so the flow can become a real integration project without sending anything by accident. See [Automation Demand Research](docs/AUTOMATION_DEMAND_RESEARCH.md) for the industry and workflow demand map behind the catalog.

## Beginner-Friendly Guides

New to this project? Start with a plain-language explanation:

- [English beginner guide](docs/BEGINNER_GUIDE.md)
- [日本語のやさしい解説](docs/BEGINNER_GUIDE.ja.md)

Need a practical first path or use-case examples?

- [Start Here](docs/START_HERE.md)
- [まずここから](docs/START_HERE.ja.md)
- [日本語の使い方マニュアル](docs/USER_MANUAL.ja.md)
- [業務自動化を企業へ提案するガイド](docs/SELLING_AUTOMATION_GUIDE.ja.md)
- [フロー選択ガイド](docs/FLOW_SELECTION_GUIDE.ja.md)
- [顧客デモ台本](docs/CLIENT_DEMO_SCRIPT.ja.md)
- [実運用セットアップガイド](docs/REAL_WORLD_SETUP_GUIDE.ja.md)
- [FAQ](docs/FAQ.ja.md)
- [Use Cases](docs/USE_CASES.md)
- [ユースケース](docs/USE_CASES.ja.md)

## Who Is This For?

- Developers who want a useful open-source automation project they can run locally.
- AI agent builders who need repeatable workflow artifacts instead of one-off chat output.
- Automation consultants who want to turn GitHub research into client-ready pilot plans.
- Business operations teams that need approvals, audit evidence, and value metrics before adopting AI automation.

## What You Get

The easiest first command is `onboard`. It checks the local environment, runs GitHub discovery, and writes a short onboarding summary that tells you what to read next.

The main `github-discover` workflow generates a practical output folder. The first files to read are:

| File | Why it matters |
|---|---|
| `run_summary.md` | Short status, candidate count, and next file to read. |
| `executive_decision_brief.md` | Buy, wait, or recovery recommendation with risks and approval request. |
| `pilot_scorecard.csv` | Spreadsheet-ready baseline and pilot metrics. |
| `value_realization_plan.md` | KPI hypotheses, rollout phases, and go/no-go criteria. |
| `stakeholder_rollout_map.md` | Owners, approvers, cadence, and escalation rules. |
| `risk_exception_register.md` | Open risks, owners, evidence needed, and stop conditions. |
| `operational_audit_plan.md` | Audit scope and required evidence before promotion. |
| `adapter_starter/` | Runnable dry-run adapter skeleton when a safe candidate exists. |
| `offer_pack/` | Client-facing proposal, service catalog, SOW, pricing model, demo script, outreach copy, and risk boundaries. |
| `client-ready/` | Intake, ROI calculator, proposal tiers, readiness score, tool selection, security review, maintenance plan, marketplace profile, and case-study templates. |
| `beginner-sales/` | Beginner-friendly side-business pack for choosing a flow, showing the client what it does, estimating ROI, pitching, scoping a 3-day PoC, and delivering safely. |
| `quickstart/` | One complete local workspace with flow project, sales pack, and demo site. |
| `client-report/` | Client-readable report generated from dry-run output files. |
| `client-demo-package.zip` | Shareable demo package manifest and zip for review, after checking secrets. |
| `FINAL_DELIVERY_GUIDE.md` | One-page final handoff guide for reviewing the generated workspace with a client. |
| `completion_checklist.md` | Confirmed evidence list for dry-run execution, approvals, connector review, report, demo, and package. |

## 1-Minute Demo

Use this first when you want to discover business automation opportunities from public GitHub projects and turn them into a practical next-step plan:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m ensurepip --upgrade
python3 -m pip install --upgrade pip setuptools
python3 -m pip install -e .
ai-automation-kit doctor --output .tmp/doctor
ai-automation-kit complete-workspace --flow-id invoice-document-followup --client-type local-business --niche accounting --output .tmp/complete-accounting
```

Open the final delivery guide:

```bash
sed -n '1,180p' .tmp/complete-accounting/FINAL_DELIVERY_GUIDE.md
```

Open the browser-friendly demo site:

```bash
open .tmp/complete-accounting/demo_site/index.html
```

Open the client-ready offer pack when you want to turn the research into a small paid automation pilot:

```bash
sed -n '1,180p' .tmp/onboarding/offer_pack/README.md
```

Generate the deeper sales-to-delivery pack when you want to package the work for a specific niche:

```bash
ai-automation-kit client-ready --business-area operations --client-type local-business --niche accounting --source-output .tmp/onboarding --output .tmp/client-ready
```

Generate the beginner side-business pack when you want a visual, client-explainable offer around one concrete flow:

```bash
ai-automation-kit beginner-sales --flow-id invoice-document-followup --client-type local-business --niche accounting --output .tmp/beginner-sales
```

Choose and install a local automation-flow scaffold when you want to turn an idea into a concrete project folder:

```bash
ai-automation-kit flows list
ai-automation-kit flows list --industry finance
ai-automation-kit flows show invoice-document-followup
ai-automation-kit flows install invoice-document-followup --output .tmp/flow-invoice-document-followup
ai-automation-kit flows validate .tmp/flow-invoice-document-followup
ai-automation-kit flows run .tmp/flow-invoice-document-followup
ai-automation-kit flows approve .tmp/flow-invoice-document-followup --approver owner@example.com
```

## 3-Minute Walkthrough

After the first run, read these in order:

1. `run_summary.md` to see whether the run found a ready candidate, a manual-review candidate, or needs better search terms.
2. `executive_decision_brief.md` to decide whether to approve a controlled pilot, hold for manual review, or rerun discovery.
3. `pilot_scorecard.csv` to see which baseline and pilot metrics the team should track.
4. `artifact_index.md` to explore every generated artifact and decide what to inspect next.

If `next_read` points to `adapter_starter/README.md`, the kit generated a dry-run adapter starter. If it points to `manual_review_pack.md`, inspect license, maintenance, and examples before reuse. If it points to `query_recovery.md`, broaden the GitHub search before planning implementation.

### Example Output

The plan tells you:

- which GitHub repositories are worth reviewing first
- which candidates need license or maintenance review
- which starter-kit template to use next
- how to run a dry-run prototype
- which success metrics prove the automation is actually useful
- which candidates are ready for a 30-day adapter prototype
- which risks block production use until review
- which client-facing documents can support a scoped paid pilot

Example generated files:

- `.tmp/operations-discovery/report.md`
- `.tmp/operations-discovery/artifact_index.md`
- `.tmp/operations-discovery/github_candidates.md`
- `.tmp/operations-discovery/adapter_blueprint.md`
- `.tmp/operations-discovery/adapter_starter/`
- `.tmp/operations-discovery/business_automation_plan.md`
- `.tmp/operations-discovery/business_automation_summary.json`
- `.tmp/onboarding/offer_pack/proposal.md`
- `.tmp/onboarding/offer_pack/statement_of_work.md`
- `.tmp/client-ready/roi_calculator.csv`
- `.tmp/client-ready/implementation_readiness_score.json`
- `.tmp/client-ready/maintenance_plan.md`
- `.tmp/beginner-sales/START_HERE_FOR_SIDE_BUSINESS.md`
- `.tmp/beginner-sales/flow_gallery.html`
- `.tmp/beginner-sales/selected_flow_demo.html`
- `.tmp/beginner-sales/proposal_one_pager.md`
- `.tmp/beginner-sales/three_day_poc_plan.md`
- `.tmp/complete-accounting/FINAL_DELIVERY_GUIDE.md`
- `.tmp/complete-accounting/completion_checklist.md`
- `.tmp/complete-accounting/client_demo_package/client_demo_package.zip`
- `.tmp/quickstart-accounting/START_HERE.md`
- `.tmp/quickstart-accounting/demo_site/index.html`
- `.tmp/client-report/client_report.md`
- `.tmp/client-demo-package/client_demo_package.zip`
- `.tmp/flow-invoice-document-followup/flow.yaml`
- `.tmp/flow-invoice-document-followup/workflow_map.mmd`
- `.tmp/flow-invoice-document-followup/scripts/run_dry_run.py`
- `.tmp/flow-invoice-document-followup/config/connectors.json`
- `.tmp/flow-invoice-document-followup/automation_output/draft_outputs.md`
- `.tmp/flow-invoice-document-followup/automation_output/approval_queue.csv`
- `.tmp/flow-invoice-document-followup/local_outbox/email_drafts.md`

## Example Use Cases

- Operations: find workflow orchestration projects and turn them into controlled internal pilots.
- Support: discover helpdesk, chatbot, and ticket automation ideas with human review gates.
- Finance: review invoice, expense, and spreadsheet automation candidates before touching real data.
- Sales: identify CRM and outreach automation patterns without copying unsafe code.
- HR: explore onboarding or recruiting workflow ideas with approval and audit requirements.
- Marketing: turn content and campaign automation repositories into measurable pilot plans.
- Freelance/consulting: turn discovery results into a bounded automation audit, dry-run prototype, proposal, statement of work, and maintenance offer. The kit does not guarantee income; it helps package the work responsibly.
- Client-ready delivery: turn an automation idea into intake, ROI, pricing, security, tool selection, outreach, handoff, case-study, and monthly maintenance assets.
- Beginner side-business path: choose one visible flow, explain it with `selected_flow_demo.html`, ask discovery questions, estimate ROI, send a one-page proposal, and deliver a 3-day dry-run PoC without touching production systems.
- Flow installer: choose a concrete workflow from 60+ researched patterns across finance, support, sales, HR, operations, healthcare, real estate, legal, ecommerce, education, manufacturing, hospitality, field service, IT, and marketing, then install a local dry-run project scaffold.

## How This Differs From Chat AI

Normal chat AI answers one prompt at a time. This kit makes the workflow repeatable:

- explicit input configs
- saved outputs
- run history
- source maps and citations
- dry-run approval records
- placeholder-only delivery assets
- tests that prove each template still works

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m ensurepip --upgrade
python3 -m pip install --upgrade pip setuptools
python3 -m pip install -e .
ai-automation-kit --version
ai-automation-kit doctor --output .tmp/doctor
python3 -m pytest -q
python3 scripts/run_all_demos.py
```

The demo outputs are written to `.tmp/all-templates/`. To run the guided GitHub onboarding path after setup:

```bash
ai-automation-kit onboard --business-area operations --limit 2 --output .tmp/onboarding
```

## How This Fits With Local Agent Workbenches

This project pairs well with:

- `goonobu-dot/local-agent-workbench`
- `goonobu-dot/claude-code-workbench`

The workbenches give you a local multi-agent cockpit for parallel Codex CLI or Claude Code sessions. This starter kit gives those agents a repeatable business automation path:

1. Discover automation candidates from GitHub.
2. Research candidate projects with citations.
3. Answer internal questions from docs.
4. Draft approved replies or handoffs.
5. Convert spreadsheets into internal app schemas.
6. Package the workflow for delivery with metrics and safety checks.

## Template Commands

### onboard

Run this first when you want the shortest path from install to a usable business automation discovery result:

```bash
ai-automation-kit onboard --business-area operations --limit 2 --output .tmp/onboarding --create-offer-pack
```

Creates `doctor/doctor_report.md`, `github_discover_config.json`, `onboarding_summary.md`, `onboarding_summary.json`, optional `offer_pack/`, and the normal GitHub discovery artifacts. The summary prints and records the first files to read, recommended next actions, and the exact rerun command.

### offer-pack

Generate a client-ready offer pack from an existing discovery output folder:

```bash
ai-automation-kit offer-pack --business-area operations --client-type small-business --source-output .tmp/onboarding --output .tmp/offer-pack
```

Creates `README.md`, `service_catalog.md`, `client_discovery_questions.md`, `proposal.md`, `statement_of_work.md`, `pricing_model.md`, `demo_script.md`, `outreach_messages.md`, `delivery_checklist.md`, `risk_boundaries.md`, and `offer_pack.json`. These files are designed for scoped automation consulting or freelance pilots. They include risk boundaries and avoid income guarantees.

### client-ready

Generate the full sales-to-delivery pack for a specific niche:

```bash
ai-automation-kit client-ready --business-area operations --client-type local-business --niche accounting --source-output .tmp/onboarding --output .tmp/client-ready
```

Creates `client_intake.md`, `client_intake.json`, `roi_calculator.csv`, `pricing_recommendation.md`, `proposal_tiers.md`, `implementation_readiness_score.json`, `security_review.md`, `prompt_injection_checklist.md`, `approval_map.md`, `data_classification.md`, `tool_stack_recommendation.md`, `maintenance_plan.md`, `retainer_offer.md`, `monthly_review.md`, `case_study_template.md`, `before_after_report.md`, `marketplace_profile.md`, `outreach_sequence.md`, `handoff_training.md`, `tool_comparison.md`, `template_adaptation_guide.md`, `compliance_boundaries.md`, `niche_playbook.md`, `connector_blueprints.md`, `demo_inputs.csv`, and `client_ready.json`.

This is the strongest monetization-oriented command. It still does not guarantee income; it gives a user the practical assets needed to sell, scope, deliver, and maintain a small automation pilot responsibly.

### beginner-sales

Generate a beginner-friendly side-business pack for one concrete flow:

```bash
ai-automation-kit beginner-sales --flow-id invoice-document-followup --client-type local-business --niche accounting --output .tmp/beginner-sales
```

Creates `START_HERE_FOR_SIDE_BUSINESS.md`, `flow_gallery.html`, `selected_flow_demo.html`, `proposal_one_pager.md`, `beginner_pitch_script.md`, `client_questions.md`, `roi_simple_calculator.csv`, `three_day_poc_plan.md`, `price_menu.md`, `outreach_messages.md`, `objection_handling.md`, `demo_walkthrough.md`, `client_delivery_checklist.md`, `positioning.md`, `differentiation_matrix.md`, and `beginner_sales.json`.

This is the shortest route for a new AI-agent user who wants to show a company what can be automated. It is deliberately visual and client-facing: pick one flow, explain the before/after, estimate value, run a dry PoC, and keep human approval before real-world actions.

### quickstart

Create the fastest beginner workspace: runnable flow, sales materials, and demo site in one folder.

```bash
ai-automation-kit quickstart --flow-id invoice-document-followup --client-type local-business --niche accounting --output .tmp/quickstart-accounting
```

Creates `START_HERE.md`, `quickstart.json`, `flow_project/`, `beginner_sales/`, and `demo_site/index.html`.

### complete-workspace

Create the full ready-to-review local delivery workspace in one command:

```bash
ai-automation-kit complete-workspace --flow-id invoice-document-followup --client-type local-business --niche accounting --output .tmp/complete-accounting
```

Creates `FINAL_DELIVERY_GUIDE.md`, `completion_checklist.md`, `delivery_manifest.json`, `quickstart/`, `connector_doctor/`, `client_report/`, `demo_site/index.html`, and `client_demo_package/client_demo_package.zip`. The command also runs the local dry-run flow and exports approval records. Real external sends and production changes remain disabled until the client approves credentials, data handling, rollback, and human approval rules.

### flow-guide

Choose a good first workflow by industry, genre, or niche:

```bash
ai-automation-kit flow-guide --industry finance --niche accounting --output .tmp/flow-guide
```

Creates `recommended_flows.md` and `recommended_flows.json`.

### install-bundle

Create a fuller client bundle with flow project, beginner sales materials, client-ready delivery assets, and demo site:

```bash
ai-automation-kit install-bundle --flow-id invoice-document-followup --client-type local-business --niche accounting --output .tmp/client-bundle
```

Creates `bundle_index.md`, `flow_project/`, `beginner_sales/`, `client_ready/`, and `demo_site/index.html`.

### demo-site

Turn an existing generated folder into a browser-friendly index:

```bash
ai-automation-kit demo-site --source .tmp/quickstart-accounting --output .tmp/quickstart-accounting/demo_site
```

Creates `index.html` and `demo_site.json`.

### connector-doctor

Check which local and future external connectors are ready or still need setup:

```bash
ai-automation-kit connector-doctor --project .tmp/quickstart-accounting/flow_project --output .tmp/connector-doctor
```

Creates `connector_doctor.md` and `connector_doctor.json`. Real external connectors remain disabled until credentials, data handling, approval owner, and rollback rules are defined.

### client-report

Turn a dry-run flow execution into a client-readable report:

```bash
ai-automation-kit client-report --flow-project .tmp/quickstart-accounting/flow_project --output .tmp/client-report
```

Creates `client_report.md`, `client_report.html`, and `client_report.json`.

### package-client-demo

Create a review package from generated demo materials:

```bash
ai-automation-kit package-client-demo --source .tmp/quickstart-accounting --output .tmp/client-demo-package
```

Creates `client_demo_manifest.json`, `README.md`, and `client_demo_package.zip`. Check for secrets or private client data before sharing.

### flows

List 60+ automation flows by industry or genre, inspect the steps, and install a local project scaffold:

```bash
ai-automation-kit flows list
ai-automation-kit flows list --industry finance
ai-automation-kit flows list --genre approval
ai-automation-kit flows show invoice-document-followup
ai-automation-kit flows install invoice-document-followup --output .tmp/flow-invoice-document-followup
ai-automation-kit flows validate .tmp/flow-invoice-document-followup
ai-automation-kit flows run .tmp/flow-invoice-document-followup
ai-automation-kit flows approve .tmp/flow-invoice-document-followup --approver owner@example.com
```

Installed flow projects include `README.md`, `.env.example`, `config/connectors.json`, `docs/SYSTEM_RUNBOOK.md`, `flow.yaml`, `flow.json`, `workflow_map.mmd`, `before_after_workflow.md`, `human_approval_points.md`, `sample_data/input.csv`, `scripts/run_automation.py`, `scripts/approve_all.py`, `scripts/run_dry_run.py`, and `tests/test_flow_contract.py`. Running the flow creates `automation_output/work_queue.csv`, `automation_output/draft_outputs.md`, `automation_output/approval_queue.csv`, `automation_output/connector_tasks.jsonl`, `automation_output/status_report.md`, and `automation_output/run_log.json`. Approving the flow creates `automation_output/approved_actions.csv`, `local_outbox/email_drafts.md`, and `local_outbox/slack_messages.md`. The runtime is local-first and dry-run only, so it does not send external messages, grant access, move money, approve hiring decisions, or update production systems.

### doctor

Run this first after install. It checks the local Python environment, output write access, Git availability, `.env` safety, and whether `GITHUB_TOKEN` is set.

```bash
ai-automation-kit doctor --output .tmp/doctor
```

For an optional live GitHub API check:

```bash
ai-automation-kit doctor --output .tmp/doctor --check-github
```

### github-discover

Start here when you want a one-command GitHub discovery workflow for business automation ideas:

```bash
ai-automation-kit github-discover --business-area sales --limit 5 --output .tmp/sales-automation-discovery
```

For operations automation discovery:

```bash
ai-automation-kit github-discover --business-area operations --limit 2 --output .tmp/operations-discovery
```

Creates `run_summary.md`, `run_summary.json`, `executive_decision_brief.md`, `executive_decision_brief.json`, `pilot_scorecard.md`, `pilot_scorecard.json`, `pilot_scorecard.csv`, `value_realization_plan.md`, `value_realization_plan.json`, `value_measurement_report.md`, `value_measurement_report.json`, `stakeholder_rollout_map.md`, `stakeholder_rollout_map.json`, `risk_exception_register.md`, `risk_exception_register.json`, `operational_audit_plan.md`, `operational_audit_plan.json`, `enterprise_readiness.md`, `enterprise_readiness.json`, `artifact_index.md`, `artifact_index.json`, `report.md`, `github_candidates.md`, `github_candidates.csv`, `github_candidates.json`, `adoption_shortlist.md`, `adoption_shortlist.json`, `adapter_blueprint.md`, `adapter_blueprint.json`, `adapter_starter/`, `manual_review_pack.md`, `manual_review_pack.json`, `candidate_briefs/`, `business_automation_plan.md`, `business_automation_summary.json`, run records, and the generated `github_discover_config.json`. The run summary gives the shortest status, candidate count, and next file to read. The executive decision brief turns discovery into a buy, wait, or recovery recommendation with investment case, risks, and approval request. The pilot scorecard gives spreadsheet-ready baseline and pilot fields for measuring value. The value realization plan turns the GitHub candidate into KPI hypotheses, measurement baselines, a 90-day rollout, and go/no-go criteria. The value measurement report defines metric cards, required baseline data, pilot measurements, and decision thresholds. The stakeholder rollout map assigns owners, approvers, operating cadence, and escalation rules so the pilot has a real operating model. The risk exception register lists unresolved rollout risks with owner, evidence, and stop condition. The operational audit plan defines post-pilot audit scope, cadence, required evidence, and stop triggers. Enterprise readiness keeps production release blocked until license review, dry-run, approval, audit log, and secret review controls are complete. The artifact index tells you what else was generated. The business plan recommends which starter-kit template to use next and includes success metrics for the workflow. Candidate briefs include adoption decision, deployment shape, 30-day implementation plan, and risk register. The adapter blueprint turns the top safe candidate into an adapter-only implementation contract, and `adapter_starter/` gives you a dry-run Python skeleton plus smoke test. If no candidate is safe enough for adapter generation, `manual_review_pack.md` explains what to inspect before reuse.

The command prints `artifact_index=...` and `next_read=...` after a successful run. `next_read` points to `adapter_starter/README.md` when a safe adapter candidate exists, `manual_review_pack.md` when candidates need review, or `query_recovery.md` when the search needs broader fallback queries.

Supported business areas include `sales`, `support`, `finance`, `operations`, `marketing`, and `hr`.

You can override the GitHub query directly:

```bash
ai-automation-kit github-discover --business-area support --query "customer support ai-agent stars:>1000" --limit 10 --output .tmp/support-discovery
```

### research-agent

```bash
ai-automation-kit research-agent --config examples/research-agent/sample_research.json --output .tmp/research-agent-demo
```

Creates `report.md`, `report.html`, `report.json`, `failed_fetches.json`, run records, and source records.

You can also fetch public GitHub repository metadata directly:

```bash
ai-automation-kit research-agent --config examples/research-agent/github_repos.json --output .tmp/github-repo-demo
```

Or search GitHub for high-signal public repositories and turn the results into a reusable report:

```bash
ai-automation-kit research-agent --config examples/research-agent/github_search.json --output .tmp/github-search-demo
```

GitHub search runs also create `run_summary.json`, `run_summary.md`, `value_realization_plan.json`, `value_realization_plan.md`, `value_measurement_report.json`, `value_measurement_report.md`, `stakeholder_rollout_map.json`, `stakeholder_rollout_map.md`, `risk_exception_register.json`, `risk_exception_register.md`, `operational_audit_plan.json`, `operational_audit_plan.md`, `enterprise_readiness.json`, `enterprise_readiness.md`, `github_candidates.json`, `github_candidates.csv`, `github_candidates.md`, `adoption_shortlist.md`, `adapter_blueprint.md`, `adapter_blueprint.json`, `adapter_starter/`, `manual_review_pack.md`, `manual_review_pack.json`, and `candidate_briefs/` with an adoption score, automation-fit label, production gate, license-risk label, adoption effort, deployment shape, 30-day implementation plan, risk register, and recommended next step. If a search returns no candidates, the run writes `query_recovery.md`, `query_recovery.json`, a discovery-recovery `value_realization_plan.md`, `value_measurement_report.md`, `stakeholder_rollout_map.md`, `risk_exception_register.md`, and `operational_audit_plan.md` with the next measurable search-quality goal, ownership model, stop condition, and audit trace. If candidates exist but none pass the adapter gate, it writes `manual_review_pack.md` with license, maintenance, and dry-run review steps. Set `"include_readme": true` in the config when you want README files downloaded into the output folder for deeper review.

```bash
ai-automation-kit research-agent --config examples/research-agent/github_repo_with_readme.json --output .tmp/github-readme-demo
```

For higher GitHub API limits, set `GITHUB_TOKEN` in your shell before running the command. Without a token, GitHub allows public unauthenticated requests at a lower rate limit.

See `docs/GITHUB_DATA.md` for supported fields, search settings, and GitHub API references.

### docs-rag

```bash
ai-automation-kit docs-rag --config examples/docs-rag/sample_docs_rag.json --output .tmp/docs-rag-demo
```

Creates `artifact_index.md`, a grounded `answer.md`, `answer.json`, `chunks.jsonl`, `source_map.json`, run records, and source records. Answers include confidence, citations, usage gate, operator checklist, and next actions.

### internal-ai-workflow

```bash
ai-automation-kit internal-ai-workflow --config examples/internal-ai-workflow/sample_inquiry.json --output .tmp/internal-ai-workflow-demo
```

Creates `artifact_index.md`, a draft reply, risk level, SLA, owner role, escalation path, review checklist, and a pending dry-run approval request.

### excel-to-internal-app

```bash
ai-automation-kit excel-to-internal-app --config examples/excel-to-internal-app/sample_app.json --output .tmp/excel-to-internal-app-demo
```

Creates `artifact_index.md`, `schema.sql`, `fields.json`, `data-quality-report.json`, `admin-view.md`, `migration-report.md`, and `app-spec.md` from CSV.

### delivery-pipeline

```bash
ai-automation-kit delivery-pipeline --config examples/delivery-pipeline/sample_delivery_pipeline.json --output .tmp/delivery-pipeline-demo
```

Creates `artifact_index.md`, delivery README, `.env.example`, Docker Compose, operation manual, delivery checklist, release plan, rollback plan, success metrics, and smoke test notes.

## Checked-in Examples

- `examples/research-agent/expected/report.md`
- `examples/docs-rag/expected/answer.md`
- `examples/internal-ai-workflow/expected/draft_reply.md`
- `examples/excel-to-internal-app/expected/migration-report.md`
- `examples/delivery-pipeline/expected/delivery-checklist.md`

## Safety Defaults

- Runtime outputs go under `.tmp/` and are ignored by Git.
- `.env` files are ignored; `.env.example` contains placeholders only.
- `research-agent` rejects localhost and private network HTTP targets.
- Failed fetches mask sensitive query parameters.
- `internal-ai-workflow` creates pending dry-run approval records instead of sending messages.
- Third-party OSS integrations are adapter-only until license review. See `docs/OSS_INTEGRATIONS.md`.

## Public Release Readiness

Before publishing a release, run:

```bash
python3 scripts/public_release_audit.py
python3 scripts/release_smoke.py
```

Review:

- `.tmp/release-smoke/doctor/doctor_report.md`
- `.tmp/release-smoke/installed-doctor/doctor_report.md`
- `.tmp/release-smoke/github-operations/artifact_index.md`
- `.tmp/release-smoke/github-operations/business_automation_plan.md`
- `.tmp/release-smoke/github-operations/adapter_blueprint.md`
- `.tmp/release-smoke/github-operations/adapter_starter/README.md`
- `.tmp/release-smoke/github-support/manual_review_pack.md`
- `.tmp/all-templates/docs-rag/answer.md`
- `.tmp/all-templates/internal-ai-workflow/review-checklist.md`
- `.tmp/all-templates/excel-to-internal-app/data-quality-report.json`
- `.tmp/all-templates/excel-to-internal-app/app-spec.md`
- `.tmp/all-templates/delivery-pipeline/docs/release-plan.md`
- `.tmp/all-templates/delivery-pipeline/docs/rollback-plan.md`
- `.tmp/all-templates/delivery-pipeline/docs/success-metrics.md`

See `docs/SHOWCASE.md` for the public demo story.

Open `docs/demo.html` in a browser for a static demo page that shows the value story and generated artifacts.
