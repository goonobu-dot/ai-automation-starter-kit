# AI Automation Starter Kit やさしい解説

このページは、AI Automation Starter Kit を中学生でも分かるように説明するページです。

## このプロジェクトは何か

AI Automation Starter Kit は、GitHub に公開されている便利なプログラムを調べて、仕事の自動化に使えそうなものを見つけるためのツールです。

GitHub には、世界中の人が作った公開プロジェクトがたくさんあります。中には、次のような仕事に役立つものがあります。

- お問い合わせ対応を助けるもの
- 書類を整理するもの
- 表計算ファイルを社内アプリに変えるもの
- 同じ作業を自動で進めるもの
- AIエージェントを動かすもの

このプロジェクトは、そうした公開プロジェクトを調べて、次のようなことを整理します。

- どのプロジェクトが役立ちそうか
- すぐ試してよいか
- どんなリスクを確認すべきか
- 小さく試すなら何から始めるか
- 自動化で本当に効果が出たかどう測るか

## 何のために作ったのか

普通のAIチャットは、質問すると答えを返してくれます。これは便利です。

でも、会社やチームで自動化を進めるには、会話だけでは足りないことがあります。

たとえば、次のような情報が必要になります。

- 何を見つけたのか
- 最初に何を読むべきか
- 試してよい状態なのか
- 誰が承認するのか
- どんなリスクが残っているのか
- 何を測れば効果が分かるのか
- どうやって安全に試すのか

このプロジェクトは、AIや自動化のアイデアを、あとから見直せるファイルに変えるために作られています。

## 何ができるのか

最初に使うなら `onboard` が一番簡単です。

このコマンドは、環境チェック、GitHub検索、判断用ファイルの作成、次に読むファイルの案内までまとめて実行します。

細かく調査だけ実行したい場合の中心コマンドは `github-discover` です。

このコマンドは、業務領域に合わせて GitHub から自動化候補を探します。

たとえば、次のような領域を指定できます。

- operations
- support
- finance
- sales
- marketing
- hr

実行すると、結果フォルダの中に判断用のファイルが作られます。

主なファイルは次のとおりです。

| ファイル | 簡単な意味 |
|---|---|
| `run_summary.md` | 今回の調査結果と、次に読むべきファイルのまとめです。 |
| `executive_decision_brief.md` | 試してよいか、待つべきか、再調査すべきかを判断する資料です。 |
| `pilot_scorecard.csv` | 試験導入で効果が出たか測るための表です。 |
| `value_realization_plan.md` | 自動化でどんな価値を出すかを整理する計画書です。 |
| `risk_exception_register.md` | 本番利用の前に解決すべきリスク一覧です。 |
| `operational_audit_plan.md` | あとで確認すべき証拠や監査項目の計画です。 |
| `adapter_starter/` | 安全に試すための dry-run 用サンプルコードです。 |
| `offer_pack/` | 小さな顧客向け提案に使う提案書、サービスメニュー、価格設計、営業文、安全境界です。 |
| `beginner-sales/` | フロー一覧、選択したフローの見えるデモ、営業トーク、質問リスト、ROI計算、提案書、3日PoC計画です。 |

## どうやって使うのか

まず、プロジェクトをダウンロードします。

```bash
git clone https://github.com/goonobu-dot/ai-automation-starter-kit.git
cd ai-automation-starter-kit
```

次に、Python の実行環境を作ります。

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m ensurepip --upgrade
python3 -m pip install --upgrade pip setuptools
python3 -m pip install -e .
```

最初の流れをまとめて実行します。

```bash
ai-automation-kit onboard --business-area operations --limit 2 --output .tmp/onboarding --create-offer-pack
```

まず要約を読みます。

```bash
sed -n '1,180p' .tmp/onboarding/onboarding_summary.md
```

実行後は、次の順番で読むと分かりやすいです。

1. `.tmp/onboarding/run_summary.md`
2. `.tmp/onboarding/executive_decision_brief.md`
3. `.tmp/onboarding/pilot_scorecard.csv`
4. `.tmp/onboarding/artifact_index.md`
5. 副業・受託の小さな提案に変える場合は `.tmp/onboarding/offer_pack/README.md`

offer-pack は提案書や納品範囲を作るための補助資料です。収益を保証するものではありません。

AIエージェントを使い始めた人が、ひとつの業務自動化を企業へ説明したい場合は、次のコマンドを使います。

```bash
ai-automation-kit beginner-sales --flow-id invoice-document-followup --client-type local-business --niche accounting --output .tmp/beginner-sales
```

実行後は、次の順番で見ると分かりやすいです。

1. `.tmp/beginner-sales/flow_gallery.html`
2. `.tmp/beginner-sales/selected_flow_demo.html`
3. `.tmp/beginner-sales/client_questions.md`
4. `.tmp/beginner-sales/roi_simple_calculator.csv`
5. `.tmp/beginner-sales/proposal_one_pager.md`

これにより、「この自動化で何ができるのか」を見せながら説明し、いきなり本番導入ではなく、小さな dry-run PoC として提案できます。

## 普通のAIチャットと何が違うのか

普通のAIチャットは、その場で答えを返してくれます。

AI Automation Starter Kit は、あとから見直せる仕事の流れを作ります。

普通のAIチャット:

- すぐ考えるには便利
- 結果が会話の中に残りやすい
- チームで後から確認しにくい
- 承認、リスク、効果測定があいまいになりやすい

AI Automation Starter Kit:

- 結果をファイルとして保存する
- 実行履歴を残す
- 判断資料を作る
- リスクや監査の資料を作る
- 効果測定の表を作る
- dry-run で安全に試せる
- 同じ手順を何度も再現しやすい

## どんな人に役立つか

このプロジェクトは、次のような人に役立ちます。

- AI自動化を学びたい開発者
- AIエージェントを作っている人
- 業務自動化を提案する人
- 会社の業務改善を考える人
- GitHub の公開プロジェクトから学びたい人

## たとえ話

GitHub は、世界中の人が作ったレシピが集まっている大きな図書館のようなものです。

このプロジェクトは、ただ「このレシピは面白そう」と言うだけではありません。

次のことを一緒に確認します。

- どのレシピを試す価値があるか
- 危ない材料はないか
- 誰が試すことを承認するか
- 結果がよかったかどう測るか
- 本番で使う前に安全に練習できるか

つまり、このプロジェクトの目的は、面白そうなOSSのアイデアを、実際に試せる業務自動化の計画に変えることです。
