from __future__ import annotations

import csv
import html
import json
from io import StringIO
from pathlib import Path


PUBLIC_PATTERNS: list[dict[str, str]] = [
    {
        "id": "skill-pack",
        "name": "AI Agent Skill Pack",
        "source": "Anthropic Claude Code Skills, Codex skills, Cursor rules",
        "purpose": "Turn one workflow into reusable agent instructions.",
        "command": "skill-pack",
    },
    {
        "id": "approval-gate",
        "name": "Human Approval Gate",
        "source": "OpenAI Agents SDK guardrails, handoffs, human-in-the-loop patterns",
        "purpose": "Separate AI drafts from real-world commitments.",
        "command": "approval-gate",
    },
    {
        "id": "mcp-connector-plan",
        "name": "MCP Connector Plan",
        "source": "OpenAI Apps SDK MCP, Anthropic MCP, connector marketplaces",
        "purpose": "Explain what accounts, connectors, secrets, and permissions are needed.",
        "command": "mcp-connector-plan",
    },
    {
        "id": "agent-team",
        "name": "Agent Team Roles",
        "source": "Claude Code subagents, CrewAI, multi-agent delivery teams",
        "purpose": "Split sales, intake, build, QA, and delivery roles.",
        "command": "agent-team",
    },
    {
        "id": "eval-loop",
        "name": "Evaluation And Improvement Loop",
        "source": "OpenAI eval flywheel, Anthropic eval guidance",
        "purpose": "Measure whether the automation is useful and improve it safely.",
        "command": "eval-loop",
    },
    {
        "id": "workflow-explainer",
        "name": "Workflow Explainer",
        "source": "n8n, Flowise, Windmill visual workflow patterns",
        "purpose": "Make the before/after workflow visible to non-engineers.",
        "command": "workflow-explainer",
    },
    {
        "id": "self-host-pack",
        "name": "Self-Host Deployment Pack",
        "source": "n8n self-hosted starter kits, Docker deployment runbooks",
        "purpose": "Guide local, Docker, VPS, and cloud-hosted rollout decisions.",
        "command": "self-host-pack",
    },
    {
        "id": "connector-catalog",
        "name": "Connector Piece Catalog",
        "source": "Activepieces pieces, n8n integrations, MCP connector catalogs",
        "purpose": "Map common business jobs to connector pieces.",
        "command": "connector-catalog",
    },
    {
        "id": "script-ui-pack",
        "name": "Script To Workflow UI Pack",
        "source": "Windmill script-to-webhook-to-UI patterns",
        "purpose": "Turn local scripts into operator-facing jobs, forms, and dashboards.",
        "command": "script-ui-pack",
    },
    {
        "id": "knowledge-rag-pack",
        "name": "Knowledge RAG Pack",
        "source": "Dify, Flowise, Docs RAG app patterns",
        "purpose": "Package internal FAQ and document Q&A safely.",
        "command": "knowledge-rag-pack",
    },
    {
        "id": "automation-hooks",
        "name": "Automation Hooks",
        "source": "Claude Code hooks, CI checks, preflight automation",
        "purpose": "Run checks after files are generated and before anything is shared.",
        "command": "automation-hooks",
    },
    {
        "id": "governance-pack",
        "name": "Security And Operations Governance",
        "source": "GitHub Actions, enterprise agent governance, security review patterns",
        "purpose": "Add audit, risk, review, incident, and maintenance controls.",
        "command": "governance-pack",
    },
]


