import json
from pathlib import Path

from ai_automation_kit.templates.internal_ai_workflow import run_internal_ai_workflow


def test_internal_ai_workflow_generates_draft_and_pending_approval(tmp_path):
    config = tmp_path / "config.json"
    config.write_text(
        json.dumps(
            {
                "inquiry_text": "Can you send pricing and onboarding details for the automation starter kit?",
                "customer_name": "Avery",
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "out"

    run = run_internal_ai_workflow(config_path=config, output_dir=output)

    draft_md = (output / "draft_reply.md").read_text(encoding="utf-8")
    draft_json = json.loads((output / "draft_reply.json").read_text(encoding="utf-8"))
    approval = json.loads((output / "approval_request.json").read_text(encoding="utf-8"))
    run_record = json.loads((output / "runs" / f"{run.run_id}.json").read_text(encoding="utf-8"))

    assert run.status == "succeeded"
    assert run.template_name == "internal-ai-workflow"
    assert "Hi Avery," in draft_md
    assert "pricing" in draft_md.lower()
    assert draft_json["customer_name"] == "Avery"
    assert draft_json["inquiry_text"] == "Can you send pricing and onboarding details for the automation starter kit?"
    assert draft_json["risk_level"] == "medium"
    assert "approval_checks" in draft_json
    assert (output / "review-checklist.md").exists()
    assert "Confirm pricing is current" in (output / "review-checklist.md").read_text(encoding="utf-8")
    assert approval["status"] == "pending"
    assert approval["dry_run"] is True
    assert approval["action_type"] == "send_reply"
    assert approval["payload"]["draft_path"] == "draft_reply.md"
    assert approval["payload"]["customer_name"] == "Avery"
    assert run_record["artifacts"] == [
        {"kind": "markdown", "path": "draft_reply.md"},
        {"kind": "json", "path": "draft_reply.json"},
        {"kind": "markdown", "path": "review-checklist.md"},
        {"kind": "approval_request", "path": "approval_request.json"},
    ]


def test_internal_ai_workflow_uses_generic_greeting_without_customer_name(tmp_path):
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"inquiry_text": "Please explain setup next steps."}), encoding="utf-8")
    output = tmp_path / "out"

    run_internal_ai_workflow(config_path=config, output_dir=output)

    draft_md = (output / "draft_reply.md").read_text(encoding="utf-8")
    draft_json = json.loads((output / "draft_reply.json").read_text(encoding="utf-8"))
    assert "Hi there," in draft_md
    assert draft_json["customer_name"] is None


def test_internal_ai_workflow_sample_config_matches_expected_draft(tmp_path):
    config = Path("examples/internal-ai-workflow/sample_inquiry.json")
    expected = Path("examples/internal-ai-workflow/expected/draft_reply.md")
    output = tmp_path / "out"

    run_internal_ai_workflow(config_path=config, output_dir=output)

    assert (output / "draft_reply.md").read_text(encoding="utf-8") == expected.read_text(encoding="utf-8")
