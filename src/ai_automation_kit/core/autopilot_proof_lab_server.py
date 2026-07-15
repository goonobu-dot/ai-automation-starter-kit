"""Secure localhost-only browser server for the Autopilot Proof Lab."""

from __future__ import annotations

import json
import mimetypes
import os
import re
import secrets
import socket
import stat
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Dict, Iterable, Optional
from urllib.parse import urlsplit

from ai_automation_kit.core.autopilot_proof_lab import assessment_status
from ai_automation_kit.core.autopilot_proof_lab import evaluate_assessment
from ai_automation_kit.core.autopilot_proof_lab import load_assessment
from ai_automation_kit.core.autopilot_proof_lab import REPORT_NAMES
from ai_automation_kit.core.autopilot_proof_lab import set_gate
from ai_automation_kit.core.autopilot_proof_lab_ui import render_autopilot_proof_lab_ui


MAX_REQUEST_BYTES = 64 * 1024
MAX_REPORT_BYTES = 20 * 1024 * 1024
READ_TIMEOUT_SECONDS = 1.0
TOKEN_HEADER = "X-Autopilot-Proof-Lab-Token"
REPORT_NAME_RE = re.compile(r"^[A-Za-z0-9._-]{1,128}$")
ALLOWED_REPORTS = REPORT_NAMES
REPORT_DIRECTORY = "05_REPORTS"
LANGUAGES = {"ja", "en"}


class AutopilotProofLabHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def create_autopilot_proof_lab_server(
    workspace, language: str = "ja", port: int = 0
) -> AutopilotProofLabHTTPServer:
    language = _validate_server_language(language)
    workspace_path = Path(workspace).expanduser().resolve(strict=False)
    assessment = load_assessment(workspace_path)

    class Handler(BaseHTTPRequestHandler):
        server_version = "AutopilotProofLab/1.0"
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
            self._send_error_envelope(405, "method_not_allowed", "unsupported method for this endpoint")

        def do_DELETE(self):
            self._send_error_envelope(405, "method_not_allowed", "unsupported method for this endpoint")

        def do_PATCH(self):
            self._send_error_envelope(405, "method_not_allowed", "unsupported method for this endpoint")

        def do_OPTIONS(self):
            self._send_error_envelope(405, "method_not_allowed", "unsupported method for this endpoint")

        @property
        def _parsed_url(self):
            return urlsplit(self.path)

        def _dispatch(self, method: str) -> None:
            try:
                self._reject_untrusted_client()
                self._reject_untrusted_host()
                path = self._parsed_url.path

                if path == "/":
                    if method != "GET":
                        raise _RequestError(405, "method_not_allowed", "unsupported method for this endpoint")
                    self._send_html(200, render_autopilot_proof_lab_ui(self.server.language, self.server.session_token))
                    return

                self._require_token()
                if method == "POST":
                    self._reject_bad_origin()

                if path == "/api/status":
                    if method != "GET":
                        raise _RequestError(405, "method_not_allowed", "unsupported method for this endpoint")
                    self._send_json(200, _envelope(True, _status_payload(self.server.workspace)))
                    return

                if path == "/api/evaluate":
                    if method != "POST":
                        raise _RequestError(405, "method_not_allowed", "unsupported method for this endpoint")
                    self._validated_json_body(required=set(), allowed=set())
                    with self.server.state_change_lock:
                        evaluation = evaluate_assessment(self.server.workspace)
                    payload = _status_payload(self.server.workspace)
                    payload["evaluation"] = evaluation
                    self._send_json(200, _envelope(True, payload))
                    return

                if path == "/api/gate":
                    if method != "POST":
                        raise _RequestError(405, "method_not_allowed", "unsupported method for this endpoint")
                    request = self._validated_json_body(
                        required={"gate", "status", "owner"},
                        allowed={"gate", "status", "owner", "evidence_ids", "note"},
                    )
                    with self.server.state_change_lock:
                        gate = set_gate(
                            self.server.workspace,
                            request["gate"],
                            request["status"],
                            request["owner"],
                            evidence_ids=request.get("evidence_ids"),
                            note=request.get("note", ""),
                        )
                    payload = _status_payload(self.server.workspace)
                    payload["gate"] = gate
                    self._send_json(200, _envelope(True, payload))
                    return

                if path.startswith("/api/reports/"):
                    if method != "GET":
                        raise _RequestError(405, "method_not_allowed", "unsupported method for this endpoint")
                    report_name = path[len("/api/reports/") :]
                    self._serve_report(report_name)
                    return

                raise _RequestError(404, "not_found", "unknown endpoint")
            except _RequestError as error:
                self._send_error_envelope(error.status, error.code, error.message)
            except OverflowError as error:
                self._send_error_envelope(413, "request_too_large", str(error))
            except (RuntimeError, ValueError) as error:
                self._send_error_envelope(400, "request_error", str(error))

        def _serve_report(self, report_name: str) -> None:
            if not REPORT_NAME_RE.fullmatch(report_name):
                raise _RequestError(400, "bad_report_path", "report path is not allowed")
            if report_name not in ALLOWED_REPORTS:
                raise _RequestError(404, "not_found", "report file does not exist yet")
            reports_root = (self.server.workspace / REPORT_DIRECTORY).resolve(strict=False)
            try:
                reports_root.relative_to(self.server.workspace)
            except ValueError as error:
                raise _RequestError(400, "bad_report_path", "report path is not allowed") from error
            try:
                content = _read_report_bytes(reports_root, report_name)
            except FileNotFoundError:
                raise _RequestError(404, "not_found", "report file does not exist yet")
            except ValueError as error:
                raise _RequestError(400, "bad_report_path", str(error)) from error
            self._send_file(report_name, content)

        def _reject_untrusted_client(self) -> None:
            if self.client_address[0] not in {"127.0.0.1", "::1"}:
                raise _RequestError(403, "loopback_only", "only loopback clients may use this server")

        def _reject_untrusted_host(self) -> None:
            host = self.headers.get("Host", "")
            if host not in _allowed_hosts(self.server):
                raise _RequestError(400, "host_not_allowed", "untrusted Host header")

        def _reject_bad_origin(self) -> None:
            origin = self.headers.get("Origin")
            if not origin:
                raise _RequestError(403, "origin_not_allowed", "Origin is required for state-changing requests")
            parsed = urlsplit(origin)
            if parsed.scheme != "http" or parsed.netloc not in _allowed_hosts(self.server):
                raise _RequestError(403, "origin_not_allowed", "Origin is not allowed for state-changing requests")

        def _require_token(self) -> None:
            provided = self.headers.get(TOKEN_HEADER)
            if not provided:
                raise _RequestError(401, "missing_token", "missing autopilot proof lab token")
            if provided != self.server.session_token:
                raise _RequestError(403, "bad_token", "autopilot proof lab token is invalid")

        def _validated_content_length(self) -> int:
            header = self.headers.get("Content-Length")
            if not header:
                return 0
            try:
                value = int(header)
            except ValueError as error:
                raise _RequestError(400, "bad_content_length", "Content-Length must be an integer") from error
            if value < 0:
                raise _RequestError(400, "bad_content_length", "Content-Length must be non-negative")
            if value > MAX_REQUEST_BYTES:
                raise OverflowError("request exceeds the body limit")
            return value

        def _read_body(self, content_length: int) -> bytes:
            if content_length <= 0:
                return b""
            try:
                body = self.rfile.read(content_length)
            except (socket.timeout, OSError) as error:
                raise _RequestError(400, "short_body", "request body ended early") from error
            if len(body) != content_length:
                raise _RequestError(400, "short_body", "request body ended early")
            return body

        def _validated_json_body(self, *, required: Iterable[str], allowed: Iterable[str]) -> Dict:
            content_type = self.headers.get("Content-Type", "")
            if content_type.split(";", 1)[0].strip().lower() != "application/json":
                raise _RequestError(400, "bad_content_type", "request body must use application/json")
            content_length = self._validated_content_length()
            payload = _read_json_object(self._read_body(content_length))
            payload_keys = set(payload)
            required_keys = set(required)
            allowed_keys = set(allowed)
            if payload_keys != required_keys and not (payload_keys <= allowed_keys and required_keys <= payload_keys):
                raise _RequestError(400, "bad_json", "request body fields are invalid")
            return payload

        def _send_json(self, status: int, payload: Dict) -> None:
            encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(encoded)

        def _send_html(self, status: int, markup: str) -> None:
            encoded = markup.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(encoded)

        def _send_file(self, name: str, content: bytes) -> None:
            suffix = Path(name).suffix.lower()
            content_type = mimetypes.guess_type(name)[0] or "application/octet-stream"
            if suffix == ".md":
                content_type = "text/markdown; charset=utf-8"
            elif suffix == ".json":
                content_type = "application/json; charset=utf-8"
            elif suffix == ".html":
                content_type = "text/html; charset=utf-8"
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(content)

        def _send_error_envelope(self, status: int, code: str, message: str) -> None:
            self._send_json(status, _envelope(False, {}, error={"code": code, "message": message}))

    server = AutopilotProofLabHTTPServer(("127.0.0.1", port), Handler)
    server.workspace = workspace_path
    server.language = assessment.get("language") if assessment.get("language") in LANGUAGES else language
    server.session_token = secrets.token_hex(32)
    server.state_change_lock = threading.RLock()
    return server


