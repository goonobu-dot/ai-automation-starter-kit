# Docs RAG Answer

## Question

How long can customers return unopened items?

## Answer

Customers can return unopened items within 30 days with a receipt.

## Grounding

- Grounded: `true`

## Confidence

- `high`

## Usage Gate

Safe to use after source review and approval.

- Return Policy (examples/docs-rag/sample_docs/return_policy.md) - `doc-001-049411e7-chunk-002`

## Operator Checklist

- [ ] Open the cited source and confirm the answer is still current.
- [ ] Confirm the answer does not expose private or customer-specific data.
- [ ] Route customer-facing use through the approval owner.

## Next Actions

- Review the cited source before using this answer in production.
- If the answer affects customers, route it through an approval workflow.
