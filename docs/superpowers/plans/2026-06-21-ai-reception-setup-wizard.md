# AI Reception Setup Wizard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an AI reception / first-response employee path that shows beginners what to prepare, generates a local operator UI, and packages the flow for safer monetized PoC work.

**Architecture:** Extend the existing flow catalog and installer instead of adding a separate app. AI reception becomes a first-class flow family, while every installed flow receives common setup artifacts: requirements checklist, client setup request, connector status, monetization plan, and `operator_ui/index.html`.

**Tech Stack:** Python standard library, existing CLI, existing dry-run flow runtime, Markdown/HTML generated artifacts, pytest.

---

### Task 1: Add Contract Tests

**Files:**
- Modify: `tests/test_flows.py`
- Modify: `tests/test_cli.py`
- Modify: `tests/test_public_readiness.py`

- [ ] Add tests requiring AI reception flow IDs, setup artifacts, and README/release-smoke coverage.
- [ ] Run focused tests and confirm failures are caused by missing AI reception features.

### Task 2: Add AI Reception Flows And Setup Artifacts

**Files:**
- Modify: `src/ai_automation_kit/core/flows.py`

- [ ] Add AI reception flow definitions for LINE/form/email intake, estimate intake, appointment precheck, and daily report.
- [ ] Extend `install_flow()` to generate:
  - `setup_requirements.md`
  - `client_setup_request.md`
  - `connector_status.md`
  - `monetization_plan.md`
  - `operator_ui/index.html`
- [ ] Keep all outputs local and dry-run first.

### Task 3: Add CLI And Public Docs Coverage

**Files:**
- Modify: `src/ai_automation_kit/cli.py`
- Modify: `README.md`
- Modify: `docs/AI_RECEPTION_EMPLOYEE_PACK.md`
- Modify: `docs/AI_RECEPTION_EMPLOYEE_PACK.ja.md`
- Modify: `scripts/public_release_audit.py`
- Modify: `scripts/release_smoke.py`

- [ ] Add documented commands for listing and installing reception flows.
- [ ] Add public docs explaining what users must prepare and how AI agents can help them install the project.
- [ ] Add release audit and smoke coverage for the new docs/artifacts.

### Task 4: Verification

**Files:**
- No new production files unless tests require corrections.

- [ ] Run `python3 -m pytest -q`.
- [ ] Run `python3 scripts/public_release_audit.py`.
- [ ] Run `python3 scripts/release_smoke.py --skip-github --output .tmp/release-smoke-ai-reception`.
- [ ] If all pass, commit and push public repository and backup branch.
