# はじめかた（30分で最初のデモまで）

このページが、このプロジェクトの唯一の入口です。ほかのドキュメントは、まだ開かなくて大丈夫です。

読者として想定しているのは、「AIエージェント（ChatGPTやClaudeのように、指示を受けて作業を進めてくれるAIのこと）を触り始めたばかりで、副業として中小企業に業務自動化を提案してみたい」という方です。

このページのゴールは1つだけです。**30分で、お客様に見せられるデモ一式を自分のパソコンの中に作ること。** プログラミングの知識は不要です。コマンドはすべてコピペで動きます。

## このキットは何をするものか

AI Automation Starter Kit は、業務自動化の提案に必要な資料（デモ画面・ヒアリングシート・提案書・価格表など）を、コマンド1つでまとめて生成するツールです。

大事な安全設計が1つあります。**このキットは外部に何も送信しません。** メール送信や本番システムの更新は行わず、すべて「下書き」と「承認待ちリスト」としてファイルに出力されます（これを dry-run＝ドライラン、本番実行しないお試し実行と呼びます）。だから初心者が試しても、お客様に迷惑をかける事故が起きません。

## 事前に必要なもの

- パソコン（Mac / Windows / Linux）
- Python 3.10以上（Pythonとは、このツールを動かすためのプログラミング言語です。[python.org](https://www.python.org/downloads/) から無料で入れられます）
- ターミナル（Macなら「ターミナル.app」、Windowsなら「PowerShell」。文字でパソコンに指示を出す画面のことです）

確認方法（ターミナルに貼り付けてEnter）:

```bash
python3 --version
```

`Python 3.10` 以上の数字が出ればOKです。

## ステップ1: インストール（約5分）

まず、このプロジェクトをパソコンに取り込み、専用の作業環境を作ります。1行ずつ、または全部まとめて貼り付けて実行してください。

```bash
git clone https://github.com/goonobu-dot/ai-automation-starter-kit.git
cd ai-automation-starter-kit
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip setuptools
python3 -m pip install -e .
```

- `git clone` は、プロジェクト一式をダウンロードするコマンドです（gitが無い場合はGitHubページの「Code → Download ZIP」でも構いません）。
- `venv` は、パソコンの他の環境を汚さないための「仮想環境（このプロジェクト専用の作業部屋）」です。
- Windows (PowerShell) の場合、4行目は `.venv\Scripts\Activate.ps1` に読み替えてください。

インストールできたか確認します:

```bash
ai-automation-kit --version
ai-automation-kit doctor --output .tmp/doctor
```

`doctor` は健康診断コマンドです。Pythonのバージョンや書き込み権限などを確認し、問題があれば日本語の対処法を表示します。

## ステップ2: 初心者ナビを起動する（約3分）

次のコマンドで、日本語の「初心者ナビ」が起動します。今のあなたの段階（環境準備 → 最初のデモ → 営業準備 → 最初の案件 → 納品と請求）を選ぶと、次にやることを具体的に教えてくれます。

```bash
ai-automation-kit beginner
```

段階を直接指定することもできます:

```bash
ai-automation-kit beginner --step 2
```

迷子になったら、いつでもこのコマンドに戻ってきてください。このナビがこのキットの案内役です。

## ステップ3: デモ一式を生成する（約10分）

中小企業への提案で一番使いやすい例として、「請求書と書類の追跡（未提出の書類を見つけて確認リストと催促文の下書きを作る業務）」のデモ一式を生成します。

```bash
ai-automation-kit complete-workspace --flow-id invoice-document-followup --client-type local-business --niche accounting --output .tmp/complete-accounting
```

30秒ほどで、`.tmp/complete-accounting/` フォルダに商談用の資料一式ができます。まず次の2つだけ開いてください。

```bash
open .tmp/complete-accounting/client_command_center.html
open .tmp/complete-accounting/FINAL_DELIVERY_GUIDE.md
```

（Windowsは `open` を `start` に、Linuxは `xdg-open` に読み替えてください。コマンドが難しければ、Finderやエクスプローラーで `.tmp/complete-accounting` フォルダを開き、ファイルをダブルクリックしても同じです）

- `client_command_center.html` — ブラウザで開ける「生成物の案内板」。お客様に見せるデモ画面もここから辿れます。
- `FINAL_DELIVERY_GUIDE.md` — 生成物をどの順で使うかの1枚ガイドです。

営業用の資料（ヒアリングシート・提案書・価格表）を作りたいときは、こちらも実行してみてください:

```bash
ai-automation-kit beginner-sales --flow-id invoice-document-followup --client-type local-business --niche accounting --output .tmp/beginner-sales
```

`.tmp/beginner-sales/` に、そのまま商談で読み上げられるヒアリング質問（`client_questions.md`）、1枚提案書（`proposal_one_pager.md`）、価格の決め方つき料金メニュー（`price_menu.md`）などが生成されます。

## ステップ4: 次に読むもの

ここまでで「デモを見せられる状態」になりました。実際の商談（お客様探し → ヒアリング → 提案 → 受注 → 納品 → 請求）の進め方は、次のチュートリアルに全工程をまとめています。

- **[中小企業への自動化提案チュートリアル](TUTORIAL_SME_PROPOSAL.ja.md)** — 営業から請求までのエンドツーエンド実践ガイド（次はこれだけ読めば大丈夫です）

その先で必要になったときに開くもの:

- [ドキュメント索引（INDEX）](INDEX.md) — 全ドキュメントのカテゴリ別一覧。**最初は🔰入門カテゴリ以外は読まないでください。**
- [使い方マニュアル](USER_MANUAL.ja.md) — 全コマンドの操作説明書
- [FAQ](FAQ.ja.md) — よくある質問

## 困ったときは

- コマンドがエラーになる → `ai-automation-kit doctor --output .tmp/doctor` を実行し、表示される日本語の対処法に従ってください。
- 何をすればいいか分からなくなった → `ai-automation-kit beginner` に戻ってください。
- それでも解決しない → [FAQ](FAQ.ja.md) を確認するか、GitHubのIssueで質問してください。

## 安全に関する約束

このキットの生成物は「下書き」です。お客様への送信・本番システムの変更は、必ず人間が内容を確認してから、人間の手で行ってください。また、APIキーやパスワードなどの秘密情報は、チャットにも生成ファイルにも書かないでください。収益を保証するものではありませんが、最初の1件を安全に進めるための道具は揃っています。
