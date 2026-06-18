# Start Here

Use this page when you are visiting AI Automation Starter Kit for the first time.

## First 3 minutes

Read the project in this order:

1. `README.md` for the short project overview.
2. `docs/BEGINNER_GUIDE.md` for a plain explanation.
3. This file when you want the first command path.
4. `docs/USE_CASES.md` for examples by business area.

## First command path

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

## Read after the command

1. `.tmp/operations-discovery/run_summary.md`
2. `.tmp/operations-discovery/executive_decision_brief.md`
3. `.tmp/operations-discovery/pilot_scorecard.csv`
4. `.tmp/operations-discovery/artifact_index.md`

## Result meanings

- `adapter_starter/README.md`: a dry-run adapter starter is available.
- `manual_review_pack.md`: review license, maintenance, and safety first.
- `query_recovery.md`: broaden the search before planning a pilot.

