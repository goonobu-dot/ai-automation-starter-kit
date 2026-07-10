import json
import re
import socket
import threading
import time
from http.client import HTTPConnection
from pathlib import Path

import pytest

from ai_automation_kit.core.report_intake import MAX_FILE_BYTES
from ai_automation_kit.core.report_wizard import load_session
from ai_automation_kit.core.report_wizard_server import (
    MAX_REQUEST_BYTES,
    create_report_wizard_server,
    run_report_wizard_server,
)
from ai_automation_kit.core.report_wizard_ui import render_report_wizard_ui


def _multipart_body(parts, boundary="BOUNDARY"):
    chunks = []
    for part in parts:
        chunks.append("--{}\r\n".format(boundary).encode("utf-8"))
        disposition = 'Content-Disposition: form-data; name="files"; filename="{}"\r\n'.format(part["filename"])
        chunks.append(disposition.encode("utf-8"))
        chunks.append(b"Content-Type: application/octet-stream\r\n\r\n")
        chunks.append(part["content"])
        chunks.append(b"\r\n")
    chunks.append("--{}--\r\n".format(boundary).encode("utf-8"))
    return b"".join(chunks), boundary


def _request(server, method, path, *, body=None, headers=None):
    connection = HTTPConnection(server.server_address[0], server.server_address[1], timeout=5)
    try:
        merged_headers = {"Host": "127.0.0.1:{}".format(server.server_address[1])}
        if headers:
            merged_headers.update(headers)
        connection.request(method, path, body=body, headers=merged_headers)
        response = connection.getresponse()
        payload = response.read()
        return response.status, response.getheaders(), payload
    finally:
        connection.close()


def _json_request(server, method, path, *, token=True, body=None, headers=None):
    merged_headers = {"Accept": "application/json"}
    if token:
        merged_headers["X-Report-Wizard-Token"] = server.session_token
    if headers:
        merged_headers.update(headers)
    status, response_headers, payload = _request(server, method, path, body=body, headers=merged_headers)
    return status, dict(response_headers), json.loads(payload.decode("utf-8"))


def _start_server(workspace, language="ja"):
    server = create_report_wizard_server(workspace, language=language, port=0)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
    thread.start()
    return server, thread


def _stop_server(server, thread):
    server.shutdown()
    thread.join(timeout=5)
    server.server_close()


def _upload(server, role, filename, content):
    body, boundary = _multipart_body([{"filename": filename, "content": content}])
    return _json_request(
        server,
        "POST",
        "/api/upload?role={}".format(role),
        body=body,
        headers={
            "Content-Type": "multipart/form-data; boundary={}".format(boundary),
            "Content-Length": str(len(body)),
            "Origin": "http://127.0.0.1:{}".format(server.server_address[1]),
        },
    )


def _answer_until_ready(server):
    while True:
        _, _, state = _json_request(server, "GET", "/api/state")
        current = state["data"]["state"]["current_question"]
        if not current:
            return
        payload = json.dumps({"answer": "Confirmed {}".format(current["id"]), "skipped": False}).encode("utf-8")
        _json_request(
            server,
            "POST",
            "/api/answer",
            body=payload,
            headers={
                "Content-Type": "application/json",
                "Content-Length": str(len(payload)),
                "Origin": "http://127.0.0.1:{}".format(server.server_address[1]),
            },
        )


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
    return status_code, json.loads(body.decode("utf-8"))


def _multipart_request_bytes(server, role, body, boundary="BOUNDARY"):
    request = (
        "POST /api/upload?role={role} HTTP/1.1\r\n"
        "Host: 127.0.0.1:{port}\r\n"
        "Accept: application/json\r\n"
        "Origin: http://127.0.0.1:{port}\r\n"
        "Content-Type: multipart/form-data; boundary={boundary}\r\n"
        "X-Report-Wizard-Token: {token}\r\n"
        "Content-Length: {length}\r\n"
        "\r\n"
    ).format(
        role=role,
        port=server.server_address[1],
        boundary=boundary,
        token=server.session_token,
        length=len(body),
    ).encode("utf-8")
    return request


