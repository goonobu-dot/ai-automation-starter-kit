import json

from ai_automation_kit.core.models import RunRecord, SourceRecord
from ai_automation_kit.core.store import JsonRunStore


def test_store_writes_run_and_source_records(tmp_path):
    store = JsonRunStore(tmp_path)
    run = RunRecord("run-1", "research-agent", {"topic": "x"}, "start", None, "running", [], [], [])
    source = SourceRecord("src-1", "web", "https://example.com", "Example", "now", "hash", "raw", "md", {})

    store.save_run(run)
    store.save_source(source)

    assert json.loads((tmp_path / "runs" / "run-1.json").read_text())["run_id"] == "run-1"
    assert json.loads((tmp_path / "sources" / "src-1.json").read_text())["source_id"] == "src-1"
