# Autopilot Readiness Builder Design

Date: 2026-07-13
Status: Proposed; implementation requires explicit review

## 1. Decision

Build an Autopilot Readiness Builder before adding unattended external actions.
The builder must determine whether a workflow is ready for automation, guide a
human through solvable gaps, and return a reasoned `not_ready` decision when
the required evidence or controls do not exist.

The existing Human Approval Edition remains unchanged. It continues to own
local evidence intake, Codex-assisted drafting, PIN approval, approved-output
reuse, and the local audit chain. Any future service that performs external
writes must use a separate runtime and trust boundary.

## 2. Product Outcomes

For any of the 22 office packs, the builder produces one of four outcomes:

- `ready_unattended`: the assessment supports designing a future runtime in
  which a separately authorized standard path could run without per-case
  approval;
- `ready_conditional`: standard cases run automatically and exceptions stop;
- `assist_only`: AI can prepare evidence and drafts, but a human decision stays;
- `not_ready`: automation must not proceed under the current conditions.

A `not_ready` result is a valid deliverable. It includes evidence, blocking
gates, remediation owners, acceptance conditions, and a reassessment path.

These outcomes are advisory readiness labels for a future, separate Autopilot
runtime. They do not execute a current pack and do not override the bundled pack
contract. Every current pack retains its per-draft approval requirement inside
the Human Approval Edition, including after an `L3` or `L4` assessment.

An assessment may narrow current behavior, but it may never remove or weaken a
bundled `prohibited_action`, approval requirement, or risk boundary. A future
runtime that does not require per-case approval needs a new, separately
reviewed action contract approved by authorized business, legal, and security
owners. That migration cannot be generated or activated by the readiness
decision itself. Source-pack prohibitions remain mandatory human-boundary
signals unless that entirely separate contract explicitly retains a stricter
boundary after specialist review.

## 3. Non-Goals

This design does not:

- add external connectors to the current office workspace;
- remove the current PIN approval contract;
- let an LLM invent or approve production policy;
- treat a weighted score as a substitute for mandatory controls;
- promise that every pack can perform consequential external actions;
- implement payment, employment, contract, access, filing, or certification
  actions in the first Autopilot release.

## 4. Human Journey

```text
choose objective
  -> describe current work
  -> add evidence and examples
  -> answer one contextual question
  -> review extracted workflow and rule candidates
  -> resolve or assign gaps
  -> run historical shadow tests
  -> compare human and AI outcomes
  -> receive readiness decision
  -> remediate, remain assisted, stop, or prepare a controlled pilot
```

Every question includes:

- plain-language question text;
- why the answer is needed;
- one or more realistic examples;
- a `do not know` path;
- the evidence currently supporting the question;
- the consequence of leaving it unresolved.

The UI must ask one primary question at a time. It may show progress and the
number of unresolved topics, but it must not present a large technical
questionnaire as the default interaction.

## 5. Readiness Domains

The assessment covers nine domains:

1. trigger and duplicate detection;
2. input evidence and data classification;
3. output and completion criteria;
4. deterministic decision policy;
5. exceptions and escalation ownership;
6. connector actions and least privilege;
7. retries, compensation, and recovery;
8. accountability, retention, and applicable obligations;
9. baseline value and operating cost.

Each domain stores `confirmed`, `candidate`, `missing`, `conflicting`, or
`not_applicable`, plus evidence references and a responsible owner.

## 6. Hard Gates

Weighted scoring may prioritize work, but it cannot override these gates:

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

External writes require every relevant gate. Missing a hard gate caps the
decision at `assist_only` or `not_ready`, regardless of the aggregate score.

## 7. Automation Levels

```text
L0 not_ready
L1 assisted_draft
L2 shadow
L3 conditional_autopilot
L4 unattended_standard_path
```

`L4` does not mean that exceptions disappear. It means the declared standard
path is unattended while every unmatched, conflicting, over-limit, or failed
case is quarantined.

## 8. Core Data Contracts

### 8.1 Assessment

```json
{
  "assessment_id": "asmt_...",
  "pack_id": "invoice-order-check-daily",
  "organization": "Example Co",
  "objective": "Reduce manual matching without releasing payments",
  "requested_level": "L3",
  "current_level": "L1",
  "status": "collecting_evidence",
  "created_at": "2026-07-13T00:00:00Z",
  "policy_version": 1
}
```

### 8.2 Evidence reference

```json
{
  "evidence_id": "ev_...",
  "role": "current_process_example",
  "relative_path": "evidence/approved-example.md",
  "sha256": "...",
  "classification": "confidential",
  "provided_by": "Operations owner",
  "verified_at": null
}
```

### 8.3 Decision rule

