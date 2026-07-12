Read this repository's AGENTS.md and help me create a monthly report workspace.
Ask only one question at a time and confirm the save location, workspace name, approver, and first reporting month.
After creation, open and explain where to place past approved reports, past supporting files, and this month's files.

# Start With Codex

Choose from ten daily workflows in the [English beginner guide](docs/daily-workflows.html). The [Japanese guide](docs/daily-workflows.ja.html) is also available.

For five email-free work relief packs, open the [English manual](docs/work-relief-workflows.html) or the [Japanese manual](docs/work-relief-workflows.ja.html). Gmail and email automation are out of scope there and will be a separate project.

This file is for a beginner who wants Codex to prepare the local monthly-report workspace without guessing hidden steps.

Ask only one question at a time.

## What to tell Codex first

Use the three lines above as your first message. They tell Codex to:

1. read the repository contract in `AGENTS.md`;
2. ask only one question at a time;
3. create the workspace with the exact CLI flow;
4. explain the three folder types after setup.

## What Codex should do

Codex should begin with:

```bash
codex login status
```

If login is not ready, Codex should stop and explain the next human step. It should not ask for an API key, token, secret, password, or shell bypass. This flow is based on local Codex login, not on copying credentials into chat.

After the four setup answers are confirmed, Codex should run:

```bash
ai-automation-kit office-workspace create --root "<save-root>" --name "<workspace-name>" --approver "<approver-name>" --pin "<6-to-32-digit-pin>" --period "<YYYY-MM>" --language en
```

Then Codex should validate the result before opening the UI:

```bash
ai-automation-kit office-workspace status --workspace "<workspace-path>" --json
```

Codex may inspect the first month after you place sample files:

```bash
ai-automation-kit office-workspace inspect --workspace "<workspace-path>" --period "<YYYY-MM>"
```

Only after the workspace exists and the status check succeeds should Codex open the local UI:

```bash
ai-automation-kit office-workspace serve --root "<save-root>" --language en
```

## The three folder types Codex must open and explain

After creation, Codex should open these local folders and explain them in plain language:

1. `01_APPROVED_PAST_OUTPUTS`
   Put older finished monthly reports here. These are the strongest writing examples.
2. `02_PAST_SUPPORTING_FILES`
   Put older reference files here, such as background spreadsheets, notes, or previous source exports.
3. `03_CURRENT_INPUTS/<YYYY-MM>`
   Put this month's files here. This is the only folder for the current reporting cycle.

Codex should explain that `05_DRAFTS` is where local drafts appear later, and `06_APPROVED_OUTPUTS` is where locally approved final copies are saved. Codex should also say clearly that this workflow does not send anything externally.

## Safety rules for this setup

- Do not ask for an API key.
- Do not send anything externally.
- validate the setup before opening the local UI.
- Do not ask for approval-bypass or sandbox-bypass flags.
- Do not ask for a custom executable path, shell command, or remote-send option.
- Do not send email, Slack, or any external message from this flow.
- Validate the setup before opening the local UI.
- Keep the conversation human-first and one question at a time.

## Platform truth

Phase 1A workspace creation and approval mutation require macOS or Linux. If you are on Windows, Codex should say that honestly before trying to create or modify the workspace. Read-only docs are still fine, but the safe local mutation path is macOS/Linux only in this release.

## Manual recovery truth

If the workspace state is inconsistent, a lock stays behind, or the UI says manual recovery is required, Codex should say that plainly. It should not pretend the workspace is healthy. The recovery path is local and visible:

- check `00_START_HERE/workspace_status.json`;
- check `.system/workspace.json`;
- check `.system/periods/<YYYY-MM>/state.json`;
- check `.system/runs/` for unfinished runs;
- check `07_AUDIT/audit.jsonl` for the approval trail.

If recovery still looks unclear, Codex should stop, summarize what is known, and ask for one next decision instead of making risky guesses.
