from ai_automation_kit.core.flows import get_flow
from ai_automation_kit.core.flows import install_flow
from ai_automation_kit.core.flows import list_flows
from ai_automation_kit.core.flows import validate_flow_project
from ai_automation_kit.core.flow_runtime import approve_all_pending
from ai_automation_kit.core.flow_runtime import run_flow_project


def test_catalog_contains_many_industry_and_genre_flows():
    flows = list_flows()

    assert len(flows) >= 60
    assert {
        "finance",
        "support",
        "sales",
        "hr",
        "operations",
        "marketing",
        "it",
        "healthcare",
        "real-estate",
        "legal",
        "ecommerce",
        "education",
        "manufacturing",
        "hospitality",
        "field-service",
    } <= {flow["industry"] for flow in flows}
    assert {
        "document",
        "communication",
        "reporting",
        "approval",
        "research",
        "data-entry",
        "scheduling",
        "inventory",
        "compliance",
        "customer-success",
    } <= {flow["genre"] for flow in flows}


def test_catalog_covers_high_demand_workflow_patterns_from_research():
    flow_ids = {flow["id"] for flow in list_flows()}

    expected = {
        "accounts-payable-invoice-capture",
        "lead-routing-followup",
        "appointment-reminder",
        "order-shipping-status",
        "contract-intake-review",
        "patient-intake-reminder",
        "property-maintenance-triage",
        "inventory-reorder-alert",
        "field-service-dispatch",
        "course-inquiry-followup",
    }
    assert expected <= flow_ids


def test_catalog_includes_ai_reception_employee_flows_from_business_research():
    flow_ids = {flow["id"] for flow in list_flows()}

    expected = {
        "ai-reception-line-inquiry",
        "ai-reception-estimate-intake",
        "ai-reception-appointment-precheck",
        "ai-reception-daily-report",
    }
    assert expected <= flow_ids


def test_catalog_includes_next_priority_ai_employee_flows_from_report():
    flow_ids = {flow["id"] for flow in list_flows()}

    expected = {
        "ai-admin-faq-routing",
        "ai-admin-policy-request",
        "ai-sales-research-brief",
        "ai-sales-meeting-followup-prep",
    }
    assert expected <= flow_ids


def test_get_flow_returns_structured_steps():
    flow = get_flow("invoice-document-followup")

    assert flow["name"] == "Invoice and Document Follow-up"
    assert len(flow["steps"]) >= 5
    assert any(step["human_approval"] for step in flow["steps"])
    assert flow["risk_policy"]["production_guardrail"]


def test_install_flow_creates_local_project_scaffold(tmp_path):
    output = tmp_path / "invoice-project"

    payload = install_flow("invoice-document-followup", output)

    assert payload["flow_id"] == "invoice-document-followup"
    assert (output / "README.md").exists()
    assert (output / "flow.yaml").exists()
    assert (output / "workflow_map.mmd").exists()
    assert (output / "before_after_workflow.md").exists()
    assert (output / "human_approval_points.md").exists()
    assert (output / "ai_action_procedure.md").exists()
    assert (output / "sample_data" / "input.csv").exists()
    assert (output / "scripts" / "run_dry_run.py").exists()
    assert (output / "scripts" / "run_automation.py").exists()
    assert (output / "scripts" / "approve_all.py").exists()
    assert (output / ".env.example").exists()
    assert (output / "config" / "connectors.json").exists()
    assert (output / "docs" / "SYSTEM_RUNBOOK.md").exists()
    assert (output / "tests" / "test_flow_contract.py").exists()


def test_install_ai_reception_flow_creates_beginner_setup_and_operator_ui(tmp_path):
    output = tmp_path / "ai-reception-project"

    payload = install_flow("ai-reception-line-inquiry", output)

    assert payload["flow_id"] == "ai-reception-line-inquiry"
    assert (output / "setup_requirements.md").exists()
    assert (output / "client_setup_request.md").exists()
    assert (output / "connector_status.md").exists()
    assert (output / "monetization_plan.md").exists()
    assert (output / "operator_ui" / "index.html").exists()

    setup_text = (output / "setup_requirements.md").read_text()
    procedure_text = (output / "ai_action_procedure.md").read_text()
    ui_text = (output / "operator_ui" / "index.html").read_text()
    monetization_text = (output / "monetization_plan.md").read_text()

    assert "API keys" in setup_text
    assert "reception folder" in setup_text
    assert "human approval" in setup_text
    assert "Allowed Actions" in procedure_text
    assert "Forbidden Actions" in procedure_text
    assert "Escalation Rules" in procedure_text
    assert "AI Reception Employee" in ui_text
    assert "Approval Queue" in ui_text
    assert "Paid dry-run PoC" in monetization_text
    assert "Do not promise income" in monetization_text


def test_run_flow_project_executes_generic_automation_outputs(tmp_path):
    output = tmp_path / "invoice-project"
    install_flow("invoice-document-followup", output)

    result = run_flow_project(output)

    assert result["status"] == "succeeded"
    assert result["rows_processed"] == 1
    assert (output / "automation_output" / "work_queue.csv").exists()
    assert (output / "automation_output" / "draft_outputs.md").exists()
    assert (output / "automation_output" / "approval_queue.csv").exists()
    assert (output / "automation_output" / "status_report.md").exists()
    assert (output / "automation_output" / "run_log.json").exists()
    assert (output / "automation_output" / "connector_tasks.jsonl").exists()
    assert "Create follow-up draft" in (output / "automation_output" / "draft_outputs.md").read_text()
    assert "human approval" in (output / "automation_output" / "approval_queue.csv").read_text()


def test_approve_all_pending_creates_local_outbox_artifacts(tmp_path):
    output = tmp_path / "invoice-project"
    install_flow("invoice-document-followup", output)
    run_flow_project(output)

    result = approve_all_pending(output, approver="owner@example.com")

    assert result["status"] == "approved"
    assert result["approved_items"] == 2
    assert (output / "automation_output" / "approved_actions.csv").exists()
    assert (output / "local_outbox" / "email_drafts.md").exists()
    assert (output / "local_outbox" / "slack_messages.md").exists()
    assert "owner@example.com" in (output / "automation_output" / "approved_actions.csv").read_text()
    assert "not sent automatically" in (output / "local_outbox" / "email_drafts.md").read_text()


def test_all_catalog_flows_can_be_installed_and_run(tmp_path):
    for flow in list_flows():
        output = tmp_path / flow["id"]
        install_flow(flow["id"], output)
        result = run_flow_project(output)
        assert result["status"] == "succeeded", flow["id"]
        assert result["rows_processed"] == 1, flow["id"]
        assert (output / "automation_output" / "run_log.json").exists(), flow["id"]


def test_validate_flow_project_checks_required_files(tmp_path):
    output = tmp_path / "support-project"
    install_flow("support-reply-draft", output)

    result = validate_flow_project(output)

    assert result["status"] == "ready"
    assert result["missing"] == []
