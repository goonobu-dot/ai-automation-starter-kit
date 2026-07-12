# Daily Workflow Pack Expansion Design

Date: 2026-07-12
Status: Ready for implementation planning review

## 1. Objective

Extend the existing monthly office workspace into a shared daily office engine
that can power ten local-first daily packs in this order:

1. inquiry handling
2. sales activity
3. daily finance
4. project progress
5. attendance exceptions
6. meeting actions
7. expense completeness
8. invoice/order completeness
9. internal request backlog
10. executive digest

The expansion must preserve:

- monthly workspace compatibility;
- human approval before any final local publication;
- append-only audit records;
- bilingual Japanese and English UI/manual surfaces;
- installed-wheel smoke coverage;
- the current local-only, no-external-send product truth.

## 2. Existing Monthly Architecture Analysis

The current monthly office workspace already has the right ownership split.

- `src/ai_automation_kit/core/office_workspace_builder.py` owns safe public
  folder creation, no-follow file operations, workspace status, and trusted
  root validation.
- `src/ai_automation_kit/core/office_workspace_state.py` owns period state,
  stage transitions, answers, draft promotion, approval, and audit append.
- `src/ai_automation_kit/core/workflow_pack.py` loads a bundled monthly pack
  from a SHA-256-verified manifest and rejects unknown fields.
- `src/ai_automation_kit/core/office_workspace_server.py` owns the localhost
  API, nonce checks, token checks, and dispatch into state and Codex runner
  modules.
- `src/ai_automation_kit/core/office_workspace_ui.py` provides a self-contained
  bilingual operator UI for list and detail views.
- `scripts/release_smoke.py` and `tests/test_public_readiness.py` already treat
  the monthly workspace as a public release surface, including installed-wheel
  smoke.

Those modules should be extended, not replaced.

The current monthly implementation also exposes the exact limits that the daily
expansion must solve:

1. monthly-only naming is embedded in user-facing copy, CLI flags, and some
   state assumptions;
2. cycle validation is currently centered on `YYYY-MM`;
3. the run-result contract is effectively one draft markdown file plus missing
   questions, which is too narrow for queue-style daily artifacts;
4. the browser UI is hard-coded for a single monthly pack;
5. installed-wheel smoke proves the monthly loop only.

## 3. Approaches Considered

### A. Build a separate daily product beside `office-workspace`

This would keep the monthly path stable, but it would duplicate workspace
builder, approval, audit, runner, server, and UI code. It would also split the
documentation and release-smoke surface into two overlapping products.

### B. Generalize the existing office workspace into a cadence-aware engine

This is the selected approach. The engine remains one local product with one
security model, one approval model, one audit model, one localhost UI, and one
installed-wheel surface. Monthly becomes the compatibility baseline; daily
packs become additional bundled contracts.

### C. Route daily work through `report-wizard` instead of `office-workspace`

`report-wizard` is useful for onboarding and report drafting, but it does not
currently own the hardened approval PIN flow, audit chain, or pack-driven
workspace contract that the monthly office workspace already has. Reusing it as
the main daily product would recreate features that `office-workspace` already
owns more cleanly.

## 4. Selected Product Boundary

The daily expansion remains inside the current Phase 1A product truth.

- It is local-first and local-only.
- It drafts or prepares review packets; it does not send anything externally.
- It can classify, summarize, check completeness, and prepare action queues.
- It cannot self-approve, publish, pay, commit to customers, alter employment
  records, or perform production writes.
- Every pack ends at a human approval gate and local save.

This design deliberately does not add cloud connectors, email sending, CRM
mutation, calendar writes, payroll writes, or accounting-system writes.

## 5. Shared Daily Engine

### 5.1 Cadence-aware workspace contract

The folder contract stays recognizable so monthly users do not have to relearn
the product:

```text
Client_Name_Inquiry_Handling/
├── 00_START_HERE/
│   ├── open_this_first.html
│   └── workspace_status.json
├── 01_APPROVED_PAST_OUTPUTS/
├── 02_PAST_SUPPORTING_FILES/
├── 03_CURRENT_INPUTS/
│   └── 2026-07-12/
├── 04_QUESTIONS/
│   └── 2026-07-12/
├── 05_DRAFTS/
│   └── 2026-07-12/
├── 06_APPROVED_OUTPUTS/
│   └── 2026-07-12/
├── 07_AUDIT/
└── .system/
    ├── workspace.json
    ├── pack-manifest.json
    ├── cycles/2026-07-12/state.json
    └── runs/<run_id>/
```

The public folders do not change. The internal `.system/periods/` directory is
generalized to `.system/cycles/` so the engine can support:

- monthly IDs: `YYYY-MM`
- weekly IDs: `YYYY-Www`
- daily IDs: `YYYY-MM-DD`

