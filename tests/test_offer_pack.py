import json

from ai_automation_kit.core.offer_pack import generate_offer_pack


def test_generate_offer_pack_uses_discovery_outputs(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "business_automation_summary.json").write_text(
        json.dumps(
            {
                "business_area": "operations",
                "executive_recommendation": "Start with a workflow operations pilot.",
                "recommended_projects": [
                    {
                        "full_name": "activepieces/activepieces",
                        "url": "https://github.com/activepieces/activepieces",
                    }
                ],
            }
        )
    )
    (source / "pilot_scorecard.csv").write_text("metric,owner\nmanual_handoffs,operations\n")

    output = tmp_path / "offer"
    payload = generate_offer_pack(
        source_output=source,
        output=output,
        business_area="operations",
        client_type="small-business",
    )

    assert payload["business_area"] == "operations"
    assert payload["client_type"] == "small-business"
    assert payload["source_summary"]["recommended_projects"][0]["full_name"] == "activepieces/activepieces"
    assert (output / "README.md").exists()
    assert (output / "service_catalog.md").exists()
    assert (output / "client_discovery_questions.md").exists()
    assert (output / "proposal.md").exists()
    assert (output / "statement_of_work.md").exists()
    assert (output / "pricing_model.md").exists()
    assert (output / "demo_script.md").exists()
    assert (output / "outreach_messages.md").exists()
    assert (output / "delivery_checklist.md").exists()
    assert (output / "risk_boundaries.md").exists()
    assert (output / "offer_pack.json").exists()
    proposal = (output / "proposal.md").read_text()
    assert "workflow operations pilot" in proposal
    assert "\u514d\u8cac" in proposal
    assert "\u69d8" in proposal
    pricing = (output / "pricing_model.md").read_text()
    assert "No income is guaranteed" in pricing
    assert "5\u301c15\u4e07\u5186" in pricing
    assert "1\u301c3\u4e07\u5186" in pricing
    questions = (output / "client_discovery_questions.md").read_text()
    assert "\u8aad\u307f\u4e0a\u3052" in questions


def test_generate_offer_pack_without_source_still_creates_starter_pack(tmp_path):
    output = tmp_path / "offer"

    payload = generate_offer_pack(
        source_output=tmp_path / "missing",
        output=output,
        business_area="support",
        client_type="solo-consultant",
    )

    assert payload["source_status"] == "missing"
    assert payload["business_area"] == "support"
    assert "support" in (output / "proposal.md").read_text()
    assert "human approval" in (output / "risk_boundaries.md").read_text()
