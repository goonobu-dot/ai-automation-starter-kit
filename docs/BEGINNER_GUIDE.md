# Beginner-Friendly Guide

This page explains AI Automation Starter Kit in plain language.

## What this project is

AI Automation Starter Kit is a tool that helps you find useful open-source projects on GitHub and turn them into business automation plans.

GitHub has many public projects made by developers around the world. Some of them can help with work such as:

- answering support questions
- organizing documents
- turning spreadsheets into internal tools
- automating repeated business steps
- building AI agents

This project helps you look at those public projects and ask practical questions:

- Which projects look useful?
- Which ones are safe enough to review?
- What risks should we check first?
- What should a team try in a small pilot?
- How do we measure whether the automation actually helped?

## Why it exists

Normal AI chat can give advice. That is useful, but it often ends as a conversation.

Real automation work needs more than advice. A team needs files that can be reviewed, shared, repeated, and audited.

This project exists to turn an idea into a practical workflow. It creates files that explain:

- what was found
- what to read first
- whether a pilot should start
- who needs to approve it
- what risks are open
- what metrics should be measured
- how to try the first prototype safely

## What it can do

The main command is `github-discover`.

It searches GitHub for automation projects in a business area such as operations, support, finance, sales, marketing, or HR.

Then it creates an output folder with decision files.

Important files include:

| File | Simple meaning |
|---|---|
| `run_summary.md` | A short summary of what happened and what to read next. |
| `executive_decision_brief.md` | A decision note that says whether to try, wait, or search again. |
| `pilot_scorecard.csv` | A spreadsheet-style file for measuring whether the pilot worked. |
| `value_realization_plan.md` | A plan for what value the automation should create. |
| `risk_exception_register.md` | A list of risks that must be handled before production use. |
| `operational_audit_plan.md` | A plan for what evidence must be checked later. |
| `adapter_starter/` | A safe dry-run starter when a candidate is ready to prototype. |

## How to use it

First, download the project:

```bash
git clone https://github.com/goonobu-dot/ai-automation-starter-kit.git
cd ai-automation-starter-kit
```

Create a Python environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m ensurepip --upgrade
python3 -m pip install --upgrade pip setuptools
python3 -m pip install -e .
```

Check your setup:

```bash
ai-automation-kit doctor --output .tmp/doctor
```

Run GitHub discovery:

```bash
ai-automation-kit github-discover --business-area operations --limit 2 --output .tmp/operations-discovery
```

Then read these files in order:

1. `.tmp/operations-discovery/run_summary.md`
2. `.tmp/operations-discovery/executive_decision_brief.md`
3. `.tmp/operations-discovery/pilot_scorecard.csv`
4. `.tmp/operations-discovery/artifact_index.md`

## How it is different from normal chat AI

Normal chat AI gives an answer in a conversation.

This project creates a repeatable workflow.

Normal chat AI:

- can be useful for quick thinking
- may not leave enough evidence
- can be hard for a team to review later
- may not define approvals, risks, or measurements

AI Automation Starter Kit:

- saves output files
- keeps a run history
- creates decision documents
- creates risk and audit documents
- creates value measurement files
- supports dry-run prototypes
- makes the workflow easier to repeat

## Who should use it

This project is useful for:

- developers learning AI automation
- AI agent builders
- automation consultants
- business teams planning internal automation
- people who want to learn from public GitHub projects

## Simple analogy

Think of GitHub as a huge library of recipes.

This project does not just say, "This recipe looks good."

It helps you check:

- which recipe is worth trying
- what ingredients are risky
- who should approve the test
- how to measure whether the result is good
- how to practice safely before serving it for real

That is the main purpose of this project: move from an interesting open-source idea to a controlled automation pilot.