Monthly public behavior remains unchanged. Existing monthly commands keep
working through compatibility wrappers.

### 5.2 Module ownership

The expansion should preserve the current module boundaries and add only the
smallest new shared primitives:

- `office_workspace_cycle.py`:
  validate cadence, parse cycle IDs, derive the next cycle, and provide
  localized cadence labels.
- `workflow_pack.py`:
  support both the current monthly pack contract and a new daily-capable pack
  contract.
- `office_workspace_builder.py`:
  create a workspace for any bundled office pack while preserving current
  monthly defaults.
- `office_workspace_state.py`:
  own generic cycle state, carry-forward metadata, multi-artifact approval, and
  monthly compatibility wrappers such as `create_period()`.
- `codex_runner.py`:
  stage a pack-specific output schema, run Codex in the existing isolated
  sandbox, and publish only validated artifact bundles.
- `office_workspace_server.py`:
  expose pack catalog and cycle-aware actions while preserving existing monthly
  routes and current-state enforcement.
- `office_workspace_ui.py`:
  stay self-contained, but become pack-aware and cadence-aware instead of
  monthly-only.
- `cli.py`:
  keep `office-workspace` as the product entrypoint and expand flags without
  breaking existing monthly calls.

### 5.3 State model

The state machine does not need a daily-specific reinvention. The existing
stages still fit daily packs:

```text
created -> inputs_ready -> reviewed -> questioning -> ready_for_run
ready_for_run -> running -> ready_for_review -> approved
running -> cancelled | failed
cancelled | failed -> ready_for_run
```

The shared state object should become cycle-based and add:

- `cadence`: `daily`, `weekly`, or `monthly`
- `cycle_id`: exact current cycle key
- `artifact_bundle`: promoted draft artifacts for review
- `approved_bundle`: approved output metadata and hashes
- `carry_forward`: explicit references to prior approved outputs or unresolved
  queues reused for the next cycle

The current monthly `period_id` fields can remain as compatibility aliases in
the JSON returned by the monthly CLI and server paths until the broader rename
is safe.

### 5.4 Run-result contract

Daily packs need more than one markdown draft. The runner output contract
should move to a bundle model:

```json
{
  "missing_questions": [
    {
      "id": "response_owner",
      "question": "Who owns customer replies for this queue today?",
      "required": true
    }
  ],
  "artifacts": [
    {
      "id": "digest",
      "relative_path": "inquiry_handling_digest.md",
      "content": "# Daily inquiry digest\n",
      "content_type": "text/markdown"
    },
    {
      "id": "reply_queue",
      "relative_path": "reply_queue.csv",
      "content": "ticket_id,priority,next_action\n",
      "content_type": "text/csv"
    }
  ]
}
```

Monthly compatibility is preserved by adapting the existing monthly result
shape into a single-artifact bundle:

- `draft_markdown` becomes one markdown artifact with the pack-declared
  relative path;
- existing monthly output schema remains valid;
- daily packs use bundled pack-specific output schemas that require
  `artifacts`.

### 5.5 Rollover and carry-forward

Daily work often contains unresolved items. The next-cycle preparation flow
should therefore support explicit carry-forward without mutating approved prior
outputs.

The engine should:

1. prepare the next cycle only after approval or an explicit operator choice;
2. allow the operator to reuse specific prior approved artifacts as style or
   context references;
3. copy or snapshot selected unresolved queue files into the next cycle's
   support manifest as declared carry-forward inputs;
4. record those carry-forward hashes in the new cycle state and audit trail.

Monthly rollover stays append-only and continues to use the current model.

### 5.6 Bilingual UI and manual strategy

The UI should move from monthly-specific strings to shared bilingual base
strings plus pack metadata:

- generic labels:
  workspace, current cycle, inspect, answer, generate, approve, next cycle;
- cadence-aware labels:
  next day, next week, next month;
- pack labels:
  display name, artifact names, input examples, pack warnings.

Monthly copy stays intact for the existing monthly pack. Daily packs provide
Japanese and English display names and short operator hints in pack metadata or
adjacent bundled copy resources. Public manuals should be paired HTML files,
never mixed-language pages.

### 5.7 Approval and audit

The current approval model remains the business boundary:

- named approver plus local approval PIN;
- append-only audit log in `07_AUDIT/audit.jsonl`;
- approval lock around publication and state save;
- no self-approval by the AI agent.

For daily bundles, each audit entry should also record:

- bundle hash;
- per-artifact hashes;
- carry-forward source hashes;
- pack hash and schema version;
- prior audit-entry hash.

## 6. Backward Compatibility Rules

Monthly compatibility is a release gate, not a best-effort goal.

1. `monthly-report` remains bundled and unchanged from the operator's point of
   view.
