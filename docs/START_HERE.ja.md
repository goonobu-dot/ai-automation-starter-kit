# まずここから

AI Automation Starter Kit を初めて見る人は、このページから読むと流れを理解しやすくなります。

## 最初の3分

次の順番で読むのがおすすめです。

1. `README.md` で概要を見る。
2. `docs/BEGINNER_GUIDE.ja.md` でやさしい説明を読む。
3. このファイルで最初の実行手順を見る。
4. `docs/USE_CASES.ja.md` で業務別の使い方を見る。

## 最初に実行すること

```bash
git clone https://github.com/goonobu-dot/ai-automation-starter-kit.git
cd ai-automation-starter-kit
python3 -m venv .venv
source .venv/bin/activate
python3 -m ensurepip --upgrade
python3 -m pip install --upgrade pip setuptools
python3 -m pip install -e .
ai-automation-kit doctor --output .tmp/doctor
ai-automation-kit onboard --business-area operations --limit 2 --output .tmp/onboarding --create-offer-pack
ai-automation-kit beginner-sales --flow-id invoice-document-followup --client-type local-business --niche accounting --output .tmp/beginner-sales
```

## コマンド実行後に読むもの

1. `.tmp/onboarding/onboarding_summary.md`
2. onboarding summary に表示される最初の `next_read` ファイル
3. `.tmp/onboarding/executive_decision_brief.md`
4. `.tmp/onboarding/pilot_scorecard.csv`
5. 副業・受託の小さな提案に変える場合は `.tmp/onboarding/offer_pack/README.md`
6. ひとつの業務フローを企業へ見せたい場合は `.tmp/beginner-sales/selected_flow_demo.html`

## 結果の見方

- `adapter_starter/README.md`: dry-run 用の adapter starter があります。
- `offer_pack/README.md`: 顧客向けの提案・納品資料があります。
- `beginner-sales/README.md`: フローの見えるデモ、営業トーク、ROI計算、提案書、3日PoC計画があります。
- `manual_review_pack.md`: ライセンス、メンテナンス、安全性の確認が先に必要です。
- `query_recovery.md`: 自動化計画の前に検索条件を広げる必要があります。
