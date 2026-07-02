import json

from ai_automation_kit.core.beginner_sales import generate_beginner_sales_pack


def test_generate_beginner_sales_pack_turns_flow_into_sellable_beginner_assets(tmp_path):
    output = tmp_path / "beginner-sales"

    payload = generate_beginner_sales_pack(
        flow_id="invoice-document-followup",
        output=output,
        client_type="local-business",
        niche="accounting",
    )

    expected = [
        "README.md",
        "START_HERE_FOR_SIDE_BUSINESS.md",
        "flow_gallery.html",
        "selected_flow_demo.html",
        "proposal_one_pager.md",
        "beginner_pitch_script.md",
        "client_questions.md",
        "roi_simple_calculator.csv",
        "three_day_poc_plan.md",
        "price_menu.md",
        "outreach_messages.md",
        "objection_handling.md",
        "demo_walkthrough.md",
        "client_delivery_checklist.md",
        "positioning.md",
        "differentiation_matrix.md",
        "beginner_sales.json",
    ]
    for name in expected:
        assert (output / name).exists(), name

    assert payload["flow"]["id"] == "invoice-document-followup"
    assert payload["beginner_score"]["total"] >= 90
    assert "Invoice and Document Follow-up" in (output / "README.md").read_text()
    assert "No income is guaranteed" in (output / "START_HERE_FOR_SIDE_BUSINESS.md").read_text()
    assert "Human approval" in (output / "selected_flow_demo.html").read_text()
    assert "n8n" in (output / "differentiation_matrix.md").read_text()
    assert "accounting" in (output / "positioning.md").read_text()
    stored = json.loads((output / "beginner_sales.json").read_text())
    assert stored["niche"] == "accounting"

    price_menu = (output / "price_menu.md").read_text()
    assert "5\u301c15\u4e07\u5186" in price_menu
    assert "1\u301c3\u4e07\u5186" in price_menu
    assert "\u4fa1\u683c\u306e\u6c7a\u3081\u65b9" in price_menu

    proposal = (output / "proposal_one_pager.md").read_text()
    assert "\u69d8" in proposal
    assert "\u514d\u8cac" in proposal
    assert "\u30b9\u30b1\u30b8\u30e5\u30fc\u30eb" in proposal
    assert "5\u301c15\u4e07\u5186" in proposal

    questions = (output / "client_questions.md").read_text()
    assert "\u6708\u306b\u4f55\u56de" in questions
    assert "\u8aad\u307f\u4e0a\u3052" in questions


def test_generate_beginner_sales_pack_can_render_gallery_from_industry(tmp_path):
    output = tmp_path / "sales-gallery"

    payload = generate_beginner_sales_pack(
        flow_id=None,
        output=output,
        client_type="small-business",
        niche="clinic",
        industry="healthcare",
    )

    gallery = (output / "flow_gallery.html").read_text()
    readme = (output / "README.md").read_text()
    assert payload["industry"] == "healthcare"
    assert payload["flow"]["industry"] == "healthcare"
    assert "patient-intake-reminder" in gallery or "appointment-reminder" in gallery
    assert "selected_flow_demo.html" in readme
