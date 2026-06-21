from __future__ import annotations

import json
from pathlib import Path


REQUIRED_PROJECT_FILES = [
    "README.md",
    "flow.yaml",
    "flow.json",
    ".env.example",
    "config/connectors.json",
    "docs/SYSTEM_RUNBOOK.md",
    "workflow_map.mmd",
    "before_after_workflow.md",
    "human_approval_points.md",
    "setup_requirements.md",
    "client_setup_request.md",
    "connector_status.md",
    "monetization_plan.md",
    "operator_ui/index.html",
    "sample_data/input.csv",
    "scripts/run_dry_run.py",
    "scripts/run_automation.py",
    "scripts/approve_all.py",
    "tests/test_flow_contract.py",
]


def _step(step_id: str, name: str, tool: str, input_data: str, output: str, human_approval: bool) -> dict:
    return {
        "id": step_id,
        "name": name,
        "tool": tool,
        "input": input_data,
        "output": output,
        "human_approval": human_approval,
    }


FLOW_CATALOG = [
    {
        "id": "invoice-document-followup",
        "name": "Invoice and Document Follow-up",
        "industry": "finance",
        "genre": "document",
        "summary": "Track missing invoices or documents, draft follow-up messages, and create a weekly status report.",
        "tools": ["Google Sheets", "Gmail / Outlook", "Slack / Teams"],
        "sample_columns": ["client", "missing_document", "due_date", "owner", "status"],
        "steps": [
            _step("intake", "Read missing document list", "Google Sheets", "Spreadsheet rows", "Normalized work queue", False),
            _step("classify", "Prioritize overdue or high-value requests", "Local rules", "Work queue", "Priority labels", False),
            _step("draft", "Create follow-up draft", "Gmail / Outlook", "Priority queue", "Draft message", True),
            _step("notify", "Notify owner for review", "Slack / Teams", "Draft message", "Approval request", True),
            _step("report", "Create weekly collection report", "Google Sheets", "Reviewed statuses", "Status report", False),
        ],
        "success_metrics": ["hours_saved", "fewer_missing_documents", "faster_follow_up"],
    },
    {
        "id": "support-reply-draft",
        "name": "Support Reply Draft",
        "industry": "support",
        "genre": "communication",
        "summary": "Turn inbound customer questions into categorized reply drafts with human approval before sending.",
        "tools": ["Helpdesk export", "Docs", "Gmail / Outlook"],
        "sample_columns": ["ticket_id", "customer", "question", "priority", "status"],
        "steps": [
            _step("intake", "Read new support inquiries", "Helpdesk export", "Ticket rows", "Question queue", False),
            _step("retrieve", "Find likely policy or FAQ context", "Docs", "Question queue", "Context notes", False),
            _step("draft", "Draft customer reply", "AI assistant", "Question and context", "Reply draft", True),
            _step("approve", "Reviewer approves or edits draft", "Human reviewer", "Reply draft", "Approved reply", True),
            _step("log", "Record response status", "Helpdesk export", "Approved reply", "Updated ticket log", False),
        ],
        "success_metrics": ["reply_time", "draft_acceptance_rate", "escalation_rate"],
    },
    {
        "id": "ai-reception-line-inquiry",
        "name": "AI Reception Employee: LINE / Form Inquiry",
        "industry": "reception",
        "genre": "first-response",
        "summary": "Receive LINE, web form, or email inquiries, draft first responses, collect missing details, and escalate items that need a human owner.",
        "tools": ["LINE / Web form / Email export", "FAQ / knowledge base", "Google Sheets", "Slack / Teams"],
        "sample_columns": ["inquiry_id", "customer", "channel", "message", "requested_action", "owner", "status"],
        "steps": [
            _step("intake", "Collect new inquiries from the reception channel", "LINE / Web form / Email export", "Inbound inquiry rows", "Reception work queue", False),
            _step("classify", "Classify FAQ, booking, estimate, complaint, or human-only request", "Local rules + FAQ", "Reception work queue", "Intent and risk labels", False),
            _step("draft", "Draft first response and missing-information questions", "AI assistant", "Intent and risk labels", "Customer reply draft", True),
            _step("record", "Record inquiry details and next action", "Google Sheets", "Customer reply draft", "Reception log row", False),
            _step("escalate", "Notify the human owner for approval or direct handling", "Slack / Teams", "Reception log row", "Human approval request", True),
            _step("report", "Create daily reception summary", "Markdown report", "Reception log row", "Daily reception report", False),
        ],
        "success_metrics": ["first_response_time", "missed_inquiries", "human_escalation_rate", "hours_saved"],
    },
    {
        "id": "ai-reception-estimate-intake",
        "name": "AI Reception Employee: Estimate Intake",
        "industry": "reception",
        "genre": "first-response",
        "summary": "Turn quote or estimate requests into structured requirement packets before a human prepares the final proposal.",
        "tools": ["Web form / Email inbox", "Question checklist", "Google Sheets", "Email draft"],
        "sample_columns": ["request_id", "customer", "service_needed", "budget", "deadline", "missing_info", "owner"],
        "steps": [
            _step("intake", "Collect estimate requests", "Web form / Email inbox", "Request rows", "Estimate request queue", False),
            _step("check", "Check required fields for estimate readiness", "Question checklist", "Estimate request queue", "Missing-information list", False),
            _step("draft", "Draft follow-up questions for missing details", "Email draft", "Missing-information list", "Customer question draft", True),
            _step("record", "Save structured estimate packet", "Google Sheets", "Customer question draft", "Estimate intake log", False),
            _step("handoff", "Route ready packets to the human estimator", "Slack / Teams", "Estimate intake log", "Estimator handoff", True),
        ],
        "success_metrics": ["estimate_prep_time", "missing_information_rate", "handoff_quality", "response_time"],
    },
    {
        "id": "ai-reception-appointment-precheck",
        "name": "AI Reception Employee: Appointment Precheck",
        "industry": "reception",
        "genre": "scheduling",
        "summary": "Prepare appointment requests by collecting availability, required details, and human approval before confirmation.",
        "tools": ["Booking form / LINE", "Calendar export", "Google Sheets", "Email / LINE draft"],
        "sample_columns": ["request_id", "customer", "preferred_date", "service", "contact", "owner", "status"],
        "steps": [
            _step("intake", "Collect appointment requests", "Booking form / LINE", "Booking rows", "Appointment queue", False),
            _step("precheck", "Check required details and schedule constraints", "Calendar export", "Appointment queue", "Precheck result", False),
            _step("draft", "Draft confirmation or clarification message", "Email / LINE draft", "Precheck result", "Appointment message draft", True),
            _step("record", "Record precheck status", "Google Sheets", "Appointment message draft", "Appointment log", False),
            _step("approve", "Human owner approves final confirmation", "Human reviewer", "Appointment log", "Approval record", True),
        ],
        "success_metrics": ["booking_admin_time", "no_show_risk", "confirmation_speed", "missing_details"],
    },
    {
        "id": "ai-reception-daily-report",
        "name": "AI Reception Employee: Daily Report",
        "industry": "reception",
        "genre": "reporting",
        "summary": "Summarize daily inquiries, unresolved items, response drafts, and owner actions for a small business operator.",
        "tools": ["Google Sheets", "Local reports", "Slack / Teams", "Email draft"],
        "sample_columns": ["date", "new_inquiries", "resolved", "needs_owner", "missed_items", "owner", "note"],
        "steps": [
            _step("collect", "Read the daily reception log", "Google Sheets", "Reception log rows", "Daily activity queue", False),
            _step("summarize", "Summarize volume, unresolved items, and risks", "Local rules + AI assistant", "Daily activity queue", "Daily summary draft", True),
            _step("actions", "Create owner action list", "Local reports", "Daily summary draft", "Owner task list", True),
            _step("notify", "Prepare internal daily report message", "Slack / Teams", "Owner task list", "Internal report draft", True),
            _step("archive", "Archive report and metrics", "Markdown report", "Internal report draft", "Daily report archive", False),
        ],
        "success_metrics": ["unresolved_inquiries", "owner_response_time", "daily_report_time", "missed_followups"],
    },
    {
        "id": "weekly-kpi-report",
        "name": "Weekly KPI Report",
        "industry": "operations",
        "genre": "reporting",
        "summary": "Collect spreadsheet metrics, summarize changes, and produce a weekly operator report.",
        "tools": ["Google Sheets", "Markdown report", "Slack / Teams"],
        "sample_columns": ["metric", "last_week", "this_week", "owner", "note"],
        "steps": [
            _step("collect", "Read KPI rows", "Google Sheets", "Metric table", "Validated metrics", False),
            _step("compare", "Calculate week-over-week changes", "Local rules", "Validated metrics", "Change list", False),
            _step("explain", "Draft short explanations", "AI assistant", "Change list", "Narrative report", True),
            _step("review", "Owner checks claims", "Human reviewer", "Narrative report", "Approved report", True),
            _step("publish", "Post approved summary", "Slack / Teams", "Approved report", "Team update", False),
        ],
        "success_metrics": ["reporting_time", "metric_coverage", "decision_cycle_time"],
    },
    {
        "id": "purchase-approval-routing",
        "name": "Purchase Approval Routing",
        "industry": "operations",
        "genre": "approval",
        "summary": "Route purchase requests to the right approver and keep a decision trail.",
        "tools": ["Form export", "Slack / Teams", "Google Sheets"],
        "sample_columns": ["request_id", "requester", "amount", "category", "approver"],
        "steps": [
            _step("intake", "Read purchase request", "Form export", "Request row", "Request packet", False),
            _step("route", "Select approval owner", "Local rules", "Request packet", "Approver assignment", False),
            _step("request", "Send approval request", "Slack / Teams", "Approver assignment", "Approval message", True),
            _step("record", "Record decision", "Google Sheets", "Approver response", "Decision log", False),
            _step("escalate", "Flag overdue decisions", "Slack / Teams", "Decision log", "Escalation note", True),
        ],
        "success_metrics": ["approval_cycle_time", "overdue_count", "audit_completeness"],
    },
    {
        "id": "github-oss-research",
        "name": "GitHub OSS Research Pack",
        "industry": "operations",
        "genre": "research",
        "summary": "Research public GitHub projects, shortlist candidates, and produce adoption evidence.",
        "tools": ["GitHub API", "Markdown report", "CSV scorecard"],
        "sample_columns": ["query", "repo", "stars", "license", "risk"],
        "steps": [
            _step("search", "Search public repositories", "GitHub API", "Search query", "Candidate list", False),
            _step("score", "Score candidates", "Local rules", "Candidate list", "Ranked shortlist", False),
            _step("review", "Review license and maintenance", "Human reviewer", "Ranked shortlist", "Approved candidate", True),
            _step("plan", "Draft adoption plan", "Markdown report", "Approved candidate", "Pilot plan", True),
            _step("handoff", "Create implementation checklist", "CSV scorecard", "Pilot plan", "Handoff checklist", False),
        ],
        "success_metrics": ["review_time", "candidate_quality", "blocked_risk_count"],
    },
    {
        "id": "crm-lead-cleanup",
        "name": "CRM Lead Cleanup",
        "industry": "sales",
        "genre": "data-cleanup",
        "summary": "Find stale or incomplete leads and generate safe cleanup recommendations.",
        "tools": ["CRM export", "CSV report", "Slack / Teams"],
        "sample_columns": ["lead_id", "company", "last_contacted", "stage", "owner"],
        "steps": [
            _step("export", "Read CRM export", "CRM export", "Lead rows", "Lead queue", False),
            _step("detect", "Find stale or incomplete leads", "Local rules", "Lead queue", "Cleanup candidates", False),
            _step("recommend", "Draft next action", "AI assistant", "Cleanup candidates", "Action recommendations", True),
            _step("approve", "Sales owner approves updates", "Human reviewer", "Action recommendations", "Approved actions", True),
            _step("track", "Write cleanup report", "CSV report", "Approved actions", "Cleanup scorecard", False),
        ],
        "success_metrics": ["stale_lead_reduction", "owner_response_rate", "pipeline_hygiene"],
    },
    {
        "id": "sales-meeting-prep",
        "name": "Sales Meeting Prep",
        "industry": "sales",
        "genre": "research",
        "summary": "Prepare account notes, open questions, and a meeting brief from approved sources.",
        "tools": ["CRM export", "Docs", "Markdown brief"],
        "sample_columns": ["account", "opportunity", "recent_note", "risk", "next_meeting"],
        "steps": [
            _step("collect", "Collect account notes", "CRM export", "Account rows", "Account packet", False),
            _step("summarize", "Summarize recent activity", "AI assistant", "Account packet", "Prep summary", True),
            _step("questions", "Draft discovery questions", "AI assistant", "Prep summary", "Question list", True),
            _step("review", "Rep reviews sensitive claims", "Human reviewer", "Meeting brief", "Approved brief", True),
            _step("archive", "Save prep brief", "Markdown brief", "Approved brief", "Prep artifact", False),
        ],
        "success_metrics": ["prep_time_saved", "meeting_quality", "follow_up_completion"],
    },
    {
        "id": "employee-onboarding-checklist",
        "name": "Employee Onboarding Checklist",
        "industry": "hr",
        "genre": "approval",
        "summary": "Track onboarding tasks, missing setup items, and manager reminders.",
        "tools": ["HR spreadsheet", "Slack / Teams", "Checklist"],
        "sample_columns": ["employee", "start_date", "task", "owner", "status"],
        "steps": [
            _step("intake", "Read onboarding task list", "HR spreadsheet", "Task rows", "Onboarding queue", False),
            _step("detect", "Find missing or overdue tasks", "Local rules", "Onboarding queue", "Reminder list", False),
            _step("draft", "Draft manager reminders", "AI assistant", "Reminder list", "Reminder drafts", True),
            _step("approve", "HR owner approves reminders", "Human reviewer", "Reminder drafts", "Approved reminders", True),
            _step("report", "Create onboarding status report", "Checklist", "Task statuses", "Status report", False),
        ],
        "success_metrics": ["onboarding_completion", "overdue_tasks", "manager_response_time"],
    },
    {
        "id": "recruiting-screen-summary",
        "name": "Recruiting Screen Summary",
        "industry": "hr",
        "genre": "document",
        "summary": "Summarize screening notes and route candidates for human decision.",
        "tools": ["ATS export", "Docs", "Scorecard"],
        "sample_columns": ["candidate", "role", "screen_notes", "stage", "recruiter"],
        "steps": [
            _step("collect", "Read screening notes", "ATS export", "Candidate rows", "Candidate packet", False),
            _step("summarize", "Summarize notes against criteria", "AI assistant", "Candidate packet", "Screen summary", True),
            _step("flag", "Flag missing evidence", "Local rules", "Screen summary", "Review flags", False),
            _step("review", "Recruiter reviews summary", "Human reviewer", "Screen summary", "Approved summary", True),
            _step("handoff", "Create hiring team handoff", "Scorecard", "Approved summary", "Handoff note", False),
        ],
        "success_metrics": ["summary_time", "missing_evidence_rate", "handoff_quality"],
    },
    {
        "id": "campaign-content-review",
        "name": "Campaign Content Review",
        "industry": "marketing",
        "genre": "communication",
        "summary": "Draft campaign variants and route them through brand and legal review.",
        "tools": ["Content brief", "Docs", "Approval tracker"],
        "sample_columns": ["campaign", "channel", "message", "owner", "review_status"],
        "steps": [
            _step("brief", "Read campaign brief", "Content brief", "Brief rows", "Creative packet", False),
            _step("draft", "Draft campaign variants", "AI assistant", "Creative packet", "Message variants", True),
            _step("brand", "Route brand review", "Approval tracker", "Message variants", "Brand decision", True),
            _step("legal", "Route legal review if required", "Approval tracker", "Brand decision", "Legal decision", True),
            _step("publish_plan", "Create approved publishing list", "Docs", "Approved messages", "Publishing plan", False),
        ],
        "success_metrics": ["review_cycle_time", "approved_variant_rate", "revision_count"],
    },
    {
        "id": "expense-policy-check",
        "name": "Expense Policy Check",
        "industry": "finance",
        "genre": "approval",
        "summary": "Check expense rows against policy hints and create reviewer queues without auto-rejecting.",
        "tools": ["Expense export", "Policy docs", "CSV report"],
        "sample_columns": ["expense_id", "employee", "amount", "category", "receipt_status"],
        "steps": [
            _step("export", "Read expense rows", "Expense export", "Expense rows", "Expense queue", False),
            _step("policy", "Match policy hints", "Policy docs", "Expense queue", "Policy notes", False),
            _step("flag", "Flag review-needed items", "Local rules", "Policy notes", "Reviewer queue", False),
            _step("review", "Finance reviews flagged items", "Human reviewer", "Reviewer queue", "Review decisions", True),
            _step("report", "Create audit trail report", "CSV report", "Review decisions", "Audit trail", False),
        ],
        "success_metrics": ["review_time", "policy_exception_rate", "audit_completeness"],
    },
    {
        "id": "it-access-request",
        "name": "IT Access Request",
        "industry": "it",
        "genre": "approval",
        "summary": "Route software or account access requests with owner approval and evidence logs.",
        "tools": ["Form export", "Identity checklist", "Slack / Teams"],
        "sample_columns": ["request_id", "employee", "system", "access_level", "manager"],
        "steps": [
            _step("intake", "Read access request", "Form export", "Request rows", "Access queue", False),
            _step("classify", "Classify system and access level", "Identity checklist", "Access queue", "Risk label", False),
            _step("approve", "Ask manager or system owner approval", "Slack / Teams", "Risk label", "Approval record", True),
            _step("handoff", "Create IT fulfillment note", "Identity checklist", "Approval record", "Fulfillment note", True),
            _step("audit", "Record access evidence", "CSV report", "Fulfillment note", "Audit log", False),
        ],
        "success_metrics": ["request_cycle_time", "approval_traceability", "access_error_rate"],
    },
]