2. Existing monthly CLI flows keep working:
   `office-workspace create --period YYYY-MM`,
   `status --workspace ... --json`,
   `inspect --workspace ... --period YYYY-MM`,
   `serve --root ...`.
3. Existing monthly workspace folder names remain unchanged.
4. Existing monthly state transitions, approval behavior, audit behavior, and
   no-follow filesystem rules remain unchanged.
5. Existing monthly installed-wheel smoke remains mandatory and must still pass
   before any daily pack is called release-ready.

The expansion may add new flags such as `--pack` and `--cycle`, but it must not
remove or silently reinterpret the current monthly flags.

## 7. Workflow Pack Contract

The pack system should gain a backward-compatible daily-capable contract.

### 7.1 Pack schema direction

- keep support for the current monthly schema version;
- add a new pack schema version for cadence-aware office packs;
- require every bundled pack to declare cadence, outputs, approval role, and
  prohibited actions;
- continue to reject unknown fields, external URLs, executable declarations,
  absolute paths, path traversal, and free-form command injection.

A representative daily pack payload should look like:

```json
{
  "schema_version": 2,
  "id": "daily-inquiry-handling",
  "display_name": {"ja": "日次問い合わせ対応", "en": "Daily Inquiry Handling"},
  "category": "operations",
  "cadence": "daily",
  "risk_tier": "medium",
  "business_outcome": "Prepare a local inquiry triage digest and reply queue",
  "inputs": [
    {
      "id": "inquiry_export",
      "required": true,
      "accepted_extensions": [".csv", ".xlsx", ".json", ".md", ".txt"]
    },
    {
      "id": "reference_notes",
      "required": false,
      "accepted_extensions": [".md", ".txt", ".pdf", ".docx"]
    }
  ],
  "questions": [
    {"id": "response_owner", "type": "short_text", "required": true, "max_length": 200},
    {"id": "sla_rule", "type": "short_text", "required": false, "max_length": 200}
  ],
  "prompt_template_id": "daily-inquiry-handling-v1",
  "allowed_prompt_variables": ["cycle_id", "source_manifest", "answers", "carry_forward"],
  "outputs": [
    {"id": "digest", "relative_path": "inquiry_handling_digest.md", "max_bytes": 1048576},
    {"id": "reply_queue", "relative_path": "reply_queue.csv", "max_bytes": 1048576}
  ],
  "approval": {"required": true, "role": "inquiry_owner"},
  "prohibited_actions": ["external_send", "publish", "payment", "production_write", "self_approve"],
  "success_metrics": ["triage_minutes", "missing_owner_count", "same_day_followup_rate"]
}
```

### 7.2 Pack order and scope

The first ten daily packs should be implemented in this exact order.

| Order | Pack ID | Outcome | Main approved artifacts | Risk tier |
| --- | --- | --- | --- | --- |
| 1 | `daily-inquiry-handling` | Triage incoming inquiries and prepare local reply queue | digest + reply queue | medium |
| 2 | `daily-sales-activity` | Summarize activity, gaps, and follow-ups | digest + follow-up queue | medium |
| 3 | `daily-finance` | Summarize cash movements and exceptions without payment action | digest + exception queue | medium |
| 4 | `daily-project-progress` | Summarize status, blockers, and next owners | digest + blockers queue | low |
| 5 | `daily-attendance-exceptions` | Identify missing punches, leave anomalies, or schedule gaps | digest + exception queue | medium |
| 6 | `daily-meeting-actions` | Extract action items and owners from meeting notes | digest + action register | low |
| 7 | `daily-expense-completeness` | Check missing receipts and incomplete entries | digest + completeness queue | medium |
| 8 | `daily-invoice-order-completeness` | Check missing invoice, order, or support documents | digest + completeness queue | medium |
| 9 | `daily-internal-request-backlog` | Summarize internal request backlog and aging | digest + backlog queue | low |
| 10 | `daily-executive-digest` | Roll up important daily signals for an executive reader | executive digest | medium |

## 8. Pack-by-Pack Design Notes

### 8.1 Inquiry handling

- Inputs: inquiry export, escalation notes, FAQ/policy notes, yesterday carry
  forward queue.
- Questions: response owner, same-day SLA, escalation policy.
- Outputs: `inquiry_handling_digest.md`, `reply_queue.csv`.
- Guardrails: no sending, no final customer promises, no hidden prioritization
  rules without evidence.

### 8.2 Sales activity

- Inputs: CRM export, call notes, pipeline notes, prior-day follow-up queue.
- Questions: sales owner, today's priority segment, stale-lead threshold.
- Outputs: `sales_activity_digest.md`, `sales_followups.csv`.
- Guardrails: no CRM mutation, no fabricated deal stage changes, no revenue
  commitment.

### 8.3 Daily finance

