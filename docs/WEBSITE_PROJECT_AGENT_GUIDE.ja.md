# ホームページ制作プロジェクト AIエージェント利用ガイド

このガイドは、このGitHubプロジェクトを Codex、Claude Code、Cursor などで使うための説明です。

目的は「AIで他社サイトをコピーすること」ではありません。人間が確認しながら、オリジナルのホームページと、問い合わせ・予約を管理する裏側の仕組みを作れるようにすることです。

## どのAIでも共通の使い方

1. まずAIにこのガイドを読ませます。
2. 次に `docs/WEBSITE_SIDE_HUSTLE_GUIDE.ja.md` を読ませます。
3. `website-side-hustle` コマンドで案件用パックを生成します。
4. 生成された `ai_agent_handoff.md` をAIに読ませます。
5. 見た目を詰める前に `designer_grade_agent_playbook.md` をAIに読ませます。
6. APIキー、パスワード、実在顧客の個人情報はチャットに貼りません。
7. 公開、料金、予約確定、例外対応は必ず人間が確認します。

## そのまま使える依頼文

```text
このGitHubプロジェクトを、ホームページ制作副業のスターターキットとして読んでください。
docs/WEBSITE_PROJECT_AGENT_GUIDE.ja.md と docs/WEBSITE_SIDE_HUSTLE_GUIDE.ja.md を主な指示として使ってください。
小規模事業者向けに、オリジナルのホームページと、問い合わせ・予約を管理する簡単な裏側の仕組みを作るのを手伝ってください。
デザインは、ヒアリング、方向性、実装、ブラウザー批評、修正、最終確認のループで進めてください。
競合サイトの丸ごとコピーはしないでください。
APIキー、パスワード、実在顧客の個人情報をチャットに貼るよう求めないでください。
情報が足りないときは、一問ずつ聞いてください。
公開、予約確定、料金、ポリシー例外は人間承認を必須にしてください。
```

## AIに任せてよいこと

- 顧客ヒアリング内容をホームページ構成に整理する
- 文字、色、余白、写真、セクション階層を含むデザイン方向性を提案する
- 表側のページを作る、または修正する
- 表示後に、階層、信頼感、オリジナリティ、スマホ表示、アクセシビリティ、導線を批評する
- 問い合わせフォームやCTAの導線を作る
- 問い合わせ台帳の項目を作る
- 返信テンプレートの下書きを作る
- 毎日の運用手順を説明する
- ブラウザー表示や生成ファイルを確認する

## 人間が必ず見ること

- 実在する事業情報が正しいか
- 最終的なブランド判断として、その見た目が事業に合っているか
- 文章、ブランドの雰囲気、料金、規約が正しいか
- 写真、ロゴ、素材の利用権があるか
- フォーム、メール、スプレッドシート、予約ツールのアカウント所有者
- 実際の予約確定、価格例外、キャンセル規定などの例外対応

## Codexでの使い方

Codexは、ローカルのファイルを読み書きしながら作る作業に向いています。

向いている依頼:

- 「観光ホテル向けの website-side-hustle パックを生成して」
- 「サンプルサイトをブラウザーで開いて、スマホ表示を改善して」
- 「予約問い合わせの管理画面モックを追加して」
- 「テストを実行して、変更点を説明して」

## Claude Codeでの使い方

Claude Codeは、リポジトリ全体を読みながら実装計画や説明文を作る作業に向いています。

向いている依頼:

- 「生成されたパックを読んで、顧客案件用の実装計画にして」
- 「安全ルールを守ったままサンプルサイトを作り替えて」
- 「初心者向けの納品説明文を書いて」

## Cursorでの使い方

Cursorは、初心者がコードを見ながら少しずつ編集するときに向いています。

向いている依頼:

- 「このホームページのこの部分をわかりやすく説明して」
- 「ホテル向けの文章を美容室向けに変えて」
- 「問い合わせステータスの定義がどこにあるか探して」

## やってはいけないこと

- 競合サイトを丸ごとコピーする
- 生成したUIを、人間確認なしに「デザイナー承認済み」と扱う
- 実在しない口コミ、実績、資格を書く
- AIだけで予約を確定する
- 承認なしに本番メールやメッセージを送る
- 不必要な個人情報を保存する
- ライセンスが不明なのに安全だと言い切る

## 最初のコマンド

```bash
ai-automation-kit website-side-hustle --industry hospitality --client-type local-business --niche tourism-hotel --output .tmp/website-side-hustle
```

生成後に見るファイル:

- `.tmp/website-side-hustle/START_HERE_WEBSITE_SIDE_HUSTLE.md`
- `.tmp/website-side-hustle/client_kickoff_questions.md`
- `.tmp/website-side-hustle/ai_agent_handoff.md`
- `.tmp/website-side-hustle/designer_grade_agent_playbook.md`
- `.tmp/website-side-hustle/public_ai_design_sources.md`
- `.tmp/website-side-hustle/website_quality_gate.md`
- `.tmp/website-side-hustle/homepage_review_scorecard.csv`
- `.tmp/website-side-hustle/agent_design_review_prompt.md`
- `.tmp/website-side-hustle/beginner_human_guide.ja.md`
- `.tmp/website-side-hustle/delivery_acceptance_checklist.md`
- `.tmp/website-side-hustle/client_handoff_note.md`
- `.tmp/website-side-hustle/sample_site/index.html`
- `.tmp/website-side-hustle/inquiry_dashboard.html`
