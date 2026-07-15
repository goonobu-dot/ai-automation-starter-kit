"""Secure localhost image picker for Manual Studio draft manuals."""

from __future__ import annotations

import hashlib
import json
import secrets
import socket
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Dict
from urllib.parse import parse_qs, urlsplit

from ai_automation_kit.core.manual_studio import _load_draft_result
from ai_automation_kit.core.manual_studio import _load_verified_manifest
from ai_automation_kit.core.manual_studio import _safe_manifest_path
from ai_automation_kit.core.manual_studio import _sha256
from ai_automation_kit.core.manual_studio import _workspace_path
from ai_automation_kit.core.manual_studio import apply_manual_frame_selections
from ai_automation_kit.core.manual_studio import load_manual_studio_status
from ai_automation_kit.core.manual_studio_frame_picker_ui import render_manual_frame_picker_ui


TOKEN_HEADER = "X-Manual-Frame-Picker-Token"
MAX_REQUEST_BYTES = 64 * 1024
READ_TIMEOUT_SECONDS = 1.0


class ManualFramePickerHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def _allowed_hosts(server: ManualFramePickerHTTPServer) -> set:
    port = server.server_address[1]
    return {"127.0.0.1:{}".format(port), "localhost:{}".format(port)}


def _server_origin(server: ManualFramePickerHTTPServer) -> str:
    return "http://127.0.0.1:{}".format(server.server_address[1])


def _frame_id(frame_path: str) -> str:
    return hashlib.sha256(frame_path.encode("utf-8")).hexdigest()[:24]


def _picker_state(workspace: Path, token: str) -> Dict:
    root = _workspace_path(workspace)
    studio = load_manual_studio_status(root)
    if studio["stage"] != "ready_for_review":
        raise ValueError("build the draft manual before choosing images")
    manifest = _load_verified_manifest(root)
    plan = _load_draft_result(root, manifest)
    frames_by_video = {}
    for video in manifest["videos"]:
        frames_by_video[video["path"]] = [
            {
                "frame_id": _frame_id(frame["path"]),
                "frame_path": frame["path"],
                "timestamp_seconds": frame["timestamp_seconds"],
                "image_url": "/frames/{}?token={}".format(_frame_id(frame["path"]), token),
            }
            for frame in sorted(video["frames"], key=lambda item: item["timestamp_seconds"])
        ]
    steps = []
    for step in plan["steps"]:
        candidates = frames_by_video.get(step["source_video"], []) if step["frame_path"] else []
        steps.append(
            {
                "order": step["order"],
                "title": step["title"],
                "instruction": step["instruction"],
                "source_video": step["source_video"],
                "selected_frame_id": _frame_id(step["frame_path"]) if step["frame_path"] else None,
                "selected_frame_path": step["frame_path"],
                "candidates": candidates,
            }
        )
    return {
        "name": studio["name"],
        "language": studio["language"],
        "stage": studio["stage"],
        "steps": steps,
    }


def _frame_map(workspace: Path) -> Dict[str, Dict[str, str]]:
    manifest = _load_verified_manifest(workspace)
    result = {}
    for video in manifest["videos"]:
        for frame in video["frames"]:
            frame_id = _frame_id(frame["path"])
            entry = {"path": frame["path"], "sha256": frame["sha256"]}
            if frame_id in result and result[frame_id]["path"] != frame["path"]:
                raise ValueError("frame identifier collision")
            result[frame_id] = entry
    return result


