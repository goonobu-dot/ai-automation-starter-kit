# 実行ブリッジ

このガイドは、ローカル dry-run で確認したフローを、実際の実行基盤へ渡すための入口です。

## 対応先

- `n8n`
- `activepieces`
- `windmill`

## 例

```bash
ai-automation-kit flow-export \
  --flow-id invoice-document-followup \
  --target n8n \
  --output .tmp/flow-export-n8n
```

生成されるのは、完成済み本番環境ではなく、取り込み用の starter です。

承認ステップと dry-run 境界は、そのまま残して使ってください。
