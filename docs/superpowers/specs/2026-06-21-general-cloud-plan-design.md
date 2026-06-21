# General Cloud Plan Design

## Goal

Make `cloud-plan` a general cloud deployment planning helper, not a LINE Bot-specific helper.

## Scope

`cloud-plan` must support common automation workloads:

- `webhook-api`
- `scheduled-job`
- `worker-queue`
- `web-app`
- `static-functions`
- `container-service`

LINE, Gmail, Google Sheets, Slack, CRM, storage folders, and generic webhooks are connectors. They may affect secrets and setup notes, but they must not define the whole cloud plan.

## Outputs

The command should create general cloud planning artifacts:

- `START_HERE_CLOUD_PLAN.md`
- `cloud_provider_matrix.md`
- `workload_architecture.md`
- `runtime_choice.md`
- `secrets_and_env.md`
- `network_and_domain.md`
- `deploy_runbook.md`
- `operations_runbook.md`
- `cost_guardrails.md`
- `compliance_data_boundary.md`
- `incident_rollback.md`
- `human_approval_required.md`
- `cloud_plan.json`

Legacy filenames may remain for compatibility, but README and release smoke should lead with the general artifacts.

## Boundary

The command must not claim to create cloud accounts, billing, domains, DNS, IAM, app credentials, or production webhooks automatically. It should generate a reviewable plan, commands, and human approval gates.

