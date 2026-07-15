import json
import re
import socket
import threading
from http.client import HTTPConnection
from pathlib import Path

import pytest

from ai_automation_kit.core import autopilot_proof_lab_server
from ai_automation_kit.core.autopilot_proof_lab import (
    REPORT_NAMES,
    add_evidence,
    add_shadow_case,
    create_assessment,
)
from ai_automation_kit.core.autopilot_proof_lab_server import (
    MAX_REQUEST_BYTES,
    TOKEN_HEADER,
    create_autopilot_proof_lab_server,
    run_autopilot_proof_lab_server,
)
from ai_automation_kit.core.autopilot_proof_lab_ui import render_autopilot_proof_lab_ui


FINAL_HARD_GATES = (
    "input_identifiable",
    "completion_testable",
    "standard_policy_confirmed",
    "exceptions_detectable",
    "exception_owner_assigned",
    "least_privilege_available",
    "idempotency_defined",
    "recovery_defined",
    "kill_switch_owned",
    "data_use_permitted",
    "shadow_test_passed",
)


def write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def build_workspace(tmp_path: Path) -> Path:
    workspace = tmp_path / "proof-lab"
    create_assessment(
        workspace,
        pack_id="monthly-report",
        organization="Acme",
        objective="月報作成の自動化可否を判定する",
        requested_level="L3",
        language="ja",
    )
    evidence = add_evidence(
        workspace,
        write(tmp_path / "policy.md", "# Policy\n"),
        role="policy",
        classification="internal",
        provided_by="Yamada",
    )
    add_shadow_case(
        workspace,
        case_id="case-001",
        input_path=write(tmp_path / "case-input.txt", "input\n"),
        expected_path=write(tmp_path / "expected.txt", "approved\n"),
        proposed_path=write(tmp_path / "proposed.txt", "approved\n"),
        risk_tier="medium",
        case_class="normal",
        expected_route="standard",
        proposed_route="standard",
        recovery_tested=True,
        recovery_passed=True,
    )
    return workspace


def _request(server, method, path, *, body=None, headers=None):
    connection = HTTPConnection(server.server_address[0], server.server_address[1], timeout=5)
    try:
        merged_headers = {"Host": "127.0.0.1:{}".format(server.server_address[1])}
        if headers:
            merged_headers.update(headers)
        connection.request(method, path, body=body, headers=merged_headers)
        response = connection.getresponse()
        payload = response.read()
        return response.status, dict(response.getheaders()), payload
    finally:
        connection.close()


def _json_request(server, method, path, *, token=True, body=None, headers=None, origin=True):
    merged_headers = {"Accept": "application/json"}
    if token:
        merged_headers[TOKEN_HEADER] = server.session_token
    if method == "POST" and origin:
        merged_headers["Origin"] = "http://127.0.0.1:{}".format(server.server_address[1])
    if headers:
        merged_headers.update(headers)
    status, response_headers, payload = _request(server, method, path, body=body, headers=merged_headers)
    decoded = json.loads(payload.decode("utf-8"))
    assert set(decoded) == {"ok", "data", "next_action", "error"}
    return status, response_headers, decoded


def _post_json(server, path, payload, *, origin=True, token=True):
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Content-Length": str(len(body)),
    }
    if origin:
        headers["Origin"] = "http://127.0.0.1:{}".format(server.server_address[1])
    return _json_request(server, "POST", path, token=token, body=body, headers=headers, origin=False)


def _start_server(workspace: Path, language="ja"):
    server = create_autopilot_proof_lab_server(workspace, language=language, port=0)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
    thread.start()
    return server, thread


def _stop_server(server, thread):
    server.shutdown()
    thread.join(timeout=5)
    server.server_close()


def _raw_http(server, request_bytes, *, close_write=False):
    with socket.create_connection(server.server_address, timeout=2) as client:
        client.settimeout(2)
        client.sendall(request_bytes)
        if close_write:
            client.shutdown(socket.SHUT_WR)
        chunks = []
        while True:
            try:
                chunk = client.recv(65536)
            except socket.timeout:
                break
            if not chunk:
                break
            chunks.append(chunk)
        return b"".join(chunks)


