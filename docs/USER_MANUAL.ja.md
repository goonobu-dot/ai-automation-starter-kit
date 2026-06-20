# AI Automation Starter Kit 使い方マニュアル

このマニュアルは、AIエージェントを使い始めた人が、業務自動化の候補を選び、デモを作り、企業へ説明し、小さな dry-run PoC まで進めるための手順です。

収益を保証するものではありません。目的は、あいまいなAI自動化の話を、見えるフロー、提案書、実行結果、承認ポイントつきの安全な案件に変えることです。

## 1. 最初に実行する

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip setuptools
python3 -m pip install -e .
ai-automation-kit doctor --output .tmp/doctor
```

## 2. まず1つの案件フォルダを作る

```bash
ai-automation-kit quickstart \
  --flow-id invoice-document-followup \
  --client-type local-business \
  --niche accounting \
  --output .tmp/quickstart-accounting
```

生成される主なファイル:

- `.tmp/quickstart-accounting/START_HERE.md`
- `.tmp/quickstart-accounting/flow_project/`
- `.tmp/quickstart-accounting/beginner_sales/`
- `.tmp/quickstart-accounting/demo_site/index.html`

## 3. 業務フローを選ぶ

```bash
ai-automation-kit flow-guide --industry finance --niche accounting --output .tmp/flow-guide
```

`recommended_flows.md` を見て、企業に説明しやすいフローを選びます。最初は、請求書、問い合わせ、日報、承認、リマインドのように、入力と出力が分かりやすいものを選びます。

## 4. 企業に見せる資料を作る

```bash
ai-automation-kit beginner-sales \
  --flow-id invoice-document-followup \
  --client-type local-business \
  --niche accounting \
  --output .tmp/beginner-sales
```

見る順番:

1. `selected_flow_demo.html`
2. `client_questions.md`
3. `roi_simple_calculator.csv`
4. `proposal_one_pager.md`
5. `three_day_poc_plan.md`

## 5. 実際の dry-run を動かす

```bash
ai-automation-kit flows install invoice-document-followup --output .tmp/flow-project
ai-automation-kit flows run .tmp/flow-project
ai-automation-kit flows approve .tmp/flow-project --approver owner@example.com
```

生成される主な結果:

- `automation_output/work_queue.csv`
- `automation_output/draft_outputs.md`
- `automation_output/approval_queue.csv`
- `automation_output/status_report.md`
- `local_outbox/email_drafts.md`
- `local_outbox/slack_messages.md`

## 6. 顧客向けレポートを作る

```bash
ai-automation-kit client-report --flow-project .tmp/flow-project --output .tmp/client-report
```

`client_report.md` と `client_report.html` が作られます。企業には、何件処理したか、どのファイルを見ればよいか、次に続けるべきかを説明できます。

## 7. 共有用パッケージを作る

```bash
ai-automation-kit package-client-demo --source .tmp/quickstart-accounting --output .tmp/client-demo-package
```

`client_demo_package.zip` が作られます。共有前に、秘密情報や顧客の機密データが入っていないか必ず確認してください。

## 8. 実運用へ進む前に確認する

```bash
ai-automation-kit connector-doctor --project .tmp/flow-project --output .tmp/connector-doctor
```

Gmail送信、Slack投稿、Google Sheets書き込みなどは、初期状態では無効です。本番接続は、顧客の承認、認証情報、データ分類、停止手順、承認者を決めてから進めます。

