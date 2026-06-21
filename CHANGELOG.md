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