def _parse_http_json(response_bytes):
    header_bytes, _, body = response_bytes.partition(b"\r\n\r\n")
    status_line = header_bytes.splitlines()[0].decode("iso-8859-1")
    status_code = int(status_line.split()[1])
    payload = json.loads(body.decode("utf-8"))
    assert set(payload) == {"ok", "data", "next_action", "error"}
    return status_code, payload


def test_create_autopilot_proof_lab_server_binds_localhost_and_requires_existing_valid_assessment(tmp_path):
    workspace = build_workspace(tmp_path)
    server, thread = _start_server(workspace)
    try:
        assert server.server_address[0] == "127.0.0.1"
        assert server.workspace == workspace.resolve()
        assert re.fullmatch(r"[0-9a-f]{64}", server.session_token)
    finally:
        _stop_server(server, thread)

    with pytest.raises(ValueError, match="language must be 'ja' or 'en'"):
        create_autopilot_proof_lab_server(workspace, language="fr", port=0)

    with pytest.raises(ValueError, match="assessment workspace has not been created"):
        create_autopilot_proof_lab_server(tmp_path / "missing", language="ja", port=0)

    invalid = tmp_path / "invalid"
    create_assessment(
        invalid,
        pack_id="monthly-report",
        organization="Bad",
        objective="Bad",
        requested_level="L3",
        language="ja",
    )
    state_path = invalid / ".proof_lab" / "state.json"
    state_path.write_text("{broken", encoding="utf-8")
    with pytest.raises(ValueError, match="manual_recovery_required"):
        create_autopilot_proof_lab_server(invalid, language="ja", port=0)


def test_server_root_ui_and_rendered_languages_include_advisory_notice(tmp_path):
    workspace = build_workspace(tmp_path)
    server, thread = _start_server(workspace)
    try:
        status, headers, payload = _request(server, "GET", "/")
        assert status == 200
        assert headers["Content-Type"] == "text/html; charset=utf-8"
        html = payload.decode("utf-8")
        assert "次のアクション" in html
        assert "外部アクションは実行されません" in html
        assert "承認フローは解除されません" in html
        assert "?token=" not in html
    finally:
        _stop_server(server, thread)

    ja_html = render_autopilot_proof_lab_ui("ja", "a" * 64)
    en_html = render_autopilot_proof_lab_ui("en", "b" * 64)
    assert "次のアクション" in ja_html
    assert "評価ID" in ja_html
    assert "ステージ" in ja_html
    assert "到達可能レベル" in ja_html
    assert "--case-class normal" in ja_html
    assert "--workspace" in ja_html
    assert "--source" in ja_html
    assert "--expected-route standard --proposed-route standard" in ja_html
    assert "Autopilot Proof Lab" in en_html
    assert "Assessment ID" in en_html
    assert "Stage" in en_html
    assert "Maximum level" in en_html
    assert "status.maximum_level" in en_html
    assert "No external actions run from this screen." in en_html
    assert "No approval removal happens here." in en_html


