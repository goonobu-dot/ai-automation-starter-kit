from __future__ import annotations

import html
import json
import shutil
import zipfile
from pathlib import Path

from ai_automation_kit.core.beginner_sales import generate_beginner_sales_pack
from ai_automation_kit.core.client_ready import generate_client_ready_pack
from ai_automation_kit.core.execution_expansion import generate_deployment_pack
from ai_automation_kit.core.execution_expansion import generate_document_intake_pack
from ai_automation_kit.core.execution_expansion import generate_flow_export
from ai_automation_kit.core.execution_expansion import generate_observability_pack
from ai_automation_kit.core.execution_expansion import generate_runtime_safety_pack
from ai_automation_kit.core.execution_expansion import generate_secrets_bootstrap
from ai_automation_kit.core.execution_expansion import generate_state_backend_pack
from ai_automation_kit.core.flow_runtime import approve_all_pending
from ai_automation_kit.core.flow_runtime import run_flow_project
from ai_automation_kit.core.flows import get_flow
from ai_automation_kit.core.flows import install_flow
from ai_automation_kit.core.flows import list_flows


DEMO_EXTENSIONS = {".md", ".html", ".csv", ".json", ".mmd", ".yaml", ".yml", ".txt"}
SHARE_CHECK_SECRET_MARKERS = ["sk-", "ghp_", "BEGIN PRIVATE KEY", "AWS_SECRET_ACCESS_KEY=", "token=", "password="]
STARTER_FLOW_IDS = [
    "invoice-document-followup",
    "support-reply-draft",
    "weekly-kpi-report",
    "crm-lead-cleanup",
    "lead-routing-followup",
    "appointment-reminder",
    "order-shipping-status",
    "inventory-reorder-alert",
    "candidate-interview-scheduling",
    "field-service-dispatch",
]