EXTRA_FLOW_SPECS = [
    ("accounts-payable-invoice-capture", "Accounts Payable Invoice Capture", "finance", "document", "Capture invoice fields, route exceptions, and prepare approval evidence.", ["Email inbox", "OCR export", "ERP / accounting system"], ["vendor", "invoice_no", "amount", "due_date", "status"], ["processing_time", "exception_rate", "approval_cycle_time"]),
    ("invoice-approval-reminder", "Invoice Approval Reminder", "finance", "approval", "Find invoices waiting for approval and remind the right owner.", ["Accounting export", "Slack / Teams", "Email"], ["invoice_no", "owner", "amount", "age_days", "status"], ["overdue_invoices", "approval_cycle_time", "touches_per_invoice"]),
    ("cashflow-weekly-forecast", "Cashflow Weekly Forecast", "finance", "reporting", "Summarize expected cash inflows and outflows into a weekly finance view.", ["Spreadsheet", "Bank export", "Markdown report"], ["week", "expected_inflow", "expected_outflow", "owner", "note"], ["forecast_time", "variance_rate", "decision_speed"]),
    ("receipt-missing-followup", "Receipt Missing Follow-up", "finance", "communication", "Detect missing receipts and draft employee follow-up messages.", ["Expense export", "Email", "Slack / Teams"], ["employee", "expense_id", "amount", "receipt_status", "owner"], ["missing_receipts", "followup_time", "audit_completeness"]),
    ("budget-variance-explanation", "Budget Variance Explanation", "finance", "reporting", "Compare actuals to budget and draft variance explanations for review.", ["Spreadsheet", "ERP export", "Markdown report"], ["department", "budget", "actual", "variance", "owner"], ["report_time", "variance_coverage", "review_quality"]),
    ("lead-routing-followup", "Lead Routing and Follow-up", "sales", "communication", "Route inbound leads, draft first follow-up, and track response status.", ["Website form", "CRM", "Email"], ["lead", "company", "source", "score", "owner"], ["speed_to_lead", "response_rate", "qualified_leads"]),
    ("proposal-renewal-reminder", "Proposal Renewal Reminder", "sales", "approval", "Find stale proposals and create owner reminders for renewal or close-out.", ["CRM", "Email", "Slack / Teams"], ["deal", "customer", "proposal_date", "stage", "owner"], ["stale_deals", "followup_completion", "forecast_hygiene"]),
    ("quote-request-triage", "Quote Request Triage", "sales", "data-entry", "Normalize quote requests and prepare a reviewed sales handoff.", ["Inbox", "CRM", "Spreadsheet"], ["request_id", "customer", "product", "deadline", "owner"], ["triage_time", "handoff_quality", "missed_deadlines"]),
    ("customer-onboarding-handoff", "Customer Onboarding Handoff", "sales", "customer-success", "Convert closed-won details into a customer onboarding checklist.", ["CRM", "Project tracker", "Docs"], ["account", "plan", "start_date", "owner", "risk"], ["handoff_time", "missing_fields", "onboarding_delay"]),
    ("sales-call-summary", "Sales Call Summary", "sales", "document", "Turn call notes into next steps, risks, and CRM update drafts.", ["Call notes", "CRM", "Markdown brief"], ["account", "call_date", "notes", "next_step", "owner"], ["admin_time", "crm_completeness", "next_step_completion"]),
    ("ticket-priority-triage", "Ticket Priority Triage", "support", "customer-success", "Classify support tickets and route urgent items for human review.", ["Helpdesk export", "Docs", "Slack / Teams"], ["ticket_id", "customer", "topic", "priority", "status"], ["first_response_time", "escalation_accuracy", "backlog_age"]),
    ("refund-request-review", "Refund Request Review", "support", "approval", "Prepare refund-review packets without auto-approving money movement.", ["Helpdesk", "Policy docs", "Spreadsheet"], ["ticket_id", "customer", "amount", "reason", "status"], ["review_time", "policy_compliance", "customer_wait_time"]),
    ("customer-feedback-summary", "Customer Feedback Summary", "support", "reporting", "Summarize feedback themes and route product-impacting issues.", ["Survey export", "Helpdesk", "Markdown report"], ["customer", "rating", "comment", "topic", "owner"], ["theme_coverage", "report_time", "issue_followup"]),
    ("sla-breach-alert", "SLA Breach Alert", "support", "approval", "Detect tickets close to SLA breach and notify owners.", ["Helpdesk export", "Slack / Teams", "CSV report"], ["ticket_id", "owner", "sla_due", "priority", "status"], ["sla_breaches", "alert_latency", "owner_response_time"]),
    ("knowledge-base-gap-report", "Knowledge Base Gap Report", "support", "research", "Find repeated support questions that need documentation.", ["Helpdesk export", "Docs", "Markdown report"], ["question", "frequency", "topic", "owner", "status"], ["repeat_questions", "article_backlog", "deflection_rate"]),
    ("candidate-interview-scheduling", "Candidate Interview Scheduling", "hr", "scheduling", "Coordinate interview slots and draft candidate scheduling messages.", ["ATS export", "Calendar", "Email"], ["candidate", "role", "interviewer", "slot", "status"], ["scheduling_time", "no_show_rate", "candidate_response_time"]),
    ("timesheet-reminder", "Timesheet Reminder", "hr", "communication", "Detect missing timesheets and notify employees or managers.", ["HR spreadsheet", "Slack / Teams", "Email"], ["employee", "week", "manager", "status", "due_date"], ["missing_timesheets", "followup_time", "payroll_readiness"]),
    ("policy-acknowledgement-tracker", "Policy Acknowledgement Tracker", "hr", "compliance", "Track policy acknowledgements and create escalation reminders.", ["HRIS export", "Docs", "Email"], ["employee", "policy", "due_date", "manager", "status"], ["acknowledgement_rate", "overdue_count", "audit_readiness"]),
    ("performance-review-packet", "Performance Review Packet", "hr", "document", "Collect review notes and prepare manager review packets.", ["HRIS export", "Docs", "Spreadsheet"], ["employee", "manager", "cycle", "notes", "status"], ["prep_time", "missing_reviews", "review_quality"]),
    ("training-completion-report", "Training Completion Report", "hr", "reporting", "Summarize training completion and overdue learning items.", ["LMS export", "Spreadsheet", "Markdown report"], ["employee", "course", "due_date", "status", "manager"], ["completion_rate", "overdue_training", "report_time"]),
    ("appointment-reminder", "Appointment Reminder", "healthcare", "scheduling", "Prepare appointment reminders and no-show risk flags for review.", ["Scheduling export", "SMS / Email draft", "Spreadsheet"], ["patient", "appointment_time", "provider", "status", "contact"], ["no_show_rate", "reminder_time", "schedule_fill_rate"]),
    ("patient-intake-reminder", "Patient Intake Reminder", "healthcare", "document", "Track missing intake forms and draft reminder messages.", ["Form export", "Email", "Scheduling system"], ["patient", "form", "appointment_date", "status", "owner"], ["missing_forms", "intake_completion", "front_desk_time"]),
    ("insurance-eligibility-checklist", "Insurance Eligibility Checklist", "healthcare", "compliance", "Create an eligibility review checklist before appointments.", ["Insurance export", "Scheduling system", "Checklist"], ["patient", "payer", "appointment_date", "eligibility_status", "owner"], ["verification_time", "claim_risk", "missing_info_rate"]),
    ("care-followup-task-list", "Care Follow-up Task List", "healthcare", "communication", "Create reviewed follow-up task lists after visits.", ["Visit notes", "Task tracker", "Email draft"], ["patient", "visit_date", "followup", "owner", "status"], ["followup_completion", "task_creation_time", "missed_followups"]),
    ("property-maintenance-triage", "Property Maintenance Triage", "real-estate", "approval", "Route tenant maintenance requests by urgency and owner.", ["Tenant form", "Property tracker", "SMS / Email draft"], ["property", "tenant", "issue", "urgency", "status"], ["triage_time", "response_time", "work_order_accuracy"]),
    ("lease-renewal-reminder", "Lease Renewal Reminder", "real-estate", "communication", "Find upcoming lease renewals and draft owner-approved reminders.", ["Lease spreadsheet", "Email", "CRM"], ["tenant", "property", "lease_end", "owner", "status"], ["renewal_rate", "followup_time", "vacancy_risk"]),
    ("showing-schedule-coordination", "Showing Schedule Coordination", "real-estate", "scheduling", "Coordinate property showing requests and create confirmation drafts.", ["Lead form", "Calendar", "Email"], ["lead", "property", "requested_time", "agent", "status"], ["schedule_time", "show_rate", "agent_admin_time"]),
    ("listing-update-checklist", "Listing Update Checklist", "real-estate", "document", "Create listing update tasks from photos, price changes, and descriptions.", ["Listing tracker", "Docs", "Approval tracker"], ["listing", "field", "change", "owner", "status"], ["update_cycle_time", "missing_assets", "approval_completion"]),
    ("contract-intake-review", "Contract Intake Review", "legal", "document", "Collect contract intake details and prepare a lawyer review packet.", ["Intake form", "Docs", "Matter tracker"], ["matter", "client", "contract_type", "deadline", "owner"], ["intake_time", "missing_fields", "review_readiness"]),
    ("legal-deadline-tracker", "Legal Deadline Tracker", "legal", "scheduling", "Track legal deadlines and create escalation reminders.", ["Matter tracker", "Calendar", "Email"], ["matter", "deadline", "responsible", "risk", "status"], ["missed_deadlines", "reminder_time", "calendar_accuracy"]),
    ("nda-request-routing", "NDA Request Routing", "legal", "approval", "Route NDA requests by template type and approval owner.", ["Form export", "Document templates", "Approval tracker"], ["requester", "counterparty", "template", "deadline", "status"], ["routing_time", "template_accuracy", "approval_cycle_time"]),
    ("compliance-evidence-collection", "Compliance Evidence Collection", "legal", "compliance", "Collect evidence links and owner attestations for compliance review.", ["Spreadsheet", "Docs", "Email"], ["control", "evidence", "owner", "due_date", "status"], ["evidence_completion", "audit_readiness", "overdue_items"]),
    ("order-shipping-status", "Order Shipping Status", "ecommerce", "communication", "Sync order status and draft customer shipping updates.", ["Store export", "Shipping platform", "Email"], ["order_id", "customer", "carrier", "tracking", "status"], ["support_tickets", "update_time", "delivery_visibility"]),
    ("inventory-reorder-alert", "Inventory Reorder Alert", "ecommerce", "inventory", "Detect low inventory and prepare reorder review queues.", ["Inventory export", "Supplier list", "Spreadsheet"], ["sku", "stock", "reorder_point", "supplier", "status"], ["stockout_risk", "reorder_time", "inventory_accuracy"]),
    ("return-request-triage", "Return Request Triage", "ecommerce", "approval", "Prepare return request review packets with policy checks.", ["Store export", "Policy docs", "Helpdesk"], ["order_id", "customer", "reason", "amount", "status"], ["return_cycle_time", "policy_compliance", "manual_touches"]),
    ("abandoned-cart-followup", "Abandoned Cart Follow-up", "ecommerce", "communication", "Draft safe abandoned-cart follow-ups for approved campaigns.", ["Store export", "Email platform", "CRM"], ["customer", "cart_value", "product", "last_seen", "status"], ["recovery_rate", "draft_time", "campaign_approval_time"]),
    ("course-inquiry-followup", "Course Inquiry Follow-up", "education", "communication", "Route course inquiries and draft student follow-up messages.", ["Inquiry form", "CRM", "Email"], ["student", "course", "question", "source", "owner"], ["response_time", "enrollment_conversion", "missed_inquiries"]),
    ("student-attendance-alert", "Student Attendance Alert", "education", "reporting", "Find attendance risks and create advisor alert lists.", ["Attendance export", "Advisor tracker", "Email"], ["student", "class", "absences", "advisor", "status"], ["risk_detection_time", "advisor_followup", "attendance_improvement"]),
    ("assignment-missing-reminder", "Assignment Missing Reminder", "education", "communication", "Detect missing assignments and draft student or parent reminders.", ["LMS export", "Email", "Spreadsheet"], ["student", "assignment", "due_date", "teacher", "status"], ["missing_work", "reminder_time", "completion_rate"]),
    ("training-cohort-report", "Training Cohort Report", "education", "reporting", "Summarize cohort progress and completion risk.", ["LMS export", "Spreadsheet", "Markdown report"], ["cohort", "course", "completion", "risk", "owner"], ["report_time", "completion_rate", "intervention_speed"]),
    ("work-order-priority", "Work Order Priority", "manufacturing", "approval", "Prioritize work orders and route exceptions to supervisors.", ["MES export", "Spreadsheet", "Slack / Teams"], ["work_order", "line", "priority", "due_date", "status"], ["schedule_adherence", "supervisor_response", "backlog_age"]),
    ("quality-issue-log", "Quality Issue Log", "manufacturing", "compliance", "Normalize quality issues and create corrective-action review queues.", ["Inspection export", "CAPA tracker", "Markdown report"], ["issue_id", "line", "defect", "severity", "owner"], ["defect_response_time", "capa_completion", "audit_readiness"]),
    ("supplier-delay-alert", "Supplier Delay Alert", "manufacturing", "communication", "Detect supplier delays and notify purchasing owners.", ["Supplier spreadsheet", "ERP export", "Email"], ["supplier", "part", "expected_date", "risk", "owner"], ["delay_visibility", "expedite_time", "production_risk"]),
    ("maintenance-schedule-reminder", "Maintenance Schedule Reminder", "manufacturing", "scheduling", "Create preventive maintenance reminders and overdue alerts.", ["Maintenance tracker", "Calendar", "Slack / Teams"], ["asset", "maintenance_date", "technician", "status", "risk"], ["downtime_risk", "completion_rate", "schedule_accuracy"]),
    ("reservation-confirmation-flow", "Reservation Confirmation Flow", "hospitality", "communication", "Draft reservation confirmations and special-request notes.", ["Booking export", "Email", "Property system"], ["guest", "arrival", "room", "request", "status"], ["confirmation_time", "special_request_accuracy", "guest_response"]),
    ("guest-review-response", "Guest Review Response", "hospitality", "communication", "Draft review responses and escalate service issues.", ["Review export", "Docs", "Approval tracker"], ["guest", "rating", "comment", "topic", "status"], ["response_time", "brand_consistency", "issue_escalation"]),
    ("housekeeping-task-board", "Housekeeping Task Board", "hospitality", "scheduling", "Convert room status into a housekeeping task board.", ["Property system", "Task tracker", "Mobile checklist"], ["room", "checkout_time", "task", "owner", "status"], ["room_turn_time", "task_completion", "front_desk_calls"]),
    ("event-lead-followup", "Event Lead Follow-up", "hospitality", "sales", "Route event inquiries and draft follow-up messages.", ["Inquiry form", "CRM", "Email"], ["lead", "event_date", "guest_count", "budget", "owner"], ["response_time", "booking_conversion", "proposal_cycle_time"]),
    ("field-service-dispatch", "Field Service Dispatch", "field-service", "scheduling", "Route service requests to technicians with availability and urgency.", ["Service form", "Calendar", "SMS / Email draft"], ["request", "customer", "location", "urgency", "technician"], ["dispatch_time", "first_visit_resolution", "travel_efficiency"]),
    ("job-completion-report", "Job Completion Report", "field-service", "document", "Turn job notes and photos into a completion report draft.", ["Mobile form", "Photo links", "PDF / Markdown report"], ["job_id", "customer", "work_done", "photos", "status"], ["report_time", "missing_evidence", "invoice_readiness"]),
    ("parts-request-routing", "Parts Request Routing", "field-service", "inventory", "Route parts requests and flag stock or supplier issues.", ["Technician form", "Inventory export", "Supplier list"], ["part", "job_id", "quantity", "stock", "status"], ["parts_delay", "request_time", "stock_accuracy"]),
    ("renewal-service-reminder", "Renewal Service Reminder", "field-service", "communication", "Find upcoming service renewals and draft reminder messages.", ["Customer list", "Calendar", "Email"], ["customer", "service", "renewal_date", "owner", "status"], ["renewal_rate", "followup_time", "missed_renewals"]),
]


