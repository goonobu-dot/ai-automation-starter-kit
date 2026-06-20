# 実運用セットアップガイド

このプロジェクトは、初期状態では安全のため dry-run です。Gmail送信、Slack投稿、Google Sheets書き込みなどは勝手に実行しません。

## 実運用前の確認

```bash
ai-automation-kit connector-doctor --project .tmp/flow-project --output .tmp/connector-doctor
```

## 実接続で必要なこと

- 顧客が所有するアカウントを使う
- 認証情報を `.env` か顧客の秘密情報管理に置く
- 送信、投稿、書き込みの前に承認者を決める
- ログに機密情報を残しすぎない
- 失敗時に止める手順を書く
- まず少量データで試す

## よくある接続先

| 接続先 | 最初の使い方 | 注意点 |
|---|---|---|
| Gmail / Outlook | 下書き生成 | 自動送信は最後まで無効でよい |
| Slack / Teams | 承認依頼の下書き | Webhook管理と投稿先を確認 |
| Google Sheets | 入力CSVの代わり | 書き込み権限を最小化 |
| Notion / Airtable | タスク管理 | データ構造の変更に注意 |
| HubSpot / CRM | リード整理 | 本番更新は承認後 |
| n8n / Make / Zapier | 外部連携の実装先 | タスク数、認証、保守範囲を確認 |

## 本番化してよい条件

- dry-run の結果を顧客が確認した
- ROIまたは業務改善の仮説がある
- 承認者が決まっている
- エラー時の停止手順がある
- 保守担当が決まっている

