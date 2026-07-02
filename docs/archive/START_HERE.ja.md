# まずここから

このページは、初めて来た人が最初の3分で AI Automation Starter Kit の役割をつかむための入口です。

全部の資料を先に読む必要はありません。リポジトリが大きく見える場合は、最初に [初心者ルートマップ](BEGINNER_ROUTE_MAP.ja.md) を開いてください。最初に開くもの、最初は無視してよいもの、CLIを使わないルート、CLIを使うルート、副業・受託ルート、社内導入ルート、ホームページ案件ルート、クラウド・APIルートを整理しています。

## これは何か

AI Automation Starter Kit は、GitHub上の公開OSSを調べて、業務自動化に使えそうな候補を見つけ、検討資料に変えるローカルPython CLIです。

単なるリポジトリ検索ではありません。会社やチームで試す前に、本当に役立つか、安全に試せるか、ライセンス確認が必要か、効果をどう測るかまで整理します。

## 最初の3分

1. まず [初心者ルートマップ](BEGINNER_ROUTE_MAP.ja.md) で、自分の進むルートを選びます。
2. 次に [やさしい解説](BEGINNER_GUIDE.ja.md) で、このプロジェクトの目的をつかみます。
3. [使い方マニュアル](USER_MANUAL.ja.md) の「最初に安心してほしいこと」と「5分で分かる全体像」を読みます。
4. AIやクラウドが不安な場合は [AI初心者サポートマップ](AI_BEGINNER_SUPPORT_MAP.ja.md) をAIエージェントに読ませます。
5. 副業や受託として最初の1件を進めたい場合は [最初の顧客案件ウォークスルー](FIRST_CLIENT_WALKTHROUGH.ja.md) を読みます。
6. ローカル導入後に `ai-automation-kit complete-workspace --flow-id invoice-document-followup --client-type local-business --niche accounting --output .tmp/complete-accounting` を実行します。
7. `.tmp/complete-accounting/client_command_center.html` と `.tmp/complete-accounting/FINAL_DELIVERY_GUIDE.md` を開きます。
8. クラウドやAPI設定へ進む前に `guided-setup`、`guided-review`、`cloud-plan` の順番で不足情報を整理します。

## 読む順番

| あなたの状況 | 次に読むもの | 最初に試すこと |
| --- | --- | --- |
| 何から始めればよいか分からない | [初心者ルートマップ](BEGINNER_ROUTE_MAP.ja.md) | CLIを使わないルート |
| 開発者 | [Quickstart](../README.md#quickstart) | guided onboarding |
| 自動化支援をしたい | [ユースケース](USE_CASES.ja.md) | `onboard --create-offer-pack` |
| AIエージェントを使い始めて副業化したい | [最初の顧客案件ウォークスルー](FIRST_CLIENT_WALKTHROUGH.ja.md) | `complete-workspace` |
| クラウドやAPI設定が不安 | [AI初心者サポートマップ](AI_BEGINNER_SUPPORT_MAP.ja.md) | `guided-setup` |
| 会社やチームで検討 | [やさしい解説](BEGINNER_GUIDE.ja.md) | executive decision brief |
| 英語で読みたい | [Start Here](START_HERE.md) | [Beginner guide](BEGINNER_GUIDE.md) |

## 安全面

生成される資料は、まず dry-run で検討する前提です。offer-pack は提案や納品範囲を整理するための資料であり、収益を保証するものではありません。第三者OSSを本番利用する前に、ライセンス、セキュリティ、データ取り扱い、承認者を確認してください。

## 次の段階

- [実行ブリッジ](EXECUTION_BRIDGES.ja.md)
- [運用拡張ガイド](OPERATIONS_EXPANSION.ja.md)
