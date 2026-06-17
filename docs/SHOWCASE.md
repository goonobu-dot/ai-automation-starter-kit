# AI Automation Starter Kit Showcase

This showcase explains the public demo story for the starter kit. Use it when you want to explain the project in a README, release note, demo call, or social post.

Open `docs/demo.html` in a browser when you want a visual demo page for this story.

## 30-Second Summary

AI Automation Starter Kit is a local Python CLI that turns public GitHub projects into business automation pilot plans.

It does three things:

1. Finds and ranks OSS projects for a business area.
2. Converts the best candidates into decision, value, risk, rollout, and audit artifacts.
3. Generates dry-run adapter starters and reusable local workflow templates.

## What A Visitor Should Understand

- This is not a landing page or a chat prompt collection.
- It is a runnable CLI project with tests, examples, release checks, and generated artifacts.
- The main use case is moving from GitHub research to a controlled automation pilot.
- The outputs are designed for teams that need evidence before adopting automation.

## Audience

- Developers building AI automation tooling.
- AI agent builders who need repeatable local workflows.
- Automation consultants preparing client pilot plans.
- Operations, support, finance, sales, marketing, and HR teams evaluating workflow automation.

## Outcome

After running the demo, a user should have:

- a ranked GitHub candidate list
- `executive_decision_brief.md` for approve, wait, or rerun decisions
- `pilot_scorecard.csv` for tracking baseline and pilot metrics
- `value_realization_plan.md` for KPIs and rollout phases
- `risk_exception_register.md` for blockers and stop conditions
- `operational_audit_plan.md` for required evidence
- `adapter_starter/` when a safe dry-run prototype can be generated

## Positioning

AI Automation Starter Kit turns public OSS signals into repeatable business automation workflows.

It is designed to sit next to local multi-agent workbenches:

- `local-agent-workbench`: run parallel Codex CLI sessions in tmux
- `claude-code-workbench`: run parallel Claude Code sessions in tmux
- `ai-automation-starter-kit`: turn agent research into reusable automation artifacts

## Demo Flow

### 1. Discover

Run GitHub discovery for a business area:

```bash
ai-automation-kit github-discover --business-area operations --limit 2 --output .tmp/operations-discovery
```

Key output:

- `run_summary.md`
- `executive_decision_brief.md`
- `pilot_scorecard.csv`
- `value_realization_plan.md`
- `value_measurement_report.md`
- `stakeholder_rollout_map.md`
- `risk_exception_register.md`
- `operational_audit_plan.md`
- `enterprise_readiness.md`
- `report.md`
- `artifact_index.md`
- `github_candidates.md`
- `adoption_shortlist.md`
- `adapter_blueprint.md`
- `adapter_starter/`
- `candidate_briefs/<owner>__<repo>.md`
- `business_automation_plan.md`
- `business_automation_summary.json`

### 2. Decide

Open `run_summary.md`, then `executive_decision_brief.md`, then `pilot_scorecard.csv`.

The plan shows:

- approve, wait, or discovery-recovery recommendation
- investment case and approval request
- baseline and pilot metric fields for spreadsheet tracking
- KPI hypotheses and baseline measurement
- metric cards, baseline fields, pilot measurements, and value thresholds
- 90-day rollout phases
- go/no-go criteria
- role ownership, approval matrix, operating cadence, and escalation rules
- unresolved risks, required evidence, and stop conditions
- audit scope, sampling cadence, evidence requirements, and stop triggers
- recommended repositories
- production gates such as `ready_for_adapter` or `blocked_until_license_review`
- license and maintenance risk
- suggested starter-kit templates
- implementation path
- success metrics
- adoption decision and 30-day implementation plan
- risk register for each candidate brief

### 3. Deliver

Use the recommended template to produce reusable artifacts:

```bash
ai-automation-kit docs-rag --config examples/docs-rag/sample_docs_rag.json --output .tmp/docs-rag-demo
ai-automation-kit internal-ai-workflow --config examples/internal-ai-workflow/sample_inquiry.json --output .tmp/internal-ai-workflow-demo
ai-automation-kit excel-to-internal-app --config examples/excel-to-internal-app/sample_app.json --output .tmp/excel-to-internal-app-demo
ai-automation-kit delivery-pipeline --config examples/delivery-pipeline/sample_delivery_pipeline.json --output .tmp/delivery-pipeline-demo
```

## Why Users Should Care

The kit does not stop at an AI answer. It creates reusable files:

- source-backed reports
- candidate rankings
- approval checklists
- data-quality reports
- usage gates and operator checklists
- internal app specs with roles and permissions
- release and rollback plans
- delivery checklists
- success metrics
- run records

These files make automation easier to review, repeat, and hand off.

## Public Demo Script

Use this short story in a README, release note, or X post:

```text
I open-sourced AI Automation Starter Kit.

It discovers business automation opportunities from GitHub, ranks candidate OSS projects, and turns the result into executive decisions, value scorecards, rollout maps, risk registers, audit plans, and dry-run adapter starters.

Start with:
ai-automation-kit github-discover --business-area operations --limit 2 --output .tmp/operations-discovery

Then use the five templates for research, docs Q&A, approved replies, spreadsheet-to-app migration, and delivery packaging.
```

## Release Checklist

- Run `python3 scripts/public_release_audit.py`
- Run `python3 scripts/release_smoke.py`
- Confirm `.tmp/` outputs are ignored
- Confirm `.env` files are ignored
- Confirm `business_automation_plan.md` is useful without extra explanation
