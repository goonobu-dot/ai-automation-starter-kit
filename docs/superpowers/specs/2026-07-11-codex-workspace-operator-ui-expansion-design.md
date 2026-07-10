# Codex Workspace and White-Collar Operator UI Expansion Design

Date: 2026-07-11
Status: Ready for user written-spec review

## 1. Objective

Make Codex the installation and customization assistant, while making a local
browser UI the normal daily operating surface. A beginner should not need to
remember commands, folder names, or prompts after setup.

The first complete Phase 1A product is monthly report preparation. Daily,
weekly, and KPI reports follow in Phase 1B. The same workspace contract and
operator UI will then support high-frequency white-collar document, triage,
reporting, and follow-up work in Japan and internationally.

The product promise is:

> Install Codex, open this GitHub project, ask Codex to set up the work, place
> approved files in the folders Codex identifies, and use the local UI to
> prepare reviewable outputs.

It is not a promise of unattended business decisions or automatic external
sending.

## 2. Evidence and Selection Principles

The expansion targets are based on recurring work rather than novelty.

- Japan's Ministry of Health, Labour and Welfare `job tag` describes general
  office work as document creation and organization, email handling, order and
  purchase slips, ledgers, data entry, and internal forms. It also separates
  general administration, HR, reception, accounting, sales administration,
  finance, trade, planning, production administration, healthcare
  administration, and call-center work.
- The U.S. Bureau of Labor Statistics reported 17.75 million office and
  administrative support jobs in May 2025, including more than 3.28 million
  secretaries and administrative assistants.
- OECD research identifies writing, interpretation, and administrative tasks
  as common generative-AI use areas in white-collar work.
- OpenAI documents `codex exec` as a stable non-interactive command and supports
  limiting the working directory and sandbox policy.

Primary references:

- https://shigoto.mhlw.go.jp/User/OfficeOccupations
- https://shigoto.mhlw.go.jp/User/Search/Field
- https://www.bls.gov/news.release/ocwage.t01.htm
- https://www.oecd.org/content/dam/oecd/en/publications/reports/2025/06/is-generative-ai-a-general-purpose-technology_6c76e7b2/704e2d12-en.pdf
- https://developers.openai.com/codex/cli/reference/

Every workflow must pass these selection gates:

1. It occurs repeatedly: daily, weekly, monthly, or per customer/request.
2. It has identifiable input files or rows.
3. It produces a reviewable document, queue, checklist, or draft.
4. A human approval owner can be named.
5. It can begin without a cloud connector or external API.
6. It has a believable paid setup or support offer for a small business.
7. Legal, medical, employment, payment, and customer commitments remain human
   decisions.

## 3. Approaches Considered

### A. A separate application for every workflow

This produces tailored screens, but creates duplicated code, inconsistent
safety, and an impossible maintenance burden.

### B. One operator UI with installable workflow packs

This is the selected approach. One engine owns folder setup, intake, Codex
execution, questions, drafts, approvals, and audit records. Workflow packs
define labels, accepted inputs, questions, prompts, outputs, and approval rules.

### C. A generic chat that invents each workflow from scratch

This is flexible but too unpredictable for beginners. It makes folder names,
outputs, and safety behavior inconsistent and is difficult to test.

## 4. User Journey

### 4.1 Customer setup

1. The service provider installs ChatGPT and Codex and completes Codex login.
2. Codex clones or opens this GitHub repository.
3. The customer says: `このプロジェクトで業務自動化をセットアップして`.
4. Codex reads `START_WITH_CODEX.ja.md` and the repository `AGENTS.md`.
5. Codex asks one question at a time: business task, workspace location,
   reporting cadence, language, and approval owner.
6. Codex runs the deterministic workspace builder.
7. Codex opens the local operator UI and tells the customer exactly which files
   belong in each folder.

### 4.2 Normal daily or monthly use

1. Open the desktop shortcut or saved local UI address.
2. Select an installed workflow.
3. Put current files in the clearly named input folder or upload them in the UI.
4. Press `資料を確認`.
5. Resolve visible warnings or answer one missing-information question.
6. Press `下書きを作成`.
7. Review provenance, unresolved items, and the draft.
8. Press `承認して完成版へ保存`.

### 4.3 Period rollover

The UI provides `次の期間を準備` after approval. It creates the next dated
input, draft, question, and approved-output folders without deleting the prior
period. Approved prior outputs can become style references only after the user
confirms them.

## 5. Workspace Contract

Codex creates one workspace per client and business workflow:

