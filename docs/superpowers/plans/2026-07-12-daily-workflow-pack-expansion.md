# Daily Workflow Pack Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use `subagent-driven-development` or `executing-plans`. Steps use checkbox syntax and must be completed in order. Do not collapse pack tasks out of sequence.

**Goal:** Extend the current monthly office workspace into a shared daily engine while preserving monthly compatibility, human approval, audit integrity, bilingual UI/manuals, and installed-wheel smoke. Implement the ten daily packs in this exact order: inquiry handling, sales activity, daily finance, project progress, attendance exceptions, meeting actions, expense completeness, invoice/order completeness, internal request backlog, executive digest.

**Architecture:** Generalize the current monthly `office-workspace` path into a cadence-aware cycle engine. Keep the current builder/state/runner/server/UI split, preserve current monthly CLI behavior as a compatibility layer, and add pack-driven daily workspaces that publish validated artifact bundles into the same local approval flow.

**Tech Stack:** Python 3.9 standard library, existing no-follow filesystem safety primitives, current `office_workspace_*` modules, current bundled workflow-pack manifest model, self-contained HTML/CSS/JavaScript UI, pytest, and installed-wheel release smoke.

---

## Delivery Roles

- GPT-5.4 workers implement the bounded tasks below with named write sets.
- GPT-5.5 performs read-only correctness, security, and compatibility reviews
  after Tasks 4, 9, and 15.
- GPT-5.6 directs sequencing, resolves interfaces, runs final verification, and
  decides whether the release gate passes.
- No worker may remove monthly compatibility, bypass approval/sandbox rules, or
  convert the product into an external-send workflow.

## File Map

| File | Responsibility |
| --- | --- |
| `src/ai_automation_kit/core/workflow_pack.py` | backward-compatible pack validation and bundled-pack loading |
| `src/ai_automation_kit/core/office_workspace_cycle.py` | cadence parsing, cycle validation, next-cycle calculation |
| `src/ai_automation_kit/core/office_workspace_builder.py` | workspace creation and public-folder ownership |
| `src/ai_automation_kit/core/office_workspace_state.py` | cycle state, question loop, artifact promotion, approval, audit |
| `src/ai_automation_kit/core/codex_runner.py` | isolated run staging and pack-specific output validation |
| `src/ai_automation_kit/core/office_workspace_server.py` | secure localhost API |
| `src/ai_automation_kit/core/office_workspace_ui.py` | bilingual pack-aware operator UI |
| `src/ai_automation_kit/cli.py` | `office-workspace` command surface |
| `src/ai_automation_kit/packs/*.json` | bundled pack definitions, prompt templates, output schemas |
| `scripts/release_smoke.py` | installed-wheel smoke for monthly and daily office workspaces |
| `tests/test_workflow_pack.py` | pack contract and manifest trust tests |
| `tests/test_office_workspace.py` | builder/state/approval/audit tests |
| `tests/test_office_workspace_server.py` | server/API integration tests |
| `tests/test_office_workspace_ui.py` | localized UI contract tests |
| `tests/test_public_readiness.py` | public-surface and smoke-coverage assertions |

## Task 1: Backward-Compatible Cadence and Pack Contract

**Owner:** GPT-5.4 worker A

**Files:**
- Modify: `src/ai_automation_kit/core/workflow_pack.py`
- Create: `src/ai_automation_kit/core/office_workspace_cycle.py`
- Modify: `tests/test_workflow_pack.py`

- [ ] **Step 1: Write failing compatibility tests**

Add tests that prove:

- the current `monthly-report` pack still loads unchanged;
- a new daily pack schema can declare `cadence: daily`;
- invalid cadence or output bundle declarations are rejected;
- unknown fields still fail closed.

Run: `python3 -m pytest -q tests/test_workflow_pack.py`

Expected: failures because cadence-aware pack support does not exist yet.

- [ ] **Step 2: Implement a shared cycle helper**

Create `office_workspace_cycle.py` with:

