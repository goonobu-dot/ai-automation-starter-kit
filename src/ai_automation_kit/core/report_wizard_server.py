"""Localhost-only HTTP server for the report wizard."""

from __future__ import annotations

import cgi
import io
import json
import os
import secrets
import socket
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlsplit

from ai_automation_kit.core.report_intake import MAX_FILE_BYTES
from ai_automation_kit.core.report_intake import SCRIPT_EXTENSIONS
from ai_automation_kit.core.report_wizard import build_report_workspace
from ai_automation_kit.core.report_wizard import confirm_folder_plan
from ai_automation_kit.core.report_wizard import create_session
from ai_automation_kit.core.report_wizard import inspect_session
from ai_automation_kit.core.report_wizard import load_session
from ai_automation_kit.core.report_wizard import session_status
from ai_automation_kit.core.report_wizard import set_session_goal
from ai_automation_kit.core.report_wizard import answer_current_question
from ai_automation_kit.core.report_wizard import approve_report
from ai_automation_kit.core.report_wizard import STATE_FILENAME
from ai_automation_kit.core.report_wizard_ui import render_report_wizard_ui


MAX_REQUEST_BYTES = 12 * 1024 * 1024
TOKEN_HEADER = "X-Report-Wizard-Token"
UPLOAD_PREFIX_BYTES = 6
READ_TIMEOUT_SECONDS = 1.0


class ReportWizardHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def _workspace_path(workspace: Path) -> Path:
    return Path(workspace).expanduser().resolve(strict=False)


def _ensure_session(workspace: Path, language: str) -> Dict:
    workspace = _workspace_path(workspace)
    if not (workspace / STATE_FILENAME).exists():
        return create_session(workspace, "monthly", language)
    return load_session(workspace)


def _validate_server_language(language: str) -> str:
    if language not in {"ja", "en"}:
        raise ValueError("language must be 'ja' or 'en'")
    return language


def _allowed_hosts(server: ReportWizardHTTPServer) -> set:
    port = server.server_address[1]
    return {"127.0.0.1:{}".format(port), "localhost:{}".format(port)}


def _server_origin(server: ReportWizardHTTPServer) -> str:
    return "http://127.0.0.1:{}".format(server.server_address[1])


def _upload_dir(workspace: Path, role: str) -> Path:
    return _workspace_path(workspace) / "00_uploads" / role


def _sanitize_filename(filename: str) -> str:
    raw_name = Path(filename or "file").name
    stem = Path(raw_name).stem or "file"
    suffix = Path(raw_name).suffix
    safe_stem = "".join(ch if ch.isalnum() or ch in {"-", "_", "."} else "_" for ch in stem).strip("._") or "file"
    safe_suffix = "".join(ch if ch.isalnum() or ch in {"."} else "" for ch in suffix.lower())
    return safe_stem + safe_suffix


def _validate_uploaded_filename(filename: str) -> str:
    sanitized = _sanitize_filename(filename)
    suffix = Path(sanitized).suffix.lower()
    if suffix in SCRIPT_EXTENSIONS:
        raise ValueError("upload extension is not allowed")
    return sanitized


def _staged_upload_paths(workspace: Path) -> Dict[str, List[Path]]:
    uploads = {"past": [], "current": []}
    for role in uploads:
        directory = _upload_dir(workspace, role)
        if not directory.exists():
            continue
        uploads[role] = sorted(path for path in directory.iterdir() if path.is_file())
    return uploads


def _staged_upload_payload(workspace: Path) -> Dict[str, List[Dict]]:
    payload = {"past": [], "current": []}
    for role, paths in _staged_upload_paths(workspace).items():
        for path in paths:
            payload[role].append({"name": path.name, "path": str(path), "bytes": path.stat().st_size})
    return payload


def _save_uploaded_files(workspace: Path, role: str, parts: List[Tuple[str, bytes]]) -> List[Dict]:
    directory = _upload_dir(workspace, role)
    directory.mkdir(parents=True, exist_ok=True)
    saved = []
    for filename, content in parts:
        sanitized = _validate_uploaded_filename(filename)
        if len(content) > MAX_FILE_BYTES:
            raise OverflowError("uploaded file exceeds the 10 MiB intake limit")
        final_path = None
        for _ in range(32):
            candidate = "{}-{}".format(secrets.token_hex(UPLOAD_PREFIX_BYTES), sanitized)
            path = directory / candidate
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
            descriptor = None
            try:
                descriptor = os.open(str(path), flags, 0o600)
                with os.fdopen(descriptor, "wb") as handle:
                    descriptor = None
                    handle.write(content)
                    handle.flush()
                    os.fsync(handle.fileno())
                final_path = path
                break
            except FileExistsError:
                continue
            finally:
                if descriptor is not None:
                    os.close(descriptor)
        if final_path is None:
            raise ValueError("could not allocate a unique upload filename")
        saved.append({"name": final_path.name, "path": str(final_path), "bytes": len(content), "role": role})
    return saved


