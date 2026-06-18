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
ai-automation-kit github-discover --business-area operations --limit 2 --output .tmp/operations-discovery
```

## コマンド実行後に読むもの

1. `.tmp/operations-discovery/run_summary.md`
2. `.tmp/operations-discovery/executive_decision_brief.md`
3. `.tmp/operations-discovery/pilot_scorecard.csv`
4. `.tmp/operations-discovery/artifact_index.md`

## 結果の見方

- `adapter_starter/README.md`: dry-run 用の adapter starter があります。
- `manual_review_pack.md`: ライセンス、メンテナンス、安全性の確認が先に必要です。
- `query_recovery.md`: 自動化計画の前に検索条件を広げる必要があります。