- `validate_cycle_id(cadence: str, cycle_id: str) -> str`
- `next_cycle_id(cadence: str, cycle_id: str) -> str`
- strict support for `daily`, `weekly`, and `monthly`
- no implicit timezone or locale mutation

- [ ] **Step 3: Extend pack loading without breaking monthly**

Update `workflow_pack.py` so it:

- supports the current monthly schema as-is;
- supports a new daily-capable schema version with `cadence`;
- keeps SHA-256 manifest verification;
- continues to reject unknown fields, absolute paths, external URLs, path
  traversal, and prohibited-action omissions.

- [ ] **Step 4: Pass focused tests**

Run: `python3 -m pytest -q tests/test_workflow_pack.py`

Expected: all tests pass and `monthly-report` remains valid.

## Task 2: Generic Cycle State with Monthly Wrappers

**Owner:** GPT-5.4 worker B

**Files:**
- Modify: `src/ai_automation_kit/core/office_workspace_builder.py`
- Modify: `src/ai_automation_kit/core/office_workspace_state.py`
- Modify: `tests/test_office_workspace.py`

- [ ] **Step 1: Write failing cycle tests**

Add tests for:

- daily cycle creation under `.system/cycles/<YYYY-MM-DD>/`;
- monthly wrapper compatibility through existing `create_period()` and
  `inspect_period()`;
- next-cycle preparation for daily and monthly cadences;
- invalid daily IDs and cross-cadence misuse.

Run: `python3 -m pytest -q tests/test_office_workspace.py -k "cycle or rollover or period"`

Expected: failures because state is still monthly-period-specific.

- [ ] **Step 2: Generalize internal state to cycles**

Implement generic cycle state ownership and keep monthly wrappers:

- `create_cycle(...)`
- `inspect_cycle(...)`
- `save_cycle_answer(...)`
- `approve_cycle_bundle(...)`

Retain current public monthly helpers as thin adapters for compatibility.

- [ ] **Step 3: Preserve filesystem and audit safety**

Keep all current guarantees:

- atomic JSON writes;
- no-follow path handling;
- append-only approval and rollover;
- approval lock behavior;
- no overwrite on artifact publication.

- [ ] **Step 4: Pass focused tests**

Run: `python3 -m pytest -q tests/test_office_workspace.py`

Expected: monthly tests still pass and new daily cycle tests pass.

## Task 3: Multi-Artifact Run Result and Approval Bundle

**Owner:** GPT-5.4 worker C

**Files:**
- Modify: `src/ai_automation_kit/core/codex_runner.py`
- Modify: `src/ai_automation_kit/core/office_workspace_state.py`
- Modify: `tests/test_office_workspace.py`
- Modify: `tests/test_codex_runner.py`

- [ ] **Step 1: Write failing artifact-bundle tests**

Add tests for:

- monthly single-draft results still promote correctly;
- daily results can publish multiple staged artifacts;
- artifact collisions do not overwrite prior files;
- approval records bundle hashes and per-artifact hashes.

Run: `python3 -m pytest -q tests/test_codex_runner.py tests/test_office_workspace.py -k "artifact or bundle or approve"`

Expected: failures because only `draft_markdown` is supported today.

- [ ] **Step 2: Add bundle-aware validation**

Update the runner/state boundary so it accepts:

- current monthly output schema and adapter path;
- pack-specific daily output schemas requiring `artifacts`;
- content-type and relative-path validation against pack outputs.

- [ ] **Step 3: Keep approval semantics unchanged**

Approval still requires:

- named approver;
- local PIN verification;
- append-only audit entry;
- local publication only.

The difference is that approval now publishes one validated artifact bundle
instead of assuming one markdown file.

- [ ] **Step 4: Pass focused tests**

Run: `python3 -m pytest -q tests/test_codex_runner.py tests/test_office_workspace.py`

Expected: bundle tests pass and monthly tests remain green.

## Task 4: CLI, Server, and UI Foundation for Pack-Aware Daily Workspaces

