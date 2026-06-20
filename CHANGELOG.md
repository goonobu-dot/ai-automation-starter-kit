# Changelog

## Unreleased

- Added `complete-workspace` to generate a ready-to-review local delivery folder in one command.
- Added final delivery guide, completion checklist, connector report, client report, demo site, and demo zip packaging to the operator workflow.
- Added revenue readiness scoring, sales closing script, paid PoC scope, and value measurement sheet to the complete workspace.
- Added pre-contract checklist, proposal email, first 30 days plan, and proof-of-value template to reduce gaps between demo, paid PoC, and measurable follow-through.
- Added OSS pattern benchmark, integration backlog, deployment options, and production observability plan to align generated workspaces with public automation patterns from n8n, Activepieces, Windmill, and Trigger.dev-style systems.
- Added automation opportunity scorecard, client onboarding form, and go-live decision gate to close the gap between sales discovery, client approval, and production readiness.
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
