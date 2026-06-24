# AI Automation Starter Kit User Manual

This manual explains how to use AI Automation Starter Kit to find a business automation opportunity, create a safe demo, prepare a client proposal, and move toward a small paid dry-run PoC.

This project does not guarantee income. Its purpose is to turn vague AI automation ideas into concrete files: workflow choices, demo evidence, proposal materials, approval boundaries, value measurements, and go-live gates.

## 1. Install And Check The Local Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip setuptools
python3 -m pip install -e .
ai-automation-kit doctor --output .tmp/doctor
```

Open `.tmp/doctor/doctor_report.md` if the command reports warnings.

## 2. Create One Complete Client Workspace

If you are not sure where to start, use `complete-workspace`. It creates the runnable dry-run flow, approval records, connector check, client report, demo site, demo package, revenue readiness scorecard, Paid PoC scope, proposal email, first 30 days plan, proof-of-value template, production readiness files, and `business_launch/` proposal pack.

```bash
ai-automation-kit complete-workspace \
  --flow-id invoice-document-followup \
  --client-type local-business \
  --niche accounting \
  --output .tmp/complete-accounting
```

Read these first:

- `.tmp/complete-accounting/FINAL_DELIVERY_GUIDE.md`
- `.tmp/complete-accounting/client_report/client_report.html`
- `.tmp/complete-accounting/demo_site/index.html`
- `.tmp/complete-accounting/revenue_readiness_scorecard.md`
- `.tmp/complete-accounting/paid_poc_scope.md`
- `.tmp/complete-accounting/pre_contract_checklist.md`
- `.tmp/complete-accounting/business_launch/START_HERE_BUSINESS_LAUNCH.md`
- `.tmp/complete-accounting/business_launch/first_client_offer.md`
- `.tmp/complete-accounting/flow_exports/n8n/START_HERE_FLOW_EXPORT.md`
- `.tmp/complete-accounting/deployment_packs/coolify/START_HERE_DEPLOYMENT_PACK.md`
- `.tmp/complete-accounting/runtime_safety/approval_policy.md`
- `.tmp/complete-accounting/secrets_bootstrap/secret_ownership.md`
- `.tmp/complete-accounting/document_intake/START_HERE_DOCUMENT_INTAKE.md`
- `.tmp/complete-accounting/observability_pack/trace_model.md`
- `.tmp/complete-accounting/state_backend/START_HERE_STATE_BACKEND.md`

## 3. Build A Business Proposal Pack

Use `business-launch` when the operator is new to AI and needs plain proposal materials before approaching a company.

```bash
ai-automation-kit business-launch \
  --industry finance \
  --client-type local-business \
  --niche accounting \
  --output .tmp/business-launch
```

It creates:

- `START_HERE_BUSINESS_LAUNCH.md`
- `target_industry_playbook.md`
- `first_client_offer.md`
- `discovery_call_script.md`
- `proposal_builder.md`
- `pricing_and_scope_menu.md`
- `risk_boundary_sheet.md`
- `30_day_business_launch_plan.md`
- `client_pitch_email.md`

Use this pack to explain a small, safe first offer: one workflow, one sample data source, one human approver, one measurable outcome, and no production sends until the client approves the next step.

## 4. Choose What To Sell

Create a catalog of sellable automation opportunities:

```bash
ai-automation-kit opportunity-catalog --industry finance --output .tmp/opportunity-catalog
```

Open `.tmp/opportunity-catalog/opportunity_catalog.html`.

If a client already told you their pain, use:

```bash
ai-automation-kit recommend-flow \
  --industry finance \
  --pain "missing invoice follow up" \
  --tools "Google Sheets Gmail" \
  --monthly-items 80 \
  --output .tmp/recommend-flow
```

Open `.tmp/recommend-flow/recommended_flow.md` and `.tmp/recommend-flow/recommended_poc_scope.md`.

## 5. Share Files Safely

Before sending generated files to a client, run:

```bash
ai-automation-kit share-check --source .tmp/complete-accounting --output .tmp/share-check
```

If `share_check.md` says `blocked`, remove the secret-like markers before sharing.

## 6. Move Into A Real Execution Stack

Export the chosen flow into a real automation tool:

```bash
ai-automation-kit flow-export \
  --flow-id invoice-document-followup \
  --target n8n \
  --output .tmp/flow-export-n8n
```

Create a deployment starter:

```bash
ai-automation-kit deployment-pack \
  --flow-id invoice-document-followup \
  --provider coolify \
  --connectors gmail,google-sheets \
  --output .tmp/deployment-coolify
```

Add runtime safety, secrets, document conversion, observability, and state:

```bash
ai-automation-kit runtime-safety --flow-id invoice-document-followup --output .tmp/runtime-safety
ai-automation-kit secrets-bootstrap --flow-id invoice-document-followup --provider infisical --connectors gmail,google-sheets --output .tmp/secrets-bootstrap
ai-automation-kit document-intake --flow-id invoice-document-followup --mode advanced --output .tmp/document-intake
ai-automation-kit observability-pack --flow-id invoice-document-followup --output .tmp/observability-pack
ai-automation-kit state-backend --flow-id invoice-document-followup --backend supabase --output .tmp/state-backend
```

## 7. Move From Demo To Paid PoC

The safest first offer is a bounded Paid PoC:

- use sample or anonymized data
- keep external sends disabled
- keep production writes disabled
- create drafts, queues, reports, and approval evidence
- measure manual time vs dry-run time
- ask the client to choose continue, revise, or stop

Do not sell the first engagement as fully autonomous production automation. Sell it as a safe discovery and proof-of-value step.
