# Website Project Agent Guide

This guide explains how to use this GitHub project with Codex, Claude Code, Cursor, or another AI coding agent.

The goal is not to make an AI clone websites. The goal is to help a human deliver an original small-business website plus a simple inquiry or reservation operations system.

## How To Use With Any Agent

1. Ask the agent to read this guide first.
2. Ask it to read `docs/WEBSITE_SIDE_HUSTLE_GUIDE.md`.
3. Generate a project pack with `website-side-hustle`.
4. Ask the agent to read the generated `ai_agent_handoff.md`.
5. Keep real secrets, passwords, API keys, and private customer records out of chat.
6. Keep human approval for launch, prices, booking confirmation, and policy exceptions.

## Recommended Agent Flow

Use the same flow across Codex, Claude Code, Cursor, or another AI agent:

1. Read the repository instructions.
2. Read the generated project pack.
3. Ask for missing business facts one question at a time.
4. Build or revise the front website.
5. Build or explain the back-office workflow.
6. Verify the website and dashboard in a browser.
7. Produce a short client handoff note.

This flow keeps the AI agent useful without turning it into an unsupervised business operator.

## Recommended Prompt

```text
Read this repository as a website side-hustle starter kit.
Use docs/WEBSITE_PROJECT_AGENT_GUIDE.md and docs/WEBSITE_SIDE_HUSTLE_GUIDE.md as the main instructions.
Help me create an original small-business website and a simple inquiry or reservation operations system.
Do not clone competitors.
Do not ask me to paste API keys, passwords, or real customer private data in chat.
Ask one question at a time when information is missing.
Keep launch, final booking confirmation, prices, and policy exceptions behind human approval.
```

## Agent Responsibilities

- Turn the client brief into a clear website structure.
- Build or revise the front-end page.
- Create form, contact, and call-to-action paths.
- Create or explain the back-office intake table.
- Draft response templates.
- Explain what the human operator must check each day.
- List open questions, missing client assets, and unresolved approvals.
- Verify browser rendering and generated files before claiming completion.

## Human Responsibilities

- Confirm the real business facts.
- Approve final copy, brand tone, prices, and policies.
- Provide licensed photos, logos, and assets.
- Own the client accounts for hosting, forms, inboxes, spreadsheets, and booking tools.
- Confirm every real booking, price exception, and policy exception.

## Codex

Codex works well when the project is local and file-based.

Good requests:

- "Generate the website-side-hustle pack for a tourism hotel."
- "Open the sample site and improve the mobile layout."
- "Add a reservation inquiry dashboard mockup."
- "Run tests and tell me what changed."

## Claude Code

Claude Code works well when you want repo-wide editing and explanatory handoff notes.

Good requests:

- "Read the generated pack and create a client-specific implementation plan."
- "Refactor the sample site while preserving the safety rules."
- "Write a handoff note for a beginner operator."

## Cursor

Cursor works well when a beginner wants inline help while editing files.

Good requests:

- "Explain this section of the homepage in plain language."
- "Help me change this section for a salon instead of a hotel."
- "Find where the inquiry status pipeline is defined."

## What The Agent Should Never Do

- Never sell a direct clone.
- Never invent testimonials, awards, certifications, or customer facts.
- Never auto-confirm a booking.
- Never send production emails or messages without approval.
- Never store unnecessary sensitive data.
- Never hide license uncertainty from the human operator.

## Handoff Note Template

Ask the agent to finish with a short note like this:

```text
What was built:
- Website:
- Inquiry or reservation workflow:
- Files to review:

What the client must confirm:
- Business facts:
- Contact destinations:
- Prices and policies:
- Booking or inquiry approval owner:

What remains manual:
- Final booking confirmation
- Price exceptions
- Policy exceptions
- Production sending

Verification completed:
- Desktop browser:
- Mobile browser:
- Form or CTA path:
- Back-office table or dashboard:
```

## First Command

```bash
ai-automation-kit website-side-hustle --industry hospitality --client-type local-business --niche tourism-hotel --output .tmp/website-side-hustle
```

Then open:

- `.tmp/website-side-hustle/START_HERE_WEBSITE_SIDE_HUSTLE.md`
- `.tmp/website-side-hustle/ai_agent_handoff.md`
- `.tmp/website-side-hustle/beginner_human_guide.md`
- `.tmp/website-side-hustle/beginner_human_guide.ja.md`
- `.tmp/website-side-hustle/sample_site/index.html`
- `.tmp/website-side-hustle/inquiry_dashboard.html`
