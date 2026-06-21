# Grill Me Prompts

These prompts help beginners copy a safe request into an AI agent. The goal is not to get one large answer. The goal is to make the AI ask one question at a time.

## Opportunity Selection

```text
I am new to AI agents.
I want to create a small business automation PoC.
Please ask me one question at a time to decide which workflow I should start with.

Use these criteria: easy to explain, testable with sample data, keeps human approval, and avoids dangerous automatic actions.
```

## Client Interview

```text
I am preparing for a client interview about business automation.
Please ask the client interview questions one at a time.

Start with current pain, input source, output destination, reviewer, and impact if the workflow fails.
If the answer is vague, ask for a concrete example.
```

## Flow Fit Review

```text
Please review whether this flow fits the client.
Do not jump to a conclusion.
Ask one question at a time.

Check:
- business pain
- sample data
- output destination
- human approval
- success metric
- what must not be automated
```

## Cloud Readiness

Use this cloud readiness prompt when local dry-run worked but you are not sure whether cloud deployment is justified.

```text
Please read the cloud-plan output.
I am new to cloud deployment.

Ask me what to verify next, one question at a time.
Separate billing, secrets, IAM, domain, webhook, scheduler, queue, logs, rollback, and human approval.
Do not ask me to paste real API keys or secrets into chat.
```

## API / Secret / Webhook Check

```text
I am stuck on API, secret, or webhook setup.
I will not paste real values.

First tell me what is safe to share.
Then ask one question at a time.
Separate secret names, error text, setting labels, and whether logs exist.
```

## Proposal Review

Use this proposal review prompt before sending scope, price, or delivery promises to a client.

```text
Please review this automation proposal before I send it to a client.

Ask one question at a time.
Check whether I am promising full automation, guaranteed revenue, unmanned operation, or unsafe production updates.
Check whether PoC scope, fee, duration, deliverables, approver, and stop condition are clear.
```

## Stop A Risky Automation

```text
Please check whether this automation idea is risky.

Stop me if it involves medical, legal, financial, personal data, production sending, contracts, payments, discounts, deletion, cancellation, or promises to customers.
Help me convert it into a safe dry-run or approval queue, one question at a time.
```