def _flow_from_spec(spec: tuple[str, str, str, str, str, list[str], list[str], list[str]]) -> dict:
    flow_id, name, industry, genre, summary, tools, sample_columns, success_metrics = spec
    return {
        "id": flow_id,
        "name": name,
        "industry": industry,
        "genre": genre,
        "summary": summary,
        "tools": tools,
        "sample_columns": sample_columns,
        "steps": [
            _step("intake", "Collect source records", tools[0], "Source rows", "Work queue", False),
            _step("normalize", "Clean and classify records", "Local rules", "Work queue", "Structured queue", False),
            _step("draft", "Prepare recommended action or message", tools[-1], "Structured queue", "Draft output", True),
            _step("approve", "Named owner reviews sensitive action", "Human reviewer", "Draft output", "Approved output", True),
            _step("report", "Write run log and metric report", "Markdown / CSV report", "Approved output", "Audit-ready report", False),
        ],
        "success_metrics": success_metrics,
    }


FLOW_CATALOG.extend(_flow_from_spec(spec) for spec in EXTRA_FLOW_SPECS)


def list_flows(industry: str | None = None, genre: str | None = None) -> list[dict]:
    flows = FLOW_CATALOG
    if industry:
        flows = [flow for flow in flows if flow["industry"] == industry]
    if genre:
        flows = [flow for flow in flows if flow["genre"] == genre]
    return [_flow_summary(flow) for flow in flows]


