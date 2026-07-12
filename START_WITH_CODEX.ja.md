このリポジトリの AGENTS.md を読み、月報自動化の作業場所を作ってください。
質問は1回に1つだけ行い、保存場所、作業名、承認者、最初の対象月を確認してください。
作成後、過去の完成月報、過去の参考資料、今月資料を入れる場所を開いて説明してください。

# Codexではじめる

問い合わせ、営業、日次収支など10種類の日次業務は、[初心者向けHTMLガイド](docs/daily-workflows.ja.html)から選べます。英語版は[こちら](docs/daily-workflows.html)です。

メール送信なしの作業負担軽減5パックは、[日本語手順書](docs/work-relief-workflows.ja.html)と[英語版](docs/work-relief-workflows.html)から見られます。Gmail とメール自動化はその対象外で、別プロジェクトとして扱います。

このファイルは、月報作業場所を Codex にローカルで整えてもらうための、初心者向けの実務メモです。宣伝ではなく、実際に何を確認して何を実行するかだけを書いています。

## 最初に Codex へ送る内容

上の3行を、そのまま最初の依頼文として使ってください。これで Codex は次の順番で進めるべきだと分かります。

1. まず `AGENTS.md` を読む
2. 質問は1回に1つだけ行う
3. 正式な CLI コマンドで作業場所を作る
4. 作成後に3種類のフォルダを開いて意味を説明する

## Codex が最初に行う確認

最初に確認するコマンドはこれです。

```bash
codex login status
```

ログインが未完了なら、Codex はそこで止まり、人間が次に何をするかを説明します。APIキー、token、secret、password をチャットで要求してはいけません。この流れはローカルの Codex ログインを前提にしており、資格情報を貼り付けて進める方式ではありません。

## 作業場所を作るコマンド

保存場所、作業名、承認者、対象月の4点が決まったら、Codex は次の形式で実行します。

```bash
ai-automation-kit office-workspace create --root "<保存先ルート>" --name "<作業名>" --approver "<承認者名>" --pin "<6〜32桁の数字PIN>" --period "<YYYY-MM>" --language ja
```

作成直後にローカルUIを開くのではなく、先に状態確認を行います。

```bash
ai-automation-kit office-workspace status --workspace "<作業場所パス>" --json
```

今月資料を置いた後に、初回の確認を行うコマンドはこれです。

```bash
ai-automation-kit office-workspace inspect --workspace "<作業場所パス>" --period "<YYYY-MM>"
```

状態確認が通ってから、はじめてローカルUIを開きます。

```bash
ai-automation-kit office-workspace serve --root "<保存先ルート>" --language ja
```

## Codex が開いて説明する3種類のフォルダ

作成後、Codex は次の3種類の置き場を開いて、やさしい言葉で説明してください。

1. `01_APPROVED_PAST_OUTPUTS`
   以前の完成済み月報を入れる場所です。文体や構成の見本になります。
2. `02_PAST_SUPPORTING_FILES`
   以前の参考資料を入れる場所です。補助の表、メモ、前回の元データなどを置きます。
3. `03_CURRENT_INPUTS/<YYYY-MM>`
   今月の資料を入れる場所です。今回の月報で使うファイルはここに集めます。

あわせて、`05_DRAFTS` は下書き、`06_APPROVED_OUTPUTS` はローカル承認後の完成版、`07_AUDIT` は承認記録だと説明してください。外部送信はしないことも、はっきり伝える必要があります。

## このセットアップの安全ルール

- APIキーを要求しない
- 外部送信しない
- ローカルUIを開く前に検証する
- approval bypass や sandbox bypass の指定を求めない
- 独自の shell コマンドや外部送信オプションを追加しない
- メール、Slack、外部サービスへ勝手に送らない
- ローカルUIを開く前に検証する
- 会話は人間向けに、1回に1つの質問で進める

## 対応OSの事実

Phase 1A の安全な作業場所作成と承認更新は macOS または Linux 専用です。Windows ではこの方式に必要な安全なローカル更新機能がないため、Codex は無理に進めず、その事実を先に説明してください。読むだけの資料確認はできますが、作成・更新の本流は macOS または Linux 前提です。

## 手動復旧が必要なときの正直な扱い

状態ファイルの不整合、取り残された lock、途中で止まった run などがある場合、Codex は「手動復旧が必要です」と正直に伝えてください。直っていないのに直ったふりをしてはいけません。確認場所はローカルにあります。

- `00_START_HERE/workspace_status.json`
- `.system/workspace.json`
- `.system/periods/<YYYY-MM>/state.json`
- `.system/runs/`
- `07_AUDIT/audit.jsonl`

それでも判断できない場合は、Codex は勝手に進めず、分かっている事実を短く整理し、次にどれを確認するかを1つだけ質問してください。