**Owner:** GPT-5.4 worker D

**Files:**
- Modify: `src/ai_automation_kit/cli.py`
- Modify: `src/ai_automation_kit/core/office_workspace_server.py`
- Modify: `src/ai_automation_kit/core/office_workspace_ui.py`
- Modify: `tests/test_office_workspace_server.py`
- Modify: `tests/test_office_workspace_ui.py`

- [ ] **Step 1: Write failing interface tests**

Add tests for:

- `office-workspace create --pack <pack_id> --cycle <cycle_id>`;
- existing monthly `--period` flow still works unchanged;
- server payload includes bundled pack choices and cadence-aware next-action
  text;
- UI localizes `next day`, `next week`, and `next month` correctly.

Run: `python3 -m pytest -q tests/test_office_workspace_server.py tests/test_office_workspace_ui.py`

Expected: failures because the server and UI are monthly-only.

- [ ] **Step 2: Expand the CLI without breaking old monthly calls**

Add:

- `--pack` to workspace creation with default `monthly-report`;
- `--cycle` as the generic cycle flag;
- backward-compatible monthly aliases where needed.

- [ ] **Step 3: Generalize UI copy and detail rendering**

Keep the current two-view product, but make it pack-aware and cadence-aware.
Do not regress:

- self-contained HTML;
- no language leakage;
- local-only API usage;
- same-origin token and nonce handling;
- beginner-first wording.

- [ ] **Step 4: Pass focused tests**

Run: `python3 -m pytest -q tests/test_office_workspace_server.py tests/test_office_workspace_ui.py`

Expected: monthly tests still pass and new daily interface tests pass.

- [ ] **Step 5: GPT-5.5 review checkpoint**

Review `workflow_pack`, `office_workspace_cycle`, `office_workspace_state`,
`office_workspace_server`, `office_workspace_ui`, and `cli.py` for correctness,
compatibility, security, and hidden monthly regressions before pack work
begins.

## Task 5: Pack 1 - Inquiry Handling

**Owner:** GPT-5.4 worker E

**Files:**
- Create: `src/ai_automation_kit/packs/daily_inquiry_handling.json`
- Create: `src/ai_automation_kit/packs/daily_inquiry_handling_prompt.json`
- Create: `src/ai_automation_kit/packs/daily_inquiry_handling_output.schema.json`
- Modify: `src/ai_automation_kit/packs/manifest.json`
- Modify: `tests/test_workflow_pack.py`
- Create or Modify: `tests/test_office_workspace_daily_packs.py`

- [ ] **Step 1: Write failing inquiry-pack tests**

Cover pack loading, allowed output files, bilingual display names, and one
synthetic daily cycle that yields a digest plus reply queue.

- [ ] **Step 2: Implement bundled pack resources**

Pack contract:

- `pack_id`: `daily-inquiry-handling`
- outputs:
  `inquiry_handling_digest.md`, `reply_queue.csv`
- required question:
  `response_owner`

- [ ] **Step 3: Run focused tests**

Run: `python3 -m pytest -q tests/test_workflow_pack.py tests/test_office_workspace_daily_packs.py -k inquiry`

Expected: pack tests pass.

## Task 6: Pack 2 - Sales Activity

**Owner:** GPT-5.4 worker E

**Files:**
- Create: `src/ai_automation_kit/packs/daily_sales_activity.json`
- Create: `src/ai_automation_kit/packs/daily_sales_activity_prompt.json`
- Create: `src/ai_automation_kit/packs/daily_sales_activity_output.schema.json`
- Modify: `src/ai_automation_kit/packs/manifest.json`
- Modify: `tests/test_workflow_pack.py`
- Modify: `tests/test_office_workspace_daily_packs.py`

- [ ] **Step 1: Write failing sales-pack tests**

Cover digest plus follow-up queue generation, stale-lead warnings, and no-CRM
mutation wording.

- [ ] **Step 2: Implement bundled pack resources**

Outputs:

