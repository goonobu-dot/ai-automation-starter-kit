import json

from ai_automation_kit.core.client_ready import generate_client_ready_pack


def test_generate_client_ready_pack_creates_sales_delivery_and_maintenance_assets(tmp_path):
    source = tmp_path / "onboarding"
    source.mkdir()
    (source / "business_automation_summary.json").write_text(
        json.dumps(
            {
                "business_area": "operations",
                "executive_recommendation": "Start with an accounting workflow pilot.",
                "recommended_projects": [
                    {"full_name": "n8n-io/n8n", "url": "https://github.com/n8n-io/n8n", "score": 90}
                ],
            }
        )
    )
    output = tmp_path / "client-ready"

    payload = generate_client_ready_pack(
        source_output=source,
        output=output,
        business_area="operations",
        client_type="local-business",
        niche="accounting",
    )

    expected = [
        "README.md",
        "client_intake.md",
        "client_intake.json",
        "roi_calculator.csv",
        "pricing_recommendation.md",
        "proposal_tiers.md",
        "implementation_readiness_score.json",
        "implementation_readiness_score.md",
        "security_review.md",
        "prompt_injection_checklist.md",
        "approval_map.md",
        "data_classification.md",
        "tool_stack_recommendation.md",
        "maintenance_plan.md",
        "retainer_offer.md",
        "monthly_review.md",
        "case_study_template.md",
        "before_after_report.md",
        "marketplace_profile.md",
        "outreach_sequence.md",
        "handoff_training.md",
        "tool_comparison.md",
        "template_adaptation_guide.md",
        "compliance_boundaries.md",
        "niche_playbook.md",
        "connector_blueprints.md",
        "demo_inputs.csv",
        "client_ready.json",
    ]
    for name in expected:
        assert (output / name).exists(), name
    assert payload["score"]["total"] >= 85
    assert payload["niche"] == "accounting"
    assert "No income is guaranteed" in (output / "README.md").read_text()
    assert "accounting" in (output / "niche_playbook.md").read_text()
    assert "n8n-io/n8n" in (output / "tool_stack_recommendation.md").read_text()
    assert "human approval" in (output / "approval_map.md").read_text()


def test_generate_client_ready_pack_without_source_still_scores_and_warns(tmp_path):
    output = tmp_path / "client-ready"

    payload = generate_client_ready_pack(
        source_output=tmp_path / "missing",
        output=output,
        business_area="support",
        client_type="solo-founder",
        niche="clinic",
    )

    assert payload["source_status"] == "missing"
    assert payload["score"]["total"] >= 80
    assert "Run `onboard --create-offer-pack`" in (output / "README.md").read_text()
    assert "clinic" in (output / "marketplace_profile.md").read_text()
