from __future__ import annotations

import json
from pathlib import Path

from ai_automation_kit.core.flows import get_flow


def _parse_connectors(connectors: str) -> list[str]:
    items = [item.strip() for item in connectors.split(",")]
    return [item for item in items if item]


def _connector_env_keys(connector: str) -> list[str]:
    mapping = {
        "gmail": ["GMAIL_CLIENT_ID", "GMAIL_CLIENT_SECRET", "GMAIL_REFRESH_TOKEN"],
        "google-sheets": ["GOOGLE_SHEETS_SPREADSHEET_ID", "GOOGLE_SERVICE_ACCOUNT_JSON"],
        "line": ["LINE_CHANNEL_ACCESS_TOKEN", "LINE_CHANNEL_SECRET"],
        "slack": ["SLACK_BOT_TOKEN", "SLACK_SIGNING_SECRET"],
        "storage-folder": ["LOCAL_INPUT_FOLDER", "LOCAL_OUTPUT_FOLDER"],
        "webhook": ["WEBHOOK_SHARED_SECRET"],
        "local-folder": ["LOCAL_INPUT_FOLDER", "LOCAL_OUTPUT_FOLDER"],
    }
    return mapping.get(connector, [connector.upper().replace("-", "_") + "_VALUE"])


def generate_flow_export(flow_id: str, target: str, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    flow = get_flow(flow_id)
    payload = {
        "status": "ready",
        "flow_id": flow["id"],
        "flow_name": flow["name"],
        "target": target,
        "step_count": len(flow["steps"]),
    }
    (output / "flow_export.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "START_HERE_FLOW_EXPORT.md").write_text(_render_flow_export_start(flow, payload), encoding="utf-8")
    (output / "mapping_notes.md").write_text(_render_flow_export_mapping_notes(flow, target), encoding="utf-8")
    if target == "n8n":
        (output / "n8n_workflow.json").write_text(json.dumps(_render_n8n_workflow(flow), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (output / "n8n_import_notes.md").write_text(_render_n8n_import_notes(flow), encoding="utf-8")
    elif target == "activepieces":
        (output / "activepieces_flow.json").write_text(
            json.dumps(_render_activepieces_flow(flow), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (output / "activepieces_piece_notes.md").write_text(_render_activepieces_notes(flow), encoding="utf-8")
    elif target == "windmill":
        (output / "windmill_flow.yaml").write_text(_render_windmill_flow(flow), encoding="utf-8")
        (output / "windmill_script.ts").write_text(_render_windmill_script(flow), encoding="utf-8")
        (output / "windmill_webhook_notes.md").write_text(_render_windmill_notes(flow), encoding="utf-8")
    else:
        raise ValueError(f"Unsupported flow export target: {target}")
    return payload


def generate_deployment_pack(flow_id: str, provider: str, connectors: str, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    flow = get_flow(flow_id)
    connector_list = _parse_connectors(connectors)
    payload = {
        "status": "ready",
        "flow_id": flow["id"],
        "provider": provider,
        "connectors": connector_list,
        "starter_type": provider,
    }
    (output / "deployment_pack.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "START_HERE_DEPLOYMENT_PACK.md").write_text(_render_deployment_start(flow, payload), encoding="utf-8")
    (output / "deployment_decision.md").write_text(_render_deployment_decision(payload), encoding="utf-8")
    (output / "env.example").write_text(_render_env_example(connector_list), encoding="utf-8")
    if provider == "coolify":
        (output / "docker-compose.yml").write_text(_render_coolify_compose(), encoding="utf-8")
        (output / "coolify_env_import.txt").write_text(_render_env_import(connector_list), encoding="utf-8")
        (output / "coolify_runbook.md").write_text(_render_coolify_runbook(flow), encoding="utf-8")
    elif provider == "cloudflare-agents":
        (output / "wrangler.toml").write_text(_render_cloudflare_wrangler(), encoding="utf-8")
        (output / "agent.ts").write_text(_render_cloudflare_agent(flow), encoding="utf-8")
        (output / "cloudflare_agents_runbook.md").write_text(_render_cloudflare_runbook(flow), encoding="utf-8")
    elif provider == "supabase":
        (output / "supabase_schema.sql").write_text(_render_supabase_schema(), encoding="utf-8")
        (output / "supabase_functions.ts").write_text(_render_supabase_functions(flow), encoding="utf-8")
        (output / "supabase_runbook.md").write_text(_render_supabase_runbook(flow), encoding="utf-8")
    else:
        raise ValueError(f"Unsupported deployment provider: {provider}")
    return payload


def generate_runtime_safety_pack(flow_id: str, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    flow = get_flow(flow_id)
    payload = {
        "status": "ready",
        "flow_id": flow["id"],
        "approval_steps": [step["id"] for step in flow["steps"] if step["human_approval"]],
        "retry_policy": {"max_retries": 3, "backoff": "exponential", "dead_letter_queue": True},
    }
    (output / "runtime_safety.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "approval_policy.md").write_text(_render_approval_policy(flow), encoding="utf-8")
    (output / "retry_policy.json").write_text(json.dumps(payload["retry_policy"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "idempotency_keys.md").write_text(_render_idempotency_keys(flow), encoding="utf-8")
    (output / "queue_design.md").write_text(_render_queue_design(), encoding="utf-8")
    (output / "rollback_runbook.md").write_text(_render_runtime_rollback(), encoding="utf-8")
    (output / "run_history_schema.json").write_text(json.dumps(_runtime_history_schema(flow), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def generate_secrets_bootstrap(flow_id: str, provider: str, connectors: str, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    flow = get_flow(flow_id)
    connector_list = _parse_connectors(connectors)
    secrets = []
    for connector in connector_list:
        for key in _connector_env_keys(connector):
            secrets.append({"name": key, "connector": connector, "owner": "human", "rotation": "quarterly"})
    payload = {"status": "ready", "flow_id": flow["id"], "provider": provider, "secrets": secrets}
    (output / "secrets_manifest.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "infisical_import.env").write_text(_render_env_import(connector_list), encoding="utf-8")
    (output / "secret_ownership.md").write_text(_render_secret_ownership(flow, secrets), encoding="utf-8")
    (output / "secret_bootstrap_runbook.md").write_text(_render_secret_bootstrap_runbook(provider), encoding="utf-8")
    return payload


def generate_document_intake_pack(flow_id: str, mode: str, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    flow = get_flow(flow_id)
    payload = {"status": "ready", "flow_id": flow["id"], "mode": mode}
    (output / "document_intake.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "START_HERE_DOCUMENT_INTAKE.md").write_text(_render_document_start(flow, mode), encoding="utf-8")
    (output / "markitdown_config.json").write_text(json.dumps(_markitdown_config(flow), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "docling_config.json").write_text(json.dumps(_docling_config(flow, mode), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "document_pipeline.md").write_text(_render_document_pipeline(), encoding="utf-8")
    return payload


def generate_observability_pack(flow_id: str, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    flow = get_flow(flow_id)
    payload = {"status": "ready", "flow_id": flow["id"], "provider": "langfuse"}
    (output / "observability_pack.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "langfuse_env.example").write_text("LANGFUSE_PUBLIC_KEY=\nLANGFUSE_SECRET_KEY=\nLANGFUSE_HOST=\n", encoding="utf-8")
    (output / "trace_model.md").write_text(_render_trace_model(), encoding="utf-8")
    (output / "eval_dataset.csv").write_text(_render_eval_dataset(flow), encoding="utf-8")
    (output / "prompt_review_checklist.md").write_text(_render_prompt_review_checklist(), encoding="utf-8")
    return payload


def generate_state_backend_pack(flow_id: str, backend: str, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    flow = get_flow(flow_id)
    payload = {"status": "ready", "flow_id": flow["id"], "backend": backend}
    (output / "state_backend.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "START_HERE_STATE_BACKEND.md").write_text(_render_state_backend_start(flow, backend), encoding="utf-8")
    (output / "operator_state_model.md").write_text(_render_operator_state_model(), encoding="utf-8")
    if backend == "supabase":
        (output / "supabase_schema.sql").write_text(_render_supabase_state_schema(), encoding="utf-8")
    elif backend == "cloudflare-agents":
        (output / "agent_state.ts").write_text(_render_cloudflare_state_agent(), encoding="utf-8")
    else:
        raise ValueError(f"Unsupported state backend: {backend}")
    return payload


def _render_flow_export_start(flow: dict, payload: dict) -> str:
    return "\n".join(
        [
            "# Flow Export Starter",
            "",
            f"- Flow: `{flow['name']}`",
            f"- Target: `{payload['target']}`",
            "",
            "Use this folder to move the local dry-run design into a real execution engine without losing approval steps.",
            "",
        ]
    )


def _render_flow_export_mapping_notes(flow: dict, target: str) -> str:
    lines = ["# Mapping Notes", "", f"Target: `{target}`", ""]
    for step in flow["steps"]:
        lines.append(f"- `{step['id']}` -> `{step['tool']}` -> approval=`{step['human_approval']}`")
    return "\n".join(lines) + "\n"


def _render_n8n_workflow(flow: dict) -> dict:
    nodes = []
    connections = {}
    for index, step in enumerate(flow["steps"], start=1):
        node_name = step["id"]
        nodes.append(
            {
                "id": str(index),
                "name": node_name,
                "type": "n8n-nodes-base.code" if not step["human_approval"] else "n8n-nodes-base.manualTrigger",
                "position": [index * 220, 120],
                "parameters": {
                    "language": "python",
                    "notes": step["name"],
                    "tool": step["tool"],
                    "input": step["input"],
                    "output": step["output"],
                },
            }
        )
        if index < len(flow["steps"]):
            connections[node_name] = {"main": [[{"node": flow["steps"][index]["id"], "type": "main", "index": 0}]]}
    return {"name": flow["name"], "nodes": nodes, "connections": connections}


def _render_n8n_import_notes(flow: dict) -> str:
    return "\n".join(
        [
            "# n8n Import Notes",
            "",
            "1. Import `n8n_workflow.json` into n8n.",
            "2. Replace code nodes with native integrations where possible.",
            "3. Keep approval steps manual until production review is complete.",
            f"4. Use the flow id `{flow['id']}` as the workflow tag.",
            "",
        ]
    )


def _render_activepieces_flow(flow: dict) -> dict:
    return {
        "name": flow["name"],
        "trigger": {"name": "manual", "displayName": "Manual Trigger"},
        "steps": [
            {
                "name": step["id"],
                "displayName": step["name"],
                "settings": {"tool": step["tool"], "input": step["input"], "output": step["output"]},
                "type": "CODE" if not step["human_approval"] else "PIECE",
            }
            for step in flow["steps"]
        ],
    }


def _render_activepieces_notes(flow: dict) -> str:
    return "\n".join(
        [
            "# Activepieces Piece Notes",
            "",
            "Treat each external connector as a reusable piece with a stable schema.",
            "Map approval steps to human review pieces or MCP-driven operator checkpoints.",
            f"Recommended starter flow: `{flow['id']}`.",
            "",
        ]
    )


def _render_windmill_flow(flow: dict) -> str:
    lines = [f"name: {flow['id']}", "summary: flow export from ai-automation-kit", "steps:"]
    for step in flow["steps"]:
        lines.extend(
            [
                f"  - id: {step['id']}",
                f"    summary: {step['name']}",
                "    script: ./windmill_script.ts",
            ]
        )
    return "\n".join(lines) + "\n"


def _render_windmill_script(flow: dict) -> str:
    return "\n".join(
        [
            "export async function main(input: Record<string, unknown>) {",
            f"  return {{ flowId: \"{flow['id']}\", received: input, status: \"dry-run\" }};",
            "}",
            "",
        ]
    )


def _render_windmill_notes(flow: dict) -> str:
    return "\n".join(
        [
            "# Windmill Webhook Notes",
            "",
            "Use the generated script as the first script in a Windmill flow.",
            "Windmill can turn the script into a webhook and UI after the local dry-run is proven.",
            f"Preserve human approval steps from `{flow['id']}`.",
            "",
        ]
    )


def _render_deployment_start(flow: dict, payload: dict) -> str:
    return "\n".join(
        [
            "# Deployment Pack",
            "",
            f"- Flow: `{flow['name']}`",
            f"- Provider: `{payload['provider']}`",
            "",
            "This pack is a starter, not an auto-deployer. A human still owns billing, domains, and secrets.",
            "",
        ]
    )


def _render_deployment_decision(payload: dict) -> str:
    return "\n".join(
        [
            "# Deployment Decision",
            "",
            f"- Provider: `{payload['provider']}`",
            f"- Connectors: `{', '.join(payload['connectors']) or 'none'}`",
            "- Keep production webhooks, schedulers, and outbound messages off until dry-run review is complete.",
            "",
        ]
    )


def _render_env_example(connectors: list[str]) -> str:
    keys = []
    for connector in connectors:
        keys.extend(_connector_env_keys(connector))
    if not keys:
        keys = ["FLOW_ID"]
    return "\n".join(f"{key}=" for key in keys) + "\n"


def _render_env_import(connectors: list[str]) -> str:
    return _render_env_example(connectors)


def _render_coolify_compose() -> str:
    return "\n".join(
        [
            "services:",
            "  automation-kit:",
            "    image: python:3.11-slim",
            "    working_dir: /app",
            "    command: python scripts/run_automation.py",
            "    env_file:",
            "      - ./.env",
            "    volumes:",
            "      - ./flow_project:/app",
            "",
        ]
    )


def _render_coolify_runbook(flow: dict) -> str:
    return "\n".join(
        [
            "# Coolify Runbook",
            "",
            "1. Create a new application in Coolify.",
            "2. Upload this folder or point Coolify to the repo.",
            "3. Import the env values from `coolify_env_import.txt`.",
            "4. Do one no-send dry-run before enabling schedules.",
            f"5. Review approval steps from `{flow['id']}`.",
            "",
        ]
    )


def _render_cloudflare_wrangler() -> str:
    return "\n".join(
        [
            'name = "ai-automation-kit-agent"',
            'main = "agent.ts"',
            'compatibility_date = "2026-06-25"',
            "",
        ]
    )


def _render_cloudflare_agent(flow: dict) -> str:
    return "\n".join(
        [
            "export default {",
            "  async fetch() {",
            f"    return new Response(JSON.stringify({{ flowId: \"{flow['id']}\", status: \"review-first\" }}), {{ headers: {{ \"content-type\": \"application/json\" }} }});",
            "  },",
            "};",
            "",
        ]
    )


def _render_cloudflare_runbook(flow: dict) -> str:
    return "\n".join(
        [
            "# Cloudflare Agents Runbook",
            "",
            "Use this when you want a lightweight stateful deployment with scheduling and MCP-friendly execution.",
            f"Map the agent state to the approval queue for `{flow['id']}`.",
            "",
        ]
    )


def _render_supabase_schema() -> str:
    return "\n".join(
        [
            "create table if not exists automation_runs (",
            "  id uuid primary key,",
            "  flow_id text not null,",
            "  status text not null,",
            "  created_at timestamptz default now()",
            ");",
            "",
        ]
    )


def _render_supabase_functions(flow: dict) -> str:
    return "\n".join(
        [
            "export async function handleAutomationEvent(payload: Record<string, unknown>) {",
            f"  return {{ flowId: \"{flow['id']}\", accepted: true, payload }};",
            "}",
            "",
        ]
    )


def _render_supabase_runbook(flow: dict) -> str:
    return "\n".join(
        [
            "# Supabase Runbook",
            "",
            "Use Supabase when you want auth, database, and a lightweight operator backend in one place.",
            f"Store run rows, approvals, and logs for `{flow['id']}`.",
            "",
        ]
    )


def _render_approval_policy(flow: dict) -> str:
    lines = ["# Approval Policy", ""]
    for step in flow["steps"]:
        if step["human_approval"]:
            lines.append(f"- `{step['id']}` requires human approval before execution.")
    return "\n".join(lines) + "\n"


def _render_idempotency_keys(flow: dict) -> str:
    return "\n".join(
        [
            "# Idempotency Keys",
            "",
            f"- Primary key: `{flow['id']}:source_record_id:action_type`",
            "- Use one outbound action key per draft or send candidate.",
            "- Replay only when the previous attempt is explicitly marked failed.",
            "",
        ]
    )


def _render_queue_design() -> str:
    return "\n".join(
        [
            "# Queue Design",
            "",
            "- `ingest_queue` for new records",
            "- `approval_queue` for steps that need human review",
            "- `dead_letter_queue` for repeated failures",
            "- `report_queue` for summaries and audits",
            "",
        ]
    )


def _render_runtime_rollback() -> str:
    return "\n".join(
        [
            "# Runtime Rollback",
            "",
            "1. Stop scheduler or webhook intake.",
            "2. Freeze approval processing.",
            "3. Preserve run history and queued payloads.",
            "4. Rotate any affected connector secrets.",
            "5. Re-run only from reviewed checkpoints.",
            "",
        ]
    )


def _runtime_history_schema(flow: dict) -> dict:
    return {
        "flow_id": flow["id"],
        "fields": ["run_id", "source_record_id", "step_id", "status", "attempt", "approver", "timestamp"],
    }


def _render_secret_ownership(flow: dict, secrets: list[dict]) -> str:
    lines = ["# Secret Ownership", "", f"Flow: `{flow['id']}`", ""]
    for item in secrets:
        lines.append(f"- `{item['name']}` -> connector `{item['connector']}` -> owner `{item['owner']}`")
    return "\n".join(lines) + "\n"


def _render_secret_bootstrap_runbook(provider: str) -> str:
    return "\n".join(
        [
            "# Secret Bootstrap Runbook",
            "",
            f"- Provider: `{provider}`",
            "- Keep secrets out of chat and Git.",
            "- Let a human enter values in the secret manager.",
            "- Test with a sample record before enabling production traffic.",
            "",
        ]
    )


def _render_document_start(flow: dict, mode: str) -> str:
    return "\n".join(
        [
            "# Document Intake Starter",
            "",
            f"- Flow: `{flow['id']}`",
            f"- Mode: `{mode}`",
            "- `MarkItDown` is the fast path.",
            "- `Docling` is the advanced path for PDF structure and tables.",
            "",
        ]
    )


def _markitdown_config(flow: dict) -> dict:
    return {"flow_id": flow["id"], "output_format": "markdown", "preserve_headings": True}


def _docling_config(flow: dict, mode: str) -> dict:
    return {"flow_id": flow["id"], "mode": mode, "extract_tables": True, "ocr": mode == "advanced"}


def _render_document_pipeline() -> str:
    return "\n".join(
        [
            "# Document Pipeline",
            "",
            "1. Accept the inbound file into a review folder.",
            "2. Convert with MarkItDown for quick text extraction.",
            "3. If tables or layout matter, run the Docling path.",
            "4. Save the converted markdown/json into the dry-run workspace.",
            "5. Keep approvals before any external updates.",
            "",
        ]
    )


def _render_trace_model() -> str:
    return "\n".join(
        [
            "# Trace Model",
            "",
            "- Trace each run from intake to approval to report generation.",
            "- Record prompt version, source record id, approver, and retry count.",
            "- Tag failures by connector, transformation, approval, or delivery stage.",
            "",
        ]
    )


def _render_eval_dataset(flow: dict) -> str:
    return "\n".join(
        [
            "case_id,input_summary,expected_behavior,review_owner",
            f"{flow['id']}-001,missing invoice record,draft follow-up and require approval,operator",
            f"{flow['id']}-002,already completed record,skip outbound action,operator",
            "",
        ]
    )


def _render_prompt_review_checklist() -> str:
    return "\n".join(
        [
            "# Prompt Review Checklist",
            "",
            "- Does the prompt avoid asking for secrets in chat?",
            "- Does it tell the model when to stop and ask for human approval?",
            "- Does it preserve the dry-run boundary?",
            "",
        ]
    )


def _render_state_backend_start(flow: dict, backend: str) -> str:
    return "\n".join(
        [
            "# State Backend Starter",
            "",
            f"- Flow: `{flow['id']}`",
            f"- Backend: `{backend}`",
            "- Use this when local files are no longer enough for approvals and run history.",
            "",
        ]
    )


def _render_operator_state_model() -> str:
    return "\n".join(
        [
            "# Operator State Model",
            "",
            "- `runs` keeps one row per automation execution.",
            "- `approvals` keeps pending, approved, rejected, and changed decisions.",
            "- `notes` stores operator comments and customer-specific exceptions.",
            "- `artifacts` stores generated reports, drafts, and audit evidence.",
            "",
        ]
    )


def _render_supabase_state_schema() -> str:
    return "\n".join(
        [
            "create table if not exists approvals (",
            "  id uuid primary key,",
            "  flow_id text not null,",
            "  run_id uuid not null,",
            "  step_id text not null,",
            "  status text not null,",
            "  approver text,",
            "  created_at timestamptz default now()",
            ");",
            "",
        ]
    )


def _render_cloudflare_state_agent() -> str:
    return "\n".join(
        [
            "export class ApprovalAgent {",
            "  state: Record<string, unknown> = {};",
            "  async setApproval(runId: string, status: string) {",
            "    this.state[runId] = status;",
            "    return this.state[runId];",
            "  }",
            "}",
            "",
        ]
    )
