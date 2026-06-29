# 業務自動化 拡充機能ガイド

このガイドは、OpenAI、Anthropic、n8n、Activepieces、Windmill、Dify、Flowise、CrewAI、GitHub Actions などの公開情報やオープンソースから学べる構造を、このプロジェクトに取り込んだ拡充機能の説明です。

目的は、他のプロジェクトをコピーすることではありません。役立つ考え方を学び、AI初心者でも業務自動化を副業や企業導入に使いやすい形へ変換することです。

## 最初はコマンドセンターから

```bash
ai-automation-kit command-center --language both --output .tmp/command-center
```

見るファイル:

- `START_HERE_COMMAND_CENTER.md`
- `COMMAND_CENTER.md`
- `COMMAND_CENTER.ja.md`
- `command_center.html`
- `next_step_decision_tree.md`

機能が増えて迷子になりそうなときは、ここから始めてください。

## 12個の拡充パック

| パック | コマンド | 参考にした考え方 | 使う場面 |
|---|---|---|---|
| AIエージェント用スキル | `skill-pack` | Anthropic Skills、Codex skills、Cursor rules | AIに毎回同じ指示を渡したい |
| 人間承認ゲート | `approval-gate` | OpenAI guardrails、人間承認 | AIの下書きと実行を分けたい |
| MCPコネクタ計画 | `mcp-connector-plan` | OpenAI/Anthropic MCP | Gmail、Sheets、Slack、Drive、LINE、Webhook の準備をしたい |
| エージェントチーム | `agent-team` | Claude subagents、CrewAI | 営業、ヒアリング、実装、QA、納品の役割を分けたい |
| 評価改善ループ | `eval-loop` | OpenAI/Anthropic eval | 自動化が本当に役立ったか測りたい |
| フロー説明 | `workflow-explainer` | n8n、Flowise、Windmill | 顧客に業務フローを見える化したい |
| セルフホスト導入 | `self-host-pack` | n8n self-host、Docker runbook | Docker、VPS、クラウド運用を考えたい |
| コネクタ部品カタログ | `connector-catalog` | Activepieces pieces、n8n integrations | どの業務にどの接続部品が必要か知りたい |
| スクリプトUI化 | `script-ui-pack` | Windmill | スクリプトをフォーム、ジョブ、Webhook、管理画面にしたい |
| ナレッジRAG | `knowledge-rag-pack` | Dify、Flowise、docs RAG | 社内FAQや書類Q&Aを作りたい |
| 自動検査フック | `automation-hooks` | Claude Code hooks、CI checks | 共有前や導入前に自動チェックしたい |
| ガバナンス | `governance-pack` | GitHub Actions、企業向け運用管理 | セキュリティ、監査、事故対応、月次レビューを整えたい |

## 初心者におすすめの順番

1. `command-center`
2. `side-hustle-blueprints`
3. `skill-pack`
4. `approval-gate`
5. `mcp-connector-plan`
6. `workflow-explainer`
7. `eval-loop`
8. `governance-pack`

この順番なら、売る案件を決め、AIに渡す指示を作り、人間承認の境界を決め、接続準備をし、顧客に説明し、価値を測り、運用ルールまで作れます。

## 安全ルール

AIは、分類、整理、下書き、説明、準備ができます。ただし、顧客への送信、予約確定、価格変更、返金、法務・医療・金融・人事などの判断、本番コネクタ変更、クラウド課金、公開文言は、人間が承認してください。

