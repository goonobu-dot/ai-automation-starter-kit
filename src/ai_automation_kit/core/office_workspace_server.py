"""Secure localhost API server for office workspaces."""

from __future__ import annotations

import json
import os
import re
import secrets
import shutil
import socket
import subprocess
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Dict, Iterable, Optional, Tuple
from urllib.parse import urlsplit

from ai_automation_kit.core.codex_runner import cancel_run
from ai_automation_kit.core.codex_runner import codex_preflight
from ai_automation_kit.core.codex_runner import run_status
from ai_automation_kit.core.codex_runner import start_codex_run
from ai_automation_kit.core.office_workspace_builder import _absolute_path
from ai_automation_kit.core.office_workspace_builder import _path_uses_symlink
from ai_automation_kit.core.office_workspace_builder import _read_text_no_follow
from ai_automation_kit.core.office_workspace_builder import create_office_workspace
from ai_automation_kit.core.office_workspace_builder import validate_period_id
from ai_automation_kit.core.office_workspace_builder import validate_workspace_root
from ai_automation_kit.core.office_workspace_state import _load_period_state
from ai_automation_kit.core.office_workspace_state import approve_draft
from ai_automation_kit.core.office_workspace_state import create_period
from ai_automation_kit.core.office_workspace_state import inspect_period
from ai_automation_kit.core.office_workspace_state import load_workspace
from ai_automation_kit.core.office_workspace_state import save_answer
from ai_automation_kit.core.office_workspace_ui import render_office_workspace_ui
from ai_automation_kit.core.workflow_pack import list_bundled_packs
from ai_automation_kit.core.workflow_pack import load_bundled_pack


MAX_REQUEST_BYTES = 64 * 1024
MAX_ANSWER_CHARS = 4096
READ_TIMEOUT_SECONDS = 1.0
TOKEN_HEADER = "X-Office-Workspace-Token"
ACTION_NONCE_RE = re.compile(r"^[0-9a-f]{64}$")
WORKSPACE_ID_RE = re.compile(r"^ws-[0-9a-f]{32}$")
RUN_ID_RE = re.compile(r"^run-[0-9a-f]{32}$")
SAFE_IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
SAFE_DRAFT_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}\.md$")
WORKSPACE_ROUTE_RE = re.compile(r"^/api/workspaces/(?P<workspace_id>ws-[0-9a-f]{32})$")
WORKSPACE_ACTION_ROUTE_RE = re.compile(
    r"^/api/workspaces/(?P<workspace_id>ws-[0-9a-f]{32})/"
    r"(?P<action>inspect|answer|generate|cancel|approve|rollover|open-folder)$"
)
ROOT_CHOICES = frozenset({"server_root", "default"})
FOLDER_ROLE_PATHS = {
    "start_here": ("00_START_HERE", False),
    "approved_past_outputs": ("01_APPROVED_PAST_OUTPUTS", False),
    "past_supporting_files": ("02_PAST_SUPPORTING_FILES", False),
    "current_inputs": ("03_CURRENT_INPUTS", True),
    "questions": ("04_QUESTIONS", True),
    "drafts": ("05_DRAFTS", True),
    "approved_outputs": ("06_APPROVED_OUTPUTS", True),
    "audit": ("07_AUDIT", False),
}


class OfficeWorkspaceHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def create_office_workspace_server(root: Path, language: str = "ja", port: int = 0) -> OfficeWorkspaceHTTPServer:
    language = _validate_server_language(language)
    root_path = _prepare_server_root(root)

    class Handler(BaseHTTPRequestHandler):
        server_version = "OfficeWorkspace/1.0"
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
                        self._send_error_envelope(405, "method_not_allowed", "unsupported method for this endpoint")
                        return
                    self._serve_root()
                    return

                self._require_token()

                if method == "POST":
                    self._reject_bad_origin()

                if path == "/api/workspaces":
                    if method == "GET":
                        self._serve_workspaces()
                        return
                    if method == "POST":
                        self._serve_create_workspace()
                        return
                    self._send_error_envelope(405, "method_not_allowed", "unsupported method for this endpoint")
                    return

                workspace_match = WORKSPACE_ROUTE_RE.fullmatch(path)
                if workspace_match:
                    if method != "GET":
                        self._send_error_envelope(405, "method_not_allowed", "unsupported method for this endpoint")
                        return
                    self._serve_workspace_detail(workspace_match.group("workspace_id"))
                    return

                action_match = WORKSPACE_ACTION_ROUTE_RE.fullmatch(path)
                if action_match:
                    if method != "POST":
                        self._send_error_envelope(405, "method_not_allowed", "unsupported method for this endpoint")
                        return
                    workspace_id = action_match.group("workspace_id")
                    action = action_match.group("action")
                    self._serve_workspace_action(workspace_id, action)
                    return

                self._send_error_envelope(404, "not_found", "unknown endpoint")
            except _RequestError as error:
                self._send_error_envelope(
                    error.status,
                    error.code,
                    error.message,
                    next_action=error.next_action,
                )
            except OverflowError as error:
                self._send_error_envelope(413, "request_too_large", str(error))
            except (RuntimeError, ValueError) as error:
                mapped = _map_domain_error(error)
                self._send_error_envelope(
                    mapped.status,
                    mapped.code,
                    mapped.message,
                    next_action=mapped.next_action,
                )

        def _serve_root(self) -> None:
            self._send_html(200, render_office_workspace_ui(self.server.language, self.server.session_token))

        def _serve_workspaces(self) -> None:
            workspaces = []
            for workspace_root in _discover_workspaces(self.server):
                public_id = _public_workspace_id(self.server, workspace_root)
                workspaces.append(_workspace_summary(self.server, workspace_root, public_id))
            pack_catalog = [_pack_catalog_entry(pack) for pack in list_bundled_packs()]
            preflight = _normalized_preflight(codex_preflight())
            next_action = preflight["next_action"] if not preflight["ok"] else ""
            if not next_action and not workspaces:
                next_action = "Create a workspace and first period to begin."
            payload = {
                "workspaces": workspaces,
                "pack_catalog": pack_catalog,
                "root_choices": [{"id": "server_root", "path": str(self.server.root)}],
                "preflight": preflight,
            }
            self._send_json(200, _envelope(self.server, True, payload, next_action=next_action, error=None))

        def _serve_create_workspace(self) -> None:
            payload = self._validated_json_body(
                required={"action_nonce", "name", "root_choice", "approver", "pin"},
                allowed={"action_nonce", "name", "root_choice", "approver", "pin", "pack_id", "period_id"},
            )
            self._consume_action_nonce(payload.get("action_nonce"))
            root_choice = payload["root_choice"]
            if root_choice not in ROOT_CHOICES:
                raise _RequestError(400, "bad_root_choice", "root_choice must select the configured server root")
            pack_id = _validated_pack_id(payload.get("pack_id"))
            first_period_id = _optional_bounded_text(payload.get("period_id"), "period_id", maximum=32)
            with self.server.state_change_lock:
                workspace_root = create_office_workspace(
                    self.server.root,
                    name=_bounded_text(payload["name"], "name", maximum=200),
                    approver=_bounded_text(payload["approver"], "approver", maximum=200),
                    pin=_bounded_text(payload["pin"], "pin", maximum=64),
                    language=self.server.language,
                    pack_id=pack_id,
                )
                try:
                    if first_period_id is not None:
                        create_period(workspace_root, first_period_id)
                except Exception:
                    shutil.rmtree(workspace_root, ignore_errors=True)
                    raise
                public_id = _public_workspace_id(self.server, workspace_root)
                detail = _workspace_detail(self.server, workspace_root, public_id)
            self._send_json(
                200,
                _envelope(
                    self.server,
                    True,
                    {"workspace": detail},
                    next_action=_workspace_next_action(detail),
                    error=None,
                ),
            )

        def _serve_workspace_detail(self, workspace_id: str) -> None:
            workspace_root = _resolve_workspace_id(self.server, workspace_id)
            preflight = _normalized_preflight(codex_preflight())
            detail = _workspace_detail(self.server, workspace_root, workspace_id)
            next_action = preflight["next_action"] if not preflight["ok"] else _workspace_next_action(detail)
            self._send_json(
                200,
                _envelope(
                    self.server,
                    True,
                    {"workspace": detail, "preflight": preflight},
                    next_action=next_action,
                    error=None,
                ),
            )

        def _serve_workspace_action(self, workspace_id: str, action: str) -> None:
            workspace_root = _resolve_workspace_id(self.server, workspace_id)
            if action == "inspect":
                self._serve_inspect(workspace_root, workspace_id)
                return
            if action == "answer":
                self._serve_answer(workspace_root, workspace_id)
                return
            if action == "generate":
                self._serve_generate(workspace_root, workspace_id)
                return
            if action == "cancel":
                self._serve_cancel(workspace_root, workspace_id)
                return
            if action == "approve":
                self._serve_approve(workspace_root, workspace_id)
                return
            if action == "rollover":
                self._serve_rollover(workspace_root, workspace_id)
                return
            if action == "open-folder":
                self._serve_open_folder(workspace_root, workspace_id)
                return
            raise _RequestError(404, "not_found", "unknown endpoint")

        def _serve_inspect(self, workspace_root: Path, workspace_id: str) -> None:
            payload = self._validated_json_body(
                required={"action_nonce", "period_id"},
                allowed={"action_nonce", "period_id"},
            )
            self._consume_action_nonce(payload.get("action_nonce"))
            period_id = _validated_workspace_period_id(workspace_root, payload["period_id"])
            with self.server.state_change_lock:
                inspect_period(workspace_root, period_id)
                detail = _workspace_detail(self.server, workspace_root, workspace_id)
            self._send_json(
                200,
                _envelope(self.server, True, {"workspace": detail}, next_action=_workspace_next_action(detail), error=None),
            )

        def _serve_answer(self, workspace_root: Path, workspace_id: str) -> None:
            payload = self._validated_json_body(
                required={"action_nonce", "question_id", "answer"},
                allowed={"action_nonce", "question_id", "answer"},
            )
            self._consume_action_nonce(payload.get("action_nonce"))
            question_id = _validate_question_id(payload["question_id"])
            answer = _bounded_text(payload["answer"], "answer", maximum=MAX_ANSWER_CHARS)
            with self.server.state_change_lock:
                save_answer(workspace_root, _current_period_id(workspace_root), question_id, answer)
                detail = _workspace_detail(self.server, workspace_root, workspace_id)
            self._send_json(
                200,
                _envelope(self.server, True, {"workspace": detail}, next_action=_workspace_next_action(detail), error=None),
            )

        def _serve_generate(self, workspace_root: Path, workspace_id: str) -> None:
            payload = self._validated_json_body(
                required={"action_nonce", "period_id"},
                allowed={"action_nonce", "period_id"},
            )
            self._consume_action_nonce(payload.get("action_nonce"))
            period_id = _validated_workspace_period_id(workspace_root, payload["period_id"])
            with self.server.state_change_lock:
                period_state = _load_period_state(workspace_root, period_id)
                if period_state["stage"] != "ready_for_run":
                    raise _RequestError(
                        409,
                        "state_conflict",
                        "requested action is not allowed in the current workspace state",
                        next_action="Refresh the workspace and complete the current step first.",
                    )
                preflight = codex_preflight()
                if not preflight["ok"]:
                    status = 409 if preflight["code"] == "codex_not_logged_in" else 503
                    raise _RequestError(status, preflight["code"], "Codex is not ready", next_action=preflight["next_action"])
                run_record = start_codex_run(workspace_root, period_id)
                detail = _workspace_detail(self.server, workspace_root, workspace_id)
            self._send_json(
                200,
                _envelope(
                    self.server,
                    True,
                    {"workspace": detail, "run": run_record},
                    next_action=_workspace_next_action(detail),
                    error=None,
                ),
            )

        def _serve_cancel(self, workspace_root: Path, workspace_id: str) -> None:
            payload = self._validated_json_body(
                required={"action_nonce", "run_id"},
                allowed={"action_nonce", "run_id"},
            )
            self._consume_action_nonce(payload.get("action_nonce"))
            run_id = _validate_run_id(payload["run_id"])
            with self.server.state_change_lock:
                run_record = cancel_run(workspace_root, run_id)
                detail = _workspace_detail(self.server, workspace_root, workspace_id)
            self._send_json(
                200,
                _envelope(
                    self.server,
                    True,
                    {"workspace": detail, "run": run_record},
                    next_action=_workspace_next_action(detail),
                    error=None,
                ),
            )

        def _serve_approve(self, workspace_root: Path, workspace_id: str) -> None:
            payload = self._validated_json_body(
                required={"action_nonce", "draft_id", "approver", "pin"},
                allowed={"action_nonce", "draft_id", "approver", "pin"},
            )
            self._consume_action_nonce(payload.get("action_nonce"))
            draft_id = _validate_draft_id(payload["draft_id"])
            approver = _bounded_text(payload["approver"], "approver", maximum=200)
            pin = _bounded_text(payload["pin"], "pin", maximum=64)
            with self.server.state_change_lock:
                approve_draft(workspace_root, _current_period_id(workspace_root), draft_id, approver, pin)
                detail = _workspace_detail(self.server, workspace_root, workspace_id)
            self._send_json(
                200,
                _envelope(self.server, True, {"workspace": detail}, next_action=_workspace_next_action(detail), error=None),
            )

        def _serve_rollover(self, workspace_root: Path, workspace_id: str) -> None:
            payload = self._validated_json_body(
                required={"action_nonce", "next_period_id", "style_reference"},
                allowed={"action_nonce", "next_period_id", "style_reference"},
            )
            self._consume_action_nonce(payload.get("action_nonce"))
            next_period_id = _validated_workspace_period_id(workspace_root, payload["next_period_id"])
            style_reference = _validated_style_reference_request(payload["style_reference"])
            with self.server.state_change_lock:
                create_period(workspace_root, next_period_id, style_reference=style_reference)
                detail = _workspace_detail(self.server, workspace_root, workspace_id)
            self._send_json(
                200,
                _envelope(self.server, True, {"workspace": detail}, next_action=_workspace_next_action(detail), error=None),
            )

        def _serve_open_folder(self, workspace_root: Path, workspace_id: str) -> None:
            payload = self._validated_json_body(
                required={"action_nonce", "role"},
                allowed={"action_nonce", "role"},
            )
            self._consume_action_nonce(payload.get("action_nonce"))
            role = _validate_folder_role(payload["role"])
            with self.server.state_change_lock:
                target = _folder_path_for_role(workspace_root, _current_period_id_optional(workspace_root), role)
                command = ["open", str(target)] if sys.platform.startswith("darwin") else ["xdg-open", str(target)]
                completed = subprocess.run(
                    command,
                    check=False,
                    shell=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                if completed.returncode != 0:
                    raise _RequestError(
                        500,
                        "open_folder_failed",
                        "the local folder could not be opened",
                        next_action="Open the folder manually from the workspace path and retry.",
                    )
                detail = _workspace_detail(self.server, workspace_root, workspace_id)
            self._send_json(
                200,
                _envelope(
                    self.server,
                    True,
                    {"workspace": detail, "opened": {"role": role, "path": str(target)}},
                    next_action=_workspace_next_action(detail),
                    error=None,
                ),
            )

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
                raise _RequestError(401, "missing_token", "missing office workspace token")
            if provided != self.server.session_token:
                raise _RequestError(403, "bad_token", "office workspace token is invalid")

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
            allowed_keys = set(allowed)
            required_keys = set(required)
            if set(payload) != required_keys and not (set(payload) <= allowed_keys and required_keys <= set(payload)):
                raise _RequestError(400, "bad_json", "request body fields are invalid")
            return payload

        def _consume_action_nonce(self, value) -> None:
            if not isinstance(value, str) or not ACTION_NONCE_RE.fullmatch(value):
                raise _RequestError(409, "bad_action_nonce", "action nonce is invalid", next_action="Refresh the workspace and retry.")
            with self.server.action_nonce_lock:
                if value not in self.server.valid_action_nonces:
                    raise _RequestError(
                        409,
                        "bad_action_nonce",
                        "action nonce is invalid",
                        next_action="Refresh the workspace and retry.",
                    )
                del self.server.valid_action_nonces[value]

        def _send_json(self, status: int, payload: Dict) -> None:
            encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(encoded)

        def _send_html(self, status: int, html: str) -> None:
            encoded = html.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(encoded)

        def _send_error_envelope(
            self,
            status: int,
            code: str,
            message: str,
            *,
            next_action: Optional[str] = None,
        ) -> None:
            if self.server.language == "ja" or not isinstance(next_action, str) or not next_action:
                next_action = _error_next_action(self.server.language, code)
            payload = _envelope(
                self.server,
                False,
                {},
                next_action=next_action,
                error={"code": code, "message": message},
            )
            self._send_json(status, payload)

    server = OfficeWorkspaceHTTPServer(("127.0.0.1", port), Handler)
    server.root = root_path
    server.language = language
    server.session_token = secrets.token_hex(32)
    server.state_change_lock = threading.RLock()
    server.workspace_mapping_lock = threading.RLock()
    server.public_ids_by_root = {}
    server.roots_by_public_id = {}
    server.action_nonce_lock = threading.RLock()
    server.valid_action_nonces = {}
    return server


def _validate_server_language(language: str) -> str:
    if language not in {"ja", "en"}:
        raise ValueError("language must be 'ja' or 'en'")
    return language


def _prepare_server_root(root: Path) -> Path:
    root_path = _absolute_path(root)
    if _path_uses_symlink(root_path):
        raise ValueError("server root cannot use symlinked paths")
    if root_path.exists():
        if root_path.is_symlink() or not root_path.is_dir():
            raise ValueError("server root must be a directory")
    else:
        root_path.mkdir(mode=0o700, parents=True, exist_ok=True)
    return root_path


def _allowed_hosts(server: OfficeWorkspaceHTTPServer) -> set:
    port = server.server_address[1]
    return {"127.0.0.1:{}".format(port), "localhost:{}".format(port)}


def _server_origin(server: OfficeWorkspaceHTTPServer) -> str:
    return "http://127.0.0.1:{}".format(server.server_address[1])


def _issue_action_nonce(server: OfficeWorkspaceHTTPServer) -> str:
    nonce = secrets.token_hex(32)
    with server.action_nonce_lock:
        server.valid_action_nonces[nonce] = True
        if len(server.valid_action_nonces) > 256:
            first_key = next(iter(server.valid_action_nonces))
            del server.valid_action_nonces[first_key]
    return nonce


def _envelope(
    server: OfficeWorkspaceHTTPServer,
    ok: bool,
    data: Optional[Dict],
    *,
    next_action: Optional[str],
    error: Optional[Dict],
) -> Dict:
    payload = dict(data or {})
    payload["action_nonce"] = _issue_action_nonce(server)
    return {
        "ok": ok,
        "data": payload,
        "next_action": next_action if isinstance(next_action, str) else "",
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


def _bounded_text(value, label: str, *, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise _RequestError(400, "bad_json", "{} must be a non-empty string".format(label))
    if len(value) > maximum:
        raise _RequestError(400, "bad_json", "{} exceeds the allowed length".format(label))
    return value.strip()


def _optional_bounded_text(value, label: str, *, maximum: int) -> Optional[str]:
    if value is None:
        return None
    return _bounded_text(value, label, maximum=maximum)


def _discover_workspaces(server: OfficeWorkspaceHTTPServer) -> Tuple[Path, ...]:
    discovered = []
    if not server.root.exists():
        return tuple()
    for child in sorted(server.root.iterdir()):
        if child.is_symlink() or not child.is_dir():
            continue
        try:
            discovered.append(validate_workspace_root(child))
        except Exception:
            continue
    with server.workspace_mapping_lock:
        for workspace_root in discovered:
            _public_workspace_id(server, workspace_root)
    return tuple(discovered)


def _public_workspace_id(server: OfficeWorkspaceHTTPServer, workspace_root: Path) -> str:
    key = str(validate_workspace_root(workspace_root))
    with server.workspace_mapping_lock:
        public_id = server.public_ids_by_root.get(key)
        if public_id is None:
            public_id = "ws-{}".format(secrets.token_hex(16))
            server.public_ids_by_root[key] = public_id
            server.roots_by_public_id[public_id] = workspace_root
        return public_id


def _resolve_workspace_id(server: OfficeWorkspaceHTTPServer, workspace_id: str) -> Path:
    if not isinstance(workspace_id, str) or not WORKSPACE_ID_RE.fullmatch(workspace_id):
        raise _RequestError(404, "workspace_not_found", "workspace was not found")
    _discover_workspaces(server)
    with server.workspace_mapping_lock:
        workspace_root = server.roots_by_public_id.get(workspace_id)
    if workspace_root is None:
        raise _RequestError(404, "workspace_not_found", "workspace was not found")
    return validate_workspace_root(workspace_root)


def _workspace_summary(server: OfficeWorkspaceHTTPServer, workspace_root: Path, public_id: str) -> Dict:
    state = load_workspace(workspace_root)
    pack = load_bundled_pack(state["pack_id"])
    period_state = _load_current_period_state(workspace_root)
    current_period = state["current_period"]
    return {
        "id": public_id,
        "name": state["name"],
        "root": str(workspace_root),
        "language": state["language"],
        "pack_id": state["pack_id"],
        "display_name": dict(pack["display_name"]),
        "period_type": pack["period_type"],
        "current_period": current_period,
        "periods": list(state["periods"]),
        "updated_at": state["updated_at"],
        "period_stage": period_state["stage"] if period_state else None,
        "approver": state["approval"]["approver"],
        "run": _bounded_run_summary(_latest_run_for_period(workspace_root, current_period)),
    }


def _workspace_detail(server: OfficeWorkspaceHTTPServer, workspace_root: Path, public_id: str) -> Dict:
    state = load_workspace(workspace_root)
    pack = load_bundled_pack(state["pack_id"])
    current_period = state["current_period"]
    period_state = _load_current_period_state(workspace_root)
    return {
        "id": public_id,
        "name": state["name"],
        "root": str(workspace_root),
        "language": state["language"],
        "pack_id": state["pack_id"],
        "display_name": dict(pack["display_name"]),
        "period_type": pack["period_type"],
        "current_period": current_period,
        "periods": list(state["periods"]),
        "period": period_state,
        "approval": {
            "approver": state["approval"]["approver"],
            "audit": period_state["audit"] if period_state else {"status": "pending", "latest_hash": None, "entries": 0},
        },
        "source_manifest": _current_source_manifest(workspace_root, current_period),
        "folders": _folder_details(workspace_root, current_period),
        "run": _latest_run_for_period(workspace_root, current_period),
    }


def _load_current_period_state(workspace_root: Path) -> Optional[Dict]:
    workspace_state = load_workspace(workspace_root)
    current_period = workspace_state.get("current_period")
    if not current_period:
        return None
    return _load_period_state(workspace_root, current_period)


def _current_period_id(workspace_root: Path) -> str:
    current_period = _current_period_id_optional(workspace_root)
    if not current_period:
        raise _RequestError(
            409,
            "state_conflict",
            "requested action is not allowed in the current workspace state",
            next_action="Create the first period.",
        )
    return current_period


def _current_period_id_optional(workspace_root: Path) -> Optional[str]:
    workspace_state = load_workspace(workspace_root)
    return workspace_state.get("current_period")


def _folder_details(workspace_root: Path, current_period: Optional[str]) -> Dict:
    details = {}
    for role in FOLDER_ROLE_PATHS:
        path = _folder_path_for_role(workspace_root, current_period, role, require_current_period=False)
        files = _list_regular_files(path)
        details[role] = {
            "path": str(path) if path is not None else None,
            "files": files,
            "file_count": len(files),
        }
    return details


def _folder_path_for_role(
    workspace_root: Path,
    current_period: Optional[str],
    role: str,
    *,
    require_current_period: bool = True,
) -> Optional[Path]:
    role = _validate_folder_role(role)
    folder_name, needs_period = FOLDER_ROLE_PATHS[role]
    if needs_period:
        if not current_period:
            if require_current_period:
                raise _RequestError(
                    409,
                    "state_conflict",
                    "requested action is not allowed in the current workspace state",
                    next_action="Create the first period.",
                )
            return None
        return workspace_root / folder_name / current_period
    return workspace_root / folder_name


def _list_regular_files(path: Optional[Path]) -> list:
    if path is None or not path.exists() or not path.is_dir():
        return []
    files = []
    for child in sorted(path.iterdir()):
        if child.is_symlink() or not child.is_file():
            continue
        files.append({"name": child.name, "path": str(child), "bytes": child.stat().st_size})
    return files


def _current_source_manifest(workspace_root: Path, current_period: Optional[str]) -> Optional[Dict]:
    if not current_period:
        return None
    path = workspace_root / ".system" / "periods" / current_period / "source_manifest.json"
    if not path.exists():
        return None
    try:
        return json.loads(_read_text_no_follow(path, "source manifest"))
    except Exception:
        return None


def _latest_run_for_period(workspace_root: Path, period_id: Optional[str]) -> Optional[Dict]:
    if not period_id:
        return None
    runs_root = workspace_root / ".system" / "runs"
    if not runs_root.exists():
        return None
    latest_run_id = None
    latest_started_at = ""
    for child in runs_root.iterdir():
        if child.is_symlink() or not child.is_dir() or not RUN_ID_RE.fullmatch(child.name):
            continue
        record_path = child / "run.json"
        if not record_path.exists():
            continue
        try:
            record = json.loads(_read_text_no_follow(record_path, "run metadata"))
        except Exception:
            continue
        if record.get("period_id") != period_id:
            continue
        started_at = str(record.get("started_at") or "")
        if started_at >= latest_started_at:
            latest_started_at = started_at
            latest_run_id = child.name
    if latest_run_id is None:
        return None
    try:
        return run_status(workspace_root, latest_run_id)
    except Exception:
        return None


def _bounded_run_summary(run: Optional[Dict]) -> Optional[Dict]:
    if not isinstance(run, dict):
        return None
    allowed_statuses = {"running", "cancelling", "questioning", "ready_for_review", "failed", "cancelled"}
    run_id = run.get("run_id")
    status = run.get("status")
    if not isinstance(run_id, str) or not RUN_ID_RE.fullmatch(run_id) or status not in allowed_statuses:
        return None

    summary = {"run_id": run_id, "status": status, "started_at": None, "finished_at": None}
    for key in ("started_at", "finished_at"):
        value = run.get(key)
        if isinstance(value, str):
            summary[key] = value[:64]
    return summary


def _workspace_next_action(detail: Dict) -> str:
    current_period = detail.get("current_period")
    period = detail.get("period")
    if not current_period or not period:
        return "Create the first period."
    stage = period.get("stage")
    if stage == "created":
        return "Place the current files in the workspace and inspect them."
    if stage in {"inputs_ready", "reviewed", "questioning"}:
        return "Answer the remaining questions."
    if stage == "ready_for_run":
        return "Generate the draft."
    if stage == "running":
        return "Wait for the current run to finish or cancel it."
    if stage == "ready_for_review":
        return "Review the draft and approve it when it is ready."
    if stage == "approved":
        return "Create the next reporting period when you are ready."
    if stage in {"failed", "cancelled"}:
        return "Inspect the files again and retry draft generation."
    return ""


def _normalized_preflight(preflight: Dict) -> Dict:
    normalized = dict(preflight)
    next_action = normalized.get("next_action")
    normalized["next_action"] = next_action if isinstance(next_action, str) else ""
    return normalized


def _pack_catalog_entry(pack: Dict) -> Dict:
    return {
        "id": pack["id"],
        "display_name": dict(pack["display_name"]),
        "period_type": pack["period_type"],
    }


def _error_next_action(language: str, code: str) -> str:
    if language == "ja":
        actions = {
            "missing_token": "ページを再読み込みして、もう一度操作してください。",
            "bad_token": "ページを再読み込みして、もう一度操作してください。",
            "host_not_allowed": "許可されたローカルURLから開き直してください。",
            "origin_not_allowed": "許可されたローカル画面からもう一度操作してください。",
            "loopback_only": "この端末のローカル画面から操作してください。",
            "method_not_allowed": "画面を更新して、表示された操作を選び直してください。",
            "not_found": "画面を更新して、対象を選び直してください。",
        }
        return actions.get(code, "入力内容を確認して、もう一度操作してください。")
    actions = {
        "missing_token": "Reload the page and try the action again.",
        "bad_token": "Reload the page and try the action again.",
        "host_not_allowed": "Reopen the service from an allowed local URL.",
        "origin_not_allowed": "Retry the action from the allowed local page.",
        "loopback_only": "Use the local page on this device.",
        "method_not_allowed": "Refresh the page and choose an available action.",
        "not_found": "Refresh the page and select the item again.",
    }
    return actions.get(code, "Check the submitted values and try again.")


def _validate_question_id(value) -> str:
    if not isinstance(value, str) or not SAFE_IDENTIFIER_RE.fullmatch(value):
        raise _RequestError(400, "bad_question_id", "question_id must be a safe identifier")
    return value


def _validate_run_id(value) -> str:
    if not isinstance(value, str) or not RUN_ID_RE.fullmatch(value):
        raise _RequestError(400, "bad_run_id", "run_id must be a safe run identifier")
    return value


def _validate_draft_id(value) -> str:
    if not isinstance(value, str) or "/" in value or "\\" in value or not SAFE_DRAFT_NAME_RE.fullmatch(value):
        raise _RequestError(400, "bad_draft_id", "draft_id must be a safe markdown filename")
    return value


def _validate_folder_role(value) -> str:
    if not isinstance(value, str) or value not in FOLDER_ROLE_PATHS:
        raise _RequestError(400, "bad_folder_role", "role must be one of the allowed folder roles")
    return value


def _validated_pack_id(value) -> str:
    if value is None:
        return "monthly-report"
    if not isinstance(value, str) or not SAFE_IDENTIFIER_RE.fullmatch(value):
        raise _RequestError(400, "bad_pack_id", "pack_id must be a safe identifier")
    return value


def _validated_workspace_period_id(workspace_root: Path, value) -> str:
    if not isinstance(value, str):
        validate_period_id(value)
    pack = load_bundled_pack(load_workspace(workspace_root)["pack_id"])
    return validate_period_id(value, pack["period_type"])


def _validated_style_reference_request(value) -> Optional[Dict]:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise _RequestError(400, "bad_style_reference", "style_reference must be null or an object")
    allowed = {"confirmed", "relative_path", "sha256"}
    if set(value) != allowed:
        raise _RequestError(400, "bad_style_reference", "style_reference fields are invalid")
    if value.get("confirmed") is not True:
        raise _RequestError(400, "bad_style_reference", "style_reference must be explicitly confirmed")
    relative_path = value.get("relative_path")
    sha256_value = value.get("sha256")
    if not isinstance(relative_path, str) or not isinstance(sha256_value, str):
        raise _RequestError(400, "bad_style_reference", "style_reference must include relative_path and sha256")
    return {"relative_path": relative_path, "sha256": sha256_value}


def _map_domain_error(error: Exception) -> "_RequestError":
    message = str(error)
    if "PIN verification failed" in message or "approver must match" in message:
        return _RequestError(
            403,
            "approval_denied",
            "approval credentials are invalid",
            next_action="Check the approver and PIN, then retry.",
        )
    if "run_id does not exist" in message:
        return _RequestError(404, "run_not_found", "run was not found")
    if "does not exist" in message and message.startswith("period "):
        return _RequestError(404, "period_not_found", "period was not found")
    if message.startswith("unknown question"):
        return _RequestError(404, "question_not_found", "question was not found")
    if (
        "requires ready_for_" in message
        or "requires questioning stage" in message
        or "not allowed from stage" in message
        or "invalid transition" in message
        or "already exists" in message
        or "append-only" in message
        or "approval is already in progress" in message
        or "current draft" in message
        or "source manifest" in message
    ):
        next_action = "Refresh the workspace and complete the current step first."
        if "approval is already in progress" in message:
            next_action = "Finish the current approval, or clear the stale approval lock, then retry."
        return _RequestError(
            409,
            "state_conflict",
            "requested action is not allowed in the current workspace state",
            next_action=next_action,
        )
    if message.startswith("unknown workflow pack:"):
        return _RequestError(400, "bad_pack_id", "pack_id is invalid")
    if message.startswith("period_id must match strict "):
        return _RequestError(400, "bad_period_id", message)
    if "Codex executable is unavailable" in message or "Codex executable is not runnable" in message:
        return _RequestError(503, "codex_unavailable", "Codex is not ready", next_action="Install or repair Codex CLI.")
    if "race-resistant no-follow filesystem support" in message:
        return _RequestError(503, "environment_not_ready", "server environment is not ready", next_action=message)
    return _RequestError(400, "request_error", message)


class _RequestError(Exception):
    def __init__(
        self,
        status: int,
        code: str,
        message: str,
        *,
        next_action: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
        self.next_action = next_action


def run_office_workspace_server(root: Path, language: str = "ja", port: int = 0, open_browser: bool = True) -> int:
    server = create_office_workspace_server(root, language=language, port=port)
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


__all__ = [
    "MAX_REQUEST_BYTES",
    "OfficeWorkspaceHTTPServer",
    "TOKEN_HEADER",
    "create_office_workspace_server",
    "run_office_workspace_server",
]