```json
{
  "rule_id": "rule_...",
  "state": "candidate",
  "when": [
    {"field": "amount", "operator": "lte", "value": 100000},
    {"field": "required_documents_complete", "operator": "eq", "value": true}
  ],
  "result": "standard_path",
  "exception_result": "quarantine",
  "evidence_ids": ["ev_..."],
  "confirmed_by": null,
  "confirmer_role": null,
  "confirmed_at": null,
  "authorization_source": null,
  "pack_manifest_hash": "...",
  "prior_decision_hash": null
}
```

Free-form model text cannot become executable policy. A rule must compile into
an allowlisted operator set and be confirmed by an authorized business owner.

### 8.4 Gap

```json
{
  "gap_id": "gap_...",
  "gate": "recovery_defined",
  "severity": "blocking",
  "summary": "The vendor activation action has no verified reversal path.",
  "why_it_matters": "A wrong vendor could remain active or receive payment.",
  "owner": "Procurement systems owner",
  "remediation": "Document and test deactivation and payment-hold steps.",
  "acceptance_check": "A staged activation is reversed without residual access.",
  "target_level_after_fix": "L3"
}
```

### 8.5 Readiness decision

```json
{
  "decision": "assist_only",
  "maximum_level": "L1",
  "hard_gate_results": {
    "input_identifiable": "pass",
    "completion_testable": "pass",
    "recovery_defined": "fail"
  },
  "blocking_gap_ids": ["gap_..."],
  "human_decision_boundaries": ["vendor_activation", "banking_update"],
  "evidence_snapshot_hash": "...",
  "decided_at": "2026-07-13T00:00:00Z"
}
```

## 9. Assessment State Machine

```text
created
  -> discovering
  -> evidence_waiting | modeling_current_work
  -> rule_confirmation
  -> gap_resolution
  -> ready_for_shadow
  -> shadow_running
  -> comparison_review
  -> decision_ready
  -> ready_unattended | ready_conditional | assist_only | not_ready
```

Side states:

```text
any active state -> paused | cancelled
shadow_running -> shadow_failed -> ready_for_shadow
any state -> manual_recovery_required
any active or terminal state -> evidence_changed -> stale_decision -> reassessment
```

Transitions store actor, time, prior state, new state, evidence snapshot hash,
and reason. The AI may recommend a transition but cannot mark a hard gate as
passed without the required evidence and confirmation.

`evidence_changed` is triggered when an input hash, policy version, pack
manifest hash, connector contract, authorization record, responsible owner, or
material model/extraction version differs from the decision snapshot. A stale
decision cannot authorize a pilot or external action.

## 10. Decision Algorithm

1. Validate assessment and evidence integrity.
2. Evaluate domain completeness.
3. Evaluate hard gates deterministically.
4. Derive the highest permitted automation level.
5. Compare the requested level with the permitted level.
6. Generate blocking and non-blocking gaps.
7. Produce a remediation roadmap for solvable gaps.
8. Separate permanent human boundaries from temporary gaps.
9. Require shadow evidence before any `L3` or `L4` recommendation.
10. Hash the evidence, policy, test results, and final decision.

The system never converts low confidence into a pass. Uncertainty produces a
question, a quarantine rule, a lower level, or `not_ready`.

## 11. Shadow Testing

Shadow mode runs the proposed workflow without external writes. A case contains
input evidence, expected human outcome, proposed policy outcome, AI artifacts,
and comparison fields.

Minimum measurements:

- exact-match and material-match rates;
- false positive and false negative counts;
- unsupported-claim count;
- duplicate-action simulation count;
- exception-detection rate;
- quarantine precision;
- elapsed time and estimated cost;
- recovery-test success;
- human correction categories.

Pass thresholds are pack- and organization-specific. High-risk false negatives
cannot be averaged away by high performance on routine cases.

Minimum shadow contract for an `L3` or `L4` recommendation:

- cover normal, near-limit, missing-data, duplicate, conflicting, expired, and
  external-failure cases;
- use at least 100 representative cases or the most recent three months of
  available cases, whichever is larger, unless a responsible owner documents
  why the volume does not exist and extends `L2` monitoring;
- include at least one case for every declared exception route;
- allow zero critical false negatives for high-risk consequences;
- prove stale, changed, and incomplete evidence is rejected or quarantined;
- prove replay does not create a duplicate side effect;
- execute at least one recovery or compensation simulation;
- report results separately by risk tier and case class.

An organization may impose stricter thresholds. It may not use a high average
accuracy to waive a critical-case failure.

## 12. Pack Extension Contract

The current 22 pack contracts remain draft contracts. Autopilot assessment adds
a separate extension document per organization:

```json
{
  "pack_id": "inquiry-daily",
  "trigger": {},
  "input_contract": {},
  "policy_rules": [],
  "allowed_actions": [],
  "prohibited_actions": [],
  "limits": {},
  "idempotency": {},
  "exception_routes": [],
  "retry_policy": {},
  "compensations": [],
  "verification": {},
  "kill_switch": {},
  "retention": {}
}
```