def _read_json(body: bytes) -> Dict:
    if not body:
        return {}
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("request body must be valid UTF-8 JSON") from error
    if not isinstance(payload, dict):
        raise ValueError("request body must be a JSON object")
    return payload


def _response_payload(state: Optional[Dict], data: Optional[Dict] = None) -> Dict:
    return {
        "ok": True,
        "stage": state.get("stage") if state else None,
        "next_action": state.get("next_action") if state else "",
        "data": data or {},
    }


def _error_payload(message: str, state: Optional[Dict] = None, code: str = "request_error") -> Dict:
    return {
        "ok": False,
        "stage": state.get("stage") if state else None,
        "next_action": state.get("next_action") if state else "",
        "error": {"code": code, "message": message},
    }


def _status_error_code(message: str, default: int = 400) -> int:
    if "only allowed" in message or "requires" in message:
        return 409
    if "unresolved" in message:
        return 409
    return default


def create_report_wizard_server(workspace: Path, language: str = "ja", port: int = 0) -> ThreadingHTTPServer:
    language = _validate_server_language(language)
    workspace = _workspace_path(workspace)
    _ensure_session(workspace, language)

    class Handler(BaseHTTPRequestHandler):
        server_version = "ReportWizard/1.0"
        sys_version = ""

        def log_message(self, format, *args):  # noqa: A003
            return

        def setup(self):
            super().setup()
            self.connection.settimeout(READ_TIMEOUT_SECONDS)

        def do_GET(self):
            self._dispatch("GET")

        def do_POST(self):
            self._dispatch("POST")

        def do_PUT(self):
            self._json_error(405, "unsupported method for this endpoint", code="method_not_allowed")

        def do_DELETE(self):
            self._json_error(405, "unsupported method for this endpoint", code="method_not_allowed")

        def do_PATCH(self):
            self._json_error(405, "unsupported method for this endpoint", code="method_not_allowed")

        def do_OPTIONS(self):
            self._json_error(405, "unsupported method for this endpoint", code="method_not_allowed")

        def _dispatch(self, method: str) -> None:
            try:
                self._reject_untrusted_client()
                self._reject_untrusted_host()
                if method == "POST":
                    self._reject_bad_origin()
                if self.path == "/" or self.path.startswith("/?"):
                    if method != "GET":
                        self._json_error(405, "unsupported method for this endpoint", code="method_not_allowed")
                        return
                    self._require_token()
                    self._serve_root()
                    return

                path = self._parsed_url.path
                if path == "/api/state":
                    if method != "GET":
                        self._json_error(405, "unsupported method for this endpoint", code="method_not_allowed")
                        return
                    self._require_token()
                    self._serve_state()
                    return
                if path == "/api/goal":
                    self._require_token()
                    self._serve_goal()
                    return
                if path == "/api/upload":
                    self._require_token()
                    self._serve_upload()
                    return
                if path == "/api/inspect":
                    self._require_token()
                    self._serve_inspect()
                    return
                if path == "/api/confirm":
                    self._require_token()
                    self._serve_confirm()
                    return
                if path == "/api/answer":
                    self._require_token()
                    self._serve_answer()
                    return
                if path == "/api/build":
                    self._require_token()
                    self._serve_build()
                    return
                if path == "/api/approve":
                    self._require_token()
                    self._serve_approve()
                    return
                self._json_error(404, "unknown endpoint", code="not_found")
            except _RequestError as error:
                self._json_error(error.status, error.message, code=error.code)
            except OverflowError as error:
                self._json_error(413, str(error), code="request_too_large")
            except ValueError as error:
                state = self._safe_state()
                self._json_error(_status_error_code(str(error)), str(error), state=state)

        @property
        def _parsed_url(self):
            return urlsplit(self.path)

        def _safe_state(self) -> Optional[Dict]:
            try:
                return load_session(self.server.workspace)
            except ValueError:
                return None

        def _reject_untrusted_client(self) -> None:
            if self.client_address[0] not in {"127.0.0.1", "::1"}:
                raise _RequestError(403, "only loopback clients may use this server", "loopback_only")

        def _reject_untrusted_host(self) -> None:
            host = self.headers.get("Host", "")
            if host not in _allowed_hosts(self.server):
                raise _RequestError(400, "untrusted Host header", "host_not_allowed")

        def _reject_bad_origin(self) -> None:
            origin = self.headers.get("Origin")
            if not origin:
                return
            parsed = urlsplit(origin)
            allowed = _allowed_hosts(self.server)
            if parsed.scheme != "http" or parsed.netloc not in allowed:
                raise _RequestError(403, "Origin is not allowed for state-changing requests", "origin_not_allowed")

        def _require_token(self) -> None:
            query = parse_qs(self._parsed_url.query, keep_blank_values=False)
            provided = self.headers.get(TOKEN_HEADER) or query.get("token", [None])[0]
            if not provided:
                raise _RequestError(401, "missing report wizard token", "missing_token")
            if provided != self.server.session_token:
                raise _RequestError(403, "report wizard token is invalid", "bad_token")

        def _validated_content_length(self) -> int:
            content_length_header = self.headers.get("Content-Length")
            if not content_length_header:
                return 0
            try:
                content_length = int(content_length_header)
            except ValueError as error:
                raise _RequestError(400, "Content-Length must be an integer", "bad_content_length") from error
            if content_length < 0:
                raise _RequestError(400, "Content-Length must be non-negative", "bad_content_length")
            if content_length > MAX_REQUEST_BYTES:
                raise OverflowError("request exceeds the 12 MiB body limit")
            return content_length

        def _read_body(self, content_length: int) -> bytes:
            if content_length <= 0:
                return b""
            try:
                body = self.rfile.read(content_length)
            except socket.timeout as error:
                raise _RequestError(400, "request body ended early", "short_body") from error
            except OSError as error:
                raise _RequestError(400, "request body ended early", "short_body") from error
            if len(body) != content_length:
                raise _RequestError(400, "request body ended early", "short_body")
            return body

        def _send_json(self, status: int, payload: Dict) -> None:
            encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(encoded)

        def _json_error(self, status: int, message: str, *, state: Optional[Dict] = None, code: str = "request_error") -> None:
            self._send_json(status, _error_payload(message, state=state or self._safe_state(), code=code))

        def _serve_root(self) -> None:
            state = load_session(self.server.workspace)
            language = state.get("language") if state.get("language") in {"ja", "en"} else self.server.language
            body = render_report_wizard_ui(language, self.server.session_token).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _serve_state(self) -> None:
            state = session_status(self.server.workspace)
            payload = _response_payload(state, {"state": state, "uploads": _staged_upload_payload(self.server.workspace)})
            self._send_json(200, payload)

        def _serve_goal(self) -> None:
            if self.command != "POST":
                self._json_error(405, "unsupported method for this endpoint", code="method_not_allowed")
                return
            content_length = self._validated_content_length()
            with self.server.state_change_lock:
                payload = _read_json(self._read_body(content_length))
                if any(_staged_upload_paths(self.server.workspace).values()):
                    raise _RequestError(409, "goal can only be changed before uploads are added", "stage_conflict")
                state = set_session_goal(
                    self.server.workspace,
                    payload.get("report_type", ""),
                    payload.get("language", ""),
                )
            self._send_json(200, _response_payload(state, {"state": state, "uploads": _staged_upload_payload(self.server.workspace)}))

        def _serve_upload(self) -> None:
            if self.command != "POST":
                self._json_error(405, "unsupported method for this endpoint", code="method_not_allowed")
                return
            query = parse_qs(self._parsed_url.query, keep_blank_values=False)
            role = query.get("role", [None])[0]
            if role not in {"past", "current"}:
                raise _RequestError(400, "upload role must be 'past' or 'current'", "bad_role")
            content_type = self.headers.get("Content-Type", "")
            if "multipart/form-data" not in content_type:
                raise _RequestError(400, "upload requires multipart/form-data", "bad_content_type")
            content_length = self._validated_content_length()
            with self.server.state_change_lock:
                body = self._read_body(content_length)
                state = load_session(self.server.workspace)
                if state["stage"] != "created":
                    raise _RequestError(409, "uploads are only allowed before inspection begins", "stage_conflict")
                environ = {
                    "REQUEST_METHOD": "POST",
                    "CONTENT_TYPE": content_type,
                    "CONTENT_LENGTH": str(len(body)),
                }
                form = cgi.FieldStorage(
                    fp=io.BytesIO(body),
                    headers=self.headers,
                    environ=environ,
                    keep_blank_values=False,
                )
                fields = form.list or []
                parts = []
                for field in fields:
                    if field.name != "files" or not getattr(field, "filename", None):
                        continue
                    content = field.file.read(MAX_FILE_BYTES + 1)
                    if len(content) > MAX_FILE_BYTES:
                        raise OverflowError("uploaded file exceeds the 10 MiB intake limit")
                    parts.append((field.filename, content))
                if not parts:
                    raise _RequestError(400, "at least one file upload is required", "missing_files")
                saved = _save_uploaded_files(self.server.workspace, role, parts)
                state = load_session(self.server.workspace)
            self._send_json(
                200,
                _response_payload(state, {"saved": saved, "uploads": _staged_upload_payload(self.server.workspace), "state": state}),
            )

        def _serve_inspect(self) -> None:
            if self.command != "POST":
                self._json_error(405, "unsupported method for this endpoint", code="method_not_allowed")
                return
            content_length = self._validated_content_length()
            with self.server.state_change_lock:
                self._read_body(content_length)
                uploads = _staged_upload_paths(self.server.workspace)
                state = inspect_session(self.server.workspace, uploads["past"], uploads["current"])
            self._send_json(200, _response_payload(state, {"state": state, "uploads": _staged_upload_payload(self.server.workspace)}))

        def _serve_confirm(self) -> None:
            if self.command != "POST":
                self._json_error(405, "unsupported method for this endpoint", code="method_not_allowed")
                return
            content_length = self._validated_content_length()
            with self.server.state_change_lock:
                payload = _read_json(self._read_body(content_length))
                corrections = payload.get("corrections")
                if corrections is None:
                    corrections = {}
                if not isinstance(corrections, dict):
                    raise _RequestError(400, "corrections must be a JSON object", "bad_corrections")
                state = confirm_folder_plan(self.server.workspace, corrections)
            self._send_json(200, _response_payload(state, {"state": state, "uploads": _staged_upload_payload(self.server.workspace)}))

        def _serve_answer(self) -> None:
            if self.command != "POST":
                self._json_error(405, "unsupported method for this endpoint", code="method_not_allowed")
                return
            content_length = self._validated_content_length()
            with self.server.state_change_lock:
                payload = _read_json(self._read_body(content_length))
                skipped = bool(payload.get("skipped"))
                answer = payload.get("answer", "")
                state = answer_current_question(self.server.workspace, answer, skipped=skipped)
            self._send_json(200, _response_payload(state, {"state": state, "uploads": _staged_upload_payload(self.server.workspace)}))

        def _serve_build(self) -> None:
            if self.command != "POST":
                self._json_error(405, "unsupported method for this endpoint", code="method_not_allowed")
                return
            content_length = self._validated_content_length()
            with self.server.state_change_lock:
                self._read_body(content_length)
                state = build_report_workspace(self.server.workspace)
            self._send_json(200, _response_payload(state, {"state": state, "uploads": _staged_upload_payload(self.server.workspace)}))

        def _serve_approve(self) -> None:
            if self.command != "POST":
                self._json_error(405, "unsupported method for this endpoint", code="method_not_allowed")
                return
            content_length = self._validated_content_length()
            with self.server.state_change_lock:
                payload = _read_json(self._read_body(content_length))
                state = approve_report(self.server.workspace, payload.get("approver", ""))
            self._send_json(200, _response_payload(state, {"state": state, "uploads": _staged_upload_payload(self.server.workspace)}))

    server = ReportWizardHTTPServer(("127.0.0.1", port), Handler)
    server.workspace = workspace
    server.session_token = secrets.token_urlsafe(24)
    server.language = language
    server.state_change_lock = threading.RLock()
    return server


def run_report_wizard_server(workspace: Path, language: str = "ja", port: int = 0, open_browser: bool = True) -> int:
    workspace = _workspace_path(workspace)
    _ensure_session(workspace, language)
    server = create_report_wizard_server(workspace, language=language, port=port)
    url = "{}/?token={}".format(_server_origin(server), server.session_token)
    print(url)
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


class _RequestError(Exception):
    def __init__(self, status: int, message: str, code: str) -> None:
        super().__init__(message)
        self.status = status
        self.message = message
        self.code = code
