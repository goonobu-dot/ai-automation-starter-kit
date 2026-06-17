# AI Automation Starter Kit

Cloneable starter kit for reusable AI automation workflows. It turns five OSS-inspired ideas into local, testable templates with run records, source/provenance files, and checked-in examples.

## 1-Minute Demo

Use this first when you want to discover business automation opportunities from public GitHub projects and turn them into a practical next-step plan:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m ensurepip --upgrade
python3 -m pip install --upgrade pip setuptools
python3 -m pip install -e .
ai-automation-kit doctor --output .tmp/doctor
ai-automation-kit github-discover --business-area operations --limit 2 --output .tmp/operations-discovery
```

Open the generated plan:

```bash
sed -n '1,180p' .tmp/operations-discovery/business_automation_plan.md
```

Or open the artifact index when you want to know what to read first:

```bash
sed -n '1,180p' .tmp/operations-discovery/artifact_index.md
```

### Example Output

The plan tells you:

- which GitHub repositories are worth reviewing first
- which candidates need license or maintenance review
- which starter-kit template to use next
- how to run a dry-run prototype
- which success metrics prove the automation is actually useful
- which candidates are ready for a 30-day adapter prototype
- which risks block production use until review

Example generated files:

- `.tmp/operations-discovery/report.md`
- `.tmp/operations-discovery/artifact_index.md`
- `.tmp/operations-discovery/github_candidates.md`
- `.tmp/operations-discovery/adapter_blueprint.md`
- `.tmp/operations-discovery/adapter_starter/`
- `.tmp/operations-discovery/business_automation_plan.md`
- `.tmp/operations-discovery/business_automation_summary.json`

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

The demo outputs are written to `.tmp/all-templates/`.

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
