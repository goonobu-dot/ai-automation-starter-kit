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
    assert "## Next Actions" in answer
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
