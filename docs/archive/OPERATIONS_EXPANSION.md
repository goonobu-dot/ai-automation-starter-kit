# Operations Expansion

This guide explains the new packs that turn a local dry-run into a safer real-world deployment path.

## Commands

- `deployment-pack`
- `runtime-safety`
- `secrets-bootstrap`
- `document-intake`
- `observability-pack`
- `state-backend`

## Example Commands

```bash
ai-automation-kit deployment-pack \
  --flow-id invoice-document-followup \
  --provider coolify \
  --connectors gmail,google-sheets \
  --output .tmp/deployment-coolify
```

```bash
ai-automation-kit runtime-safety \
  --flow-id invoice-document-followup \
  --output .tmp/runtime-safety
```

```bash
ai-automation-kit secrets-bootstrap \
  --flow-id invoice-document-followup \
  --provider infisical \
  --connectors gmail,google-sheets \
  --output .tmp/secrets-bootstrap
```

```bash
ai-automation-kit document-intake \
  --flow-id invoice-document-followup \
  --mode advanced \
  --output .tmp/document-intake
```

```bash
ai-automation-kit observability-pack \
  --flow-id invoice-document-followup \
  --output .tmp/observability-pack
```

```bash
ai-automation-kit state-backend \
  --flow-id invoice-document-followup \
  --backend supabase \
  --output .tmp/state-backend
```
