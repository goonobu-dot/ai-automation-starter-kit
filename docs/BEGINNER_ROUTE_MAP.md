# Beginner Route Map

This page is the map for people who open this project and feel, "There are too many files. I do not know what to read first."

Do not read everything first. This project is large because it covers research, side-hustle sales, local dry-runs, cloud setup, approval gates, generated demos, and public-release checks. A beginner should not start by reading every manual. A beginner should choose one route and ignore the rest until it becomes necessary.

The first rule is simple:

> One workflow, one sample input, one draft output, one human approver.

If you keep that rule, this project becomes much easier to use.

## The Short Version

Start here:

1. Read this page.
2. Read [Start Here](START_HERE.md).
3. Read [AI Beginner Support Map](AI_BEGINNER_SUPPORT_MAP.md).
4. Use the No-CLI path if you are not ready for terminal commands.
5. Use the CLI path if you want the project to generate files for you.
6. Keep real secrets, client private data, production access, and paid cloud changes out of chat until a human approves the next step.

## What This Project Helps You Do

This project helps you turn a vague business automation idea into visible files:

- a workflow map
- a list of missing inputs
- a dry-run plan
- AI draft outputs
- a human approval queue
- a client-friendly report
- a proposal or paid PoC scope
- a cloud or connector setup checklist
- a go-live or stop decision

The important point is that it does not ask you to automate everything on day one. It helps you explain one small workflow safely.

## What to open first

If you only open five things, open these:

| Order | File | Why |
|---|---|---|
| 1 | `docs/BEGINNER_ROUTE_MAP.md` | Choose the route and avoid reading overload. |
| 2 | `docs/START_HERE.md` | Understand the first 3 minutes. |
| 3 | `docs/AI_BEGINNER_SUPPORT_MAP.md` | Learn what AI can help with and what humans must approve. |
| 4 | `docs/AI_AGENT_GRILL_ME_SKILL.md` | Give ChatGPT, Claude, Cursor, Codex, or Claude Code a one-question-at-a-time interview pattern. |
| 5 | `docs/USER_MANUAL.md` | Follow the longer manual when you are ready to install or generate files. |

## What to ignore at first

What to ignore at first:

- release engineering files
- GitHub Actions and packaging details
- every generated output filename
- every cloud provider option
- every connector choice
- every advanced governance pack
- every public OSS research artifact

Come back to those only when your first workflow is clear.

## Choose Your Route

### No-CLI path

Use this route if you are new to terminal commands, Python, APIs, or cloud setup.

1. Open [AI Agent Grill Me Skill](AI_AGENT_GRILL_ME_SKILL.md).
2. Paste it into ChatGPT, Claude, Gemini, Cursor, Codex, Claude Code, or another AI agent.
3. Ask the AI to read this GitHub project with you.
4. Tell it: "Ask me one question at a time. Help me choose one business workflow."
5. Answer with business context, not secrets.
6. Ask it to produce a simple plan before any cloud or API setup.

Use this prompt:

```text
Please read this GitHub project with me: ai-automation-starter-kit.
I am a beginner. Do not ask everything at once.
Ask one question at a time.
Help me choose one small workflow, one input source, one draft output, and one human approver.
Do not ask me to paste real API keys, passwords, secrets, private client data, or production access.
When the workflow is clear, show me which file in this project I should read next.
```

### CLI path

Use this route when you are ready to let the project generate a folder of files.

Install:

```bash
git clone https://github.com/goonobu-dot/ai-automation-starter-kit.git
cd ai-automation-starter-kit
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip setuptools
python3 -m pip install -e .
ai-automation-kit doctor --output .tmp/doctor
```

Then generate the first complete workspace:

```bash
ai-automation-kit complete-workspace \
  --flow-id invoice-document-followup \
  --client-type local-business \
  --niche accounting \
  --output .tmp/complete-accounting
```

Open only these first:

1. `.tmp/complete-accounting/FINAL_DELIVERY_GUIDE.md`
2. `.tmp/complete-accounting/client_command_center.html`
3. `.tmp/complete-accounting/demo_site/index.html`
4. `.tmp/complete-accounting/client_report/client_report.html`
5. `.tmp/complete-accounting/business_launch/START_HERE_BUSINESS_LAUNCH.md`

### Side-hustle path

Use this route if your goal is to sell a small automation service to a local business or small company.

Start with:

```bash
ai-automation-kit side-hustle-blueprints \
  --industry local-business \
  --operator-level beginner \
  --output .tmp/side-hustle-blueprints
```