- `sales_activity_digest.md`
- `sales_followups.csv`

- [ ] **Step 3: Run focused tests**

Run: `python3 -m pytest -q tests/test_workflow_pack.py tests/test_office_workspace_daily_packs.py -k sales`

Expected: pack tests pass.

## Task 7: Pack 3 - Daily Finance

**Owner:** GPT-5.4 worker F

**Files:**
- Create: `src/ai_automation_kit/packs/daily_finance.json`
- Create: `src/ai_automation_kit/packs/daily_finance_prompt.json`
- Create: `src/ai_automation_kit/packs/daily_finance_output.schema.json`
- Modify: `src/ai_automation_kit/packs/manifest.json`
- Modify: `tests/test_workflow_pack.py`
- Modify: `tests/test_office_workspace_daily_packs.py`

- [ ] **Step 1: Write failing daily-finance tests**

Cover digest plus exception queue generation and explicit no-payment guardrails.

- [ ] **Step 2: Implement bundled pack resources**

Outputs:

- `daily_finance_digest.md`
- `cash_exceptions.csv`

- [ ] **Step 3: Run focused tests**

Run: `python3 -m pytest -q tests/test_workflow_pack.py tests/test_office_workspace_daily_packs.py -k finance`

Expected: pack tests pass.

## Task 8: Pack 4 - Project Progress

**Owner:** GPT-5.4 worker F

**Files:**
- Create: `src/ai_automation_kit/packs/daily_project_progress.json`
- Create: `src/ai_automation_kit/packs/daily_project_progress_prompt.json`
- Create: `src/ai_automation_kit/packs/daily_project_progress_output.schema.json`
- Modify: `src/ai_automation_kit/packs/manifest.json`
- Modify: `tests/test_workflow_pack.py`
- Modify: `tests/test_office_workspace_daily_packs.py`

- [ ] **Step 1: Write failing project-progress tests**

Cover blocker extraction, owner preservation, and unresolved-item handling.

- [ ] **Step 2: Implement bundled pack resources**

Outputs:

- `project_progress_digest.md`
- `project_blockers.csv`

- [ ] **Step 3: Run focused tests**

Run: `python3 -m pytest -q tests/test_workflow_pack.py tests/test_office_workspace_daily_packs.py -k project`

Expected: pack tests pass.

## Task 9: Pack 5 - Attendance Exceptions

**Owner:** GPT-5.4 worker G

**Files:**
- Create: `src/ai_automation_kit/packs/daily_attendance_exceptions.json`
- Create: `src/ai_automation_kit/packs/daily_attendance_exceptions_prompt.json`
- Create: `src/ai_automation_kit/packs/daily_attendance_exceptions_output.schema.json`
- Modify: `src/ai_automation_kit/packs/manifest.json`
- Modify: `tests/test_workflow_pack.py`
- Modify: `tests/test_office_workspace_daily_packs.py`

- [ ] **Step 1: Write failing attendance tests**

Cover missing-punch detection, explicit employment-risk wording, and no-payroll
mutation boundaries.

- [ ] **Step 2: Implement bundled pack resources**

Outputs:

- `attendance_exceptions_digest.md`
- `attendance_exceptions.csv`

- [ ] **Step 3: Run focused tests**

Run: `python3 -m pytest -q tests/test_workflow_pack.py tests/test_office_workspace_daily_packs.py -k attendance`

Expected: pack tests pass.

- [ ] **Step 4: GPT-5.5 review checkpoint**

Review all five implemented daily packs for pack-contract drift, confusing
question design, and medium-risk wording before continuing to the second half.

## Task 10: Pack 6 - Meeting Actions

**Owner:** GPT-5.4 worker G

**Files:**
- Create: `src/ai_automation_kit/packs/daily_meeting_actions.json`
- Create: `src/ai_automation_kit/packs/daily_meeting_actions_prompt.json`
- Create: `src/ai_automation_kit/packs/daily_meeting_actions_output.schema.json`
- Modify: `src/ai_automation_kit/packs/manifest.json`
- Modify: `tests/test_workflow_pack.py`
- Modify: `tests/test_office_workspace_daily_packs.py`

