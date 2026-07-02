# Start Here

This page helps a first-time visitor understand AI Automation Starter Kit in the First 3 minutes.

Do not read every document first. If the repository feels too large, open [Beginner Route Map](../BEGINNER_ROUTE_MAP.md) first. It tells you what to open first, what to ignore at first, and which route fits you: No-CLI, CLI, side-hustle, company internal, website project, or cloud/API setup.

## What This Project Is

AI Automation Starter Kit is a local Python CLI that finds promising public OSS projects from GitHub and turns them into practical business automation planning artifacts.

It is not just a repository search tool. It helps a team decide whether an OSS project is useful, safe to try, legally reviewable, measurable, and ready for a controlled pilot.

## First 3 minutes

1. Read [Beginner Route Map](../BEGINNER_ROUTE_MAP.md) to choose your route.
2. Read the [beginner guide](../BEGINNER_GUIDE.md) to understand the purpose.
3. Read the first sections of the [user manual](../USER_MANUAL.md): safety, first path, and first workspace.
4. If cloud, APIs, or approvals feel confusing, ask an AI agent to read [AI Beginner Support Map](AI_BEGINNER_SUPPORT_MAP.md) with you.
5. If you want to turn this into a freelance or consulting offer, read [First Client Walkthrough](../FIRST_CLIENT_WALKTHROUGH.md).
6. After local setup, run `ai-automation-kit complete-workspace --flow-id invoice-document-followup --client-type local-business --niche accounting --output .tmp/complete-accounting`.
7. Open `.tmp/complete-accounting/client_command_center.html` and `.tmp/complete-accounting/FINAL_DELIVERY_GUIDE.md`.
8. Before moving into APIs or cloud, use `guided-setup`, `guided-review`, and `cloud-plan` to list missing inputs and human approvals.

## Choose Your Path

| You are | Read next | Try first |
| --- | --- | --- |
| Unsure where to start | [Beginner Route Map](../BEGINNER_ROUTE_MAP.md) | No-CLI path |
| Developer | [Quickstart](../../README.md#quickstart) | guided onboarding |
| Automation consultant | [Use Cases](USE_CASES.md) | `onboard --create-offer-pack` |
| New AI-agent side-business builder | [First Client Walkthrough](../FIRST_CLIENT_WALKTHROUGH.md) | `complete-workspace` |
| Beginner worried about cloud or APIs | [AI Beginner Support Map](AI_BEGINNER_SUPPORT_MAP.md) | `guided-setup` |
| Business team | [Beginner guide](../BEGINNER_GUIDE.md) | executive decision brief |
| Japanese reader | [まずここから](START_HERE.ja.md) | [日本語のやさしい解説](../BEGINNER_GUIDE.ja.md) |

## Safety Note

Generated pilot assets are dry-run oriented. Offer-pack files help scope and explain paid work, but they do not guarantee income. Review license, security, data handling, and approvals before using any third-party OSS in production.

## New Bridge Layer

- Read [Execution bridges](../EXECUTION_BRIDGES.md) for `n8n`, `Activepieces`, and `Windmill`.
- Read [Operations expansion](OPERATIONS_EXPANSION.md) for deployment, secrets, observability, and state packs.
