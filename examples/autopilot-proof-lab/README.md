# Automation Proof Lab Fixture

Small, privacy-safe fixture set for `ai-automation-kit autopilot-proof-lab`.

- Scope: fictional invoice-order review only
- Safety: no real people, no vendor identities, no account numbers, no secrets
- Language: English-first with Japanese helper text in the evidence and JSON notes
- Boundary: readiness is advisory only; no external actions are activated

## Included files

- `evidence/current-process.md`
- `evidence/approved-policy.md`
- `evidence/recovery-plan.md`
- `normal/{input.json,expected.json,proposed.json}`
- `near_limit/{input.json,expected.json,proposed.json}`
- `missing_data/{input.json,expected.json,proposed.json}`
- `duplicate/{input.json,expected.json,proposed.json}`
- `conflicting/{input.json,expected.json,proposed.json}`
- `expired/{input.json,expected.json,proposed.json}`
- `external_failure/{input.json,expected.json,proposed.json}`

## Case directory to CLI class mapping

The fixture directory names are descriptive. The current CLI `--case-class` values are:

| Fixture directory | CLI `--case-class` | Typical route |
| --- | --- | --- |
| `normal` | `normal` | `standard` |
| `near_limit` | `near_limit` | `standard` |
| `missing_data` | `missing_data` | `quarantine` |
| `duplicate` | `duplicate` | `quarantine` |
| `conflicting` | `conflicting` | `quarantine` |
| `expired` | `expired` | `quarantine` |
| `external_failure` | `external_failure` | `quarantine` |

## Implemented hard-gate IDs

Use these exact gate names with `set-gate`:

- `input_identifiable`
- `completion_testable`
- `standard_policy_confirmed`
- `exceptions_detectable`
- `exception_owner_assigned`
- `least_privilege_available`
- `idempotency_defined`
- `recovery_defined`
- `kill_switch_owned`
- `data_use_permitted`
- `shadow_test_passed`

## Sample run

Run from the repository root:

```bash
ai-automation-kit autopilot-proof-lab init \
  --pack-id invoice-order-check-daily \
  --organization "Northwind Example Co" \
  --objective "Evaluate a safe invoice-order review shadow workflow" \
  --requested-level L3 \
  --workspace .tmp/proof-lab-fixture \
  --language en

ai-automation-kit autopilot-proof-lab add-evidence \
  --workspace .tmp/proof-lab-fixture \
  --source ./examples/autopilot-proof-lab/evidence/current-process.md \
  --role current_process_example \
  --classification internal \
  --provided-by "Operations owner"

ai-automation-kit autopilot-proof-lab add-evidence \
  --workspace .tmp/proof-lab-fixture \
  --source ./examples/autopilot-proof-lab/evidence/approved-policy.md \
  --role policy \
  --classification internal \
  --provided-by "Finance controller"

ai-automation-kit autopilot-proof-lab add-evidence \
  --workspace .tmp/proof-lab-fixture \
  --source ./examples/autopilot-proof-lab/evidence/recovery-plan.md \
  --role recovery_procedure \
  --classification internal \
  --provided-by "Systems owner"
```

Add one low-risk standard case:

```bash
ai-automation-kit autopilot-proof-lab add-case \
  --workspace .tmp/proof-lab-fixture \
  --case-id normal-001 \
  --input ./examples/autopilot-proof-lab/normal/input.json \
  --expected ./examples/autopilot-proof-lab/normal/expected.json \
  --proposed ./examples/autopilot-proof-lab/normal/proposed.json \
  --risk-tier low \
  --case-class normal \
  --expected-route standard \
  --proposed-route standard \
  --recovery-tested \
  --recovery-passed
```

Add the rest of the fixture, including quarantine paths and one critical exception:

```bash
ai-automation-kit autopilot-proof-lab add-case \
  --workspace .tmp/proof-lab-fixture \
  --case-id near-limit-001 \
  --input ./examples/autopilot-proof-lab/near_limit/input.json \
  --expected ./examples/autopilot-proof-lab/near_limit/expected.json \
  --proposed ./examples/autopilot-proof-lab/near_limit/proposed.json \
  --risk-tier medium \
  --case-class near_limit \
  --expected-route standard \
  --proposed-route standard

ai-automation-kit autopilot-proof-lab add-case \
  --workspace .tmp/proof-lab-fixture \
  --case-id missing-data-001 \
  --input ./examples/autopilot-proof-lab/missing_data/input.json \
  --expected ./examples/autopilot-proof-lab/missing_data/expected.json \
  --proposed ./examples/autopilot-proof-lab/missing_data/proposed.json \
  --risk-tier medium \
  --case-class missing_data \
  --expected-route quarantine \
  --proposed-route quarantine \
  --exception-expected \
  --exception-detected

ai-automation-kit autopilot-proof-lab add-case \
  --workspace .tmp/proof-lab-fixture \
  --case-id duplicate-001 \
  --input ./examples/autopilot-proof-lab/duplicate/input.json \
  --expected ./examples/autopilot-proof-lab/duplicate/expected.json \
  --proposed ./examples/autopilot-proof-lab/duplicate/proposed.json \
  --risk-tier high \
  --case-class duplicate \
  --expected-route quarantine \
  --proposed-route quarantine \
  --exception-expected \
  --exception-detected \
  --duplicate-action-simulations 1

ai-automation-kit autopilot-proof-lab add-case \
  --workspace .tmp/proof-lab-fixture \
  --case-id conflicting-001 \
  --input ./examples/autopilot-proof-lab/conflicting/input.json \
  --expected ./examples/autopilot-proof-lab/conflicting/expected.json \
  --proposed ./examples/autopilot-proof-lab/conflicting/proposed.json \
  --risk-tier high \
  --case-class conflicting \
  --expected-route quarantine \
  --proposed-route quarantine \
  --exception-expected \
  --exception-detected

ai-automation-kit autopilot-proof-lab add-case \
  --workspace .tmp/proof-lab-fixture \
  --case-id expired-001 \
  --input ./examples/autopilot-proof-lab/expired/input.json \
  --expected ./examples/autopilot-proof-lab/expired/expected.json \
  --proposed ./examples/autopilot-proof-lab/expired/proposed.json \
  --risk-tier medium \
  --case-class expired \
  --expected-route quarantine \
  --proposed-route quarantine \
  --exception-expected \
  --exception-detected

ai-automation-kit autopilot-proof-lab add-case \
  --workspace .tmp/proof-lab-fixture \
  --case-id external-failure-001 \
  --input ./examples/autopilot-proof-lab/external_failure/input.json \
  --expected ./examples/autopilot-proof-lab/external_failure/expected.json \
  --proposed ./examples/autopilot-proof-lab/external_failure/proposed.json \
  --risk-tier critical \
  --case-class external_failure \
  --expected-route quarantine \
  --proposed-route quarantine \
  --exception-expected \
  --exception-detected
```