def test_status_gate_evaluate_and_report_flow(tmp_path):
    workspace = build_workspace(tmp_path)
    server, thread = _start_server(workspace)
    try:
        status, _, payload = _json_request(server, "GET", "/api/status")
        assert status == 200
        assert payload["ok"] is True
        assert payload["data"]["assessment"]["pack_id"] == "monthly-report"
        assessment_id = payload["data"]["assessment"]["assessment_id"]
        assert payload["data"]["status"]["assessment_id"] == assessment_id
        assert payload["data"]["status"]["stage"] == "ready_for_shadow"
        assert payload["data"]["status"]["maximum_level"] == "L0"
        assert payload["next_action"] == payload["data"]["status"]["next_action"]
        assert payload["data"]["status"]["evidence_count"] == 1
        assert payload["data"]["status"]["shadow_case_count"] == 1
        assert len(payload["data"]["assessment"]["gates"]) == 11
        assert set(payload["data"]["assessment"]["gates"]) == set(FINAL_HARD_GATES)
        assert payload["data"]["report_paths"]["readiness_report.html"] == str(
            workspace / "05_REPORTS" / "readiness_report.html"
        )
        assert payload["data"]["report_links"]["readiness_report.html"] == "/api/reports/readiness_report.html"
        assert set(payload["data"]["report_paths"]) == set(REPORT_NAMES)
        assert set(payload["data"]["report_links"]) == set(REPORT_NAMES)

        for gate_name in FINAL_HARD_GATES:
            note = "gate passed"
            if gate_name == "shadow_test_passed":
                note = "low-volume justification: only 1 historical case exists; owner accepts advisory limit"
            gate_response = _post_json(
                server,
                "/api/gate",
                {
                    "gate": gate_name,
                    "status": "pass",
                    "owner": "ops-owner",
                    "evidence_ids": ["ev-0001"],
                    "note": note,
                },
            )[2]
            assert gate_response["ok"] is True
            assert gate_response["data"]["gate"]["status"] == "pass"

        evaluate = _post_json(server, "/api/evaluate", {})[2]
        assert evaluate["ok"] is True
        assert evaluate["data"]["evaluation"]["decision"] == "assist_only"
        assert evaluate["data"]["evaluation"]["maximum_level"] == "L1"
        assert evaluate["data"]["status"]["decision"] == "assist_only"
        assert evaluate["data"]["status"]["maximum_level"] == "L1"
        assert evaluate["data"]["status"]["assessment_id"] == assessment_id
        assert evaluate["data"]["status"]["stage"] == "assist_only"
        assert evaluate["next_action"] == evaluate["data"]["status"]["next_action"]
        assert evaluate["data"]["status"]["advisory_only"] is True

        report_status, report_headers, report_body = _request(
            server,
            "GET",
            "/api/reports/readiness_report.html",
            headers={TOKEN_HEADER: server.session_token},
        )
        assert report_status == 200
        assert report_headers["Content-Type"] == "text/html; charset=utf-8"
        assert "Readiness" in report_body.decode("utf-8")
    finally:
        _stop_server(server, thread)


def test_server_rejects_missing_bad_token_host_origin_method_and_endpoint(tmp_path):
    workspace = build_workspace(tmp_path)
    server, thread = _start_server(workspace)
    try:
        status, _, payload = _json_request(server, "GET", "/api/status", token=False)
        assert status == 401
        assert payload["error"]["code"] == "missing_token"

        status, _, payload = _json_request(
            server,
            "GET",
            "/api/status",
            token=False,
            headers={TOKEN_HEADER: "bad"},
        )
        assert status == 403
        assert payload["error"]["code"] == "bad_token"

        status, _, payload = _request(
            server,
            "GET",
            "/api/status",
            headers={"Accept": "application/json", TOKEN_HEADER: server.session_token, "Host": "evil.test"},
        )
        decoded = json.loads(payload.decode("utf-8"))
        assert status == 400
        assert decoded["error"]["code"] == "host_not_allowed"

        status, _, payload = _post_json(server, "/api/evaluate", {}, origin=False)
        assert status == 403
        assert payload["error"]["code"] == "origin_not_allowed"

        status, _, payload = _json_request(server, "PUT", "/api/status")
        assert status == 405
        assert payload["error"]["code"] == "method_not_allowed"

        status, _, payload = _json_request(server, "GET", "/api/missing")
        assert status == 404
        assert payload["error"]["code"] == "not_found"
    finally:
        _stop_server(server, thread)


