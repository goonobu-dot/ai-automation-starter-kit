# Research Report: AI automation starter kit value

## Run Timeline

- Run ID: `example-run`
- Started: `2026-06-16T00:00:00Z`
- Finished: `2026-06-16T00:00:00Z`

## Source Table

| # | Title | URI | Summary |
|---:|---|---|---|
| 1 | AI Workflow Automation | `examples/research-agent/sample_sources/ai_workflows.html` | AI workflow automation connects repeatable business tasks with tools, approvals, and saved outputs. |
| 2 | Document RAG Starter | `examples/research-agent/sample_sources/rag_docs.html` | Document RAG pipelines convert files into searchable knowledge with citations and repeatable ingestion. |

## Failed URL Log

- None

## Rerun Command

```bash
PYTHONPATH=src python3 -m ai_automation_kit.cli research-agent --config examples/research-agent/sample_research.json --output .tmp/research-agent-demo
```

