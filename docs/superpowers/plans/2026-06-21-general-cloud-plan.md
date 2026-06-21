# General Cloud Plan Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn `cloud-plan` into a cloud-wide deployment planning command with workload and connector awareness.

**Architecture:** Keep the existing CLI command and add optional `--workload` and `--connectors` arguments. Extend `operator_console.py` with workload profiles, connector environment mapping, and new general cloud planning renderers. Keep legacy artifact filenames as compatibility aliases while docs and tests assert the new general files.

**Tech Stack:** Python CLI, pytest, Markdown artifact generation.

---

### Task 1: Test General Cloud Plan Behavior

**Files:**
- Modify: `tests/test_cli.py`

- [ ] Add parser assertions for `--workload` and `--connectors`.
- [ ] Add a behavior test that runs `cloud-plan` for a non-LINE flow with `--workload scheduled-job`.
- [ ] Assert general artifacts exist and `cloud_plan.json` records workload, connector list, human approval steps, and provider.
- [ ] Run the focused tests and verify they fail before implementation.

### Task 2: Implement CLI and Cloud Plan Generation

**Files:**
- Modify: `src/ai_automation_kit/cli.py`
- Modify: `src/ai_automation_kit/core/operator_console.py`

- [ ] Add workload choices to the parser.
- [ ] Add connector parsing to `cloud-plan`.
- [ ] Add workload profile data for the six common deployment shapes.
- [ ] Replace LINE-centric payload fields with general workload and connector fields.
- [ ] Generate the new general cloud files.
- [ ] Preserve legacy files as aliases for compatibility.
- [ ] Run focused tests and verify pass.

### Task 3: Update Public Docs and Release Gates

**Files:**
- Modify: `README.md`
- Modify: `scripts/release_smoke.py`
- Modify: `scripts/public_release_audit.py`
- Modify: `tests/test_public_readiness.py`
- Modify: `docs/RELEASE_CHECKLIST.md`
- Modify: `CHANGELOG.md`

- [ ] Update README to show generic workload examples first.
- [ ] Update release smoke output path and required files away from LINE-specific naming.
- [ ] Update public audit snippets to require the new general artifacts.
- [ ] Update release checklist review evidence.
- [ ] Run full tests, public audit, and release smoke.

