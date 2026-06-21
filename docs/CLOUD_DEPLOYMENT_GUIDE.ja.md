# クラウド導入ガイド

このガイドは、AIやクラウドにまだ慣れていない人が、企業向けの業務自動化を「ローカルで見せる」段階から「クラウドで動かす準備」まで進めるための実務マニュアルです。

クラウドを全部理解してから始める必要はありません。最初に必要なのは、何を自動化したいか、どの入力を受け取るか、どこに結果を出すか、誰が確認するかを決めることです。このプロジェクトは、その情報をもとに AIエージェントが設定資料、必要な入力、クラウド候補、確認ポイントを整理できるようにします。

## まず理解すること

クラウド導入は、魔法の自動化ではありません。安全に進めるには、AIができることと、人間の承認が必要なことを分けます。

AIができること:

- 業務フローを選ぶ。
- 必要な入力を質問リストにする。
- ローカル dry-run 用のフォルダを作る。
- クラウド構成案を作る。
- `cloud-plan` で provider、workload、connector ごとの資料を作る。
- コマンド例、設定値一覧、rollback 手順を作る。
- Claude Code、Codex、Cursor などへ渡す作業依頼文を作る。

人間の承認が必要なこと:

- クラウドアカウントへログインする。
- 課金や予算アラートを承認する。
- APIキー、OAuth、Webhook URL、secret を本物の管理画面に入れる。
- 企業データをクラウドへ置いてよいか判断する。
- 本番 traffic、scheduler、queue、webhook を有効にする。
- 問題が起きた時の停止・rollback 責任者を決める。

## 最初のおすすめルート

最初から本番クラウドを作らないでください。初心者が失敗しにくい順番は次の通りです。

1. `flows list` で企業に説明しやすいフローを選ぶ。
2. `complete-workspace` でローカルの見本フォルダを作る。
3. dry-run を実行して、入力、出力、承認キューを確認する。
4. 顧客に「本番送信はまだしない」状態で見せる。
5. 顧客が価値を理解したら、`guided-setup` で必要情報を集める。
6. `guided-review` で不足項目を確認する。
7. `cloud-plan` でクラウド導入資料を作る。
8. 人間がアカウント、課金、secret、権限、domain、webhook、scheduler、queue を確認する。
9. 小さなテスト traffic だけで動作確認する。
10. 価値、リスク、費用、rollback を確認してから本番化を判断する。

## コマンド例

まずはローカルで説明できる状態を作ります。

```bash
ai-automation-kit complete-workspace \
  --flow-id invoice-document-followup \
  --client-type local-business \
  --niche accounting \
  --output .tmp/client-demo
```

クラウドに進める段階では、workload を選びます。

```bash
ai-automation-kit cloud-plan \
  --flow-id invoice-document-followup \
  --provider aws \
  --workload scheduled-job \
  --connectors gmail,google-sheets \
  --output .tmp/cloud-plan
```

Webhook/API 型の例です。

```bash
ai-automation-kit cloud-plan \
  --flow-id support-reply-draft \
  --provider google-cloud \
  --workload webhook-api \
  --connectors webhook,google-sheets \
  --output .tmp/cloud-plan-webhook
```

## workload の選び方

`webhook-api`:
外部サービスから HTTP で通知を受ける業務に向きます。LINE、Slack、問い合わせフォーム、外部システムからの通知などです。

`scheduled-job`:
毎日、毎週、毎月など決まったタイミングで処理する業務に向きます。請求書フォロー、予約リマインド、週次レポート、在庫チェックなどです。

`worker-queue`:
処理件数が多い、失敗時に再試行したい、順番待ちが必要な業務に向きます。大量メール、データ整形、CRM更新などです。

`web-app`:
担当者がブラウザで確認、承認、修正したい業務に向きます。管理画面、承認画面、顧客へのデモ画面が必要な時です。

`static-functions`:
軽いWebページと小さなAPIで足りる時に向きます。フォーム、簡易見積もり、受付ページなどです。

`container-service`:
長く動く処理、特殊なライブラリ、独自runtimeが必要な時に向きます。初心者は最初から選ばず、必要が出た時に選んでください。

## provider の選び方

初心者の最初のPoC:
Render、Railway、Vercel が説明しやすいです。設定画面が分かりやすく、短時間でURLを出しやすいからです。

Google系ツールが多い:
Google Cloud が向きます。Gmail、Google Sheets、Google Drive と相性がよいです。

企業がAWSを使っている:
AWS が向きます。Lambda、EventBridge、SQS、Secrets Manager を使う形が多くなります。

Microsoft 365、Teams、SharePoint が中心:
Azure が向きます。社内IT部門が Azure を管理している企業では説明しやすいです。

Dockerに慣れている:
Fly.io、DigitalOcean、Render の container 系が候補になります。

## AIエージェントへの依頼文

以下を Claude Code、Codex、Cursor などに貼ると、導入作業を進めやすくなります。

```text
この GitHub プロジェクト ai-automation-starter-kit を確認してください。
私はAI初心者ですが、企業向けの業務自動化を小さなPoCとして提案したいです。

まず README.md、docs/CLOUD_DEPLOYMENT_GUIDE.ja.md、docs/CLOUD_BEGINNER_PLAYBOOK.ja.md、docs/CONNECTOR_SETUP_GUIDE.ja.md を読んでください。

次に、以下の条件で進めるために、必要な入力、不足情報、ローカルdry-run、cloud-plan、顧客に確認する事項を順番に案内してください。

- 業務内容:
- 使いたいフロー:
- 顧客の業種:
- 入力元:
- 出力先:
- 使いたいクラウド:
- 使いたいconnector:
- 人間の承認者:

本物のAPIキーやsecretはチャットに書かせないでください。
本番送信や本番webhook有効化の前に、必ず人間の承認ステップを作ってください。
```

## 顧客に説明する時の言い方

最初から「完全自動化できます」と言わないでください。次のように説明してください。

「まずは本番送信しない dry-run で、現在の業務をどこまで整理できるか確認します。入力データを読み取り、AIが下書きや作業キューを作り、人間が承認する形にします。価値が見えたら、クラウドで安全に動かすための設定、費用、権限、停止手順を一緒に確認します。」

この言い方なら、初心者でも無理な約束をせず、企業側も安心して小さく試せます。

## 成功の基準

最初のクラウド導入で目指すべき成功は「全部自動化」ではありません。

- 顧客が何に困っているか説明できる。
- dry-run で作業前後の違いを見せられる。
- 承認が必要な箇所を明確にできる。
- 必要なAPI、folder、spreadsheet、mailbox、webhookを一覧化できる。
- クラウド費用と停止手順を説明できる。
- 本番化するか、修正するか、止めるかを判断できる。

ここまでできれば、AI初心者でも企業に対して現実的な自動化提案ができます。