Record gates. This intentionally leaves the sample at `assist_only`:

```bash
ai-automation-kit autopilot-proof-lab set-gate \
  --workspace .tmp/proof-lab-fixture \
  --gate input_identifiable \
  --status pass \
  --owner "Operations owner" \
  --evidence-id ev-0001 \
  --note "Structured invoice and order fields are stable in this sample."

ai-automation-kit autopilot-proof-lab set-gate \
  --workspace .tmp/proof-lab-fixture \
  --gate completion_testable \
  --status pass \
  --owner "Operations owner" \
  --evidence-id ev-0002 \
  --note "Expected routes and draft decisions are reviewable."

ai-automation-kit autopilot-proof-lab set-gate \
  --workspace .tmp/proof-lab-fixture \
  --gate standard_policy_confirmed \
  --status pass \
  --owner "Finance controller" \
  --evidence-id ev-0002 \
  --note "Policy file defines standard vs quarantine handling."

ai-automation-kit autopilot-proof-lab set-gate \
  --workspace .tmp/proof-lab-fixture \
  --gate exceptions_detectable \
  --status pass \
  --owner "Finance controller" \
  --evidence-id ev-0002 \
  --note "Missing, duplicate, conflict, expiry, and external failure patterns are defined."

ai-automation-kit autopilot-proof-lab set-gate \
  --workspace .tmp/proof-lab-fixture \
  --gate exception_owner_assigned \
  --status pass \
  --owner "Finance controller" \
  --evidence-id ev-0001 \
  --note "Exceptions return to a named human queue."

ai-automation-kit autopilot-proof-lab set-gate \
  --workspace .tmp/proof-lab-fixture \
  --gate least_privilege_available \
  --status pass \
  --owner "Systems owner" \
  --evidence-id ev-0003 \
  --note "The proof lab stores local evidence only and does not write to external systems."

ai-automation-kit autopilot-proof-lab set-gate \
  --workspace .tmp/proof-lab-fixture \
  --gate idempotency_defined \
  --status fail \
  --owner "Systems owner" \
  --evidence-id ev-0003 \
  --note "Replay protection is not yet tested outside this small fixture."

ai-automation-kit autopilot-proof-lab set-gate \
  --workspace .tmp/proof-lab-fixture \
  --gate recovery_defined \
  --status pass \
  --owner "Systems owner" \
  --evidence-id ev-0003 \
  --note "Recovery stays local: quarantine queue, audit note, manual restart."

ai-automation-kit autopilot-proof-lab set-gate \
  --workspace .tmp/proof-lab-fixture \
  --gate kill_switch_owned \
  --status pass \
  --owner "Systems owner" \
  --evidence-id ev-0003 \
  --note "Operator can stop by pausing intake and reviewing the quarantine queue."

ai-automation-kit autopilot-proof-lab set-gate \
  --workspace .tmp/proof-lab-fixture \
  --gate data_use_permitted \
  --status pass \
  --owner "Finance controller" \
  --evidence-id ev-0002 \
  --note "Fixture data is fictional and approved for local testing."

ai-automation-kit autopilot-proof-lab set-gate \
  --workspace .tmp/proof-lab-fixture \
  --gate shadow_test_passed \
  --status pass \
  --owner "Operations owner" \
  --evidence-id ev-0001 \
  --note "Seven sanitized historical examples are useful for learning, not for claiming unattended readiness."
```

Evaluate and inspect status:

```bash
ai-automation-kit autopilot-proof-lab evaluate \
  --workspace .tmp/proof-lab-fixture

ai-automation-kit autopilot-proof-lab status \
  --workspace .tmp/proof-lab-fixture \
  --json
```

## Expected outcome

This fixture is intentionally small. It should honestly remain `assist_only` for at least these reasons:

- only seven shadow cases are included
- one gate is deliberately failed: `idempotency_defined`
- one exception case (`conflicting`) includes a content mismatch for human review
- no external actions are activated
- current human approval stays in place

Look for these safety signals in the output:

- `decision=assist_only` or `"decision": "assist_only"`
- `external_actions_enabled=false` in CLI status output
- `"external_actions_activated": false` in evaluation JSON

Promotion above `assist_only` would require more than this sample: complete evidence, all hard gates passed, stronger shadow results, and a separately justified readiness decision.
