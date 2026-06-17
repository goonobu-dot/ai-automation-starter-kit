# Release Plan: Example AI Delivery

## Preflight

- [ ] Confirm `.env.example` has placeholders only.
- [ ] Run `docker compose config`.
- [ ] Complete smoke test evidence before handoff.

## Release Steps

1. Deploy to a dry-run or staging environment first.
2. Run one representative workflow with synthetic data.
3. Review logs, approvals, and generated artifacts.
4. Promote only after the project owner signs off.

## Services

- `app`: release after smoke test passes.
- `worker`: release after smoke test passes.
