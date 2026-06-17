# AI Automation Starter Kit

Cloneable starter kit for reusable AI automation workflows. It turns five OSS-inspired ideas into local, testable templates with run records, source/provenance files, and checked-in examples.

## 1-Minute Demo

Use this first when you want to discover business automation opportunities from public GitHub projects and turn them into a practical next-step plan:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip setuptools
python3 -m pip install -e .
ai-automation-kit github-discover --business-area operations --limit 2 --output .tmp/operations-discovery
```

Open the generated plan:

```bash
sed -n '1,180p' .tmp/operations-discovery/business_automation_plan.md
```

### Example Output

The plan tells you:

- which GitHub repositories are worth reviewing first
- which candidates need license or maintenance review
- which starter-kit template to use next
- how to run a dry-run prototype
- which success metrics prove the automation is actually useful

Example generated files:

- `.tmp/operations-discovery/report.md`
- `.tmp/operations-discovery/github_candidates.md`
- `.tmp/operations-discovery/business_automation_plan.md`
- `.tmp/operations-discovery/business_automation_summary.json`

## How This Differs From Chat AI

Normal chat AI answers one prompt at a time. This kit makes the workflow repeatable:

- explicit input configs
- saved outputs
- run history
- source maps and citations
- dry-run approval records
- placeholder-only delivery assets
- tests that prove each template still works

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m ensurepip --upgrade
python3 -m pip install --upgrade pip setuptools
python3 -m pip install -e .
python3 -m pytest -q
python3 scripts/run_all_demos.py
```

The demo outputs are written to `.tmp/all-templates/`.

## How This Fits With Local Agent Workbenches

This project pairs well with:

- `goonobu-dot/local-agent-workbench`
- `goonobu-dot/claude-code-workbench`

The workbenches give you a local multi-agent cockpit for parallel Codex CLI or Claude Code sessions. This starter kit gives those agents a repeatable business automation path:

1. Discover automation candidates from GitHub.
2. Research candidate projects with citations.
3. Answer internal questions from docs.
4. Draft approved replies or handoffs.
5. Convert spreadsheets into internal app schemas.
6. Package the workflow for delivery with metrics and safety checks.

## Template Commands

### github-discover

Start here when you want a one-command GitHub discovery workflow for business automation ideas:

```bash
ai-automation-kit github-discover --business-area sales --limit 5 --output .tmp/sales-automation-discovery
```

Creates `report.md`, `github_candidates.md`, `github_candidates.csv`, `github_candidates.json`, `business_automation_plan.md`, `business_automation_summary.json`, run records, and the generated `github_discover_config.json`. The business plan recommends which starter-kit template to use next and includes success metrics for the workflow.

Supported business areas include `sales`, `support`, `finance`, `operations`, `marketing`, and `hr`.

You can override the GitHub query directly:

```bash
ai-automation-kit github-discover --business-area support --query "customer support ai-agent stars:>1000" --limit 10 --output .tmp/support-discovery
```

### research-agent

```bash
ai-automation-kit research-agent --config examples/research-agent/sample_research.json --output .tmp/research-agent-demo
```

Creates `report.md`, `report.html`, `report.json`, `failed_fetches.json`, run records, and source records.

You can also fetch public GitHub repository metadata directly:

```bash
ai-automation-kit research-agent --config examples/research-agent/github_repos.json --output .tmp/github-repo-demo
```

Or search GitHub for high-signal public repositories and turn the results into a reusable report:

```bash
ai-automation-kit research-agent --config examples/research-agent/github_search.json --output .tmp/github-search-demo
```

GitHub search runs also create `github_candidates.json`, `github_candidates.csv`, and `github_candidates.md` with a lightweight adoption score, automation-fit label, license-risk label, and recommended next step. Set `"include_readme": true` in the config when you want README files downloaded into the output folder for deeper review.

```bash
ai-automation-kit research-agent --config examples/research-agent/github_repo_with_readme.json --output .tmp/github-readme-demo
```

For higher GitHub API limits, set `GITHUB_TOKEN` in your shell before running the command. Without a token, GitHub allows public unauthenticated requests at a lower rate limit.

See `docs/GITHUB_DATA.md` for supported fields, search settings, and GitHub API references.

### docs-rag

```bash
ai-automation-kit docs-rag --config examples/docs-rag/sample_docs_rag.json --output .tmp/docs-rag-demo
```

Creates a grounded `answer.md`, `answer.json`, `chunks.jsonl`, `source_map.json`, run records, and source records. Answers include confidence, citations, and next actions.

### internal-ai-workflow

```bash
ai-automation-kit internal-ai-workflow --config examples/internal-ai-workflow/sample_inquiry.json --output .tmp/internal-ai-workflow-demo
```

Creates a draft reply, risk level, review checklist, and a pending dry-run approval request.

### excel-to-internal-app

```bash
ai-automation-kit excel-to-internal-app --config examples/excel-to-internal-app/sample_app.json --output .tmp/excel-to-internal-app-demo
```

Creates `schema.sql`, `fields.json`, `data-quality-report.json`, `admin-view.md`, and `migration-report.md` from CSV.

### delivery-pipeline

```bash
ai-automation-kit delivery-pipeline --config examples/delivery-pipeline/sample_delivery_pipeline.json --output .tmp/delivery-pipeline-demo
```

Creates delivery README, `.env.example`, Docker Compose, operation manual, delivery checklist, success metrics, and smoke test notes.

## Checked-in Examples

- `examples/research-agent/expected/report.md`
- `examples/docs-rag/expected/answer.md`
- `examples/internal-ai-workflow/expected/draft_reply.md`
- `examples/excel-to-internal-app/expected/migration-report.md`
- `examples/delivery-pipeline/expected/delivery-checklist.md`

## Safety Defaults

- Runtime outputs go under `.tmp/` and are ignored by Git.
- `.env` files are ignored; `.env.example` contains placeholders only.
- `research-agent` rejects localhost and private network HTTP targets.
- Failed fetches mask sensitive query parameters.
- `internal-ai-workflow` creates pending dry-run approval records instead of sending messages.
- Third-party OSS integrations are adapter-only until license review. See `docs/OSS_INTEGRATIONS.md`.

## Public Release Readiness

Before publishing a release, run:

```bash
python3 -m pytest -q
python3 scripts/run_all_demos.py
ai-automation-kit github-discover --business-area operations --limit 2 --output .tmp/release-smoke-discovery
```

Review:

- `.tmp/release-smoke-discovery/business_automation_plan.md`
- `.tmp/all-templates/docs-rag/answer.md`
- `.tmp/all-templates/internal-ai-workflow/review-checklist.md`
- `.tmp/all-templates/excel-to-internal-app/data-quality-report.json`
- `.tmp/all-templates/delivery-pipeline/docs/success-metrics.md`

See `docs/SHOWCASE.md` for the public demo story.

Open `docs/demo.html` in a browser for a static demo page that shows the value story and generated artifacts.
