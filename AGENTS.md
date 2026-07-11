# AGENTS.md

This repository includes an `office-workspace` path for Codex-led monthly report setup. Follow this contract when the user asks you to prepare or operate that path.

## Conversation contract

- Ask one question at a time.
- Confirm exactly four setup facts before creation: save root, workspace name, approver name, and first reporting month.
- Keep the wording human-first. Explain folder purpose before using internal jargon.
- If information is missing, ask for only the next missing fact. Do not dump a checklist all at once.

## Required startup check

Run this before workspace setup:

```bash
codex login status
```

If it fails, stop and explain the next human action. Do not switch to an API key flow, do not ask for copied secrets, and do not invent a workaround that changes the security model.

## Exact workspace creation path

Use the official CLI only:

```bash
ai-automation-kit office-workspace create --root "<save-root>" --name "<workspace-name>" --approver "<approver-name>" --pin "<6-to-32-digit-pin>" --period "<YYYY-MM>" --language "<ja|en>"
```

Then validate the workspace before any browser action:

```bash
ai-automation-kit office-workspace status --workspace "<workspace-path>" --json
```

If the user has already placed files for the first month, inspect them with:

```bash
ai-automation-kit office-workspace inspect --workspace "<workspace-path>" --period "<YYYY-MM>"
```

Only after validation may you launch the local UI:

```bash
ai-automation-kit office-workspace serve --root "<save-root>" --language "<ja|en>"
```

## What you must explain and open

After creation, open and explain these three folder types:

1. `01_APPROVED_PAST_OUTPUTS`: older approved monthly reports;
2. `02_PAST_SUPPORTING_FILES`: older supporting references;
3. `03_CURRENT_INPUTS/<YYYY-MM>`: current-month inputs only.

Also explain:

- `05_DRAFTS` is for local drafts;
- `06_APPROVED_OUTPUTS` is for locally approved final copies;
- `07_AUDIT` is the local approval trail.

## Hard safety boundaries

- Do not ask for an API key.
- Do not ask for shell overrides, executable overrides, sandbox bypass flags, approval bypass flags, or remote execution flags.
- Do not use `--yolo`, `--dangerously-bypass-approvals-and-sandbox`, or similar shortcuts.
- Do not send anything externally. No email, chat, webhook, publish, or update action belongs to this flow.
- Validate the setup before opening the local UI.
- Validate the local setup before opening the local UI.
- Keep the workspace local. Explain truthfully that approval is a local record on this device.

## Testing expectation

When you change this path, run focused checks first. The normal minimum set is:

```bash
python3 -m pytest -q tests/test_cli.py tests/test_public_readiness.py
python3 -m pytest -q tests/test_office_workspace_server.py tests/test_office_workspace_ui.py
```

Use a narrower target only when the change is obviously smaller, then widen again before calling the work done.

## Platform truth for Phase 1A

Phase 1A workspace mutation is supported on macOS or Linux only. If the user is on Windows, say so directly before attempting creation or approval mutation. Do not imply full support where it does not exist.

## Manual recovery truth

If state is inconsistent, a stale run lock remains, or the tool reports manual recovery required, say that plainly. Do not hide the condition behind vague reassurance. Recovery is local and should start with:

- `00_START_HERE/workspace_status.json`
- `.system/workspace.json`
- `.system/periods/<YYYY-MM>/state.json`
- `.system/runs/`
- `07_AUDIT/audit.jsonl`

If those checks do not resolve the situation, stop, summarize the facts, and ask one next question instead of improvising risky edits.
