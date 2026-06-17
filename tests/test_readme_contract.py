from pathlib import Path


def test_root_readme_documents_starter_kit_quickstart():
    root_readme = Path(__file__).resolve().parents[2] / "README.md"
    text = root_readme.read_text()
    assert "AI Automation Starter Kit" in text
    assert "ai-automation-starter-kit" in text
    assert "PYTHONPATH=src python3 -m ai_automation_kit.cli research-agent" in text
    assert "examples/research-agent/sample_research.json" in text
    assert "examples/research-agent/expected/report.md" in text
    assert "PYTHONPATH=src python3 -m ai_automation_kit.cli docs-rag" in text
    assert "examples/docs-rag/sample_docs_rag.json" in text
    assert "examples/docs-rag/expected/answer.md" in text
    assert "PYTHONPATH=src python3 -m ai_automation_kit.cli internal-ai-workflow" in text
    assert "examples/internal-ai-workflow/sample_inquiry.json" in text
    assert "PYTHONPATH=src python3 -m ai_automation_kit.cli excel-to-internal-app" in text
    assert "examples/excel-to-internal-app/sample_app.json" in text
    assert "PYTHONPATH=src python3 -m ai_automation_kit.cli delivery-pipeline" in text
    assert "examples/delivery-pipeline/sample_delivery_pipeline.json" in text
