# 運用拡張ガイド

このガイドは、dry-run の見本を、より実務的な導入準備へ進めるための補助資料です。

## 追加されたコマンド

- `deployment-pack`
- `runtime-safety`
- `secrets-bootstrap`
- `document-intake`
- `observability-pack`
- `state-backend`

## 例

```bash
ai-automation-kit deployment-pack \
  --flow-id invoice-document-followup \
  --provider coolify \
  --connectors gmail,google-sheets \
  --output .tmp/deployment-coolify
```

```bash
ai-automation-kit runtime-safety --flow-id invoice-document-followup --output .tmp/runtime-safety
ai-automation-kit secrets-bootstrap --flow-id invoice-document-followup --provider infisical --connectors gmail,google-sheets --output .tmp/secrets-bootstrap
ai-automation-kit document-intake --flow-id invoice-document-followup --mode advanced --output .tmp/document-intake
ai-automation-kit observability-pack --flow-id invoice-document-followup --output .tmp/observability-pack
ai-automation-kit state-backend --flow-id invoice-document-followup --backend supabase --output .tmp/state-backend
```
