# Release Checklist

Use this checklist before publishing or tagging a public release.

## Automated Checks

```bash
python3 scripts/public_release_audit.py
python3 scripts/release_smoke.py
```

Use `python3 scripts/release_smoke.py --skip-github` when working offline.

## Review Generated Evidence

- `.tmp/release-smoke/doctor/doctor_report.md`
- `.tmp/release-smoke/installed-doctor/doctor_report.md`
- `.tmp/release-smoke/onboard-operations/onboarding_summary.md`
- `.tmp/release-smoke/onboard-operations/onboarding_summary.json`
- `.tmp/release-smoke/onboard-operations/doctor/doctor_report.md`
- `.tmp/release-smoke/onboard-operations/github_discover_config.json`
- `.tmp/release-smoke/github-operations/run_summary.md`
- `.tmp/release-smoke/github-operations/executive_decision_brief.md`
- `.tmp/release-smoke/github-operations/pilot_scorecard.csv`
- `.tmp/release-smoke/github-operations/enterprise_readiness.md`
- `.tmp/release-smoke/github-operations/value_realization_plan.md`
- `.tmp/release-smoke/github-operations/value_measurement_report.md`
- `.tmp/release-smoke/github-operations/stakeholder_rollout_map.md`
- `.tmp/release-smoke/github-operations/risk_exception_register.md`
- `.tmp/release-smoke/github-operations/operational_audit_plan.md`
- `.tmp/release-smoke/github-operations/artifact_index.md`
- `.tmp/release-smoke/github-operations/business_automation_plan.md`
- `.tmp/release-smoke/github-operations/adoption_shortlist.md`
- `.tmp/release-smoke/github-operations/adapter_blueprint.md`
- `.tmp/release-smoke/github-operations/adapter_starter/README.md`
- `.tmp/release-smoke/github-operations/adapter_starter/smoke_test.py`
- `.tmp/release-smoke/github-operations/candidate_briefs/`
- `.tmp/release-smoke/github-support/run_summary.md`
- `.tmp/release-smoke/github-support/executive_decision_brief.md`
- `.tmp/release-smoke/github-support/pilot_scorecard.csv`
- `.tmp/release-smoke/github-support/enterprise_readiness.md`
- `.tmp/release-smoke/github-support/value_realization_plan.md`
- `.tmp/release-smoke/github-support/value_measurement_report.md`
- `.tmp/release-smoke/github-support/stakeholder_rollout_map.md`
- `.tmp/release-smoke/github-support/risk_exception_register.md`
- `.tmp/release-smoke/github-support/operational_audit_plan.md`
- `.tmp/release-smoke/github-support/manual_review_pack.md`
- `.tmp/all-templates/docs-rag/answer.md`
- `.tmp/all-templates/internal-ai-workflow/review-checklist.md`
- `.tmp/all-templates/excel-to-internal-app/app-spec.md`
- `.tmp/all-templates/delivery-pipeline/docs/release-plan.md`
- `.tmp/all-templates/delivery-pipeline/docs/rollback-plan.md`

## Manual Safety Review

- [ ] Confirm no `.env` or private credentials are tracked.
- [ ] Confirm `.env.example` contains placeholders only.
- [ ] Confirm `.tmp/`, `.venv/`, and egg-info files are ignored.
- [ ] Confirm GitHub candidate reuse remains adapter-only until license review.
- [ ] Confirm `executive_decision_brief.md` gives a buy, wait, or discovery recovery recommendation with approval request.
- [ ] Confirm `pilot_scorecard.csv` can be used to track baseline and pilot measurements in a spreadsheet.
- [ ] Confirm `value_realization_plan.md` ties automation work to KPI, baseline, rollout, and go/no-go evidence.
- [ ] Confirm `value_measurement_report.md` defines metric cards, baseline fields, pilot measurements, and value thresholds.
- [ ] Confirm `stakeholder_rollout_map.md` assigns owners, approvers, operating cadence, and escalation rules.
- [ ] Confirm `risk_exception_register.md` lists open exceptions, owners, required evidence, and stop conditions.
- [ ] Confirm `operational_audit_plan.md` defines audit scope, cadence, evidence requirements, and stop triggers.
- [ ] Confirm dry-run, approval, rollback, and audit guidance is visible in generated outputs.
- [ ] Confirm `artifact_index.md` points to the right first-read files.
- [ ] Run the generated adapter starter smoke test when `adapter_starter/` is present.
- [ ] Confirm README quickstart works from a fresh virtual environment.

## Release Decision

Publish only when tests pass, demos generate, `doctor` has no failed checks, and the live GitHub smoke output is useful without extra explanation.
