# 初心者ルートマップ

このページは、このプロジェクトを開いて「資料が多すぎて、どこから読めばいいか分からない」と感じる人のための地図です。

最初から全部読まないでください。このプロジェクトは、GitHub調査、副業提案、ローカルdry-run、クラウド設定、承認ゲート、デモ生成、公開前チェックまで含んでいるため、資料が多くなっています。初心者は、最初から全部を理解しようとせず、1つのルートだけを選んで進めれば大丈夫です。

最初のルールはこれです。

> 1つの業務、1つのサンプル入力、1つの下書き出力、1人の承認者。

このルールを守ると、このプロジェクトはかなり使いやすくなります。

## まず結論

最初はこの順番です。

1. このページを読む。
2. [まずここから](START_HERE.ja.md) を読む。
3. [AI初心者サポートマップ](AI_BEGINNER_SUPPORT_MAP.ja.md) を読む。
4. ターミナル操作が不安なら、CLIを使わないルートで進む。
5. ファイルを自動生成したいなら、CLIを使うルートで進む。
6. 本物のAPIキー、顧客の機密情報、本番アクセス、課金が発生するクラウド変更は、人間承認なしに扱わない。

## このプロジェクトで何ができるのか

このプロジェクトは、あいまいな業務自動化の相談を、見えるファイルに変えます。

- 業務フロー図
- 足りない入力情報の一覧
- dry-run計画
- AIの下書き出力
- 人間承認キュー
- 顧客向けレポート
- 提案書や有料PoCの範囲
- クラウドやコネクタ設定のチェックリスト
- 本番化するか、止めるかの判断材料

大事なのは、初日に全部を自動化しようとしないことです。まず、1つの小さな業務を安全に説明できる状態にします。

## 最初に開くもの

5つだけ開くなら、これです。

| 順番 | ファイル | 理由 |
|---|---|---|
| 1 | `docs/BEGINNER_ROUTE_MAP.ja.md` | 読む順番を決め、資料迷子を防ぐため。 |
| 2 | `docs/START_HERE.ja.md` | 最初の3分で全体像をつかむため。 |
| 3 | `docs/AI_BEGINNER_SUPPORT_MAP.ja.md` | AIに任せてよいことと、人間が承認することを分けるため。 |
| 4 | `docs/AI_AGENT_GRILL_ME_SKILL.ja.md` | ChatGPT、Claude、Cursor、Codex、Claude Code などに1問ずつ案内してもらうため。 |
| 5 | `docs/USER_MANUAL.ja.md` | インストールや生成コマンドに進むときの詳しい手順。 |

## 最初は無視してよいもの

最初は無視してよいもの:

- リリースや公開作業のためのファイル
- GitHub Actions やパッケージングの細かい設定
- 生成される全ファイル名の暗記
- すべてのクラウド選択肢
- すべてのコネクタ選択肢
- 高度なガバナンス資料
- 公開OSS調査の細かい資料

最初の業務フローが決まってから戻れば十分です。

## ルートを選ぶ

### CLIを使わないルート

ターミナル、Python、API、クラウド設定がまだ不安な人は、このルートです。

1. [AIエージェント Grill Me スキル](AI_AGENT_GRILL_ME_SKILL.ja.md) を開きます。
2. ChatGPT、Claude、Gemini、Cursor、Codex、Claude Code などに貼ります。
3. AIに「このGitHubプロジェクトを一緒に読んで」と依頼します。
4. 「1問ずつ質問して。1つの業務を選ぶのを手伝って」と伝えます。
5. 業務内容は答えてよいですが、secretや顧客機密情報は貼りません。
6. クラウドやAPI設定に入る前に、AIに簡単な計画を作らせます。

そのまま使える依頼文:

```text
この GitHub プロジェクト ai-automation-starter-kit を一緒に読んでください。
私は初心者です。一度にたくさん質問しないでください。
1問ずつ質問してください。
1つの小さな業務、1つの入力元、1つの下書き出力、1人の承認者を決めるのを手伝ってください。
本物のAPIキー、password、secret、顧客の機密情報、本番アクセスはチャットに貼らせないでください。
業務フローが見えたら、このプロジェクトのどのファイルを次に読めばよいか教えてください。
```

### CLIを使うルート

このプロジェクトにファイル一式を生成してほしい場合は、このルートです。

インストール:

```bash
git clone https://github.com/goonobu-dot/ai-automation-starter-kit.git
cd ai-automation-starter-kit
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip setuptools
python3 -m pip install -e .
ai-automation-kit doctor --output .tmp/doctor
```

最初の見本ワークスペースを作ります。

```bash
ai-automation-kit complete-workspace \
  --flow-id invoice-document-followup \
  --client-type local-business \
  --niche accounting \
  --output .tmp/complete-accounting
```

最初に開くもの:

1. `.tmp/complete-accounting/FINAL_DELIVERY_GUIDE.md`
2. `.tmp/complete-accounting/client_command_center.html`
3. `.tmp/complete-accounting/demo_site/index.html`
4. `.tmp/complete-accounting/client_report/client_report.html`
5. `.tmp/complete-accounting/business_launch/START_HERE_BUSINESS_LAUNCH.md`

### 副業・受託ルート