def run_autopilot_proof_lab_server(workspace, language: str = "ja", port: int = 0, open_browser: bool = True) -> int:
    server = create_autopilot_proof_lab_server(workspace, language=language, port=port)
    url = _server_origin(server) + "/"
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


def _validate_server_language(language: str) -> str:
    if language not in LANGUAGES:
        raise ValueError("language must be 'ja' or 'en'")
    return language


def _allowed_hosts(server: AutopilotProofLabHTTPServer) -> set:
    port = server.server_address[1]
    return {"127.0.0.1:{}".format(port), "localhost:{}".format(port)}


def _server_origin(server: AutopilotProofLabHTTPServer) -> str:
    return "http://127.0.0.1:{}".format(server.server_address[1])


def _read_report_bytes(reports_root: Path, report_name: str) -> bytes:
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        raise ValueError("secure report reading is unavailable on this platform")
    directory_fd = None
    report_fd = None
    try:
        directory_fd = os.open(
            str(reports_root),
            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
        )
        try:
            report_fd = os.open(report_name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory_fd)
        except FileNotFoundError:
            raise
        except OSError as error:
            raise ValueError("report must be a regular file and cannot be a symlink") from error
        opened = os.fstat(report_fd)
        if not stat.S_ISREG(opened.st_mode):
            raise ValueError("report must be a regular file")
        if opened.st_size > MAX_REPORT_BYTES:
            raise ValueError("report exceeds the size limit")
        chunks = []
        total = 0
        while True:
            chunk = os.read(report_fd, 65536)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_REPORT_BYTES:
                raise ValueError("report exceeds the size limit")
            chunks.append(chunk)
        return b"".join(chunks)
    except FileNotFoundError:
        raise
    except ValueError:
        raise
    except OSError as error:
        raise ValueError("report directory must be a real local directory") from error
    finally:
        if report_fd is not None:
            os.close(report_fd)
        if directory_fd is not None:
            os.close(directory_fd)


def _status_payload(workspace: Path) -> Dict:
    assessment = load_assessment(workspace)
    status = assessment_status(workspace)
    report_paths = {
        name: str(workspace / REPORT_DIRECTORY / name) for name in ALLOWED_REPORTS
    }
    report_links = {name: "/api/reports/{}".format(name) for name in ALLOWED_REPORTS}
    return {
        "assessment": assessment,
        "status": status,
        "report_paths": report_paths,
        "report_links": report_links,
    }


def _envelope(ok: bool, data: Optional[Dict], *, error: Optional[Dict] = None) -> Dict:
    payload = dict(data or {})
    status = payload.get("status") or {}
    return {
        "ok": ok,
        "data": payload,
        "next_action": status.get("next_action", "") if status else "",
        "error": error,
    }


def _read_json_object(body: bytes) -> Dict:
    try:
        payload = json.loads(body.decode("utf-8") if body else "{}")
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise _RequestError(400, "bad_json", "request body must be valid UTF-8 JSON") from error
    if not isinstance(payload, dict):
        raise _RequestError(400, "bad_json", "request body must be a JSON object")
    return payload


class _RequestError(Exception):
    def __init__(self, status: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
