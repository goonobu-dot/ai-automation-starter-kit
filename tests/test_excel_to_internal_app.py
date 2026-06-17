import json

from ai_automation_kit.templates.excel_to_internal_app import run_excel_to_internal_app


def test_excel_to_internal_app_generates_schema_and_migration_report(tmp_path):
    csv_file = tmp_path / "customers.csv"
    csv_file.write_text(
        "customer_id,name,signup_date,monthly_fee,active\n"
        "1,Ada,2026-06-01,29.5,true\n"
        "2,Grace,2026-06-02,35.0,false\n",
        encoding="utf-8",
    )
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"app_name": "Customer CRM", "csv_path": str(csv_file)}), encoding="utf-8")
    output = tmp_path / "out"

    run = run_excel_to_internal_app(config_path=config, output_dir=output)

    assert run.status == "succeeded"
    schema = (output / "schema.sql").read_text()
    fields = json.loads((output / "fields.json").read_text())
    report = (output / "migration-report.md").read_text()
    validation = json.loads((output / "data-quality-report.json").read_text())
    assert "CREATE TABLE customer_crm" in schema
    assert "customer_id INTEGER" in schema
    assert "signup_date DATE" in schema
    assert "monthly_fee REAL" in schema
    assert fields["fields"][0]["name"] == "customer_id"
    assert "Customer CRM" in report
    assert "## Data Quality" in report
    assert "## Permissions" in report
    assert "## Suggested App Screens" in report
    assert validation["row_count"] == 2
    assert validation["columns"][0]["name"] == "customer_id"
    assert validation["columns"][0]["blank_count"] == 0
    assert (output / "app-spec.md").exists()
    assert "## Roles" in (output / "app-spec.md").read_text()
    artifact_index = (output / "artifact_index.md").read_text()
    assert "Artifact Index: excel-to-internal-app" in artifact_index
    assert "migration-report.md" in artifact_index
    assert (output / "runs" / f"{run.run_id}.json").exists()


def test_excel_to_internal_app_defaults_unknown_values_to_text(tmp_path):
    csv_file = tmp_path / "inventory.csv"
    csv_file.write_text("sku,mixed\nA-1,alpha\nA-2,123\n", encoding="utf-8")
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"app_name": "Inventory", "csv_path": str(csv_file)}), encoding="utf-8")

    run_excel_to_internal_app(config_path=config, output_dir=tmp_path / "out")

    schema = (tmp_path / "out" / "schema.sql").read_text()
    assert "mixed TEXT" in schema
