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

It does not guarantee income. It helps you turn a business pain into a safer dry-run, a clearer client conversation, and a smaller PoC offer.

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

The easiest first command is `onboard`.

It checks your setup, searches GitHub, creates decision files, and writes one summary that tells you what to read next.

The lower-level discovery command is `github-discover`.

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
| `offer_pack/` | Proposal, service menu, pricing model, outreach copy, and safety boundaries for a scoped client pilot. |
| `beginner-sales/` | Visual flow gallery, selected-flow demo, pitch script, ROI calculator, proposal one-pager, and 3-day PoC plan for a beginner-friendly client conversation. |

## How to use it

If you are new, first read [Start Here](START_HERE.md).

If you want to use this for a first freelance or consulting client, read [First Client Walkthrough](FIRST_CLIENT_WALKTHROUGH.md).

If cloud, API keys, intake folders, or approval owners feel confusing, ask an AI agent to read [AI Beginner Support Map](AI_BEGINNER_SUPPORT_MAP.md) with you and guide you one question at a time.

Then download the project:

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

Run the easiest full starter workflow. If you are not sure where to begin, `complete-workspace` creates the demo, dry-run files, client report, and business launch materials in one folder.

```bash
ai-automation-kit complete-workspace --flow-id invoice-document-followup --client-type local-business --niche accounting --output .tmp/complete-accounting
```

Open the first guide:

```bash
sed -n '1,180p' .tmp/complete-accounting/FINAL_DELIVERY_GUIDE.md
```

Then read these files in order:

1. `.tmp/complete-accounting/FINAL_DELIVERY_GUIDE.md`
2. `.tmp/complete-accounting/client_command_center.html`
3. `.tmp/complete-accounting/demo_site/index.html`
4. `.tmp/complete-accounting/client_report/client_report.html`
5. `.tmp/complete-accounting/business_launch/START_HERE_BUSINESS_LAUNCH.md`

The generated folder contains many files, but you do not need to read all of them at first. Start with the guide, demo, report, and business launch materials.

If you are new to AI agents and want to explain one automation idea to a business, generate the beginner sales pack:

```bash
ai-automation-kit beginner-sales --flow-id invoice-document-followup --client-type local-business --niche accounting --output .tmp/beginner-sales
```

Then open:

1. `.tmp/beginner-sales/flow_gallery.html`
2. `.tmp/beginner-sales/selected_flow_demo.html`
3. `.tmp/beginner-sales/client_questions.md`
4. `.tmp/beginner-sales/roi_simple_calculator.csv`
5. `.tmp/beginner-sales/proposal_one_pager.md`

This gives you a clearer way to show a company what the automation does before asking them to approve a pilot.

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
