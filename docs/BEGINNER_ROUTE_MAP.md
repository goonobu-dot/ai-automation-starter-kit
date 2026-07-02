# Beginner Route Map

Read this like a signboard, not a technical manual.

This project has many features. Do not read everything first. You do not need to understand the whole repository before using it. This page only helps you choose one doorway.

## 30-second version

Start with one small decision:

> One workflow, one sample input, one draft output, one human approver.

That is enough for the first day.

Examples:

- Read inquiry emails and draft replies.
- Find missing invoice documents and create a check list.
- Sort FAQ questions and draft answers.
- Turn a weekly manual report into a draft report.

The first goal is not to automate an entire company. The first goal is to show one safe workflow that a person can understand.

## Stop here for today

For day one, stop after this:

1. Pick one repeated task.
2. Pick where the input comes from.
3. Pick the draft output AI should create.
4. Pick the person who approves it.
5. Do not send real messages or update production systems.

If those are not clear, do not start cloud, APIs, webhooks, databases, or production access yet.

## How to look at this project

This project is a toolbox for business automation beginners.

You do not open every tool at once. Pick one tool for one job.

What you do:

- choose the job
- ask the client or team simple questions
- prepare sample data
- review the AI draft
- decide whether to continue, revise, or stop

What AI can help with:

- organize the questions to ask
- describe the workflow
- draft replies or task lists
- write client explanations
- list missing inputs

## What to open first

If you are lost, read only this order:

1. Getting Started (Japanese, the single entrance)
2. This page
3. Documentation Index
4. AI Agent Grill Me Skill
5. User Manual

File names:

- `docs/GETTING_STARTED.ja.md`
- `docs/BEGINNER_ROUTE_MAP.md`
- `docs/INDEX.md`
- `docs/AI_AGENT_GRILL_ME_SKILL.md`
- `docs/USER_MANUAL.md`

## What to ignore at first

Ignore these on the first day:

- GitHub Actions
- packaging
- release checks
- every cloud option
- every connector option
- every generated filename
- advanced governance files

They matter later. They are not first-day reading.

## Choose one doorway

### 1. No-CLI path

Choose this if terminal commands, Python, APIs, or cloud setup feel uncomfortable.

Paste this into ChatGPT, Claude, Gemini, Cursor, Codex, Claude Code, or another AI assistant:

```text
Please read this GitHub project with me: ai-automation-starter-kit.
I am a beginner.
Do not explain everything at once.
Ask one question at a time.
Help me choose one workflow, one input, one draft output, and one human approver.
Do not ask me to paste real API keys, passwords, secrets, private client data, or production access.
```

Use this path when you want the AI to guide you before you run anything.

### 2. CLI path

Choose this when you want the project to generate files for you.

Start with `complete-workspace`.

It creates a sample workflow, client explanation, demo, report, and proposal files.

At first, open only these generated files:

- `FINAL_DELIVERY_GUIDE.md`
- `client_command_center.html`

### 3. Side-hustle path

Choose this if you want to offer small automation work to a local business or small company.

Your first offer is not "I will automate everything."

Your first offer is a small paid dry-run PoC.

A dry-run PoC means: use sample data, create AI drafts and work lists, keep real sending off, and show whether the workflow has value.

Start with `side-hustle-blueprints`.

### 4. Company internal path

Choose this if you want to improve work inside a company or team.

Pick one repeated pain:

- sorting inquiries
- drafting replies
- checking missing documents
- creating weekly reports
- routing FAQ questions

Then choose one workflow and run a local dry-run.

### 5. Website project path

Choose this if you want to build a homepage plus simple inquiry or reservation operations.

Start with `website-side-hustle`.

Do not clone competitor websites. Public sources are for learning structure, not copying brand, text, images, or full page layout.

### 6. Cloud and API path

Choose this last.

Before cloud or APIs, confirm:

- What task is being automated?
- Where does the input come from?
- What output is created?
- Who approves it?
- Is sample data available?
- How do you stop real sending?

Then use `guided-setup`.

If cloud is needed after that, use `cloud-plan`.

## Where command-center fits

Use `command-center` when the project feels large and you need a menu.

It is not always the first step. It is useful after you know the workflow and need to choose the next pack, such as an approval gate, AI skill, connector plan, workflow explainer, eval loop, or governance pack.

## Human approval

AI can draft, classify, summarize, organize, explain, and make checklists.

A human must approve:

- real customer sends
- booking confirmations
- price changes
- refunds
- production data changes
- paid cloud changes
- public webhooks
- private client data use
- legal, medical, financial, HR, or safety decisions

## Final note

This project should not make beginners feel behind.

You do not need to understand everything. Choose one small workflow, let AI draft something, and keep a human approval step. That is a real first step.