```text
Client_Name_Monthly_Report/
├── 00_START_HERE/
│   ├── open_this_first.html
│   └── workspace_status.json
├── 01_APPROVED_PAST_OUTPUTS/
├── 02_PAST_SUPPORTING_FILES/
├── 03_CURRENT_INPUTS/
│   └── 2026-07/
├── 04_QUESTIONS/
│   └── 2026-07/
├── 05_DRAFTS/
│   └── 2026-07/
├── 06_APPROVED_OUTPUTS/
│   └── 2026-07/
├── 07_AUDIT/
└── .system/
    ├── workspace.json
    ├── pack-manifest.json
    ├── periods/2026-07/state.json
    └── runs/<run_id>/
        ├── input_snapshot/
        ├── sandbox/
        ├── output_staging/
        └── events.jsonl
```

Display names are localized in the UI. Stable internal folder identifiers stay
machine-readable. The UI must open each folder from a familiar folder icon and
must explain what belongs there with a concrete example.

This is a new `office-workspace` product path. It does not replace or silently
migrate the existing `flows install` scaffold. It reuses the proven report
intake, hashing, state-validation, and localhost-security primitives. Existing
flow projects continue to use `flow.yaml`, `automation_output`, and
`local_outbox` unchanged.

The report-wizard concepts map as follows:

| Existing concept | Office-workspace location |
| --- | --- |
| approved past output | `01_APPROVED_PAST_OUTPUTS/` |
| past supporting material | `02_PAST_SUPPORTING_FILES/` |
| current upload or intake | `03_CURRENT_INPUTS/<period_id>/` |
| GrillMe session | `04_QUESTIONS/<period_id>/` |
| draft | `05_DRAFTS/<period_id>/` |
| approval artifact | `06_APPROVED_OUTPUTS/<period_id>/` plus `07_AUDIT/` |
| internal state and run staging | `.system/` |

### 5.1 Module ownership

Phase 1 uses these non-overlapping modules:

- `office_workspace_builder.py`: create and validate the public folder tree;
- `office_workspace_state.py`: own `.system/workspace.json`, period state,
  locks, transitions, and append-only audit records;
- `workflow_pack.py`: validate the versioned pack schema and trusted manifest;
- `codex_runner.py`: preflight, isolated subprocess execution, event parsing,
  cancellation, and staged-output validation;
- `monthly_report_pack.py` and bundled JSON: monthly-report-specific labels,
  questions, prompt template, and output schema;
- `office_workspace_server.py`: localhost HTTP routes and state-change security;
- `office_workspace_ui.py`: self-contained Japanese and English HTML/JS;
- `cli.py`: thin command registration only.

The builder is the only owner of public folder creation. State is the only
writer of workspace and period JSON. The runner writes only inside its run
directory. The server and UI call these modules and do not duplicate rules.

### 5.2 Period state machine

Monthly IDs use `YYYY-MM`, weekly IDs use ISO `YYYY-Www`, and daily IDs use
`YYYY-MM-DD`. Invalid or duplicate IDs are rejected.

```text
created -> inputs_ready -> reviewed -> questioning -> ready_for_run
ready_for_run -> running -> ready_for_review -> approved
running -> cancelled | failed
cancelled | failed -> ready_for_run
```

The decision to reuse an approved output as a style reference is stored in the
next period state as its hash and relative path. Rollover never changes the
prior period.

## 6. Codex Integration Boundary

Codex has two roles.

### 6.1 Setup and customization role

Codex may clone the repository, check prerequisites, create the workspace,
install a workflow pack, launch the local server, and modify a copied workflow
pack when the customer requests a change. Phase 1 adds
`START_WITH_CODEX.ja.md`, `START_WITH_CODEX.md`, and a repository `AGENTS.md`.
Those files define the exact setup command, beginner interview order, safety
boundaries, and verification commands; they are release-required artifacts.

### 6.2 Bounded execution role

The UI may invoke `codex exec` only through a dedicated runner module. It never
runs Codex against the public workspace. The host creates an isolated run
directory, copies verified source snapshots into it, marks the snapshots
read-only, and gives Codex write access only to that disposable run directory.
After completion, the host validates staged outputs and atomically promotes new
files into `05_DRAFTS`; it never asks Codex to write approved outputs, audit
records, source folders, or workspace state.

The command is constructed as an argument array, never a shell string:

```text
codex exec
  --cd <.system/runs/run_id/sandbox>
  --sandbox workspace-write
  --json
  --output-schema <bundled-output-schema.json>
  --output-last-message <output_staging/final.json>
  --skip-git-repo-check
  -
```

