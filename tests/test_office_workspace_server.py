import hashlib
import json
import os
import re
import socket
import threading
import time
from http.client import HTTPConnection
from pathlib import Path

import pytest

from ai_automation_kit.core import office_workspace_server
from ai_automation_kit.core.codex_runner import start_codex_run, wait_for_run
from ai_automation_kit.core.office_workspace_state import (
    _load_period_state,
    _save_period_state,
    _transition_period,
    promote_run_result,
)
from ai_automation_kit.core.office_workspace_server import (
    MAX_REQUEST_BYTES,
    TOKEN_HEADER,
    create_office_workspace_server,
)


RUN_ID = "run-1234567890abcdef1234567890abcdef"


def write_text(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def write_fake_codex(path: Path) -> Path:
    write_text(
        path,
        """#!/usr/bin/env python3
import json
import sys
from pathlib import Path

argv = sys.argv[1:]
if argv[:2] == ["login", "status"]:
    raise SystemExit(0)
if not argv or argv[0] != "exec":
    raise SystemExit(91)
sys.stdin.read()
print(json.dumps({"event": "run.started", "status": "running"}), flush=True)
output_path = Path(argv[argv.index("--output-last-message") + 1])
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(
    json.dumps({"missing_questions": [], "draft_markdown": "# Draft\\nJuly summary\\n"}),
    encoding="utf-8",
)
print(json.dumps({"event": "run.finished", "status": "completed"}), flush=True)
""",
    )
    os.chmod(path, 0o755)
    return path


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


def _json_request(server, method, path, *, token=True, body=None, headers=None):
    merged_headers = {"Accept": "application/json"}
    if token:
        merged_headers[TOKEN_HEADER] = server.session_token
    if headers:
        merged_headers.update(headers)
    status, response_headers, payload = _request(server, method, path, body=body, headers=merged_headers)
    decoded = json.loads(payload.decode("utf-8"))
    _assert_response_contract(decoded)
    return status, response_headers, decoded


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
    _assert_response_contract(payload)
    return status_code, payload


def _assert_response_contract(payload):
    assert set(payload) == {"ok", "data", "next_action", "error"}
    assert isinstance(payload["ok"], bool)
    assert isinstance(payload["data"], dict)
    assert isinstance(payload["next_action"], str)
    assert payload["error"] is None or isinstance(payload["error"], dict)

    def assert_next_actions_are_strings(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key == "next_action":
                    assert isinstance(child, str)
                assert_next_actions_are_strings(child)
        elif isinstance(value, list):
            for child in value:
                assert_next_actions_are_strings(child)

    assert_next_actions_are_strings(payload)


def _start_server(root: Path, monkeypatch):
    monkeypatch.setattr(
        office_workspace_server,
        "codex_preflight",
        lambda executable="codex", timeout_seconds=5: {"ok": True, "code": "ok", "next_action": None},
    )
    server = create_office_workspace_server(root, language="ja", port=0)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
    thread.start()
    return server, thread


def _stop_server(server, thread):
    server.shutdown()
    thread.join(timeout=5)
    server.server_close()


def _action_nonce(payload):
    return payload["data"]["action_nonce"]


def _post_json(server, path, payload, *, origin=True, token=True):
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Content-Length": str(len(body)),
    }
    if origin:
        headers["Origin"] = "http://127.0.0.1:{}".format(server.server_address[1])
    return _json_request(server, "POST", path, token=token, body=body, headers=headers)


def _get_workspaces(server):
    return _json_request(server, "GET", "/api/workspaces")


def _create_workspace(server, *, nonce, name="Monthly", approver="Owner", pin="482913", root_choice="server_root"):
    status, _, payload = _post_json(
        server,
        "/api/workspaces",
        {
            "action_nonce": nonce,
            "name": name,
            "root_choice": root_choice,
            "approver": approver,
            "pin": pin,
        },
    )
    assert status == 200
    assert payload["ok"] is True
    return payload


def _workspace_detail(server, workspace_id):
    return _json_request(server, "GET", "/api/workspaces/{}".format(workspace_id))


def _rollover(server, workspace_id, nonce, next_period_id, style_reference=None):
    return _post_json(
        server,
        "/api/workspaces/{}/rollover".format(workspace_id),
        {
            "action_nonce": nonce,
            "next_period_id": next_period_id,
            "style_reference": style_reference,
        },
    )


def _inspect(server, workspace_id, nonce, period_id):
    return _post_json(
        server,
        "/api/workspaces/{}/inspect".format(workspace_id),
        {"action_nonce": nonce, "period_id": period_id},
    )


def _answer(server, workspace_id, nonce, question_id, answer):
    return _post_json(
        server,
        "/api/workspaces/{}/answer".format(workspace_id),
        {"action_nonce": nonce, "question_id": question_id, "answer": answer},
    )


def _generate(server, workspace_id, nonce, period_id):
    return _post_json(
        server,
        "/api/workspaces/{}/generate".format(workspace_id),
        {"action_nonce": nonce, "period_id": period_id},
    )


def _approve(server, workspace_id, nonce, draft_id, approver, pin):
    return _post_json(
        server,
        "/api/workspaces/{}/approve".format(workspace_id),
        {
            "action_nonce": nonce,
            "draft_id": draft_id,
            "approver": approver,
            "pin": pin,
        },
    )


def _open_folder(server, workspace_id, nonce, role):
    return _post_json(
        server,
        "/api/workspaces/{}/open-folder".format(workspace_id),
        {"action_nonce": nonce, "role": role},
    )


def test_create_office_workspace_server_binds_localhost_and_lists_workspaces(tmp_path, monkeypatch):
    server, thread = _start_server(tmp_path / "workspaces", monkeypatch)
    try:
        assert server.server_address[0] == "127.0.0.1"
        assert server.root == (tmp_path / "workspaces").resolve()
        assert re.fullmatch(r"[0-9a-f]{64}", server.session_token)

        status, headers, payload = _get_workspaces(server)

        assert status == 200
        assert headers["Cache-Control"] == "no-store"
        assert payload == {
            "ok": True,
            "data": payload["data"],
            "next_action": "Create a monthly workspace to begin.",
            "error": None,
        }
        assert payload["data"]["workspaces"] == []
        assert payload["data"]["preflight"]["ok"] is True
        assert payload["data"]["root_choices"] == [
            {"id": "server_root", "path": str((tmp_path / "workspaces").resolve())}
        ]
        assert re.fullmatch(r"[0-9a-f]{64}", _action_nonce(payload))
    finally:
        _stop_server(server, thread)


def test_workspace_list_includes_bounded_latest_persisted_run_for_current_period(tmp_path, monkeypatch):
    server, thread = _start_server(tmp_path / "workspaces", monkeypatch)
    try:
        _, _, listed = _get_workspaces(server)
        created = _create_workspace(server, nonce=_action_nonce(listed))
        workspace = created["data"]["workspace"]
        workspace_id = workspace["id"]
        workspace_root = Path(workspace["root"])
        _, _, period = _rollover(server, workspace_id, _action_nonce(created), "2026-07")

        run_root = workspace_root / ".system" / "runs" / RUN_ID
        write_text(
            run_root / "run.json",
            json.dumps(
                {
                    "run_id": RUN_ID,
                    "period_id": "2026-07",
                    "status": "ready_for_review",
                    "started_at": "2026-07-11T01:02:03Z",
                    "finished_at": "2026-07-11T01:02:04Z",
                    "prompt": "must not leave the server",
                    "sandbox": "/private/internal/path",
                }
            ),
        )

        status, _, payload = _get_workspaces(server)

        assert status == 200
        summary = next(item for item in payload["data"]["workspaces"] if item["id"] == workspace_id)
        assert summary["run"] == {
            "run_id": RUN_ID,
            "status": "ready_for_review",
            "started_at": "2026-07-11T01:02:03Z",
            "finished_at": "2026-07-11T01:02:04Z",
        }
        assert "prompt" not in summary["run"]
        assert "sandbox" not in summary["run"]
        assert _action_nonce(period)
    finally:
        _stop_server(server, thread)


@pytest.mark.parametrize("language", ["fr", ""])
def test_create_office_workspace_server_rejects_invalid_language_before_mutation(tmp_path, language):
    root = tmp_path / "workspaces"

    with pytest.raises(ValueError, match="language must be 'ja' or 'en'"):
        create_office_workspace_server(root, language=language, port=0)

    assert not root.exists()


def test_server_rejects_missing_bad_token_host_origin_method_endpoint_and_nonce_reuse(tmp_path, monkeypatch):
    server, thread = _start_server(tmp_path / "workspaces", monkeypatch)
    try:
        status, _, payload = _json_request(server, "GET", "/api/workspaces", token=False)
        assert status == 401
        assert payload["ok"] is False
        assert payload["error"]["code"] == "missing_token"

        status, _, payload = _json_request(
            server,
            "GET",
            "/api/workspaces",
            token=False,
            headers={TOKEN_HEADER: "bad"},
        )
        assert status == 403
        assert payload["error"]["code"] == "bad_token"

        status, _, payload = _request(
            server,
            "GET",
            "/api/workspaces",
            headers={
                "Accept": "application/json",
                TOKEN_HEADER: server.session_token,
                "Host": "evil.test",
            },
        )
        decoded = json.loads(payload.decode("utf-8"))
        _assert_response_contract(decoded)
        assert status == 400
        assert decoded["error"]["code"] == "host_not_allowed"

        status, _, payload = _post_json(
            server,
            "/api/workspaces",
            {
                "action_nonce": _action_nonce(_get_workspaces(server)[2]),
                "name": "Monthly",
                "root_choice": "server_root",
                "approver": "Owner",
                "pin": "482913",
            },
            origin=False,
        )
        assert status == 403
        assert payload["error"]["code"] == "origin_not_allowed"

        status, _, payload = _json_request(server, "PUT", "/api/workspaces")
        assert status == 405
        assert payload["error"]["code"] == "method_not_allowed"

        status, _, payload = _json_request(server, "GET", "/api/missing")
        assert status == 404
        assert payload["error"]["code"] == "not_found"

        _, _, listed = _get_workspaces(server)
        first_nonce = _action_nonce(listed)
        created = _create_workspace(server, nonce=first_nonce)
        reused = _post_json(
            server,
            "/api/workspaces",
            {
                "action_nonce": first_nonce,
                "name": "Another",
                "root_choice": "server_root",
                "approver": "Owner",
                "pin": "482913",
            },
        )[2]
        assert created["ok"] is True
        assert reused["ok"] is False
        assert reused["error"]["code"] == "bad_action_nonce"
    finally:
        _stop_server(server, thread)


def test_server_rejects_malicious_origin_before_business_handler(tmp_path, monkeypatch):
    server, thread = _start_server(tmp_path / "workspaces", monkeypatch)
    calls = {"create": 0}

    def fail_if_called(*args, **kwargs):
        calls["create"] += 1
        raise AssertionError("business handler must not run for an untrusted Origin")

    monkeypatch.setattr(office_workspace_server, "create_office_workspace", fail_if_called)
    try:
        _, _, listed = _get_workspaces(server)
        body = {
            "action_nonce": _action_nonce(listed),
            "name": "Monthly",
            "root_choice": "server_root",
            "approver": "Owner",
            "pin": "482913",
        }
        encoded = json.dumps(body).encode("utf-8")

        status, _, payload = _json_request(
            server,
            "POST",
            "/api/workspaces",
            body=encoded,
            headers={
                "Content-Type": "application/json",
                "Content-Length": str(len(encoded)),
                "Origin": "http://evil.test",
            },
        )

        assert status == 403
        assert payload["error"]["code"] == "origin_not_allowed"
        assert calls == {"create": 0}
    finally:
        _stop_server(server, thread)


def test_server_rejects_non_loopback_client_before_business_handler(tmp_path, monkeypatch):
    calls = {"preflight": 0}

    def fail_if_called(*args, **kwargs):
        calls["preflight"] += 1
        raise AssertionError("business handler must not run for a remote client")

    monkeypatch.setattr(office_workspace_server, "codex_preflight", fail_if_called)
    server = create_office_workspace_server(tmp_path / "workspaces", language="ja", port=0)
    server_side, client_side = socket.socketpair()
    try:
        request = (
            "GET /api/workspaces HTTP/1.1\r\n"
            "Host: 127.0.0.1:{port}\r\n"
            "Accept: application/json\r\n"
            "{token_header}: {token}\r\n"
            "Connection: close\r\n"
            "\r\n"
        ).format(
            port=server.server_address[1],
            token_header=TOKEN_HEADER,
            token=server.session_token,
        ).encode("utf-8")
        client_side.sendall(request)
        client_side.shutdown(socket.SHUT_WR)

        server.RequestHandlerClass(server_side, ("203.0.113.7", 49152), server)
        server_side.shutdown(socket.SHUT_WR)
        response = b""
        while True:
            chunk = client_side.recv(65536)
            if not chunk:
                break
            response += chunk

        status, payload = _parse_http_json(response)
        assert status == 403
        assert payload["error"]["code"] == "loopback_only"
        assert calls == {"preflight": 0}
        assert server.server_address[0] == "127.0.0.1"
    finally:
        server_side.close()
        client_side.close()
        server.server_close()


def test_server_rejects_oversized_malformed_short_and_non_object_json_bodies(tmp_path, monkeypatch):
    server, thread = _start_server(tmp_path / "workspaces", monkeypatch)
    try:
        request = (
            "POST /api/workspaces HTTP/1.1\r\n"
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
        assert "Traceback" not in json.dumps(payload)

        request = (
            "POST /api/workspaces HTTP/1.1\r\n"
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

        request = (
            "POST /api/workspaces HTTP/1.1\r\n"
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

        _, _, listed = _get_workspaces(server)
        nonce = _action_nonce(listed)
        body = b"{broken"
        status, _, payload = _json_request(
            server,
            "POST",
            "/api/workspaces",
            body=body,
            headers={
                "Content-Type": "application/json",
                "Content-Length": str(len(body)),
                "Origin": "http://127.0.0.1:{}".format(server.server_address[1]),
                TOKEN_HEADER: server.session_token,
            },
        )
        assert status == 400
        assert payload["error"]["code"] == "bad_json"

        body = json.dumps(["not", "an", "object"]).encode("utf-8")
        status, _, payload = _json_request(
            server,
            "POST",
            "/api/workspaces",
            body=body,
            headers={
                "Content-Type": "application/json",
                "Content-Length": str(len(body)),
                "Origin": "http://127.0.0.1:{}".format(server.server_address[1]),
                TOKEN_HEADER: server.session_token,
            },
        )
        assert status == 400
        assert payload["error"]["code"] == "bad_json"
        assert payload["data"]["action_nonce"] != nonce
    finally:
        _stop_server(server, thread)


def test_create_and_detail_use_opaque_server_mapped_workspace_ids(tmp_path, monkeypatch):
    server, thread = _start_server(tmp_path / "workspaces", monkeypatch)
    try:
        _, _, listed = _get_workspaces(server)
        created = _create_workspace(server, nonce=_action_nonce(listed), name="Okinawa Monthly")
        workspace = created["data"]["workspace"]
        internal_id = json.loads((Path(workspace["root"]) / ".system" / "workspace.json").read_text(encoding="utf-8"))[
            "workspace_id"
        ]

        assert workspace["id"] != internal_id
        assert workspace["id"] not in workspace["root"]

        status, _, payload = _workspace_detail(server, workspace["id"])
        assert status == 200
        assert payload["data"]["workspace"]["id"] == workspace["id"]
        assert payload["data"]["workspace"]["name"] == "Okinawa Monthly"
        assert payload["data"]["workspace"]["current_period"] is None
        assert payload["data"]["workspace"]["period"] is None
        assert payload["data"]["workspace"]["run"] is None
        assert payload["data"]["workspace"]["folders"]["approved_past_outputs"]["path"].endswith(
            "01_APPROVED_PAST_OUTPUTS"
        )
    finally:
        _stop_server(server, thread)


def test_validation_rejects_unknown_workspace_and_bad_period_question_run_draft_and_role_values(tmp_path, monkeypatch):
    server, thread = _start_server(tmp_path / "workspaces", monkeypatch)
    try:
        _, _, listed = _get_workspaces(server)
        created = _create_workspace(server, nonce=_action_nonce(listed))
        workspace_id = created["data"]["workspace"]["id"]
        nonce = _action_nonce(created)

        status, _, payload = _workspace_detail(server, "ws-0123456789abcdef0123456789abcdef")
        assert status == 404
        assert payload["error"]["code"] == "workspace_not_found"

        status, _, payload = _inspect(server, workspace_id, nonce, "2026-7")
        assert status == 400
        assert payload["error"]["code"] == "bad_period_id"
        nonce = _action_nonce(payload)

        status, _, payload = _answer(server, workspace_id, nonce, "../audience", "Owner team")
        assert status == 400
        assert payload["error"]["code"] == "bad_question_id"
        nonce = _action_nonce(payload)

        status, _, payload = _post_json(
            server,
            "/api/workspaces/{}/cancel".format(workspace_id),
            {"action_nonce": nonce, "run_id": "bad-run-id"},
        )
        assert status == 400
        assert payload["error"]["code"] == "bad_run_id"
        nonce = _action_nonce(payload)

        status, _, payload = _approve(server, workspace_id, nonce, "../draft.md", "Owner", "482913")
        assert status == 400
        assert payload["error"]["code"] == "bad_draft_id"
        nonce = _action_nonce(payload)

        status, _, payload = _open_folder(server, workspace_id, nonce, "../../evil")
        assert status == 400
        assert payload["error"]["code"] == "bad_folder_role"
    finally:
        _stop_server(server, thread)


def test_successful_monthly_http_flow_rolls_over_inspects_answers_generates_opens_and_approves(tmp_path, monkeypatch):
    server, thread = _start_server(tmp_path / "workspaces", monkeypatch)
    opened = {}

    def fake_start_codex_run(workspace, period_id, *, executable="codex", timeout_seconds=900):
        promote_run_result(
            workspace,
            period_id,
            RUN_ID,
            {"missing_questions": [], "draft_markdown": "# Draft\nJuly summary\n"},
        )
        return {"run_id": RUN_ID, "status": "ready_for_review"}

    def fake_run(argv, **kwargs):
        opened["argv"] = list(argv)
        opened["kwargs"] = dict(kwargs)
        return type("Completed", (), {"returncode": 0})()

    monkeypatch.setattr(office_workspace_server, "start_codex_run", fake_start_codex_run)
    monkeypatch.setattr(office_workspace_server.subprocess, "run", fake_run)
    try:
        _, _, listed = _get_workspaces(server)
        created = _create_workspace(server, nonce=_action_nonce(listed), name="Client Monthly")
        workspace = created["data"]["workspace"]
        workspace_id = workspace["id"]
        workspace_root = Path(workspace["root"])

        status, _, payload = _rollover(server, workspace_id, _action_nonce(created), "2026-07")
        assert status == 200
        assert payload["data"]["workspace"]["current_period"] == "2026-07"

        write_text(workspace_root / "01_APPROVED_PAST_OUTPUTS" / "approved.md", "# Past\n売上: 100\n")
        write_text(workspace_root / "03_CURRENT_INPUTS" / "2026-07" / "current.md", "# Current\n売上: 120\n")

        status, _, payload = _inspect(server, workspace_id, _action_nonce(payload), "2026-07")
        assert status == 200
        assert payload["data"]["workspace"]["period"]["stage"] == "questioning"
        assert payload["data"]["workspace"]["period"]["pending_question_ids"] == ["audience"]

        status, _, payload = _answer(server, workspace_id, _action_nonce(payload), "audience", "Owner team")
        assert status == 200
        assert payload["data"]["workspace"]["period"]["stage"] == "ready_for_run"

        status, _, payload = _generate(server, workspace_id, _action_nonce(payload), "2026-07")
        assert status == 200
        assert payload["data"]["run"]["run_id"] == RUN_ID
        assert payload["data"]["workspace"]["period"]["stage"] == "ready_for_review"
        assert payload["data"]["workspace"]["period"]["current_draft"]["name"] == "monthly_report.md"

        status, _, payload = _open_folder(server, workspace_id, _action_nonce(payload), "current_inputs")
        assert status == 200
        assert opened["argv"][0] in {"open", "xdg-open"}
        assert opened["argv"][1].endswith("/03_CURRENT_INPUTS/2026-07")
        assert opened["kwargs"]["shell"] is False
        assert payload["data"]["opened"]["role"] == "current_inputs"

        status, _, payload = _approve(
            server,
            workspace_id,
            _action_nonce(payload),
            "monthly_report.md",
            "Owner",
            "482913",
        )
        assert status == 200
        assert payload["data"]["workspace"]["period"]["stage"] == "approved"
        assert len(payload["data"]["workspace"]["period"]["approved_outputs"]) == 1

        status, _, payload = _rollover(server, workspace_id, _action_nonce(payload), "2026-08")
        assert status == 200
        assert payload["data"]["workspace"]["current_period"] == "2026-08"
        assert payload["data"]["workspace"]["periods"] == ["2026-07", "2026-08"]

        status, _, payload = _workspace_detail(server, workspace_id)
        assert status == 200
        assert payload["data"]["workspace"]["current_period"] == "2026-08"
        assert (workspace_root / "06_APPROVED_OUTPUTS" / "2026-07" / "monthly_report.md").exists()
    finally:
        _stop_server(server, thread)


def test_wrong_pin_and_invalid_transition_do_not_leak_details_or_mutate_state(tmp_path, monkeypatch):
    server, thread = _start_server(tmp_path / "workspaces", monkeypatch)

    def fake_start_codex_run(workspace, period_id, *, executable="codex", timeout_seconds=900):
        promote_run_result(
            workspace,
            period_id,
            RUN_ID,
            {"missing_questions": [], "draft_markdown": "# Draft\nJuly summary\n"},
        )
        return {"run_id": RUN_ID, "status": "ready_for_review"}

    monkeypatch.setattr(office_workspace_server, "start_codex_run", fake_start_codex_run)
    try:
        _, _, listed = _get_workspaces(server)
        created = _create_workspace(server, nonce=_action_nonce(listed))
        workspace = created["data"]["workspace"]
        workspace_id = workspace["id"]
        workspace_root = Path(workspace["root"])

        status, _, payload = _rollover(server, workspace_id, _action_nonce(created), "2026-07")
        assert status == 200
        nonce = _action_nonce(payload)

        status, _, payload = _generate(server, workspace_id, nonce, "2026-07")
        assert status == 409
        assert payload["error"]["code"] == "state_conflict"
        assert payload["error"]["message"] == "requested action is not allowed in the current workspace state"
        assert "ready_for_run" not in json.dumps(payload)

        write_text(workspace_root / "01_APPROVED_PAST_OUTPUTS" / "approved.md", "# Past\n売上: 100\n")
        write_text(workspace_root / "03_CURRENT_INPUTS" / "2026-07" / "current.md", "# Current\n売上: 120\n")
        status, _, payload = _inspect(server, workspace_id, _action_nonce(payload), "2026-07")
        status, _, payload = _answer(server, workspace_id, _action_nonce(payload), "audience", "Owner team")
        status, _, payload = _generate(server, workspace_id, _action_nonce(payload), "2026-07")
        assert status == 200

        status, _, payload = _approve(
            server,
            workspace_id,
            _action_nonce(payload),
            "monthly_report.md",
            "Owner",
            "000000",
        )
        assert status == 403
        assert payload["error"]["code"] == "approval_denied"
        assert payload["error"]["message"] == "approval credentials are invalid"
        assert "PIN verification failed" not in json.dumps(payload)
        assert not (workspace_root / "07_AUDIT" / "audit.jsonl").exists()

        detail = _workspace_detail(server, workspace_id)[2]
        assert detail["data"]["workspace"]["period"]["stage"] == "ready_for_review"
        assert detail["data"]["workspace"]["period"]["approved_outputs"] == []
    finally:
        _stop_server(server, thread)


def test_cancel_after_persisted_completed_run_is_idempotent_and_preserves_artifacts(tmp_path, monkeypatch):
    server, thread = _start_server(tmp_path / "workspaces", monkeypatch)
    fake_codex = write_fake_codex(tmp_path / "fake_codex.py")

    def start_with_fake_codex(workspace, period_id, *, executable="codex", timeout_seconds=900):
        return start_codex_run(workspace, period_id, executable=str(fake_codex), timeout_seconds=timeout_seconds)

    monkeypatch.setattr(office_workspace_server, "start_codex_run", start_with_fake_codex)
    try:
        _, _, listed = _get_workspaces(server)
        created = _create_workspace(server, nonce=_action_nonce(listed))
        workspace = created["data"]["workspace"]
        workspace_id = workspace["id"]
        workspace_root = Path(workspace["root"])

        _, _, payload = _rollover(server, workspace_id, _action_nonce(created), "2026-07")
        write_text(workspace_root / "01_APPROVED_PAST_OUTPUTS" / "approved.md", "# Past\n売上: 100\n")
        write_text(workspace_root / "03_CURRENT_INPUTS" / "2026-07" / "current.md", "# Current\n売上: 120\n")
        _, _, payload = _inspect(server, workspace_id, _action_nonce(payload), "2026-07")
        _, _, payload = _answer(server, workspace_id, _action_nonce(payload), "audience", "Owner team")
        status, _, payload = _generate(server, workspace_id, _action_nonce(payload), "2026-07")
        assert status == 200
        run_id = payload["data"]["run"]["run_id"]
        completed = wait_for_run(workspace_root, run_id, timeout_seconds=5)
        assert completed["status"] == "ready_for_review"
        persisted_run = json.loads(
            (workspace_root / ".system" / "runs" / run_id / "run.json").read_text(encoding="utf-8")
        )
        assert persisted_run["status"] == "ready_for_review"

        period_before = _load_period_state(workspace_root, "2026-07")
        draft_path = workspace_root / period_before["current_draft"]["path"]
        draft_bytes_before = draft_path.read_bytes()
        draft_hash_before = period_before["current_draft"]["sha256"]
        assert hashlib.sha256(draft_bytes_before).hexdigest() == draft_hash_before
        approved_root = workspace_root / "06_APPROVED_OUTPUTS" / "2026-07"
        approved_before = sorted(
            (path.relative_to(approved_root).as_posix(), path.read_bytes())
            for path in approved_root.rglob("*")
            if path.is_file()
        )
        audit_path = workspace_root / "07_AUDIT" / "audit.jsonl"
        audit_before = audit_path.read_bytes() if audit_path.exists() else None

        status, _, payload = _post_json(
            server,
            "/api/workspaces/{}/cancel".format(workspace_id),
            {"action_nonce": _action_nonce(payload), "run_id": run_id},
        )

        assert status == 200
        assert payload["data"]["run"]["status"] == "ready_for_review"
        assert payload["data"]["workspace"]["period"]["stage"] == "ready_for_review"
        period_after = _load_period_state(workspace_root, "2026-07")
        assert period_after == period_before
        assert draft_path.read_bytes() == draft_bytes_before
        assert period_after["current_draft"]["sha256"] == draft_hash_before
        assert hashlib.sha256(draft_path.read_bytes()).hexdigest() == draft_hash_before
        assert sorted(
            (path.relative_to(approved_root).as_posix(), path.read_bytes())
            for path in approved_root.rglob("*")
            if path.is_file()
        ) == approved_before
        assert (audit_path.read_bytes() if audit_path.exists() else None) == audit_before
    finally:
        _stop_server(server, thread)


def test_approve_before_review_returns_conflict_without_output_or_audit_mutation(tmp_path, monkeypatch):
    server, thread = _start_server(tmp_path / "workspaces", monkeypatch)
    try:
        _, _, listed = _get_workspaces(server)
        created = _create_workspace(server, nonce=_action_nonce(listed))
        workspace = created["data"]["workspace"]
        workspace_id = workspace["id"]
        workspace_root = Path(workspace["root"])
        status, _, payload = _rollover(server, workspace_id, _action_nonce(created), "2026-07")
        assert status == 200
        write_text(workspace_root / "05_DRAFTS" / "2026-07" / "monthly_report.md", "# Unreviewed\n")
        before = _load_period_state(workspace_root, "2026-07")

        status, _, payload = _approve(
            server,
            workspace_id,
            _action_nonce(payload),
            "monthly_report.md",
            "Owner",
            "482913",
        )

        assert status == 409
        assert payload["error"]["code"] == "state_conflict"
        assert _load_period_state(workspace_root, "2026-07") == before
        assert list((workspace_root / "06_APPROVED_OUTPUTS" / "2026-07").iterdir()) == []
        assert not (workspace_root / "07_AUDIT" / "audit.jsonl").exists()
    finally:
        _stop_server(server, thread)


def test_generate_is_serialized_and_second_request_is_rejected_while_first_run_is_active(tmp_path, monkeypatch):
    server, thread = _start_server(tmp_path / "workspaces", monkeypatch)
    first_started = threading.Event()
    release_first = threading.Event()
    calls = {"count": 0}

    def fake_start_codex_run(workspace, period_id, *, executable="codex", timeout_seconds=900):
        calls["count"] += 1
        period_state = _load_period_state(workspace, period_id)
        if period_state["stage"] == "ready_for_run":
            _transition_period(period_state, "running")
            _save_period_state(workspace, period_state)
        first_started.set()
        release_first.wait(timeout=5)
        return {"run_id": RUN_ID, "status": "running"}

    monkeypatch.setattr(office_workspace_server, "start_codex_run", fake_start_codex_run)
    try:
        _, _, listed = _get_workspaces(server)
        created = _create_workspace(server, nonce=_action_nonce(listed))
        workspace = created["data"]["workspace"]
        workspace_id = workspace["id"]
        workspace_root = Path(workspace["root"])

        status, _, payload = _rollover(server, workspace_id, _action_nonce(created), "2026-07")
        write_text(workspace_root / "01_APPROVED_PAST_OUTPUTS" / "approved.md", "# Past\n売上: 100\n")
        write_text(workspace_root / "03_CURRENT_INPUTS" / "2026-07" / "current.md", "# Current\n売上: 120\n")
        status, _, payload = _inspect(server, workspace_id, _action_nonce(payload), "2026-07")
        status, _, payload = _answer(server, workspace_id, _action_nonce(payload), "audience", "Owner team")

        first_nonce = _action_nonce(payload)
        second_nonce = _workspace_detail(server, workspace_id)[2]["data"]["action_nonce"]
        results = {}

        def first_generate():
            results["first"] = _generate(server, workspace_id, first_nonce, "2026-07")

        def second_generate():
            results["second"] = _generate(server, workspace_id, second_nonce, "2026-07")

        first_thread = threading.Thread(target=first_generate)
        second_thread = threading.Thread(target=second_generate)
        first_thread.start()
        assert first_started.wait(timeout=2)
        second_thread.start()
        time.sleep(0.1)
        assert second_thread.is_alive() is True
        release_first.set()
        first_thread.join(timeout=5)
        second_thread.join(timeout=5)

        assert not first_thread.is_alive()
        assert not second_thread.is_alive()
        assert calls["count"] == 1
        assert results["first"][0] == 200
        assert results["first"][2]["data"]["run"]["status"] == "running"
        assert results["second"][0] == 409
        assert results["second"][2]["error"]["code"] == "state_conflict"
    finally:
        _stop_server(server, thread)