def create_manual_frame_picker_server(workspace: Path, port: int = 0) -> ManualFramePickerHTTPServer:
    root = _workspace_path(workspace)
    state = load_manual_studio_status(root)
    if state["language"] not in {"ja", "en"}:
        raise ValueError("language must be 'ja' or 'en'")
    _picker_state(root, "validation-token")

    class Handler(BaseHTTPRequestHandler):
        server_version = "ManualFramePicker/1.0"
        sys_version = ""

        def log_message(self, format, *args):  # noqa: A003
            return

        def setup(self):
            super().setup()
            self.connection.settimeout(READ_TIMEOUT_SECONDS)

        @property
        def _parsed_url(self):
            return urlsplit(self.path)

        def do_GET(self):
            self._dispatch("GET")

        def do_POST(self):
            self._dispatch("POST")

        def do_PUT(self):
            self._json_error(405, "unsupported method", "method_not_allowed")

        do_DELETE = do_PUT
        do_PATCH = do_PUT
        do_OPTIONS = do_PUT

        def _dispatch(self, method: str) -> None:
            try:
                self._reject_untrusted_client()
                self._reject_untrusted_host()
                if method == "POST":
                    self._reject_bad_origin()
                self._require_token()
                path = self._parsed_url.path
                if path == "/":
                    if method != "GET":
                        raise _RequestError(405, "unsupported method", "method_not_allowed")
                    self._serve_root()
                    return
                if path == "/api/state":
                    if method != "GET":
                        raise _RequestError(405, "unsupported method", "method_not_allowed")
                    self._send_json(200, _picker_state(self.server.workspace, self.server.session_token))
                    return
                if path == "/api/selections":
                    if method != "POST":
                        raise _RequestError(405, "unsupported method", "method_not_allowed")
                    self._serve_selections()
                    return
                if path == "/manual":
                    if method != "GET":
                        raise _RequestError(405, "unsupported method", "method_not_allowed")
                    self._serve_manual()
                    return
                if path == "/answer-guide":
                    if method != "GET":
                        raise _RequestError(405, "unsupported method", "method_not_allowed")
                    self._serve_answer_guide()
                    return
                if path.startswith("/frames/"):
                    if method != "GET":
                        raise _RequestError(405, "unsupported method", "method_not_allowed")
                    self._serve_frame(path.removeprefix("/frames/"))
                    return
                raise _RequestError(404, "unknown endpoint", "not_found")
            except _RequestError as error:
                self._json_error(error.status, error.message, error.code)
            except ValueError as error:
                self._json_error(400, str(error), "validation_error")
            except (OSError, socket.timeout):
                self._json_error(400, "request could not be read", "request_error")

        def _reject_untrusted_client(self) -> None:
            if self.client_address[0] not in {"127.0.0.1", "::1"}:
                raise _RequestError(403, "only loopback clients may use this server", "loopback_only")

        def _reject_untrusted_host(self) -> None:
            if self.headers.get("Host", "") not in _allowed_hosts(self.server):
                raise _RequestError(400, "untrusted Host header", "host_not_allowed")

        def _reject_bad_origin(self) -> None:
            origin = self.headers.get("Origin")
            if not origin:
                raise _RequestError(403, "Origin is required", "origin_not_allowed")
            parsed = urlsplit(origin)
            if parsed.scheme != "http" or parsed.netloc not in _allowed_hosts(self.server):
                raise _RequestError(403, "Origin is not allowed", "origin_not_allowed")

        def _require_token(self) -> None:
            query = parse_qs(self._parsed_url.query, keep_blank_values=False)
            provided = self.headers.get(TOKEN_HEADER) or query.get("token", [None])[0]
            if not provided:
                raise _RequestError(401, "missing image picker token", "missing_token")
            if not secrets.compare_digest(provided, self.server.session_token):
                raise _RequestError(403, "image picker token is invalid", "bad_token")

        def _read_json(self) -> Dict:
            raw_length = self.headers.get("Content-Length")
            try:
                length = int(raw_length or "0")
            except ValueError as error:
                raise _RequestError(400, "invalid Content-Length", "bad_content_length") from error
            if length <= 0 or length > MAX_REQUEST_BYTES:
                raise _RequestError(400, "request body size is invalid", "bad_content_length")
            body = self.rfile.read(length)
            if len(body) != length:
                raise _RequestError(400, "request body ended early", "short_body")
            try:
                payload = json.loads(body.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                raise _RequestError(400, "request body must be JSON", "bad_json") from error
            if not isinstance(payload, dict):
                raise _RequestError(400, "request body must be an object", "bad_json")
            return payload

        def _security_headers(self) -> None:
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'self'; img-src 'self'; style-src 'self' 'unsafe-inline'; "
                "script-src 'self' 'unsafe-inline'; connect-src 'self'; base-uri 'none'; "
                "form-action 'self'; frame-ancestors 'none'",
            )

        def _send_json(self, status: int, payload: Dict) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self._security_headers()
            self.end_headers()
            self.wfile.write(body)

        def _json_error(self, status: int, message: str, code: str) -> None:
            self._send_json(status, {"ok": False, "error": message, "code": code})

        def _serve_root(self) -> None:
            state = load_manual_studio_status(self.server.workspace)
            body = render_manual_frame_picker_ui(state["language"], self.server.session_token).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self._security_headers()
            self.end_headers()
            self.wfile.write(body)

        def _serve_frame(self, frame_id: str) -> None:
            frame = self.server.frame_map.get(frame_id)
            if frame is None:
                raise _RequestError(404, "unknown frame", "not_found")
            image = _safe_manifest_path(
                self.server.workspace, frame["path"], "02_EXTRACTED_FRAMES", "frame path"
            )
            if _sha256(image) != frame["sha256"]:
                raise _RequestError(409, "frame no longer matches the capture manifest", "frame_changed")
            body = image.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(body)))
            self._security_headers()
            self.end_headers()
            self.wfile.write(body)

        def _serve_manual(self) -> None:
            manual_path = self.server.workspace / "04_DRAFT_MANUAL" / "manual.html"
            body = manual_path.read_text(encoding="utf-8")
            token = self.server.session_token
            for frame in self.server.frame_map.values():
                frame_path = frame["path"]
                source = "../" + frame_path
                replacement = "/frames/{}?token={}".format(_frame_id(frame_path), token)
                body = body.replace(source, replacement)
            body = body.replace(
                "../05_REVIEW/ANSWER_GUIDE.html",
                "/answer-guide?token={}".format(token),
            )
            encoded = body.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self._security_headers()
            self.end_headers()
            self.wfile.write(encoded)

        def _serve_answer_guide(self) -> None:
            guide_path = self.server.workspace / "05_REVIEW" / "ANSWER_GUIDE.html"
            encoded = guide_path.read_text(encoding="utf-8").encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self._security_headers()
            self.end_headers()
            self.wfile.write(encoded)

        def _serve_selections(self) -> None:
            payload = self._read_json()
            raw_selections = payload.get("selections")
            if not isinstance(raw_selections, list):
                raise _RequestError(400, "selections must be a list", "bad_selections")
            selections = []
            for item in raw_selections:
                if not isinstance(item, dict) or set(item) != {"order", "frame_id"}:
                    raise _RequestError(400, "selection fields are invalid", "bad_selections")
                frame = self.server.frame_map.get(item["frame_id"])
                if frame is None:
                    raise _RequestError(400, "selected frame is unknown", "bad_selections")
                selections.append({"order": item["order"], "frame_path": frame["path"]})
            with self.server.state_change_lock:
                result = apply_manual_frame_selections(
                    self.server.workspace,
                    selections=selections,
                    selected_by="Local image picker",
                )
            self._send_json(200, {"ok": True, **result})

    server = ManualFramePickerHTTPServer(("127.0.0.1", port), Handler)
    server.workspace = root
    server.session_token = secrets.token_urlsafe(24)
    server.state_change_lock = threading.RLock()
    server.frame_map = _frame_map(root)
    return server


def run_manual_frame_picker_server(
    workspace: Path,
    *,
    port: int = 0,
    open_browser: bool = True,
) -> int:
    server = create_manual_frame_picker_server(workspace, port=port)
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


__all__ = [
    "ManualFramePickerHTTPServer",
    "TOKEN_HEADER",
    "create_manual_frame_picker_server",
    "run_manual_frame_picker_server",
]
