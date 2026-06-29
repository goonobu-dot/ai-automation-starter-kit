# AI Automation Starter Kit 使い方マニュアル

このマニュアルは、AIやクラウドにまだ慣れていない人が、企業の業務自動化を安全に提案し、最初の dry-run まで進めるための手順書です。

最初から全部を理解する必要はありません。まずは「1つの業務」「1つの入力」「1つの出力」「1人の承認者」に絞ります。

このプロジェクトが目指すのは、あいまいなAI自動化の話を、見えるフロー、必要な入力、提案資料、実行結果、承認ポイントつきの小さな案件に変えることです。収益や受注を保証するものではありませんが、企業へ説明しやすい形に整えるための道具として使えます。

## 最初に安心してほしいこと

このプロジェクトは、いきなり本番送信や本番データ更新をするものではありません。

最初は dry-run です。dry-run とは、実際の送信、投稿、顧客データ更新をせずに、下書き、作業キュー、承認リスト、レポートだけを作る安全な試し方です。

最初からチャットに貼らないもの:

- 本物のAPIキー
- password
- 顧客の個人情報
- 本番のWebhook URL
- クラウドの管理者権限
- 顧客の機密資料

AIに相談してよいもの:

- どの業務を自動化候補にするか
- 顧客に何を聞くか
- どの資料を見ればよいか
- サンプルデータの形
- dry-run の進め方
- クラウドに進む前の確認事項
- 提案文や説明文の下書き

## 5分で分かる全体像

1. 企業の困りごとを1つ選びます。
2. このプロジェクトで近い業務フローを選びます。
3. ローカルPCで見本フォルダを作ります。
4. サンプルデータで dry-run します。
5. 下書き、作業キュー、承認リスト、レポートを確認します。
6. 顧客に「本番ではなく見本」として説明します。
7. 価値がありそうなら、必要なAPI、フォルダ、クラウド、承認者を整理します。
8. 有料PoCにする場合は、範囲、期間、費用、停止条件を明確にします。

初心者が最初に目指すゴールは「全部自動化」ではありません。顧客が見て分かる形で、手作業がどう減るかを説明できる状態です。

## 最初に読む3つの資料

迷ったら、まずこの順番で読んでください。

1. [初心者ルートマップ](BEGINNER_ROUTE_MAP.ja.md)
2. [まずここから](START_HERE.ja.md)
3. [AI初心者サポートマップ](AI_BEGINNER_SUPPORT_MAP.ja.md)
4. [初心者向けクラウド挑戦プレイブック](CLOUD_BEGINNER_PLAYBOOK.ja.md)

ルートマップは、このプロジェクトの機能が増えたことで初心者が迷わないようにするための入口です。最初に開くもの、最初は無視してよいもの、CLIを使わないルート、CLIを使うルート、副業・受託ルート、社内導入ルート、ホームページ案件ルート、クラウド・APIルートを整理しています。

営業や副業として使いたい場合は、次に [最初の顧客案件ウォークスルー](FIRST_CLIENT_WALKTHROUGH.ja.md) を読んでください。

クラウドやAPI設定で不安がある場合は、[クラウド導入ガイド](CLOUD_DEPLOYMENT_GUIDE.ja.md) と [連携設定ガイド](CONNECTOR_SETUP_GUIDE.ja.md) を読みます。

## まずAIに読ませる依頼文

ChatGPT、Claude、Gemini、Cursor、Codex、Claude Code などに、次の文章を貼ってください。

```text
この GitHub プロジェクト ai-automation-starter-kit を確認してください。
私はAIやクラウドにまだ慣れていません。

まず docs/BEGINNER_ROUTE_MAP.ja.md、docs/START_HERE.ja.md、docs/USER_MANUAL.ja.md、docs/AI_BEGINNER_SUPPORT_MAP.ja.md、docs/CLOUD_BEGINNER_PLAYBOOK.ja.md を読んでください。

その後、私に1問ずつ質問してください。
一度にたくさん聞かず、次の順番で確認してください。

1. どの業務を自動化したいか
2. 入力はどこから来るか
3. 出力は何にしたいか
4. 誰が確認・承認するか
5. サンプルデータを用意できるか
6. APIやクラウドが必要か
7. まずローカル dry-run で見せられるか
8. 顧客へ有料PoCとして提案できる範囲はどこか

本物のAPIキー、password、secret、顧客の機密情報はチャットに書かせないでください。
本番送信、本番更新、課金、クラウド公開の前には、必ず人間の承認を入れてください。
```

## インストール

ターミナルで次を実行します。

