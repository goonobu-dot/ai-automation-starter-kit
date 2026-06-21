# Grill Me Checklists

Use these checklists to make an AI agent interview a beginner one question at a time. The user does not need to judge everything alone. The AI should ask, challenge, and stop unsafe steps.

## Workflow Fit

Use this workflow fit checklist before choosing a flow for a client.

- Is the business pain clear?
- Is the input source clear?
- Is the output destination clear?
- Can sample data be used?
- Is there a measurable success metric?
- Can human approval remain in the loop?
- Is the excluded scope clear?

## Client Interview

- Who does the work today?
- How long does it take?
- Which tools are involved?
- What data may the AI read?
- What output may the AI create?
- Who approves it?
- Who stops it if something goes wrong?

## Local Dry-Run

- Is production sending disabled?
- Is only sample data used?
- Is a work queue generated?
- Is draft output generated?
- Is an approval queue preserved?
- Is there a before/after story the client can understand?

## Cloud Readiness

- Is there a clear reason to move to cloud?
- Is the workload selected?
- Is the provider selected?
- Is there a billing owner?
- Is the secret storage path clear?
- Who reviews logs?
- Who owns rollback?
- Who approves production traffic?

## Human Approval

- Approval before customer messages.
- Approval before CRM or spreadsheet updates.
- Approval before webhook activation.
- Approval before scheduler activation.
- Approval before queue consumer activation.
- Approval before domain or public URL exposure.

## Stop Condition

- A secret is missing.
- Logs are not visible.
- The client pushes for production sending too early.
- The success metric is unclear.
- API permissions are not understood.
- There is no rollback owner.
- Personal data or high-risk decisions are mixed into the workflow.

If a stop condition is true, return to dry-run or redesign.