def generate_command_center(output: Path, language: str = "both") -> dict:
    output.mkdir(parents=True, exist_ok=True)
    payload = {"status": "ready", "language": language, "patterns": PUBLIC_PATTERNS}
    (output / "command_center.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "START_HERE_COMMAND_CENTER.md").write_text(_render_command_center_start(), encoding="utf-8")
    (output / "COMMAND_CENTER.md").write_text(_render_command_center_en(), encoding="utf-8")
    (output / "COMMAND_CENTER.ja.md").write_text(_render_command_center_ja(), encoding="utf-8")
    (output / "next_step_decision_tree.md").write_text(_render_decision_tree(), encoding="utf-8")
    (output / "command_center.html").write_text(_render_command_center_html(), encoding="utf-8")
    return payload


def generate_skill_pack(flow_id: str, agent: str, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    agent_label = _agent_label(agent)
    _write_json(output / "skill_pack.json", {"status": "ready", "flow_id": flow_id, "agent": agent})
    (output / "SKILL.md").write_text(
        "\n".join(
            [
                f"# Skill: {flow_id} Automation Delivery",
                "",
                f"Use this skill with {agent_label}, Codex, Claude Code, Cursor, ChatGPT, or another AI agent.",
                "",
                "## Mission",
                "",
                "Help a beginner turn one business workflow into a bounded, reviewable automation pilot.",
                "",
                "## Required Behavior",
                "",
                "- Ask one question at a time.",
                "- Keep secrets, API keys, passwords, and private customer data out of chat.",
                "- Prefer local dry-run before production automation.",
                "- Keep Human approval visible before external sends, bookings, prices, refunds, cloud changes, or public claims.",
                "- Produce client-facing explanations, not only code.",
                "",
                "## First Files To Produce",
                "",
                "1. workflow summary",
                "2. missing input list",
                "3. approval gate",
                "4. dry-run plan",
                "5. client handoff note",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (output / "agent_usage.md").write_text(
        f"# Agent Usage\n\nThis pack is optimized for {agent_label}. Paste `SKILL.md` into the agent, then ask it to interview the operator one question at a time.\n",
        encoding="utf-8",
    )
    (output / "agent_team_roles.md").write_text(_render_agent_roles(flow_id), encoding="utf-8")
    (output / "skill_install_notes.md").write_text(
        "# Skill Install Notes\n\nKeep this file with the client project. Review it before asking an AI agent to change workflow behavior.\n",
        encoding="utf-8",
    )
    return {"status": "ready", "flow_id": flow_id, "agent": agent}


def generate_approval_gate(flow_id: str, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    gate = {
        "status": "ready",
        "flow_id": flow_id,
        "draft_allowed": ["classification", "summaries", "reply drafts", "status suggestions"],
        "human_approval_required": [
            "external send",
            "booking confirmation",
            "price change",
            "refund or cancellation exception",
            "cloud account change",
            "public claim",
        ],
        "stop_conditions": ["missing owner", "private data in prompt", "unknown connector", "failed dry-run"],
    }
    _write_json(output / "approval_gate.json", gate)
    (output / "approval_policy.md").write_text(
        "# Approval Policy\n\nAI may draft and organize. Human approval is required for booking confirmation, external sends, price changes, refunds, policy exceptions, public claims, and production connector changes.\n",
        encoding="utf-8",
    )
    (output / "human_review_queue.csv").write_text(
        "item_id,action,reason,approver,status\n1,external_send,customer-facing message,owner,pending\n",
        encoding="utf-8",
    )
    (output / "resume_after_approval.md").write_text(
        "# Resume After Approval\n\nAfter approval, record the approver, timestamp, action, and exact output. Then run the next dry-run before production.\n",
        encoding="utf-8",
    )
    return gate


def generate_mcp_connector_plan(flow_id: str, connectors: str, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    connector_list = _split_csv(connectors)
    _write_json(output / "mcp_connector_plan.json", {"status": "ready", "flow_id": flow_id, "connectors": connector_list})
    lines = ["# MCP Connector Plan", "", f"Flow: `{flow_id}`", "", "| Connector | Purpose | Human setup needed |", "|---|---|---|"]
    for connector in connector_list:
        lines.append(f"| {connector} | Business data or action channel | Account owner, permissions, test data, and secret storage |")
    (output / "mcp_connector_plan.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (output / "env_request_list.md").write_text(
        "# Environment Request List\n\nAsk the account owner for names of accounts, test folders, test inboxes, and allowed scopes. Do not ask for secrets in chat.\n",
        encoding="utf-8",
    )
    (output / "secrets_boundary.md").write_text(
        "# Secrets Boundary\n\nDo not paste secrets, passwords, API keys, OAuth tokens, private customer records, or payment data into chat. Use the provider dashboard or a reviewed secret manager.\n",
        encoding="utf-8",
    )
    (output / "connector_test_plan.md").write_text(
        "# Connector Test Plan\n\nUse redacted sample data first. Confirm read-only access before write access. Keep production sends disabled until approval.\n",
        encoding="utf-8",
    )
    return {"status": "ready", "flow_id": flow_id, "connectors": connector_list}


def generate_agent_team(flow_id: str, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    _write_json(output / "agent_team.json", {"status": "ready", "flow_id": flow_id})
    (output / "agent_team_roles.md").write_text(_render_agent_roles(flow_id), encoding="utf-8")
    (output / "agent_handoff_protocol.md").write_text(
        "# Agent Handoff Protocol\n\nEvery handoff must include goal, current files, known blockers, approval boundary, next command, and what must not be changed.\n",
        encoding="utf-8",
    )
    (output / "team_review_checklist.md").write_text(
        "# Team Review Checklist\n\n- Sales scout found a real pain\n- Intake mapper collected facts\n- Builder used sample data\n- QA reviewer ran checks\n- Delivery lead wrote handoff\n",
        encoding="utf-8",
    )
    return {"status": "ready", "flow_id": flow_id}


def generate_eval_loop(flow_id: str, metric: str, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    payload = {"status": "ready", "flow_id": flow_id, "metric": metric, "failure_modes": ["late reply", "wrong status", "missing approval", "connector failure"]}
    _write_json(output / "eval_loop.json", payload)
    (output / "eval_dataset.csv").write_text(
        "case_id,input,expected_output,metric,pass_fail\n1,redacted sample inquiry,draft with approval required," + metric + ",\n",
        encoding="utf-8",
    )
    (output / "failure_modes.md").write_text("# Failure Modes\n\n- late reply\n- wrong status\n- missing approval\n- connector failure\n", encoding="utf-8")
    (output / "improvement_loop.md").write_text(
        "# Improvement Loop\n\n1. Run with sample data.\n2. Compare expected vs actual.\n3. Record failure modes.\n4. Fix prompts, rules, or connectors.\n5. Re-run before client use.\n",
        encoding="utf-8",
    )
    return payload


def generate_workflow_explainer(flow_id: str, audience: str, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    _write_json(output / "workflow_explainer.json", {"status": "ready", "flow_id": flow_id, "audience": audience})
    (output / "workflow_map.mmd").write_text(
        "flowchart LR\n  A[Input] --> B[AI draft or classification]\n  B --> C[Human approval]\n  C --> D[Client-safe output]\n",
        encoding="utf-8",
    )
    (output / "before_after.md").write_text(
        "# Before / After\n\nBefore: work is scattered and checked manually.\n\nAfter: inputs are collected, AI drafts, Human approval gates decisions, and outputs are tracked.\n",
        encoding="utf-8",
    )
    (output / "client_talk_track.md").write_text(
        "# Client Talk Track\n\nThis is a small proof-of-value workflow. It makes the process visible before production automation.\n",
        encoding="utf-8",
    )
    (output / "workflow_explainer.html").write_text(_render_workflow_html(flow_id, audience), encoding="utf-8")
    return {"status": "ready", "flow_id": flow_id, "audience": audience}


def generate_self_host_pack(flow_id: str, provider: str, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    _write_json(output / "self_host_pack.json", {"status": "ready", "flow_id": flow_id, "provider": provider})
    (output / "docker_compose_plan.md").write_text(
        "# Docker Compose Plan\n\nUse Docker only after local dry-run passes. Keep secrets in env files excluded from git. Add logs, backup, and rollback before client production.\n",
        encoding="utf-8",
    )
    (output / "self_host_runbook.md").write_text(
        "# Self-Host Runbook\n\nStart with staging, verify logs, test rollback, check cost owner, and document who can stop the service.\n",
        encoding="utf-8",
    )
    (output / "deployment_decision.md").write_text(
        "# Deployment Decision\n\nChoose local, managed cloud, VPS, or Docker based on data sensitivity, uptime needs, budget, and operator skill.\n",
        encoding="utf-8",
    )
    return {"status": "ready", "flow_id": flow_id, "provider": provider}


def generate_connector_catalog(industry: str, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    connectors = [
        ("Google Sheets", "status table and lightweight database", "safe first operating table"),
        ("Gmail", "inquiry and follow-up drafts", "keep final sends approved"),
        ("Slack", "internal alerts", "avoid customer data in channels"),
        ("Notion", "knowledge and handoff docs", "control sharing"),
        ("Google Drive", "document intake", "review folder permissions"),
        ("Webhook", "form and app integration", "test with sample events"),
    ]
    _write_json(output / "connector_piece_catalog.json", {"status": "ready", "industry": industry, "connectors": connectors})
    lines = ["# Connector Piece Catalog", "", "| Connector | Use | Safety note |", "|---|---|---|"]
    for name, use, note in connectors:
        lines.append(f"| {name} | {use} | {note} |")
    (output / "connector_piece_catalog.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (output / "connector_selection_matrix.csv").write_text(_rows_to_csv(["connector", "use", "safety_note"], connectors), encoding="utf-8")
    return {"status": "ready", "industry": industry}


def generate_script_ui_pack(flow_id: str, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    _write_json(output / "script_ui_pack.json", {"status": "ready", "flow_id": flow_id})
    (output / "script_to_ui_plan.md").write_text(
        "# Script To UI Plan\n\nWrap the script with inputs, dry-run output, approval queue, logs, and a small operator page before scheduling production jobs.\n",
        encoding="utf-8",
    )
    (output / "ui_workflow_options.md").write_text(
        "# UI Workflow Options\n\nOptions: local CLI, HTML operator page, webhook endpoint, scheduled job, queue worker, or internal dashboard.\n",
        encoding="utf-8",
    )
    (output / "operator_form_schema.json").write_text(json.dumps({"flow_id": flow_id, "fields": ["input_source", "dry_run", "approver"]}, indent=2) + "\n", encoding="utf-8")
    return {"status": "ready", "flow_id": flow_id}


def generate_knowledge_rag_pack(flow_id: str, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    _write_json(output / "knowledge_rag_pack.json", {"status": "ready", "flow_id": flow_id})
    (output / "knowledge_base_pack.md").write_text(
        "# Knowledge Base Pack\n\nCollect approved documents, remove private data, define source priority, and test answers with source citations before staff use.\n",
        encoding="utf-8",
    )
    (output / "rag_answer_policy.md").write_text(
        "# RAG Answer Policy\n\nEvery answer needs a source citation, uncertainty note, escalation rule, and human review for HR, legal, medical, financial, or safety topics.\n",
        encoding="utf-8",
    )
    (output / "document_ingestion_checklist.md").write_text(
        "# Document Ingestion Checklist\n\n- approved source\n- owner\n- update cadence\n- private data removed\n- outdated versions archived\n",
        encoding="utf-8",
    )
    return {"status": "ready", "flow_id": flow_id}


def generate_automation_hooks(flow_id: str, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    _write_json(output / "automation_hooks.json", {"status": "ready", "flow_id": flow_id})
    (output / "automation_hooks.md").write_text(
        "# Automation Hooks\n\nRun checks after generation, before sharing, before deployment, and after client approval. Hooks should report results, not silently mutate production.\n",
        encoding="utf-8",
    )
    (output / "preflight_checks.md").write_text(
        "# Preflight Checks\n\n- secret scan\n- markdown link check\n- generated file existence\n- dry-run output check\n- approval gate check\n- client-share check\n",
        encoding="utf-8",
    )
    (output / "hook_config.example.json").write_text(json.dumps({"checks": ["secret_scan", "link_check", "dry_run", "approval_gate"]}, indent=2) + "\n", encoding="utf-8")
    return {"status": "ready", "flow_id": flow_id}


def generate_governance_pack(flow_id: str, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    _write_json(output / "governance_pack.json", {"status": "ready", "flow_id": flow_id})
    (output / "governance_pack.md").write_text(
        "# Governance Pack\n\nUse this for review gates, access boundaries, incident handling, monthly review, and client-facing accountability.\n",
        encoding="utf-8",
    )
    (output / "operational_governance.md").write_text(
        "# Operational Governance\n\nMaintain approval audit logs, connector owner list, incident response owner, rollback steps, and monthly value review.\n",
        encoding="utf-8",
    )
    (output / "security_review_checklist.md").write_text(
        "# Security Review Checklist\n\n- least privilege\n- no secrets in git\n- sample data only\n- prompt injection review\n- production send disabled until approval\n",
        encoding="utf-8",
    )
    return {"status": "ready", "flow_id": flow_id}


def _render_command_center_start() -> str:
    return "\n".join(
        [
            "# Start Here: Command Center",
            "",
            "Open this folder first when the project feels too large.",
            "",
            "1. Read `COMMAND_CENTER.md` or `COMMAND_CENTER.ja.md`.",
            "2. Open `command_center.html` for the visual menu.",
            "3. Use `next_step_decision_tree.md` to choose one command.",
            "4. Generate only the pack you need next.",
            "",
        ]
    )


def _render_command_center_en() -> str:
    lines = [
        "# Command Center",
        "",
        "Side-hustle entry and business automation menu. This keeps beginners from getting lost as the system grows.",
        "",
        "| Need | Start with |",
        "|---|---|",
        "| Choose a sellable offer | `side-hustle-blueprints` |",
        "| Build a homepage and inquiry workflow | `website-side-hustle` |",
        "| Turn a flow into a client demo | `complete-workspace` |",
        "| Give instructions to an AI agent | `skill-pack` |",
        "| Add human approval boundaries | `approval-gate` |",
        "| Plan connectors and MCP-style access | `mcp-connector-plan` |",
        "| Explain the workflow visually | `workflow-explainer` |",
        "| Measure results and improve | `eval-loop` |",
        "| Prepare deployment and rollback | `self-host-pack` |",
        "| Choose connector pieces | `connector-catalog` |",
        "| Turn scripts into UI workflows | `script-ui-pack` |",
        "| Build document Q&A safely | `knowledge-rag-pack` |",
        "| Add automatic preflight checks | `automation-hooks` |",
        "| Add security and operations rules | `governance-pack` |",
        "",
        "These 12 expansion packs are inspired by public patterns from OpenAI, Anthropic, n8n, Activepieces, Windmill, Dify, Flowise, CrewAI, GitHub Actions, and similar automation projects.",
    ]
    return "\n".join(lines) + "\n"


def _render_command_center_ja() -> str:
    return "\n".join(
        [
            "# コマンドセンター",
            "",
            "業務自動化の仕組み作りで迷子にならないための入口です。",
            "",
            "| やりたいこと | 最初に使うコマンド |",
            "|---|---|",
            "| 副業で売る案件を選びたい | `side-hustle-blueprints` |",
            "| ホームページと問い合わせ運用を作りたい | `website-side-hustle` |",
            "| 顧客に見せるデモ一式を作りたい | `complete-workspace` |",
            "| AIエージェントに作業を渡したい | `skill-pack` |",
            "| 人間承認の境界を作りたい | `approval-gate` |",
            "| GmailやSheetsなどの接続準備をしたい | `mcp-connector-plan` |",
            "| 業務フローを見える化したい | `workflow-explainer` |",
            "| 効果測定と改善ループを作りたい | `eval-loop` |",
            "| 導入先やrollbackを考えたい | `self-host-pack` |",
            "| 接続部品を選びたい | `connector-catalog` |",
            "| スクリプトをUIやWebhookにしたい | `script-ui-pack` |",
            "| 社内FAQや書類Q&Aを作りたい | `knowledge-rag-pack` |",
            "| 共有前の自動チェックを入れたい | `automation-hooks` |",
            "| セキュリティと運用ルールを作りたい | `governance-pack` |",
            "",
            "12個の拡充パックは、OpenAI、Anthropic、n8n、Activepieces、Windmill、Dify、Flowise、CrewAI、GitHub Actions などの公開パターンを、初心者にも使いやすい業務自動化の形に整理したものです。",
            "",
        ]
    )


def _render_decision_tree() -> str:
    return "# Next Step Decision Tree\n\n- If you do not know what to sell: `side-hustle-blueprints`\n- If you have one flow: `skill-pack` then `approval-gate`\n- If tools must connect: `mcp-connector-plan`\n- If the client is confused: `workflow-explainer`\n- If value is unclear: `eval-loop`\n- If deployment feels risky: `self-host-pack`\n- If you need app pieces: `connector-catalog`\n- If you already have a script: `script-ui-pack`\n- If answers must cite documents: `knowledge-rag-pack`\n- If mistakes must be caught early: `automation-hooks`\n- If a business will rely on it monthly: `governance-pack`\n"


def _render_command_center_html() -> str:
    cards = [
        "<section><h2>Side Hustle Blueprints</h2><p>Choose the first sellable automation offer.</p><code>side-hustle-blueprints</code></section>",
        "<section><h2>Website Side Hustle</h2><p>Create a homepage and inquiry operations pack.</p><code>website-side-hustle</code></section>",
        "<section><h2>Complete Workspace</h2><p>Create a client-ready demo and delivery workspace.</p><code>complete-workspace</code></section>",
    ]
    for item in PUBLIC_PATTERNS:
        cards.append(
            f"<section><h2>{html.escape(item['name'])}</h2><p>{html.escape(item['purpose'])}</p><code>{html.escape(item['command'])}</code></section>"
        )
    return "<!doctype html><html><head><meta charset='utf-8'><title>AI Automation Command Center</title><style>body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:0;background:#f8fafc;color:#111827}main{max-width:1120px;margin:auto;padding:24px;display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}header{max-width:1120px;margin:auto;padding:32px 24px 8px}section{background:white;border:1px solid #d8dee8;border-radius:8px;padding:16px}code{font-weight:700;color:#1d4ed8}</style></head><body><header><h1>AI Automation Command Center</h1><p>Choose the next business automation pack without getting lost.</p></header><main>" + "".join(cards) + "</main></body></html>"


def _render_agent_roles(flow_id: str) -> str:
    return "\n".join(
        [
            "# Agent Team Roles",
            "",
            f"Flow: `{flow_id}`",
            "",
            "- Sales scout: identifies pain, buyer, and first offer.",
            "- Intake mapper: asks one question at a time and collects sample data boundaries.",
            "- Automation builder: creates dry-run workflow assets.",
            "- QA reviewer: checks links, secrets, approval gates, and edge cases.",
            "- Delivery lead: prepares handoff, training, and next-step proposal.",
            "",
        ]
    )


def _render_workflow_html(flow_id: str, audience: str) -> str:
    return f"<!doctype html><html><head><meta charset='utf-8'><title>Workflow Explainer</title><style>body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:24px;color:#111827}}.step{{border:1px solid #d8dee8;border-radius:8px;padding:14px;margin:10px 0}}</style></head><body><h1>{html.escape(flow_id)} Workflow</h1><p>Audience: {html.escape(audience)}</p><div class='step'>1. Input arrives</div><div class='step'>2. AI drafts or classifies</div><div class='step'>3. Human approval</div><div class='step'>4. Client-safe output</div></body></html>"


def _agent_label(agent: str) -> str:
    labels = {"claude-code": "Claude Code", "codex": "Codex", "cursor": "Cursor"}
    return labels.get(agent, agent)


def _split_csv(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _rows_to_csv(headers: list[str], rows: list[tuple[str, ...]]) -> str:
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(headers)
    writer.writerows(rows)
    return buffer.getvalue()