```bash
git clone https://github.com/goonobu-dot/ai-automation-starter-kit.git
cd ai-automation-starter-kit
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip setuptools
python3 -m pip install -e .
ai-automation-kit doctor --output .tmp/doctor
```

`doctor` は、ローカル環境が使える状態か確認するためのコマンドです。

## いちばん簡単な始め方

迷ったら、この1コマンドから始めます。

```bash
ai-automation-kit complete-workspace \
  --flow-id invoice-document-followup \
  --client-type local-business \
  --niche accounting \
  --output .tmp/complete-accounting
```

これは、請求書や不足書類のフォローを例にした見本フォルダを作ります。

最初に見るファイルはこの5つだけで十分です。

| ファイル | 何を見るためのものか |
|---|---|
| `.tmp/complete-accounting/FINAL_DELIVERY_GUIDE.md` | 全体の入口です。まずここを読みます。 |
| `.tmp/complete-accounting/client_command_center.html` | ブラウザで資料の場所を確認できます。 |
| `.tmp/complete-accounting/demo_site/index.html` | 顧客に見せる見本です。 |
| `.tmp/complete-accounting/client_report/client_report.html` | dry-run の結果を説明するレポートです。 |
| `.tmp/complete-accounting/business_launch/START_HERE_BUSINESS_LAUNCH.md` | 副業や受託提案に進む時の入口です。 |

生成されるファイルは多いですが、最初から全部読む必要はありません。まず上の5つを開けば、何ができるかをつかめます。

## 業務フローを選ぶ

企業へ提案しやすいフローを探す場合は、次を使います。

```bash
ai-automation-kit flow-guide --industry finance --niche accounting --output .tmp/flow-guide
```

`recommended_flows.md` を見て、説明しやすいフローを1つ選びます。

最初に選びやすい業務:

- 問い合わせ返信の下書き
- 請求書や不足書類のフォロー
- 予約前の確認リスト
- FAQ振り分け
- 週次レポート作成
- 顧客リスト整理
- 日報や作業報告の要約

最初は避けた方がよい業務:

- 法律、医療、金融などの重要判断
- 自動で契約、支払い、解約、値引きを行う業務
- 失敗時に取り消しが難しい本番DB更新
- 承認者が決まっていない業務
- 顧客データの取り扱いルールが不明な業務

## 顧客に見せる資料を作る

AI初心者が企業へ説明したい場合は、`beginner-sales` を使います。

```bash
ai-automation-kit beginner-sales \
  --flow-id invoice-document-followup \
  --client-type local-business \
  --niche accounting \
  --output .tmp/beginner-sales
```

見る順番:

1. `.tmp/beginner-sales/flow_gallery.html`
2. `.tmp/beginner-sales/selected_flow_demo.html`
3. `.tmp/beginner-sales/client_questions.md`
4. `.tmp/beginner-sales/roi_simple_calculator.csv`
5. `.tmp/beginner-sales/proposal_one_pager.md`
6. `.tmp/beginner-sales/three_day_poc_plan.md`

顧客には、次のように説明します。

```text
まず本番送信はしません。
サンプルデータで業務の流れを再現し、AIが下書きや作業キューを作り、人間が確認する形で見せます。
価値が見えたら、API、フォルダ、クラウド、費用、停止手順を整理して、小さなPoCとして進めるか判断します。
```

## dry-run を動かす

実際のフローをローカルで試す場合は、次を使います。

```bash
ai-automation-kit flows install invoice-document-followup --output .tmp/flow-project
ai-automation-kit flows run .tmp/flow-project
ai-automation-kit flows approve .tmp/flow-project --approver owner@example.com
```

生成される主な結果:

| ファイル | 意味 |
|---|---|
| `automation_output/work_queue.csv` | AIが作った作業候補の一覧です。 |
| `automation_output/draft_outputs.md` | 返信や処理内容の下書きです。 |
| `automation_output/approval_queue.csv` | 人間が確認するための承認リストです。 |
| `automation_output/status_report.md` | 実行結果のまとめです。 |
| `local_outbox/email_drafts.md` | 実送信しないメール下書きです。 |

ここで重要なのは「AIが勝手に送らない」ことです。まず人間が見て、修正し、承認する形にします。

## 顧客向けレポートを作る

dry-run の結果を顧客へ説明する資料に変えます。

```bash
ai-automation-kit client-report --flow-project .tmp/flow-project --output .tmp/client-report
```

`client_report.md` と `client_report.html` が作られます。

顧客に伝えること:

- 何件を処理したか
- AIが何を下書きしたか
- 人間が確認すべきものは何か
- 本番化する前に何が足りないか
- 続ける、直す、止めるのどれがよいか

