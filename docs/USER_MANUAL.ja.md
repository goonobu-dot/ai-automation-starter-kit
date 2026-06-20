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

迷った場合は、まずこの1コマンドを使います。案件フォルダ、dry-run 実行結果、承認記録、コネクタ診断、顧客レポート、デモサイト、共有用 zip、最終チェックリスト、収益化評価、営業クロージング台本、有償PoC範囲、価値測定シート、契約前チェック、提案メール、30日運用計画、成果証明テンプレート、公開OSSパターン比較、統合バックログ、導入方式、運用監視計画、案件化スコア、顧客オンボーディング、本番移行判断、ブラウザで見られるコマンドセンター、AI初心者向けの事業化提案パックまでまとめて作ります。

```bash
ai-automation-kit complete-workspace \
  --flow-id invoice-document-followup \
  --client-type local-business \
  --niche accounting \
  --output .tmp/complete-accounting
```

最初に見るファイル:

- `.tmp/complete-accounting/FINAL_DELIVERY_GUIDE.md`
- `.tmp/complete-accounting/completion_checklist.md`
- `.tmp/complete-accounting/client_report/client_report.html`
- `.tmp/complete-accounting/demo_site/index.html`
- `.tmp/complete-accounting/client_demo_package/client_demo_package.zip`
- `.tmp/complete-accounting/revenue_readiness_scorecard.md`
- `.tmp/complete-accounting/sales_closing_script.md`
- `.tmp/complete-accounting/paid_poc_scope.md`
- `.tmp/complete-accounting/value_measurement_sheet.csv`
- `.tmp/complete-accounting/pre_contract_checklist.md`
- `.tmp/complete-accounting/client_proposal_email.md`
- `.tmp/complete-accounting/first_30_days_plan.md`
- `.tmp/complete-accounting/proof_of_value_template.md`
- `.tmp/complete-accounting/oss_pattern_benchmark.md`
- `.tmp/complete-accounting/integration_backlog.md`
- `.tmp/complete-accounting/deployment_options.md`
- `.tmp/complete-accounting/production_observability_plan.md`
- `.tmp/complete-accounting/automation_opportunity_scorecard.csv`
- `.tmp/complete-accounting/client_onboarding_form.md`
- `.tmp/complete-accounting/go_live_decision.md`
- `.tmp/complete-accounting/client_command_center.html`
- `.tmp/complete-accounting/side_business_starter_10.md`
- `.tmp/complete-accounting/before_after_demo.html`
- `.tmp/complete-accounting/business_launch/START_HERE_BUSINESS_LAUNCH.md`
- `.tmp/complete-accounting/business_launch/first_client_offer.md`

個別に作業したい場合は、次の `quickstart` から順番に進めます。

## 2.1. AIに慣れていない人が企業へ事業化提案する

「どの会社に、何を、いくらで、どう説明すればいいか」が分からない場合は、事業化提案パックを作ります。

```bash
ai-automation-kit business-launch \
  --industry finance \
  --client-type local-business \
  --niche accounting \
  --output .tmp/business-launch
```

生成される主なファイル:

- `.tmp/business-launch/START_HERE_BUSINESS_LAUNCH.md`
- `.tmp/business-launch/target_industry_playbook.md`
- `.tmp/business-launch/first_client_offer.md`
- `.tmp/business-launch/discovery_call_script.md`
- `.tmp/business-launch/proposal_builder.md`
- `.tmp/business-launch/pricing_and_scope_menu.md`
- `.tmp/business-launch/risk_boundary_sheet.md`
- `.tmp/business-launch/30_day_business_launch_plan.md`
- `.tmp/business-launch/client_pitch_email.md`

このパックは、いきなり本番自動化を売るためのものではありません。最初は、企業の繰り返し業務を見える化し、サンプルデータで dry-run し、Paid PoC として安全に提案するためのものです。

## 2.5. 何を売り込むか迷った場合

営業用の案件カタログを作ります。

```bash
ai-automation-kit opportunity-catalog --industry finance --output .tmp/opportunity-catalog
```

`opportunity_catalog.html` を開くと、提案しやすい自動化案件、価格目安、導入日数、証明する指標を一覧できます。

顧客の困りごとからおすすめフローを選ぶ場合:

```bash
ai-automation-kit recommend-flow \
  --industry finance \
  --pain "missing invoice follow up" \
  --tools "Google Sheets Gmail" \
  --monthly-items 80 \
  --output .tmp/recommend-flow
```

共有前に安全確認する場合:

```bash
ai-automation-kit share-check --source .tmp/complete-accounting --output .tmp/share-check
```

`share_check.md` が `blocked` の場合は、秘密情報らしい文字列を消してから共有します。

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

`client_command_center.html` を最初に開くと、初回確認、案件化、有償PoC、顧客確認、本番移行のどの資料を見るべきかをブラウザ上で確認できます。さらに `oss_pattern_benchmark.md`、`integration_backlog.md`、`deployment_options.md`、`production_observability_plan.md`、`automation_opportunity_scorecard.csv`、`client_onboarding_form.md`、`go_live_decision.md` も確認します。n8n、Activepieces、Windmill、Trigger.dev のような公開OSS/公開サービスで一般的な考え方を参考に、テンプレート化、MCP化できる統合、Webhook/UI化、リトライ、キュー、承認監査、ログ確認、顧客の承認者、本番移行の可否まで準備してから実運用へ進めます。
