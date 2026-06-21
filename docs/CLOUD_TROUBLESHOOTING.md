# Cloud Troubleshooting

This guide helps beginners diagnose common cloud deployment problems without rushing into production.

## Deployment Failed

Use this section when deployment failed and you need to separate account, billing, IAM, runtime, file, and command issues.

Check:

- Are you logged in to the provider?
- Is billing enabled?
- Is the project, region, or subscription correct?
- Does the deployer have the required IAM role?
- Are the build files present in the repository?
- Does the runtime match the project?

AI agent prompt:

```text
Please review deploy_runbook.md and the full error text.
Do not print real secrets.
Classify the failure as account, billing, IAM, runtime, missing file, or command syntax.
Suggest only the next safe diagnostic command.
```

## Secret Is Missing

Symptoms:

- The service starts but stops during processing.
- You see `secret is missing` or `environment variable not found`.
- A connector cannot authenticate.

Check:

- All values in `secrets_and_env.md` are set in the provider.
- Names match exactly.
- Real values were not committed to GitHub.
- Local `.env` and cloud secrets are not being confused.

Only share secret names in chat. Put real values in the provider secret manager.

## Webhook Does Not Arrive

Check:

- Is the workload `webhook-api`?
- Is there a public HTTPS URL?
- Is the external service using the correct webhook URL?
- Is the path correct?
- Does the signature secret match?
- Do logs show incoming requests?

LINE is only one connector example. Use the same URL, secret, and log checks for Slack, forms, CRM webhooks, and other inbound systems.

## Scheduler Does Not Run

Check:

- Is the workload `scheduled-job`?
- Is the schedule expression correct?
- Is timezone interpretation correct?
- Does the target function or job exist?
- Does the execution role exist?
- Do logs show invocation history?

Beginner rule: test with a short interval first, then move to the production interval after approval.

## Queue Is Stuck

Check:

- Is the workload `worker-queue`?
- Is the worker running?
- Are retry settings too aggressive?
- Is there a dead-letter queue or failure log?
- Is the same item being processed repeatedly?

Test with one item before increasing production volume.

## Rollback

Use this rollback section when you need to stop first and investigate second.

If something goes wrong:

1. Disable webhook, scheduler, queue consumer, or public traffic.
2. Roll back to the previous revision or stop the service.
3. Rotate any exposed secrets.
4. Preserve logs.
5. Tell the client: stopped, investigating, next update time.

The beginner goal is not to fix everything instantly. The first goal is to stop safely.
