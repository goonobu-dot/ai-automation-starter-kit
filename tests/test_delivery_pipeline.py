import json

from ai_automation_kit.templates.delivery_pipeline import run_delivery_pipeline


def test_delivery_pipeline_generates_delivery_assets_without_real_secrets(tmp_path):
    config = tmp_path / "config.json"
    config.write_text(
        json.dumps(
            {
                "project_name": "Research Agent Starter",
                "template_name": "research-agent",
                "env_vars": ["OPENAI_API_KEY", "FIRECRAWL_API_KEY"],
                "services": ["research-agent"],
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "out"

    run = run_delivery_pipeline(config_path=config, output_dir=output)

    assert run.status == "succeeded"
    assert (output / "README.md").exists()
    assert (output / ".env.example").exists()
    assert (output / "docker-compose.yml").exists()
    assert (output / "docs" / "operation-manual.md").exists()
    assert (output / "docs" / "delivery-checklist.md").exists()
    assert (output / "docs" / "success-metrics.md").exists()
    assert (output / "tests" / "smoke-test.md").exists()
    env_text = (output / ".env.example").read_text()
    assert "OPENAI_API_KEY=" in env_text
    assert "sk-" not in env_text
    checklist = (output / "docs" / "delivery-checklist.md").read_text()
    metrics = (output / "docs" / "success-metrics.md").read_text()
    assert "Research Agent Starter" in checklist
    assert "Manual time saved per week" in metrics
    assert (output / "runs" / f"{run.run_id}.json").exists()
