# 顧客導入サポート運用手順書

この手順書は、初心者がAIの補助を使って、顧客向け業務自動化案件を営業前、ヒアリング中、デモ後、導入中、運用中にどう進めるかをまとめたものです。目的は、できることを誇張せず、売れる形に整えることです。

## 運用方針

AIは準備、質問、下書き、確認、文書化を支援します。人間は顧客事実、アカウント、secret、本番変更、法的境界、お金を承認します。

収益保証しない。完全自動化や無人運用を約束しない。提案は、範囲を絞った有料dry-run PoCにします。

## 営業前

AIエージェントに準備させるもの:

- 業界ごとの課題仮説を1つ
- 推奨業務フローを1つ
- before/after説明
- 顧客への短い質問リスト
- 架空の入力例
- 架空の出力例
- 人間承認に残す点
- 含めない範囲
- 有料dry-run PoCで検証できること

最低限の準備:

- カタログから業務フローを1つ選ぶ
- 入力元の見当をつける
- 出力の見当をつける
- 顧客の言葉で説明できるようにする
- stop conditionを用意する

## ヒアリング中

AIが作った質問リストを使います。ただし、質問するのは人間です。

確認すること:

- 現在の手作業
- 頻度と件数
- 現在使っているツール
- 担当者と承認者
- 入力例
- 出力例
- 顧客側の制限
- データの機密性
- dry-runで試せる範囲
- 成功指標

営業中に本物のAPIキーを求めないでください。聞くのは、誰がそのシステムを管理しているか、有料PoCが始まったらアクセスを用意できるかです。

## 初回デモ後

AIにメモを整理させます。

- 顧客課題の要約
- 提案する業務フロー
- 必要なサンプルデータ
- connector/account request list
- approval queue design
- dry-run test plan
- risks and exclusions
- paid PoC scope
- follow-up email

初回デモは、架空または伏せ字データを使います。work queue、draft output、approval queue、reportを見せます。本物の顧客メッセージは送信しません。

## 導入支援

PoCが始まったら、AIは運用者を支援できます。

- project checklist作成
- sample data columns確認
- `.env.example` の下書き
- APIキーを作る場所の説明
- folder naming rules作成
- test cases作成
- rollback notes作成
- secretを消したerror確認
- client status report作成

人間が必ず行うこと:

- accounts作成
- billing承認
- API keys作成
- secretの安全な保存
- read/write permissions承認
- dry-run実行または承認
- production traffic承認

## go-liveゲート

次が揃うまで本番化しません。

- dry-run outputを確認済み
- human approverが明確
- rollback ownerが明確
- loggingが見える
- error handlingを説明できる
- secret storageがチャット外
- production sendingを意図して有効化している
- 顧客がscopeを承認している
- 危険ケースにmanual fallbackがある

1つでも不足していれば、dry-runのままにします。

## 月次運用

継続支援では、AIに次を作らせます。

- monthly automation report
- failed item summary
- approval queue summary
- time saved estimate
- missed input list
- new workflow candidates
- risk review
- client follow-up email

運用者は、送信前に必ず確認します。

## 顧客向けの約束

使ってよい約束:

> 1つの業務フローを安全なdry-runで検証します。重要な出力は人間が承認しながら、AIで手作業の準備時間を減らせるか確認します。

避ける約束:

- 「御社を完全自動化します」
- 「収益を保証します」
- 「人間の確認は不要です」
- 「AIがcloudやAPI設定を全部自動で管理できます」

## AIに貼る導入支援依頼文

```text
顧客導入サポート運用手順書を読んでください。
この顧客向け業務自動化案件を1ステップずつ準備してください。
営業前、ヒアリング中、初回デモ後、導入支援、go-liveゲート、月次運用に分けてください。
収益保証や完全自動化は約束しないでください。
本物のsecretはチャットで求めないでください。
```