This extension is generated from the assessment but is not executable until
all hard gates, confirmation requirements, and shadow checks pass.

The extension's `prohibited_actions` is the union of bundled pack prohibitions
and organization-specific prohibitions. `allowed_actions` must be disjoint from
that union. Validation fails closed when an action appears in both sets.

## 13. Architecture Boundary

### In the existing repository

- readiness interview;
- evidence folder and manifests;
- current-workflow modeling;
- rule candidates;
- gap register;
- shadow test cases and comparisons;
- readiness decision and human-readable report.

These capabilities are read-only or draft-producing and match the existing
trust model.

### In a separate Autopilot runtime

- scheduler and triggers;
- service identities and connector credentials;
- durable execution ledger;
- idempotent workers;
- retries and quarantine;
- external action dispatch;
- post-action verification;
- compensation and rollback;
- global, workflow, and connector kill switches;
- side-effect audit and operational alerts.

The Autopilot runtime imports only signed, approved assessment artifacts. It
does not accept arbitrary instructions from source documents or model output.

## 14. User Interface

Required screens:

1. objective chooser;
2. one-question interview;
3. evidence preparation;
4. current workflow map;
5. candidate rule confirmation;
6. gaps and remediation owners;
7. shadow test setup;
8. human-versus-system comparison;
9. readiness decision;
10. controlled pilot preparation.

Each screen shows the next useful action. Technical identifiers are secondary
to plain-language labels. Risk is always expressed in text, not color alone.

## 15. Generated Artifacts

- `current_workflow.md`
- `automation_scope.md`
- `source_inventory.csv`
- `decision_table.csv`
- `exception_register.csv`
- `connector_permissions.md`
- `recovery_plan.md`
- `kill_switch_plan.md`
- `shadow_test_cases.csv`
- `comparison_report.md`
- `readiness_decision.json`
- `readiness_report.html`
- `improvement_roadmap.md`
- `proposal_scope.md`

All artifacts include assessment ID, pack ID, policy version, generated time,
and evidence snapshot hash where applicable.

## 16. Acceptance Tests

### Human interaction

- asks one primary question at a time;
- explains why each answer matters;
- accepts `do not know` without inventing an answer;
- resumes an interrupted assessment;
- shows an actionable next step for every blocking gap.

### Gate enforcement

- a high aggregate score cannot override a failed hard gate;
- external writes cannot be recommended without idempotency and recovery;
- missing exception owner prevents `L3` and `L4`;
- failed shadow tests prevent `L3` and `L4`;
- high-risk prohibited actions remain human boundaries;
- conflicting evidence produces a question or lower decision.

### Evidence and audit

- source hashes are checked before decision generation;
- changed evidence invalidates stale decisions;
- rule confirmation records the human confirmer;
- confirmation records role, time, authorization source, pack manifest hash,
  and prior decision hash;
- decisions are reproducible from the stored snapshot;
- no source document can inject executable policy.

### Honest refusal

- returns `not_ready` when required evidence cannot be obtained;
- distinguishes temporary gaps, poor economics, legal boundaries, technical
  impossibility, and organizational refusal;
- creates a useful report even when no implementation is recommended.

## 17. Implementation Sequence

### Phase 0: contracts and fixtures

Define assessment schemas, gate definitions, deterministic operators, sample
organizations, and expected decisions.

### Phase 1: discovery and decision

Implement interview, evidence manifests, workflow model, rule candidates, gap
register, hard-gate evaluator, readiness report, and resume support.

### Phase 2: shadow mode

Implement historical cases, human result import, comparison, thresholds,
recovery simulations, and decision invalidation.

### Phase 3: controlled pilot export

Produce signed Autopilot extension artifacts and pilot plans. Do not dispatch
external actions yet.

### Phase 4: separate runtime

After a separate design and security review, implement durable execution,
connectors, policy enforcement, kill switches, verification, and compensation.

## 18. Release Gates

Implementation cannot be called ready until:

- Japanese and English human manuals exist;
- all 22 packs have assessment fixtures;
- hard-gate behavior has negative tests;
- `not_ready` paths are tested as first-class successes;
- interrupted sessions resume without losing answers;
- stale evidence invalidates decisions;
- shadow comparison detects critical mismatches;
- installed-wheel smoke completes an assessment without source-tree imports;
- a separate reviewer confirms no external action path was introduced.

## 19. Product Language

Preferred promise:

> Identify what can be automated, resolve what is missing, automate the safe
> standard path, and stop when the evidence is not enough.

Avoid promises such as “automate everything” or “replace human judgment.” The
product differentiator is a useful path to automation plus an evidence-backed
ability to refuse unsafe or uneconomic work.
