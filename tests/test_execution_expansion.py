import json

from ai_automation_kit.cli import main
from ai_automation_kit.core.operator_console import generate_complete_workspace


def test_main_runs_flow_export_for_n8n(tmp_path):
    output = tmp_path / "exports"

    exit_code = main(
        [
            "flow-export",
            "--flow-id",
            "invoice-document-followup",
            "--target",
            "n8n",
            "--output",
            str(output),
        ]
    )

    assert exit_code == 0
    assert (output / "START_HERE_FLOW_EXPORT.md").exists()
    assert (output / "n8n_workflow.json").exists()
    assert (output / "mapping_notes.md").exists()
    workflow = json.loads((output / "n8n_workflow.json").read_text())
    assert workflow["name"] == "Invoice and Document Follow-up"


def test_main_runs_deployment_pack_for_coolify(tmp_path):
    output = tmp_path / "deploy"

    exit_code = main(
        [
            "deployment-pack",
            "--flow-id",
            "invoice-document-followup",
            "--provider",
            "coolify",
            "--connectors",
            "gmail,google-sheets",
            "--output",
            str(output),
        ]
    )

    assert exit_code == 0
    assert (output / "START_HERE_DEPLOYMENT_PACK.md").exists()
    assert (output / "docker-compose.yml").exists()
    assert (output / "coolify_env_import.txt").exists()
    payload = json.loads((output / "deployment_pack.json").read_text())
    assert payload["provider"] == "coolify"


def test_main_runs_runtime_safety_pack(tmp_path):
    output = tmp_path / "runtime"

    exit_code = main(["runtime-safety", "--flow-id", "invoice-document-followup", "--output", str(output)])

    assert exit_code == 0
    assert (output / "approval_policy.md").exists()
    assert (output / "retry_policy.json").exists()
    assert (output / "idempotency_keys.md").exists()
    policy = json.loads((output / "runtime_safety.json").read_text())
    assert policy["status"] == "ready"


def test_main_runs_secrets_bootstrap_pack(tmp_path):
    output = tmp_path / "secrets"

    exit_code = main(
        [
            "secrets-bootstrap",
            "--flow-id",
            "invoice-document-followup",
            "--provider",
            "infisical",
            "--connectors",
            "gmail,google-sheets",
            "--output",
            str(output),
        ]
    )

    assert exit_code == 0
    assert (output / "secrets_manifest.json").exists()
    assert (output / "infisical_import.env").exists()
    assert (output / "secret_ownership.md").exists()


def test_main_runs_document_intake_pack(tmp_path):
    output = tmp_path / "documents"

    exit_code = main(["document-intake", "--flow-id", "invoice-document-followup", "--mode", "advanced", "--output", str(output)])

    assert exit_code == 0
    assert (output / "START_HERE_DOCUMENT_INTAKE.md").exists()
    assert (output / "markitdown_config.json").exists()
    assert (output / "docling_config.json").exists()
    assert (output / "document_pipeline.md").exists()


def test_main_runs_observability_pack(tmp_path):
    output = tmp_path / "observability"

    exit_code = main(["observability-pack", "--flow-id", "invoice-document-followup", "--output", str(output)])

    assert exit_code == 0
    assert (output / "langfuse_env.example").exists()
    assert (output / "trace_model.md").exists()
    assert (output / "eval_dataset.csv").exists()
    payload = json.loads((output / "observability_pack.json").read_text())
    assert payload["status"] == "ready"


def test_main_runs_state_backend_pack(tmp_path):
    output = tmp_path / "state"

    exit_code = main(["state-backend", "--flow-id", "invoice-document-followup", "--backend", "supabase", "--output", str(output)])

    assert exit_code == 0
    assert (output / "START_HERE_STATE_BACKEND.md").exists()
    assert (output / "supabase_schema.sql").exists()
    assert (output / "operator_state_model.md").exists()
    payload = json.loads((output / "state_backend.json").read_text())
    assert payload["backend"] == "supabase"


def test_complete_workspace_includes_execution_and_operations_packs(tmp_path):
    output = tmp_path / "complete"

    payload = generate_complete_workspace(
        flow_id="invoice-document-followup",
        industry="finance",
        client_type="local-business",
        niche="accounting",
        approver="owner@example.com",
        output=output,
    )

    assert payload["status"] == "ready_to_share"
    assert (output / "flow_exports" / "n8n" / "n8n_workflow.json").exists()
    assert (output / "flow_exports" / "activepieces" / "activepieces_flow.json").exists()
    assert (output / "flow_exports" / "windmill" / "windmill_flow.yaml").exists()
    assert (output / "deployment_packs" / "coolify" / "deployment_pack.json").exists()
    assert (output / "deployment_packs" / "cloudflare-agents" / "deployment_pack.json").exists()
    assert (output / "deployment_packs" / "supabase" / "deployment_pack.json").exists()
    assert (output / "runtime_safety" / "runtime_safety.json").exists()
    assert (output / "secrets_bootstrap" / "secrets_manifest.json").exists()
    assert (output / "document_intake" / "document_pipeline.md").exists()
    assert (output / "observability_pack" / "observability_pack.json").exists()
    assert (output / "state_backend" / "state_backend.json").exists()