def test_state_changing_posts_reject_bad_origin_before_business_logic(tmp_path, monkeypatch):
    workspace = build_workspace(tmp_path)
    server, thread = _start_server(workspace)
    calls = {"gate": 0, "evaluate": 0}

    def fail_gate(*args, **kwargs):
        calls["gate"] += 1
        raise AssertionError("gate mutation must not run for rejected Origin")

    def fail_evaluate(*args, **kwargs):
        calls["evaluate"] += 1
        raise AssertionError("evaluation must not run for rejected Origin")

    monkeypatch.setattr(autopilot_proof_lab_server, "set_gate", fail_gate)
    monkeypatch.setattr(autopilot_proof_lab_server, "evaluate_assessment", fail_evaluate)
    try:
        status, _, payload = _post_json(
            server,
            "/api/gate",
            {
                "gate": "shadow_test_passed",
                "status": "pass",
                "owner": "ops-owner",
                "evidence_ids": [],
                "note": "",
            },
            origin=False,
        )
        assert status == 403
        assert payload["error"]["code"] == "origin_not_allowed"

        status, _, payload = _post_json(server, "/api/evaluate", {}, origin=False)
        assert status == 403
        assert payload["error"]["code"] == "origin_not_allowed"
        assert calls == {"gate": 0, "evaluate": 0}
    finally:
        _stop_server(server, thread)


def test_server_rejects_oversize_malformed_bad_content_type_and_short_body(tmp_path):
    workspace = build_workspace(tmp_path)
    server, thread = _start_server(workspace)
    try:
        request = (
            "POST /api/evaluate HTTP/1.1\r\n"
            "Host: 127.0.0.1:{port}\r\n"
            "Accept: application/json\r\n"
            "Origin: http://127.0.0.1:{port}\r\n"
            "Content-Type: application/json\r\n"
            "{token_header}: {token}\r\n"
            "Content-Length: {length}\r\n"
            "\r\n"
        ).format(
            port=server.server_address[1],
            token_header=TOKEN_HEADER,
            token=server.session_token,
            length=MAX_REQUEST_BYTES + 1,
        ).encode("utf-8")
        status, payload = _parse_http_json(_raw_http(server, request, close_write=True))
        assert status == 413
        assert payload["error"]["code"] == "request_too_large"

        request = (
            "POST /api/evaluate HTTP/1.1\r\n"
            "Host: 127.0.0.1:{port}\r\n"
            "Accept: application/json\r\n"
            "Origin: http://127.0.0.1:{port}\r\n"
            "Content-Type: application/json\r\n"
            "{token_header}: {token}\r\n"
            "Content-Length: broken\r\n"
            "\r\n"
            "{{}}"
        ).format(
            port=server.server_address[1],
            token_header=TOKEN_HEADER,
            token=server.session_token,
        ).encode("utf-8")
        status, payload = _parse_http_json(_raw_http(server, request, close_write=True))
        assert status == 400
        assert payload["error"]["code"] == "bad_content_length"

        status, _, payload = _json_request(
            server,
            "POST",
            "/api/evaluate",
            body=b"{}",
            headers={
                "Content-Type": "text/plain",
                "Content-Length": "2",
                "Origin": "http://127.0.0.1:{}".format(server.server_address[1]),
            },
            origin=False,
        )
        assert status == 400
        assert payload["error"]["code"] == "bad_content_type"

        request = (
            "POST /api/gate HTTP/1.1\r\n"
            "Host: 127.0.0.1:{port}\r\n"
            "Accept: application/json\r\n"
            "Origin: http://127.0.0.1:{port}\r\n"
            "Content-Type: application/json\r\n"
            "Connection: close\r\n"
            "{token_header}: {token}\r\n"
            "Content-Length: 40\r\n"
            "\r\n"
            "{{}}"
        ).format(
            port=server.server_address[1],
            token_header=TOKEN_HEADER,
            token=server.session_token,
        ).encode("utf-8")
        status, payload = _parse_http_json(_raw_http(server, request))
        assert status == 400
        assert payload["error"]["code"] == "short_body"

        status, _, payload = _json_request(
            server,
            "POST",
            "/api/gate",
            body=b"[]",
            headers={
                "Content-Type": "application/json",
                "Content-Length": "2",
                "Origin": "http://127.0.0.1:{}".format(server.server_address[1]),
            },
            origin=False,
        )
        assert status == 400
        assert payload["error"]["code"] == "bad_json"
    finally:
        _stop_server(server, thread)