The fixed prompt is supplied through stdin. Phase 1 does not use `--yolo`,
`--dangerously-bypass-approvals-and-sandbox`, `--full-auto`, remote mode,
network search, user-provided command flags, or a user-provided executable
path. Preflight runs `codex login status` with a short timeout and requires a
zero exit status.

The runner must also:

- associate the run with the selected workflow workspace, but execute Codex
  only inside the isolated run sandbox;
- use a workspace-write sandbox, never approval or sandbox bypass flags;
- pass a fixed, versioned task instruction owned by the workflow pack;
- treat input document content as data, never as executable instructions;
- restrict model output to the typed staging values for questions and draft;
- record start time, completion state, output paths, and safe error summaries;
- allow one run per workspace at a time;
- support cancellation and a visible timeout;
- never send email, publish, pay, update production records, or approve its own
  output.

Each source is represented by a host-created manifest entry containing its
relative snapshot path, SHA-256 hash, size, extraction status, and provenance.
Extracted text is placed inside explicit untrusted-data delimiters. The fixed
prompt says not to follow document instructions, open document links, fetch
remote content, run commands suggested by a document, or write outside the
declared output schema. The host, not the model, enforces the output allowlist,
file-count limit, size limit, regular-file rule, and absence of links.

The process starts in a new process group. Cancellation changes state to
`cancelling`, sends termination to the process group, waits five seconds, then
forces termination. Partial outputs stay quarantined under the run directory,
the lock is released in `finally`, and the period becomes `cancelled` or
`failed`. A retry always creates a new run ID. A lock contains PID, start time,
and run ID; a stale lock can be reclaimed only after the PID is confirmed dead.
The default run timeout is 15 minutes and is configurable only within a
bounded 1-to-30-minute range.

The model returns two typed values through the output schema:
`missing_questions[]` and `draft_markdown`. The model never writes the public
question or draft folders. The host validates both values. If required
questions remain, the host writes a new immutable question artifact under
`04_QUESTIONS/<period_id>/`, keeps the period in `questioning`, and quarantines
any model draft. After answers are saved by the state module, a new run may
produce `draft_markdown`; only then may the host atomically create a new file
under `05_DRAFTS/<period_id>/`. Existing question and draft files are never
overwritten.

If Codex is unavailable, logged out, or denied permission, the UI must show a
plain-language repair action. It must not silently fall back to an API key.

### 6.3 Workflow-pack trust

Phase 1 installs bundled packs only. Every pack is covered by a repository
manifest containing its relative path, schema version, and SHA-256 hash. The
loader rejects unknown fields, absolute paths, executable declarations,
unbounded prompt variables, external URLs, and prohibited-action omissions.

A Codex-customized copy is marked `local-unreviewed`. The UI shows its diff and
blocks one-click execution until a human explicitly accepts the new pack and a
fresh local manifest is written. A local acceptance is not presented as a
publisher signature. Remote pack download is out of scope for Phase 1.

## 7. Operator UI

The first screen is the product, not a marketing page.

The HTTP server binds only to `127.0.0.1` on a random available port. Every
launch creates a minimum 256-bit secret token. Requests require the token,
trusted loopback client address, an allowed localhost `Host`, and same-origin
validation for state changes. The server sends no permissive CORS headers,
rejects cross-origin state changes, uses no wildcard routes, and applies body,
file, and request-time limits. Generate, cancel, rollover, and approve are
separate POST endpoints with current-state and one-time action-nonce checks.

### 7.1 Phase 1 workspace list

- monthly-report workspaces only;
- workspace health and Codex login/preflight status;
- recent runs and unresolved approvals;
- `新しい月報作業場所を作る` command.

The multi-category home, cross-pack recommendations, and workflow marketplace
are deferred until at least two non-report packs have passed the release gates.

### 7.2 Workflow screen

- visual seven-step progress;
- buttons to open past-output, past-supporting, and current-input folders;
- file count, accepted formats, rejected files, and missing-input warnings;
- `資料を確認`, `下書きを作成`, `下書きを開く`, and
  `承認して完成版へ保存` commands;
- one-question-at-a-time clarification panel;
- provenance and human-approval panel;
- run status, cancellation, and actionable error recovery.

Draft generation and approval are never the same action. Approval requires the
named approver, a fresh action nonce, and the configured local approval PIN.
The PIN is stored only as a salted `scrypt` hash. The append-only audit entry
records operating-system user, approver label, timestamp, draft hash, source
manifest hash, pack hash, and prior audit-entry hash. This is local confirmation,
not enterprise identity authentication, and the UI labels it honestly.

