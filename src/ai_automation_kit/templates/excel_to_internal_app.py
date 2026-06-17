from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from ai_automation_kit.core.models import Artifact, RunRecord
from ai_automation_kit.core.store import JsonRunStore


def run_excel_to_internal_app(config_path: Path | str, output_dir: Path | str) -> RunRecord:
    config_file = Path(config_path)
    output = Path(output_dir)
    config = json.loads(config_file.read_text(encoding="utf-8"))
    app_name = config["app_name"]
    csv_path = Path(config["csv_path"])

    started_at = _now()
    run_id = f"run-{uuid4().hex[:12]}"
    rows = _read_csv(csv_path)
    fields = _infer_fields(rows)
    quality = _analyze_data_quality(rows)
    table_name = _slug(app_name)
    artifacts = _write_app_artifacts(output, app_name, table_name, csv_path, fields, len(rows), quality)
    finished_at = _now()
    run = RunRecord(
        run_id=run_id,
        template_name="excel-to-internal-app",
        input={"app_name": app_name, "csv_path": str(csv_path), "row_count": len(rows)},
        started_at=started_at,
        finished_at=finished_at,
        status="succeeded",
        errors=[],
        artifacts=artifacts,
    )
    JsonRunStore(output).save_run(run)
    return run


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _infer_fields(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    if not rows:
        return []
    fields = []
    for name in rows[0].keys():
        values = [row.get(name, "") for row in rows if row.get(name, "") != ""]
        fields.append({"name": name, "type": _infer_type(values)})
    return fields


def _infer_type(values: list[str]) -> str:
    if values and all(_is_integer(value) for value in values):
        return "INTEGER"
    if values and all(_is_number(value) for value in values):
        return "REAL"
    if values and all(_is_date(value) for value in values):
        return "DATE"
    return "TEXT"


def _write_app_artifacts(
    output: Path,
    app_name: str,
    table_name: str,
    csv_path: Path,
    fields: list[dict[str, str]],
    row_count: int,
    quality: dict,
) -> list[Artifact]:
    output.mkdir(parents=True, exist_ok=True)
    schema = _render_schema(table_name, fields)
    fields_doc = {"app_name": app_name, "table_name": table_name, "fields": fields}
    admin_view = _render_admin_view(app_name, table_name, fields)
    report = _render_migration_report(app_name, csv_path, table_name, fields, row_count, quality)

    (output / "schema.sql").write_text(schema, encoding="utf-8")
    (output / "fields.json").write_text(json.dumps(fields_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "data-quality-report.json").write_text(json.dumps(quality, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "admin-view.md").write_text(admin_view, encoding="utf-8")
    (output / "migration-report.md").write_text(report, encoding="utf-8")
    return [
        Artifact(kind="sql", path="schema.sql"),
        Artifact(kind="json", path="fields.json"),
        Artifact(kind="json", path="data-quality-report.json"),
        Artifact(kind="markdown", path="admin-view.md"),
        Artifact(kind="markdown", path="migration-report.md"),
    ]


def _render_schema(table_name: str, fields: list[dict[str, str]]) -> str:
    lines = [f"CREATE TABLE {table_name} ("]
    column_lines = [f"  {field['name']} {field['type']}" for field in fields]
    lines.append(",\n".join(column_lines))
    lines.append(");\n")
    return "\n".join(lines)


def _render_admin_view(app_name: str, table_name: str, fields: list[dict[str, str]]) -> str:
    lines = [f"# Admin View: {app_name}", "", f"Table: `{table_name}`", "", "## Fields", ""]
    for field in fields:
        lines.append(f"- `{field['name']}`: {field['type']}")
    lines.append("")
    return "\n".join(lines)


def _render_migration_report(
    app_name: str,
    csv_path: Path,
    table_name: str,
    fields: list[dict[str, str]],
    row_count: int,
    quality: dict,
) -> str:
    lines = [
        f"# Migration Report: {app_name}",
        "",
        f"- Source CSV: `{csv_path}`",
        f"- Target table: `{table_name}`",
        f"- Rows inspected: `{row_count}`",
        "",
        "## Inferred Fields",
        "",
    ]
    for field in fields:
        lines.append(f"- `{field['name']}` -> `{field['type']}`")
    lines.extend(["", "## Data Quality", ""])
    for column in quality["columns"]:
        lines.append(
            f"- `{column['name']}`: blanks `{column['blank_count']}`, unique values `{column['unique_count']}`"
        )
    lines.extend(
        [
            "",
            "## Next Steps",
            "",
            "- Review field names and types before importing production data.",
            "- Resolve blank required fields before using the generated schema in production.",
            "- Add permissions and audit logging before exposing this as an internal app.",
            "",
        ]
    )
    return "\n".join(lines)


def _analyze_data_quality(rows: list[dict[str, str]]) -> dict:
    if not rows:
        return {"row_count": 0, "columns": []}
    columns = []
    for name in rows[0].keys():
        values = [row.get(name, "") for row in rows]
        columns.append(
            {
                "name": name,
                "blank_count": sum(1 for value in values if value == ""),
                "unique_count": len(set(values)),
                "sample_values": [value for value in values[:3]],
            }
        )
    return {"row_count": len(rows), "columns": columns}


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    return slug or "internal_app"


def _is_integer(value: str) -> bool:
    return bool(re.fullmatch(r"-?\d+", value))


def _is_number(value: str) -> bool:
    return bool(re.fullmatch(r"-?\d+(\.\d+)?", value))


def _is_date(value: str) -> bool:
    return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value))


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
