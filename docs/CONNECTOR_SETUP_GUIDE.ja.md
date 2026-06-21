# 連携設定ガイド

このガイドは、`cloud-plan` や `guided-setup` で指定する connector の考え方を説明します。connector とは、業務自動化が接続する入力元、出力先、通知先、保存先のことです。

初心者がつまずきやすい点は、クラウド本体よりも「どのAPIキーが必要か」「どのフォルダを見ればいいか」「誰のアカウントで許可するか」です。このガイドは、その確認を簡単にするためのものです。

## 共通ルール

- 本物の secret はチャットに書かない。
- `.env.example` には名前だけを書く。
- 本物の値はクラウドの secrets manager や provider dashboard に入れる。
- 顧客のアカウントで連携する場合、顧客が owner です。
- 連携を外す方法も最初に確認します。

## Gmail

使う場面:

- 問い合わせメールの整理。
- 返信下書き。
- 請求書フォロー。
- 顧客への通知下書き。

必要になりやすいもの:

- `GMAIL_CLIENT_ID`
- `GMAIL_CLIENT_SECRET`
- `GMAIL_REFRESH_TOKEN`
- 読み取り対象の mailbox や label。
- 送信を許可するか、下書きだけにするか。

初心者向け判断:
最初は送信しないで、下書き作成またはローカル outbox にしてください。

## Google Sheets

使う場面:

- 入力データの一覧。
- 作業キュー。
- KPIレポート。
- 顧客リスト整理。

必要になりやすいもの:

- `GOOGLE_SHEETS_SPREADSHEET_ID`
- `GOOGLE_SERVICE_ACCOUNT_JSON`
- 読み取り対象 sheet 名。
- 書き込み先 sheet 名。

初心者向け判断:
最初はコピーしたテスト用 spreadsheet を使ってください。本番 spreadsheet へ直接書き込むのは、承認後にしてください。

## Slack

使う場面:

- 社内通知。
- 承認依頼。
- エスカレーション。

必要になりやすいもの:

- `SLACK_BOT_TOKEN`
- `SLACK_SIGNING_SECRET`
- 通知先 channel。
- 投稿してよい文面ルール。

初心者向け判断:
最初はテスト channel へ投稿してください。本番 channel へ通知する前に、文面と頻度を承認してください。

## LINE

使う場面:

- 店舗や教室の問い合わせ受付。
- 予約前確認。
- 顧客への返信下書き。

必要になりやすいもの:

- `LINE_CHANNEL_SECRET`
- `LINE_CHANNEL_ACCESS_TOKEN`
- Webhook URL。
- LINE Developers の channel。

初心者向け判断:
LINE は便利ですが、本番顧客に直接返信する前に approval queue を必ず残してください。LINE は一つの事例であり、このプロジェクトは cloud 全般を支援します。

## CRM

使う場面:

- lead cleanup。
- 顧客情報の更新。
- 商談メモ。
- フォローアップタスク。

必要になりやすいもの:

- `CRM_BASE_URL`
- `CRM_API_TOKEN`
- 更新してよい項目。
- 更新禁止項目。

初心者向け判断:
最初はCRMへ直接書き込まず、更新案をCSVや承認キューに出してください。

## storage-folder / local-folder

使う場面:

- CSV受け取り。
- 受付先フォルダ。
- 出力先フォルダ。
- 顧客からもらったファイルの一時置き場。

必要になりやすいもの:

- `INPUT_FOLDER_PATH`
- `OUTPUT_FOLDER_PATH`
- ファイル名ルール。
- 処理済みファイルの移動先。

初心者向け判断:
最初はローカルフォルダで十分です。クラウドフォルダへ進めるのは、dry-run の価値が見えた後で問題ありません。

## 顧客に聞く質問

- どのデータを入力にしますか。
- そのデータの owner は誰ですか。
- AIが読んでよい範囲はどこまでですか。
- AIが書き込んでよい場所はありますか。
- 送信、投稿、更新は自動でよいですか。それとも承認後ですか。
- 失敗した場合、誰が止めますか。

この質問に答えられれば、AI初心者でも connector 設定の会話を進めやすくなります。

