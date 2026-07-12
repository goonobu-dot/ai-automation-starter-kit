# Office Control Automation Research Snapshot - July 2026

This note documents why the July 2026 public docs add six daily control workflow manuals for:

- `spreadsheet-reconciliation-daily`
- `policy-change-impact-daily`
- `quality-incident-capa-daily`
- `vendor-onboarding-daily`
- `access-review-daily`
- `grant-packet-daily`

The selection is intentionally conservative. The packs prepare sourced local drafts for human review. They do not send email, publish, submit grants, approve controls, post journal entries, change access, activate vendors, close CAPAs, or adopt new runtime dependencies.

## Selection thesis

The six packs target office work where a beginner-safe local workflow has enough value without promising full automation:

1. The user already has files: spreadsheets, policies, notices, logs, matrices, forms, evidence, and prior approved outputs.
2. The useful work is source review, exception capture, missing-fact questions, and a draft for a named approver.
3. The risky work remains human-only: approval, submission, access change, vendor activation, payment, policy publication, CAPA closure, and external communication.
4. The side-business offer can be sold as a small paid pilot with visible folders and a PIN approval trail instead of as an autonomous compliance agent.

## X research signal, labeled anecdotal

Local X search was run from Codex with `/Users/admin/.local/bin/x-search` on 2026-07-13 JST. Queries included:

- `spreadsheet reconciliation manual consolidation context quality AI -is:retweet`
- `spreadsheet consolidation manual Excel reconciliation AI context -is:retweet`
- `AI agent context quality source review approval workflow spreadsheet -is:retweet`
- `manual data consolidation spreadsheet reconciliation pain -is:retweet`

The result quality was uneven and should be treated as anecdotal only. The strongest recurring signal was not direct buyer proof for regulated control automation; it was social chatter that manual CSV/spreadsheet consolidation, copy-paste filtering, spreadsheet pain, and AI/Codex-assisted file handling are recognizable office problems. Example public posts surfaced by the local search:

- https://x.com/F8Q75WZwaibw/status/2076244430340944174
- https://x.com/F8Q75WZwaibw/status/2076244433914519578
- https://x.com/DylanShawAI/status/2076237209368461611
- https://x.com/karpachoq/status/2076365978649375029

Interpretation: this supports a low-confidence, anecdotal pain signal for spreadsheet and context cleanup work. It does not prove demand for autonomous compliance, grant, finance, access, vendor, or quality decisions. The manuals therefore position the packs as reviewable local drafting workflows, not full automation.

## Primary/public evidence for grant packet work

Grant packet drafting was included because public grant workflows have visible form, workspace, and oversight complexity:

- Grants.gov Forms: https://www.grants.gov/forms
  - Public relevance: Grants.gov maintains copies of federal forms used by awarding agencies to create grant application packages, post-award reports, and retired forms.
- Grants.gov Workspace overview: https://www.grants.gov/applicants/workspace-overview
  - Public relevance: Workspace is the standard way for organizations or individuals to apply for federal grants; teams can access and edit application forms online or offline.
- GAO federal grants management report, GAO-26-108283: https://www.gao.gov/products/gao-26-108283
  - Public relevance: GAO reported approximately $1.2 trillion in FY2024 grants to tribal, state, local, and territorial governments and noted variation in how grants are designed and managed.
- GAO subaward oversight report, GAO-25-107315: https://www.gao.gov/products/gao-25-107315
  - Public relevance: GAO analyzed single audit findings tied to subrecipient monitoring, reinforcing that grant evidence and oversight are operationally complex.

Design implication: `grant-packet-daily` should only organize evidence, attachment status, deadlines, and unresolved questions. It must not submit, certify eligibility, sign forms, or promise awards.

## GitHub pattern snapshot

The following repositories were checked in July 2026 as public pattern references. They were not vendored, copied, or added as dependencies. They informed the documentation posture: local file conversion and source review are useful, diffs and lineage matter, state machines help control workflows, and prompt evaluation is a separate quality discipline.

Snapshot command path:

- `gh repo view <owner>/<repo> --json nameWithOwner,description,stargazerCount,forkCount,licenseInfo,updatedAt,pushedAt,url`
- Raw license files were also checked from `raw.githubusercontent.com` where GitHub's JSON license field returned `NOASSERTION`.

