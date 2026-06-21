# AI社員ロードマップ

このロードマップは、このプロジェクトにどのAI社員案を優先して入れるべきか、どれを後回しにすべきか、どのように安全な顧客提案へつなげるべきかを整理したものです。

このプロジェクトの目的は、AIがいきなり部署全体を置き換えると主張することではありません。AIに慣れていない人が、1つの具体的な業務を選び、必要な入力・API・受付フォルダ・承認者を準備し、ローカルdry-runを実行し、顧客に見せられるUIと提案資料を作ることです。

## 優先度1: AI受付社員

最初はここから始めます。

AI受付社員は、中小企業にとって課題が見えやすいです。

- 問い合わせ漏れ。
- 一次返信の遅れ。
- 予約や見積もり前の情報不足。
- FAQ返信の手作業。
- オーナーや担当者への確認漏れ。
- 日次の受付状況が見えない。

使うコマンド:

```bash
ai-automation-kit flows list --industry reception
ai-automation-kit flows install ai-reception-line-inquiry --output .tmp/ai-reception-line-inquiry
```

確認するファイル:

- `setup_requirements.md`
- `client_setup_request.md`
- `ai_action_procedure.md`
- `operator_ui/index.html`
- `monetization_plan.md`

最初の有料dry-run PoCとして最も提案しやすいカテゴリです。

## 優先度2: 社内FAQ / 総務AI社員

次に実用性が高いのが、社内FAQと総務・管理部門の受付です。

社内の質問、規程確認、HR・総務・IT依頼、ナレッジ不足の検出などに使います。顧客向けの本番返信よりリスクが低く、まずは社内向けの下書きと確認依頼として運用しやすいのが強みです。

使うコマンド:

```bash
ai-automation-kit flows list --industry admin
ai-automation-kit flows install ai-admin-faq-routing --output .tmp/ai-admin-faq-routing
```

向いている業務:

- 社内FAQの振り分け。
- 総務依頼の受付。
- 規程・ポリシー確認依頼の整理。
- ナレッジベース不足の検出。
- 担当者向け確認パケットの作成。

AIに例外判断、労務判断、アクセス付与、法的解釈、給与・評価に関わる判断を任せないでください。必ず人間承認を入れます。

## 優先度3: 営業リサーチAI社員

営業リサーチは有効ですが、最初は営業送信ではなく、調査・準備・下書きに限定します。

使うコマンド:

```bash
ai-automation-kit flows list --industry sales-research
ai-automation-kit flows install ai-sales-research-brief --output .tmp/ai-sales-research-brief
```

向いている業務:

- 顧客企業の調査メモ。
- 商談前の準備資料。
- 商談後のフォローアップ下書き。
- CRM更新案。
- 提案書に入れる材料整理。

アウトバウンド営業から始めないでください。大量の営業メール送信、個人情報の雑な収集、未確認の実績・価格・効果の主張はリスクが高いです。営業担当者が確認してから使う下書きに限定します。

## 後回しにするもの

次の領域は、複数のdry-run実績が出るまで後回しにします。

- 多部門AI社員パック。
- 自律的なアウトバウンド営業。
- 自律的な契約レビュー。
- 医療・法律・金融の助言。
- 決済、返金、金銭判断。
- 採用合否判断。
- 本番データベース更新。
- アクセス権限付与。

多部門AI社員という見せ方は将来的には有効です。ただし、最初から営業、経理、法務、総務を全部並べると品質保証が難しくなります。まず1つの業務で信頼を作り、その後で横展開します。

## AI行動手順書

各フローをインストールすると、`ai_action_procedure.md` が生成されます。

このファイルには次を明記します。

- Allowed Actions。
- Forbidden Actions。
- Escalation Rules。
- Human Approval Steps。
- Production Gate。

売れるAI社員は、単なるプロンプトではありません。仕事内容、許可される行動、禁止される行動、人間に回す条件を明確に持つ必要があります。

## 推奨拡張順

1. AI受付社員。
2. 社内FAQ / 総務AI社員。
3. 営業リサーチAI社員。
4. 顧客ごとの接続設定。
5. 再利用できる導入事例。
6. 複数の安全な業務実績ができた後に、多部門パック。

この順番なら、商用価値を高めながら過大な約束を避けられます。
