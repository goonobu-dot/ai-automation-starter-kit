from __future__ import annotations

import subprocess
import sys
import stat
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_first_start_script_creates_beginner_project_without_package_install(tmp_path):
    output = tmp_path / "first-project"
    venv = tmp_path / "venv"

    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "first_start.py"),
            "--output",
            str(output),
            "--venv",
            str(venv),
            "--language",
            "en",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert "READY" in completed.stdout
    assert (output / "START_HERE.html").exists()
    assert (output / "AI_NEXT_STEP.md").exists()
    assert (venv / "pyvenv.cfg").exists()
    assert '<html lang="en">' in (output / "START_HERE.html").read_text()

    second = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "first_start.py"),
            "--output",
            str(output),
            "--venv",
            str(venv),
            "--language",
            "en",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert second.returncode == 0, second.stderr
    assert "ALREADY READY" in second.stdout


def test_repository_has_double_click_launchers_and_ai_start_prompts():
    mac_launcher = ROOT / "START_HERE.command"
    windows_launcher = ROOT / "START_HERE_WINDOWS.bat"
    japanese_prompt = ROOT / "START_WITH_AI.ja.txt"
    english_prompt = ROOT / "START_WITH_AI.txt"

    assert mac_launcher.exists()
    assert windows_launcher.exists()
    assert japanese_prompt.exists()
    assert english_prompt.exists()
    assert mac_launcher.stat().st_mode & stat.S_IXUSR

    mac = mac_launcher.read_text(encoding="utf-8")
    windows = windows_launcher.read_text(encoding="utf-8")
    assert 'cd "$SCRIPT_DIR"' in mac
    assert 'python3 scripts/first_start.py --open' in mac
    assert "APIキー" in mac
    assert "scripts\\first_start.py --open" in windows
    assert "START_WITH_AI.ja.txt" in japanese_prompt.name
    assert "一度に一問" in japanese_prompt.read_text(encoding="utf-8")
    assert "one question at a time" in english_prompt.read_text(encoding="utf-8")