def test_report_route_is_safe_authenticated_and_get_only(tmp_path):
    workspace = build_workspace(tmp_path)
    server, thread = _start_server(workspace)
    try:
        _post_json(server, "/api/evaluate", {})

        status, _, payload = _request(server, "GET", "/api/reports/readiness_report.html")
        decoded = json.loads(payload.decode("utf-8"))
        assert status == 401
        assert decoded["error"]["code"] == "missing_token"

        status, _, payload = _json_request(server, "GET", "/api/reports/../../etc/passwd")
        assert status == 400
        assert payload["error"]["code"] == "bad_report_path"

        status, _, payload = _json_request(server, "GET", "/api/reports/unknown.txt")
        assert status == 404
        assert payload["error"]["code"] == "not_found"

        status, _, payload = _json_request(
            server,
            "POST",
            "/api/reports/readiness_report.html",
            body=b"{}",
            headers={
                "Content-Type": "application/json",
                "Content-Length": "2",
                "Origin": "http://127.0.0.1:{}".format(server.server_address[1]),
            },
            origin=False,
        )
        assert status == 405
        assert payload["error"]["code"] == "method_not_allowed"
    finally:
        _stop_server(server, thread)


def test_report_reader_rejects_symlink_targets(tmp_path):
    reports = tmp_path / "05_REPORTS"
    reports.mkdir()
    secret = tmp_path / "secret.txt"
    secret.write_text("TOP-SECRET", encoding="utf-8")
    (reports / "readiness_report.html").symlink_to(secret)

    with pytest.raises(ValueError, match="regular file"):
        autopilot_proof_lab_server._read_report_bytes(reports, "readiness_report.html")


def test_status_preserves_stale_advisory_contract_after_gate_change(tmp_path):
    workspace = build_workspace(tmp_path)
    server, thread = _start_server(workspace)
    try:
        _post_json(server, "/api/evaluate", {})
        _post_json(
            server,
            "/api/gate",
            {
                "gate": "input_identifiable",
                "status": "pass",
                "owner": "ops-owner",
                "evidence_ids": ["ev-0001"],
                "note": "inputs are fixed",
            },
        )

        status, _, payload = _json_request(server, "GET", "/api/status")
        assert status == 200
        current = payload["data"]["status"]
        assert current["stale"] is True
        assert current["stage"] == "stale_decision"
        assert current["maximum_level"] == "L0"
        assert payload["next_action"] == current["next_action"]
        assert current["advisory_only"] is True
        assert current["external_actions_activated"] is False
        assert current["human_approval_removed"] is False
    finally:
        _stop_server(server, thread)


def test_run_autopilot_proof_lab_server_prints_clean_url_and_respects_no_open(monkeypatch, tmp_path, capsys):
    workspace = build_workspace(tmp_path)
    calls = {"closed": False, "opened": []}

    class FakeServer:
        session_token = "f" * 64
        server_address = ("127.0.0.1", 4312)

        def serve_forever(self):
            raise KeyboardInterrupt

        def server_close(self):
            calls["closed"] = True

    def fake_create(workspace_arg, language="ja", port=0):
        calls["create"] = {"workspace": Path(workspace_arg), "language": language, "port": port}
        return FakeServer()

    monkeypatch.setattr(
        "ai_automation_kit.core.autopilot_proof_lab_server.create_autopilot_proof_lab_server",
        fake_create,
    )
    monkeypatch.setattr(
        "ai_automation_kit.core.autopilot_proof_lab_server.webbrowser.open",
        lambda url: calls["opened"].append(url),
    )

    assert run_autopilot_proof_lab_server(workspace, language="en", port=4312, open_browser=False) == 0

    captured = capsys.readouterr()
    assert captured.out.strip() == "http://127.0.0.1:4312/"
    assert "?token=" not in captured.out
    assert calls["create"] == {"workspace": workspace, "language": "en", "port": 4312}
    assert calls["opened"] == []
    assert calls["closed"] is True