- Inputs: transaction export, deposit log, AP/AR notes, bank summary.
- Questions: finance owner, exception threshold, cash-cutoff note.
- Outputs: `daily_finance_digest.md`, `cash_exceptions.csv`.
- Guardrails: no payment execution, no ledger write, no bank instruction.

### 8.4 Project progress

- Inputs: task export, milestone notes, blocker notes, yesterday summary.
- Questions: project owner, milestone priority, blocker escalation path.
- Outputs: `project_progress_digest.md`, `project_blockers.csv`.
- Guardrails: no status fabrication, no deadline changes without source support.

### 8.5 Attendance exceptions

- Inputs: attendance export, shift roster, leave notes, manager exception list.
- Questions: people owner, exception rule, escalation owner.
- Outputs: `attendance_exceptions_digest.md`, `attendance_exceptions.csv`.
- Guardrails: no payroll write, no employment decision, no disciplinary action.

### 8.6 Meeting actions

- Inputs: meeting minutes, transcript excerpts, agenda, prior action list.
- Questions: default owner policy, due-date convention.
- Outputs: `meeting_actions_digest.md`, `meeting_action_register.csv`.
- Guardrails: unresolved or ambiguous actions stay marked unresolved.

### 8.7 Expense completeness

- Inputs: expense export, receipt checklist, policy notes, prior unresolved
  queue.
- Questions: expense owner, receipt deadline, policy exceptions.
- Outputs: `expense_completeness_digest.md`, `expense_missing_receipts.csv`.
- Guardrails: no reimbursement approval, no accounting write-back.

### 8.8 Invoice/order completeness

- Inputs: invoice/order export, support document folder, approval checklist.
- Questions: finance/ops owner, completeness rule, escalation owner.
- Outputs: `invoice_order_completeness_digest.md`,
  `invoice_order_completeness_queue.csv`.
- Guardrails: no invoice issuance, no order release, no vendor commitment.

### 8.9 Internal request backlog

- Inputs: ticket export, request notes, aging rules, prior backlog snapshot.
- Questions: backlog owner, priority convention, stale threshold.
- Outputs: `internal_request_backlog_digest.md`, `internal_request_backlog.csv`.
- Guardrails: no ticket mutation, no approval decision, no routing outside
  declared rules.

### 8.10 Executive digest

- Inputs: approved outputs from the other daily packs, leadership notes, manual
  escalations.
- Questions: executive audience, must-include metrics, red-flag threshold.
- Outputs: `executive_digest.md`.
- Guardrails: no unsupported claims; any missing source pack is surfaced as an
  unresolved item.

## 9. Delivery Phases

### Phase 1: shared daily engine foundation

- cadence-aware cycle helpers;
- cycle state generalized from monthly periods;
- multi-artifact bundle promotion and approval;
- pack-aware CLI/server/UI;
- monthly regression preserved.

### Phase 2: first five daily packs

- inquiry handling;
- sales activity;
- daily finance;
- project progress;
- attendance exceptions.

### Phase 3: remaining five daily packs

- meeting actions;
- expense completeness;
- invoice/order completeness;
- internal request backlog;
- executive digest.

### Phase 4: public surfaces and release gates

- bilingual HTML manuals;
- README and docs index updates;
- installed-wheel smoke for monthly plus daily;
- public readiness and release audit updates.

## 10. Safety and Error Handling

- original inputs remain read-only;
- existing outputs are never overwritten;
- approval requires the named human approver and PIN;
- carry-forward is explicit and hashed, never implied by hidden mutation;
- medium-risk packs display domain warnings in both languages;
- missing evidence produces questions or unresolved items, not invented facts;
- external sending, payment, self-approval, and production writes stay blocked
  at the pack-contract level and the UI wording level.

## 11. Testing and Release Gates

The daily expansion is complete only if all of the following are true:

1. current monthly unit, integration, server, UI, public-readiness, and
   installed-wheel tests still pass;
2. daily cadence parsing and rollover are covered by focused unit tests;
3. artifact-bundle promotion and approval are covered by collision and audit
   tests;
4. each of the ten packs has at least one focused pack-loading test, one
   synthetic cycle integration test, and one bilingual UI label assertion;
5. installed-wheel smoke exercises the existing monthly flow and at least one
   representative daily pack flow without source-tree leakage;
6. Japanese and English manuals are separate and linked correctly;
7. `git diff --check`, focused pytest targets, full pytest, public release
   audit, and release smoke all pass fresh.

## 12. Success Criteria

The product succeeds when a beginner can still complete the current monthly
workspace loop unchanged, and can also create a daily workspace for any of the
ten ordered packs, inspect today's inputs, answer one missing question at a
time, generate a review packet, approve it locally, and prepare the next day
without leaving the same local UI and safety model.
