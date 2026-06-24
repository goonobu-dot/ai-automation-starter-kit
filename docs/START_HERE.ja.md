# まずここから

このページは、初めて来た人が最初の3分で AI Automation Starter Kit の役割をつかむための入口です。

## これは何か

AI Automation Starter Kit は、GitHub上の公開OSSを調べて、業務自動化に使えそうな候補を見つけ、検討資料に変えるローカルPython CLIです。

単なるリポジトリ検索ではありません。会社やチームで試す前に、本当に役立つか、安全に試せるか、ライセンス確認が必要か、効果をどう測るかまで整理します。

## 最初の3分

1. まず [やさしい解説](BEGINNER_GUIDE.ja.md) を読みます。
2. 次に [ユースケース](USE_CASES.ja.md) から、近い業務領域を選びます。
3. ローカル導入後に `ai-automation-kit onboard --business-area operations --limit 2 --output .tmp/onboarding --create-offer-pack` を実行します。
4. `.tmp/onboarding/onboarding_summary.md` を開き、最初の `next_read` に従って読み進めます。
5. 副業・受託の小さな提案に変える場合は `.tmp/onboarding/offer_pack/README.md` を読みます。
6. ひとつの業務フローを見せながら企業へ説明したい場合は `ai-automation-kit beginner-sales --flow-id invoice-document-followup --client-type local-business --niche accounting --output .tmp/beginner-sales` を実行します。
7. 実行ブリッジ、デプロイ starter、安全運用資料までまとめて欲しい場合は `ai-automation-kit complete-workspace --flow-id invoice-document-followup --client-type local-business --niche accounting --output .tmp/complete-accounting` を実行します。

## 読む順番

| あなたの状況 | 次に読むもの | 最初に試すこと |
| --- | --- | --- |
| 開発者 | [Quickstart](../README.md#quickstart) | guided onboarding |
| 自動化支援をしたい | [ユースケース](USE_CASES.ja.md) | `onboard --create-offer-pack` |
| AIエージェントを使い始めて副業化したい | [やさしい解説](BEGINNER_GUIDE.ja.md) | `beginner-sales` |
| 会社やチームで検討 | [やさしい解説](BEGINNER_GUIDE.ja.md) | executive decision brief |
| 英語で読みたい | [Start Here](START_HERE.md) | [Beginner guide](BEGINNER_GUIDE.md) |

## 安全面

生成される資料は、まず dry-run で検討する前提です。offer-pack は提案や納品範囲を整理するための資料であり、収益を保証するものではありません。第三者OSSを本番利用する前に、ライセンス、セキュリティ、データ取り扱い、承認者を確認してください。

## 次の段階

- [実行ブリッジ](EXECUTION_BRIDGES.ja.md)
- [運用拡張ガイド](OPERATIONS_EXPANSION.ja.md)
