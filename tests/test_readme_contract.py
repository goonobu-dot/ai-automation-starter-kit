from pathlib import Path


def test_root_readme_documents_starter_kit_quickstart():
    root_readme = Path(__file__).resolve().parents[1] / "README.md"
    text = root_readme.read_text()
    assert "AI Automation Starter Kit" in text
    assert "ai-automation-kit github-discover" in text
    assert "ai-automation-kit research-agent" in text
    assert "examples/research-agent/sample_research.json" in text
    assert "examples/research-agent/expected/report.md" in text
    assert "ai-automation-kit docs-rag" in text
    assert "examples/docs-rag/sample_docs_rag.json" in text
    assert "examples/docs-rag/expected/answer.md" in text
    assert "ai-automation-kit internal-ai-workflow" in text
    assert "examples/internal-ai-workflow/sample_inquiry.json" in text
    assert "ai-automation-kit excel-to-internal-app" in text
    assert "examples/excel-to-internal-app/sample_app.json" in text
    assert "ai-automation-kit delivery-pipeline" in text
    assert "examples/delivery-pipeline/sample_delivery_pipeline.json" in text
