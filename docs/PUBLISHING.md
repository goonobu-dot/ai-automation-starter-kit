# Publishing Checklist

Use this before publishing the project as a standalone GitHub repository.

## Required Checks

```bash
python3 -m pytest -q
python3 scripts/run_all_demos.py
```

## Manual Review

- [ ] Confirm `.env.example` files contain placeholders only.
- [ ] Confirm `.tmp/`, `.venv/`, and egg-info files are not tracked.
- [ ] Confirm checked-in examples contain no customer data.
- [ ] Confirm `docs/OSS_INTEGRATIONS.md` reflects adapter-only integration status.
- [ ] Confirm `SECURITY.md` mentions secrets, private network protections, and dry-run defaults.
- [ ] Confirm root README shows all five template commands.

## Suggested First Release

- Tag: `v0.1.0`
- Release title: `AI Automation Starter Kit v0.1.0`
- Release notes: first public starter kit with five local automation templates and deterministic examples.