- [ ] **Step 1: Write failing meeting-actions tests**

Cover action extraction, ambiguous-owner handling, and prior-action carry
forward.

- [ ] **Step 2: Implement bundled pack resources**

Outputs:

- `meeting_actions_digest.md`
- `meeting_action_register.csv`

- [ ] **Step 3: Run focused tests**

Run: `python3 -m pytest -q tests/test_workflow_pack.py tests/test_office_workspace_daily_packs.py -k meeting`

Expected: pack tests pass.

## Task 11: Pack 7 - Expense Completeness

**Owner:** GPT-5.4 worker H

**Files:**
- Create: `src/ai_automation_kit/packs/daily_expense_completeness.json`
- Create: `src/ai_automation_kit/packs/daily_expense_completeness_prompt.json`
- Create: `src/ai_automation_kit/packs/daily_expense_completeness_output.schema.json`
- Modify: `src/ai_automation_kit/packs/manifest.json`
- Modify: `tests/test_workflow_pack.py`
- Modify: `tests/test_office_workspace_daily_packs.py`

- [ ] **Step 1: Write failing expense tests**

Cover receipt gaps, exception reasons, and explicit no-reimbursement-approval
boundaries.

- [ ] **Step 2: Implement bundled pack resources**

Outputs:

- `expense_completeness_digest.md`
- `expense_missing_receipts.csv`

- [ ] **Step 3: Run focused tests**

Run: `python3 -m pytest -q tests/test_workflow_pack.py tests/test_office_workspace_daily_packs.py -k expense`

Expected: pack tests pass.

## Task 12: Pack 8 - Invoice/Order Completeness

**Owner:** GPT-5.4 worker H

**Files:**
- Create: `src/ai_automation_kit/packs/daily_invoice_order_completeness.json`
- Create: `src/ai_automation_kit/packs/daily_invoice_order_completeness_prompt.json`
- Create: `src/ai_automation_kit/packs/daily_invoice_order_completeness_output.schema.json`
- Modify: `src/ai_automation_kit/packs/manifest.json`
- Modify: `tests/test_workflow_pack.py`
- Modify: `tests/test_office_workspace_daily_packs.py`

- [ ] **Step 1: Write failing invoice/order tests**

Cover missing-support-document queues and explicit no-issuance/no-release
boundaries.

- [ ] **Step 2: Implement bundled pack resources**

Outputs:

- `invoice_order_completeness_digest.md`
- `invoice_order_completeness_queue.csv`

- [ ] **Step 3: Run focused tests**

Run: `python3 -m pytest -q tests/test_workflow_pack.py tests/test_office_workspace_daily_packs.py -k invoice`

Expected: pack tests pass.

## Task 13: Pack 9 - Internal Request Backlog

**Owner:** GPT-5.4 worker I

**Files:**
- Create: `src/ai_automation_kit/packs/daily_internal_request_backlog.json`
- Create: `src/ai_automation_kit/packs/daily_internal_request_backlog_prompt.json`
- Create: `src/ai_automation_kit/packs/daily_internal_request_backlog_output.schema.json`
- Modify: `src/ai_automation_kit/packs/manifest.json`
- Modify: `tests/test_workflow_pack.py`
- Modify: `tests/test_office_workspace_daily_packs.py`

- [ ] **Step 1: Write failing backlog tests**

Cover aging summaries, queue ordering, and unresolved-priority questions.

- [ ] **Step 2: Implement bundled pack resources**

Outputs:

- `internal_request_backlog_digest.md`
- `internal_request_backlog.csv`

- [ ] **Step 3: Run focused tests**

Run: `python3 -m pytest -q tests/test_workflow_pack.py tests/test_office_workspace_daily_packs.py -k backlog`

Expected: pack tests pass.

