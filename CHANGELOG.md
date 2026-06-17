# Changelog

## Unreleased

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