### 7.3 Beginner language

The screen says `今月の売上表をここへ入れてください`, not `Configure data
ingestion`. Internal IDs, enum names, raw JSON, and command syntax remain hidden
unless advanced details are opened.

### 7.4 Local API contract

All responses use `{ok, data, next_action, error}`. Workspace IDs are generated
opaque IDs; folder roles and period IDs are validated enums or strict formats,
never arbitrary paths.

| Method and endpoint | Request | Result | Owner |
| --- | --- | --- | --- |
| `GET /api/workspaces` | none | validated workspace summaries | server -> state |
| `POST /api/workspaces` | name, root choice, approver, PIN | created workspace summary | server -> builder/state |
| `GET /api/workspaces/{id}` | none | current period, folders, files, run and approval state | server -> state |
| `POST /api/workspaces/{id}/inspect` | period ID | accepted/rejected inputs and questions | server -> intake/state |
| `POST /api/workspaces/{id}/answer` | question ID and bounded answer | updated readiness | server -> state |
| `POST /api/workspaces/{id}/generate` | period ID and action nonce | run ID and status | server -> runner |
| `POST /api/workspaces/{id}/cancel` | run ID and action nonce | cancelling/cancelled status | server -> runner/state |
| `POST /api/workspaces/{id}/approve` | draft ID, approver, PIN, action nonce | approved output and audit hash | server -> state |
| `POST /api/workspaces/{id}/rollover` | next period ID and style-reference confirmation | new period state | server -> builder/state |
| `POST /api/workspaces/{id}/open-folder` | allowed folder-role enum | local open result | server -> platform helper |

The UI owns presentation only. It cannot construct filesystem paths, command
arguments, state transitions, audit records, or approval decisions.

## 8. Workflow Pack Contract

Each pack declares:

```json
{
  "schema_version": 1,
  "id": "monthly-report",
  "display_name": {"ja": "月報作成", "en": "Monthly Report"},
  "category": "reports",
  "risk_tier": "low",
  "business_outcome": "Create a sourced monthly report draft",
  "inputs": [
    {
      "id": "current_materials",
      "required": true,
      "accepted_extensions": [".md", ".txt", ".csv", ".json", ".docx", ".xlsx", ".pdf"]
    }
  ],
  "questions": [
    {"id": "audience", "type": "short_text", "required": true, "max_length": 200}
  ],
  "prompt_template_id": "monthly-report-v1",
  "allowed_prompt_variables": ["period_id", "source_manifest", "answers"],
  "outputs": [
    {"id": "draft", "relative_path": "monthly_report.md", "max_bytes": 1048576}
  ],
  "approval": {"required": true, "role": "report_owner"},
  "prohibited_actions": ["external_send", "publish", "payment", "production_write", "self_approve"],
  "success_metrics": ["drafting_minutes", "missing_fact_count", "human_edit_count"]
}
```

The versioned JSON Schema defines required fields, string lengths, enum values,
relative-path grammar, list sizes, question types, and output limits. Phase 1
supports `short_text`, `long_text`, `single_choice`, and `confirmation`
questions only. Prompt text is selected by a bundled template ID rather than
embedded freely in JSON. Packs cannot introduce arbitrary shell commands.
Advanced integrations remain separate connector packs.

## 9. Prioritized Workflow Packs

### Tier 1: first sellable release

1. Daily, weekly, and monthly report drafting
2. Weekly KPI summary and variance explanation
3. Meeting minutes and action-item extraction
4. Sales meeting follow-up and CRM update draft
5. Customer inquiry classification and reply draft
6. Estimate or quote request intake
7. Invoice and missing-document follow-up
8. Expense and receipt completeness check
9. Internal FAQ answer and escalation draft
10. Employee onboarding checklist and reminder draft
11. Project status report and risk summary
12. Purchase request review packet

### Tier 2: next reusable expansion

13. Budget variance commentary
14. Cash-flow input summary
15. Proposal and renewal reminder pack
16. Lead cleanup and routing
17. Support ticket priority and escalation draft
18. Knowledge-base gap report
19. Recruiting screen summary without hiring decisions
20. Training completion report
21. Contract intake checklist without legal judgment
22. Compliance evidence collection
23. Supplier delay and procurement status report
24. Production or field-service completion report
25. Property maintenance request triage
26. Reservation and appointment request preparation
27. Campaign content review pack
28. Inventory reorder alert packet
29. Attendance and missing-assignment report
30. Healthcare administrative intake completeness check without medical
    judgment

