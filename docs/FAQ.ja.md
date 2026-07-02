# FAQ

## これは本当に自動化システムですか？

はい。ただし初期状態では安全な dry-run です。ローカルでキュー、下書き、承認リスト、レポート、ローカル outbox を作ります。外部送信や本番更新は勝手にしません。

## 普通にAIチャットへ頼むのと何が違いますか？

AIチャットは会話で終わりやすいです。このプロジェクトは、フロー、提案書、ROI表、実行ログ、承認リスト、顧客レポートをファイルとして残します。

## 副業で使えますか？

使える形を目指しています。ただし収益保証ではありません。企業の繰り返し業務を見つけ、小さな dry-run PoC として提案するための道具です。

## AIに慣れていない人でも企業へ提案できますか？

提案しやすくするために `business-launch` を用意しています。狙う業種、最初の商品、ヒアリング台本、提案書、価格表、リスク境界、30日行動計画、営業メールをまとめて作ります。

```bash
ai-automation-kit business-launch --industry finance --client-type local-business --niche accounting --output .tmp/business-launch
```

最初は本番自動化ではなく、サンプルデータを使った有料の dry-run PoC として提案します。

## 最初に何を実行すればいいですか？

```bash
ai-automation-kit complete-workspace --flow-id invoice-document-followup --output .tmp/complete
```

`FINAL_DELIVERY_GUIDE.md`、`completion_checklist.md`、顧客レポート、デモサイト、共有用 zip、収益化評価、営業クロージング台本、有償PoC範囲、価値測定シート、契約前チェック、提案メール、30日運用計画、成果証明テンプレート、公開OSSパターン比較、統合バックログ、導入方式、運用監視計画、案件化スコア、顧客オンボーディング、本番移行判断、ブラウザ用コマンドセンター、`business_launch/` の事業化提案パックまで作られます。

## 初心者はどのマニュアルから読めばいいですか？

まず [はじめかた](GETTING_STARTED.ja.md) を読み、次に [使い方マニュアル](USER_MANUAL.ja.md) を読みます。副業や受託として最初の1件を進めたい場合は [最初の顧客案件ウォークスルー](FIRST_CLIENT_WALKTHROUGH.ja.md) を読んでください。

クラウド、APIキー、受付フォルダ、承認者で不安がある場合は [AI初心者サポートマップ](archive/AI_BEGINNER_SUPPORT_MAP.ja.md) をAIエージェントに読ませて、1問ずつ質問してもらうのがおすすめです。

## 企業に何を見せればいいですか？

まず `demo_site/index.html` と `beginner_sales/selected_flow_demo.html` を見せます。そのあと `client_questions.md` でヒアリングし、`proposal_one_pager.md` で小さなPoCを提案します。

## 何を売り込めばいいか分からない場合は？

`opportunity-catalog` で営業用カタログを作り、`recommend-flow` で顧客の困りごとからおすすめフローを選びます。共有前は `share-check` で秘密情報らしい文字列が混ざっていないか確認します。

## 本番接続はできますか？

設計上は進められますが、初期状態では無効です。`connector-doctor` で不足設定を確認し、`client_onboarding_form.md`、`deployment_options.md`、`production_observability_plan.md`、`go_live_decision.md` で self-host、Webhook、MCP、リトライ、キュー、承認監査、停止手順、承認者、本番移行可否を決めてから進めます。
