import json

from ai_automation_kit.templates.docs_rag import run_docs_rag


def test_docs_rag_answers_with_grounded_source_from_markdown(tmp_path):
    doc = tmp_path / "policy.md"
    doc.write_text(
        "# Return Policy\n\nCustomers can return unopened items within 30 days with a receipt.\n",
        encoding="utf-8",
    )
    config = tmp_path / "config.json"
    config.write_text(
        json.dumps(
            {
                "question": "How long can customers return unopened items?",
                "documents": [{"path": str(doc), "title": "Return Policy"}],
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "out"

    run = run_docs_rag(config_path=config, output_dir=output)

    answer = (output / "answer.md").read_text()
    assert run.status == "succeeded"
    assert "30 days" in answer
    assert "Return Policy" in answer
    assert str(doc) in answer
    assert "## Confidence" in answer
    assert "high" in answer
    assert "## Usage Gate" in answer
    assert "Safe to use after source review" in answer
    assert "## Operator Checklist" in answer
    assert "## Next Actions" in answer
    artifact_index = (output / "artifact_index.md").read_text()
    artifact_index_json = json.loads((output / "artifact_index.json").read_text())
    assert "Artifact Index: docs-rag" in artifact_index
    assert "answer.md" in artifact_index
    assert "artifact_index.md" in artifact_index
    assert artifact_index_json["template_name"] == "docs-rag"
    assert any(item["path"] == "answer.md" for item in artifact_index_json["artifacts"])
    assert any(item["path"] == "artifact_index.md" for item in artifact_index_json["artifacts"])
    assert any(item["path"] == "artifact_index.json" for item in artifact_index_json["artifacts"])
    assert (output / "chunks.jsonl").exists()
    assert (output / "source_map.json").exists()
    assert (output / "runs" / f"{run.run_id}.json").exists()


def test_docs_rag_marks_answer_as_insufficient_when_no_evidence(tmp_path):
    doc = tmp_path / "policy.md"
    doc.write_text("# Return Policy\n\nCustomers can return unopened items within 30 days.\n", encoding="utf-8")
    config = tmp_path / "config.json"
    config.write_text(
        json.dumps(
            {
                "question": "What is the warranty for underwater drones?",
                "documents": [{"path": str(doc), "title": "Return Policy"}],
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "out"

    run = run_docs_rag(config_path=config, output_dir=output)

    answer = (output / "answer.md").read_text()
    assert run.status == "succeeded"
    assert "Insufficient evidence" in answer
    assert "low" in answer
    assert "Blocked until more evidence is added" in answer
