# クラウド トラブルシューティング

このガイドは、初心者がクラウド導入で止まりやすい問題を切り分けるためのものです。焦って本番化せず、エラーを1つずつ確認してください。

## デプロイに失敗

確認すること:

- provider にログインしているか。
- billing が有効か。
- region や project が正しいか。
- 必要な IAM role があるか。
- build するファイルが repository にあるか。
- Python version や runtime が一致しているか。

AIエージェントへの依頼:

```text
deploy_runbook.md とエラー全文を確認してください。
本番のsecretは表示せず、失敗原因を account, billing, IAM, runtime, missing file, command syntax に分類してください。
次に実行する安全な確認コマンドだけを提案してください。
```

## secret が足りない

症状:

- 起動はするが処理が止まる。
- `secret is missing` や `environment variable not found` が出る。
- connector が認証できない。

確認すること:

- `secrets_and_env.md` の値が全部 provider に登録されているか。
- 値の名前が完全一致しているか。
- 本番値を GitHub に commit していないか。
- ローカル `.env` とクラウド secrets を混同していないか。

対応:
secret 名だけをチャットに出し、本物の値はクラウド管理画面に入れてください。

## webhook が届かない

確認すること:

- workload が `webhook-api` か。
- public HTTPS URL があるか。
- 外部サービス側の webhook URL が正しいか。
- path が `/webhook` など想定通りか。
- signature secret が合っているか。
- logs に request が残っているか。

LINE の場合:
LINE Developers の webhook 設定は connector 事例の1つです。LINE 固定で考えず、Slack、フォーム、CRM webhook でも同じように URL、secret、log を確認します。

## scheduler が動かない

確認すること:

- workload が `scheduled-job` か。
- schedule expression が正しいか。
- timezone の認識がずれていないか。
- 対象 function/job が存在するか。
- 実行 role があるか。
- logs に実行履歴があるか。

初心者向け対応:
最初は1日1回ではなく、テスト用に短い間隔で実行し、確認後に本番間隔へ戻してください。

## queue が詰まる

確認すること:

- workload が `worker-queue` か。
- worker が起動しているか。
- retry 回数が多すぎないか。
- dead-letter queue や失敗ログがあるか。
- 同じデータを何度も処理していないか。

対応:
本番データを増やす前に、1件だけで再試行と失敗時の動きを確認してください。

## rollback

問題が起きたら、まず止めます。

1. webhook、scheduler、queue consumer、public traffic を止める。
2. 直前の revision へ戻すか、service を停止する。
3. 漏れた可能性がある secret を rotate する。
4. logs を保存する。
5. 顧客へ「停止済み、調査中、次回報告時刻」を伝える。

初心者が最初から完璧に直す必要はありません。最初に安全に止められることが重要です。

