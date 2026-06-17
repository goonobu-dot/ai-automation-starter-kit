# Rollback Plan: Example AI Delivery

## Rollback Triggers

- Secret exposure, failed smoke test, incorrect customer-facing output, or approval bypass.

## Rollback Steps

1. Stop the affected service.
2. Preserve logs and generated artifacts for review.
3. Revert to the previous known-good configuration.
4. Notify the project owner with impact and next action.

## Services

- `app`: stop container and preserve logs before restart.
- `worker`: stop container and preserve logs before restart.