Then open:

1. `.tmp/side-hustle-blueprints/START_HERE_SIDE_HUSTLE_BLUEPRINTS.md`
2. `.tmp/side-hustle-blueprints/first_client_picker.md`
3. `.tmp/side-hustle-blueprints/client_intake_questions.md`
4. `.tmp/side-hustle-blueprints/risk_boundaries.md`

Your first offer should be a small paid dry-run PoC, not a promise to fully automate a company.

### Company internal path

Use this route if you are inside a company or helping one team improve a repeated task.

Start with:

```bash
ai-automation-kit flow-guide \
  --industry operations \
  --niche admin \
  --output .tmp/flow-guide
```

Then pick one workflow and install it:

```bash
ai-automation-kit flows install invoice-document-followup --output .tmp/flow-project
ai-automation-kit flows run .tmp/flow-project
```

Open:

1. `.tmp/flow-project/workflow_map.mmd`
2. `.tmp/flow-project/automation_output/work_queue.csv`
3. `.tmp/flow-project/automation_output/draft_outputs.md`
4. `.tmp/flow-project/automation_output/approval_queue.csv`
5. `.tmp/flow-project/automation_output/status_report.md`

### Website project path

Use this route if you want to build a homepage plus a simple inquiry or reservation operation for a client.

Start with:

```bash
ai-automation-kit website-side-hustle \
  --industry hospitality \
  --client-type local-business \
  --niche tourism-hotel \
  --output .tmp/website-side-hustle
```

Open:

1. `.tmp/website-side-hustle/START_HERE_WEBSITE_SIDE_HUSTLE.md`
2. `.tmp/website-side-hustle/client_kickoff_questions.md`
3. `.tmp/website-side-hustle/designer_grade_agent_playbook.md`
4. `.tmp/website-side-hustle/website_quality_gate.md`
5. `.tmp/website-side-hustle/delivery_acceptance_checklist.md`

Do not clone competitor websites. Use public references for learning structure, not for copying a brand, text, image, or full layout.

### Cloud and API path

Use this route only after the workflow is clear.

Start with:

```bash
ai-automation-kit guided-setup \
  --flow-id invoice-document-followup \
  --mode beginner \
  --deployment undecided \
  --connectors gmail,google-sheets \
  --output .tmp/guided-setup
```

Then review:

1. `.tmp/guided-setup/START_HERE_GUIDED_SETUP.md`
2. `.tmp/guided-setup/missing_inputs.md`
3. `.tmp/guided-setup/env_values_needed.md`
4. `.tmp/guided-setup/client_request_list.md`
5. `.tmp/guided-setup/ai_agent_instruction.md`

If cloud is needed, create a plan:

```bash
ai-automation-kit cloud-plan \
  --flow-id invoice-document-followup \
  --provider aws \
  --workload scheduled-job \
  --connectors gmail,google-sheets,storage-folder \
  --output .tmp/cloud-plan
```

The cloud plan is not a command to publish production blindly. It is a checklist for accounts, permissions, cost, secrets, rollback, and human approval.

## Where command-center Fits

Use `command-center` when you feel lost after the project grows:

```bash
ai-automation-kit command-center --language both --output .tmp/command-center
```

Open:

- `.tmp/command-center/START_HERE_COMMAND_CENTER.md`
- `.tmp/command-center/command_center.html`
- `.tmp/command-center/next_step_decision_tree.md`

This is the menu for the expansion packs such as `skill-pack`, `approval-gate`, `mcp-connector-plan`, `workflow-explainer`, `eval-loop`, and `governance-pack`.

## Human Approval Rules

AI may draft, classify, summarize, organize, and explain.

Human approval is required before:

- sending messages to real customers
- confirming bookings
- changing prices
- issuing refunds
- changing production data
- enabling paid cloud resources
- creating public webhooks
- using real client private data
- making legal, medical, financial, HR, or safety decisions

## Beginner Checklist

Before you say this is ready for a client, confirm:

- The workflow is one small process.
- The input source is known.
- The output is a draft, not an automatic action.
- A human approver is named.
- Sample or anonymized data is available.
- The dry-run output can be explained in plain language.
- The client knows this is not a production system yet.
- The next step is either continue, revise, or stop.

## The Point

This project is useful when it helps a beginner move from "AI can probably automate something" to "Here is the exact small workflow, here is the safe demo, here is what the client must provide, here is what AI can draft, and here is where a human approves."
