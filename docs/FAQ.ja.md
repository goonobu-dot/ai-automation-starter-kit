# FAQ

## これは本当に自動化システムですか？

はい。ただし初期状態では安全な dry-run です。ローカルでキュー、下書き、承認リスト、レポート、ローカル outbox を作ります。外部送信や本番更新は勝手にしません。

## 普通にAIチャットへ頼むのと何が違いますか？

AIチャットは会話で終わりやすいです。このプロジェクトは、フロー、提案書、ROI表、実行ログ、承認リスト、顧客レポートをファイルとして残します。

## 副業で使えますか？

使える形を目指しています。ただし収益保証ではありません。企業の繰り返し業務を見つけ、小さな dry-run PoC として提案するための道具です。

## 最初に何を実行すればいいですか？

```bash
ai-automation-kit quickstart --flow-id invoice-document-followup --output .tmp/quickstart
```

## 企業に何を見せればいいですか？

まず `demo_site/index.html` と `beginner_sales/selected_flow_demo.html` を見せます。そのあと `client_questions.md` でヒアリングし、`proposal_one_pager.md` で小さなPoCを提案します。

## 本番接続はできますか？

設計上は進められますが、初期状態では無効です。`connector-doctor` で不足設定を確認し、顧客の承認、認証情報、データ分類、停止手順を決めてから進めます。

