# Execution Bridges

This guide explains the execution bridge layer in AI Automation Starter Kit.

After you prove a workflow locally, you can export it into a starter for a real execution platform without rebuilding the workflow shape by hand.

## Supported Targets

- `n8n`
- `activepieces`
- `windmill`

## Example Commands

```bash
ai-automation-kit flow-export \
  --flow-id invoice-document-followup \
  --target n8n \
  --output .tmp/flow-export-n8n
```

```bash
ai-automation-kit flow-export \
  --flow-id invoice-document-followup \
  --target activepieces \
  --output .tmp/flow-export-activepieces
```

```bash
ai-automation-kit flow-export \
  --flow-id invoice-document-followup \
  --target windmill \
  --output .tmp/flow-export-windmill
```

## What You Get

- flow mapping notes
- target-specific starter files
- import or webhook notes
- preserved human approval boundaries