| Project | Verified July 2026 public snapshot | License note checked | Pattern relevance | Adoption decision |
|---|---:|---|---|---|
| MarkItDown | `microsoft/markitdown`; 165145 stars; 11777 forks; pushed 2026-06-24; https://github.com/microsoft/markitdown | Raw license text is MIT; README warns file conversion performs I/O with current process privileges. | Converts office files and other formats to Markdown for LLM/text pipelines. Supports the idea that source normalization is valuable. | No dependency adoption. Use as pattern evidence only because new conversion behavior would expand security and format risk. |
| Daff | `paulfitz/daff`; 919 stars; 76 forks; pushed 2026-05-27; https://github.com/paulfitz/daff | `package.json` says MIT; `LICENSE.md` contains permissive MIT-style terms. | Table diff and patch patterns fit spreadsheet reconciliation and daily exception comparison. | No vendoring or dependency adoption. Use as design reference for table comparison concepts only. |
| Difftastic | `Wilfred/difftastic`; 25629 stars; 495 forks; pushed 2026-07-12; https://github.com/Wilfred/difftastic | Raw license text is MIT. | Structural diff reinforces that changed structure matters, not only line-level text. | No dependency adoption. It is code-oriented, so direct fit to office docs is limited. |
| transitions | `pytransitions/transitions`; 6565 stars; 571 forks; pushed 2025-09-11; https://github.com/pytransitions/transitions | Raw license text is MIT. | State-machine pattern maps cleanly to created, questioned, ready, running, review, approved, failed, and recovery states. | No dependency adoption. Existing workspace state logic remains local. |
| OpenLineage | `OpenLineage/OpenLineage`; 2535 stars; 483 forks; pushed 2026-07-12; https://github.com/OpenLineage/OpenLineage | Raw license text is Apache-2.0. | Lineage metadata pattern supports source manifest, hashes, and review trails for office drafts. | No dependency adoption. Full lineage instrumentation is too heavy for beginner local docs. |
| Docling | `docling-project/docling`; 63044 stars; 4445 forks; pushed 2026-07-11; https://github.com/docling-project/docling | Raw license text is MIT; README notes local execution capabilities and many document formats. | Document parsing pattern supports the value of local document extraction for evidence-heavy workflows. | No dependency adoption. Broad parser adoption would require security, model, format, and packaging review. |
| Promptfoo | `promptfoo/promptfoo`; 23176 stars; 2078 forks; pushed 2026-07-12; https://github.com/promptfoo/promptfoo | Raw license text is MIT; README positions it for LLM evals and red teaming. | Evaluation and red-team mindset supports treating prompts and AI outputs as testable, not magical. | No dependency adoption. Evaluation is relevant later, but manuals only document operator behavior. |

## Risks and how the docs handle them

- Prompt injection from source files: manuals tell users to inspect accepted sources and treat source documents as evidence, not instructions.
- Unsupported claims: manuals require source review and tell users to mark missing evidence instead of approving guesses.
- External action risk: manuals explicitly exclude email automation, messaging, grant submission, access change, payment, vendor activation, policy publication, CAPA closure, and production writes.
- False compliance confidence: manuals say these packs create drafts, not certifications, sign-offs, or audit opinions.
- Sensitive data: manuals advise sample or sanitized data first and defer real-data permission to the responsible organization.
- Dependency risk: no direct code vendoring or dependency adoption was made from the researched repositories.

## Rejected high-liability ideas

The following ideas were rejected for this release because they would imply external action, regulated judgment, or high-liability automation beyond the local workspace model:

- Automatic bank reconciliation sign-off or journal entry posting.
- Automatic policy publication, employee training assignment, or attestation request.
- Automatic CAPA closure, shipment hold release, product disposition change, or supplier notification.
- Automatic vendor activation, banking update, tax form acceptance, or payment setup.
- Automatic access revocation, permission grant, or access review certification.
- Automatic grant submission, eligibility certification, signature, or award promise.
- Gmail, Outlook, Slack, Teams, or other email/message automation.

## Public-doc decision

The manuals should state:

- Six exact daily control packs are supported as reviewable local draft workflows.
- Dates use strict `YYYY-MM-DD`.
- The folders are the operating model: `01_APPROVED_PAST_OUTPUTS`, `02_PAST_SUPPORTING_FILES`, dated `03_CURRENT_INPUTS`, `04_QUESTIONS`, `05_DRAFTS`, `06_APPROVED_OUTPUTS`, and `07_AUDIT`.
- Draft filenames are exact and pack-specific.
- PIN approval is local and does not send anything.
- Next-day reuse is a checked style/reference handoff, not model training.
- Side-business positioning should sell bounded setup and review cycles, not full automation.
