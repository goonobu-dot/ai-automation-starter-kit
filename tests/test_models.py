from ai_automation_kit.core.models import ApprovalRequest, Artifact, FailedFetch, RunRecord, SourceRecord


def test_run_record_serializes_to_json_ready_dict():
    record = RunRecord(
        run_id="run-1",
        template_name="research-agent",
        input={"topic": "open source AI"},
        started_at="2026-06-16T00:00:00Z",
        finished_at=None,
        status="running",
        errors=[],
        artifacts=[],
        source_ids=[],
    )

    assert record.to_dict()["template_name"] == "research-agent"
    assert record.to_dict()["status"] == "running"


def test_source_record_keeps_provenance_fields():
    source = SourceRecord(
        source_id="src-1",
        source_type="web",
        uri="https://example.com",
        title="Example",
        retrieved_at="2026-06-16T00:00:00Z",
        content_hash="abc",
        raw_path="sources/raw/src-1.html",
        markdown_path="sources/markdown/src-1.md",
        metadata={"rank": 1},
    )

    assert source.to_dict()["uri"] == "https://example.com"
    assert source.to_dict()["metadata"]["rank"] == 1


def test_artifact_serializes_path_and_kind():
    artifact = Artifact(kind="markdown", path="reports/report.md")
    assert artifact.to_dict() == {"kind": "markdown", "path": "reports/report.md"}


def test_failed_fetch_masks_sensitive_query_values():
    failed = FailedFetch(uri="https://example.com/path?api_key=secret&safe=1", reason="timeout")
    assert "secret" not in failed.to_dict()["uri"]
    assert "api_key=***" in failed.to_dict()["uri"]


def test_approval_request_defaults_to_pending_dry_run():
    approval = ApprovalRequest(action_id="act-1", action_type="send_email", payload={"to": "team@example.com"})
    assert approval.status == "pending"
    assert approval.dry_run is True
