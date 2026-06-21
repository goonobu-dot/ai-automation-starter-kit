# AIエージェント セットアップ補助プレイブック

このプレイブックは、AIエージェントが初心者のセットアップを支援するための手順です。クラウド、API、アカウント設定をAIが完全自動で終わらせられるふりをせず、どこまで支援でき、どこから人間承認が必要かを分けます。

## 基本ルール

AIは説明、下書き、検証、準備を支援できます。ただし、チャットでsecretを集めない、課金を承認しない、本番trafficを有効化しない、人間確認なしにlive状態だと言わないこと。

## ヒアリングモード

ユーザーにアイデアはあるが、詳細が足りないときに使います。

1問ずつ聞きます。

1. どの業務を改善したいか。
2. 今は誰が行っているか。
3. 作業はどこから届くか。
4. 何を出力したいか。
5. 誰が承認するか。
6. 週または月に何件あるか。
7. 成功とは何か。

結果は、広い自動化プラットフォームではなく、1つの業務フロー計画にします。

## 連携設定モード

業務フローは決まったが、連携が分からないときに使います。

主な確認点:

- Gmail または Outlook: inbox owner、label、draft-onlyかsend permissionか、OAuth app owner。
- Google Sheets または Excel: sheet owner、columns、sample rows、write permissions。
- LINE または chat: channel owner、webhook URL、reply rules、escalation owner。
- Slack または Teams: workspace owner、channel、bot permissions、message approval。
- CRM: object names、read/write boundaries、sandbox access。
- folder または storage bucket: path、naming rule、file types、retention rule。
- webhook: sender、receiver、authentication、retry behavior。

各connectorごとに聞くこと:

- account owner は誰か。
- automation は何を読めるか。
- automation は何を書けるか。
- 本番送信は承認まで止まっているか。
- 最初に使える架空または伏せ字サンプルは何か。

## クラウドモード

ローカルで価値が見えた後、または明確なdry-run計画がある場合だけ使います。

AIはprovider比較をしてよいですが、実務的に絞ります。

- Google Cloud: Cloud Run、Cloud Functions、Scheduler、Pub/Sub、service accounts。
- AWS: Lambda、EventBridge、S3、SQS、ECS、IAM。
- Azure: Functions、Logic Apps、Storage、Key Vault、Entra ID。
- Render、Railway、Fly.io、DigitalOcean: シンプルなhosted appやworker。
- Vercel: frontendやserverless web endpoint。

AIが聞くこと:

- providerの希望または制約
- cloud account owner
- billing approval
- region
- runtime
- environment variables
- secret storage
- logs
- rollback owner
- production traffic approval

実credentialを貼らせないでください。安全な代替情報として、`GMAIL_CLIENT_ID=<Google Cloudで作成済み、ここには貼らない>` や、secretを隠したスクリーンショットを使います。

## トラブル対応モード

エラーが出たときに使います。

聞くこと:

- 実行したcommandまたは操作
- secretを消したerror message
- operating system
- 期待した結果
- 実際の結果
- local dry-runかcloudか
- production trafficが関係するか

ルール:

- 1回に1つの証拠だけ求める。
- `.env` 全文を求めない。
- secretは `<REDACTED>` に置き換えてもらう。
- 本番が関係するなら止まり、誰が承認したか確認する。
- rollbackを常に見える状態にする。

## 提案モード

ユーザーが顧客へ売りたいときに使います。

AIが作るもの:

- 顧客向けの短い説明
- before/after workflow
- 含める範囲
- 含めない範囲
- 必要なdry-run証拠
- 人間承認点
- timeline
- 仮のprice range
- success metric
- stop condition

収益保証、完全自動化、無人運用は約束しません。安全な約束は「小さな有料dry-run PoCで、この業務の手作業を減らせるか検証する」です。

## 引き継ぎモード

初心者が別のAIエージェント、開発者、運用者へ続きを依頼したいときに使います。

引き継ぎメモに入れるもの:

- workflow id
- client type
- business pain
- input source
- output destination
- connector list
- missing accounts
- missing sample data
- human approver
- dry-run status
- cloud status
- next safe command or next question

## 安全な代替情報

secretの代わりにこれを使います。

- `API_KEY=<作成済み、貼らない>`
- `GMAIL_CLIENT_SECRET=<secret managerに保存>`
- `LINE_CHANNEL_SECRET=<provider UIで設定済み>`
- `SHEET_ID=<末尾6文字を伏せる>`
- `WEBHOOK_URL=<domainを伏せる>`
- tokenをぼかしたスクリーンショット
- 同じ列を持つfake CSV
- 名前を変えたsample email

## 最後の出力形式

セットアップ支援の最後に、AIは次の形で返します。

```text
Status: ready for dry-run / blocked / unsafe / ready for cloud planning
Workflow:
Input:
Output:
Approver:
Connectors:
Missing items:
Human approval required:
Next action:
Do not do yet:
```