def test_create_report_wizard_server_binds_localhost_and_creates_session(tmp_path):
    workspace = tmp_path / "workspace"
    server, thread = _start_server(workspace)
    try:
        assert server.server_address[0] == "127.0.0.1"
        assert server.workspace == workspace.resolve()
        assert len(server.session_token) >= 24
        state = load_session(workspace)
        assert state["stage"] == "created"
        assert state["report_type"] == "monthly"

        status, _, payload = _json_request(server, "GET", "/api/state")
        assert status == 200
        assert payload["ok"] is True
        assert payload["stage"] == "created"
    finally:
        _stop_server(server, thread)


@pytest.mark.parametrize("language", ["fr", ""])
def test_create_report_wizard_server_rejects_invalid_language_before_mutation(tmp_path, language):
    workspace = tmp_path / "workspace"

    with pytest.raises(ValueError, match="language must be 'ja' or 'en'"):
        create_report_wizard_server(workspace, language=language, port=0)

    assert not workspace.exists()


def test_create_report_wizard_server_rejects_existing_invalid_state(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir(parents=True)
    (workspace / "report_wizard_state.json").write_text("{broken", encoding="utf-8")

    with pytest.raises(ValueError, match="invalid JSON"):
        create_report_wizard_server(workspace, language="ja", port=0)


def test_server_rejects_missing_bad_token_host_origin_unknown_method_and_endpoint(tmp_path):
    server, thread = _start_server(tmp_path / "workspace")
    try:
        status, _, payload = _json_request(server, "GET", "/api/state", token=False)
        assert status == 401
        assert payload["ok"] is False

        status, _, payload = _json_request(
            server,
            "GET",
            "/api/state",
            token=False,
            headers={"X-Report-Wizard-Token": "wrong"},
        )
        assert status == 403
        assert payload["error"]["message"]

        status, _, payload = _request(
            server,
            "GET",
            "/api/state",
            headers={
                "Host": "evil.test",
                "X-Report-Wizard-Token": server.session_token,
                "Accept": "application/json",
            },
        )
        host_error = json.loads(payload.decode("utf-8"))
        assert status == 400
        assert host_error["ok"] is False

        post_body = b"{}"
        status, _, payload = _json_request(
            server,
            "POST",
            "/api/build",
            body=post_body,
            headers={
                "Content-Type": "application/json",
                "Content-Length": str(len(post_body)),
                "Origin": "http://evil.test",
            },
        )
        assert status == 403
        assert payload["ok"] is False

        status, _, payload = _json_request(server, "PUT", "/api/state")
        assert status == 405
        assert payload["ok"] is False

        status, _, payload = _json_request(server, "GET", "/api/missing")
        assert status == 404
        assert payload["ok"] is False
    finally:
        _stop_server(server, thread)


def test_server_rejects_content_length_over_limit_without_hanging(tmp_path):
    server, thread = _start_server(tmp_path / "workspace")
    try:
        request = (
            "POST /api/goal HTTP/1.1\r\n"
            "Host: 127.0.0.1:{port}\r\n"
            "Accept: application/json\r\n"
            "Origin: http://127.0.0.1:{port}\r\n"
            "Content-Type: application/json\r\n"
            "X-Report-Wizard-Token: {token}\r\n"
            "Content-Length: {length}\r\n"
            "\r\n"
        ).format(
            port=server.server_address[1],
            token=server.session_token,
            length=MAX_REQUEST_BYTES + 1,
        ).encode("utf-8")
        status, body = _parse_http_json(_raw_http(server, request, close_write=True))

        assert status == 413
        assert body["ok"] is False
        assert "Traceback" not in json.dumps(body)
    finally:
        _stop_server(server, thread)


@pytest.mark.parametrize("content_length", ["broken", "-1"])
def test_server_rejects_malformed_or_negative_content_length(tmp_path, content_length):
    server, thread = _start_server(tmp_path / "workspace")
    try:
        request = (
            "POST /api/goal HTTP/1.1\r\n"
            "Host: 127.0.0.1:{port}\r\n"
            "Accept: application/json\r\n"
            "Origin: http://127.0.0.1:{port}\r\n"
            "Content-Type: application/json\r\n"
            "X-Report-Wizard-Token: {token}\r\n"
            "Content-Length: {length}\r\n"
            "\r\n"
            "{{}}"
        ).format(
            port=server.server_address[1],
            token=server.session_token,
            length=content_length,
        ).encode("utf-8")
        status, body = _parse_http_json(_raw_http(server, request, close_write=True))

        assert status == 400
        assert body["ok"] is False
        assert "Content-Length" in body["error"]["message"]
    finally:
        _stop_server(server, thread)


def test_server_rejects_short_body_when_declared_content_length_is_longer(tmp_path):
    server, thread = _start_server(tmp_path / "workspace")
    try:
        request = (
            "POST /api/goal HTTP/1.1\r\n"
            "Host: 127.0.0.1:{port}\r\n"
            "Accept: application/json\r\n"
            "Origin: http://127.0.0.1:{port}\r\n"
            "Content-Type: application/json\r\n"
            "Connection: close\r\n"
            "X-Report-Wizard-Token: {token}\r\n"
            "Content-Length: 40\r\n"
            "\r\n"
            "{{}}"
        ).format(
            port=server.server_address[1],
            token=server.session_token,
        ).encode("utf-8")
        status, body = _parse_http_json(_raw_http(server, request))

        assert status == 400
        assert body["ok"] is False
        assert "ended early" in body["error"]["message"]
        assert "Traceback" not in json.dumps(body)
    finally:
        _stop_server(server, thread)


def test_slow_upload_completion_serializes_inspect_and_is_included(tmp_path):
    server, thread = _start_server(tmp_path / "workspace")
    try:
        multipart_body, boundary = _multipart_body([{"filename": "past.md", "content": b"# Summary\n"}], boundary="SLOWBOUNDARY")
        request_head = _multipart_request_bytes(server, "past", multipart_body, boundary=boundary)
        split_at = max(1, len(multipart_body) // 2)
        upload_started = threading.Event()
        inspect_done = threading.Event()
        results = {}

        def upload_worker():
            with socket.create_connection(server.server_address, timeout=2) as client:
                client.settimeout(2)
                client.sendall(request_head + multipart_body[:split_at])
                upload_started.set()
                time.sleep(0.25)
                client.sendall(multipart_body[split_at:])
                client.shutdown(socket.SHUT_WR)
                results["upload"] = _parse_http_json(b"".join(iter(lambda: client.recv(65536), b"")))

        def inspect_worker():
            try:
                results["inspect"] = _json_request(
                    server,
                    "POST",
                    "/api/inspect",
                    body=b"{}",
                    headers={
                        "Content-Type": "application/json",
                        "Content-Length": "2",
                        "Origin": "http://127.0.0.1:{}".format(server.server_address[1]),
                    },
                )
            finally:
                inspect_done.set()

        upload_thread = threading.Thread(target=upload_worker)
        inspect_thread = threading.Thread(target=inspect_worker)
        upload_thread.start()
        assert upload_started.wait(timeout=1)
        inspect_thread.start()
        time.sleep(0.1)
        assert inspect_done.is_set() is False
        upload_thread.join(timeout=3)
        inspect_thread.join(timeout=3)

        assert not upload_thread.is_alive()
        assert not inspect_thread.is_alive()
        upload_status, upload_payload = results["upload"]
        inspect_status, _, inspect_payload = results["inspect"]
        assert upload_status == 200
        assert inspect_status == 200
        saved_path = upload_payload["data"]["saved"][0]["path"]
        accepted = inspect_payload["data"]["state"]["accepted"]
        assert any(item["original_path"] == saved_path for item in accepted)
    finally:
        _stop_server(server, thread)


def test_partial_upload_disconnect_releases_lock_and_leaves_no_leftover_before_inspect(tmp_path):
    workspace = tmp_path / "workspace"
    server, thread = _start_server(workspace)
    try:
        multipart_body, boundary = _multipart_body([{"filename": "past.md", "content": b"# Summary\n"}], boundary="BROKENBOUNDARY")
        request_head = _multipart_request_bytes(server, "past", multipart_body, boundary=boundary)
        split_at = max(1, len(multipart_body) // 2)
        upload_started = threading.Event()
        inspect_done = threading.Event()
        results = {}

        def broken_upload_worker():
            with socket.create_connection(server.server_address, timeout=2) as client:
                client.settimeout(2)
                client.sendall(request_head + multipart_body[:split_at])
                upload_started.set()
                time.sleep(0.2)
                client.shutdown(socket.SHUT_WR)
                results["upload"] = _parse_http_json(b"".join(iter(lambda: client.recv(65536), b"")))

        def inspect_worker():
            try:
                results["inspect"] = _json_request(
                    server,
                    "POST",
                    "/api/inspect",
                    body=b"{}",
                    headers={
                        "Content-Type": "application/json",
                        "Content-Length": "2",
                        "Origin": "http://127.0.0.1:{}".format(server.server_address[1]),
                    },
                )
            finally:
                inspect_done.set()

        upload_thread = threading.Thread(target=broken_upload_worker)
        inspect_thread = threading.Thread(target=inspect_worker)
        upload_thread.start()
        assert upload_started.wait(timeout=1)
        inspect_thread.start()
        time.sleep(0.1)
        assert inspect_done.is_set() is False
        upload_thread.join(timeout=3)
        inspect_thread.join(timeout=3)

        assert not upload_thread.is_alive()
        assert not inspect_thread.is_alive()
        upload_status, upload_payload = results["upload"]
        inspect_status, _, inspect_payload = results["inspect"]
        assert upload_status == 400
        assert inspect_status == 200
        assert inspect_payload["data"]["state"]["accepted"] == []
        leftovers = list((workspace / "00_uploads").rglob("*")) if (workspace / "00_uploads").exists() else []
        assert [path for path in leftovers if path.is_file()] == []
        assert upload_payload["ok"] is False
    finally:
        _stop_server(server, thread)


def test_upload_sanitizes_paths_randomizes_names_and_rejects_size_and_extension(tmp_path):
    workspace = tmp_path / "workspace"
    server, thread = _start_server(workspace)
    try:
        status, _, payload = _upload(server, "past", "../../Quarterly report.md", b"# Summary\n")
        assert status == 200
        saved = payload["data"]["saved"][0]
        saved_path = Path(saved["path"])
        assert saved_path.parent == workspace / "00_uploads" / "past"
        assert saved_path.name.endswith("-Quarterly_report.md")
        assert saved_path.name != "Quarterly_report.md"
        assert ".." not in saved_path.name
        assert saved_path.read_text(encoding="utf-8") == "# Summary\n"

        status, _, payload = _upload(server, "current", "evil.sh", b"#!/bin/sh\necho no\n")
        assert status == 400
        assert payload["ok"] is False
        assert "extension" in payload["error"]["message"]

        oversized = b"a" * (MAX_FILE_BYTES + 1)
        status, _, payload = _upload(server, "current", "large.csv", oversized)
        assert status == 413
        assert payload["ok"] is False

        assert all(str(path.resolve()).startswith(str(workspace.resolve())) for path in (workspace / "00_uploads").rglob("*") if path.is_file())
    finally:
        _stop_server(server, thread)


@pytest.mark.parametrize("report_type", ["daily", "weekly", "monthly"])
def test_goal_endpoint_updates_created_session_only_before_inputs(tmp_path, report_type):
    workspace = tmp_path / report_type
    server, thread = _start_server(workspace)
    try:
        payload = json.dumps({"report_type": report_type, "language": "en"}).encode("utf-8")
        status, _, response = _json_request(
            server,
            "POST",
            "/api/goal",
            body=payload,
            headers={
                "Content-Type": "application/json",
                "Content-Length": str(len(payload)),
                "Origin": "http://127.0.0.1:{}".format(server.server_address[1]),
            },
        )
        assert status == 200
        assert response["data"]["state"]["report_type"] == report_type
        assert response["data"]["state"]["language"] == "en"

        _upload(server, "past", "sample.md", b"# Past\n")

        status, _, response = _json_request(
            server,
            "POST",
            "/api/goal",
            body=payload,
            headers={
                "Content-Type": "application/json",
                "Content-Length": str(len(payload)),
                "Origin": "http://127.0.0.1:{}".format(server.server_address[1]),
            },
        )
        assert status == 409
        assert response["ok"] is False
    finally:
        _stop_server(server, thread)


def test_full_http_report_wizard_flow_builds_and_approves(tmp_path):
    workspace = tmp_path / "workspace"
    server, thread = _start_server(workspace, language="en")
    try:
        _upload(server, "past", "past.md", b"# Executive Summary\nRevenue: 100\n")
        _upload(server, "current", "metrics.csv", b"metric,value\nsales,120\n")

        status, _, payload = _json_request(
            server,
            "POST",
            "/api/inspect",
            body=b"{}",
            headers={
                "Content-Type": "application/json",
                "Content-Length": "2",
                "Origin": "http://127.0.0.1:{}".format(server.server_address[1]),
            },
        )
        assert status == 200
        assert payload["stage"] == "inspection_ready"

        status, _, payload = _json_request(
            server,
            "POST",
            "/api/confirm",
            body=b"{}",
            headers={
                "Content-Type": "application/json",
                "Content-Length": "2",
                "Origin": "http://127.0.0.1:{}".format(server.server_address[1]),
            },
        )
        assert status == 200
        assert payload["stage"] == "questioning"
        assert payload["data"]["state"]["current_question"]["id"] == "report_audience"

        _answer_until_ready(server)

        status, _, payload = _json_request(
            server,
            "POST",
            "/api/build",
            body=b"{}",
            headers={
                "Content-Type": "application/json",
                "Content-Length": "2",
                "Origin": "http://127.0.0.1:{}".format(server.server_address[1]),
            },
        )
        assert status == 200
        assert payload["stage"] == "ready_for_human_review"
        assert payload["data"]["state"]["artifacts"]["draft"].endswith("06_drafts/monthly_report_draft.md")

        approve = json.dumps({"approver": "Owner"}).encode("utf-8")
        status, _, payload = _json_request(
            server,
            "POST",
            "/api/approve",
            body=approve,
            headers={
                "Content-Type": "application/json",
                "Content-Length": str(len(approve)),
                "Origin": "http://127.0.0.1:{}".format(server.server_address[1]),
            },
        )
        assert status == 200
        assert payload["stage"] == "approved"
        assert payload["data"]["state"]["approval"]["approver"] == "Owner"
    finally:
        _stop_server(server, thread)


def test_json_errors_stay_actionable_without_traceback_or_token_echo(tmp_path):
    server, thread = _start_server(tmp_path / "workspace")
    try:
        payload = b"{broken"
        status, _, body = _json_request(
            server,
            "POST",
            "/api/goal",
            body=payload,
            headers={
                "Content-Type": "application/json",
                "Content-Length": str(len(payload)),
                "Origin": "http://127.0.0.1:{}".format(server.server_address[1]),
            },
        )
        assert status == 400
        assert body["ok"] is False
        assert "Traceback" not in json.dumps(body)
        assert server.session_token not in json.dumps(body)
    finally:
        _stop_server(server, thread)


def test_render_report_wizard_ui_is_self_contained_localized_and_safe():
    ja = render_report_wizard_ui("ja", "token-ja")
    en = render_report_wizard_ui("en", "token-en")

    assert "レポート種別" in ja
    assert "Report Type" not in ja
    assert "Report Type" in en
    assert "レポート種別" not in en
    assert ja.count('id="question-panel"') == 1
    assert en.count('id="question-panel"') == 1
    assert "innerHTML" not in ja
    assert "innerHTML" not in en
    assert "https://" not in ja and "http://" not in ja
    assert "https://" not in en and "http://" not in en
    assert "X-Report-Wizard-Token" in en
    assert "same-origin" in en
    assert "prefers-reduced-motion" in en
    assert "flowchart" in ja
    assert "<ol" in ja and "<ol" in en


def test_run_report_wizard_server_delegates_and_opens_browser(monkeypatch, tmp_path):
    workspace = tmp_path / "workspace"
    calls = {"closed": False, "opened": []}

    class FakeServer:
        session_token = "session-token"
        server_address = ("127.0.0.1", 4310)

        def serve_forever(self):
            raise KeyboardInterrupt

        def server_close(self):
            calls["closed"] = True

    def fake_create(workspace_arg, language="ja", port=0):
        calls["create"] = {
            "workspace": Path(workspace_arg),
            "language": language,
            "port": port,
        }
        return FakeServer()

    monkeypatch.setattr("ai_automation_kit.core.report_wizard_server.create_report_wizard_server", fake_create)
    monkeypatch.setattr("ai_automation_kit.core.report_wizard_server.webbrowser.open", lambda url: calls["opened"].append(url))

    assert run_report_wizard_server(workspace, language="en", port=4310, open_browser=True) == 0
    assert load_session(workspace)["report_type"] == "monthly"
    assert calls["create"] == {"workspace": workspace, "language": "en", "port": 4310}
    assert calls["closed"] is True
    assert calls["opened"] == ["http://127.0.0.1:4310/?token=session-token"]
