# AI Automation Starter Kit Showcase

This showcase explains the public demo story for the starter kit.

Open `docs/demo.html` in a browser when you want a visual demo page for this story.

## Positioning

AI Automation Starter Kit turns public OSS signals into repeatable business automation workflows.

It is designed to sit next to local multi-agent workbenches:

- `local-agent-workbench`: run parallel Codex CLI sessions in tmux
- `claude-code-workbench`: run parallel Claude Code sessions in tmux
- `ai-automation-starter-kit`: turn agent research into reusable automation artifacts

## Demo Flow

### 1. Discover

Run GitHub discovery for a business area:

```bash
ai-automation-kit github-discover --business-area operations --limit 2 --output .tmp/operations-discovery
```

Key output:

- `report.md`
- `github_candidates.md`
- `business_automation_plan.md`
- `business_automation_summary.json`

### 2. Decide

Open `business_automation_plan.md`.

The plan shows:

- recommended repositories
- license and maintenance risk
- suggested starter-kit templates
- implementation path
- success metrics

### 3. Deliver

Use the recommended template to produce reusable artifacts:

```bash
ai-automation-kit docs-rag --config examples/docs-rag/sample_docs_rag.json --output .tmp/docs-rag-demo
ai-automation-kit internal-ai-workflow --config examples/internal-ai-workflow/sample_inquiry.json --output .tmp/internal-ai-workflow-demo
ai-automation-kit excel-to-internal-app --config examples/excel-to-internal-app/sample_app.json --output .tmp/excel-to-internal-app-demo
ai-automation-kit delivery-pipeline --config examples/delivery-pipeline/sample_delivery_pipeline.json --output .tmp/delivery-pipeline-demo
```

## Why Users Should Care

The kit does not stop at an AI answer. It creates reusable files:

- source-backed reports
- candidate rankings
- approval checklists
- data-quality reports
- delivery checklists
- success metrics
- run records

These files make automation easier to review, repeat, and hand off.

## Public Demo Script

Use this short story in a README, release note, or X post:

```text
I open-sourced AI Automation Starter Kit.

It discovers business automation opportunities from GitHub, ranks candidate OSS projects, and turns the result into repeatable workflow artifacts.

Start with:
ai-automation-kit github-discover --business-area operations --limit 2 --output .tmp/operations-discovery

Then use the five templates for research, docs Q&A, approved replies, spreadsheet-to-app migration, and delivery packaging.
```

## Release Checklist

- Run `python3 -m pytest -q`
- Run `python3 scripts/run_all_demos.py`
- Run one live `github-discover` smoke test
- Confirm `.tmp/` outputs are ignored
- Confirm `.env` files are ignored
- Confirm `business_automation_plan.md` is useful without extra explanation