## 共有前に安全確認する

顧客へ送る前に、秘密情報らしい文字列が混ざっていないか確認します。

```bash
ai-automation-kit share-check --source .tmp/complete-accounting --output .tmp/share-check
```

`share_check.md` が `blocked` の場合は、共有せずに該当箇所を消してください。

共有用のzipを作る場合:

```bash
ai-automation-kit package-client-demo --source .tmp/complete-accounting --output .tmp/client-demo-package
```

## クラウドやAPIに進む前に

クラウドは、ローカル dry-run で価値が見えた後に進めます。

まず必要情報を集めます。

```bash
ai-automation-kit guided-setup \
  --flow-id invoice-document-followup \
  --mode beginner \
  --deployment undecided \
  --connectors gmail,google-sheets \
  --output .tmp/guided-setup
```

回答内容を確認します。

```bash
ai-automation-kit guided-review \
  --answers .tmp/guided-setup/guided_setup_answers.example.json \
  --output .tmp/guided-review
```

クラウド導入資料を作ります。

```bash
ai-automation-kit cloud-plan \
  --flow-id invoice-document-followup \
  --provider aws \
  --workload scheduled-job \
  --connectors gmail,google-sheets \
  --output .tmp/cloud-plan
```

初心者向けの考え方:

- Gmail、Google Sheets、Slack、LINEなどは connector です。
- APIキーは外部サービスを使うための秘密の値です。
- 本物のsecretはチャットに貼りません。
- クラウドの課金、権限、公開URL、本番Webhookは人間が承認します。
- 最初は本番送信ではなく、下書き、テストフォルダ、テストチャンネルで進めます。

## 実行基盤へ渡す

ローカルで価値が見えた後、実行基盤へ渡すための starter を作れます。

```bash
ai-automation-kit flow-export --flow-id invoice-document-followup --target n8n --output .tmp/flow-export-n8n
ai-automation-kit deployment-pack --flow-id invoice-document-followup --provider coolify --connectors gmail,google-sheets --output .tmp/deployment-coolify
ai-automation-kit runtime-safety --flow-id invoice-document-followup --output .tmp/runtime-safety
ai-automation-kit secrets-bootstrap --flow-id invoice-document-followup --provider infisical --connectors gmail,google-sheets --output .tmp/secrets-bootstrap
ai-automation-kit document-intake --flow-id invoice-document-followup --mode advanced --output .tmp/document-intake
ai-automation-kit observability-pack --flow-id invoice-document-followup --output .tmp/observability-pack
ai-automation-kit state-backend --flow-id invoice-document-followup --backend supabase --output .tmp/state-backend
```

この段階の目的は、いきなり本番化することではありません。実行ファイル、secret の置き場所、承認ルール、履歴保管、ログ、rollback を先に揃えることです。

## 副業・受託にする時の考え方

最初に売るものは「完全自動化」ではなく、「業務自動化診断 + dry-run PoC」が向いています。

提案しやすい形:

- 3日から2週間の小さなPoC
- サンプルデータだけで実施
- 本番送信なし
- 人間承認あり
- before/after の説明あり
- 続けるか止めるかを最後に判断

売り込み前に確認すること:

- 顧客の困りごとは本当にあるか
- 月に何件くらい発生しているか
- 手作業にどれくらい時間がかかっているか
- サンプルデータを出せるか
- 承認者は誰か
- 本番化しない範囲を説明できるか
- 失敗した時に止める手順があるか

## よくある不安

「クラウドが分からない」

最初は分からなくて大丈夫です。ローカル dry-run で見せてから、`guided-setup`、`guided-review`、`cloud-plan` の順番で整理します。

「APIキーが分からない」

AIに「どのサービスの、どの値が必要か」を説明してもらいます。ただし、本物の値はチャットに貼りません。

「企業に売ってよいレベルか不安」

最初から本番導入として売らず、業務診断と dry-run PoC として提案します。成果、リスク、続ける条件を見える化してから次に進みます。

「コマンドが多すぎる」

最初は `complete-workspace`、`beginner-sales`、`guided-setup`、`cloud-plan` だけで十分です。

## 最後のチェックリスト

企業へ見せる前に確認してください。

- 本番送信していない
- 本物のsecretを共有資料に入れていない
- 顧客データは伏せ字またはサンプルである
- 何を自動化するか1文で説明できる
- 入力、出力、承認者が決まっている
- dry-run の結果を見せられる
- 顧客に聞く質問がある
- 有料PoCの範囲、期間、停止条件がある
- クラウドに進む前の不足情報が見えている

ここまでできていれば、AI初心者でも企業へ無理なく説明できます。
