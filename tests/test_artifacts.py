from ai_automation_kit.core.artifacts import write_research_artifacts


def test_write_research_artifacts_creates_markdown_html_and_json(tmp_path):
    artifacts = write_research_artifacts(
        output_dir=tmp_path,
        topic="AI automation",
        findings=[{"title": "Example", "uri": "https://example.com", "summary": "Useful source."}],
        run={"run_id": "run-1", "started_at": "start", "finished_at": "finish", "failed_fetches": []},
        rerun_command="python3 -m ai_automation_kit.cli research-agent --config config.json --output out",
    )

    paths = {artifact.kind: tmp_path / artifact.path for artifact in artifacts}
    assert "https://example.com" in paths["markdown"].read_text()
    assert "Rerun Command" in paths["markdown"].read_text()
    assert "<html" in paths["html"].read_text()
    assert '"run_id": "run-1"' in paths["json"].read_text()


def test_write_research_artifacts_creates_failed_fetches_json(tmp_path):
    artifacts = write_research_artifacts(
        output_dir=tmp_path,
        topic="AI automation",
        findings=[],
        run={
            "run_id": "run-1",
            "started_at": "start",
            "finished_at": "finish",
            "failed_fetches": [{"uri": "https://example.com?api_key=***", "reason": "timeout"}],
        },
        rerun_command="PYTHONPATH=src python3 -m ai_automation_kit.cli research-agent --config config.json --output out",
    )

    paths = {artifact.kind: tmp_path / artifact.path for artifact in artifacts}
    assert "failed_fetches" in paths
    assert "api_key=***" in paths["failed_fetches"].read_text()
    assert "timeout" in paths["failed_fetches"].read_text()
