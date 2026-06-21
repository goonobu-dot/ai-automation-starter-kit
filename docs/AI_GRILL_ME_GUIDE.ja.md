# AI Grill Me ガイド

このガイドは、AI初心者が「AIに何を相談すればよいか分からない」状態から抜けるためのものです。

grill-me 的な進め方とは、AIに答えを丸投げすることではありません。AIに **1問ずつ** 質問してもらい、曖昧な答えをその場で突っ込んでもらい、足りない情報を埋めながら安全な業務自動化提案に近づける進め方です。

## なぜ必要か

AIに慣れている人は「分からなければAIに聞けばいい」と考えます。しかし初心者は、何を聞けばよいか、何を貼ってよいか、AIの答えをどこまで信じてよいかが分かりません。

このプロジェクトでは、そこを補うために `grill-me` を使います。

CLIを実行しなくても使えます。[AIエージェント Grill Me スキル](AI_AGENT_GRILL_ME_SKILL.ja.md) を開き、その文章を ChatGPT、Claude、Gemini、Cursor、Codex、Claude Code などに貼って、1問ずつ聞き出してもらってください。下のコマンドは、同じ内容をローカルファイルとして生成したい人のための補助手段です。

```bash
ai-automation-kit grill-me \
  --flow-id invoice-document-followup \
  --mode beginner \
  --client-type local-business \
  --deployment cloud \
  --connectors gmail,google-sheets \
  --output .tmp/grill-me
```

生成されるもの:

- `START_HERE_GRILL_ME.md`
- `questions_to_answer.md`
- `client_interview_grill.md`
- `cloud_readiness_grill.md`
- `risk_grill.md`
- `proposal_grill.md`
- `ai_agent_prompt.md`
- `grill_me.json`

## 基本ルール

- AIには1問ずつ質問してもらう。
- 長い説明を先にもらわない。
- 曖昧な答えはそのまま進めない。
- 本物のAPIキーやsecretを貼らない。
- 顧客の機密情報をそのまま貼らない。
- 本番送信、本番webhook、scheduler、queue、cloud traffic は人間承認まで止める。
- 「完全自動化」「売上保証」「24時間無人運用」を前提にしない。

## AIに最初に貼る文章

```text
私はAI初心者です。
この ai-automation-starter-kit を使って、企業向けの小さな業務自動化PoCを提案したいです。

あなたは私に1問ずつ質問してください。
長い説明を先に出さず、私の答えが曖昧なら突っ込んでください。

本物のAPIキーやsecretを貼らせないでください。
本番送信、本番webhook、scheduler、queue、cloud traffic は人間の承認があるまで進めないでください。

まず、どの業務を自動化するのがよいか確認する質問から始めてください。
```

## AIに見せてよいもの

- README のリンク。
- docs のリンク。
- エラー全文。ただし secret は消す。
- ファイル名。
- 使いたい業務フロー名。
- 顧客の業種。
- サンプルデータの形式。
- 画面やコマンドの出力。ただし個人情報とsecretは消す。

## AIに見せてはいけないもの

- 本物のAPIキー。
- password。
- OAuth token。
- private key。
- 顧客の個人情報。
- 医療、法律、金融などの機密判断データ。
- 本番環境の管理者権限。

## よいAIの使い方

悪い例:

```text
全部自動化して。
```

よい例:

```text
この業務が自動化に向いているか、1問ずつ確認してください。
顧客に聞くべき質問、用意するサンプルデータ、人間の承認点を分けてください。
```

悪い例:

```text
AWSで動かす方法を全部教えて。
```

よい例:

```text
cloud-plan の出力を読んで、次に確認すべきことを1つずつ質問してください。
課金、secret、IAM、log、rollback、人間承認を分けて確認してください。
```

## 初心者が止まりやすい場面

1. どの業務を選べばよいか分からない。
2. 顧客に何を聞けばよいか分からない。
3. APIキーやsecretの扱いが分からない。
4. cloud provider の画面で何を選べばよいか分からない。
5. エラーが出た時に何をAIへ見せればよいか分からない。
6. 提案してよい範囲と危ない範囲の区別がつかない。

`grill-me` は、この止まり方を減らすためにあります。

## 目指す状態

AI初心者が、次のことを自分の言葉で説明できる状態を目指します。

- どの業務を自動化するか。
- なぜその業務がPoC向きか。
- 何を入力にするか。
- 何を出力にするか。
- 誰が承認するか。
- 何は自動化しないか。
- クラウド化する前に何を確認するか。
- 顧客にどう説明するか。

ここまで整理できれば、初心者でも安全に一歩進めます。
