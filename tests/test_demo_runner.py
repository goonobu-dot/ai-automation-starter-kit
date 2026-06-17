from pathlib import Path


def test_demo_runner_documents_all_template_commands():
    text = Path("scripts/run_all_demos.py").read_text()
    for command in [
        "research-agent",
        "docs-rag",
        "internal-ai-workflow",
        "excel-to-internal-app",
        "delivery-pipeline",
    ]:
        assert command in text
    assert ".tmp/all-templates" in text
