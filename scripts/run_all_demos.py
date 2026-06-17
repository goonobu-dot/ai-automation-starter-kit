from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = ROOT / ".tmp" / "all-templates"

COMMANDS = [
    [
        "research-agent",
        "--config",
        "examples/research-agent/sample_research.json",
        "--output",
        ".tmp/all-templates/research-agent",
    ],
    [
        "docs-rag",
        "--config",
        "examples/docs-rag/sample_docs_rag.json",
        "--output",
        ".tmp/all-templates/docs-rag",
    ],
    [
        "internal-ai-workflow",
        "--config",
        "examples/internal-ai-workflow/sample_inquiry.json",
        "--output",
        ".tmp/all-templates/internal-ai-workflow",
    ],
    [
        "excel-to-internal-app",
        "--config",
        "examples/excel-to-internal-app/sample_app.json",
        "--output",
        ".tmp/all-templates/excel-to-internal-app",
    ],
    [
        "delivery-pipeline",
        "--config",
        "examples/delivery-pipeline/sample_delivery_pipeline.json",
        "--output",
        ".tmp/all-templates/delivery-pipeline",
    ],
]


def main() -> int:
    if OUTPUT_ROOT.exists():
        shutil.rmtree(OUTPUT_ROOT)

    env = os.environ.copy()
    src_path = str(ROOT / "src")
    env["PYTHONPATH"] = src_path if not env.get("PYTHONPATH") else f"{src_path}{os.pathsep}{env['PYTHONPATH']}"

    for command in COMMANDS:
        full_command = [sys.executable, "-m", "ai_automation_kit.cli", *command]
        print("$ " + " ".join(full_command))
        subprocess.run(full_command, cwd=ROOT, env=env, check=True)

    print(f"Wrote demo outputs to {OUTPUT_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
