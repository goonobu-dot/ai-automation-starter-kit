from __future__ import annotations

import base64
import json
import stat
import threading
import urllib.error
import urllib.request
from pathlib import Path

from ai_automation_kit.core.manual_studio import build_manual_with_codex
from ai_automation_kit.core.manual_studio import create_manual_studio
from ai_automation_kit.core.manual_studio import prepare_manual_recordings
from ai_automation_kit.core.manual_studio_frame_picker import TOKEN_HEADER
from ai_automation_kit.core.manual_studio_frame_picker import create_manual_frame_picker_server


def _write_executable(path: Path, source: str) -> Path:
    path.write_text(source, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


def _workspace(tmp_path: Path) -> tuple[Path, list[dict]]:
    workspace = tmp_path / "manual"
    create_manual_studio(workspace, name="Visual choice", language="en")
    (workspace / "01_RECORDINGS" / "work.mp4").write_bytes(b"fixture-video")
    ffprobe = _write_executable(
        tmp_path / "ffprobe",
        "#!/usr/bin/env python3\nimport json\nprint(json.dumps({'format': {'duration': '12.5'}, 'streams': [{'codec_type': 'video', 'width': 1280, 'height': 720}]}))\n",
    )
    ffmpeg = _write_executable(
        tmp_path / "ffmpeg",
        """#!/usr/bin/env python3
import base64
import pathlib
import sys
pattern = pathlib.Path(sys.argv[-1])
png = base64.b64decode(%r)
for index in (1, 2):
    path = pathlib.Path(str(pattern).replace("%%03d", f"{index:03d}"))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)
print("[Parsed_showinfo_0] n:0 pts_time:0", file=sys.stderr)
print("[Parsed_showinfo_0] n:1 pts_time:7.5", file=sys.stderr)
"""
        % base64.b64encode(
            base64.b64decode(
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
            )
        ),
    )
    prepare_manual_recordings(workspace, ffmpeg=str(ffmpeg), ffprobe=str(ffprobe))
    manifest = json.loads((workspace / ".system" / "capture_manifest.json").read_text(encoding="utf-8"))
    frames = manifest["videos"][0]["frames"]
    result = {
        "title": "Visual choice",
        "summary": "Choose the clearest evidence image.",
        "steps": [
            {
                "order": 1,
                "title": "Complete the task",
                "instruction": "Complete the visible task.",
                "frame_path": frames[1]["path"],
                "source_video": "01_RECORDINGS/work.mp4",
                "timestamp_seconds": frames[1]["timestamp_seconds"],
                "warning": "",
            }
        ],
        "exceptions": [],
        "missing_questions": [
            {
                "question": "Who confirms the completed task?",
                "reason": "The recording does not show the reviewer.",
            }
        ],
    }
    result_path = tmp_path / "result.json"
    result_path.write_text(json.dumps(result), encoding="utf-8")
    codex = _write_executable(
        tmp_path / "codex",
        """#!/usr/bin/env python3
import pathlib
import shutil
import sys
if sys.argv[1:3] == ["login", "status"]:
    raise SystemExit(0)
output = pathlib.Path(sys.argv[sys.argv.index("--output-last-message") + 1])
shutil.copyfile(%r, output)
sys.stdin.read()
"""
        % str(result_path),
    )
    build_manual_with_codex(workspace, executable=str(codex), title="Visual choice")
    return workspace, frames


def _request(server, method: str, path: str, payload=None):
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {
        TOKEN_HEADER: server.session_token,
        "Host": "127.0.0.1:{}".format(server.server_address[1]),
    }
    if body is not None:
        headers.update(
            {
                "Content-Type": "application/json",
                "Origin": "http://127.0.0.1:{}".format(server.server_address[1]),
            }
        )
    request = urllib.request.Request(
        "http://127.0.0.1:{}{}".format(server.server_address[1], path),
        data=body,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=3) as response:
            return response.status, response.headers, response.read()
    except urllib.error.HTTPError as error:
        return error.code, error.headers, error.read()


def test_frame_picker_lists_candidates_serves_images_and_saves_selection(tmp_path):
    workspace, frames = _workspace(tmp_path)
    server = create_manual_frame_picker_server(workspace, port=0)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
    thread.start()
    try:
        status, headers, body = _request(server, "GET", "/?token=" + server.session_token)
        assert status == 200
        page = body.decode("utf-8")
        assert "Choose better step images" in page
        assert "Nearby frames" in page
        assert "Full recording" in page
        assert "Currently used in the manual" in page
        assert "Initially selected by AI" not in page
        assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]

        status, _, body = _request(server, "GET", "/api/state")
        state = json.loads(body)
        assert status == 200
        assert state["steps"][0]["selected_frame_path"] == frames[1]["path"]
        assert len(state["steps"][0]["candidates"]) == 2
        first_id = state["steps"][0]["candidates"][0]["frame_id"]

        status, headers, image = _request(server, "GET", "/frames/" + first_id)
        assert status == 200
        assert headers["Content-Type"] == "image/png"
        assert image.startswith(b"\x89PNG")

        status, _, body = _request(
            server,
            "POST",
            "/api/selections",
            {"selections": [{"order": 1, "frame_id": first_id}]},
        )
        saved = json.loads(body)
        assert status == 200
        assert saved["ok"] is True
        assert saved["changed"] == 1
        plan = json.loads((workspace / "04_DRAFT_MANUAL" / "manual_plan.json").read_text(encoding="utf-8"))
        assert plan["steps"][0]["frame_path"] == frames[0]["path"]

        status, _, body = _request(server, "GET", "/manual?token=" + server.session_token)
        manual = body.decode("utf-8")
        assert status == 200
        assert "/answer-guide?token=" + server.session_token in manual
        assert "../05_REVIEW/ANSWER_GUIDE.html" not in manual

        status, _, body = _request(server, "GET", "/answer-guide?token=" + server.session_token)
        answer_guide = body.decode("utf-8")
        assert status == 200
        assert "Complete missing details with AI" in answer_guide
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()


def test_frame_picker_rejects_state_change_without_origin(tmp_path):
    workspace, _ = _workspace(tmp_path)
    server = create_manual_frame_picker_server(workspace, port=0)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
    thread.start()
    try:
        request = urllib.request.Request(
            "http://127.0.0.1:{}/api/selections".format(server.server_address[1]),
            data=b'{"selections":[]}',
            headers={TOKEN_HEADER: server.session_token, "Content-Type": "application/json"},
            method="POST",
        )
        try:
            urllib.request.urlopen(request, timeout=3)
            raise AssertionError("request unexpectedly succeeded")
        except urllib.error.HTTPError as error:
            assert error.code == 403
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()
