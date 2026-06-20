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
- `.tmp/release-smoke/onboard-operations/offer_pack/README.md`
- `.tmp/release-smoke/onboard-operations/offer_pack/proposal.md`
- `.tmp/release-smoke/onboard-operations/offer_pack/statement_of_work.md`
- `.tmp/release-smoke/onboard-operations/offer_pack/pricing_model.md`
- `.tmp/release-smoke/offer-pack-operations/README.md`
- `.tmp/release-smoke/offer-pack-operations/service_catalog.md`
- `.tmp/release-smoke/offer-pack-operations/proposal.md`
- `.tmp/release-smoke/offer-pack-operations/statement_of_work.md`
- `.tmp/release-smoke/offer-pack-operations/pricing_model.md`
- `.tmp/release-smoke/offer-pack-operations/risk_boundaries.md`
- `.tmp/release-smoke/client-ready-accounting/README.md`
- `.tmp/release-smoke/client-ready-accounting/client_intake.md`
- `.tmp/release-smoke/client-ready-accounting/roi_calculator.csv`
- `.tmp/release-smoke/client-ready-accounting/implementation_readiness_score.json`
- `.tmp/release-smoke/client-ready-accounting/security_review.md`
- `.tmp/release-smoke/client-ready-accounting/tool_stack_recommendation.md`
- `.tmp/release-smoke/client-ready-accounting/maintenance_plan.md`
- `.tmp/release-smoke/client-ready-accounting/marketplace_profile.md`
- `.tmp/release-smoke/client-ready-accounting/case_study_template.md`
- `.tmp/release-smoke/complete-accounting/FINAL_DELIVERY_GUIDE.md`
- `.tmp/release-smoke/complete-accounting/completion_checklist.md`
- `.tmp/release-smoke/complete-accounting/delivery_manifest.json`
- `.tmp/release-smoke/complete-accounting/revenue_readiness_scorecard.md`
- `.tmp/release-smoke/complete-accounting/sales_closing_script.md`
- `.tmp/release-smoke/complete-accounting/paid_poc_scope.md`
- `.tmp/release-smoke/complete-accounting/value_measurement_sheet.csv`
- `.tmp/release-smoke/complete-accounting/pre_contract_checklist.md`
- `.tmp/release-smoke/complete-accounting/client_proposal_email.md`
- `.tmp/release-smoke/complete-accounting/first_30_days_plan.md`
- `.tmp/release-smoke/complete-accounting/proof_of_value_template.md`
- `.tmp/release-smoke/complete-accounting/oss_pattern_benchmark.md`
- `.tmp/release-smoke/complete-accounting/integration_backlog.md`
- `.tmp/release-smoke/complete-accounting/deployment_options.md`
- `.tmp/release-smoke/complete-accounting/production_observability_plan.md`
- `.tmp/release-smoke/complete-accounting/automation_opportunity_scorecard.csv`
- `.tmp/release-smoke/complete-accounting/client_onboarding_form.md`
- `.tmp/release-smoke/complete-accounting/go_live_decision.md`
- `.tmp/release-smoke/complete-accounting/client_command_center.html`
- `.tmp/release-smoke/complete-accounting/side_business_starter_10.md`
- `.tmp/release-smoke/complete-accounting/before_after_demo.html`
- `.tmp/release-smoke/complete-accounting/business_launch/START_HERE_BUSINESS_LAUNCH.md`
- `.tmp/release-smoke/complete-accounting/business_launch/first_client_offer.md`
- `.tmp/release-smoke/business-launch/START_HERE_BUSINESS_LAUNCH.md`
- `.tmp/release-smoke/business-launch/target_industry_playbook.md`
- `.tmp/release-smoke/business-launch/first_client_offer.md`
- `.tmp/release-smoke/business-launch/risk_boundary_sheet.md`
- `.tmp/release-smoke/opportunity-catalog/opportunity_catalog.html`
- `.tmp/release-smoke/recommend-flow/recommended_flow.md`
- `.tmp/release-smoke/share-check/share_check.md`
- `docs/USER_MANUAL.md`
- `docs/SELLING_AUTOMATION_GUIDE.md`
- `docs/FLOW_SELECTION_GUIDE.md`
- `docs/CLIENT_DEMO_SCRIPT.md`
- `docs/REAL_WORLD_SETUP_GUIDE.md`
- `docs/FAQ.md`
- `.tmp/release-smoke/complete-accounting/quickstart/flow_project/automation_output/run_log.json`
- `.tmp/release-smoke/complete-accounting/connector_doctor/connector_doctor.md`
- `.tmp/release-smoke/complete-accounting/client_report/client_report.html`
- `.tmp/release-smoke/complete-accounting/client_demo_package/client_demo_package.zip`
- `.tmp/release-smoke/flow-invoice-document-followup/README.md`
- `.tmp/release-smoke/flow-invoice-document-followup/.env.example`
- `.tmp/release-smoke/flow-invoice-document-followup/config/connectors.json`
- `.tmp/release-smoke/flow-invoice-document-followup/docs/SYSTEM_RUNBOOK.md`
- `.tmp/release-smoke/flow-invoice-document-followup/flow.yaml`
- `.tmp/release-smoke/flow-invoice-document-followup/workflow_map.mmd`
- `.tmp/release-smoke/flow-invoice-document-followup/human_approval_points.md`
- `.tmp/release-smoke/flow-invoice-document-followup/scripts/run_dry_run.py`
- `.tmp/release-smoke/flow-invoice-document-followup/automation_output/work_queue.csv`
- `.tmp/release-smoke/flow-invoice-document-followup/automation_output/draft_outputs.md`
- `.tmp/release-smoke/flow-invoice-document-followup/automation_output/approval_queue.csv`
- `.tmp/release-smoke/flow-invoice-document-followup/automation_output/status_report.md`
- `.tmp/release-smoke/flow-invoice-document-followup/automation_output/run_log.json`
- `.tmp/release-smoke/flow-invoice-document-followup/automation_output/approved_actions.csv`
- `.tmp/release-smoke/flow-invoice-document-followup/local_outbox/email_drafts.md`
- `.tmp/release-smoke/flow-invoice-document-followup/local_outbox/slack_messages.md`
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
- [ ] Confirm offer-pack files do not guarantee income and clearly define scope, pricing model, client approval, and safety boundaries.
- [ ] Confirm `business-launch` outputs explain the first offer, discovery call, pricing, risk boundaries, and 30-day launch path without promising income or fully autonomous production work.
- [ ] Confirm English manuals explain the same business proposal path as the Japanese manuals.
- [ ] Confirm client-ready files cover intake, ROI, proposal tiers, security, tool selection, maintenance, marketplace profile, and case-study evidence.
- [ ] Confirm `flows list`, `flows show`, `flows install`, `flows validate`, `flows run`, and `flows approve` work for at least one installed flow.
- [ ] Confirm installed flow projects include `flow.yaml`, `workflow_map.mmd`, approval points, sample data, a dry-run script, and a contract test.
- [ ] Confirm installed flow projects include `.env.example`, `config/connectors.json`, and `docs/SYSTEM_RUNBOOK.md`.
- [ ] Confirm installed flow projects produce `automation_output/` with a work queue, draft outputs, approval queue, connector tasks, status report, and run log.
- [ ] Confirm approval produces `approved_actions.csv` and `local_outbox/` drafts without sending external messages.
- [ ] Run the generated adapter starter smoke test when `adapter_starter/` is present.
- [ ] Confirm README quickstart works from a fresh virtual environment.

## Release Decision

Publish only when tests pass, demos generate, `doctor` has no failed checks, and the live GitHub smoke output is useful without extra explanation.