小さな会社や店舗へ、自動化支援を副業や受託として提案したい場合は、このルートです。

```bash
ai-automation-kit side-hustle-blueprints \
  --industry local-business \
  --operator-level beginner \
  --output .tmp/side-hustle-blueprints
```

開くもの:

1. `.tmp/side-hustle-blueprints/START_HERE_SIDE_HUSTLE_BLUEPRINTS.md`
2. `.tmp/side-hustle-blueprints/first_client_picker.md`
3. `.tmp/side-hustle-blueprints/client_intake_questions.md`
4. `.tmp/side-hustle-blueprints/risk_boundaries.md`

最初の商品は「会社を丸ごと自動化します」ではありません。小さな有料dry-run PoCとして提案します。

### 社内導入ルート

会社の中で、または会社の1チームを支援して、繰り返し業務を改善したい場合はこのルートです。

```bash
ai-automation-kit flow-guide \
  --industry operations \
  --niche admin \
  --output .tmp/flow-guide
```

1つの業務を選び、ローカルに入れます。

```bash
ai-automation-kit flows install invoice-document-followup --output .tmp/flow-project
ai-automation-kit flows run .tmp/flow-project
```

開くもの:

1. `.tmp/flow-project/workflow_map.mmd`
2. `.tmp/flow-project/automation_output/work_queue.csv`
3. `.tmp/flow-project/automation_output/draft_outputs.md`
4. `.tmp/flow-project/automation_output/approval_queue.csv`
5. `.tmp/flow-project/automation_output/status_report.md`

### ホームページ案件ルート

ホームページ制作と、問い合わせ・予約の簡単な運用をセットで作りたい場合はこのルートです。

```bash
ai-automation-kit website-side-hustle \
  --industry hospitality \
  --client-type local-business \
  --niche tourism-hotel \
  --output .tmp/website-side-hustle
```

開くもの:

1. `.tmp/website-side-hustle/START_HERE_WEBSITE_SIDE_HUSTLE.md`
2. `.tmp/website-side-hustle/client_kickoff_questions.md`
3. `.tmp/website-side-hustle/designer_grade_agent_playbook.md`
4. `.tmp/website-side-hustle/website_quality_gate.md`
5. `.tmp/website-side-hustle/delivery_acceptance_checklist.md`

競合サイトを丸ごとコピーしてはいけません。公開情報は、構成や考え方を学ぶために使い、ブランド、文章、画像、全体レイアウトをそのまま使わないでください。

### クラウド・APIルート

クラウドやAPIへ進むのは、業務フローが決まった後です。

```bash
ai-automation-kit guided-setup \
  --flow-id invoice-document-followup \
  --mode beginner \
  --deployment undecided \
  --connectors gmail,google-sheets \
  --output .tmp/guided-setup
```

確認するもの:

1. `.tmp/guided-setup/START_HERE_GUIDED_SETUP.md`
2. `.tmp/guided-setup/missing_inputs.md`
3. `.tmp/guided-setup/env_values_needed.md`
4. `.tmp/guided-setup/client_request_list.md`
5. `.tmp/guided-setup/ai_agent_instruction.md`

クラウドが必要なら、計画を作ります。

```bash
ai-automation-kit cloud-plan \
  --flow-id invoice-document-followup \
  --provider aws \
  --workload scheduled-job \
  --connectors gmail,google-sheets,storage-folder \
  --output .tmp/cloud-plan
```

cloud-plan は、本番公開を自動で進めるコマンドではありません。アカウント、権限、費用、secret、rollback、人間承認を整理するためのチェックリストです。

## command-center の位置づけ

機能が増えて迷ったら、`command-center` を使います。

```bash
ai-automation-kit command-center --language both --output .tmp/command-center
```

開くもの:

- `.tmp/command-center/START_HERE_COMMAND_CENTER.md`
- `.tmp/command-center/command_center.html`
- `.tmp/command-center/next_step_decision_tree.md`

これは、`skill-pack`、`approval-gate`、`mcp-connector-plan`、`workflow-explainer`、`eval-loop`、`governance-pack` などの拡張パックを選ぶためのメニューです。

## 人間承認ルール

AIに任せてよいこと:

- 下書き
- 分類
- 要約
- 整理
- 説明
- チェックリスト作成

人間承認が必要なこと:

- 実在顧客への送信
- 予約確定
- 価格変更
- 返金
- 本番データ変更
- 課金が発生するクラウド有効化
- 公開Webhook作成
- 実在顧客の個人情報利用
- 法律、医療、金融、人事、安全に関わる判断

## 初心者チェックリスト

顧客に見せる前に、これを確認します。

- 業務は1つに絞れている。
- 入力元が分かっている。
- 出力は自動実行ではなく下書きになっている。
- 人間の承認者が決まっている。
- サンプルデータ、または匿名化データを使える。
- dry-run の結果をやさしい言葉で説明できる。
- 顧客に「まだ本番システムではない」と伝えられる。
- 次の判断が「続ける、直す、止める」のどれかに分かれている。

## このページの目的

このプロジェクトの価値は、「AIで何か自動化できそう」という曖昧な状態から、「この小さな業務を、この安全な見本で、この入力を使い、このAI下書きを作り、この人が承認する」という状態に進めることです。

