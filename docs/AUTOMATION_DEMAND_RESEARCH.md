# Automation Demand Research

This note maps public demand signals into the built-in flow catalog. It is not a promise of revenue. It is a practical guide for deciding which automation flows deserve more templates, examples, and connectors first.

## Research Signals Used

- Workflow automation and business process automation markets are growing quickly, with demand tied to workflow optimization, low-code platforms, AI, analytics, faster decisions, and customer experience.
- Public automation vendors and reports repeatedly emphasize repetitive tasks: emails, data entry, document processing, notifications, approvals, system integrations, customer service, finance, HR, IT, sales, and operations.
- Agentic automation sources emphasize that automation is moving from one-off task generation toward orchestration where people approve and software executes.
- X research showed strong interest in ready-to-use small-business workflows, open-source AI agents, workflow automation replacing paid subscriptions, and systems where agents draft proposals, emails, and routines while humans review.

## Priority Industries

| Priority | Industry | Why It Is In The Catalog | Example Flow IDs |
|---|---|---|---|
| 1 | Finance / accounting | High-volume document processing, invoice routing, approvals, audit evidence, and reporting. | `accounts-payable-invoice-capture`, `invoice-document-followup`, `expense-policy-check` |
| 2 | Customer support | Repeated messages, ticket triage, knowledge-base gaps, SLA alerts, refund review. | `support-reply-draft`, `ticket-priority-triage`, `sla-breach-alert` |
| 3 | Sales / CRM | Lead routing, follow-up, meeting prep, proposals, CRM hygiene. | `lead-routing-followup`, `crm-lead-cleanup`, `sales-meeting-prep` |
| 4 | HR / recruiting | Onboarding, scheduling, policy acknowledgement, training, screening summaries. | `employee-onboarding-checklist`, `candidate-interview-scheduling`, `policy-acknowledgement-tracker` |
| 5 | Operations / approvals | Purchase requests, KPI reporting, recurring approvals, status reporting. | `weekly-kpi-report`, `purchase-approval-routing` |
| 6 | Healthcare / clinics | Intake reminders, scheduling, eligibility checklists, follow-up task lists. | `patient-intake-reminder`, `appointment-reminder`, `insurance-eligibility-checklist` |
| 7 | Real estate / property management | Maintenance triage, showing coordination, lease renewals, listing updates. | `property-maintenance-triage`, `lease-renewal-reminder` |
| 8 | Legal / compliance | Contract intake, deadline tracking, NDA routing, evidence collection. | `contract-intake-review`, `legal-deadline-tracker`, `compliance-evidence-collection` |
| 9 | Ecommerce / retail | Order updates, shipping, returns, inventory alerts, abandoned carts. | `order-shipping-status`, `inventory-reorder-alert`, `return-request-triage` |
| 10 | Education / training | Inquiry follow-up, attendance alerts, missing assignments, cohort reports. | `course-inquiry-followup`, `student-attendance-alert` |
| 11 | Manufacturing | Work orders, quality logs, supplier delays, maintenance reminders. | `work-order-priority`, `quality-issue-log`, `supplier-delay-alert` |
| 12 | Hospitality | Reservations, guest reviews, housekeeping, event lead follow-up. | `reservation-confirmation-flow`, `guest-review-response` |
| 13 | Field service | Dispatch, completion reports, parts routing, service renewals. | `field-service-dispatch`, `job-completion-report` |
| 14 | IT | Access requests, service routing, security and audit evidence. | `it-access-request` |
| 15 | Marketing | Campaign review, approval routing, content variants. | `campaign-content-review` |

## Priority Workflow Patterns

| Pattern | Why It Matters | Current Coverage |
|---|---|---|
| Document capture and review | Common in finance, legal, HR, healthcare, field service. | Invoice, contract, patient intake, job completion, recruiting summary. |
| Communication drafting | High manual volume and safe when drafts require review. | Support replies, lead follow-up, course inquiries, reminders, reviews. |
| Approval routing | Easy to explain to buyers and valuable because it creates audit evidence. | Purchase approvals, refunds, expenses, NDA, access requests. |
| Reporting and KPI summaries | Strong internal value because teams already use spreadsheets and recurring reports. | Weekly KPI, cashflow, budget variance, training, customer feedback. |
| Scheduling and reminders | Common across clinics, real estate, HR, education, service businesses. | Appointments, interviews, legal deadlines, field dispatch. |
| Inventory and operations alerts | Useful in ecommerce, manufacturing, and field service. | Reorder alerts, supplier delays, parts requests. |
| Compliance and evidence collection | Important for regulated or audit-sensitive workflows. | Expense policy, compliance evidence, quality issue logs, policy acknowledgement. |

## Sources

- UiPath 2025 Agentic AI report: https://www.uipath.com/newsroom/agentic-ai-report-findings
- UiPath agentic automation platform examples: https://www.uipath.com/platform/agentic-automation
- Zapier workflow automation guide: https://zapier.com/blog/workflow-automation/
- Zapier business automation report: https://zapier.com/blog/state-of-business-automation-2021/
- Kissflow SMB process automation focus areas: https://kissflow.com/workflow/bpm/business-process-automation/top-7-smb-areas-in-bpa/
- ThinkAutomation business process automation examples: https://www.thinkautomation.com/blog/10-business-process-automation-examples
- ShipStation automation for ecommerce operations: https://www.shipstation.com/blog/why-business-automation-isnt-optional-in-2026/
- McKinsey economic potential of generative AI: https://www.mckinsey.com/capabilities/tech-and-ai/our-insights/the-economic-potential-of-generative-ai-the-next-productivity-frontier
- Deloitte intelligent automation survey: https://www.deloitte.com/us/en/insights/topics/talent/intelligent-automation-2022-survey-results.html
- X research queries run locally with `/Users/admin/.local/bin/x-search`: Japanese business automation, workflow automation for small business, and AI automation agency workflows.
