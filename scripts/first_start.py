from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import venv
import webbrowser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a safe working automation example without API keys or package installation."
    )
    parser.add_argument("--output", default="my-first-automation")
    parser.add_argument("--venv", default=str(ROOT / ".venv"))
    parser.add_argument("--language", choices=["ja", "en"], default="ja")
    parser.add_argument("--flow-id")
    parser.add_argument("--industry", default="finance")
    parser.add_argument("--client-type", default="local-business")
    parser.add_argument("--niche", default="accounting")
    parser.add_argument("--approver", default="local-operator")
    parser.add_argument("--open", action="store_true", help="Open START_HERE.html after creation.")
    args = parser.parse_args()

    if sys.version_info < (3, 9):
        print("Python 3.9 or newer is required.", file=sys.stderr)
        return 2

    output = Path(args.output).expanduser().resolve()
    venv_dir = Path(args.venv).expanduser().resolve()
    existing_start = _existing_start_page(output)
    if existing_start is not None:
        print("ALREADY READY" if args.language == "en" else "すでに準備できています")
        print(f"Open this file: {existing_start}" if args.language == "en" else f"この画面を開きます: {existing_start}")
        if args.open:
            webbrowser.open(existing_start.as_uri())
        return 0

    python_bin = _venv_python(venv_dir)
    if not python_bin.exists():
        print(f"Creating a private Python environment: {venv_dir}")
        venv.EnvBuilder(with_pip=False).create(venv_dir)

    command = [
        str(python_bin),
        "-m",
        "ai_automation_kit.cli",
        "start",
        "--output",
        str(output),
        "--language",
        args.language,
        "--industry",
        args.industry,
        "--client-type",
        args.client_type,
        "--niche",
        args.niche,
        "--approver",
        args.approver,
    ]
    if args.flow_id:
        command.extend(["--flow-id", args.flow_id])

    env = os.environ.copy()
    source = str(ROOT / "src")
    env["PYTHONPATH"] = source if not env.get("PYTHONPATH") else f"{source}{os.pathsep}{env['PYTHONPATH']}"
    completed = subprocess.run(command, cwd=ROOT, env=env, check=False)
    if completed.returncode != 0:
        return completed.returncode

    start_here = output / "START_HERE.html"
    print("")
    print("READY")
    print(f"Open this file: {start_here}")
    if args.open:
        webbrowser.open(start_here.as_uri())
    return 0


def _venv_python(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _existing_start_page(output: Path) -> Path | None:
    manifest = output / "first_project.json"
    start_here = output / "START_HERE.html"
    if not manifest.is_file() or not start_here.is_file():
        return None
    try:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if payload.get("safe_mode") != "local_dry_run" or payload.get("external_actions") != "blocked":
        return None
    return start_here


if __name__ == "__main__":
    raise SystemExit(main())