## Task 14: Pack 10 - Executive Digest

**Owner:** GPT-5.4 worker I

**Files:**
- Create: `src/ai_automation_kit/packs/daily_executive_digest.json`
- Create: `src/ai_automation_kit/packs/daily_executive_digest_prompt.json`
- Create: `src/ai_automation_kit/packs/daily_executive_digest_output.schema.json`
- Modify: `src/ai_automation_kit/packs/manifest.json`
- Modify: `tests/test_workflow_pack.py`
- Modify: `tests/test_office_workspace_daily_packs.py`

- [ ] **Step 1: Write failing executive-digest tests**

Cover roll-up from prior approved daily outputs, missing-source warnings, and a
single approved executive digest artifact.

- [ ] **Step 2: Implement bundled pack resources**

Output:

- `executive_digest.md`

- [ ] **Step 3: Run focused tests**

Run: `python3 -m pytest -q tests/test_workflow_pack.py tests/test_office_workspace_daily_packs.py -k executive`

Expected: pack tests pass.

## Task 15: Bilingual Manuals, Installed-Wheel Smoke, and Public Release Surface

**Owner:** GPT-5.4 worker J for docs/tests; GPT-5.6 for final integration

**Files:**
- Modify: `README.md`
- Modify: `docs/INDEX.md`
- Create: `docs/office-workspace-daily.ja.html`
- Create: `docs/office-workspace-daily.html`
- Modify: `scripts/release_smoke.py`
- Modify: `scripts/public_release_audit.py`
- Modify: `tests/test_public_readiness.py`

- [ ] **Step 1: Add failing public-surface tests**

Require:

- separate Japanese and English daily manuals;
- links from README and docs index;
- installed-wheel smoke snippets for monthly and daily office workspaces;
- public readiness assertions that monthly compatibility remains present.

Run: `python3 -m pytest -q tests/test_public_readiness.py`

Expected: failures because the daily public surface does not exist yet.

- [ ] **Step 2: Write daily manuals**

Manuals must explain:

- how daily packs differ from monthly;
- how to create a daily workspace with Codex;
- how to place current inputs and carry-forward files;
- how inspect, answer, generate, approve, and next-day preparation work;
- the honest human-approval and no-external-send boundary.

- [ ] **Step 3: Extend installed-wheel smoke without replacing monthly smoke**

The smoke suite must:

1. keep the existing monthly office-workspace installed-wheel flow;
2. add one representative daily pack installed-wheel flow, preferably
   `daily-inquiry-handling`;
3. verify that the installed CLI, not the source tree, drives the smoke path;
4. prove the approved artifact hashes and clean server shutdown.

- [ ] **Step 4: Run focused and full verification**

```bash
python3 -m pytest -q tests/test_workflow_pack.py tests/test_office_workspace.py tests/test_codex_runner.py tests/test_office_workspace_server.py tests/test_office_workspace_ui.py tests/test_office_workspace_daily_packs.py
python3 -m pytest -q tests/test_public_readiness.py
python3 -m pytest -q
python3 scripts/public_release_audit.py
python3 scripts/release_smoke.py --skip-github --output .tmp/release-smoke-office-workspace-daily
git diff --check
```

Expected: all commands exit zero.

- [ ] **Step 5: GPT-5.5 final review**

Review the full daily-expansion diff for:

- monthly regression;
- approval/audit regression;
- pack-order compliance;
- language leakage;
- installed-wheel false positives;
- unsupported implicit external-action behavior.

Fix findings, rerun focused tests, then rerun the full verification once.

## Director Completion Gate

GPT-5.6 confirms:

1. monthly compatibility tests still pass fresh;
2. all ten daily packs were implemented in the required order;
3. the installed-wheel smoke covers both monthly and daily office-workspace
   flows;
4. GPT-5.5 has no unresolved Critical or Important findings;
5. `git status --short` is clean except for intentionally uncommitted release
   notes or ignored `.tmp` outputs.

Only then may the branch be considered ready for merge.
