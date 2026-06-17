# Publishing Checklist

Use this before publishing the project as a standalone GitHub repository.

## Required Checks

```bash
python3 scripts/public_release_audit.py
python3 scripts/release_smoke.py
```

Use `python3 scripts/release_smoke.py --skip-github` when validating in an offline or CI environment.

## Manual Review

- [ ] Confirm `.env.example` files contain placeholders only.
- [ ] Confirm `.tmp/`, `.venv/`, and egg-info files are not tracked.
- [ ] Confirm checked-in examples contain no customer data.
- [ ] Confirm `docs/OSS_INTEGRATIONS.md` reflects adapter-only integration status.
- [ ] Confirm `SECURITY.md` mentions secrets, private network protections, and dry-run defaults.
- [ ] Confirm root README shows all five template commands.
- [ ] Confirm `docs/RELEASE_CHECKLIST.md` is current.
- [ ] Confirm `.tmp/release-smoke/doctor/doctor_report.md` has no failed checks.
- [ ] Confirm `.tmp/release-smoke/installed-doctor/doctor_report.md` proves the built wheel installs and runs.
- [ ] Confirm live `github-discover` output includes `next_read`, adoption decision, 30-day plan, score breakdown, and risk register.
- [ ] Confirm `.tmp/release-smoke/github-support/manual_review_pack.md` is useful when no adapter candidate is safe enough.

## Suggested First Release

- Tag: `v0.1.0`
- Release title: `AI Automation Starter Kit v0.1.0`
- Release notes: first public starter kit with five local automation templates and deterministic examples.
