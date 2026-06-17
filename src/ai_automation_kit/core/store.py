from __future__ import annotations

import json
from pathlib import Path

from ai_automation_kit.core.models import RunRecord, SourceRecord


class JsonRunStore:
    def __init__(self, base_dir: Path | str):
        self.base_dir = Path(base_dir)

    def save_run(self, run: RunRecord) -> Path:
        path = self.base_dir / "runs" / f"{run.run_id}.json"
        self._write_json(path, run.to_dict())
        return path

    def save_source(self, source: SourceRecord) -> Path:
        path = self.base_dir / "sources" / f"{source.source_id}.json"
        self._write_json(path, source.to_dict())
        return path

    @staticmethod
    def _write_json(path: Path, data: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
