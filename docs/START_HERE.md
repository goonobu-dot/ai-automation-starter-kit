# Start Here

This page helps a first-time visitor understand AI Automation Starter Kit in the First 3 minutes.

## What This Project Is

AI Automation Starter Kit is a local Python CLI that finds promising public OSS projects from GitHub and turns them into practical business automation planning artifacts.

It is not just a repository search tool. It helps a team decide whether an OSS project is useful, safe to try, legally reviewable, measurable, and ready for a controlled pilot.

## First 3 minutes

1. Read the [beginner guide](BEGINNER_GUIDE.md) if the project is new to you.
2. Skim [Use Cases](USE_CASES.md) and choose a business area.
3. Run `ai-automation-kit onboard --business-area operations --limit 2 --output .tmp/onboarding --create-offer-pack` after local setup.
4. Open `.tmp/onboarding/onboarding_summary.md` and follow the first `next_read` file.
5. Open `.tmp/onboarding/offer_pack/README.md` if you want to turn the result into a scoped consulting or freelance pilot.
6. Run `ai-automation-kit beginner-sales --flow-id invoice-document-followup --client-type local-business --niche accounting --output .tmp/beginner-sales` if you want a visual, beginner-friendly sales pack around one workflow.
7. Run `ai-automation-kit complete-workspace --flow-id invoice-document-followup --client-type local-business --niche accounting --output .tmp/complete-accounting` if you want the full workspace plus bridge, deployment, safety, secrets, document, observability, and state starters.

## Choose Your Path

| You are | Read next | Try first |
| --- | --- | --- |
| Developer | [Quickstart](../README.md#quickstart) | guided onboarding |
| Automation consultant | [Use Cases](USE_CASES.md) | `onboard --create-offer-pack` |
| New AI-agent side-business builder | [Beginner guide](BEGINNER_GUIDE.md) | `beginner-sales` |
| Business team | [Beginner guide](BEGINNER_GUIDE.md) | executive decision brief |
| Japanese reader | [まずここから](START_HERE.ja.md) | [日本語のやさしい解説](BEGINNER_GUIDE.ja.md) |

## Safety Note

Generated pilot assets are dry-run oriented. Offer-pack files help scope and explain paid work, but they do not guarantee income. Review license, security, data handling, and approvals before using any third-party OSS in production.

## New Bridge Layer

- Read [Execution bridges](EXECUTION_BRIDGES.md) for `n8n`, `Activepieces`, and `Windmill`.
- Read [Operations expansion](OPERATIONS_EXPANSION.md) for deployment, secrets, observability, and state packs.