def get_flow(flow_id: str) -> dict:
    for flow in FLOW_CATALOG:
        if flow["id"] == flow_id:
            return {**flow, "risk_policy": _risk_policy(flow)}
    raise KeyError(f"Unknown flow: {flow_id}")


def install_flow(flow_id: str, output: Path) -> dict:
    flow = get_flow(flow_id)
    output.mkdir(parents=True, exist_ok=True)
    (output / "config").mkdir(exist_ok=True)
    (output / "docs").mkdir(exist_ok=True)
    (output / "sample_data").mkdir(exist_ok=True)
    (output / "scripts").mkdir(exist_ok=True)
    (output / "tests").mkdir(exist_ok=True)

    payload = {
        "flow_id": flow["id"],
        "name": flow["name"],
        "industry": flow["industry"],
        "genre": flow["genre"],
        "status": "installed",
        "required_files": REQUIRED_PROJECT_FILES,
    }
    (output / "README.md").write_text(_render_project_readme(flow), encoding="utf-8")
    (output / "flow.yaml").write_text(_render_flow_yaml(flow), encoding="utf-8")
    (output / "flow.json").write_text(json.dumps(flow, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / ".env.example").write_text(_render_env_example(flow), encoding="utf-8")
    (output / "config" / "connectors.json").write_text(json.dumps(_connector_config(flow), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "docs" / "SYSTEM_RUNBOOK.md").write_text(_render_system_runbook(flow), encoding="utf-8")
    (output / "workflow_map.mmd").write_text(_render_mermaid(flow), encoding="utf-8")
    (output / "before_after_workflow.md").write_text(_render_before_after(flow), encoding="utf-8")
    (output / "human_approval_points.md").write_text(_render_approval_points(flow), encoding="utf-8")
    (output / "setup_requirements.md").write_text(_render_setup_requirements(flow), encoding="utf-8")
    (output / "client_setup_request.md").write_text(_render_client_setup_request(flow), encoding="utf-8")
    (output / "connector_status.md").write_text(_render_connector_status(flow), encoding="utf-8")
    (output / "monetization_plan.md").write_text(_render_monetization_plan(flow), encoding="utf-8")
    (output / "operator_ui").mkdir(exist_ok=True)
    (output / "operator_ui" / "index.html").write_text(_render_operator_ui(flow), encoding="utf-8")
    (output / "sample_data" / "input.csv").write_text(_render_sample_csv(flow), encoding="utf-8")
    (output / "scripts" / "run_dry_run.py").write_text(_render_dry_run_script(flow), encoding="utf-8")
    (output / "scripts" / "run_automation.py").write_text(_render_run_automation_script(flow), encoding="utf-8")
    (output / "scripts" / "approve_all.py").write_text(_render_approve_all_script(flow), encoding="utf-8")
    (output / "tests" / "test_flow_contract.py").write_text(_render_contract_test(flow), encoding="utf-8")
    return payload


def validate_flow_project(output: Path) -> dict:
    missing = [path for path in REQUIRED_PROJECT_FILES if not (output / path).exists()]
    return {
        "status": "ready" if not missing else "missing_files",
        "missing": missing,
        "checked_files": REQUIRED_PROJECT_FILES,
    }


def _flow_summary(flow: dict) -> dict:
    return {
        "id": flow["id"],
        "name": flow["name"],
        "industry": flow["industry"],
        "genre": flow["genre"],
        "summary": flow["summary"],
    }


def _risk_policy(flow: dict) -> dict:
    return {
        "production_guardrail": "Keep external sends, production updates, payments, hiring decisions, and access grants behind human approval.",
        "dry_run_first": True,
        "human_approval_steps": [step["id"] for step in flow["steps"] if step["human_approval"]],
    }


def _render_project_readme(flow: dict) -> str:
    return "\n".join(
        [
            f"# {flow['name']}",
            "",
            flow["summary"],
            "",
            f"- Industry: `{flow['industry']}`",
            f"- Genre: `{flow['genre']}`",
            f"- Flow ID: `{flow['id']}`",
            "",
            "## Files",
            "",
            "- `flow.yaml` - editable flow definition.",
            "- `config/connectors.json` - local connector routing configuration.",
            "- `workflow_map.mmd` - Mermaid workflow diagram.",
            "- `before_after_workflow.md` - before/after business explanation.",
            "- `human_approval_points.md` - steps that require human review.",
            "- `setup_requirements.md` - what the operator and client must prepare.",
            "- `client_setup_request.md` - client-facing request list for data, folders, and API access.",
            "- `connector_status.md` - setup checklist for input, output, approval, and production connectors.",
            "- `monetization_plan.md` - scoped paid dry-run PoC positioning and price guardrails.",
            "- `operator_ui/index.html` - browser-friendly local UI for explaining the flow.",
            "- `sample_data/input.csv` - safe sample input data.",
            "- `scripts/run_automation.py` - local runtime script.",
            "- `scripts/approve_all.py` - local approval-to-outbox script.",
            "- `scripts/run_dry_run.py` - compatibility wrapper for dry-run execution.",
            "",
            "## Run The Dry Run",
            "",
            "```bash",
            "python3 scripts/run_dry_run.py",
            "python3 scripts/run_automation.py",
            "python3 scripts/approve_all.py --approver you@example.com",
            "python3 -m pytest tests/test_flow_contract.py -q",
            "```",
            "",
            "This scaffold is safe-by-default. It creates local queues, drafts, approval records, reports, and local outbox files. It does not send external messages or update production systems.",
            "",
        ]
    )


def _render_flow_yaml(flow: dict) -> str:
    lines = [
        f"id: {flow['id']}",
        f"name: {flow['name']}",
        f"industry: {flow['industry']}",
        f"genre: {flow['genre']}",
        f"summary: {flow['summary']}",
        "tools:",
    ]
    lines.extend(f"  - {tool}" for tool in flow["tools"])
    lines.append("steps:")
    for index, step in enumerate(flow["steps"], start=1):
        lines.extend(
            [
                f"  - number: {index}",
                f"    id: {step['id']}",
                f"    name: {step['name']}",
                f"    tool: {step['tool']}",
                f"    input: {step['input']}",
                f"    output: {step['output']}",
                f"    human_approval: {str(step['human_approval']).lower()}",
            ]
        )
    lines.append("success_metrics:")
    lines.extend(f"  - {metric}" for metric in flow["success_metrics"])
    lines.append("risk_policy:")
    lines.append(f"  production_guardrail: {_risk_policy(flow)['production_guardrail']}")
    lines.append("  dry_run_first: true")
    return "\n".join(lines) + "\n"


def _connector_config(flow: dict) -> dict:
    return {
        "mode": "dry-run",
        "flow_id": flow["id"],
        "input": {"type": "csv", "path": "sample_data/input.csv"},
        "outputs": {
            "work_queue": "automation_output/work_queue.csv",
            "draft_outputs": "automation_output/draft_outputs.md",
            "approval_queue": "automation_output/approval_queue.csv",
            "connector_tasks": "automation_output/connector_tasks.jsonl",
            "status_report": "automation_output/status_report.md",
            "run_log": "automation_output/run_log.json",
            "local_outbox": "local_outbox/",
        },
        "connectors": [
            {"id": "csv_input", "type": "local_csv", "enabled": True, "production_safe": True},
            {"id": "email_draft", "type": "local_email_draft", "enabled": True, "production_safe": True},
            {"id": "slack_draft", "type": "local_slack_draft", "enabled": True, "production_safe": True},
            {"id": "file_report", "type": "local_file_report", "enabled": True, "production_safe": True},
        ],
        "disabled_external_connectors": [
            {"id": "gmail_send", "reason": "requires OAuth and explicit human approval"},
            {"id": "slack_post", "reason": "requires webhook and explicit human approval"},
            {"id": "google_sheets_write", "reason": "requires service account and client data review"},
        ],
    }


def _render_env_example(flow: dict) -> str:
    return "\n".join(
        [
            f"# {flow['name']} local automation settings",
            "FLOW_MODE=dry-run",
            "APPROVER_EMAIL=owner@example.com",
            "# Optional future connectors. Leave empty for local-only execution.",
            "GMAIL_CLIENT_ID=",
            "GMAIL_CLIENT_SECRET=",
            "SLACK_WEBHOOK_URL=",
            "GOOGLE_SHEETS_CREDENTIALS_JSON=",
            "",
        ]
    )


def _render_system_runbook(flow: dict) -> str:
    return "\n".join(
        [
            f"# System Runbook: {flow['name']}",
            "",
            "This generated project is a local automation system scaffold. It runs safely in dry-run mode and writes all outputs to local files.",
            "",
            "## Run",
            "",
            "```bash",
            "python3 scripts/run_automation.py",
            "python3 scripts/approve_all.py --approver owner@example.com",
            "python3 -m pytest tests/test_flow_contract.py -q",
            "```",
            "",
            "## Outputs",
            "",
            "- `automation_output/work_queue.csv`",
            "- `automation_output/draft_outputs.md`",
            "- `automation_output/approval_queue.csv`",
            "- `automation_output/connector_tasks.jsonl`",
            "- `automation_output/status_report.md`",
            "- `automation_output/run_log.json`",
            "- `automation_output/approved_actions.csv` after approval",
            "- `local_outbox/email_drafts.md` after approval",
            "- `local_outbox/slack_messages.md` after approval",
            "",
            "## Production Boundary",
            "",
            "The default system never sends external messages, posts to Slack, updates Google Sheets, grants access, moves money, or makes irreversible decisions.",
            "Enable real connectors only after credentials, data classification, approval ownership, and rollback rules are defined.",
            "",
        ]
    )


def _render_mermaid(flow: dict) -> str:
    lines = ["flowchart TD"]
    previous = None
    for index, step in enumerate(flow["steps"], start=1):
        node = f"S{index}"
        label = f"{index}. {step['name']}\\n{step['tool']}"
        if step["human_approval"]:
            label += "\\nHuman approval"
        lines.append(f'  {node}["{label}"]')
        if previous:
            lines.append(f"  {previous} --> {node}")
        previous = node
    return "\n".join(lines) + "\n"


def _render_before_after(flow: dict) -> str:
    return "\n".join(
        [
            f"# Before / After: {flow['name']}",
            "",
            "## Before",
            "",
            "- Work is tracked manually across inboxes, spreadsheets, or chat.",
            "- Status is hard to audit.",
            "- Follow-up depends on individual memory.",
            "- Reporting requires repeated copy and paste.",
            "",
            "## After",
            "",
            "- Work enters a visible queue.",
            "- Safe steps run in dry-run mode first.",
            "- Human approval is preserved where decisions affect customers, money, hiring, access, or production data.",
            "- Output files and logs provide evidence for client review.",
            "",
        ]
    )


def _render_approval_points(flow: dict) -> str:
    lines = [f"# Human Approval Points: {flow['name']}", ""]
    approval_steps = [step for step in flow["steps"] if step["human_approval"]]
    for step in approval_steps:
        lines.extend(
            [
                f"## {step['id']}: {step['name']}",
                "",
                f"- Tool: {step['tool']}",
                f"- Input: {step['input']}",
                f"- Output: {step['output']}",
                "- Rule: do not send, update production, approve, reject, grant access, or make irreversible changes without named owner review.",
                "",
            ]
        )
    return "\n".join(lines)


def _render_setup_requirements(flow: dict) -> str:
    return "\n".join(
        [
            f"# Setup Requirements: {flow['name']}",
            "",
            "Use this checklist before promising real automation to a client. The default project runs locally and writes safe dry-run files.",
            "",
            "## What The Operator Must Prepare",
            "",
            "- API keys or OAuth access for any real connector that will be enabled later.",
            "- A reception folder or source export folder for incoming CSV, email, LINE, form, or spreadsheet data.",
            "- A local output folder for work queues, drafts, approval records, reports, and outbox files.",
            "- A named human approval owner who can review customer-facing messages and sensitive actions.",
            "- A small sample dataset that does not contain secrets, payment data, medical decisions, legal advice, or production-only records.",
            "",
            "## What The Client Must Prepare",
            "",
            "- The current manual workflow and the person responsible for each decision.",
            "- Frequently asked questions, standard answers, service menus, pricing rules, or intake questions.",
            "- Escalation rules for complaints, refunds, contracts, medical/legal/financial questions, and urgent requests.",
            "- Success metrics such as response time, missed inquiries, hours saved, error reduction, or owner follow-up time.",
            "",
            "## First Safe Run",
            "",
            "1. Put sample rows in `sample_data/input.csv`.",
            "2. Run `python3 scripts/run_automation.py`.",
            "3. Review `automation_output/approval_queue.csv`.",
            "4. Run `python3 scripts/approve_all.py --approver owner@example.com` only after confirming the drafts.",
            "5. Share `operator_ui/index.html`, `before_after_workflow.md`, and `monetization_plan.md` with the client for the PoC discussion.",
            "",
        ]
    )


def _render_client_setup_request(flow: dict) -> str:
    return "\n".join(
        [
            f"# Client Setup Request: {flow['name']}",
            "",
            "Please provide only the minimum information required for a dry-run proof of concept. Do not send passwords, private API secrets, production customer exports, payment records, or legally sensitive documents through chat.",
            "",
            "## Business Context",
            "",
            f"- Target workflow: {flow['name']}",
            f"- Main business outcome: {', '.join(flow['success_metrics'])}",
            "- Current owner for the workflow:",
            "- Final approver for customer-facing outputs:",
            "",
            "## Data And Folders",
            "",
            "- Sample input file or reception folder path:",
            "- Output folder where reports can be written:",
            "- Existing Google Sheet, CRM export, inbox export, or form export:",
            "- Fields that must never be shared externally:",
            "",
            "## Rules",
            "",
            "- Standard reply or FAQ source:",
            "- When the AI should ask a follow-up question:",
            "- When the AI must stop and escalate to a human:",
            "- Actions that are forbidden during the PoC:",
            "",
            "## Approval",
            "",
            "- Approver name:",
            "- Approver email:",
            "- Review cadence:",
            "- Go-live condition after the dry run:",
            "",
        ]
    )


def _render_connector_status(flow: dict) -> str:
    connector_rows = [
        ("Input source", "local CSV / exported folder", "ready", "Use `sample_data/input.csv` until real connector access is approved."),
        ("Draft output", "local Markdown and CSV", "ready", "Generated files stay local and are not sent automatically."),
        ("Approval queue", "local CSV", "ready", "Named owner approval is required for human approval steps."),
        ("Operator UI", "local HTML", "ready", "Open `operator_ui/index.html` in a browser for demos."),
        ("Gmail / Outlook", "OAuth", "needs_setup", "Enable only after client approves credentials and sending rules."),
        ("Google Sheets", "service account / OAuth", "needs_setup", "Enable only after data classification and write permissions are reviewed."),
        ("LINE / Slack / Teams", "token or webhook", "needs_setup", "Enable only after notification wording and escalation rules are approved."),
    ]
    lines = [
        f"# Connector Status: {flow['name']}",
        "",
        "| Area | Connector | Status | Notes |",
        "|---|---|---|---|",
    ]
    lines.extend(f"| {area} | {connector} | {status} | {notes} |" for area, connector, status, notes in connector_rows)
    lines.extend(
        [
            "",
            "Production connectors remain disabled by default. A real connector should not send, post, update, or delete anything until dry-run evidence, rollback rules, and human approval are accepted.",
            "",
        ]
    )
    return "\n".join(lines)


def _render_monetization_plan(flow: dict) -> str:
    return "\n".join(
        [
            f"# Monetization Plan: {flow['name']}",
            "",
            "This file helps a beginner package the workflow as a bounded service. Do not promise income, guaranteed savings, or fully autonomous operation.",
            "",
            "## Offer Positioning",
            "",
            f"Sell this as a Paid dry-run PoC for `{flow['name']}`. The client pays for workflow mapping, sample-data setup, dry-run automation, review UI, and a decision report.",
            "",
            "## Suggested Scope",
            "",
            "- 1 workflow",
            "- 1 source export or reception folder",
            "- 1 output report location",
            "- 1 human approval owner",
            "- 3 to 5 business days for the first PoC",
            "- No production sending, no irreversible updates, and no high-risk decisions",
            "",
            "## Pricing Guardrails",
            "",
            "- Starter dry-run PoC: 50,000 to 150,000 JPY",
            "- Setup plus first month support: 100,000 to 300,000 JPY",
            "- Monthly maintenance after approval: 30,000 to 100,000 JPY",
            "",
            "## Value Evidence To Collect",
            "",
            "- Number of items processed per month",
            "- Current manual minutes per item",
            "- Response delay or missed-work count",
            "- Draft acceptance rate",
            "- Human escalation rate",
            "- Client decision: continue, revise, or stop",
            "",
            "## Safety Rule",
            "",
            "Do not promise income. Present this as a practical automation delivery kit that helps operators explain, test, and safely package one client workflow.",
            "",
        ]
    )


def _render_operator_ui(flow: dict) -> str:
    approval_steps = [step for step in flow["steps"] if step["human_approval"]]
    step_cards = "\n".join(
        f"<li><strong>{index}. {step['name']}</strong><span>{step['tool']} -> {step['output']}</span></li>"
        for index, step in enumerate(flow["steps"], start=1)
    )
    approval_cards = "\n".join(
        f"<li>{step['name']} <span>{step['output']}</span></li>" for step in approval_steps
    )
    metrics = "\n".join(f"<li>{metric.replace('_', ' ')}</li>" for metric in flow["success_metrics"])
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>{flow['name']} Operator UI</title>
  <style>
    body {{ margin: 0; font-family: Arial, sans-serif; background: #f6f7f9; color: #17202a; }}
    header {{ background: #12343b; color: white; padding: 28px; }}
    main {{ max-width: 1080px; margin: 0 auto; padding: 24px; }}
    section {{ background: white; border: 1px solid #d8dee4; border-radius: 8px; padding: 18px; margin-bottom: 16px; }}
    h1, h2 {{ margin-top: 0; }}
    ul {{ padding-left: 22px; }}
    li {{ margin: 10px 0; }}
    li span {{ display: block; color: #57606a; font-size: 14px; margin-top: 3px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; }}
    .status {{ display: inline-block; padding: 4px 8px; border-radius: 6px; background: #dafbe1; color: #116329; font-weight: 700; }}
    .warning {{ background: #fff8c5; color: #7d4e00; }}
  </style>
</head>
<body>
  <header>
    <p class=\"status\">Local dry-run</p>
    <h1>AI Reception Employee</h1>
    <p>{flow['name']} - {flow['summary']}</p>
  </header>
  <main>
    <section>
      <h2>What This Automates</h2>
      <p>This UI explains the selected workflow for a client demo. It does not connect to live systems or send external messages.</p>
    </section>
    <div class=\"grid\">
      <section>
        <h2>Workflow</h2>
        <ul>{step_cards}</ul>
      </section>
      <section>
        <h2>Approval Queue</h2>
        <p class=\"status warning\">Human approval required</p>
        <ul>{approval_cards}</ul>
      </section>
      <section>
        <h2>Success Metrics</h2>
        <ul>{metrics}</ul>
      </section>
      <section>
        <h2>Files To Review</h2>
        <ul>
          <li>setup_requirements.md<span>What the operator and client must prepare.</span></li>
          <li>client_setup_request.md<span>Questions to collect before a paid PoC.</span></li>
          <li>automation_output/approval_queue.csv<span>Items waiting for human review after dry-run.</span></li>
          <li>monetization_plan.md<span>Scoped paid PoC positioning.</span></li>
        </ul>
      </section>
    </div>
  </main>
</body>
</html>
"""


def _render_sample_csv(flow: dict) -> str:
    header = ",".join(flow["sample_columns"])
    sample = ",".join(_sample_value(column) for column in flow["sample_columns"])
    return f"{header}\n{sample}\n"


def _sample_value(column: str) -> str:
    samples = {
        "client": "Acme Co",
        "missing_document": "June invoice",
        "due_date": "2026-06-30",
        "owner": "ops@example.com",
        "status": "open",
        "ticket_id": "T-1001",
        "customer": "Avery",
        "question": "Can you confirm the next step?",
        "priority": "normal",
        "metric": "open_tasks",
        "last_week": "42",
        "this_week": "31",
        "note": "sample",
        "inquiry_id": "INQ-1001",
        "channel": "LINE",
        "message": "I would like to ask about availability and pricing.",
        "requested_action": "appointment",
        "request_id": "REQ-1001",
        "service_needed": "initial consultation",
        "budget": "100000",
        "deadline": "2026-07-15",
        "missing_info": "preferred date",
        "preferred_date": "2026-07-01",
        "service": "consultation",
        "contact": "customer@example.com",
        "date": "2026-06-21",
        "new_inquiries": "12",
        "resolved": "9",
        "needs_owner": "3",
        "missed_items": "0",
    }
    return samples.get(column, f"sample_{column}")


def _render_dry_run_script(flow: dict) -> str:
    return f'''from __future__ import annotations

from run_automation import main


if __name__ == "__main__":
    raise SystemExit(main())
'''


def _render_run_automation_script(flow: dict) -> str:
    return f'''from __future__ import annotations

from pathlib import Path

from ai_automation_kit.core.flow_runtime import run_flow_project


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    result = run_flow_project(ROOT, mode="dry-run")
    output_dir = ROOT / "automation_output"
    print(f"automation_status={{result['status']}}")
    print(f"rows_processed={{result['rows_processed']}}")
    print(f"work_queue={{output_dir / 'work_queue.csv'}}")
    print(f"draft_outputs={{output_dir / 'draft_outputs.md'}}")
    print(f"approval_queue={{output_dir / 'approval_queue.csv'}}")
    print(f"connector_tasks={{output_dir / 'connector_tasks.jsonl'}}")
    print(f"status_report={{output_dir / 'status_report.md'}}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def _render_approve_all_script(flow: dict) -> str:
    return f'''from __future__ import annotations

import argparse
from pathlib import Path

from ai_automation_kit.core.flow_runtime import approve_all_pending


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Approve pending local automation drafts into local outbox files.")
    parser.add_argument("--approver", default="local-operator")
    args = parser.parse_args()
    result = approve_all_pending(ROOT, approver=args.approver)
    print(f"approval_status={{result['status']}}")
    print(f"approved_items={{result['approved_items']}}")
    for path in result["outbox"]:
        print(f"outbox={{path}}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def _render_contract_test(flow: dict) -> str:
    return f'''from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_flow_contract_files_exist():
    assert (ROOT / "flow.yaml").exists()
    assert (ROOT / "workflow_map.mmd").exists()
    assert (ROOT / "sample_data" / "input.csv").exists()


def test_flow_stays_dry_run_first():
    text = (ROOT / "flow.yaml").read_text(encoding="utf-8")
    assert "id: {flow['id']}" in text
    assert "dry_run_first: true" in text
    assert "human_approval: true" in text
'''