The existing catalog of 73 dry-run flows remains available. Only packs that
meet the contract, have tests, and produce a clear local artifact are promoted
into the beginner UI.

Promotion also depends on risk tier:

- `low`: internal reports, KPI drafts, minutes, project status, and knowledge
  summaries. Eligible for the beginner UI after normal release gates.
- `medium`: customer communications, sales commitments, invoices, expenses,
  purchasing, HR administration, and financial commentary. Draft-only output,
  named domain owner, synthetic-data fixtures, and domain warning required.
- `high`: legal, compliance decisions, healthcare content, hiring decisions,
  payment execution, production access, and regulated submissions. Hidden from
  the beginner UI until a separate domain design, red-team suite, approval
  model, and release decision are completed. Phase 1 cannot install these.

## 10. Delivery Phases

### Phase 1A: bounded monthly-report product

- Codex setup entry documents and commands;
- automatic workspace creation;
- workspace folder-open controls;
- two local UI views: workspace list and monthly-report workspace detail;
- Codex preflight and the isolated bounded runner;
- period rollover;
- Japanese and English beginner manuals;
- one bundled monthly-report pack.

Phase 1A is complete only when a fresh user can create one monthly workspace,
run one synthetic month, cancel and retry one run, approve the draft locally,
roll to the next month, and repeat the process from an installed wheel.

### Phase 1B: report-family expansion

- daily, weekly, and KPI report packs;
- shared report-workspace list filters;
- reuse of approved prior outputs as explicitly confirmed style references.

### Phase 2: document and communication work

- meeting minutes;
- sales follow-up;
- customer inquiry;
- estimate intake;
- invoice and missing-document follow-up;
- expense completeness;
- internal FAQ.

### Phase 3: department packs

- finance, HR, operations, customer support, sales, property, hospitality,
  education, manufacturing, and healthcare-administration packs;
- searchable category screen;
- pack installation and safe customization through Codex.

### Phase 4: optional integrations

- approved email, calendar, spreadsheet, CRM, and messaging connectors;
- scheduled runs and notifications;
- cloud deployment only after local dry-run and human approval are proven.

## 11. Safety and Error Handling

- Original inputs are read-only.
- Existing output files are never overwritten; collisions receive new names.
- Symlinks, executables, archives, path traversal, and unsupported binaries are
  rejected.
- Input text cannot alter the system prompt, run shell commands, or expand file
  access.
- AI-generated facts must be linked to source provenance or marked unresolved.
- Draft generation can fail without losing accepted inputs or prior outputs.
- Every failure explains what happened, what remains safe, and the exact next
  action.
- High-impact decisions and all external actions remain human-approved.

## 12. Testing and Release Gates

- unit tests for pack schema, workspace creation, period rollover, and status;
- regression tests for existing report intake and state transitions;
- security tests for path traversal, symlinks, output collisions, prompt
  injection, concurrent runs, cancellation, and timeouts;
- Codex runner tests using a fake executable and deterministic JSONL events;
- integration tests from setup through approved local output;
- browser QA at desktop and mobile sizes in Japanese and English;
- public documentation link and language-separation checks;
- wheel installation smoke test;
- full test suite, public release audit, CI, GitHub Pages, and final human
  review before publication.

## 13. Multi-Agent Delivery Model

Implementation uses explicit model roles:

- GPT-5.4 workers implement bounded tasks with named file ownership and focused
  tests. Workers do not share write ownership and do not revert other work.
- GPT-5.5 reviewers perform read-only specification, security, data-loss, and
  release reviews. They report Critical and Important findings before optional
  polish.
- GPT-5.6 acts as director and integrator. It defines task contracts, keeps the
  critical path local, reviews every worker change, resolves cross-module
  decisions, runs final verification, and decides whether publication gates
  pass.

Agents do not run broad overlapping rewrites. Parallel work is limited to
independent modules or read-only review. Every implementation batch ends with
focused tests before integration, and final completion claims depend on fresh
end-to-end verification by the director.

## 14. Success Criteria

A first-time user can complete setup with Codex and generate a reviewable
monthly report without typing a shell command or obtaining an API key. On the
second month, the user only opens the UI, adds current materials, resolves any
questions, creates a draft, and approves the saved output.

A service provider can install one additional Tier 1 workflow for a customer
without changing the shared engine, and can demonstrate the input, draft,
approval, and measurable time-saving path in under 15 minutes.
