from ai_automation_kit.core.flows import get_flow
from ai_automation_kit.core.flows import install_flow
from ai_automation_kit.core.flows import list_flows
from ai_automation_kit.core.flows import validate_flow_project


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
    assert (output / "sample_data" / "input.csv").exists()
    assert (output / "scripts" / "run_dry_run.py").exists()
    assert (output / "tests" / "test_flow_contract.py").exists()


def test_validate_flow_project_checks_required_files(tmp_path):
    output = tmp_path / "support-project"
    install_flow("support-reply-draft", output)

    result = validate_flow_project(output)

    assert result["status"] == "ready"
    assert result["missing"] == []