def generate_opportunity_catalog(industry: str | None, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    flows = list_flows(industry=industry) if industry else _starter_flows()
    if not flows:
        flows = _starter_flows()
    rows = [_catalog_row(flow, index) for index, flow in enumerate(flows[:24], start=1)]
    payload = {"status": "ready", "industry": industry or "starter", "count": len(rows), "opportunities": rows}
    (output / "opportunity_catalog.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "opportunity_catalog.md").write_text(_render_opportunity_catalog_md(payload), encoding="utf-8")
    (output / "opportunity_catalog.html").write_text(_render_opportunity_catalog_html(payload), encoding="utf-8")
    return payload


def generate_recommended_flow_from_intake(
    industry: str | None,
    pain: str,
    tools: str,
    monthly_items: int,
    output: Path,
) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    candidates = list_flows(industry=industry) if industry else list_flows()
    if not candidates:
        candidates = list_flows()
    scored = sorted(
        (_intake_score(flow, pain=pain, tools=tools, monthly_items=monthly_items) for flow in candidates),
        key=lambda item: item["score"],
        reverse=True,
    )
    recommended = scored[0]
    payload = {
        "status": "ready",
        "industry": industry or "any",
        "pain": pain,
        "tools": tools,
        "monthly_items": monthly_items,
        "recommended_flow": recommended,
        "alternatives": scored[1:4],
    }
    (output / "recommended_flow.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "recommended_flow.md").write_text(_render_recommended_flow(payload), encoding="utf-8")
    (output / "recommended_poc_scope.md").write_text(_render_recommended_poc_scope(payload), encoding="utf-8")
    return payload


def generate_share_check(source: Path, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    findings = []
    for path in _collect_demo_file_paths(source):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError as exc:
            findings.append({"path": path.relative_to(source).as_posix(), "severity": "warning", "marker": "read_error", "detail": str(exc)})
            continue
        for marker in SHARE_CHECK_SECRET_MARKERS:
            if marker in text:
                findings.append({"path": path.relative_to(source).as_posix(), "severity": "blocked", "marker": marker, "detail": "Secret-like marker found."})
        if "/Users/" in text or "file:///Users/" in text:
            findings.append({"path": path.relative_to(source).as_posix(), "severity": "warning", "marker": "local_path", "detail": "Local machine path found; review before sharing."})
    status = "blocked" if any(item["severity"] == "blocked" for item in findings) else "warning" if findings else "ready"
    payload = {"status": status, "source": str(source), "findings": findings, "files_scanned": len(_collect_demo_file_paths(source))}
    (output / "share_check.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "share_check.md").write_text(_render_share_check(payload), encoding="utf-8")
    return payload


def generate_business_launch_pack(
    industry: str | None,
    client_type: str,
    niche: str,
    operator_level: str,
    output: Path,
) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    flows = list_flows(industry=industry) if industry else _starter_flows()
    if not flows:
        flows = _starter_flows()
    recommended_flow = _business_launch_flow_choice(flows, niche)
    starter_offers = [_business_launch_offer_row(flow, index) for index, flow in enumerate(flows[:10], start=1)]
    payload = {
        "status": "ready",
        "industry": industry or "starter",
        "client_type": client_type,
        "niche": niche,
        "operator_level": operator_level,
        "recommended_flow": recommended_flow,
        "starter_offers": starter_offers,
        "positioning": "企業向け自動化導入の小さなPaid PoCを安全に提案するための事業化パック",
    }
    (output / "business_launch.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "START_HERE_BUSINESS_LAUNCH.md").write_text(_render_business_launch_start(payload), encoding="utf-8")
    (output / "target_industry_playbook.md").write_text(_render_target_industry_playbook(payload), encoding="utf-8")
    (output / "first_client_offer.md").write_text(_render_first_client_offer(payload), encoding="utf-8")
    (output / "discovery_call_script.md").write_text(_render_discovery_call_script(payload), encoding="utf-8")
    (output / "proposal_builder.md").write_text(_render_proposal_builder(payload), encoding="utf-8")
    (output / "pricing_and_scope_menu.md").write_text(_render_pricing_and_scope_menu(payload), encoding="utf-8")
    (output / "risk_boundary_sheet.md").write_text(_render_risk_boundary_sheet(payload), encoding="utf-8")
    (output / "30_day_business_launch_plan.md").write_text(_render_30_day_business_launch_plan(payload), encoding="utf-8")
    (output / "client_pitch_email.md").write_text(_render_client_pitch_email(payload), encoding="utf-8")
    return payload


def generate_website_side_hustle_pack(
    industry: str | None,
    client_type: str,
    niche: str,
    operator_level: str,
    output: Path,
) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    vertical = niche.replace("-", " ")
    sources = _website_side_hustle_sources()
    payload = {
        "status": "ready",
        "industry": industry or "hospitality",
        "client_type": client_type,
        "niche": niche,
        "operator_level": operator_level,
        "positioning": "AI coding agent native starter pack for selling, designing, building, checking, and maintaining small-business websites safely.",
        "delivery_stack": [
            "Codex or another coding agent",
            "shadcn/ui or equivalent accessible primitives",
            "Astro or static HTML for marketing sites",
            "Open Props or local CSS tokens",
            "lucide icons",
            "WCAG and Google Search guidance",
        ],
        "sources": sources,
        "starter_verticals": [
            "tourism hotel",
            "clinic",
            "salon",
            "restaurant",
            "lawyer or accountant",
            "local service trades",
        ],
        "artifacts": [
            "START_HERE_WEBSITE_SIDE_HUSTLE.md",
            "commercial_use_sources.md",
            "client_brief.md",
            "client_kickoff_questions.md",
            "ai_agent_handoff.md",
            "designer_grade_agent_playbook.md",
            "public_ai_design_sources.md",
            "website_quality_gate.md",
            "homepage_review_scorecard.csv",
            "agent_design_review_prompt.md",
            "beginner_human_guide.md",
            "beginner_human_guide.ja.md",
            "reservation_inquiry_system.md",
            "inquiry_intake_schema.csv",
            "reservation_pipeline.csv",
            "response_templates.md",
            "operator_runbook.md",
            "integration_options.md",
            "privacy_and_consent.md",
            "sla_and_followup.md",
            "inquiry_dashboard.html",
            "delivery_acceptance_checklist.md",
            "client_handoff_note.md",
            "proposal_one_pager.md",
            "maintenance_plan.md",
            "sample_site/index.html",
        ],
    }
    (output / "website_side_hustle.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "START_HERE_WEBSITE_SIDE_HUSTLE.md").write_text(_render_website_side_hustle_start(payload), encoding="utf-8")
    (output / "README.md").write_text(_render_website_side_hustle_readme(payload), encoding="utf-8")
    (output / "positioning.md").write_text(_render_website_side_hustle_positioning(payload), encoding="utf-8")
    (output / "niche_offer_menu.md").write_text(_render_website_side_hustle_niche_offer_menu(payload), encoding="utf-8")
    (output / "commercial_use_sources.md").write_text(_render_website_side_hustle_sources_md(payload), encoding="utf-8")
    (output / "source_catalog.csv").write_text(_render_website_side_hustle_sources_csv(payload), encoding="utf-8")
    (output / "client_brief.md").write_text(_render_website_side_hustle_client_brief(payload), encoding="utf-8")
    (output / "client_kickoff_questions.md").write_text(_render_website_side_hustle_kickoff_questions(payload), encoding="utf-8")
    (output / "ai_agent_handoff.md").write_text(_render_website_side_hustle_agent_handoff(payload), encoding="utf-8")
    (output / "designer_grade_agent_playbook.md").write_text(_render_website_side_hustle_designer_grade_playbook(payload), encoding="utf-8")
    (output / "public_ai_design_sources.md").write_text(_render_website_side_hustle_public_ai_design_sources(payload), encoding="utf-8")
    (output / "website_quality_gate.md").write_text(_render_website_side_hustle_quality_gate(payload), encoding="utf-8")
    (output / "homepage_review_scorecard.csv").write_text(_render_website_side_hustle_scorecard_csv(payload), encoding="utf-8")
    (output / "agent_design_review_prompt.md").write_text(_render_website_side_hustle_agent_review_prompt(payload), encoding="utf-8")
    (output / "beginner_human_guide.md").write_text(_render_website_side_hustle_beginner_human_guide_en(payload), encoding="utf-8")
    (output / "beginner_human_guide.ja.md").write_text(_render_website_side_hustle_beginner_human_guide(payload), encoding="utf-8")
    (output / "design_direction_template.md").write_text(_render_website_side_hustle_design_direction(payload), encoding="utf-8")
    (output / "copy_collection_sheet.md").write_text(_render_website_side_hustle_copy_sheet(payload), encoding="utf-8")
    (output / "codex_workflow.md").write_text(_render_website_side_hustle_codex_workflow(payload), encoding="utf-8")
    (output / "implementation_stack.md").write_text(_render_website_side_hustle_stack(payload), encoding="utf-8")
    (output / "homepage_structure_guide.md").write_text(_render_website_side_hustle_structure(payload), encoding="utf-8")
    (output / "reservation_inquiry_system.md").write_text(_render_website_side_hustle_reservation_system(payload), encoding="utf-8")
    (output / "inquiry_intake_schema.csv").write_text(_render_website_side_hustle_inquiry_schema_csv(payload), encoding="utf-8")
    (output / "reservation_pipeline.csv").write_text(_render_website_side_hustle_reservation_pipeline_csv(payload), encoding="utf-8")
    (output / "response_templates.md").write_text(_render_website_side_hustle_response_templates(payload), encoding="utf-8")
    (output / "operator_runbook.md").write_text(_render_website_side_hustle_operator_runbook(payload), encoding="utf-8")
    (output / "integration_options.md").write_text(_render_website_side_hustle_integration_options(payload), encoding="utf-8")
    (output / "privacy_and_consent.md").write_text(_render_website_side_hustle_privacy_consent(payload), encoding="utf-8")
    (output / "sla_and_followup.md").write_text(_render_website_side_hustle_sla_followup(payload), encoding="utf-8")
    (output / "inquiry_dashboard.html").write_text(_render_website_side_hustle_inquiry_dashboard(payload), encoding="utf-8")
    (output / "originality_and_license_rules.md").write_text(_render_website_side_hustle_rules(payload), encoding="utf-8")
    (output / "delivery_checklist.md").write_text(_render_website_side_hustle_delivery_checklist(payload), encoding="utf-8")
    (output / "delivery_acceptance_checklist.md").write_text(_render_website_side_hustle_acceptance_checklist(payload), encoding="utf-8")
    (output / "client_handoff_note.md").write_text(_render_website_side_hustle_client_handoff(payload), encoding="utf-8")
    (output / "accessibility_and_seo_checklist.md").write_text(_render_website_side_hustle_accessibility_seo(payload), encoding="utf-8")
    (output / "proposal_one_pager.md").write_text(_render_website_side_hustle_proposal(payload), encoding="utf-8")
    (output / "pricing_menu.md").write_text(_render_website_side_hustle_pricing(payload), encoding="utf-8")
    (output / "maintenance_plan.md").write_text(_render_website_side_hustle_maintenance(payload), encoding="utf-8")
    (output / "outreach_messages.md").write_text(_render_website_side_hustle_outreach(payload), encoding="utf-8")
    (output / "launch_checklist.md").write_text(_render_website_side_hustle_launch(payload), encoding="utf-8")
    sample_dir = output / "sample_site"
    sample_dir.mkdir(parents=True, exist_ok=True)
    (sample_dir / "index.html").write_text(_render_website_side_hustle_sample_site(payload), encoding="utf-8")
    return payload


def generate_guided_setup(
    flow_id: str,
    mode: str,
    deployment: str,
    connectors: str,
    output: Path,
) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    flow = get_flow(flow_id)
    connector_list = _parse_connector_list(connectors)
    questions = _guided_setup_questions(flow, deployment, connector_list)
    answers = _guided_setup_answer_template(flow, mode, deployment, connector_list, questions)
    missing_inputs = [question["id"] for question in questions if question["required"]]
    payload = {
        "status": "needs_input",
        "flow_id": flow["id"],
        "flow_name": flow["name"],
        "mode": mode,
        "deployment": deployment,
        "connectors": connector_list,
        "required_question_count": len(missing_inputs),
        "missing_required_inputs": missing_inputs,
        "next_action": "Use guided_setup_questions.md with an AI agent and answer one question at a time.",
    }
    (output / "guided_setup.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "START_HERE_GUIDED_SETUP.md").write_text(_render_guided_setup_start(flow, payload), encoding="utf-8")
    (output / "guided_setup_questions.md").write_text(_render_guided_setup_questions(flow, questions, mode), encoding="utf-8")
    (output / "guided_setup_answers.example.json").write_text(json.dumps(answers, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "missing_inputs.md").write_text(_render_missing_inputs(flow, questions), encoding="utf-8")
    (output / "local_setup_plan.md").write_text(_render_local_setup_plan(flow, connector_list), encoding="utf-8")
    (output / "cloud_setup_plan.md").write_text(_render_cloud_setup_plan(flow, deployment, connector_list), encoding="utf-8")
    (output / "env_values_needed.md").write_text(_render_env_values_needed(connector_list, deployment), encoding="utf-8")
    (output / "client_request_list.md").write_text(_render_client_request_list(flow, connector_list), encoding="utf-8")
    (output / "ai_agent_instruction.md").write_text(_render_ai_agent_instruction(flow, mode), encoding="utf-8")
    (output / "readiness_score.json").write_text(json.dumps(_guided_readiness_score(payload), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "next_action.md").write_text(_render_guided_next_action(flow, mode, deployment), encoding="utf-8")
    return payload


def generate_guided_review(answers: Path, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    answer_payload = json.loads(answers.read_text(encoding="utf-8"))
    flow = get_flow(answer_payload["flow_id"])
    mode = answer_payload.get("mode", "beginner")
    deployment = answer_payload.get("deployment", "undecided")
    connectors = answer_payload.get("connectors", ["local-folder"])
    answer_values = answer_payload.get("answers", {})
    required_ids = [
        "business_goal",
        "reception_source",
        "knowledge_source",
        "output_destination",
        "human_approval_rules",
        "deployment_target",
        "client_data_boundary",
        "success_metric",
    ]
    if any(connector in {"line", "gmail", "google-sheets", "slack"} for connector in connectors):
        required_ids.append("connector_owner")
    if deployment in {"cloud", "render", "railway", "cloud-run", "vps", "undecided"}:
        required_ids.append("cloud_operator")

    missing_inputs = [field for field in required_ids if not str(answer_values.get(field, "")).strip()]
    local_required = [field for field in required_ids if field != "cloud_operator"]
    local_ready = all(str(answer_values.get(field, "")).strip() for field in local_required)
    status = "needs_client_input" if missing_inputs else "ready_for_dry_run"
    if not missing_inputs and deployment not in {"local", "undecided"}:
        status = "ready_for_cloud_planning"

    payload = {
        "status": status,
        "flow_id": flow["id"],
        "flow_name": flow["name"],
        "mode": mode,
        "deployment": deployment,
        "connectors": connectors,
        "missing_inputs": missing_inputs,
        "local_dry_run_ready": local_ready,
        "recommended_next_step": _guided_review_next_step(status, local_ready, deployment),
    }
    (output / "guided_review.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "START_HERE_GUIDED_REVIEW.md").write_text(_render_guided_review_start(flow, payload), encoding="utf-8")
    (output / "setup_readiness_report.md").write_text(_render_setup_readiness_report(flow, payload, answer_values), encoding="utf-8")
    (output / "automation_build_plan.md").write_text(_render_automation_build_plan(flow, payload), encoding="utf-8")
    (output / "client_missing_items_email.md").write_text(_render_client_missing_items_email(flow, payload), encoding="utf-8")
    (output / "cloud_provider_decision.md").write_text(_render_cloud_provider_decision(payload), encoding="utf-8")
    (output / "local_vs_cloud_decision.md").write_text(_render_local_vs_cloud_decision(payload), encoding="utf-8")
    (output / "ai_agent_handoff_prompt.md").write_text(_render_ai_agent_handoff_prompt(flow, payload), encoding="utf-8")
    (output / "next_commands.md").write_text(_render_guided_review_next_commands(flow, payload), encoding="utf-8")
    return payload


def generate_cloud_plan(flow_id: str, provider: str, output: Path, workload: str = "webhook-api", connectors: str = "local-folder") -> dict:
    output.mkdir(parents=True, exist_ok=True)
    flow = get_flow(flow_id)
    profile = _cloud_provider_profile(provider)
    workload_profile = _cloud_workload_profile(provider, workload)
    connector_list = _parse_connector_list(connectors)
    env_values = _cloud_required_env_values(flow, connector_list, workload)
    payload = {
        "status": "plan_ready",
        "flow_id": flow["id"],
        "flow_name": flow["name"],
        "provider": provider,
        "provider_name": profile["name"],
        "workload": workload,
        "workload_name": workload_profile["name"],
        "connectors": connector_list,
        "architecture": workload_profile["architecture"],
        "runtime": workload_profile["runtime"],
        "network": workload_profile["network"],
        "best_for": profile["best_for"],
        "beginner_fit": profile["beginner_fit"],
        "provider_services": profile["services"],
        "human_steps_required": _cloud_human_steps(profile, workload_profile, connector_list),
        "env_values": env_values,
        "does_not_auto_create_accounts": True,
    }
    (output / "cloud_plan.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "START_HERE_CLOUD_PLAN.md").write_text(_render_cloud_plan_start(flow, payload), encoding="utf-8")
    (output / "cloud_provider_matrix.md").write_text(_render_cloud_provider_matrix(payload), encoding="utf-8")
    (output / "workload_architecture.md").write_text(_render_cloud_architecture(flow, payload), encoding="utf-8")
    (output / "runtime_choice.md").write_text(_render_cloud_runtime_choice(payload), encoding="utf-8")
    (output / "secrets_and_env.md").write_text(_render_cloud_secret_setup(payload), encoding="utf-8")
    (output / "network_and_domain.md").write_text(_render_cloud_network_and_domain(payload), encoding="utf-8")
    (output / "deploy_runbook.md").write_text(_render_cloud_deploy_commands(flow, payload), encoding="utf-8")
    (output / "operations_runbook.md").write_text(_render_cloud_post_deploy_test(payload), encoding="utf-8")
    (output / "cost_guardrails.md").write_text(_render_cloud_cost_note(payload), encoding="utf-8")
    (output / "compliance_data_boundary.md").write_text(_render_cloud_compliance_data_boundary(flow, payload), encoding="utf-8")
    (output / "incident_rollback.md").write_text(_render_cloud_rollback_plan(payload), encoding="utf-8")
    (output / "human_approval_required.md").write_text(_render_cloud_human_approval(payload), encoding="utf-8")
    (output / "cloud_architecture.md").write_text(_render_cloud_architecture(flow, payload), encoding="utf-8")
    (output / "cloud_cost_note.md").write_text(_render_cloud_cost_note(payload), encoding="utf-8")
    (output / "secret_setup.md").write_text(_render_cloud_secret_setup(payload), encoding="utf-8")
    (output / "iam_setup.md").write_text(_render_cloud_iam_setup(payload), encoding="utf-8")
    (output / "deploy_commands.md").write_text(_render_cloud_deploy_commands(flow, payload), encoding="utf-8")
    (output / "webhook_setup.md").write_text(_render_cloud_webhook_setup(flow, payload), encoding="utf-8")
    (output / "post_deploy_test.md").write_text(_render_cloud_post_deploy_test(payload), encoding="utf-8")
    (output / "rollback_plan.md").write_text(_render_cloud_rollback_plan(payload), encoding="utf-8")
    return payload


def generate_grill_me_pack(
    flow_id: str,
    mode: str,
    client_type: str,
    deployment: str,
    connectors: str,
    output: Path,
) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    flow = get_flow(flow_id)
    connector_list = _parse_connector_list(connectors)
    payload = {
        "status": "ready",
        "flow_id": flow["id"],
        "flow_name": flow["name"],
        "mode": mode,
        "client_type": client_type,
        "deployment": deployment,
        "connectors": connector_list,
        "principle": "Ask one question at a time, block unsafe shortcuts, and keep real secrets out of chat.",
        "question_count": len(_grill_me_questions(flow, deployment, connector_list)),
    }
    (output / "grill_me.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "START_HERE_GRILL_ME.md").write_text(_render_grill_me_start(flow, payload), encoding="utf-8")
    (output / "questions_to_answer.md").write_text(_render_grill_me_questions(flow, payload), encoding="utf-8")
    (output / "client_interview_grill.md").write_text(_render_client_interview_grill(flow, payload), encoding="utf-8")
    (output / "cloud_readiness_grill.md").write_text(_render_cloud_readiness_grill(flow, payload), encoding="utf-8")
    (output / "risk_grill.md").write_text(_render_risk_grill(flow, payload), encoding="utf-8")
    (output / "proposal_grill.md").write_text(_render_proposal_grill(flow, payload), encoding="utf-8")
    (output / "ai_agent_prompt.md").write_text(_render_grill_me_ai_agent_prompt(flow, payload), encoding="utf-8")
    return payload


def generate_flow_guide(industry: str | None, genre: str | None, niche: str, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    candidates = list_flows(industry=industry, genre=genre)
    if not candidates:
        candidates = list_flows()
    ranked = [_ranked_flow(flow, niche, index) for index, flow in enumerate(candidates[:20], start=1)]
    payload = {
        "industry": industry or "any",
        "genre": genre or "any",
        "niche": niche,
        "count": len(ranked),
        "recommended_flows": ranked,
    }
    (output / "recommended_flows.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "recommended_flows.md").write_text(_render_flow_guide(payload), encoding="utf-8")
    return payload


def generate_quickstart_workspace(
    flow_id: str | None,
    industry: str,
    client_type: str,
    niche: str,
    output: Path,
) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    selected_flow = get_flow(flow_id) if flow_id else get_flow(list_flows(industry=industry)[0]["id"])
    flow_dir = output / "flow_project"
    beginner_dir = output / "beginner_sales"
    install_flow(selected_flow["id"], flow_dir)
    generate_beginner_sales_pack(
        flow_id=selected_flow["id"],
        output=beginner_dir,
        client_type=client_type,
        niche=niche,
        industry=selected_flow["industry"],
    )
    generate_demo_site(source=output, output=output / "demo_site", title=f"{selected_flow['name']} Quickstart")
    payload = {
        "status": "ready",
        "flow_id": selected_flow["id"],
        "flow_project": str(flow_dir),
        "beginner_sales": str(beginner_dir),
        "demo_site": str(output / "demo_site" / "index.html"),
    }
    (output / "quickstart.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "START_HERE.md").write_text(_render_quickstart_start(selected_flow, payload), encoding="utf-8")
    return payload


def generate_demo_site(source: Path, output: Path, title: str = "Client Automation Demo") -> dict:
    output.mkdir(parents=True, exist_ok=True)
    assets = _collect_demo_assets(source)
    payload = {"status": "ready", "source": str(source), "output": str(output), "title": title, "asset_count": len(assets)}
    (output / "demo_site.json").write_text(json.dumps({**payload, "assets": assets}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "index.html").write_text(_render_demo_site(title, assets), encoding="utf-8")
    return payload


def generate_install_bundle(flow_id: str, client_type: str, niche: str, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    flow = get_flow(flow_id)
    flow_dir = output / "flow_project"
    beginner_dir = output / "beginner_sales"
    client_ready_dir = output / "client_ready"
    install_flow(flow_id, flow_dir)
    generate_beginner_sales_pack(flow_id=flow_id, output=beginner_dir, client_type=client_type, niche=niche, industry=flow["industry"])
    generate_client_ready_pack(
        source_output=beginner_dir,
        output=client_ready_dir,
        business_area=flow["industry"],
        client_type=client_type,
        niche=niche,
    )
    generate_demo_site(source=output, output=output / "demo_site", title=f"{flow['name']} Client Bundle")
    payload = {
        "status": "ready",
        "flow_id": flow_id,
        "flow_project": str(flow_dir),
        "beginner_sales": str(beginner_dir),
        "client_ready": str(client_ready_dir),
        "demo_site": str(output / "demo_site" / "index.html"),
    }
    (output / "install_bundle.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "bundle_index.md").write_text(_render_bundle_index(flow, payload), encoding="utf-8")
    return payload


def generate_connector_doctor(project: Path, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    config_path = project / "config" / "connectors.json"
    env_path = project / ".env"
    env_example_path = project / ".env.example"
    checks = []
    if config_path.exists():
        config = json.loads(config_path.read_text(encoding="utf-8"))
        for connector in config.get("connectors", []):
            checks.append(
                {
                    "id": connector.get("id"),
                    "type": connector.get("type"),
                    "status": "ready" if connector.get("enabled") and connector.get("production_safe") else "review",
                    "detail": "local dry-run connector",
                }
            )
        for connector in config.get("disabled_external_connectors", []):
            checks.append(
                {
                    "id": connector.get("id"),
                    "type": "external",
                    "status": "needs_setup",
                    "detail": connector.get("reason", "requires setup"),
                }
            )
    else:
        checks.append({"id": "connectors.json", "type": "config", "status": "missing", "detail": str(config_path)})
    checks.append(
        {
            "id": ".env",
            "type": "secrets",
            "status": "ready" if env_path.exists() else "needs_setup",
            "detail": ".env present" if env_path.exists() else f"Create from {env_example_path}",
        }
    )
    status = "ready" if all(check["status"] == "ready" for check in checks) else "needs_setup"
    payload = {"status": status, "project": str(project), "checks": checks}
    (output / "connector_doctor.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "connector_doctor.md").write_text(_render_connector_doctor(payload), encoding="utf-8")
    return payload


def generate_client_report(flow_project: Path, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    automation_dir = flow_project / "automation_output"
    run_log_path = automation_dir / "run_log.json"
    run_log = json.loads(run_log_path.read_text(encoding="utf-8")) if run_log_path.exists() else {}
    files = {
        "work_queue": automation_dir / "work_queue.csv",
        "draft_outputs": automation_dir / "draft_outputs.md",
        "approval_queue": automation_dir / "approval_queue.csv",
        "approved_actions": automation_dir / "approved_actions.csv",
        "status_report": automation_dir / "status_report.md",
    }
    payload = {
        "status": "ready" if run_log_path.exists() else "missing_run",
        "flow_project": str(flow_project),
        "rows_processed": run_log.get("rows_processed", 0),
        "automation_status": run_log.get("status", "unknown"),
        "available_files": {name: str(path) for name, path in files.items() if path.exists()},
    }
    (output / "client_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = _render_client_report(payload)
    (output / "client_report.md").write_text(report, encoding="utf-8")
    (output / "client_report.html").write_text(_markdown_shell_html("Client Automation Report", report), encoding="utf-8")
    return payload


def package_client_demo(source: Path, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    files = _collect_demo_file_paths(source)
    package_path = output / "client_demo_package.zip"
    with zipfile.ZipFile(package_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(source).as_posix())
    payload = {
        "status": "packaged",
        "source": str(source),
        "package": str(package_path),
        "file_count": len(files),
        "files": [path.relative_to(source).as_posix() for path in files],
    }
    (output / "client_demo_manifest.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "README.md").write_text(_render_package_readme(payload), encoding="utf-8")
    return payload


def generate_complete_workspace(
    flow_id: str | None,
    industry: str,
    client_type: str,
    niche: str,
    approver: str,
    output: Path,
) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    quickstart_dir = output / "quickstart"
    quickstart = generate_quickstart_workspace(
        flow_id=flow_id,
        industry=industry,
        client_type=client_type,
        niche=niche,
        output=quickstart_dir,
    )
    flow_project = quickstart_dir / "flow_project"
    run_payload = run_flow_project(flow_project)
    approval_payload = approve_all_pending(flow_project, approver=approver)
    connector = generate_connector_doctor(project=flow_project, output=output / "connector_doctor")
    report = generate_client_report(flow_project=flow_project, output=output / "client_report")
    demo = generate_demo_site(source=quickstart_dir, output=output / "demo_site", title="Ready-To-Share Automation Demo")
    package = package_client_demo(source=quickstart_dir, output=output / "client_demo_package")
    flow = get_flow(quickstart["flow_id"])
    generate_flow_export(flow["id"], "n8n", output / "flow_exports" / "n8n")
    generate_flow_export(flow["id"], "activepieces", output / "flow_exports" / "activepieces")
    generate_flow_export(flow["id"], "windmill", output / "flow_exports" / "windmill")
    generate_deployment_pack(flow["id"], "coolify", "gmail,google-sheets", output / "deployment_packs" / "coolify")
    generate_deployment_pack(
        flow["id"], "cloudflare-agents", "gmail,google-sheets", output / "deployment_packs" / "cloudflare-agents"
    )
    generate_deployment_pack(flow["id"], "supabase", "gmail,google-sheets", output / "deployment_packs" / "supabase")
    runtime_safety = generate_runtime_safety_pack(flow["id"], output / "runtime_safety")
    secrets_bootstrap = generate_secrets_bootstrap(
        flow["id"], "infisical", "gmail,google-sheets", output / "secrets_bootstrap"
    )
    document_intake = generate_document_intake_pack(flow["id"], "advanced", output / "document_intake")
    observability_pack = generate_observability_pack(flow["id"], output / "observability_pack")
    state_backend = generate_state_backend_pack(flow["id"], "supabase", output / "state_backend")
    business_launch = generate_business_launch_pack(
        industry=flow["industry"],
        client_type=client_type,
        niche=niche,
        operator_level="beginner",
        output=output / "business_launch",
    )
    payload = {
        "status": "ready_to_share" if run_payload["status"] == "succeeded" and approval_payload["status"] == "approved" else "needs_attention",
        "flow_id": quickstart["flow_id"],
        "flow_name": flow["name"],
        "industry": flow["industry"],
        "genre": flow["genre"],
        "client_type": client_type,
        "niche": niche,
        "quickstart": str(quickstart_dir),
        "flow_project": str(flow_project),
        "connector_doctor": str(output / "connector_doctor" / "connector_doctor.md"),
        "client_report": str(output / "client_report" / "client_report.md"),
        "demo_site": str(output / "demo_site" / "index.html"),
        "client_demo_package": str(output / "client_demo_package" / "client_demo_package.zip"),
        "business_launch": str(output / "business_launch" / "START_HERE_BUSINESS_LAUNCH.md"),
        "rows_processed": run_payload["rows_processed"],
        "approved_items": approval_payload["approved_items"],
        "connector_status": connector["status"],
        "report_status": report["status"],
        "demo_asset_count": demo["asset_count"],
        "package_file_count": package["file_count"],
        "business_launch_status": business_launch["status"],
        "runtime_safety_status": runtime_safety["status"],
        "secrets_bootstrap_status": secrets_bootstrap["status"],
        "document_intake_status": document_intake["status"],
        "observability_status": observability_pack["status"],
        "state_backend_status": state_backend["status"],
    }
    payload["revenue_score"] = _revenue_readiness_score(payload)
    (output / "delivery_manifest.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "FINAL_DELIVERY_GUIDE.md").write_text(_render_complete_delivery_guide(payload), encoding="utf-8")
    (output / "completion_checklist.md").write_text(_render_completion_checklist(payload), encoding="utf-8")
    (output / "revenue_readiness_scorecard.md").write_text(_render_revenue_scorecard(payload), encoding="utf-8")
    (output / "sales_closing_script.md").write_text(_render_sales_closing_script(payload), encoding="utf-8")
    (output / "paid_poc_scope.md").write_text(_render_paid_poc_scope(payload), encoding="utf-8")
    (output / "value_measurement_sheet.csv").write_text(_render_value_measurement_csv(payload), encoding="utf-8")
    (output / "pre_contract_checklist.md").write_text(_render_pre_contract_checklist(payload), encoding="utf-8")
    (output / "client_proposal_email.md").write_text(_render_client_proposal_email(payload), encoding="utf-8")
    (output / "first_30_days_plan.md").write_text(_render_first_30_days_plan(payload), encoding="utf-8")
    (output / "proof_of_value_template.md").write_text(_render_proof_of_value_template(payload), encoding="utf-8")
    (output / "oss_pattern_benchmark.md").write_text(_render_oss_pattern_benchmark(payload), encoding="utf-8")
    (output / "integration_backlog.md").write_text(_render_integration_backlog(payload), encoding="utf-8")
    (output / "deployment_options.md").write_text(_render_deployment_options(payload), encoding="utf-8")
    (output / "production_observability_plan.md").write_text(_render_production_observability_plan(payload), encoding="utf-8")
    (output / "automation_opportunity_scorecard.csv").write_text(_render_automation_opportunity_scorecard(payload), encoding="utf-8")
    (output / "client_onboarding_form.md").write_text(_render_client_onboarding_form(payload), encoding="utf-8")
    (output / "go_live_decision.md").write_text(_render_go_live_decision(payload), encoding="utf-8")
    (output / "client_command_center.html").write_text(_render_client_command_center(payload), encoding="utf-8")
    (output / "side_business_starter_10.md").write_text(_render_side_business_starter_10(payload), encoding="utf-8")
    (output / "before_after_demo.html").write_text(_render_before_after_demo(payload), encoding="utf-8")
    return payload


def _ranked_flow(flow: dict, niche: str, index: int) -> dict:
    score = max(60, 101 - index * 3)
    if niche.lower() in {flow["industry"].lower(), flow["genre"].lower()}:
        score += 5
    return {**flow, "rank": index, "score": min(100, score)}


def _render_flow_guide(payload: dict) -> str:
    lines = [
        "# Flow Selection Guide",
        "",
        f"- Industry: `{payload['industry']}`",
        f"- Genre: `{payload['genre']}`",
        f"- Niche: `{payload['niche']}`",
        "",
        "| Rank | Score | Flow ID | Industry | Genre | Name |",
        "|---:|---:|---|---|---|---|",
    ]
    for flow in payload["recommended_flows"]:
        lines.append(
            f"| {flow['rank']} | {flow['score']} | `{flow['id']}` | {flow['industry']} | {flow['genre']} | {flow['name']} |"
        )
    lines.extend(
        [
            "",
            "## How To Choose",
            "",
            "- Start with a flow the client already understands.",
            "- Prefer workflows with clear input, approval owner, and measurable output.",
            "- Avoid production connectors until a dry-run proves value.",
            "",
        ]
    )
    return "\n".join(lines)


def _starter_flows() -> list[dict]:
    return [get_flow(flow_id) for flow_id in STARTER_FLOW_IDS]


def _catalog_row(flow: dict, index: int) -> dict:
    base_price = 500 + index * 150
    return {
        "rank": index,
        "flow_id": flow["id"],
        "name": flow["name"],
        "industry": flow["industry"],
        "genre": flow["genre"],
        "summary": flow["summary"],
        "price_range": f"${base_price}-${base_price + 1200}",
        "delivery_days": "3-10 days",
        "proof_metric": flow["success_metrics"][0] if flow.get("success_metrics") else "hours_saved",
        "safe_first_step": "Local dry-run with human approval before external actions.",
    }


def _render_opportunity_catalog_md(payload: dict) -> str:
    lines = [
        "# Automation Opportunity Catalog",
        "",
        f"- Industry: `{payload['industry']}`",
        f"- Opportunities: `{payload['count']}`",
        "",
        "| Rank | Flow | Industry | Price Range | Delivery | Proof Metric |",
        "|---:|---|---|---|---|---|",
    ]
    for item in payload["opportunities"]:
        lines.append(
            f"| {item['rank']} | `{item['flow_id']}` {item['name']} | {item['industry']} | {item['price_range']} | {item['delivery_days']} | {item['proof_metric']} |"
        )
    lines.extend(
        [
            "",
            "## How To Sell",
            "",
            "- Pick one workflow the client already understands.",
            "- Show the before/after demo before discussing tools.",
            "- Sell a bounded dry-run PoC first, not a production automation promise.",
            "",
        ]
    )
    return "\n".join(lines)


def _render_opportunity_catalog_html(payload: dict) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td>{item['rank']}</td>"
        f"<td><strong>{html.escape(item['name'])}</strong><br><code>{html.escape(item['flow_id'])}</code></td>"
        f"<td>{html.escape(item['summary'])}</td>"
        f"<td>{html.escape(item['price_range'])}</td>"
        f"<td>{html.escape(item['delivery_days'])}</td>"
        f"<td>{html.escape(item['proof_metric'])}</td>"
        "</tr>"
        for item in payload["opportunities"]
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Automation Opportunity Catalog</title>
  <style>
    body {{ margin: 0; font-family: Arial, sans-serif; color: #172033; background: #f7f8fa; }}
    header {{ background: #ffffff; border-bottom: 1px solid #d9dee7; padding: 28px; }}
    main {{ max-width: 1180px; margin: 0 auto; padding: 24px; }}
    table {{ width: 100%; border-collapse: collapse; background: #ffffff; border: 1px solid #d9dee7; }}
    th, td {{ padding: 12px; border-bottom: 1px solid #e6e9ef; text-align: left; vertical-align: top; }}
    th {{ background: #eef2f7; }}
    code {{ background: #eef2f7; padding: 2px 5px; border-radius: 4px; }}
  </style>
</head>
<body>
  <header>
    <h1>Automation Opportunity Catalog</h1>
    <p>Use this catalog to pick one sellable dry-run PoC before proposing production automation.</p>
  </header>
  <main>
    <table>
      <thead><tr><th>Rank</th><th>Flow</th><th>Client Problem</th><th>Price Range</th><th>Delivery</th><th>Proof Metric</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </main>
</body>
</html>
"""


def _intake_score(flow: dict, pain: str, tools: str, monthly_items: int) -> dict:
    text = " ".join([flow["id"], flow["name"], flow["summary"], flow["industry"], flow["genre"], " ".join(flow.get("tools", []))]).lower()
    pain_terms = [term for term in pain.lower().replace("-", " ").split() if len(term) >= 4]
    tool_terms = [term for term in tools.lower().replace("/", " ").split() if len(term) >= 3]
    score = 50
    score += sum(8 for term in pain_terms if term in text)
    score += sum(5 for term in tool_terms if term in text)
    score += min(20, max(0, monthly_items // 10))
    if "approval" in text or "draft" in text:
        score += 8
    return {**flow, "score": min(100, score), "why": _intake_reason(flow, pain_terms, tool_terms)}


def _intake_reason(flow: dict, pain_terms: list[str], tool_terms: list[str]) -> str:
    matched = [term for term in pain_terms + tool_terms if term in " ".join([flow["id"], flow["name"], flow["summary"], " ".join(flow.get("tools", []))]).lower()]
    if matched:
        return "Matched intake terms: " + ", ".join(sorted(set(matched))[:8])
    return "Best available workflow by industry and safe dry-run fit."


def _render_recommended_flow(payload: dict) -> str:
    flow = payload["recommended_flow"]
    lines = [
        "# Recommended Flow From Client Intake",
        "",
        f"- Recommended flow: `{flow['id']}`",
        f"- Name: {flow['name']}",
        f"- Score: `{flow['score']}/100`",
        f"- Why: {flow['why']}",
        f"- Client pain: {payload['pain']}",
        f"- Tools mentioned: {payload['tools']}",
        f"- Monthly items: `{payload['monthly_items']}`",
        "",
        "## First Action",
        "",
        f"Run `ai-automation-kit complete-workspace --flow-id {flow['id']} --output .tmp/{flow['id']}-workspace` and open `client_command_center.html`.",
        "",
        "## Alternatives",
        "",
    ]
    lines.extend(f"- `{item['id']}` {item['name']} - score `{item['score']}/100`" for item in payload["alternatives"])
    lines.append("")
    return "\n".join(lines)


def _render_recommended_poc_scope(payload: dict) -> str:
    flow = payload["recommended_flow"]
    return "\n".join(
        [
            f"# Paid PoC Recommendation: {flow['name']}",
            "",
            "## Offer",
            "",
            f"Create a safe dry-run for `{flow['id']}` using one approved sample data source, human approval, and a before/after report.",
            "",
            "## Scope",
            "",
            "- Confirm workflow owner and approval owner.",
            "- Import or paste one sample data export.",
            "- Generate queue, draft output, approval list, report, and demo.",
            "- Measure baseline minutes per item against dry-run minutes per item.",
            "- Decide continue, revise, or stop.",
            "",
            "## Do Not Include Yet",
            "",
            "- Production sends or writes.",
            "- Payment, access, legal, hiring, or regulated decisions.",
            "- Unreviewed client secrets or sensitive data.",
            "",
        ]
    )


def _render_share_check(payload: dict) -> str:
    lines = [
        "# Share Check",
        "",
        f"- Status: `{payload['status']}`",
        f"- Source: `{payload['source']}`",
        f"- Files scanned: `{payload['files_scanned']}`",
        "",
    ]
    if payload["findings"]:
        lines.extend(["## Findings", "", "| Severity | File | Marker | Detail |", "|---|---|---|---|"])
        for item in payload["findings"]:
            lines.append(f"| `{item['severity']}` | `{item['path']}` | `{item['marker']}` | {item['detail']} |")
    else:
        lines.extend(["## Findings", "", "No secret-like markers or local machine paths were found in shareable text assets."])
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `ready`: share after normal client review.",
            "- `warning`: review findings, remove local paths if needed, then share.",
            "- `blocked`: do not share until secret-like markers are removed.",
            "",
        ]
    )
    return "\n".join(lines)


def _business_launch_flow_choice(flows: list[dict], niche: str) -> dict:
    niche_terms = {term for term in niche.lower().replace("-", " ").split() if len(term) >= 4}
    best = None
    best_score = -1
    for index, flow in enumerate(flows):
        text = " ".join([flow["id"], flow["name"], flow["summary"], flow["industry"], flow["genre"]]).lower()
        score = 100 - index * 2
        score += sum(6 for term in niche_terms if term in text)
        if flow["id"] in STARTER_FLOW_IDS:
            score += 8
        if flow["genre"] in {"document", "communication", "reporting", "approval"}:
            score += 5
        if score > best_score:
            best = flow
            best_score = score
    selected = dict(best or flows[0])
    selected["business_launch_score"] = max(0, min(100, best_score))
    selected["why_beginner_friendly"] = "入力、承認者、成果物、測定指標を説明しやすく、最初は本番送信なしのdry-runで提案できます。"
    return selected


def _business_launch_offer_row(flow: dict, index: int) -> dict:
    entry_price = 30000 + index * 5000
    return {
        "rank": index,
        "flow_id": flow["id"],
        "name": flow["name"],
        "industry": flow["industry"],
        "client_pain": flow["summary"],
        "first_offer": "3日間の業務自動化dry-run診断",
        "price_jpy": f"{entry_price:,}円-{entry_price + 70000:,}円",
        "proof": flow.get("success_metrics", ["hours_saved"])[0],
    }


def _render_business_launch_start(payload: dict) -> str:
    flow = payload["recommended_flow"]
    return "\n".join(
        [
            "# Business Launch Start Guide",
            "",
            "このフォルダは、AIに慣れていない人が企業向け自動化導入を小さく事業化提案するための実行パックです。",
            "",
            "## 最初に読む順番",
            "",
            "1. `target_industry_playbook.md` で狙う企業と困りごとを決める。",
            "2. `first_client_offer.md` で最初の商品を確認する。",
            "3. `discovery_call_script.md` を見ながらヒアリングする。",
            "4. `proposal_builder.md` で提案書を作る。",
            "5. `pricing_and_scope_menu.md` で価格と範囲を選ぶ。",
            "6. `risk_boundary_sheet.md` で保証しないことと禁止事項を説明する。",
            "7. `client_pitch_email.md` を送る。",
            "",
            "## 推奨する最初の提案",
            "",
            f"- Flow: `{flow['id']}`",
            f"- Name: {flow['name']}",
            f"- Industry: {flow['industry']}",
            f"- Why: {flow['why_beginner_friendly']}",
            "",
            "## 守ること",
            "",
            "- 最初はPaid PoCとして売る。",
            "- 本番送信、顧客データの自動更新、支払い、採用、法務判断は含めない。",
            "- 成果保証ではなく、業務の見える化、dry-run、時間削減の測定を提供する。",
            "",
        ]
    )


def _render_target_industry_playbook(payload: dict) -> str:
    lines = [
        "# Target Industry Playbook",
        "",
        f"- Target industry: `{payload['industry']}`",
        f"- Niche: `{payload['niche']}`",
        f"- Client type: `{payload['client_type']}`",
        "",
        "## 狙いやすい企業",
        "",
        "- 毎週同じ確認、転記、返信、集計、督促が発生している。",
        "- 担当者がスプレッドシート、メール、チャット、CSVで業務を回している。",
        "- いきなり本番自動化は怖いが、業務の見える化と試作には興味がある。",
        "- 社内にAI担当者がいない、またはAIを使い始めたばかり。",
        "",
        "## 売り込みやすい切り口",
        "",
        "| Rank | Flow | 初回提案 | 価格目安 | 測定指標 |",
        "|---:|---|---|---|---|",
    ]
    for offer in payload["starter_offers"]:
        lines.append(
            f"| {offer['rank']} | `{offer['flow_id']}` {offer['name']} | {offer['first_offer']} | {offer['price_jpy']} | {offer['proof']} |"
        )
    lines.extend(
        [
            "",
            "## 最初の判断基準",
            "",
            "- 月30件以上ある業務を優先する。",
            "- 1件あたり5分以上かかる業務を優先する。",
            "- 承認者が1人に決まる業務を優先する。",
            "- 個人情報、決済、法務、採用判断は初回PoCから外す。",
            "",
        ]
    )
    return "\n".join(lines)


def _render_first_client_offer(payload: dict) -> str:
    flow = payload["recommended_flow"]
    return "\n".join(
        [
            f"# First Client Offer: {flow['name']}",
            "",
            "## 商品名",
            "",
            "企業向け自動化導入 dry-run 診断 + Paid PoC 設計",
            "",
            "## 何を提供するか",
            "",
            f"`{flow['id']}` の業務を対象に、現在の手作業を整理し、AIとローカル自動化でどこまで短縮できるかを本番送信なしで確認します。",
            "",
            "## 納品物",
            "",
            "- 業務フロー図",
            "- before/after説明",
            "- サンプルデータでのdry-run出力",
            "- 承認ポイント一覧",
            "- 時間削減の測定シート",
            "- 次に本番化する場合の安全条件",
            "",
            "## 提案価格",
            "",
            "- 初回診断: 30,000円-50,000円",
            "- Paid PoC: 80,000円-200,000円",
            "- 月次改善支援: 30,000円-100,000円/月",
            "",
            "## 売り文句",
            "",
            "いきなり社内システムを変えるのではなく、まず手作業を見える化し、サンプルデータで自動化の効果を確認します。安全に試して、続けるか止めるかを判断できます。",
            "",
        ]
    )


def _render_discovery_call_script(payload: dict) -> str:
    flow = payload["recommended_flow"]
    return "\n".join(
        [
            f"# Discovery Call Script: {flow['name']}",
            "",
            "## 1. 最初の説明",
            "",
            "今日は自動化を売り込む前に、今どこで時間がかかっているか、どこなら安全に試せるかを確認します。最初から本番システムには触りません。",
            "",
            "## 2. 質問",
            "",
            "- 毎週または毎月、繰り返している作業は何ですか。",
            "- その作業は月に何件ありますか。",
            "- 1件あたり何分かかりますか。",
            "- どのツールを使っていますか。例: Excel, Google Sheets, Gmail, Slack, LINE, Notion",
            "- ミスや遅れが起きると、何が困りますか。",
            "- 最終確認する人は誰ですか。",
            "- 自動送信してはいけないものは何ですか。",
            "- サンプルデータや匿名化したCSVは出せますか。",
            "",
            "## 3. 締め方",
            "",
            "この内容なら、まず3日程度のdry-runで、手作業の流れ、AIが作る下書き、承認ポイント、時間削減の見込みを確認できます。結果を見て、本番化するか止めるかを決めましょう。",
            "",
        ]
    )


def _render_proposal_builder(payload: dict) -> str:
    flow = payload["recommended_flow"]
    return "\n".join(
        [
            f"# Proposal Builder: {flow['name']}",
            "",
            "## 提案書テンプレート",
            "",
            "### 目的",
            "",
            f"{payload['niche']} の繰り返し業務を対象に、AIとローカル自動化で作業時間、確認漏れ、返信遅れを減らせるか検証します。",
            "",
            "### 対象業務",
            "",
            f"- 推奨フロー: `{flow['id']}` {flow['name']}",
            f"- 業務内容: {flow['summary']}",
            "",
            "### 実施内容",
            "",
            "- 現在の作業手順を整理",
            "- サンプルデータでdry-run",
            "- AI下書き、確認リスト、承認キューを作成",
            "- before/afterをレポート化",
            "- 本番化する場合の条件を整理",
            "",
            "### 成功条件",
            "",
            "- 担当者が出力を理解できる",
            "- 手作業より短い、または確認漏れが減る見込みがある",
            "- 承認者と禁止事項が明確",
            "- 継続、修正、停止の判断ができる",
            "",
        ]
    )


def _render_pricing_and_scope_menu(payload: dict) -> str:
    return "\n".join(
        [
            "# Pricing And Scope Menu",
            "",
            "| Plan | Price | Best For | Includes | Not Included |",
            "|---|---:|---|---|---|",
            "| 初回診断 | 30,000円-50,000円 | 初めてAI自動化を試す企業 | ヒアリング、業務整理、改善候補1件、簡易提案 | 実装、本番接続 |",
            "| Paid PoC | 80,000円-200,000円 | 効果を見て判断したい企業 | サンプルデータdry-run、下書き、承認キュー、測定シート、報告 | 本番送信、常時運用 |",
            "| 月次改善 | 30,000円-100,000円/月 | 小さく継続改善したい企業 | 月1-2回の改善、レポート、追加フロー相談 | 24時間監視、重い開発 |",
            "| 本番化支援 | 個別見積 | PoCで価値が確認できた企業 | connector設定、承認ルール、運用設計、監視計画 | 法務/セキュリティ責任の代行 |",
            "",
            "## 初心者向けの価格ルール",
            "",
            "- 最初から大きく売らない。",
            "- 成果保証ではなく、検証、見える化、改善提案として売る。",
            "- 安すぎると責任範囲が曖昧になるので、無料相談の次は小さな有料診断にする。",
            "- 本番化はPoC後に別契約にする。",
            "",
        ]
    )


def _render_risk_boundary_sheet(payload: dict) -> str:
    return "\n".join(
        [
            "# Risk Boundary Sheet",
            "",
            "## 保証しないこと",
            "",
            "- 売上増加や利益増加を保証しない。",
            "- 完全自動化を保証しない。",
            "- 人間の確認なしで正しい判断ができることを保証しない。",
            "- 既存システムに必ず接続できることを保証しない。",
            "",
            "## 初回PoCでやらないこと",
            "",
            "- 本番送信",
            "- 本番データの更新",
            "- 支払い、返金、採用、契約、法務判断",
            "- パスワードやAPIキーの預かり",
            "- 個人情報や機密情報を含むデータ処理",
            "",
            "## 必ず確認すること",
            "",
            "- 業務オーナー",
            "- 承認者",
            "- 使ってよいサンプルデータ",
            "- 出力を確認する人",
            "- stop条件",
            "- 本番化する場合の責任範囲",
            "",
        ]
    )


def _render_30_day_business_launch_plan(payload: dict) -> str:
    return "\n".join(
        [
            "# 30 Day Business Launch Plan",
            "",
            "## Week 1: 提案の型を作る",
            "",
            "- `first_client_offer.md` を自分の言葉に直す。",
            "- 10社の候補企業をリスト化する。",
            "- 1つの業種、1つの業務だけに絞る。",
            "",
            "## Week 2: ヒアリングを取る",
            "",
            "- `client_pitch_email.md` を送る。",
            "- 返信があった企業に `discovery_call_script.md` で聞く。",
            "- 無料相談で終わらせず、小さな有料診断を提案する。",
            "",
            "## Week 3: Paid PoCを実施する",
            "",
            "- サンプルデータだけでdry-runを作る。",
            "- before/afterと承認ポイントを見せる。",
            "- 測定シートで時間削減の可能性を確認する。",
            "",
            "## Week 4: 継続提案に進む",
            "",
            "- 継続、修正、停止をクライアントに選んでもらう。",
            "- 本番化する場合は別契約にする。",
            "- 月次改善支援を小さく提案する。",
            "",
        ]
    )


def _render_client_pitch_email(payload: dict) -> str:
    flow = payload["recommended_flow"]
    return "\n".join(
        [
            f"# Client Pitch Email: {flow['name']}",
            "",
            f"Subject: {payload['niche']}業務の手作業を小さく自動化検証しませんか",
            "",
            "{{会社名}}",
            "{{担当者名}} 様",
            "",
            "突然のご連絡失礼します。",
            "",
            f"{payload['niche']}まわりの繰り返し業務について、いきなり本番システムを変えるのではなく、サンプルデータでAI自動化の効果を確認する小さな診断を行っています。",
            "",
            f"最初の対象としては `{flow['name']}` のような業務が向いています。",
            "",
            "初回は以下だけを確認します。",
            "",
            "- どの作業に時間がかかっているか",
            "- 月に何件あるか",
            "- どこで確認漏れや遅れが起きるか",
            "- 本番送信せずに試せるサンプルデータがあるか",
            "",
            "もし合いそうであれば、3日程度のPaid PoCとして、業務フロー、AI下書き、承認ポイント、before/afterレポートまで作れます。",
            "",
            "一度15分ほど、対象になりそうな業務があるかだけ確認できればと思います。",
            "",
            "{{あなたの名前}}",
            "",
        ]
    )


def _render_quickstart_start(flow: dict, payload: dict) -> str:
    return "\n".join(
        [
            f"# Quickstart Workspace: {flow['name']}",
            "",
            "## Run Order",
            "",
            "1. Open `beginner_sales/selected_flow_demo.html`.",
            "2. Read `beginner_sales/client_questions.md`.",
            "3. Run the local automation dry-run:",
            "",
            "```bash",
            "cd flow_project",
            "python3 scripts/run_automation.py",
            "python3 scripts/approve_all.py --approver owner@example.com",
            "```",
            "",
            "4. Open `flow_project/automation_output/status_report.md`.",
            "5. Open `demo_site/index.html` for the client-facing overview.",
            "",
            "## Generated Paths",
            "",
            f"- Flow project: `{payload['flow_project']}`",
            f"- Beginner sales: `{payload['beginner_sales']}`",
            f"- Demo site: `{payload['demo_site']}`",
            "",
        ]
    )


def _render_bundle_index(flow: dict, payload: dict) -> str:
    return "\n".join(
        [
            f"# Client Automation Bundle: {flow['name']}",
            "",
            "This folder combines the runnable dry-run flow, beginner sales materials, client-ready delivery assets, and demo site.",
            "",
            "## Contents",
            "",
            f"- `flow_project/`: local dry-run automation system for `{payload['flow_id']}`.",
            "- `beginner_sales/`: pitch, proposal, ROI calculator, and visual demo.",
            "- `client_ready/`: intake, pricing, security, maintenance, and handoff assets.",
            "- `demo_site/index.html`: browser-friendly overview for a client conversation.",
            "",
            "## Safety",
            "",
            "The default system writes local files only. Real connectors require separate approval, credentials, and data review.",
            "",
        ]
    )


def _render_connector_doctor(payload: dict) -> str:
    lines = ["# Connector Doctor", "", f"- Status: `{payload['status']}`", f"- Project: `{payload['project']}`", "", "| ID | Type | Status | Detail |", "|---|---|---|---|"]
    for check in payload["checks"]:
        lines.append(f"| `{check['id']}` | {check['type']} | `{check['status']}` | {check['detail']} |")
    lines.extend(
        [
            "",
            "## Next Step",
            "",
            "Keep local dry-run connectors enabled until the client approves data handling, credentials, rollback, and human approval rules.",
            "",
        ]
    )
    return "\n".join(lines)


def _render_client_report(payload: dict) -> str:
    lines = [
        "# Client Automation Report",
        "",
        f"- Status: `{payload['status']}`",
        f"- Automation status: `{payload['automation_status']}`",
        f"- Rows processed: `{payload['rows_processed']}`",
        "",
        "## Available Evidence",
        "",
    ]
    if payload["available_files"]:
        lines.extend(f"- `{name}`: `{path}`" for name, path in payload["available_files"].items())
    else:
        lines.append("- No automation output files were found. Run the flow before sharing this report.")
    lines.extend(
        [
            "",
            "## Client Review Questions",
            "",
            "- Is the queue understandable?",
            "- Are the drafts useful enough to revise?",
            "- Is the approval point correct?",
            "- Should this pilot continue, revise, or stop?",
            "",
        ]
    )
    return "\n".join(lines)


def _render_package_readme(payload: dict) -> str:
    return "\n".join(
        [
            "# Client Demo Package",
            "",
            f"- Status: `{payload['status']}`",
            f"- Files packaged: `{payload['file_count']}`",
            f"- Zip: `{payload['package']}`",
            "",
            "This package is for client review. Check that no private credentials or client secrets are included before sharing.",
            "",
        ]
    )


def _render_complete_delivery_guide(payload: dict) -> str:
    return "\n".join(
        [
            f"# Final Delivery Guide: {payload['flow_name']}",
            "",
            f"- Status: `{payload['status']}`",
            f"- Flow ID: `{payload['flow_id']}`",
            f"- Rows processed in dry-run: `{payload['rows_processed']}`",
            f"- Approved draft items: `{payload['approved_items']}`",
            f"- Connector status: `{payload['connector_status']}`",
            "",
            "## Open These Files In This Order",
            "",
            f"1. `{payload['quickstart']}/START_HERE.md`",
            f"2. `{payload['quickstart']}/beginner_sales/selected_flow_demo.html`",
            f"3. `{payload['client_report']}`",
            f"4. `{payload['demo_site']}`",
            f"5. `{payload['client_demo_package']}`",
            "6. `revenue_readiness_scorecard.md`",
            "7. `sales_closing_script.md`",
            "8. `paid_poc_scope.md`",
            "9. `value_measurement_sheet.csv`",
            "10. `pre_contract_checklist.md`",
            "11. `client_proposal_email.md`",
            "12. `first_30_days_plan.md`",
            "13. `proof_of_value_template.md`",
            "14. `oss_pattern_benchmark.md`",
            "15. `integration_backlog.md`",
            "16. `deployment_options.md`",
            "17. `production_observability_plan.md`",
            "18. `automation_opportunity_scorecard.csv`",
            "19. `client_onboarding_form.md`",
            "20. `go_live_decision.md`",
            "21. `client_command_center.html`",
            "22. `side_business_starter_10.md`",
            "23. `before_after_demo.html`",
            "24. `business_launch/START_HERE_BUSINESS_LAUNCH.md`",
            "",
            "## What To Tell The Client",
            "",
            "- The first version runs locally and writes files only.",
            "- The workflow already produced a queue, drafts, approval records, and a readable report.",
            "- Real external sends, production updates, payments, access grants, and sensitive-data actions stay blocked until the client approves connectors and rollback rules.",
            "",
            "## Handoff Decision",
            "",
            "No next recommendation is required before review. The client can now choose one of three decisions: continue the pilot, revise the flow, or stop.",
            "",
        ]
    )


def _render_completion_checklist(payload: dict) -> str:
    checks = [
        ("Quickstart workspace created", payload["quickstart"]),
        ("Dry-run executed", f"rows_processed={payload['rows_processed']}"),
        ("Draft approvals exported", f"approved_items={payload['approved_items']}"),
        ("Connector setup checked", payload["connector_doctor"]),
        ("Client report generated", payload["client_report"]),
        ("Demo site generated", payload["demo_site"]),
        ("Client demo zip packaged", payload["client_demo_package"]),
        ("Revenue readiness scored", f"score={payload['revenue_score']['total']}"),
        ("Paid PoC scope prepared", "paid_poc_scope.md"),
        ("Value measurement sheet prepared", "value_measurement_sheet.csv"),
        ("Pre-contract checklist prepared", "pre_contract_checklist.md"),
        ("Client proposal email prepared", "client_proposal_email.md"),
        ("First 30 days plan prepared", "first_30_days_plan.md"),
        ("Proof of value template prepared", "proof_of_value_template.md"),
        ("OSS pattern benchmark prepared", "oss_pattern_benchmark.md"),
        ("Integration backlog prepared", "integration_backlog.md"),
        ("Deployment options prepared", "deployment_options.md"),
        ("Production observability plan prepared", "production_observability_plan.md"),
        ("Automation opportunity scorecard prepared", "automation_opportunity_scorecard.csv"),
        ("Client onboarding form prepared", "client_onboarding_form.md"),
        ("Go-live decision gate prepared", "go_live_decision.md"),
        ("Client command center prepared", "client_command_center.html"),
        ("Side business starter 10 prepared", "side_business_starter_10.md"),
        ("Before/after demo prepared", "before_after_demo.html"),
        ("Business launch proposal pack prepared", payload["business_launch"]),
    ]
    lines = ["# Completion Checklist", ""]
    for label, detail in checks:
        lines.append(f"- [x] {label}: `{detail}`")
    lines.extend(
        [
            "",
            "## Before Sharing Outside Your Machine",
            "",
            "- [ ] Confirm the zip contains no secrets or client private data.",
            "- [ ] Confirm the client understands this is a dry-run until real connectors are approved.",
            "- [ ] Confirm the client has one named approval owner.",
            "",
        ]
    )
    return "\n".join(lines)


def _revenue_readiness_score(payload: dict) -> dict:
    criteria = [
        ("visible_demo", 15, payload["demo_asset_count"] > 0, "Demo site and visual flow assets exist."),
        ("working_dry_run", 20, payload["rows_processed"] > 0, "The local flow produced dry-run evidence."),
        ("approval_evidence", 15, payload["approved_items"] > 0, "Approval records and local outbox files exist."),
        ("client_report", 15, payload["report_status"] == "ready", "Client-readable report exists."),
        ("safe_boundary", 15, payload["connector_status"] in {"needs_setup", "ready"}, "Production connectors are explicitly gated."),
        ("share_package", 10, payload["package_file_count"] > 0, "Shareable demo package exists."),
        ("paid_scope", 10, True, "Paid PoC scope, closing script, and value sheet are generated."),
    ]
    items = [
        {"id": item_id, "points": points if passed else 0, "max_points": points, "passed": passed, "evidence": evidence}
        for item_id, points, passed, evidence in criteria
    ]
    total = sum(item["points"] for item in items)
    level = "sellable_poc" if total >= 85 else "review_before_selling" if total >= 70 else "not_ready"
    return {"total": total, "level": level, "items": items}


def _render_revenue_scorecard(payload: dict) -> str:
    score = payload["revenue_score"]
    lines = [
        "# Revenue Readiness Scorecard",
        "",
        f"- Flow: `{payload['flow_name']}`",
        f"- Niche: `{payload['niche']}`",
        f"- Score: `{score['total']}/100`",
        f"- Level: `{score['level']}`",
        "",
        "## Score Detail",
        "",
        "| Item | Points | Evidence |",
        "|---|---:|---|",
    ]
    for item in score["items"]:
        lines.append(f"| `{item['id']}` | {item['points']}/{item['max_points']} | {item['evidence']} |")
    lines.extend(
        [
            "",
            "## Paid PoC Positioning",
            "",
            "This is ready to sell as a bounded Paid PoC when the client accepts three limits: local dry-run first, human approval before external actions, and measurable baseline comparison.",
            "",
            "## Do Not Sell As",
            "",
            "- Fully autonomous production automation.",
            "- Guaranteed income system.",
            "- A replacement for client approval, credentials review, or legal/security review.",
            "",
        ]
    )
    return "\n".join(lines)


def _render_sales_closing_script(payload: dict) -> str:
    return "\n".join(
        [
            f"# Sales Closing Script: {payload['flow_name']}",
            "",
            "## Opening",
            "",
            f"I prepared a local dry-run for your {payload['niche']} workflow. It does not send messages or update production systems, but it shows the queue, draft outputs, approval points, and report evidence.",
            "",
            "## Proof To Show",
            "",
            f"- Demo site: `{payload['demo_site']}`",
            f"- Client report: `{payload['client_report']}`",
            f"- Approval evidence: `{payload['quickstart']}/flow_project/automation_output/approved_actions.csv`",
            f"- Local outbox: `{payload['quickstart']}/flow_project/local_outbox/email_drafts.md`",
            "",
            "## Close",
            "",
            "If this matches the real workflow, the next paid step is a small PoC: we connect one approved sample data source, keep human approval, measure time saved, and decide whether to continue.",
            "",
            "## Buyer Questions",
            "",
            "- Who owns this workflow today?",
            "- How many items are processed each week?",
            "- What mistakes or delays are most expensive?",
            "- Who must approve before anything reaches a customer or production system?",
            "- What result would make a paid PoC worth continuing?",
            "",
        ]
    )


def _render_paid_poc_scope(payload: dict) -> str:
    return "\n".join(
        [
            f"# Paid PoC Scope: {payload['flow_name']}",
            "",
            "## Objective",
            "",
            f"Validate whether `{payload['flow_id']}` can reduce repeated manual work for a {payload['client_type']} without bypassing human approval.",
            "",
            "## Included",
            "",
            "- One workflow map and before/after explanation.",
            "- One approved sample input source or CSV export.",
            "- Local dry-run automation with queue, drafts, approval list, and report.",
            "- Connector readiness review.",
            "- One value measurement sheet.",
            "- One handoff call or written handoff note.",
            "",
            "## Excluded Until Separate Approval",
            "",
            "- Production sends or writes.",
            "- Payment, hiring, access, or legal decisions.",
            "- Handling secrets or regulated personal data without a data review.",
            "- Ongoing monitoring beyond the PoC window.",
            "",
            "## Acceptance Criteria",
            "",
            "- The client can identify the queue and approval owner.",
            "- The dry-run output is useful enough to revise rather than discard.",
            "- The value sheet has baseline time, pilot time, and decision notes.",
            "- The client chooses continue, revise, or stop.",
            "",
        ]
    )


def _render_value_measurement_csv(payload: dict) -> str:
    rows = [
        ["metric", "example_value", "owner", "notes"],
        ["manual_items_per_month", "80", "client", "Ask for current monthly volume."],
        ["manual_minutes_per_item", "8", "client", "Baseline before automation."],
        ["pilot_minutes_per_item", "4", "operator", "Measured during dry-run PoC."],
        ["loaded_hourly_cost", "35", "client", "Use realistic labor cost."],
        ["monthly_tool_cost", "0", "operator", "Local dry-run starts at zero tool cost."],
        ["estimated_monthly_hours_saved", "=manual_items_per_month*(manual_minutes_per_item-pilot_minutes_per_item)/60", "sheet", "Formula for spreadsheet users."],
        ["estimated_monthly_savings", "=estimated_monthly_hours_saved*loaded_hourly_cost-monthly_tool_cost", "sheet", "Use as directional estimate, not guarantee."],
        ["pilot_fee_floor", "=estimated_monthly_savings*1.5", "operator", "Sanity check for PoC pricing discussion."],
        ["continue_threshold", "client says output is useful and measurable", "client", "Continue only if value and safety are visible."],
    ]
    return "\n".join(",".join(str(cell) for cell in row) for row in rows) + "\n"


def _render_pre_contract_checklist(payload: dict) -> str:
    return "\n".join(
        [
            f"# Pre-Contract Checklist: {payload['flow_name']}",
            "",
            "## Do Not Start Paid Work Until",
            "",
            "- [ ] The client has named a workflow owner.",
            "- [ ] The client has approved a sample data source or anonymized export.",
            "- [ ] The client understands the first version is a dry-run.",
            "- [ ] The client agrees that external sends, production writes, payments, hiring, access, and legal decisions are excluded.",
            "- [ ] Success metrics are written in `value_measurement_sheet.csv`.",
            "- [ ] The paid PoC boundary in `paid_poc_scope.md` is accepted.",
            "- [ ] A stop condition is agreed before work starts.",
            "",
            "## Minimum Paid PoC Evidence",
            "",
            f"- Revenue score: `{payload['revenue_score']['total']}/100`",
            f"- Demo site: `{payload['demo_site']}`",
            f"- Client report: `{payload['client_report']}`",
            f"- Connector review: `{payload['connector_doctor']}`",
            "",
        ]
    )


def _render_client_proposal_email(payload: dict) -> str:
    return "\n".join(
        [
            f"# Client Proposal Email: {payload['flow_name']}",
            "",
            f"Subject: Small dry-run PoC for your {payload['niche']} workflow",
            "",
            "Hi {{client_name}},",
            "",
            f"I prepared a safe local demo for a `{payload['flow_name']}` workflow. It shows the queue, draft outputs, approval point, and report without sending external messages or updating production systems.",
            "",
            "The useful next step is a small paid PoC with clear limits:",
            "",
            "- use one approved sample data source,",
            "- keep human approval before any external action,",
            "- measure baseline time vs pilot time,",
            "- decide continue, revise, or stop.",
            "",
            "I would suggest reviewing the demo first, then confirming whether this workflow is worth a short PoC.",
            "",
            "Best,",
            "{{your_name}}",
            "",
        ]
    )


def _render_first_30_days_plan(payload: dict) -> str:
    return "\n".join(
        [
            f"# First 30 Days Plan: {payload['flow_name']}",
            "",
            "## Day 1",
            "",
            "- Confirm workflow owner, sample data, excluded actions, and success metrics.",
            "- Review `pre_contract_checklist.md` and `paid_poc_scope.md`.",
            "",
            "## Days 2-5",
            "",
            "- Adapt sample columns to the client workflow.",
            "- Run dry-run output and review drafts with the owner.",
            "- Update approval point and stop condition.",
            "",
            "## Days 6-14",
            "",
            "- Compare baseline and pilot timing in `value_measurement_sheet.csv`.",
            "- Fix obvious workflow mismatches.",
            "- Keep all production connectors disabled unless separately approved.",
            "",
            "## Days 15-30",
            "",
            "- Produce `proof_of_value_template.md` with before/after evidence.",
            "- Decide continue, revise, or stop.",
            "- If continuing, write the maintenance and connector approval plan.",
            "",
        ]
    )


def _render_proof_of_value_template(payload: dict) -> str:
    return "\n".join(
        [
            f"# Proof Of Value Template: {payload['flow_name']}",
            "",
            "## Before / After",
            "",
            "| Metric | Before | After Dry-Run | Evidence |",
            "|---|---:|---:|---|",
            "| Items processed |  |  | `automation_output/run_log.json` |",
            "| Minutes per item |  |  | `value_measurement_sheet.csv` |",
            "| Approval completeness |  |  | `automation_output/approved_actions.csv` |",
            "| Draft usefulness |  |  | owner review notes |",
            "",
            "## Client Decision",
            "",
            "- [ ] Continue to a revised dry-run.",
            "- [ ] Continue to connector approval planning.",
            "- [ ] Stop because value or safety is not clear enough.",
            "",
            "## Evidence Links",
            "",
            f"- Client report: `{payload['client_report']}`",
            f"- Demo site: `{payload['demo_site']}`",
            f"- Connector doctor: `{payload['connector_doctor']}`",
            "",
        ]
    )


def _render_oss_pattern_benchmark(payload: dict) -> str:
    return "\n".join(
        [
            f"# OSS Pattern Benchmark: {payload['flow_name']}",
            "",
            "This benchmark translates proven public automation patterns into this sellable local-first workspace.",
            "",
            "## Patterns To Imitate",
            "",
            "| Source | Public pattern | What this workspace should copy |",
            "|---|---|---|",
            "| n8n | Visual workflow templates, self-hosted AI starter kits, many integrations | Keep flows visible, template-driven, and easy to adapt before production connectors are enabled. |",
            "| Activepieces | Type-safe pieces and integrations that can become MCP servers for AI tools | Treat every connector as a reusable piece with a clear schema, permission boundary, and MCP-ready future path. |",
            "| Windmill | Scripts can become webhooks, workflows, schedules, and auto-generated UIs | Keep each flow scriptable first, then expose it as a webhook or simple UI only after the dry-run works. |",
            "| Trigger.dev | Long-running AI workflows with retries, queues, observability, and human approval | Add production execution rules before any client workflow moves beyond a local dry-run. |",
            "| Community template libraries | Large ready-to-import workflow examples | Convert common templates into reviewed business flows instead of copying unknown automation blindly. |",
            "",
            "## Design Rule",
            "",
            "Copy patterns, not code. Keep this project adapter-only unless a license review explicitly approves importing third-party code.",
            "",
            "## Next Product Standard",
            "",
            "- Every flow has a dry-run path, approval point, connector boundary, and measurable report.",
            "- Every external integration has a setup checklist and stop condition.",
            "- Every production candidate has retries, queues, logs, approval audit, and rollback notes.",
            "",
        ]
    )


def _render_integration_backlog(payload: dict) -> str:
    return "\n".join(
        [
            f"# Integration Backlog: {payload['flow_name']}",
            "",
            "Prioritize integrations that make the first paid PoC easier to sell, safer to run, and easier to measure.",
            "",
            "## Priority 1: Common Business Data",
            "",
            "- Google Sheets adapter: import/export queues, status, and value measurement rows.",
            "- CSV folder adapter: keep the zero-credential dry-run path for cautious clients.",
            "- Gmail or Outlook draft adapter: create drafts only until the client approves sending.",
            "- Slack or Teams draft adapter: write approval-ready messages before posting is enabled.",
            "- Webhook input adapter: receive form, CRM, or support payloads behind a validation step.",
            "",
            "## Priority 2: Sales And Operations Systems",
            "",
            "- CRM adapter for HubSpot, Salesforce, or Pipedrive field updates after approval.",
            "- Airtable or Notion adapter for lightweight client databases.",
            "- Calendar adapter for follow-up scheduling and missed-response reminders.",
            "- File storage adapter for Google Drive, OneDrive, or Dropbox document handoff.",
            "",
            "## Priority 3: OSS Platform Bridges",
            "",
            "- n8n import notes for converting a flow into a visual workflow.",
            "- Activepieces piece notes with MCP compatibility targets.",
            "- Windmill deployment notes for script-to-webhook and script-to-UI delivery.",
            "- Trigger.dev-style worker notes for long-running queues and retries.",
            "",
            "## Connector Acceptance Criteria",
            "",
            "- Includes `.env.example` keys and a no-secret sample.",
            "- Supports dry-run mode and approval-only mode.",
            "- Writes run logs and error states.",
            "- Documents required scopes, data touched, and rollback.",
            "- Can be explained to a non-programmer in one paragraph.",
            "",
        ]
    )


def _render_deployment_options(payload: dict) -> str:
    return "\n".join(
        [
            f"# Deployment Options: {payload['flow_name']}",
            "",
            "Choose the smallest deployment that proves value without creating hidden maintenance risk.",
            "",
            "## Option 1: Local dry-run",
            "",
            "- Best for first meetings, PoCs, and clients who cannot approve credentials yet.",
            "- Runs on local files and produces reports, drafts, approval CSVs, and demo assets.",
            "- Stop if the client cannot name the owner, sample data, or approval rule.",
            "",
            "## Option 2: Client machine or VPS self-host",
            "",
            "- Best when the client wants data control and predictable cost.",
            "- Use Docker or a managed VPS only after backup, update, and access rules are written.",
            "- Stop if there is no owner for uptime, backups, and credential rotation.",
            "",
            "## Option 3: n8n or Activepieces visual workflow",
            "",
            "- Best when the client wants a low-code operations team to inspect and adjust steps.",
            "- Keep the generated flow as the source explanation, then rebuild the approved steps visually.",
            "- Stop if the visual workflow cannot preserve approval and dry-run boundaries.",
            "",
            "## Option 4: Windmill-style script, webhook, or UI",
            "",
            "- Best when the client wants code-first scripts exposed as internal tools.",
            "- Promote only one stable script at a time into a webhook or UI.",
            "- Stop if inputs are not validated or the output cannot be rolled back.",
            "",
            "## Option 5: Durable worker or Trigger.dev-style queue",
            "",
            "- Best for long-running automations, retries, queues, scheduled tasks, and AI steps.",
            "- Add explicit retry limits, queue ownership, observability, and dead-letter handling.",
            "- Stop if failures would be invisible to the client or operator.",
            "",
        ]
    )


def _render_production_observability_plan(payload: dict) -> str:
    return "\n".join(
        [
            f"# Production Observability Plan: {payload['flow_name']}",
            "",
            "Do not move from dry-run to production until the operator can see what happened, why it happened, and what to do next.",
            "",
            "## Required Signals",
            "",
            "- Run history: start time, end time, status, rows processed, and operator.",
            "- retries: attempt count, last error, next retry time, and retry limit.",
            "- queues: pending, running, succeeded, failed, and dead-letter item counts.",
            "- approval audit: who approved, what was approved, when it was approved, and where the evidence is stored.",
            "- Connector health: credential present, scope reviewed, last successful call, and disabled state.",
            "- Value tracking: baseline time, pilot time, avoided manual steps, and client decision.",
            "",
            "## Alert Rules",
            "",
            "- Alert the operator when any production write fails.",
            "- Alert the approval owner when queue age exceeds the agreed service window.",
            "- Pause external actions when connector health changes from ready to review.",
            "- Escalate dead-letter items before the next scheduled run.",
            "",
            "## Monthly Review",
            "",
            "- Review top errors and remove brittle steps.",
            "- Confirm credentials, scopes, and approval owners are still current.",
            "- Compare measured value against the paid PoC assumptions.",
            "- Decide continue, revise, reduce scope, or retire the automation.",
            "",
        ]
    )


def _render_automation_opportunity_scorecard(payload: dict) -> str:
    rows = [
        ["metric", "score_0_to_5", "evidence_needed", "sellable_now"],
        ["pain_frequency", "4", "How often this workflow happens each month.", "yes if weekly or higher"],
        ["manual_time_cost", "4", "Minutes per item and loaded hourly cost.", "yes if savings can fund a small PoC"],
        ["data_access_clarity", "3", "Sample CSV, spreadsheet, or export approved by the client.", "yes if sample data is approved"],
        ["approval_owner_clarity", "5", "Named person who approves drafts or production actions.", "yes if one owner is named"],
        ["risk_boundary_clarity", "4", "Excluded actions, sensitive data, and stop condition.", "yes if excluded actions are written"],
        ["dry_run_evidence", "5", "Queue, drafts, approval records, report, and demo assets.", "yes if generated files are reviewable"],
        ["workflow_fit_score", "=SUM(B2:B7)", "Score 22+ is a good paid PoC candidate.", "sellable_now"],
    ]
    return "\n".join(",".join(str(cell) for cell in row) for row in rows) + "\n"


def _render_client_onboarding_form(payload: dict) -> str:
    return "\n".join(
        [
            f"# Client Onboarding Form: {payload['flow_name']}",
            "",
            "Use this before touching real accounts, client data, or production connectors.",
            "",
            "## Client Basics",
            "",
            "- Company:",
            "- Department:",
            "- Main contact:",
            "- Billing contact:",
            "- Workflow owner:",
            "- Approval Owner:",
            "",
            "## Workflow Facts",
            "",
            f"- Proposed workflow: `{payload['flow_name']}`",
            f"- Niche: `{payload['niche']}`",
            "- Current manual process:",
            "- Monthly item volume:",
            "- Minutes per item:",
            "- Current tools used:",
            "- Most expensive delay or mistake:",
            "",
            "## Data And Access",
            "",
            "- Approved sample data source:",
            "- Data fields included:",
            "- Sensitive data excluded:",
            "- Credentials owner:",
            "- Systems that must never be changed without approval:",
            "",
            "## Approval And Stop Rules",
            "",
            "- Who reviews drafts:",
            "- Who approves external sends or production writes:",
            "- Stop condition:",
            "- Rollback contact:",
            "- Review cadence:",
            "",
            "## Paid PoC Decision",
            "",
            "- Budget range:",
            "- Expected decision date:",
            "- Continue criteria:",
            "- Revise criteria:",
            "- Stop criteria:",
            "",
        ]
    )


def _render_go_live_decision(payload: dict) -> str:
    return "\n".join(
        [
            f"# Go-Live Decision: {payload['flow_name']}",
            "",
            "This gate decides whether the dry-run can become a production automation.",
            "",
            "## Current Recommendation",
            "",
            "Do Not Go Live until every required checkbox below is complete. Keep using local dry-run output for client review.",
            "",
            "## Required Before Go-Live",
            "",
            "- [ ] `client_onboarding_form.md` is complete.",
            "- [ ] `automation_opportunity_scorecard.csv` shows a strong paid PoC fit.",
            "- [ ] Client has approved data source, fields, credentials owner, and excluded data.",
            "- [ ] Approval Owner is named for drafts and production actions.",
            "- [ ] Connector scopes and rollback steps are documented.",
            "- [ ] `production_observability_plan.md` has run history, retries, queues, approval audit, alerts, and monthly review owner.",
            "- [ ] A final dry-run report was reviewed by the client.",
            "- [ ] First production run has a human operator watching it.",
            "",
            "## Go-Live Choices",
            "",
            "- Continue dry-run: value is promising but production safety is incomplete.",
            "- Limited go-live: one connector, one workflow owner, one rollback path, and human approval.",
            "- Stop: value, safety, or ownership is not clear enough.",
            "",
            "## First Production Run Notes",
            "",
            "- Date:",
            "- Operator:",
            "- Approval Owner:",
            "- Connector enabled:",
            "- Items processed:",
            "- Errors:",
            "- Decision after first run:",
            "",
        ]
    )


def _render_client_command_center(payload: dict) -> str:
    cards = [
        (
            "Start Here",
            "Open the final guide, demo site, and client report before reading the deeper files.",
            [
                ("Final delivery guide", "FINAL_DELIVERY_GUIDE.md"),
                ("Demo site", "demo_site/index.html"),
                ("Client report", "client_report/client_report.html"),
            ],
        ),
        (
            "Sellable PoC",
            "Use these files to decide whether the workflow is worth pitching as a bounded paid pilot.",
            [
                ("Revenue readiness", "revenue_readiness_scorecard.md"),
                ("Opportunity scorecard", "automation_opportunity_scorecard.csv"),
                ("Paid PoC scope", "paid_poc_scope.md"),
                ("Proposal email", "client_proposal_email.md"),
            ],
        ),
        (
            "Client Intake",
            "Capture the owner, approval rules, data source, exclusions, and stop condition.",
            [
                ("Client onboarding form", "client_onboarding_form.md"),
                ("Pre-contract checklist", "pre_contract_checklist.md"),
                ("Value measurement sheet", "value_measurement_sheet.csv"),
            ],
        ),
        (
            "Production Path",
            "Keep production blocked until deployment, connectors, monitoring, and approval audit are clear.",
            [
                ("Deployment options", "deployment_options.md"),
                ("Integration backlog", "integration_backlog.md"),
                ("Observability plan", "production_observability_plan.md"),
                ("Go-Live Gate", "go_live_decision.md"),
            ],
        ),
    ]
    card_html = "\n".join(_command_center_card(title, body, links) for title, body, links in cards)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Client Command Center - {html.escape(payload['flow_name'])}</title>
  <style>
    body {{ margin: 0; font-family: Arial, sans-serif; color: #182235; background: #f6f7f9; }}
    header {{ padding: 28px; background: #ffffff; border-bottom: 1px solid #d9dee7; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 24px; }}
    .summary {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin: 20px 0; }}
    .stat, .card {{ background: #ffffff; border: 1px solid #d9dee7; border-radius: 8px; padding: 16px; }}
    .stat strong {{ display: block; font-size: 22px; margin-bottom: 4px; }}
    .grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }}
    h1, h2 {{ margin-top: 0; }}
    a {{ color: #1659b7; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    ul {{ padding-left: 20px; }}
    code {{ background: #eef2f7; padding: 2px 5px; border-radius: 4px; }}
    @media (max-width: 820px) {{ .summary, .grid {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <header>
    <h1>Client Command Center</h1>
    <p>{html.escape(payload['flow_name'])} for {html.escape(payload['client_type'])} / {html.escape(payload['niche'])}</p>
  </header>
  <main>
    <section class="summary" aria-label="Workspace summary">
      <div class="stat"><strong>{html.escape(str(payload['rows_processed']))}</strong>rows processed</div>
      <div class="stat"><strong>{html.escape(str(payload['approved_items']))}</strong>approved drafts</div>
      <div class="stat"><strong>{html.escape(str(payload['revenue_score']['total']))}/100</strong>revenue readiness</div>
      <div class="stat"><strong>{html.escape(payload['connector_status'])}</strong>connector status</div>
    </section>
    <section class="grid">
      {card_html}
    </section>
  </main>
</body>
</html>
"""


def _command_center_card(title: str, body: str, links: list[tuple[str, str]]) -> str:
    items = "\n".join(f"<li><a href='{html.escape(path)}'>{html.escape(label)}</a> <code>{html.escape(path)}</code></li>" for label, path in links)
    return f"""<article class="card">
  <h2>{html.escape(title)}</h2>
  <p>{html.escape(body)}</p>
  <ul>{items}</ul>
</article>"""


def _render_side_business_starter_10(payload: dict) -> str:
    lines = [
        "# Side Business Starter 10",
        "",
        "These are the easiest workflows to explain, demo, and sell as bounded dry-run PoCs. Start here before browsing the full catalog.",
        "",
        "| Rank | Flow ID | Buyer | Why It Sells | First Proof |",
        "|---:|---|---|---|---|",
    ]
    buyers = {
        "invoice-document-followup": "accounting teams",
        "support-reply-draft": "support teams",
        "weekly-kpi-report": "operations managers",
        "crm-lead-cleanup": "sales teams",
        "lead-routing-followup": "local service businesses",
        "appointment-reminder": "clinics and salons",
        "order-shipping-status": "ecommerce shops",
        "inventory-reorder-alert": "retail and ecommerce teams",
        "candidate-interview-scheduling": "small HR teams",
        "field-service-dispatch": "field service teams",
    }
    for index, flow in enumerate(_starter_flows(), start=1):
        lines.append(
            f"| {index} | `{flow['id']}` | {buyers.get(flow['id'], flow['industry'])} | {flow['summary']} | `{flow['success_metrics'][0]}` |"
        )
    lines.extend(
        [
            "",
            "## Rule",
            "",
            "Sell one visible workflow, run one dry-run, measure one before/after metric, then decide continue, revise, or stop.",
            "",
        ]
    )
    return "\n".join(lines)


def _render_before_after_demo(payload: dict) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Before / After Demo - {html.escape(payload['flow_name'])}</title>
  <style>
    body {{ margin: 0; font-family: Arial, sans-serif; background: #f7f8fa; color: #172033; }}
    header {{ background: #ffffff; border-bottom: 1px solid #d9dee7; padding: 28px; }}
    main {{ max-width: 1060px; margin: 0 auto; padding: 24px; }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
    section {{ background: #ffffff; border: 1px solid #d9dee7; border-radius: 8px; padding: 18px; }}
    .metric {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 16px; }}
    .metric div {{ background: #eef2f7; padding: 14px; border-radius: 8px; }}
    code {{ background: #eef2f7; padding: 2px 5px; border-radius: 4px; }}
    @media (max-width: 760px) {{ .grid, .metric {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <header>
    <h1>Before / After Demo</h1>
    <p>{html.escape(payload['flow_name'])} for {html.escape(payload['niche'])}</p>
  </header>
  <main>
    <div class="grid">
      <section>
        <h2>Before</h2>
        <ul>
          <li>Manual queue review across spreadsheets, email, and chat.</li>
          <li>Follow-up drafts are written from scratch.</li>
          <li>Approval evidence is scattered or missing.</li>
          <li>Value is hard to prove after the work is done.</li>
        </ul>
      </section>
      <section>
        <h2>After Dry-Run</h2>
        <ul>
          <li>Work queue, drafts, approval list, and report are generated locally.</li>
          <li>Human approval remains required before any external action.</li>
          <li>Client can inspect evidence before committing to production.</li>
          <li>Value is measured in the generated scorecards.</li>
        </ul>
      </section>
    </div>
    <section>
      <h2>Proof From This Workspace</h2>
      <div class="metric">
        <div><strong>{html.escape(str(payload['rows_processed']))}</strong><br>rows processed</div>
        <div><strong>{html.escape(str(payload['approved_items']))}</strong><br>approved drafts</div>
        <div><strong>{html.escape(str(payload['revenue_score']['total']))}/100</strong><br>sellable PoC score</div>
      </div>
      <p>Open <code>client_command_center.html</code> to navigate the full delivery pack.</p>
    </section>
  </main>
</body>
</html>
"""


def _collect_demo_assets(source: Path) -> list[dict]:
    assets = []
    for path in _collect_demo_file_paths(source):
        rel = path.relative_to(source).as_posix()
        assets.append({"path": rel, "title": _title_from_path(path), "kind": path.suffix.lstrip(".") or "file"})
    return assets[:200]


def _collect_demo_file_paths(source: Path) -> list[Path]:
    if not source.exists():
        return []
    paths = []
    for path in sorted(source.rglob("*")):
        if not path.is_file():
            continue
        if any(part.startswith(".") for part in path.relative_to(source).parts):
            continue
        if path.suffix.lower() in DEMO_EXTENSIONS and path.name not in {"client_demo_package.zip"}:
            paths.append(path)
    return paths


def _title_from_path(path: Path) -> str:
    if path.suffix.lower() in {".md", ".html"}:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return path.name
        for line in text.splitlines():
            stripped = line.strip().strip("#").strip()
            if stripped and not stripped.startswith("<"):
                return stripped[:80]
    return path.name


def _render_demo_site(title: str, assets: list[dict]) -> str:
    rows = "\n".join(
        f"<tr><td>{html.escape(asset['title'])}</td><td><code>{html.escape(asset['kind'])}</code></td><td><a href='../{html.escape(asset['path'])}'>{html.escape(asset['path'])}</a></td></tr>"
        for asset in assets
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    body {{ margin: 0; font-family: Arial, sans-serif; color: #172033; background: #f7f8fa; }}
    header {{ background: #ffffff; border-bottom: 1px solid #d9dee7; padding: 28px; }}
    main {{ max-width: 1080px; margin: 0 auto; padding: 24px; }}
    table {{ width: 100%; border-collapse: collapse; background: #ffffff; border: 1px solid #d9dee7; }}
    th, td {{ padding: 12px; border-bottom: 1px solid #e6e9ef; text-align: left; vertical-align: top; }}
    th {{ background: #eef2f7; }}
    code {{ background: #eef2f7; padding: 2px 5px; border-radius: 4px; }}
  </style>
</head>
<body>
  <header>
    <h1>{html.escape(title)}</h1>
    <p>Open these assets during a client conversation. Keep production actions behind human approval.</p>
  </header>
  <main>
    <table>
      <thead><tr><th>Asset</th><th>Type</th><th>Path</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </main>
</body>
</html>
"""


def _markdown_shell_html(title: str, markdown: str) -> str:
    escaped = html.escape(markdown)
    return f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{html.escape(title)}</title></head>
<body><pre>{escaped}</pre></body>
</html>
"""


def _parse_connector_list(connectors: str) -> list[str]:
    values = [item.strip().lower() for item in connectors.split(",") if item.strip()]
    return values or ["local-folder"]


def _guided_setup_questions(flow: dict, deployment: str, connectors: list[str]) -> list[dict]:
    base_questions = [
        {
            "id": "business_goal",
            "label": "What business result should this automation improve?",
            "plain_language": "Example: reduce missed LINE inquiries, reply faster, or prepare daily reports.",
            "required": True,
        },
        {
            "id": "reception_source",
            "label": "Where does the work arrive today?",
            "plain_language": "Choose the reception source: LINE, Gmail, web form, Google Sheets, CSV folder, or another inbox.",
            "required": True,
        },
        {
            "id": "knowledge_source",
            "label": "What should the AI use as approved reference information?",
            "plain_language": "Examples: FAQ, price list, service menu, policy docs, booking rules, or past approved replies.",
            "required": True,
        },
        {
            "id": "output_destination",
            "label": "Where should outputs go?",
            "plain_language": "Examples: local folder, email drafts, Google Sheets, Slack notification, or operator UI.",
            "required": True,
        },
        {
            "id": "human_approval_rules",
            "label": "Which cases must stop for human approval?",
            "plain_language": "Examples: complaints, refunds, contracts, legal/medical/financial topics, price changes, or booking confirmation.",
            "required": True,
        },
        {
            "id": "deployment_target",
            "label": "Where should the automation run?",
            "plain_language": "Choose local PC, Render/Railway, Google Cloud Run, VPS, or undecided.",
            "required": True,
        },
        {
            "id": "client_data_boundary",
            "label": "What client data is allowed in the dry-run?",
            "plain_language": "Use sample or masked data first. Do not include passwords, secrets, payment records, or sensitive production exports.",
            "required": True,
        },
        {
            "id": "success_metric",
            "label": "How will you know the PoC worked?",
            "plain_language": f"Good metrics for this flow include: {', '.join(flow['success_metrics'])}.",
            "required": True,
        },
    ]
    if any(connector in {"line", "gmail", "google-sheets", "slack"} for connector in connectors):
        base_questions.append(
            {
                "id": "connector_owner",
                "label": "Who owns each API account or connector?",
                "plain_language": "The client should confirm who owns LINE, Gmail, Google Sheets, Slack, or other accounts before keys are created.",
                "required": True,
            }
        )
    if deployment in {"cloud", "render", "railway", "cloud-run", "vps", "undecided"}:
        base_questions.append(
            {
                "id": "cloud_operator",
                "label": "Who will manage cloud settings and monthly checks?",
                "plain_language": "Pick a named operator for environment variables, logs, billing, uptime checks, and incident response.",
                "required": True,
            }
        )
    return base_questions


def _guided_setup_answer_template(
    flow: dict,
    mode: str,
    deployment: str,
    connectors: list[str],
    questions: list[dict],
) -> dict:
    return {
        "flow_id": flow["id"],
        "mode": mode,
        "deployment": deployment,
        "connectors": connectors,
        "answers": {question["id"]: "" for question in questions},
        "notes": "Fill this file after answering guided_setup_questions.md. Leave unknown values blank and rerun readiness review manually or with an AI agent.",
    }


def _render_guided_setup_start(flow: dict, payload: dict) -> str:
    return "\n".join(
        [
            "# Start Here: Guided Setup",
            "",
            f"Flow: `{flow['id']}` - {flow['name']}",
            f"Mode: `{payload['mode']}`",
            f"Deployment: `{payload['deployment']}`",
            "",
            "This folder is a guided intake package. It does not deploy anything by itself. It tells the operator, client, or AI agent which inputs are required before local or cloud automation can be prepared.",
            "",
            "## Read In This Order",
            "",
            "1. `guided_setup_questions.md`",
            "2. `guided_setup_answers.example.json`",
            "3. `missing_inputs.md`",
            "4. `env_values_needed.md`",
            "5. `local_setup_plan.md` or `cloud_setup_plan.md`",
            "6. `client_request_list.md`",
            "7. `ai_agent_instruction.md`",
            "8. `next_action.md`",
            "",
            "Use an AI agent such as Codex, Claude Code, or Cursor to ask these questions one at a time and write the answers into a real `guided_setup_answers.json` file.",
            "",
        ]
    )


def _render_guided_setup_questions(flow: dict, questions: list[dict], mode: str) -> str:
    lines = [
        f"# Guided Setup Questions: {flow['name']}",
        "",
        "These questions collect the minimum inputs needed before local or cloud automation setup.",
        "",
        f"Mode: `{mode}`",
        "",
    ]
    for index, question in enumerate(questions, start=1):
        lines.extend(
            [
                f"## {index}. {question['label']}",
                "",
                f"- ID: `{question['id']}`",
                f"- Required: `{str(question['required']).lower()}`",
                f"- Beginner explanation: {question['plain_language']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Required Keywords",
            "",
            "This guide must identify the reception source, knowledge source, output destination, human approval rules, deployment target, and success metric before production planning.",
            "",
        ]
    )
    return "\n".join(lines)


def _render_missing_inputs(flow: dict, questions: list[dict]) -> str:
    lines = [
        f"# Missing Inputs: {flow['name']}",
        "",
        "The following required inputs are still missing until the operator or AI agent fills `guided_setup_answers.json`.",
        "",
    ]
    lines.extend(f"- `{question['id']}`: {question['label']}" for question in questions if question["required"])
    lines.extend(
        [
            "",
            "Do not create real credentials, webhooks, or production sends until these inputs are answered and reviewed.",
            "",
        ]
    )
    return "\n".join(lines)


def _render_local_setup_plan(flow: dict, connectors: list[str]) -> str:
    return "\n".join(
        [
            f"# Local Setup Plan: {flow['name']}",
            "",
            "Use this when the operator wants to run the first proof locally.",
            "",
            "1. Install the selected flow with `ai-automation-kit flows install`.",
            "2. Put sample or masked input data in `sample_data/input.csv`.",
            "3. Keep connectors in dry-run mode.",
            "4. Run `python3 scripts/run_automation.py`.",
            "5. Review `automation_output/approval_queue.csv`.",
            "6. Open `operator_ui/index.html` for the client explanation.",
            "",
            f"Requested connectors: {', '.join(connectors)}",
            "",
        ]
    )


def _render_cloud_setup_plan(flow: dict, deployment: str, connectors: list[str]) -> str:
    recommendation = "Render or Railway for first PoC" if deployment in {"cloud", "undecided", "render", "railway"} else deployment
    if "google-sheets" in connectors or "gmail" in connectors:
        recommendation += "; consider Google Cloud Run when Google OAuth and Sheets are central"
    return "\n".join(
        [
            f"# Cloud Setup Plan: {flow['name']}",
            "",
            f"Recommended first cloud path: {recommendation}.",
            "",
            "Cloud setup should happen only after the dry-run answers are complete.",
            "",
            "## Minimum Cloud Requirements",
            "",
            "- GitHub repository access.",
            "- Cloud account owner.",
            "- Environment variables configured outside GitHub.",
            "- HTTPS endpoint for webhooks.",
            "- Logs that do not expose secrets or unnecessary personal data.",
            "- Human approval before real external sends.",
            "- Monthly billing and operations owner.",
            "",
            f"Requested connectors: {', '.join(connectors)}",
            "",
        ]
    )


def _render_env_values_needed(connectors: list[str], deployment: str) -> str:
    env_rows = [
        ("APPROVER_EMAIL", "Named person who reviews AI drafts before real action."),
        ("FLOW_MODE", "Use `dry-run` until go-live is approved."),
    ]
    if "line" in connectors:
        env_rows.extend(
            [
                ("LINE_CHANNEL_SECRET", "Verifies that LINE webhook events are from the correct LINE account."),
                ("LINE_CHANNEL_ACCESS_TOKEN", "Allows approved LINE actions after production approval."),
            ]
        )
    if "gmail" in connectors:
        env_rows.extend(
            [
                ("GMAIL_CLIENT_ID", "Google OAuth application ID for Gmail access."),
                ("GMAIL_CLIENT_SECRET", "Google OAuth secret. Do not commit it to GitHub."),
            ]
        )
    if "google-sheets" in connectors:
        env_rows.append(("GOOGLE_SHEETS_CREDENTIALS_JSON", "Service account or OAuth credentials for spreadsheet access."))
    if "slack" in connectors:
        env_rows.append(("SLACK_WEBHOOK_URL", "Webhook URL for approved internal notifications."))
    if deployment != "local":
        env_rows.append(("PUBLIC_BASE_URL", "Cloud HTTPS URL used by webhooks."))
    lines = ["# Environment Values Needed", "", "| Name | Plain-language meaning |", "|---|---|"]
    lines.extend(f"| `{name}` | {meaning} |" for name, meaning in env_rows)
    lines.append("")
    return "\n".join(lines)


def _render_client_request_list(flow: dict, connectors: list[str]) -> str:
    return "\n".join(
        [
            f"# Client Request List: {flow['name']}",
            "",
            "Ask the client for these items before setup.",
            "",
            "- One sample input export with private data removed.",
            "- FAQ, price list, policy, service menu, or approved reply examples.",
            "- Name and email of the approval owner.",
            "- Clear list of cases that must stop for human approval.",
            "- Decision on local dry-run first, then cloud setup later.",
            f"- Connector account owners for: {', '.join(connectors)}.",
            "- Confirmation that API keys and secrets will not be shared in chat or committed to GitHub.",
            "",
        ]
    )


def _render_ai_agent_instruction(flow: dict, mode: str) -> str:
    detail_rule = "Explain terms in plain language before asking for values." if mode == "beginner" else "Keep explanations short and focus on required fields."
    return "\n".join(
        [
            f"# AI Agent Instruction: {flow['name']}",
            "",
            "Ask the user one question at a time using `guided_setup_questions.md`.",
            "",
            f"- Mode: `{mode}`",
            f"- Instruction style: {detail_rule}",
            "- Write final answers into `guided_setup_answers.json`.",
            "- If the user does not know an answer, leave it blank and list it in `missing_inputs.md`.",
            "- Do not ask for raw secrets in chat.",
            "- Explain API keys, OAuth, webhooks, folders, and deployment target in plain language when needed.",
            "- Keep production sends blocked until human approval and go-live conditions are complete.",
            "",
        ]
    )


def _guided_readiness_score(payload: dict) -> dict:
    missing_count = len(payload["missing_required_inputs"])
    score = max(0, 100 - missing_count * 10)
    return {
        "status": "needs_input" if missing_count else "ready_for_dry_run",
        "score": score,
        "missing_required_inputs": payload["missing_required_inputs"],
        "deployment": payload["deployment"],
        "mode": payload["mode"],
    }


def _render_guided_next_action(flow: dict, mode: str, deployment: str) -> str:
    return "\n".join(
        [
            f"# Next Action: {flow['name']}",
            "",
            "1. Open `guided_setup_questions.md`.",
            "2. Ask an AI agent to question the operator one item at a time.",
            "3. Save answers as `guided_setup_answers.json`.",
            "4. Review `missing_inputs.md`.",
            "5. If local, install the flow and run a dry-run.",
            "6. If cloud, complete `cloud_setup_plan.md` and `env_values_needed.md` before creating real credentials.",
            "",
            f"Current mode: `{mode}`",
            f"Current deployment preference: `{deployment}`",
            "",
        ]
    )


def _guided_review_next_step(status: str, local_ready: bool, deployment: str) -> str:
    if status == "needs_client_input" and local_ready:
        return "Run a local dry-run with masked sample data, then collect the missing cloud owner or deployment inputs."
    if status == "needs_client_input":
        return "Collect missing client inputs before building the automation folder."
    if status == "ready_for_cloud_planning":
        return f"Prepare {deployment} environment variables, logs, rollback, and billing ownership after local dry-run approval."
    return "Install the flow, run local dry-run, review approval queue, then decide whether cloud deployment is needed."


def _cloud_provider_profile(provider: str) -> dict:
    profiles = {
        "google-cloud": {
            "name": "Google Cloud",
            "services": ["Cloud Run", "Cloud Scheduler", "Cloud Tasks", "Secret Manager", "Cloud Logging"],
            "best_for": "Containerized webhook APIs, Google Sheets/Gmail-heavy workflows, and teams already using Google Cloud.",
            "beginner_fit": "medium",
            "human_steps_required": ["Google account login", "billing setup", "project selection", "service account approval"],
        },
        "aws": {
            "name": "AWS",
            "services": ["Lambda", "API Gateway", "EventBridge", "SQS", "Secrets Manager", "CloudWatch Logs"],
            "best_for": "Serverless webhook APIs, enterprise AWS accounts, and low-idle-cost event processing.",
            "beginner_fit": "medium",
            "human_steps_required": ["AWS account login", "region selection", "IAM approval", "budget alert approval"],
        },
        "azure": {
            "name": "Azure",
            "services": ["Container Apps", "Functions", "Storage Queue", "Key Vault", "Azure Monitor"],
            "best_for": "Microsoft 365, Teams, SharePoint, Entra ID, and enterprise Azure environments.",
            "beginner_fit": "medium",
            "human_steps_required": ["Azure login", "subscription selection", "resource group approval", "managed identity approval"],
        },
        "render": {
            "name": "Render Web Service",
            "services": ["Web Service", "Cron Job", "Background Worker", "Environment Variables", "Logs"],
            "best_for": "Fast beginner PoC, demo webhook, and small paid pilot before enterprise cloud migration.",
            "beginner_fit": "high",
            "human_steps_required": ["Render login", "repo connection", "environment variable entry", "paid plan review"],
        },
        "railway": {
            "name": "Railway Service",
            "services": ["Service", "Cron", "Variables", "Logs"],
            "best_for": "Fast prototype deployment with simple variable management and low setup friction.",
            "beginner_fit": "high",
            "human_steps_required": ["Railway login", "project creation", "environment variable entry", "usage limit review"],
        },
        "vercel": {
            "name": "Vercel Functions",
            "services": ["Functions", "Cron Jobs", "Environment Variables", "Logs"],
            "best_for": "Web UI, intake forms, and lightweight API routes attached to a customer-facing app.",
            "beginner_fit": "high",
            "human_steps_required": ["Vercel login", "project import", "environment variable entry", "function limit review"],
        },
        "digitalocean": {
            "name": "DigitalOcean App Platform",
            "services": ["App Platform", "Functions", "Jobs", "Environment Variables", "Logs"],
            "best_for": "Small business apps, predictable PaaS deployment, and GitHub-connected low-friction hosting.",
            "beginner_fit": "medium",
            "human_steps_required": ["DigitalOcean login", "app creation", "environment variable entry", "billing alert review"],
        },
        "fly": {
            "name": "Fly.io Machines",
            "services": ["Machines", "Fly Secrets", "fly logs"],
            "best_for": "Docker-first developers who want edge placement and a simple `fly deploy` workflow.",
            "beginner_fit": "medium",
            "human_steps_required": ["Fly.io login", "app launch", "secret entry", "region and billing review"],
        },
    }
    return profiles[provider]


def _cloud_workload_profile(provider: str, workload: str) -> dict:
    provider_runtime = {
        "google-cloud": {
            "webhook-api": "Cloud Run HTTPS service",
            "scheduled-job": "Cloud Scheduler -> Cloud Run Job",
            "worker-queue": "Cloud Tasks or Pub/Sub -> Cloud Run worker",
            "web-app": "Cloud Run web app",
            "static-functions": "Cloud Run or Firebase Hosting + Functions",
            "container-service": "Cloud Run container service",
        },
        "aws": {
            "webhook-api": "API Gateway -> Lambda",
            "scheduled-job": "EventBridge Scheduler -> Lambda",
            "worker-queue": "SQS -> Lambda worker",
            "web-app": "App Runner or ECS Fargate",
            "static-functions": "CloudFront/S3 -> Lambda",
            "container-service": "ECS Fargate",
        },
        "azure": {
            "webhook-api": "Azure Functions HTTP trigger or Container Apps",
            "scheduled-job": "Timer Trigger Function or Container Apps Job",
            "worker-queue": "Storage Queue -> Function or Container Apps worker",
            "web-app": "Azure Container Apps",
            "static-functions": "Static Web Apps + Functions",
            "container-service": "Azure Container Apps",
        },
        "render": {
            "webhook-api": "Render Web Service",
            "scheduled-job": "Render Cron Job",
            "worker-queue": "Render Background Worker",
            "web-app": "Render Web Service",
            "static-functions": "Render Static Site plus API service",
            "container-service": "Render Web Service from Docker",
        },
        "railway": {
            "webhook-api": "Railway Service",
            "scheduled-job": "Railway Cron",
            "worker-queue": "Railway Worker Service",
            "web-app": "Railway Service",
            "static-functions": "Railway web app plus API service",
            "container-service": "Railway Docker Service",
        },
        "vercel": {
            "webhook-api": "Vercel Function / API Route",
            "scheduled-job": "Vercel Cron Job",
            "worker-queue": "Vercel Cron + external queue",
            "web-app": "Vercel web app",
            "static-functions": "Vercel static site + Functions",
            "container-service": "Use another provider for long-running containers",
        },
        "digitalocean": {
            "webhook-api": "App Platform service",
            "scheduled-job": "App Platform job or scheduled function",
            "worker-queue": "Worker component",
            "web-app": "App Platform web app",
            "static-functions": "Static site + Functions",
            "container-service": "App Platform container",
        },
        "fly": {
            "webhook-api": "Fly Machine HTTPS app",
            "scheduled-job": "Fly Machine scheduled process",
            "worker-queue": "Fly worker process",
            "web-app": "Fly Machine web app",
            "static-functions": "Static assets served by app plus handlers",
            "container-service": "Fly Machine container",
        },
    }[provider][workload]
    names = {
        "webhook-api": "Webhook/API endpoint",
        "scheduled-job": "Scheduled job",
        "worker-queue": "Worker/queue processor",
        "web-app": "Web app with operator UI",
        "static-functions": "Static site plus functions",
        "container-service": "Container service",
    }
    network = "Public HTTPS endpoint" if workload in {"webhook-api", "web-app", "static-functions", "container-service"} else "Private or scheduler-triggered runtime"
    return {
        "name": names[workload],
        "runtime": provider_runtime,
        "network": network,
        "architecture": f"Input source -> {provider_runtime} -> Secrets manager/env vars -> Logs/metrics -> Human approval queue",
    }


def _cloud_required_env_values(flow: dict, connectors: list[str], workload: str) -> list[str]:
    values = ["APPROVER_EMAIL", "FLOW_MODE"]
    if workload in {"webhook-api", "web-app", "static-functions", "container-service"}:
        values.append("PUBLIC_BASE_URL")
    connector_values = {
        "line": ["LINE_CHANNEL_SECRET", "LINE_CHANNEL_ACCESS_TOKEN"],
        "gmail": ["GMAIL_CLIENT_ID", "GMAIL_CLIENT_SECRET", "GMAIL_REFRESH_TOKEN"],
        "google-sheets": ["GOOGLE_SHEETS_SPREADSHEET_ID", "GOOGLE_SERVICE_ACCOUNT_JSON"],
        "slack": ["SLACK_BOT_TOKEN", "SLACK_SIGNING_SECRET"],
        "teams": ["TEAMS_WEBHOOK_URL"],
        "webhook": ["INBOUND_WEBHOOK_SECRET"],
        "crm": ["CRM_BASE_URL", "CRM_API_TOKEN"],
        "storage-folder": ["INPUT_FOLDER_PATH", "OUTPUT_FOLDER_PATH"],
        "local-folder": ["INPUT_FOLDER_PATH", "OUTPUT_FOLDER_PATH"],
        "email": ["SMTP_HOST", "SMTP_USERNAME", "SMTP_PASSWORD"],
    }
    for connector in connectors:
        values.extend(connector_values.get(connector, [f"{connector.upper().replace('-', '_')}_CONFIG"]))
    return list(dict.fromkeys(values))


def _cloud_human_steps(profile: dict, workload_profile: dict, connectors: list[str]) -> list[str]:
    steps = list(profile["human_steps_required"])
    steps.extend(
        [
            f"Approve workload shape: {workload_profile['name']}",
            "Approve environment variables before deployment",
            "Approve logging and retention policy",
            "Approve rollback owner before production traffic",
        ]
    )
    if "line" in connectors:
        steps.append("Paste deployed webhook URL into LINE Developers after review")
    if "gmail" in connectors or "google-sheets" in connectors:
        steps.append("Approve Google OAuth or service account access outside chat")
    if "slack" in connectors or "teams" in connectors:
        steps.append("Approve chat workspace app or webhook installation")
    return list(dict.fromkeys(steps))


def _render_cloud_plan_start(flow: dict, payload: dict) -> str:
    return "\n".join(
        [
            "# Start Here: Cloud Plan",
            "",
            f"Flow: `{flow['id']}` - {flow['name']}",
            f"Provider: `{payload['provider']}` - {payload['provider_name']}",
            f"Workload: `{payload['workload']}` - {payload['workload_name']}",
            f"Connectors: `{', '.join(payload['connectors'])}`",
            "",
            "This folder does not create real cloud resources by itself. It creates the architecture, runtime choice, commands, secret plan, network notes, operations runbook, cost guardrails, compliance boundary, and rollback plan needed before a human approves deployment.",
            "",
            "## Read In This Order",
            "",
            "1. `cloud_provider_matrix.md`",
            "2. `workload_architecture.md`",
            "3. `runtime_choice.md`",
            "4. `secrets_and_env.md`",
            "5. `network_and_domain.md`",
            "6. `deploy_runbook.md`",
            "7. `operations_runbook.md`",
            "8. `cost_guardrails.md`",
            "9. `compliance_data_boundary.md`",
            "10. `incident_rollback.md`",
            "11. `human_approval_required.md`",
            "",
        ]
    )


def _render_cloud_provider_matrix(payload: dict) -> str:
    services = ", ".join(payload["provider_services"])
    return "\n".join(
        [
            f"# Cloud Provider Matrix: {payload['provider_name']}",
            "",
            f"| Item | Choice |",
            "|---|---|",
            f"| Provider | `{payload['provider']}` |",
            f"| Workload | `{payload['workload']}` - {payload['workload_name']} |",
            f"| Runtime | {payload['runtime']} |",
            f"| Services to review | {services} |",
            f"| Beginner fit | `{payload['beginner_fit']}` |",
            "",
            "Use this file to explain why this provider/runtime was selected before anyone touches the cloud console.",
            "",
        ]
    )


def _render_cloud_architecture(flow: dict, payload: dict) -> str:
    return "\n".join(
        [
            f"# Workload Architecture: {payload['provider_name']}",
            "",
            f"Flow: `{flow['id']}`",
            f"Workload: `{payload['workload']}` - {payload['workload_name']}",
            "",
            f"Architecture: {payload['architecture']}",
            "",
            f"Runtime: {payload['runtime']}",
            f"Network: {payload['network']}",
            f"Provider services: {', '.join(payload['provider_services'])}",
            f"Best for: {payload['best_for']}",
            f"Beginner fit: `{payload['beginner_fit']}`",
            "",
            "## Boundary",
            "",
            "AI can generate files, commands, and checks. A human still needs to log in, approve billing, create or select accounts, enter secrets into the provider UI or CLI, approve domains and DNS, and enable real production traffic.",
            "",
        ]
    )


def _render_cloud_runtime_choice(payload: dict) -> str:
    return "\n".join(
        [
            f"# Runtime Choice: {payload['workload_name']}",
            "",
            f"Selected runtime: {payload['runtime']}",
            "",
            "## Why This Shape",
            "",
            f"- Matches workload type `{payload['workload']}`.",
            f"- Keeps secrets in {payload['provider_name']} secret/env systems.",
            "- Keeps logs visible before any production traffic is enabled.",
            "- Allows a human approval queue before irreversible actions.",
            "",
            "## When To Change It",
            "",
            "- Use `webhook-api` for inbound HTTP events such as LINE, Slack, forms, or external systems.",
            "- Use `scheduled-job` for daily reports, invoice follow-ups, reminders, and batch checks.",
            "- Use `worker-queue` when retries and backlog processing matter.",
            "- Use `web-app` when the operator needs a browser UI.",
            "- Use `static-functions` for lightweight pages with small API handlers.",
            "- Use `container-service` when the automation needs a long-running service or custom runtime.",
            "",
        ]
    )


def _render_cloud_cost_note(payload: dict) -> str:
    return "\n".join(
        [
            f"# Cloud Cost Note: {payload['provider_name']}",
            "",
            "Costs depend on account plan, region, traffic, memory, logs, build minutes, and outbound network usage.",
            "",
            "## Beginner Rule",
            "",
            "- Start with local dry-run.",
            "- Deploy a small cloud PoC only after the client approves the sample workflow.",
            "- Set a billing owner before any production webhook is enabled.",
            "- Add a low budget alert or usage cap when the provider supports it.",
            "- Prefer scheduled or serverless shapes for low-volume automation.",
            "- Review logs and billing after the first test day.",
            "",
        ]
    )


def _render_cloud_secret_setup(payload: dict) -> str:
    lines = [
        f"# Secrets And Environment: {payload['provider_name']}",
        "",
        "Do not paste real secrets into chat and do not commit them to GitHub.",
        "",
        "## Required Values",
        "",
    ]
    lines.extend(f"- `{name}`" for name in payload["env_values"])
    lines.extend(["", "## Provider Notes", ""])
    if payload["provider"] == "google-cloud":
        lines.extend(
            [
                "Use Google Secret Manager for production secrets.",
                "Use `gcloud secrets create` and `gcloud secrets versions add` after human login.",
            ]
        )
    elif payload["provider"] == "aws":
        lines.extend(
            [
                "Use AWS Secrets Manager for production secrets.",
                "Use `aws secretsmanager create-secret` after human login and region selection.",
            ]
        )
    elif payload["provider"] == "azure":
        lines.extend(["Use Azure Key Vault secrets or Container Apps secrets after subscription approval."])
    elif payload["provider"] == "fly":
        lines.extend(["Use `fly secrets set` for runtime secrets."])
    else:
        lines.extend(["Use the provider dashboard environment variable or secrets screen."])
    lines.append("")
    return "\n".join(lines)


def _render_cloud_iam_setup(payload: dict) -> str:
    return "\n".join(
        [
            f"# IAM Setup: {payload['provider_name']}",
            "",
            "Use the minimum role needed for deployment and logs. Do not reuse personal owner/admin credentials for client production work.",
            "",
            "## Human Approval Required",
            "",
            "\n".join(f"- {item}" for item in payload["human_steps_required"]),
            "",
            "## Minimum Access Pattern",
            "",
            "- Deploy service or function.",
            "- Read configured secrets at runtime.",
            "- Write application logs.",
            "- Roll back to the previous revision or disable the webhook.",
            "",
        ]
    )


def _render_cloud_network_and_domain(payload: dict) -> str:
    webhook_notes = []
    if payload["workload"] in {"webhook-api", "web-app", "static-functions", "container-service"}:
        webhook_notes.extend(
            [
                "- Confirm the generated HTTPS URL.",
                "- Decide whether a custom domain is needed for client trust.",
                "- Configure DNS only after the owner approves the domain.",
                "- For connector webhooks, paste the final URL in the external service only after smoke tests pass.",
            ]
        )
    else:
        webhook_notes.extend(
            [
                "- No public inbound endpoint is required for this workload by default.",
                "- Keep scheduler and queue access private where the provider supports it.",
                "- Use a public URL only for health checks or operator dashboards that need it.",
            ]
        )
    return "\n".join([f"# Network And Domain: {payload['provider_name']}", "", *webhook_notes, ""])


def _render_cloud_deploy_commands(flow: dict, payload: dict) -> str:
    app = flow["id"].replace("_", "-")
    provider = payload["provider"]
    workload = payload["workload"]
    if provider == "aws" and workload == "scheduled-job":
        commands = [
            "aws configure sso",
            f"aws lambda create-function --function-name {app} --runtime python3.11 --handler main.handler --role YOUR_LAMBDA_ROLE_ARN --zip-file fileb://function.zip",
            f"aws events put-rule --name {app}-schedule --schedule-expression 'rate(1 day)'",
            f"aws events put-targets --rule {app}-schedule --targets Id=1,Arn=YOUR_LAMBDA_ARN",
        ]
    else:
        commands = _cloud_default_deploy_commands(provider, app, payload)
    lines = [f"# Deploy Runbook: {payload['provider_name']}", "", "Review before running. Replace placeholders first.", "", "```bash"]
    lines.extend(commands)
    lines.extend(["```", ""])
    return "\n".join(lines)


def _cloud_default_deploy_commands(provider: str, app: str, payload: dict) -> list[str]:
    return {
        "google-cloud": [
            "gcloud auth login",
            "gcloud config set project YOUR_PROJECT_ID",
            f"gcloud run deploy {app} --source . --region asia-northeast1 --allow-unauthenticated",
        ],
        "aws": [
            "aws configure sso",
            f"aws lambda create-function --function-name {app} --runtime python3.11 --handler main.handler --role YOUR_LAMBDA_ROLE_ARN --zip-file fileb://function.zip",
            f"aws apigatewayv2 create-api --name {app}-api --protocol-type HTTP",
        ],
        "azure": [
            "az login",
            "az group create --name ai-automation-rg --location japaneast",
            f"az containerapp up --name {app} --resource-group ai-automation-rg --location japaneast --source .",
        ],
        "render": [
            "Connect this repository in the Render dashboard.",
            "Create the service type shown in `runtime_choice.md` and set the environment variables from `secrets_and_env.md`.",
            "Deploy, then copy the service URL if the workload requires public HTTPS.",
        ],
        "railway": [
            "railway login",
            "railway init",
            "railway up",
        ],
        "vercel": [
            "vercel login",
            "vercel env add APPROVER_EMAIL",
            "vercel deploy",
        ],
        "digitalocean": [
            "doctl auth init",
            "Create an App Platform app from the repository or container image.",
            "Set environment variables in App Platform before enabling traffic.",
        ],
        "fly": [
            "fly auth login",
            f"fly launch --name {app} --no-deploy",
            "fly secrets set APPROVER_EMAIL=replace_me FLOW_MODE=dry-run",
            "fly deploy",
        ],
    }[provider]


def _render_cloud_webhook_setup(flow: dict, payload: dict) -> str:
    lines = [
        f"# Webhook Setup: {flow['name']}",
        "",
        "Use this only when the workload or connector needs inbound HTTPS.",
        "",
        "Example:",
        "",
        "```text",
        "https://YOUR_PUBLIC_HOST/webhook",
        "```",
        "",
        "Human steps:",
        "",
        "1. Confirm the deployed HTTPS URL.",
        "2. Confirm the connector owner has approved webhook activation.",
        "3. Paste the URL into the external service dashboard.",
        "4. Send one test event only after `operations_runbook.md` is reviewed.",
    ]
    if "line" in payload["connectors"]:
        lines.append("5. For LINE, paste the URL in LINE Developers after the client approves the channel.")
    lines.append("")
    return "\n".join(lines)


def _render_cloud_compliance_data_boundary(flow: dict, payload: dict) -> str:
    return "\n".join(
        [
            f"# Compliance Data Boundary: {flow['name']}",
            "",
            "Before cloud deployment, decide what data is allowed to leave the local machine or client system.",
            "",
            "## Required Decisions",
            "",
            "- Which sample data can be used in dry-run.",
            "- Which production data categories are excluded.",
            "- Who can view cloud logs.",
            "- How long logs are retained.",
            "- Whether personal, financial, medical, legal, or client-confidential data appears in prompts, logs, queues, or exports.",
            "",
            "## Connector Boundary",
            "",
            "\n".join(f"- `{connector}`: confirm owner, access scope, and revocation path." for connector in payload["connectors"]),
            "",
        ]
    )


def _render_cloud_post_deploy_test(payload: dict) -> str:
    return "\n".join(
        [
            f"# Operations Runbook: {payload['provider_name']}",
            "",
            "- Confirm the service has a public HTTPS URL.",
            "- Confirm secrets are set in the provider, not in GitHub.",
            "- Confirm logs are visible.",
            "- Send one test event, webhook, scheduled run, or queue item based on the selected workload.",
            "- Confirm the response is dry-run or approval-gated.",
            "- Stop if errors, unexpected sends, or missing logs appear.",
            "",
        ]
    )


def _render_cloud_rollback_plan(payload: dict) -> str:
    return "\n".join(
        [
            f"# Incident Rollback: {payload['provider_name']}",
            "",
            "1. Disable public traffic, scheduled trigger, or queue consumer first.",
            "2. Roll back to the previous cloud revision or stop the service.",
            "3. Rotate any exposed secrets.",
            "4. Export logs for review.",
            "5. Notify the client that production traffic is stopped.",
            "",
        ]
    )


def _render_cloud_human_approval(payload: dict) -> str:
    lines = [
        "# Human Approval Required",
        "",
        "The AI can prepare the plan, but these items require a human owner.",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["human_steps_required"])
    lines.extend(
        [
            "- Enter real secrets only in the approved cloud secrets manager or provider dashboard.",
            "- Approve billing before public deployment.",
            "- Approve webhook, scheduler, queue, domain, or public traffic activation before real production use.",
            "- Confirm rollback owner before production use.",
            "",
        ]
    )
    return "\n".join(lines)


def _grill_me_questions(flow: dict, deployment: str, connectors: list[str]) -> list[tuple[str, str]]:
    questions = [
        ("business_pain", "What business pain are we trying to reduce, and how does the client feel it today?"),
        ("current_process", "What is the current manual process from input to output?"),
        ("sample_data", "What sample data can be used for a no-send dry-run?"),
        ("output_review", "Who reviews the AI output before it reaches a customer or production system?"),
        ("success_metric", "What number proves the PoC helped: time saved, missed work reduced, faster replies, or fewer errors?"),
        ("human_approval", "Where must human approval remain before production use?"),
        ("risk_boundary", "What must the automation never do automatically?"),
        ("client_owner", "Who owns the client account, data source, connector, and final approval?"),
    ]
    if deployment != "local":
        questions.extend(
            [
                ("cloud_reason", "Why is cloud deployment needed now instead of staying in local dry-run?"),
                ("billing_owner", "Who approves cloud billing, budget alerts, logs, and rollback ownership?"),
            ]
        )
    if connectors:
        questions.append(("connector_scope", f"What access is needed for these connectors: {', '.join(connectors)}?"))
    if "line" in connectors or "slack" in connectors or "gmail" in connectors:
        questions.append(("send_boundary", "Are messages sent automatically, drafted only, or held in an approval queue?"))
    return questions


def _render_grill_me_start(flow: dict, payload: dict) -> str:
    return "\n".join(
        [
            "# Start Here: Grill Me Review",
            "",
            f"Flow: `{flow['id']}` - {flow['name']}",
            f"Mode: `{payload['mode']}`",
            f"Client type: `{payload['client_type']}`",
            f"Deployment target: `{payload['deployment']}`",
            f"Connectors: `{', '.join(payload['connectors'])}`",
            "",
            "Use this folder when the operator is new to AI and does not know what to ask next.",
            "",
            "The operating rule is simple: ask one question at a time, wait for the answer, challenge vague answers, and stop before secrets, production traffic, or unsafe promises enter the workflow.",
            "",
            "## Read In This Order",
            "",
            "1. `ai_agent_prompt.md`",
            "2. `questions_to_answer.md`",
            "3. `client_interview_grill.md`",
            "4. `risk_grill.md`",
            "5. `cloud_readiness_grill.md`",
            "6. `proposal_grill.md`",
            "",
            "## Success",
            "",
            "Success is not a perfect answer on the first try. Success is a safer, clearer automation proposal after repeated questions.",
            "",
        ]
    )


def _render_grill_me_questions(flow: dict, payload: dict) -> str:
    lines = [
        f"# Questions To Answer: {flow['name']}",
        "",
        "Answer these with an AI agent. The AI should ask one question at a time and should not move forward when the answer is vague.",
        "",
    ]
    for index, (question_id, question) in enumerate(_grill_me_questions(flow, payload["deployment"], payload["connectors"]), start=1):
        lines.extend([f"## {index}. `{question_id}`", "", question, "", "Good answer should include:", "", "- A concrete owner.", "- A concrete data source or business event.", "- A clear human approval point.", ""])
    return "\n".join(lines)


def _render_client_interview_grill(flow: dict, payload: dict) -> str:
    return "\n".join(
        [
            f"# Client Interview Grill: {flow['name']}",
            "",
            "Use this when talking to a client or preparing a discovery call.",
            "",
            "## Ask One Question At A Time",
            "",
            "1. What work is currently repetitive, delayed, or often missed?",
            "2. Who does the work today?",
            "3. What input starts the work?",
            "4. What output should exist at the end?",
            "5. Who checks the output?",
            "6. What should never be sent, updated, or promised automatically?",
            "7. What sample data can be used without exposing sensitive production information?",
            "8. What would make this PoC worth paying for?",
            "",
            "## Stop Conditions",
            "",
            "- The client cannot name the workflow owner.",
            "- The client wants production automation before dry-run evidence.",
            "- The client asks to paste real secrets into chat.",
            "- The client cannot define success or approval rules.",
            "",
        ]
    )


def _render_cloud_readiness_grill(flow: dict, payload: dict) -> str:
    connectors = ", ".join(payload["connectors"])
    return "\n".join(
        [
            f"# Cloud Readiness Grill: {flow['name']}",
            "",
            f"Deployment target: `{payload['deployment']}`",
            f"Connectors: `{connectors}`",
            "",
            "Cloud is justified only after local dry-run value is visible.",
            "",
            "## Questions",
            "",
            "1. What exactly failed or became inconvenient in local dry-run?",
            "2. Is the workload a webhook/API, scheduled job, worker queue, web app, static functions app, or container service?",
            "3. Who owns the cloud account?",
            "4. Who approves billing and budget alerts?",
            "5. Where will secrets be stored?",
            "6. Where will logs be reviewed?",
            "7. What turns production traffic on?",
            "8. What turns production traffic off?",
            "",
            "## Required Before Cloud",
            "",
            "- `guided-setup` answers are filled.",
            "- `guided-review` has no blocking missing items.",
            "- `cloud-plan` exists for the selected provider and workload.",
            "- Human approval is recorded before secrets, webhook, scheduler, queue, domain, or public traffic are enabled.",
            "",
        ]
    )


def _render_risk_grill(flow: dict, payload: dict) -> str:
    return "\n".join(
        [
            f"# Risk Grill: {flow['name']}",
            "",
            "This file is for challenging the idea before it becomes a risky automation.",
            "",
            "## Hard Questions",
            "",
            "1. Could the automation send a wrong message to a real customer?",
            "2. Could it update a real system without approval?",
            "3. Could it expose personal, legal, medical, financial, or confidential data?",
            "4. Could the client misunderstand this as guaranteed income or complete automation?",
            "5. Is there a rollback owner?",
            "6. Are logs available without exposing secrets?",
            "7. Is there a manual fallback if the automation stops?",
            "",
            "## Default Safe Position",
            "",
            "- Start with dry-run.",
            "- Keep AI output as draft or work queue.",
            "- Require human approval before sending, posting, updating, or deleting.",
            "- Do not ask for real API keys or secrets in chat.",
            "- Do not promise income, 24-hour unmanned operation, or full replacement of human judgment.",
            "",
        ]
    )


def _render_proposal_grill(flow: dict, payload: dict) -> str:
    return "\n".join(
        [
            f"# Proposal Grill: {flow['name']}",
            "",
            "Use this before sending a proposal to a client.",
            "",
            "## Proposal Must Answer",
            "",
            "1. What workflow is included?",
            "2. What workflow is excluded?",
            "3. What sample data is needed?",
            "4. What output will the client see?",
            "5. Who approves AI output?",
            "6. What is the first paid PoC fee, duration, and stop condition?",
            "7. What happens after the PoC: continue, revise, or stop?",
            "",
            "## Proposal Must Not Say",
            "",
            "- Fully automatic without review.",
            "- Guaranteed revenue.",
            "- Production deployment without client approval.",
            "- Real connector access before scope is approved.",
            "",
        ]
    )


def _render_grill_me_ai_agent_prompt(flow: dict, payload: dict) -> str:
    return "\n".join(
        [
            "# AI Agent Prompt",
            "",
            "Copy this into Claude Code, Codex, Cursor, or another AI agent.",
            "",
            "```text",
            "You are helping me use ai-automation-starter-kit. I am new to AI agents and business automation.",
            "",
            f"Target flow: {flow['id']} - {flow['name']}",
            f"Mode: {payload['mode']}",
            f"Client type: {payload['client_type']}",
            f"Deployment target: {payload['deployment']}",
            f"Connectors: {', '.join(payload['connectors'])}",
            "",
            "Please grill me one question at a time.",
            "Do not give me a long list first.",
            "Ask one question, wait for my answer, then challenge unclear answers.",
            "",
            "Use the project README and docs, especially:",
            "- docs/CLOUD_DEPLOYMENT_GUIDE.md or docs/CLOUD_DEPLOYMENT_GUIDE.ja.md",
            "- docs/CLOUD_BEGINNER_PLAYBOOK.md or docs/CLOUD_BEGINNER_PLAYBOOK.ja.md",
            "- docs/CONNECTOR_SETUP_GUIDE.md or docs/CONNECTOR_SETUP_GUIDE.ja.md",
            "",
            "Do not ask for real API keys or secrets in chat.",
            "Keep production sending, webhook activation, schedulers, queues, and real cloud traffic blocked until human approval is explicit.",
            "If my idea is too vague, risky, or hard to sell as a small PoC, say so directly and ask the next clarifying question.",
            "Help me reach a safe dry-run first, then a bounded paid PoC proposal.",
            "```",
            "",
        ]
    )


_GUIDED_FIELD_LABELS = {
    "business_goal": "business result this automation should improve",
    "reception_source": "where the work arrives today",
    "knowledge_source": "approved reference information for the AI",
    "output_destination": "where drafts, queues, or reports should go",
    "human_approval_rules": "cases that must stop for human approval",
    "deployment_target": "local or cloud running location",
    "client_data_boundary": "safe sample data boundary for dry-run",
    "success_metric": "metric used to judge whether the PoC worked",
    "connector_owner": "owner of each API account or connector",
    "cloud_operator": "person responsible for cloud settings and monthly checks",
}


def _guided_field_label(field: str) -> str:
    return _GUIDED_FIELD_LABELS.get(field, field.replace("_", " "))


def _render_guided_review_start(flow: dict, payload: dict) -> str:
    return "\n".join(
        [
            "# Start Here: Guided Review",
            "",
            f"Flow: `{flow['id']}` - {flow['name']}",
            f"Status: `{payload['status']}`",
            "",
            "This folder reviews a completed `guided_setup_answers.json` file. It tells a beginner operator what can be done now, what must be requested from the client, and which command to run next.",
            "",
            "## Read In This Order",
            "",
            "1. `setup_readiness_report.md`",
            "2. `client_missing_items_email.md`",
            "3. `local_vs_cloud_decision.md`",
            "4. `cloud_provider_decision.md`",
            "5. `automation_build_plan.md`",
            "6. `ai_agent_handoff_prompt.md`",
            "7. `next_commands.md`",
            "",
        ]
    )


def _render_setup_readiness_report(flow: dict, payload: dict, answers: dict) -> str:
    local_line = "Ready now for local dry-run: yes" if payload["local_dry_run_ready"] else "Ready now for local dry-run: no"
    missing = payload["missing_inputs"] or ["none"]
    lines = [
        f"# Setup Readiness Report: {flow['name']}",
        "",
        f"- Status: `{payload['status']}`",
        f"- {local_line}",
        f"- Deployment target: `{payload['deployment']}`",
        f"- Connectors: {', '.join(payload['connectors'])}",
        "",
        "## Missing Inputs",
        "",
    ]
    lines.extend(f"- `{item}`: {_guided_field_label(item)}" for item in missing)
    lines.extend(
        [
            "",
            "## Answer Summary",
            "",
            f"- Business goal: {answers.get('business_goal') or 'missing'}",
            f"- Reception source: {answers.get('reception_source') or 'missing'}",
            f"- Knowledge source: {answers.get('knowledge_source') or 'missing'}",
            f"- Output destination: {answers.get('output_destination') or 'missing'}",
            f"- Human approval rules: {answers.get('human_approval_rules') or 'missing'}",
            f"- Success metric: {answers.get('success_metric') or 'missing'}",
            "",
            "## Human Decision",
            "",
            payload["recommended_next_step"],
            "",
        ]
    )
    return "\n".join(lines)


def _render_automation_build_plan(flow: dict, payload: dict) -> str:
    return "\n".join(
        [
            f"# Automation Build Plan: {flow['name']}",
            "",
            "## Phase 1: Local Proof",
            "",
            "1. Install the selected flow into a fresh project folder.",
            "2. Put masked sample data into `sample_data/input.csv`.",
            "3. Keep `FLOW_MODE=dry-run`.",
            "4. Run the automation locally.",
            "5. Review `automation_output/approval_queue.csv` with the client.",
            "",
            "## Phase 2: Client Approval",
            "",
            "1. Confirm the workflow owner and approval owner.",
            "2. Confirm allowed data and forbidden actions.",
            "3. Confirm the success metric and baseline.",
            "4. Stop if the client cannot provide safe sample data.",
            "",
            "## Phase 3: Cloud Planning",
            "",
            "1. Choose a cloud provider only after local dry-run is approved.",
            "2. Put secrets in the provider's environment settings, not in GitHub.",
            "3. Configure logs, rollback, billing owner, and monthly review.",
            "4. Keep real sends blocked until go-live approval.",
            "",
            f"Current recommended next step: {payload['recommended_next_step']}",
            "",
        ]
    )


def _render_client_missing_items_email(flow: dict, payload: dict) -> str:
    missing = payload["missing_inputs"]
    missing_lines = (
        "\n".join(f"- {_guided_field_label(item)} (`{item}`)" for item in missing)
        if missing
        else "- No required setup items are missing."
    )
    return "\n".join(
        [
            f"# Client Missing Items Email: {flow['name']}",
            "",
            "Subject: Automation setup items needed before the next step",
            "",
            "Hello,",
            "",
            "I reviewed the automation setup answers. We can keep the first proof safe by using masked sample data and dry-run mode.",
            "",
            "The following setup items still need confirmation:",
            "",
            missing_lines,
            "",
            "Please do not send passwords, API secrets, payment data, or private production exports in chat. If credentials are needed later, they should be entered directly into the approved local or cloud environment.",
            "",
            "After these items are confirmed, we can run or continue the local dry-run and review the approval queue before any production action is enabled.",
            "",
        ]
    )


def _render_cloud_provider_decision(payload: dict) -> str:
    connectors = set(payload["connectors"])
    recommendation = "Start local. Use Render or Railway for the first simple cloud proof after approval."
    if "gmail" in connectors or "google-sheets" in connectors:
        recommendation = "Start local. Consider Google Cloud Run when Gmail or Google Sheets OAuth becomes central."
    if payload["deployment"] in {"render", "railway", "cloud-run", "vps"}:
        recommendation = f"Start local. Then use `{payload['deployment']}` only after cloud ownership and secret handling are confirmed."
    return "\n".join(
        [
            "# Cloud Provider Decision",
            "",
            f"Recommendation: {recommendation}",
            "",
            "| Option | Best use | Beginner risk |",
            "|---|---|---|",
            "| Local PC | First dry-run, client demo, sample data review | Low |",
            "| Render / Railway | Simple hosted worker or webhook proof | Medium |",
            "| Google Cloud Run | Google OAuth, Sheets/Gmail-heavy workflows | Medium |",
            "| VPS | Custom network or long-running worker | High |",
            "",
            "Cloud is useful only after the local workflow proves value. For a beginner operator, cloud setup should be treated as a separate paid implementation step with a named owner.",
            "",
        ]
    )


def _render_local_vs_cloud_decision(payload: dict) -> str:
    return "\n".join(
        [
            "# Local vs Cloud Decision",
            "",
            "| Question | Local first | Cloud later |",
            "|---|---|---|",
            "| Is the workflow still being explained to the client? | Yes | No |",
            "| Are sample inputs still being checked? | Yes | No |",
            "| Are API keys or webhooks required? | Not required for dry-run | Required for real integration |",
            "| Does it need to run when the PC is closed? | No | Yes |",
            "| Is there a billing/log owner? | Optional | Required |",
            "",
            f"Current local dry-run readiness: `{payload['local_dry_run_ready']}`",
            f"Current deployment target: `{payload['deployment']}`",
            "",
        ]
    )


def _render_ai_agent_handoff_prompt(flow: dict, payload: dict) -> str:
    missing = ", ".join(payload["missing_inputs"]) if payload["missing_inputs"] else "none"
    return "\n".join(
        [
            "# AI Agent Handoff Prompt",
            "",
            "Copy this prompt into Codex, Claude Code, Cursor, or another coding agent after sharing the project repository and the reviewed answer file.",
            "",
            "```text",
            "Please inspect this GitHub project and the generated guided review folder.",
            f"Flow ID: {flow['id']}",
            f"Current status: {payload['status']}",
            f"Missing inputs: {missing}",
            "Help me proceed step by step. First confirm whether we can run a local dry-run with masked sample data. Then prepare only the files and commands needed for the next safe step. Do not ask me to paste raw API secrets in chat. Keep production sends blocked until human approval, rollback, logging, and go-live checks are complete.",
            "```",
            "",
        ]
    )


def _render_guided_review_next_commands(flow: dict, payload: dict) -> str:
    output_dir = f".tmp/{flow['id']}"
    lines = [
        "# Next Commands",
        "",
        "Run these after reviewing `setup_readiness_report.md`.",
        "",
        "```bash",
        f"ai-automation-kit flows install {flow['id']} --output {output_dir}",
        f"ai-automation-kit flows validate {output_dir}",
    ]
    if payload["local_dry_run_ready"]:
        lines.extend(
            [
                f"ai-automation-kit flows run {output_dir}",
                f"ai-automation-kit connector-doctor --project {output_dir} --output .tmp/{flow['id']}-connector-doctor",
                f"ai-automation-kit client-report --flow-project {output_dir} --output .tmp/{flow['id']}-client-report",
            ]
        )
    else:
        lines.append("# Complete missing inputs before running the automation.")
    lines.extend(["```", ""])
    return "\n".join(lines)


def _website_side_hustle_sources() -> list[dict]:
    return [
        {
            "name": "shadcn/ui",
            "url": "https://github.com/shadcn-ui/ui",
            "license": "MIT",
            "use": "Accessible UI primitives and patterns for React websites",
            "why": "Commercial-friendly component baseline with strong real-world adoption",
            "verify": "Review the project license and generated dependencies before shipping",
        },
        {
            "name": "Astro",
            "url": "https://github.com/withastro/astro",
            "license": "MIT",
            "use": "Fast content-heavy marketing sites and static builds",
            "why": "Good fit for brochure sites that need speed and low hosting cost",
            "verify": "Choose project-local integrations only when needed",
        },
        {
            "name": "Headless UI",
            "url": "https://github.com/tailwindlabs/headlessui",
            "license": "MIT",
            "use": "Accessible menus, dialogs, disclosures, and interactions",
            "why": "Helps beginners avoid brittle custom interaction code",
            "verify": "Use only components needed for the page to keep bundles small",
        },
        {
            "name": "Open Props",
            "url": "https://github.com/argyleink/open-props",
            "license": "MIT",
            "use": "CSS tokens for spacing, shadows, easing, and responsive sizing",
            "why": "Improves visual consistency without a heavy design system dependency",
            "verify": "Copy only the tokens the project actually uses",
        },
        {
            "name": "Lucide",
            "url": "https://github.com/lucide-icons/lucide",
            "license": "ISC",
            "use": "Consistent icon set for navigation and feature cards",
            "why": "Simple commercial use and wide framework coverage",
            "verify": "Keep icon usage restrained and purposeful",
        },
        {
            "name": "WCAG Quick Reference",
            "url": "https://www.w3.org/WAI/WCAG22/quickref/",
            "license": "Public reference",
            "use": "Accessibility checks for contrast, headings, labels, focus, and semantics",
            "why": "Raises quality above pretty mockups toward real client readiness",
            "verify": "Treat screenshots as partial evidence; manual checks still matter",
        },
        {
            "name": "web.dev Accessibility",
            "url": "https://web.dev/accessibility/",
            "license": "Public reference",
            "use": "Practical implementation guidance for forms, layout, and responsive behavior",
            "why": "Beginner-friendly bridge from theory to production fixes",
            "verify": "Pair with browser checks and actual keyboard testing",
        },
        {
            "name": "Google Search SEO Starter Guide",
            "url": "https://developers.google.com/search/docs/fundamentals/seo-starter-guide",
            "license": "Public reference",
            "use": "On-page SEO, titles, links, and content structure",
            "why": "Helps side-hustle sites avoid basic discoverability mistakes",
            "verify": "Do not oversell SEO outcomes or rankings",
        },
        {
            "name": "Schema.org Hotel",
            "url": "https://schema.org/Hotel",
            "license": "Public reference",
            "use": "Structured data vocabulary for hotel websites",
            "why": "Shows how to make hospitality sites more machine-readable",
            "verify": "Use only fields the client can support truthfully",
        },
    ]


def _render_website_side_hustle_start(payload: dict) -> str:
    return "\n".join(
        [
            "# Start Here: Website Side Hustle",
            "",
            "This pack turns AI-assisted website building into a safer client-delivery system.",
            "",
            "## Recommended Order",
            "",
            "1. Read `commercial_use_sources.md` and `originality_and_license_rules.md`.",
            "2. Pick one vertical from `niche_offer_menu.md`.",
            "3. Use `client_kickoff_questions.md` and `client_brief.md` to collect facts before designing.",
            "4. Use `codex_workflow.md` with Codex or another coding agent.",
            "5. Read `designer_grade_agent_playbook.md` and `public_ai_design_sources.md` before visual refinement.",
            "6. Draft copy with `copy_collection_sheet.md` and `homepage_structure_guide.md`.",
            "7. Design the back office with `reservation_inquiry_system.md`, `operator_runbook.md`, and `integration_options.md`.",
            "8. Price the job with `pricing_menu.md` and send `proposal_one_pager.md`.",
            "9. Finish with `delivery_checklist.md`, `delivery_acceptance_checklist.md`, `client_handoff_note.md`, `accessibility_and_seo_checklist.md`, and `launch_checklist.md`.",
            "10. Open `sample_site/index.html` and `inquiry_dashboard.html` for editable examples.",
            "",
            "## Ground Rule",
            "",
            "Do not sell exact clones. Sell original small-business websites that borrow proven patterns, not protected identity.",
            "",
        ]
    )


def _render_website_side_hustle_readme(payload: dict) -> str:
    sources = ", ".join(source["name"] for source in payload["sources"][:5])
    return "\n".join(
        [
            "# Website Side Hustle Pack",
            "",
            payload["positioning"],
            "",
            f"Best starting niches: {', '.join(payload['starter_verticals'])}.",
            "",
            "## Included",
            "",
            "- Commercial-use-aware source catalog",
            "- Client kickoff questions for the first meeting",
            "- Codex workflow and prompting guide",
            "- Designer-grade AI agent playbook and public AI design source map",
            "- Client brief, copy sheet, proposal, pricing, maintenance, QA, and launch checklists",
            "- Delivery acceptance checklist and client handoff note",
            "- Reservation and inquiry aggregation templates",
            "- One editable sample site and one static back-office dashboard mockup",
            "",
            "## Public Source Base",
            "",
            f"This pack is grounded in public resources such as {sources}, plus public accessibility and SEO references.",
            "",
            "No income is guaranteed. The value of this pack is reducing beginner mistakes, legal risk, and delivery chaos.",
            "",
        ]
    )


def _render_website_side_hustle_positioning(payload: dict) -> str:
    return "\n".join(
        [
            "# Positioning",
            "",
            "Offer: original, small-business websites built quickly with AI assistance, designer-grade agent critique loops, and human-quality checklists.",
            "",
            "What this is not:",
            "- Not a promise of rankings, leads, or passive income.",
            "- Not a license to clone competitors.",
            "- Not a substitute for legal review, brand strategy, or custom photography when those matter.",
            "",
            "Why a client buys:",
            "- Faster first draft than a traditional agency process.",
            "- Stronger iteration because the agent critiques hierarchy, trust, mobile fit, and conversion before delivery.",
            "- Lower cost for brochure sites, landing pages, and local-business refreshes.",
            "- Clear scope, visible mockups, and a reviewable delivery checklist.",
            "",
        ]
    )


def _render_website_side_hustle_niche_offer_menu(payload: dict) -> str:
    rows = [
        ("tourism-hotel", "Quiet hotel or villa", "photos, booking CTA, rooms, access, FAQ", "Story, rooms, local trust, mobile booking"),
        ("clinic", "Clinic or therapist", "services, doctor profile, access, intake CTA", "Trust, compliance boundaries, clear steps"),
        ("salon", "Salon or beauty studio", "services, price ranges, staff, booking CTA", "Photos, repeat visits, social proof"),
        ("restaurant", "Restaurant or cafe", "menu highlights, reservation CTA, map, hours", "Food imagery, hours, route clarity"),
        ("professional-service", "Lawyer, accountant, consultant", "specialization, process, contact CTA", "Serious tone, proof, boundaries"),
        ("local-service", "Trades or repair", "service area, quote CTA, before/after, FAQ", "Fast trust, phone CTA, coverage area"),
    ]
    lines = [
        "# Niche Offer Menu",
        "",
        "| Niche | Buyer | First scope | What raises quality |",
        "|---|---|---|---|",
    ]
    for niche_id, buyer, scope, quality in rows:
        lines.append(f"| `{niche_id}` | {buyer} | {scope} | {quality} |")
    lines.extend(["", "Pick one niche and specialize before broadening the pack.", ""])
    return "\n".join(lines)


def _render_website_side_hustle_sources_md(payload: dict) -> str:
    lines = [
        "# Commercial-Use Public Sources",
        "",
        "Review each source again before live client use. Licenses and repository terms can change.",
        "",
        "| Source | License | Safe use | Why include it | Verify before shipping |",
        "|---|---|---|---|---|",
    ]
    for source in payload["sources"]:
        lines.append(
            f"| [{source['name']}]({source['url']}) | {source['license']} | {source['use']} | {source['why']} | {source['verify']} |"
        )
    lines.extend(
        [
            "",
            "Practical rule: public repos are source material for patterns, components, and checklists. They are not automatic permission to copy a whole site or run unknown setup scripts.",
            "",
        ]
    )
    return "\n".join(lines)


def _render_website_side_hustle_sources_csv(payload: dict) -> str:
    rows = [
        "name,url,license,safe_use,why,verify",
    ]
    for source in payload["sources"]:
        fields = [source["name"], source["url"], source["license"], source["use"], source["why"], source["verify"]]
        rows.append(",".join(f'"{field}"' for field in fields))
    rows.append("")
    return "\n".join(rows)


def _render_website_side_hustle_client_brief(payload: dict) -> str:
    return "\n".join(
        [
            "# Client Brief",
            "",
            "- Business name:",
            "- Industry and niche:",
            "- Primary goal: inquiry / booking / phone / quote / walk-in support",
            "- Required pages:",
            "- Required sections on the homepage:",
            "- Existing logo, photos, colors, fonts:",
            "- Competitor or inspiration links:",
            "- What must be avoided:",
            "- Main CTA:",
            "- Address, hours, phone, map, social links:",
            "- Price range or plan range:",
            "- Trust signals: testimonials, qualifications, reviews, certifications",
            "- Hosting and domain owner:",
            "- Delivery deadline:",
            "",
            "Do not start polished design work until the CTA, facts, and trust signals are clear.",
            "",
        ]
    )


def _render_website_side_hustle_kickoff_questions(payload: dict) -> str:
    niche = payload["niche"].replace("-", " ")
    return "\n".join(
        [
            "# Client Kickoff Questions",
            "",
            f"Use this before building the `{niche}` website. The goal is to collect enough truth to build a useful first version without guessing.",
            "",
            "## 1. Business Goal",
            "",
            "- What is the first action you want visitors to take?",
            "- Which is most valuable: phone call, form inquiry, booking link, LINE message, email, quote request, store visit, or document upload?",
            "- What would make this project worth paying for after 30 days?",
            "- What result should not be promised to customers?",
            "",
            "## 2. Customer And Offer",
            "",
            "- Who is the main customer?",
            "- What problem or desire brings them to the website?",
            "- Which service, room, plan, or offer should be easiest to find?",
            "- What price ranges, plan limits, or availability rules can be shown publicly?",
            "- What common questions should the page answer before a customer contacts you?",
            "",
            "## 3. Proof And Trust",
            "",
            "- What real proof can be shown: reviews, photos, credentials, awards, years in business, staff profile, or case notes?",
            "- Which claims need evidence before they can appear on the site?",
            "- Are there claims the business must avoid for legal, medical, financial, or brand reasons?",
            "",
            "## 4. Assets And Access",
            "",
            "- Who owns the domain, hosting, booking tool, form tool, email inbox, and analytics account?",
            "- Which photos, logo files, colors, fonts, maps, menus, or PDFs are approved for use?",
            "- Which account logins must stay with the client and should never be pasted into AI chat?",
            "",
            "## 5. Inquiry Handling",
            "",
            "- Where should inquiries arrive first?",
            "- Who checks new inquiries each business day?",
            "- What information is required before staff can reply?",
            "- Which replies can be drafted from templates?",
            "- Which steps require Human approval: prices, booking confirmation, cancellation, refund, policy exception, or public launch?",
            "",
            "## 6. Delivery Agreement",
            "",
            "- What will be delivered in the first version?",
            "- What is explicitly out of scope?",
            "- Who approves copy, photos, contact destinations, privacy text, and launch?",
            "- What happens after launch: one-time handoff, monthly maintenance, or improvement sprint?",
            "",
            "If the client cannot answer a question, mark it as missing. Do not invent facts to make the website look complete.",
            "",
        ]
    )


def _render_website_side_hustle_agent_handoff(payload: dict) -> str:
    niche = payload["niche"].replace("-", " ")
    return "\n".join(
        [
            "# AI Agent Handoff",
            "",
            "Use this file with Codex, Claude Code, Cursor, or another coding agent. It is written as a tool-neutral instruction so the same project can move between agents.",
            "",
            "## Agent Role",
            "",
            f"You are helping a beginner deliver an original small-business website and inquiry operations pack for `{niche}`.",
            "",
            "## Files To Read First",
            "",
            "1. `START_HERE_WEBSITE_SIDE_HUSTLE.md`",
            "2. `client_brief.md`",
            "3. `commercial_use_sources.md`",
            "4. `originality_and_license_rules.md`",
            "5. `homepage_structure_guide.md`",
            "6. `reservation_inquiry_system.md`",
            "7. `operator_runbook.md`",
            "8. `privacy_and_consent.md`",
            "9. `designer_grade_agent_playbook.md`",
            "",
            "## Build The Front Of The Website",
            "",
            "- Confirm the business goal: booking, inquiry, phone call, quote request, or walk-in support.",
            "- Use client-approved facts only. If facts are missing, leave placeholders and list what is needed.",
            "- Build an original layout. Public GitHub projects can inform components and patterns, but do not copy a competitor's identity, text, images, or full layout.",
            "- Make the first viewport clear: business type, offer, location or audience, and primary CTA.",
            "- Run the designer-grade loop: brief, audience, visual system, layout, copy, browser critique, revision, final acceptance.",
            "- Check mobile width, CTA visibility, image loading, text overflow, and form labels.",
            "",
            "## Build The Back Office",
            "",
            "- Treat the website form, phone notes, email, LINE, and booking portal exports as possible sources.",
            "- Normalize all leads into `inquiry_intake_schema.csv`.",
            "- Use `reservation_pipeline.csv` for statuses.",
            "- Draft replies from `response_templates.md`, but do not auto-send final replies.",
            "- Do not auto-confirm bookings, change prices, or make policy exceptions without human approval.",
            "- Keep secrets, API keys, passwords, and real private customer data out of chat.",
            "",
            "## Recommended Output",
            "",
            "- One browser-ready website or sample site",
            "- One browser-ready inquiry dashboard or spreadsheet plan",
            "- A client handoff note explaining how to update text, images, contact destinations, and inquiry statuses",
            "- A short risk note listing what still requires human approval",
            "",
            "## Final Verification",
            "",
            "Before saying the work is complete, verify the site and dashboard in a browser, inspect generated files, and confirm that no real secrets or private customer records are included.",
            "",
        ]
    )


def _render_website_side_hustle_designer_grade_playbook(payload: dict) -> str:
    return "\n".join(
        [
            "# Designer-Grade AI Agent Playbook",
            "",
            "This playbook helps an AI agent support design work at a higher level. The goal is not to pretend that design taste is automatic. The goal is to make the agent repeat the parts good designers do deliberately: understand the user, choose hierarchy, create a visual system, test the work in context, and revise from evidence.",
            "",
            "## Core Mindset",
            "",
            "A programmer using an AI agent can become stronger at design when the workflow forces the agent to explain design decisions, show trade-offs, and verify the rendered result. A designer using an AI agent can become stronger at implementation when the workflow turns taste into repeatable tokens, components, states, and acceptance checks.",
            "",
            "Do not aim for a single prompt that makes a perfect page. Aim for a loop that makes weak design visible and correctable.",
            "",
            "## The Seven-Step Design Loop",
            "",
            "1. Brief: identify the business, audience, offer, trust signals, and primary action.",
            "2. Positioning: decide what the visitor should understand in the first five seconds.",
            "3. Visual system: choose type scale, color roles, spacing rhythm, image treatment, buttons, forms, and cards.",
            "4. Information architecture: decide section order before styling individual blocks.",
            "5. Implementation: build with real content structure, accessible labels, responsive rules, and stable dimensions.",
            "6. Browser critique: inspect desktop and mobile rendering, overflow, CTA visibility, contrast, form clarity, and whether the page feels original.",
            "7. Revision: fix the highest-impact problems first, then repeat the browser critique.",
            "",
            "## Designer-Level Questions The Agent Must Answer",
            "",
            "- What should the visitor do next?",
            "- What proof makes the claim believable?",
            "- Which section can be removed because it does not help a decision?",
            "- Which visual choice supports trust rather than decoration?",
            "- What is intentionally different from references or competitors?",
            "- What breaks on mobile, small screens, long words, or missing images?",
            "- What still requires human approval: facts, claims, photos, prices, policies, privacy, or launch?",
            "",
            "## AI Agent Instructions",
            "",
            "Use this prompt before redesigning or building a client website:",
            "",
            "```text",
            "Act as a design reviewer and implementation partner.",
            "First summarize the audience, offer, trust signals, and primary action.",
            "Then propose one original visual direction with type, color, spacing, imagery, and section order.",
            "Build or revise the page using the existing stack.",
            "After rendering, critique the page like a senior designer: hierarchy, clarity, trust, originality, accessibility, mobile fit, and conversion path.",
            "Do not copy competitor identity, text, photos, or full layout.",
            "Do not invent facts, testimonials, awards, or prices.",
            "Keep launch, legal, privacy, prices, and booking confirmation behind human approval.",
            "```",
            "",
            "## What To Borrow From Public Skills And OSS",
            "",
            "- From skill systems: explicit instructions, checklists, and reusable domain knowledge.",
            "- From design systems: tokens, component states, accessible primitives, and consistency rules.",
            "- From AI UI tools: fast visual exploration, but not final quality without human review.",
            "- From open-source sites: patterns and implementation ideas, not brand identity or full-page cloning.",
            "",
            "## Quality Bar",
            "",
            "A page is not designer-grade because it looks expensive. It is designer-grade when a real visitor can understand the offer, trust the business, take the next action, and use the page comfortably on mobile.",
            "",
            "Before delivery, the agent must produce a short critique with:",
            "",
            "- strongest design choice",
            "- weakest design choice",
            "- mobile risk",
            "- accessibility risk",
            "- conversion risk",
            "- originality risk",
            "- human approvals still needed",
            "",
        ]
    )


def _render_website_side_hustle_public_ai_design_sources(payload: dict) -> str:
    rows = [
        (
            "Anthropic Claude Skills / Claude Code skills",
            "https://docs.anthropic.com/en/docs/claude-code/skills",
            "Reusable task instructions and domain knowledge for agents",
            "Use the skill pattern to package website design knowledge into clear steps and safety gates",
            "Read the docs and license before copying any third-party skill content",
        ),
        (
            "OpenAI Codex",
            "https://platform.openai.com/docs/codex",
            "Agentic coding workflow for reading, editing, testing, and reviewing code",
            "Use Codex to turn the design playbook into files, browser checks, and tests",
            "Keep secrets and private client data out of prompts and commits",
        ),
        (
            "Figma Dev Mode MCP / design-to-code context",
            "https://help.figma.com/hc/en-us/articles/32132100833559-Guide-to-the-Dev-Mode-MCP-Server",
            "Bridge between design context and implementation tools",
            "Use when a client or designer has Figma assets that should guide code",
            "Respect asset rights, client ownership, and design system boundaries",
        ),
        (
            "Vercel v0",
            "https://v0.dev/",
            "AI-assisted UI generation and exploration",
            "Use for quick layout exploration and component ideas, then verify in the real project",
            "Do not treat generated UI as automatically original or production-ready",
        ),
        (
            "shadcn/ui",
            "https://github.com/shadcn-ui/ui",
            "Accessible component patterns that can be owned in the project",
            "Use as a base for forms, buttons, cards, dialogs, and navigation",
            "Copy only what is needed and keep styling aligned with the client brand",
        ),
        (
            "A11y Project Checklist",
            "https://www.a11yproject.com/checklist/",
            "Practical accessibility checklist",
            "Use as an acceptance check before delivery",
            "Pair with browser and keyboard checks",
        ),
    ]
    lines = [
        "# Public AI Design Sources",
        "",
        "This file maps public AI, design, and OSS references that can improve the website side-hustle workflow. Treat these as learning sources and workflow references, not as permission to copy a full design, brand, or private system.",
        "",
        "| Source | URL | What it gives | How to use it | Safety check |",
        "|---|---|---|---|---|",
    ]
    for name, url, gives, use, safety in rows:
        lines.append(f"| {name} | {url} | {gives} | {use} | {safety} |")
    lines.extend(
        [
            "",
            "Recommended path:",
            "",
            "1. Use public sources to define the workflow and quality bar.",
            "2. Use client facts to create the actual design direction.",
            "3. Use AI agents to implement, critique, and revise.",
            "4. Use human review for originality, claims, accessibility, privacy, and launch.",
            "",
        ]
    )
    return "\n".join(lines)


def _render_website_side_hustle_quality_gate(payload: dict) -> str:
    return "\n".join(
        [
            "# Website Quality Gate",
            "",
            "Use this before client delivery. It turns public quality references into a practical gate for AI-assisted small-business websites.",
            "",
            "## Research Base",
            "",
            "- Core Web Vitals: check loading, interaction responsiveness, and visual stability.",
            "- WCAG and A11y Project: check headings, labels, keyboard access, contrast, focus, and alternative text.",
            "- Google SEO Starter Guide: check truthful titles, descriptions, links, headings, and useful content.",
            "- Lighthouse or browser audits: use as supporting evidence, not as the only quality judgment.",
            "- Usability heuristics: check whether the page communicates status, prevents errors, and uses familiar patterns.",
            "",
            "## Pass Gate",
            "",
            "A page can move to client review only when all of these are true:",
            "",
            "- The hero says what the business is, who it serves, and what action to take.",
            "- The primary CTA is visible on desktop and mobile before the visitor has to hunt for it.",
            "- Body text, buttons, cards, forms, and navigation do not overflow on mobile.",
            "- Images are rights-safe, load correctly, and are not dark filler.",
            "- Every form control has a useful label and a clear success or error path.",
            "- Keyboard focus is visible for links, buttons, and inputs.",
            "- Heading order is readable and there is one clear H1.",
            "- Page title and meta description are specific and truthful.",
            "- The contact or booking path has been tested end to end in dry-run mode.",
            "- No fake reviews, fake awards, invented prices, or unapproved policy claims are present.",
            "- Human approval remains required for launch, prices, legal/privacy text, and booking confirmation.",
            "",
            "## Scoring",
            "",
            "Use `homepage_review_scorecard.csv` to score the page. If any critical item fails, revise before delivery even if the total score looks high.",
            "",
            "Recommended minimums:",
            "",
            "- 90+ points: client-ready for a small brochure or inquiry site.",
            "- 80-89 points: usable draft, but revise weak sections before launch.",
            "- Under 80 points: do not present as finished.",
            "",
            "## Evidence To Keep",
            "",
            "- desktop screenshot",
            "- mobile screenshot",
            "- form or CTA dry-run result",
            "- scorecard result",
            "- list of human approvals still needed",
            "",
        ]
    )


def _render_website_side_hustle_scorecard_csv(payload: dict) -> str:
    rows = [
        ["criterion", "pass_threshold", "points", "evidence", "critical"],
        ["Hero clarity", "Business, audience, offer, and primary action are clear in the first viewport", "10", "desktop and mobile screenshots", "yes"],
        ["CTA visibility", "Primary CTA is visible and distinct on desktop and mobile", "10", "screenshots", "yes"],
        ["Trust proof", "Real reviews, credentials, photos, years, staff, or local details support the claims", "10", "client-approved proof list", "yes"],
        ["Mobile fit", "No horizontal scroll or clipped text at common mobile widths", "10", "mobile browser check", "yes"],
        ["Accessibility basics", "H1, labels, alt text, focus states, contrast, and keyboard paths are checked", "15", "manual checklist or audit notes", "yes"],
        ["Performance basics", "Images are sized, layout is stable, and Core Web Vitals risks are reviewed", "10", "Lighthouse or browser performance notes", "no"],
        ["SEO basics", "Title, meta description, headings, internal links, and useful content are truthful", "10", "page source or checklist", "no"],
        ["Form and inquiry path", "Contact or booking path works in dry-run mode and has success/error states", "10", "dry-run result", "yes"],
        ["Originality and rights", "No cloned identity, copied text, unlicensed images, or unsupported claims", "10", "source log and originality notes", "yes"],
        ["Handoff readiness", "Client can understand updates, inquiry status, approvals, and maintenance scope", "5", "client handoff note", "no"],
    ]
    return "\n".join(",".join(f'"{field}"' for field in row) for row in rows) + "\n"


def _render_website_side_hustle_agent_review_prompt(payload: dict) -> str:
    return "\n".join(
        [
            "# Agent Design Review Prompt",
            "",
            "Use this prompt after the website is rendered in a browser and before client delivery.",
            "",
            "```text",
            "Act as a senior website quality reviewer for a small-business website.",
            "",
            "Review the page against these gates:",
            "1. Hero clarity: business, audience, offer, and primary action.",
            "2. Conversion path: CTA visibility, form flow, booking/contact dry-run.",
            "3. Trust: real proof, specific claims, local details, and no invented facts.",
            "4. Accessibility: H1, heading order, labels, alt text, focus states, contrast, keyboard path.",
            "5. Mobile: no horizontal scroll, no clipped text, no cramped controls.",
            "6. Performance: image sizing, layout stability, heavy assets, Core Web Vitals risk.",
            "7. SEO: truthful title, meta description, headings, useful content, internal links.",
            "8. Originality: no copied competitor identity, text, images, or full layout.",
            "9. Back office: inquiry table, status flow, response templates, and human approval boundaries.",
            "",
            "Return:",
            "- score out of 100",
            "- top 5 fixes in priority order",
            "- critical blockers",
            "- what should be tested in the browser again",
            "- what needs human approval before launch",
            "",
            "Do not say the site is ready if any critical blocker remains.",
            "```",
            "",
        ]
    )


def _render_website_side_hustle_beginner_human_guide_en(payload: dict) -> str:
    return "\n".join(
        [
            "# Beginner Human Guide: Website And Back-Office Delivery",
            "",
            "This guide is for people who are new to AI-assisted website work. The goal is not only to create a nice-looking homepage. The goal is to help a real business receive inquiries, review them safely, reply consistently, and know what a human must approve.",
            "",
            "## The Big Picture",
            "",
            "A sellable small-business website package has two sides:",
            "",
            "- Front office: the public website customers see.",
            "- Back office: the inquiry, reservation, response, and follow-up workflow the business uses after a customer contacts them.",
            "",
            "A pretty page without a clear back-office process is hard to sell as a serious service. A simple website plus a simple operating system is much stronger.",
            "",
            "## Step 1: Understand The Business",
            "",
            "Before asking an AI agent to design anything, collect plain facts from the client.",
            "",
            "- Business name",
            "- Location or service area",
            "- Main customer type",
            "- Main goal: booking, inquiry, phone call, quote request, visit, or appointment",
            "- Services, rooms, plans, or products",
            "- Opening hours and contact methods",
            "- Trust signals: reviews, certifications, awards, years in business, staff profiles",
            "- Policies: cancellation, parking, payment, check-in, appointment rules",
            "- Existing assets: logo, photos, colors, social links, booking links",
            "",
            "If a fact is missing, leave a placeholder. Do not invent business claims, prices, testimonials, or awards.",
            "",
            "## Step 2: Build The Front Website",
            "",
            "Use a simple page order that helps a visitor decide quickly.",
            "",
            "1. Hero: what the business is, who it helps, where it is, and the main call to action.",
            "2. Reasons to choose: concrete proof instead of vague adjectives.",
            "3. Services, rooms, plans, or offers: clear names, short descriptions, and price ranges when approved.",
            "4. How it works: what happens after the customer contacts the business.",
            "5. Proof: reviews, credentials, photos, case notes, or FAQ answers.",
            "6. Access and contact: map, phone, email, form, booking link, hours, and service area.",
            "7. Final call to action: repeat the next step at the bottom.",
            "",
            "Design rule: use public design projects as learning material, not as permission to copy a competitor. Do not copy another business's text, photos, logo, full layout, or brand identity.",
            "",
            "## Step 3: Build The Back Office",
            "",
            "Start simple. Most first clients do not need a custom backend. They need one reliable place where inquiries are collected and reviewed.",
            "",
            "Good beginner setup:",
            "",
            "- Form: Google Forms, Tally, Typeform, Netlify Forms, or Formspree",
            "- Table: Google Sheets, Airtable, or Notion",
            "- Inbox support: Gmail labels or shared mailbox rules",
            "- Dashboard: a simple HTML mockup or spreadsheet view",
            "",
            "Use `inquiry_intake_schema.csv` as the field list. Use `reservation_pipeline.csv` as the status list.",
            "",
            "Recommended statuses:",
            "",
            "- `new`: not reviewed yet",
            "- `needs-info`: missing dates, contact method, guest count, or request details",
            "- `availability-check`: staff must check room, appointment, inventory, or schedule",
            "- `quoted`: a price or plan was sent",
            "- `tentative`: held but not final",
            "- `confirmed`: human-approved booking or appointment",
            "- `declined`: cannot accept the request",
            "- `canceled`: customer or business canceled",
            "- `follow-up`: waiting for a reminder or next action",
            "",
            "## Step 4: Write Response Templates",
            "",
            "Create drafts for common replies:",
            "",
            "- inquiry received",
            "- missing information",
            "- availability and quote",
            "- no availability",
            "- follow-up",
            "- general contact",
            "",
            "AI can draft replies, but a human should check names, dates, prices, policies, and tone before sending.",
            "",
            "## Step 5: Daily Operations",
            "",
            "Every business day, the operator should:",
            "",
            "1. Open the inquiry table.",
            "2. Sort by priority and next action due date.",
            "3. Remove spam and duplicate rows.",
            "4. Fill missing information when possible.",
            "5. Ask staff to check availability, price, or exceptions.",
            "6. Draft the reply.",
            "7. Have a human review and send the reply.",
            "8. Update the status and next action due date.",
            "",
            "Weekly review:",
            "",
            "- How many inquiries came from each source?",
            "- How many became bookings, appointments, or qualified leads?",
            "- Which replies were late?",
            "- Which questions were repeated?",
            "- What FAQ or website section should be improved?",
            "",
            "## Step 6: What Humans Must Approve",
            "",
            "Keep these behind human approval:",
            "",
            "- launch decision",
            "- final copy and brand tone",
            "- real customer facts",
            "- final booking confirmation",
            "- price exceptions",
            "- cancellation or refund policy exceptions",
            "- production email, SMS, LINE, or CRM sending",
            "- legal, privacy, and license decisions",
            "",
            "## Step 7: What Not To Do",
            "",
            "- Do not paste API keys, passwords, or real private customer data into chat.",
            "- Do not ask AI to confirm reservations by itself.",
            "- Do not collect payment card details through a plain contact form.",
            "- Do not create fake reviews, fake awards, or fake credentials.",
            "- Do not copy competitor websites.",
            "- Do not promise rankings, sales, or guaranteed bookings.",
            "",
            "## Step 8: Delivery Checklist",
            "",
            "Before handing the project to a client, verify:",
            "",
            "- The website opens on desktop and mobile.",
            "- The main call to action is visible near the top.",
            "- Contact destinations are correct.",
            "- The inquiry table fields are understandable.",
            "- Status rules are documented.",
            "- Response templates are reviewed.",
            "- The client knows who checks inquiries each day.",
            "- Human approval boundaries are written down.",
            "- No secrets or private customer records are included in generated files.",
            "",
            "## Why This Can Become A Side Hustle",
            "",
            "Small businesses often do not only need a new homepage. They need a clearer way to receive and handle customer interest. This package helps a beginner sell a practical outcome: a website people can use and an operating workflow the business can understand.",
            "",
        ]
    )


def _render_website_side_hustle_beginner_human_guide(payload: dict) -> str:
    return "\n".join(
        [
            "# 初心者向け: ホームページ制作と裏側運用の人間用ガイド",
            "",
            "このガイドは、AIやコードに慣れていない人が、ホームページ制作の副業を安全に始めるための手順書です。目的は「きれいなページを作ること」だけではありません。問い合わせが来た後に、誰が見て、どう返信し、どこまで人間が確認するかまで作ることです。",
            "",
            "## 全体像",
            "",
            "1. お客様の商売を理解する",
            "2. ホームページに載せる事実を集める",
            "3. 表側のページを作る",
            "4. 問い合わせ・予約を集める台帳を作る",
            "5. 返信テンプレートと確認ルールを作る",
            "6. PCとスマホで確認する",
            "7. お客様に渡す説明文を作る",
            "",
            "## 1. 最初に聞くこと",
            "",
            "- 何を増やしたいか: 予約、問い合わせ、電話、来店、見積もり依頼",
            "- お客様は誰か: 観光客、近所の人、法人、リピーター、新規客",
            "- 必ず載せる情報: 営業時間、場所、料金、サービス、部屋、写真、注意事項",
            "- 信頼材料: 口コミ、実績、資格、受賞、スタッフ紹介、よくある質問",
            "- 連絡先: メール、電話、LINE、予約サイト、Googleフォームなど",
            "",
            "## 2. 表側のホームページの作り方",
            "",
            "ホームページは、上から順番に読んだ人が迷わない構成にします。",
            "",
            "1. 最初の画面: 何の店・施設で、誰向けで、何をしてほしいかを書く",
            "2. 選ばれる理由: 他と違う点を事実で書く",
            "3. サービスや部屋: 写真、内容、料金の目安を書く",
            "4. 利用の流れ: 問い合わせから予約・来店までの流れを書く",
            "5. 信頼材料: 口コミ、実績、FAQを書く",
            "6. アクセス・営業時間・連絡先を書く",
            "7. 最後にもう一度問い合わせボタンを置く",
            "",
            "注意点: 競合サイトをそのまま真似しないでください。構成の考え方は参考にできますが、文章、写真、ロゴ、色使い、レイアウトを丸ごとコピーしてはいけません。",
            "",
            "## 3. 裏側の管理の作り方",
            "",
            "問い合わせや予約は、最初から複雑なシステムにしなくて大丈夫です。まずは一つの台帳に集めます。",
            "",
            "おすすめの最初の形:",
            "",
            "- フォーム: Googleフォーム、Tally、Netlify Formsなど",
            "- 台帳: Googleスプレッドシート、Airtable、Notionなど",
            "- ステータス: new、needs-info、availability-check、quoted、tentative、confirmed、declined、canceled、follow-up",
            "- 返信: テンプレートを使って下書きし、人間が確認して送る",
            "",
            "重要: AIが予約確定や価格変更を勝手に行う形にはしないでください。最初は、AIは整理と下書きまで、人間が最終確認という形が安全です。",
            "",
            "## 4. 毎日の運用",
            "",
            "毎日見る順番:",
            "",
            "1. 新しい問い合わせを見る",
            "2. 重複や迷惑メールを除く",
            "3. 足りない情報があれば聞き返す",
            "4. 予約や空き状況は人間が確認する",
            "5. 返信文を作り、人間が確認して送る",
            "6. 次に何をするか、いつまでにするかを書く",
            "",
            "週に一度見るもの:",
            "",
            "- 問い合わせがどこから来たか",
            "- 何件が予約や商談につながったか",
            "- 返信が遅れたものはないか",
            "- 同じ質問が何度も来ていないか",
            "- ホームページに追加すべきFAQはないか",
            "",
            "## 5. 納品するときに説明すること",
            "",
            "お客様には、次の4つを短く説明します。",
            "",
            "1. ホームページのどこを見ればよいか",
            "2. 問い合わせがどこに入るか",
            "3. ステータスをどう変えるか",
            "4. AIに任せてよいこと、人間が必ず確認すること",
            "",
            "## 6. やってはいけないこと",
            "",
            "- APIキー、パスワード、顧客の個人情報をチャットに貼る",
            "- 予約をAIだけで確定する",
            "- 料金やキャンセル規定をAIだけで変更する",
            "- 競合サイトを丸ごとコピーする",
            "- 実在しない口コミや実績を書く",
            "",
            "このガイドのゴールは、初心者でも「何を作り、何を確認し、どこからお金をもらう価値が出るのか」を見失わないようにすることです。",
            "",
        ]
    )


def _render_website_side_hustle_design_direction(payload: dict) -> str:
    return "\n".join(
        [
            "# Design Direction Template",
            "",
            "## Site Goal",
            "",
            "## Audience",
            "",
            "## Visual Tone",
            "",
            "## Section Order",
            "",
            "## Design Tokens",
            "- Typography",
            "- Background and surface colors",
            "- CTA color",
            "- Border and radius rules",
            "- Spacing scale",
            "",
            "## Proof And Trust Elements",
            "",
            "## Originality Notes",
            "- Pattern principles to borrow",
            "- Brand signals that must be different",
            "",
        ]
    )


def _render_website_side_hustle_copy_sheet(payload: dict) -> str:
    return "\n".join(
        [
            "# Copy Collection Sheet",
            "",
            "Collect client facts before asking the AI to write homepage copy.",
            "",
            "- Exact business name:",
            "- Short one-line promise:",
            "- Services or room types:",
            "- Why customers choose this business over nearby options:",
            "- What happens after inquiry or booking:",
            "- Best testimonial or review quote:",
            "- Local details that make the page believable:",
            "- FAQ topics customers ask already:",
            "- Policy notes that matter: cancellation, parking, appointments, payment, hours:",
            "",
            "Rule: replace vague adjectives with facts, scenes, or outcomes.",
            "",
        ]
    )


def _render_website_side_hustle_codex_workflow(payload: dict) -> str:
    return "\n".join(
        [
            "# Codex Workflow",
            "",
            "Use this with Codex, Claude Code, Cursor, or another coding agent after sharing the repository and the current project folder.",
            "",
            "```text",
            "Read commercial_use_sources.md, originality_and_license_rules.md, client_brief.md, and homepage_structure_guide.md first.",
            "Then build an original small-business website in one narrow niche.",
            "Use public GitHub design resources only as references for patterns and accessible components.",
            "Do not copy competitor copy, logos, or layouts exactly.",
            "Before finishing, verify desktop and mobile rendering, CTA visibility, image loading, text overflow, and the delivery checklist.",
            "```",
            "",
            "Use browser verification for every visual milestone, not only at the end.",
            "",
        ]
    )


def _render_website_side_hustle_stack(payload: dict) -> str:
    lines = [
        "# Implementation Stack",
        "",
        "Default stack for brochure and landing-page work:",
        "",
        "| Layer | Recommendation | Why |",
        "|---|---|---|",
        "| Site type | Static HTML or Astro | Fast, cheap hosting, low maintenance |",
        "| Components | shadcn/ui or lightweight local components | Accessible base patterns |",
        "| Tokens | CSS variables, optionally Open Props | Consistent spacing and styling |",
        "| Icons | lucide | Predictable, commercial-friendly icon set |",
        "| QA | Browser screenshots plus checklist | Stops layout regressions |",
        "| Hosting | GitHub Pages, Netlify, Cloudflare Pages, Vercel | Beginner-friendly deployment options |",
        "",
    ]
    return "\n".join(lines)


def _render_website_side_hustle_structure(payload: dict) -> str:
    return "\n".join(
        [
            "# Homepage Structure Guide",
            "",
            "Recommended order for small-business websites:",
            "",
            "1. Hero with exact buyer, offer, and primary CTA",
            "2. Why choose this business",
            "3. Services, room types, or featured offers",
            "4. Process or how booking/contact works",
            "5. Proof: reviews, certifications, case notes, before/after",
            "6. Access, map, hours, contact",
            "7. FAQ",
            "8. Final CTA",
            "",
            "Remove sections that do not help the client decide.",
            "",
        ]
    )


def _render_website_side_hustle_reservation_system(payload: dict) -> str:
    return "\n".join(
        [
            "# Reservation And Inquiry System",
            "",
            "This is the back-office layer that makes a website project more useful than a brochure page.",
            "",
            "## Core Flow",
            "",
            "1. Capture inquiries from the website form, phone notes, email, LINE, booking portal exports, or manual staff entry.",
            "2. Normalize every item into `inquiry_intake_schema.csv` so the operator can compare them in one place.",
            "3. Deduplicate by email, phone, requested date range, and message similarity before replying.",
            "4. Classify the item: reservation request, availability question, general inquiry, group booking, complaint, or spam.",
            "5. Check availability and policy manually before sending a reply.",
            "6. Draft a response from `response_templates.md`, then have a human review and send it.",
            "7. Move the item through `reservation_pipeline.csv` until it is confirmed, declined, canceled, or archived.",
            "",
            "## Safety Boundaries",
            "",
            "- Do not auto-confirm a booking without human approval.",
            "- Do not quote final prices unless the client has approved the current price table and exceptions.",
            "- Do not store card numbers, passport scans, medical details, or other unnecessary sensitive data.",
            "- Do not mix multiple client businesses in one shared spreadsheet unless access controls are clear.",
            "",
            "## Deliverable To Client",
            "",
            "For a beginner-friendly package, deliver a form, one shared intake table, status rules, response templates, and a daily runbook before adding automation.",
            "",
        ]
    )


def _render_website_side_hustle_inquiry_schema_csv(payload: dict) -> str:
    rows = [
        [
            "field",
            "type",
            "required",
            "example",
            "operator_note",
        ],
        ["lead_id", "text", "yes", "TH-2026-0001", "Stable ID used across email, sheet, and dashboard"],
        ["received_at", "datetime", "yes", "2026-06-25 09:15", "Use one timezone for the client"],
        ["source", "select", "yes", "website_form", "website_form, phone, email, LINE, booking_portal, manual"],
        ["customer_name", "text", "yes", "Aoki Hana", "Minimum name needed to reply"],
        ["contact_method", "select", "yes", "email", "email, phone, LINE, other"],
        ["email", "email", "no", "guest@example.com", "Needed for email replies"],
        ["phone", "text", "no", "090-0000-0000", "Keep formatting consistent"],
        ["check_in", "date", "no", "2026-08-12", "Reservation inquiries only"],
        ["check_out", "date", "no", "2026-08-14", "Reservation inquiries only"],
        ["guests", "number", "no", "2", "Adults and children can become separate fields later"],
        ["requested_room_or_service", "text", "no", "Ocean view twin", "Room, plan, service, or inquiry category"],
        ["message", "long_text", "yes", "Is parking available?", "Original customer request"],
        ["status", "select", "yes", "new", "Must match reservation_pipeline.csv"],
        ["priority", "select", "yes", "normal", "urgent, normal, low"],
        ["owner", "text", "no", "front-desk", "Person or team responsible"],
        ["next_action_due", "datetime", "no", "2026-06-25 13:00", "Prevents stale leads"],
        ["consent_notes", "text", "no", "form privacy notice accepted", "Record consent source when available"],
    ]
    return "\n".join(",".join(f'"{field}"' for field in row) for row in rows) + "\n"


def _render_website_side_hustle_reservation_pipeline_csv(payload: dict) -> str:
    rows = [
        ["status", "meaning", "owner_action", "exit_rule"],
        ["new", "Unreviewed inquiry", "Check source, spam, duplicates, and required fields", "Valid item is classified"],
        ["needs-info", "Customer details are missing", "Send missing-info template", "Customer replies or lead is closed"],
        ["availability-check", "Dates or service availability must be checked", "Confirm calendar, room, staff, or inventory", "Availability is known"],
        ["quoted", "Price or plan has been sent", "Wait for customer response and set follow-up due date", "Customer accepts, declines, or expires"],
        ["tentative", "Held but not final", "Confirm hold rule and deadline with staff", "Human approves confirmation or releases hold"],
        ["confirmed", "Booking or appointment is accepted", "Send approved confirmation details", "Service completed or canceled"],
        ["declined", "Cannot accept request", "Send no-availability or out-of-scope reply", "Archive after review"],
        ["canceled", "Customer or business canceled", "Record reason and notify relevant staff", "Archive after review"],
        ["follow-up", "Lead needs a reminder", "Send approved follow-up before due date", "Customer replies or lead is closed"],
    ]
    return "\n".join(",".join(f'"{field}"' for field in row) for row in rows) + "\n"


def _render_website_side_hustle_response_templates(payload: dict) -> str:
    return "\n".join(
        [
            "# Response Templates",
            "",
            "Use these as drafts only. A human should review availability, price, names, dates, and policy before sending.",
            "",
            "## Reservation Inquiry Received",
            "",
            "Subject: Thank you for your inquiry",
            "",
            "Thank you for contacting us. We received your request for [DATE / SERVICE]. We will check availability and reply with the next step shortly.",
            "",
            "## Missing Information",
            "",
            "Subject: A quick question about your request",
            "",
            "Thank you for your inquiry. To check availability, could you please send: [MISSING FIELD LIST]? Once we receive this, we will review the request.",
            "",
            "## Availability And Quote",
            "",
            "Subject: Availability for your requested dates",
            "",
            "We have availability for [DATE RANGE / SERVICE]. The estimated price is [APPROVED PRICE], including [INCLUSIONS]. Please reply by [DEADLINE] if you would like us to proceed.",
            "",
            "## No Availability",
            "",
            "Subject: About your requested dates",
            "",
            "Thank you for checking with us. Unfortunately, we do not have availability for [DATE RANGE]. If your dates are flexible, we can check [ALTERNATIVE DATE / OPTION].",
            "",
            "## Follow-Up",
            "",
            "Subject: Following up on your inquiry",
            "",
            "I wanted to follow up on your request for [DATE / SERVICE]. If you are still interested, please reply by [DATE]. If your plans changed, no problem.",
            "",
            "## General Contact",
            "",
            "Subject: Thank you for contacting us",
            "",
            "Thank you for your message. We will review it and reply as soon as possible. For urgent same-day matters, please call [PHONE NUMBER].",
            "",
        ]
    )


def _render_website_side_hustle_operator_runbook(payload: dict) -> str:
    return "\n".join(
        [
            "# Operator Runbook",
            "",
            "## Daily Review",
            "",
            "1. Open the intake table and sort by `priority`, then `next_action_due`, then `received_at`.",
            "2. Check `new` rows for spam, duplicates, and missing fields.",
            "3. Move valid rows to the correct status in `reservation_pipeline.csv`.",
            "4. Draft replies from `response_templates.md`.",
            "5. Ask the client or staff to approve availability, price, and exceptions before sending.",
            "6. Record the sent reply summary and set the next action due date.",
            "",
            "## Weekly Review",
            "",
            "- Count new inquiries by source.",
            "- Count confirmed, declined, canceled, and stale leads.",
            "- List repeated questions that should become FAQ content on the website.",
            "- Review response speed and missed follow-ups.",
            "",
            "## Automation Rule",
            "",
            "Automation may draft, label, copy rows, and remind. It should not send final confirmations, change prices, or make policy exceptions without human approval.",
            "",
        ]
    )


def _render_website_side_hustle_integration_options(payload: dict) -> str:
    return "\n".join(
        [
            "# Integration Options",
            "",
            "Choose the lowest-risk setup that fits the client. Keep account ownership and credentials with the client whenever possible.",
            "",
            "| Setup | Good for | Notes |",
            "|---|---|---|",
            "| Google Forms + Google Sheets | beginner intake | cheap, visible, easy to audit |",
            "| Tally or Typeform + Sheets | polished forms | check plan limits and data storage terms |",
            "| Formspree or Netlify Forms | static websites | useful for GitHub Pages, Netlify, or Astro sites |",
            "| Airtable | richer status tracking | better views, more moving parts |",
            "| Notion database | small teams already using Notion | simple, but permissions must be checked |",
            "| Gmail labels + filters | email-heavy businesses | good for triage, weak as a source of truth |",
            "| Zapier, Make, or n8n | cross-tool automation | start after the manual workflow is stable |",
            "| Self-hosted backend | custom requirements | higher maintenance and security responsibility |",
            "",
            "Do not paste API keys, email passwords, or private customer data into chat. Store secrets in the hosting provider or the client's approved password manager.",
            "",
        ]
    )


def _render_website_side_hustle_privacy_consent(payload: dict) -> str:
    return "\n".join(
        [
            "# Privacy And Consent",
            "",
            "This is an operational checklist, not legal advice. Ask the client to review privacy language for their location and industry.",
            "",
            "## Data Minimization",
            "",
            "- Collect only the fields needed to answer or process the inquiry.",
            "- Avoid sensitive data unless the business has a clear legal and operational reason.",
            "- Do not request payment card data through a plain contact form.",
            "",
            "## Form Notice",
            "",
            "Example notice: The information you send will be used to respond to your inquiry or reservation request. Please do not include sensitive personal information in this form.",
            "",
            "## Retention",
            "",
            "- Decide how long to keep unconverted inquiries.",
            "- Archive or delete stale leads on a schedule approved by the client.",
            "- Limit spreadsheet and inbox access to people who need it.",
            "",
            "## Japan-Oriented Reminder",
            "",
            "For Japanese clients, privacy handling should be reviewed against the Act on the Protection of Personal Information and the client's own privacy policy.",
            "",
        ]
    )


def _render_website_side_hustle_sla_followup(payload: dict) -> str:
    return "\n".join(
        [
            "# SLA And Follow-Up Rules",
            "",
            "## Suggested Response Targets",
            "",
            "| Priority | Target | Example |",
            "|---|---|---|",
            "| urgent | same business day | same-day stay, complaint, phone escalation |",
            "| normal | within 24 hours | normal reservation or contact inquiry |",
            "| low | within 2 business days | broad question, future planning, partnership |",
            "",
            "## Stale Lead Rules",
            "",
            "- If `new` is older than 24 hours, escalate to the owner.",
            "- If `quoted` has no reply after 48 hours, send one follow-up.",
            "- If no reply after the follow-up deadline, close or archive the lead.",
            "- If the same question repeats, add it to the website FAQ or booking notes.",
            "",
            "## Metrics To Track",
            "",
            "- inquiries by source",
            "- average first response time",
            "- confirmed reservations or accepted inquiries",
            "- stale leads",
            "- repeated FAQ topics",
            "",
        ]
    )


def _render_website_side_hustle_inquiry_dashboard(payload: dict) -> str:
    niche_label = html.escape(payload["niche"].replace("-", " ").title())
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Reservation Inbox | {niche_label}</title>
    <style>
      :root {{
        --ink: #182126;
        --paper: #f7f4ee;
        --line: #d8d0c3;
        --brand: #1f5f68;
        --accent: #b96b32;
        --ok: #2f6f4e;
        --warn: #a15c18;
        --soft: #fffaf2;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        color: var(--ink);
        background: var(--paper);
      }}
      main {{
        width: min(1120px, calc(100% - 32px));
        margin: 0 auto;
        padding: 32px 0 48px;
      }}
      header {{
        display: flex;
        justify-content: space-between;
        gap: 24px;
        align-items: end;
        border-bottom: 1px solid var(--line);
        padding-bottom: 20px;
      }}
      h1 {{ margin: 0; font-size: 34px; line-height: 1.08; }}
      p {{ margin: 8px 0 0; color: #536067; }}
      .grid {{
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 12px;
        margin: 24px 0;
      }}
      .metric {{
        background: var(--soft);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 16px;
      }}
      .metric strong {{ display: block; font-size: 28px; }}
      .metric span {{ color: #5d696f; font-size: 13px; }}
      .toolbar {{
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-bottom: 14px;
      }}
      button {{
        border: 1px solid var(--line);
        background: #fffdf8;
        color: var(--ink);
        border-radius: 999px;
        padding: 8px 12px;
        font-weight: 700;
      }}
      button.primary {{ background: var(--brand); color: white; border-color: var(--brand); }}
      table {{
        width: 100%;
        border-collapse: collapse;
        background: #fffdf8;
        border: 1px solid var(--line);
        border-radius: 8px;
        overflow: hidden;
      }}
      th, td {{
        padding: 13px 14px;
        text-align: left;
        border-bottom: 1px solid var(--line);
        vertical-align: top;
      }}
      th {{ font-size: 12px; color: #5d696f; text-transform: uppercase; background: #f1ece3; }}
      tr:last-child td {{ border-bottom: 0; }}
      .status {{
        display: inline-block;
        border-radius: 999px;
        padding: 4px 8px;
        font-size: 12px;
        font-weight: 800;
        background: #e6efe8;
        color: var(--ok);
      }}
      .status.warn {{ background: #fff0df; color: var(--warn); }}
      .status.new {{ background: #e8f1f2; color: var(--brand); }}
      .note {{
        margin-top: 18px;
        padding: 14px 16px;
        border-left: 4px solid var(--accent);
        background: #fff7ec;
      }}
      @media (max-width: 760px) {{
        header {{ display: block; }}
        .grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
        table, thead, tbody, tr, th, td {{ display: block; }}
        thead {{ display: none; }}
        tr {{ border-bottom: 1px solid var(--line); }}
        td {{ border-bottom: 0; padding: 9px 14px; }}
        td::before {{ content: attr(data-label); display: block; font-size: 11px; color: #68747a; text-transform: uppercase; }}
      }}
    </style>
  </head>
  <body>
    <main>
      <header>
        <div>
          <h1>Reservation Inbox</h1>
          <p>Static dashboard mockup for aggregating website, phone, email, and booking inquiries.</p>
        </div>
        <p>{niche_label} back office</p>
      </header>
      <section class="grid" aria-label="Inquiry metrics">
        <div class="metric"><strong>12</strong><span>new this week</span></div>
        <div class="metric"><strong>4</strong><span>need availability check</span></div>
        <div class="metric"><strong>7h</strong><span>average first response</span></div>
        <div class="metric"><strong>3</strong><span>follow-ups due</span></div>
      </section>
      <div class="toolbar" aria-label="Filters">
        <button class="primary">All active</button>
        <button>New</button>
        <button>Availability check</button>
        <button>Follow-up due</button>
      </div>
      <table>
        <thead>
          <tr>
            <th>Lead</th>
            <th>Source</th>
            <th>Request</th>
            <th>Status</th>
            <th>Next action</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td data-label="Lead">TH-2026-0001<br />Aoki Hana</td>
            <td data-label="Source">website form</td>
            <td data-label="Request">Aug 12-14, 2 guests, ocean view twin</td>
            <td data-label="Status"><span class="status new">new</span></td>
            <td data-label="Next action">Check availability by 13:00</td>
          </tr>
          <tr>
            <td data-label="Lead">TH-2026-0002<br />Miller Group</td>
            <td data-label="Source">email</td>
            <td data-label="Request">Group stay, 8 guests, parking question</td>
            <td data-label="Status"><span class="status warn">needs-info</span></td>
            <td data-label="Next action">Ask room split and arrival time</td>
          </tr>
          <tr>
            <td data-label="Lead">TH-2026-0003<br />Tanaka Ren</td>
            <td data-label="Source">phone note</td>
            <td data-label="Request">Weekend stay, flexible dates</td>
            <td data-label="Status"><span class="status">quoted</span></td>
            <td data-label="Next action">Follow up tomorrow morning</td>
          </tr>
        </tbody>
      </table>
      <div class="note">
        Human approval is required before final booking confirmation, price exceptions, or policy changes.
      </div>
    </main>
  </body>
</html>
"""


def _render_website_side_hustle_rules(payload: dict) -> str:
    return "\n".join(
        [
            "# Originality And License Rules",
            "",
            "1. Never ship a direct competitor clone.",
            "2. Never reuse third-party logos, photos, or protected copy without permission.",
            "3. Verify the source license before copying code into a commercial job.",
            "4. Prefer learning from the pattern and re-implementing it when license scope is unclear.",
            "5. Keep a record of which public sources influenced the build.",
            "6. Treat AI image generation as draft art unless the client approves the rights and usage policy.",
            "7. Keep promises narrow: site design and implementation, not guaranteed sales.",
            "",
        ]
    )


def _render_website_side_hustle_delivery_checklist(payload: dict) -> str:
    return "\n".join(
        [
            "# Delivery Checklist",
            "",
            "- [ ] Desktop and mobile checked in a browser",
            "- [ ] No horizontal scroll",
            "- [ ] CTA visible in first viewport",
            "- [ ] Contact, address, map, hours, or booking path confirmed",
            "- [ ] Images load and are rights-safe",
            "- [ ] Client copy and policies reviewed",
            "- [ ] SEO title and description set",
            "- [ ] Favicon, OGP, and footer reviewed if included",
            "- [ ] Deployment target agreed",
            "- [ ] Handoff notes written: how to edit text, images, contact info",
            "",
        ]
    )


def _render_website_side_hustle_acceptance_checklist(payload: dict) -> str:
    return "\n".join(
        [
            "# Delivery Acceptance Checklist",
            "",
            "Use this with the client before launch or handoff. It turns a vague review into visible yes/no decisions.",
            "",
            "## Website Review",
            "",
            "- [ ] The first screen clearly says what the business offers.",
            "- [ ] The main CTA goes to the approved contact, form, booking, phone, LINE, or email destination.",
            "- [ ] The business name, location, hours, prices, service area, and policies are correct.",
            "- [ ] Photos, logo, reviews, credentials, and claims are approved for public use.",
            "- [ ] The site was checked on a phone and a desktop browser.",
            "",
            "## Inquiry Workflow Review",
            "",
            "- [ ] Test inquiry reaches the chosen inbox, sheet, form backend, or dashboard.",
            "- [ ] Required fields are understandable to a real customer.",
            "- [ ] Status names are understood by the person who will check inquiries.",
            "- [ ] Response templates are approved as drafts, not automatic final replies.",
            "- [ ] Spam, duplicates, urgent cases, and missing information have a manual handling rule.",
            "",
            "## Human Approval",
            "",
            "Human approval is required before any real-world commitment or account change.",
            "- [ ] A human approves public launch.",
            "- [ ] A human approves booking confirmation, price changes, cancellation/refund exceptions, and policy exceptions.",
            "- [ ] A human owns production email, SMS, LINE, CRM, payment, and cloud account changes.",
            "- [ ] No API keys, passwords, or private customer records are included in the delivered demo files.",
            "",
            "## Sign-Off",
            "",
            "- Client approver:",
            "- Operator:",
            "- Launch decision: approve / revise / pause",
            "- Remaining fixes:",
            "- Next review date:",
            "",
        ]
    )


def _render_website_side_hustle_client_handoff(payload: dict) -> str:
    return "\n".join(
        [
            "# Client Handoff Note",
            "",
            "This note is for the business owner or staff member who will use the website and inquiry workflow after delivery.",
            "",
            "## What the client receives",
            "",
            "- A website or sample site structure that can be edited for the business.",
            "- A clear contact or booking path.",
            "- An inquiry intake schema that explains which information should be collected.",
            "- A reservation or lead pipeline with status names.",
            "- Response templates that can be reviewed before sending.",
            "- A simple dashboard or spreadsheet-style view for daily checks.",
            "- A maintenance plan for updates after launch.",
            "",
            "## What to do every business day",
            "",
            "1. Open the inquiry destination.",
            "2. Review new inquiries first.",
            "3. Mark spam or duplicates.",
            "4. Fill missing information if it is already known.",
            "5. Ask the responsible person to confirm availability, price, or policy exceptions.",
            "6. Review the drafted reply.",
            "7. Send the reply from the approved account.",
            "8. Update the status and next action date.",
            "",
            "## What to ask the builder to change",
            "",
            "- Text, photos, prices, hours, contact destinations, map links, or booking links changed.",
            "- Customers keep asking the same question.",
            "- Staff do not understand a status or daily step.",
            "- Too many inquiries arrive without required information.",
            "- A new service, room, area, campaign, or policy needs to be added.",
            "",
            "## Safety boundaries",
            "",
            "The system can organize information and prepare drafts. The business still approves public claims, bookings, prices, refunds, policy exceptions, account settings, and legal or privacy decisions.",
            "",
        ]
    )


def _render_website_side_hustle_accessibility_seo(payload: dict) -> str:
    return "\n".join(
        [
            "# Accessibility And SEO Checklist",
            "",
            "Accessibility:",
            "- [ ] One clear H1",
            "- [ ] Labels on forms and contact inputs",
            "- [ ] Focus states visible",
            "- [ ] Contrast checked for body text and buttons",
            "- [ ] Images have alt text when informative",
            "",
            "SEO and local trust:",
            "- [ ] Title tag names the business and offer",
            "- [ ] Meta description is specific and truthful",
            "- [ ] Heading structure is readable",
            "- [ ] Address, phone, hours, and service area are consistent",
            "- [ ] Add structured data only for facts the client can support",
            "",
        ]
    )


def _render_website_side_hustle_proposal(payload: dict) -> str:
    vertical = payload["niche"].replace("-", " ")
    return "\n".join(
        [
            f"# Proposal One Pager: {vertical.title()} Website",
            "",
            "## Scope",
            "",
            "One original homepage or small brochure site built from approved client facts, with mobile-responsive layout, contact or booking CTA, and browser-tested delivery.",
            "",
            "## Included",
            "",
            "- Client brief and content collection",
            "- Homepage structure and design direction",
            "- Original implementation using public, commercial-friendly references",
            "- Reservation and inquiry intake structure with manual approval boundaries",
            "- Browser QA and handoff notes",
            "",
            "## Not Included",
            "",
            "- Guaranteed rankings or sales",
            "- Fully custom back-office software",
            "- Automated booking confirmation or payment handling",
            "- Unlicensed stock libraries or competitor cloning",
            "- Ongoing ad management",
            "",
            "## Delivery Standard",
            "",
            "The site is reviewed on desktop and mobile, with visible CTA, stable layout, and documented content ownership boundaries.",
            "",
        ]
    )


def _render_website_side_hustle_pricing(payload: dict) -> str:
    return "\n".join(
        [
            "# Pricing Menu",
            "",
            "| Offer | Scope | Typical beginner range |",
            "|---|---|---|",
            "| Starter page | One homepage, basic contact CTA, simple copy shaping | JPY 30,000-60,000 |",
            "| Standard brochure site | Homepage plus 3-5 sections or pages, stronger trust content | JPY 80,000-180,000 |",
            "| Premium launch pack | Brochure site, copy workshop, SEO basics, launch checklist, one revision cycle | JPY 180,000-350,000 |",
            "| Inquiry operations add-on | intake schema, status pipeline, response templates, simple dashboard mockup | JPY 50,000-150,000 |",
            "| Monthly care | text swaps, image updates, basic monitoring, small fixes | JPY 10,000-30,000 / month |",
            "",
            "Price with boundaries. Say what is included, what is not, and what triggers a new quote.",
            "",
        ]
    )


def _render_website_side_hustle_maintenance(payload: dict) -> str:
    return "\n".join(
        [
            "# Maintenance Plan",
            "",
            "Monthly care can include:",
            "- text, prices, hours, and CTA updates",
            "- one small section refresh",
            "- link and contact checks",
            "- inquiry table and follow-up rule review",
            "- uptime or render spot checks",
            "- image swaps supplied by the client",
            "",
            "Do not include unlimited redesign work in a low-cost retainer.",
            "",
        ]
    )


def _render_website_side_hustle_outreach(payload: dict) -> str:
    niche = payload["niche"].replace("-", " ")
    return "\n".join(
        [
            "# Outreach Messages",
            "",
            "Subject: Small website refresh idea for your business",
            "",
            f"I build original small-business websites for niches like {niche} using a faster AI-assisted workflow plus human review checklists.",
            "",
            "If your current site feels outdated, hard to update, or unclear on mobile, I can start with a small homepage refresh proposal and a browser-ready mockup before any larger build.",
            "",
            "I do not clone competitor sites and I keep the first scope narrow so you can review the result safely.",
            "",
        ]
    )


def _render_website_side_hustle_launch(payload: dict) -> str:
    return "\n".join(
        [
            "# Launch Checklist",
            "",
            "- [ ] Domain and hosting owner confirmed",
            "- [ ] Analytics decision confirmed or intentionally skipped",
            "- [ ] Contact destination tested",
            "- [ ] Legal pages reviewed if needed",
            "- [ ] Backup copy of final files kept",
            "- [ ] Client knows how to request edits",
            "- [ ] Post-launch review date scheduled",
            "",
        ]
    )


def _render_website_side_hustle_sample_site(payload: dict) -> str:
    niche_label = payload["niche"].replace("-", " ").title()
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Harbor Light Stay | Sample {html.escape(niche_label)} Website</title>
    <meta name="description" content="Sample small-business website generated by the Website Side Hustle Pack." />
    <style>
      :root {{
        --ink: #172226;
        --paper: #f6f1e8;
        --sea: #184d52;
        --foam: #dcebe9;
        --accent: #d77f61;
        --line: rgba(23, 34, 38, 0.14);
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        font-family: Georgia, "Times New Roman", serif;
        color: var(--ink);
        background: linear-gradient(180deg, #f7f2ea 0%, #eef7f6 48%, #f7f2ea 100%);
      }}
      .hero {{
        min-height: 88vh;
        padding: 28px;
        display: grid;
        align-items: end;
        background:
          linear-gradient(120deg, rgba(24, 77, 82, 0.82), rgba(24, 77, 82, 0.18) 58%, rgba(24, 77, 82, 0.04)),
          radial-gradient(circle at top right, rgba(255,255,255,0.5), transparent 30%),
          linear-gradient(135deg, #7da6a1, #d8cfbf 55%, #355d61);
        color: #fffaf3;
      }}
      .hero-inner {{
        max-width: 1120px;
        width: 100%;
        margin: 0 auto;
        display: grid;
        gap: 24px;
      }}
      h1, h2, p {{ margin: 0; }}
      h1 {{
        max-width: 760px;
        font-size: clamp(3rem, 8vw, 6rem);
        line-height: 0.95;
        font-weight: 500;
      }}
      .hero p {{
        max-width: 580px;
        font-family: "Hiragino Sans", "Yu Gothic", sans-serif;
        font-size: 1.05rem;
        line-height: 1.8;
      }}
      .actions {{
        display: flex;
        flex-wrap: wrap;
        gap: 14px;
        margin-top: 12px;
      }}
      .button {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 50px;
        padding: 0 22px;
        border-radius: 999px;
        text-decoration: none;
        font-family: "Hiragino Sans", "Yu Gothic", sans-serif;
        font-weight: 700;
      }}
      .button.primary {{ background: var(--accent); color: #fffaf3; }}
      .button.secondary {{ border: 1px solid rgba(255,255,255,0.45); color: #fffaf3; }}
      main {{ max-width: 1120px; margin: 0 auto; padding: 72px 28px 96px; }}
      .grid {{ display: grid; gap: 18px; }}
      .intro {{ grid-template-columns: 1.15fr 0.85fr; align-items: start; }}
      .panel {{
        padding: 24px;
        border: 1px solid var(--line);
        border-radius: 8px;
        background: rgba(255, 250, 243, 0.72);
      }}
      .stats strong {{
        display: block;
        color: var(--sea);
        font-size: 2.2rem;
      }}
      .sections {{ margin-top: 46px; grid-template-columns: repeat(3, minmax(0, 1fr)); }}
      .section-card {{
        min-height: 220px;
        display: grid;
        align-content: end;
        padding: 24px;
        background: linear-gradient(160deg, rgba(24,77,82,0.16), rgba(24,77,82,0.78));
        color: #fffaf3;
        border-radius: 8px;
      }}
      .section-card p {{ font-family: "Hiragino Sans", "Yu Gothic", sans-serif; margin-top: 10px; line-height: 1.7; }}
      @media (max-width: 840px) {{
        .intro, .sections {{ grid-template-columns: 1fr; }}
      }}
    </style>
  </head>
  <body>
    <section class="hero">
      <div class="hero-inner">
        <div>
          <p style="font-family: 'Hiragino Sans', 'Yu Gothic', sans-serif; letter-spacing: .16em; text-transform: uppercase;">Sample Website Side Hustle Demo</p>
          <h1>Quiet hospitality, designed to convert on mobile.</h1>
        </div>
        <p>Use this sample as a starting point for a tourism-hotel or villa homepage: strong first viewport, direct booking CTA, visible trust, and section rhythm without heavy framework requirements.</p>
        <div class="actions">
          <a class="button primary" href="#">Primary CTA</a>
          <a class="button secondary" href="#">See Rooms</a>
        </div>
      </div>
    </section>
    <main>
      <section class="grid intro">
        <div class="panel">
          <h2 style="font-size: clamp(2.2rem, 6vw, 4rem); line-height: 1.02;">This sample exists to show structure, not fake prestige.</h2>
          <p style="font-family: 'Hiragino Sans', 'Yu Gothic', sans-serif; margin-top: 18px; line-height: 1.8;">Swap in real photos, verified amenities, pricing ranges, and local proof before sending to a client. Keep the page original and fact-based.</p>
        </div>
        <div class="panel stats">
          <strong>3</strong><span>core offers or room types</span>
          <strong>1</strong><span>clear mobile-first CTA</span>
          <strong>0</strong><span>competitor clone permission</span>
        </div>
      </section>
      <section class="grid sections">
        <article class="section-card">
          <h2>Offer</h2>
          <p>Show the room, service, or package in plain language.</p>
        </article>
        <article class="section-card">
          <h2>Trust</h2>
          <p>Use reviews, staff names, map, and policy facts to reduce hesitation.</p>
        </article>
        <article class="section-card">
          <h2>CTA</h2>
          <p>Phone, booking, quote, or contact. One next step, visible above the fold.</p>
        </article>
      </section>
    </main>
  </body>
</html>
"""
