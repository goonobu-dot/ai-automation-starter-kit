# Contributing

Thanks for improving AI Automation Starter Kit.

## Development Loop

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m ensurepip --upgrade
python3 -m pip install --upgrade pip setuptools
python3 -m pip install -e .
python3 -m pytest -q
python3 scripts/run_all_demos.py
```

## Rules

- Add or update tests before changing behavior.
- Keep examples deterministic and safe to commit.
- Do not commit `.env`, `.tmp`, `.venv`, customer docs, delivery zips, or generated runtime data.
- Prefer adapter-only integrations until licensing has been reviewed in `docs/OSS_INTEGRATIONS.md`.
- Keep every template runnable from a JSON config and an output directory.

