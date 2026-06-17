from __future__ import annotations

import csv
import io


def build_run_summary(candidates: list[dict], shortlist: list[dict], business_area: str | None = None) -> dict:
    status = "ready_for_adapter" if shortlist else "manual_review_required" if candidates else "query_recovery_required"
    next_read = (
        "adapter_starter/README.md"
        if shortlist
        else "manual_review_pack.md"
        if candidates
        else "query_recovery.md"
    )
    top_candidate = shortlist[0] if shortlist else candidates[0] if candidates else {}
    return {
        "status": status,
        "business_area": business_area or (top_candidate.get("business_area") if top_candidate else "general"),
        "candidate_count": len(candidates),
        "ready_candidate_count": len(shortlist),
        "next_read": next_read,
        "top_candidate": {
            "full_name": top_candidate.get("full_name", ""),
            "score": top_candidate.get("score", 0),
            "production_gate": top_candidate.get("production_gate", ""),
            "license_risk": top_candidate.get("license_risk", ""),
            "recommended_next_step": top_candidate.get("recommended_next_step", ""),
        },
    }


def render_run_summary(summary: dict) -> str:
    top_candidate = summary.get("top_candidate") or {}
    lines = [
        "# GitHub Discovery Run Summary",
        "",
        f"- Status: `{summary['status']}`",
        f"- Business area: `{summary['business_area']}`",
        f"- Candidates reviewed: `{summary['candidate_count']}`",
        f"- Ready adapter candidates: `{summary['ready_candidate_count']}`",
        f"- Next read: `{summary['next_read']}`",
        "",
        "## Top Candidate",
        "",
    ]
    if top_candidate.get("full_name"):
        lines.extend(
            [
                f"- Repository: `{top_candidate['full_name']}`",
                f"- Score: `{top_candidate['score']}`",
                f"- Gate: `{top_candidate['production_gate']}`",
                f"- License risk: `{top_candidate['license_risk']}`",
                f"- Next step: {top_candidate['recommended_next_step']}",
                "",
            ]
        )
    else:
        lines.extend(["- No candidates were found.", ""])
    return "\n".join(lines)


def build_manual_review_pack(candidates: list[dict], business_area: str | None = None) -> dict:
    area = business_area or candidates[0].get("business_area") or "general"
    return {
        "status": "manual_review_required",
        "business_area": area,
        "candidate_count": len(candidates),
        "reason": "No candidate met the ready_for_adapter gate.",
        "next_actions": [
            "Review license obligations for the highest-scoring candidate before any code reuse.",
            "Inspect README, examples, recent commits, and open issues for the top three candidates.",
            "Use candidates as workflow references only until legal and maintenance risks are cleared.",
            "Rerun discovery with broader terms if all candidates remain blocked after review.",
        ],
        "candidates": candidates[:5],
    }


def build_enterprise_readiness(summary: dict, candidates: list[dict], shortlist: list[dict]) -> dict:
    decision = "prototype_allowed" if shortlist else "review_only" if candidates else "query_recovery_required"
    evidence_files = ["run_summary.md", "artifact_index.md", "github_candidates.md"]
    if shortlist:
        evidence_files.extend(["adoption_shortlist.md", "adapter_blueprint.md", "adapter_starter/README.md"])
    elif candidates:
        evidence_files.append("manual_review_pack.md")
    else:
        evidence_files.append("query_recovery.md")

    return {
        "decision": decision,
        "production_release": "blocked_until_controls_complete",
        "business_area": summary.get("business_area", "general"),
        "candidate_count": summary.get("candidate_count", len(candidates)),
        "ready_candidate_count": summary.get("ready_candidate_count", len(shortlist)),
        "next_read": summary.get("next_read", evidence_files[-1]),
        "required_controls": [
            {
                "control": "license_review",
                "status": "required",
                "evidence": "Confirm third-party license obligations before code reuse or production rollout.",
            },
            {
                "control": "dry_run_first",
                "status": "required",
                "evidence": "Run synthetic-data dry-run before touching customer data or external systems.",
            },
            {
                "control": "human_approval",
                "status": "required",
                "evidence": "Capture workflow-owner approval before production execution.",
            },
            {
                "control": "audit_log",
                "status": "required",
                "evidence": "Keep run logs, inputs, outputs, approvals, errors, and rollback notes.",
            },
            {
                "control": "secret_review",
                "status": "required",
                "evidence": "Confirm no secrets are committed and production credentials are isolated.",
            },
        ],
        "evidence_files": evidence_files,
    }


def render_enterprise_readiness(readiness: dict) -> str:
    lines = [
        "# Enterprise Readiness",
        "",
        f"- Decision: `{readiness['decision']}`",
        f"- Production release: `{readiness['production_release']}`",
        f"- Business area: `{readiness['business_area']}`",
        f"- Candidates reviewed: `{readiness['candidate_count']}`",
        f"- Ready adapter candidates: `{readiness['ready_candidate_count']}`",
        f"- Next read: `{readiness['next_read']}`",
        "",
        "## Required Controls",
        "",
    ]
    for control in readiness["required_controls"]:
        lines.append(f"- `{control['control']}` ({control['status']}): {control['evidence']}")
    lines.extend(["", "## Evidence Files", ""])
    lines.extend(f"- `{path}`" for path in readiness["evidence_files"])
    lines.append("")
    return "\n".join(lines)


def build_executive_decision_brief(summary: dict, candidates: list[dict], shortlist: list[dict]) -> dict:
    top_candidate = shortlist[0] if shortlist else candidates[0] if candidates else {}
    business_area = summary.get("business_area") or top_candidate.get("business_area") or "general"
    if not top_candidate:
        return {
            "decision": "do_not_fund_implementation_yet",
            "business_area": business_area,
            "primary_candidate": "",
            "executive_summary": "Discovery did not return a reviewable candidate, so implementation spend should wait.",
            "investment_case": {
                "pilot_scope": "discovery recovery only",
                "expected_return_signals": [
                    "at least one reviewable candidate with clear license, examples, and recent maintenance",
                    "explicit rejection reasons for weak candidates",
                ],
                "cost_control": "limit work to another discovery batch before any adapter or integration build",
            },
            "board_level_risks": [
                {
                    "risk": "funding_without_candidate_evidence",
                    "mitigation": "approve discovery recovery only and require run_summary.md before implementation planning",
                }
            ],
            "approval_request": {
                "decision_needed": "approve another discovery batch",
                "approvers": ["process_owner"],
                "evidence": ["query_recovery.md", "run_summary.md"],
            },
        }

    pilot_allowed = bool(shortlist)
    decision = "approve_controlled_pilot" if pilot_allowed else "hold_for_manual_review"
    pilot_scope = f"one narrow {business_area} workflow"
    return {
        "decision": decision,
        "business_area": business_area,
        "primary_candidate": top_candidate.get("full_name", ""),
        "executive_summary": (
            f"Use {top_candidate.get('full_name', 'the top candidate')} to test a controlled {business_area} automation pilot."
            if pilot_allowed
            else "A candidate exists, but license, maintenance, or fit review must clear before pilot funding."
        ),
        "investment_case": {
            "pilot_scope": pilot_scope,
            "expected_return_signals": [
                "manual handoffs reduced by 30% or more",
                "median cycle time reduced by 25% or more",
                "100% of promoted actions include approval evidence",
            ],
            "cost_control": "timebox the pilot to 30 days with synthetic data first and no unapproved external actions",
        },
        "board_level_risks": [
            {
                "risk": "automation_without_controls",
                "mitigation": "block production until enterprise_readiness.md controls and risk_exception_register.md are closed",
            },
            {
                "risk": "unclear_reuse_rights",
                "mitigation": "complete license review before copying code or distributing an adapter",
            },
            {
                "risk": "measured_value_not_visible",
                "mitigation": "require value_measurement_report.md before expanding the pilot",
            },
        ],
        "approval_request": {
            "decision_needed": "approve a 30-day controlled pilot" if pilot_allowed else "approve manual review before pilot",
            "approvers": ["executive_sponsor", "process_owner", "security_owner"],
            "evidence": [
                "value_realization_plan.md",
                "value_measurement_report.md",
                "enterprise_readiness.md",
                "risk_exception_register.md",
            ],
        },
    }


def render_executive_decision_brief(brief: dict) -> str:
    lines = [
        "# Executive Decision Brief",
        "",
        f"- Decision: `{brief['decision']}`",
        f"- Business area: `{brief['business_area']}`",
        f"- Primary candidate: `{brief['primary_candidate']}`",
        f"- Summary: {brief['executive_summary']}",
        "",
        "## Investment Case",
        "",
        f"- Pilot scope: {brief['investment_case']['pilot_scope']}",
        f"- Cost control: {brief['investment_case']['cost_control']}",
        "",
        "### Expected Return Signals",
        "",
    ]
    lines.extend(f"- {item}" for item in brief["investment_case"]["expected_return_signals"])
    lines.extend(["", "## Board-Level Risks", ""])
    for item in brief["board_level_risks"]:
        lines.append(f"- `{item['risk']}`: {item['mitigation']}")
    request = brief["approval_request"]
    lines.extend(
        [
            "",
            "## Approval Request",
            "",
            f"- Decision needed: {request['decision_needed']}",
            f"- Approvers: {', '.join(f'`{approver}`' for approver in request['approvers'])}",
            "- Evidence:",
        ]
    )
    lines.extend(f"  - `{item}`" for item in request["evidence"])
    lines.append("")
    return "\n".join(lines)


def build_value_realization_plan(summary: dict, candidates: list[dict], shortlist: list[dict]) -> dict:
    top_candidate = shortlist[0] if shortlist else candidates[0] if candidates else {}
    business_area = summary.get("business_area") or top_candidate.get("business_area") or "general"
    if not top_candidate:
        return {
            "status": "discovery_recovery",
            "business_area": business_area,
            "primary_workflow": {
                "candidate": "",
                "use_case": "Recover search quality before estimating automation value.",
                "decision": "broaden_discovery",
            },
            "value_hypotheses": [
                {
                    "metric": "candidate_quality",
                    "target": "at least one low-risk candidate with clear examples and recent maintenance",
                    "measurement": "rerun discovery and inspect run_summary.md plus github_candidates.md",
                }
            ],
            "measurement_plan": [
                {
                    "baseline": "current candidate search quality",
                    "instrumentation": "query_recovery.md and github_searches.json",
                    "review_cadence": "after each query batch",
                }
            ],
            "rollout_plan": [
                {
                    "phase": "days_0_30",
                    "goal": "Recover candidate discovery with broader queries and stricter manual review.",
                    "exit_evidence": "run_summary.md shows candidates reviewed and enterprise_readiness.md is present.",
                }
            ],
            "go_no_go_criteria": [
                "Proceed only if at least one candidate has clear license, maintenance, examples, and adapter value.",
                "Stop if discovery remains empty after broadening queries and reviewing adjacent business terms.",
            ],
        }

    decision = "prototype_value_test" if shortlist else "manual_value_review"
    return {
        "status": decision,
        "business_area": business_area,
        "primary_workflow": {
            "candidate": top_candidate.get("full_name", ""),
            "use_case": top_candidate.get("business_use_case") or f"Evaluate {top_candidate.get('full_name', 'the candidate')} for {business_area} automation.",
            "decision": "run_controlled_pilot" if shortlist else "review_before_pilot",
        },
        "value_hypotheses": [
            {
                "metric": "manual_handoffs_reduced",
                "target": "reduce avoidable handoffs in the selected workflow by 30% or more",
                "measurement": "compare handoff count per workflow run before and after dry-run prototype",
            },
            {
                "metric": "cycle_time_saved",
                "target": "reduce time from request to reviewed output by 25% or more",
                "measurement": "capture timestamps in run logs for baseline and prototype runs",
            },
            {
                "metric": "approval_quality",
                "target": "100% of promoted actions include owner approval and rollback notes",
                "measurement": "sample approval_request, run_log, and rollback_notes artifacts",
            },
        ],
        "measurement_plan": [
            {
                "baseline": "current manual process",
                "instrumentation": "count handoffs, cycle time, rework, approval delays, and exception rate for 10 recent cases",
                "review_cadence": "weekly during pilot",
            },
            {
                "baseline": "synthetic dry-run prototype",
                "instrumentation": "record proposed actions, approvals, rejected actions, errors, and operator feedback",
                "review_cadence": "after each pilot batch",
            },
        ],
        "rollout_plan": [
            {
                "phase": "days_0_30",
                "goal": "Run a synthetic-data pilot for one narrow workflow and confirm value hypotheses.",
                "exit_evidence": "run logs, owner approval, rollback notes, and measured baseline comparison.",
            },
            {
                "phase": "days_31_60",
                "goal": "Connect one internal data source behind dry-run mode and validate exception handling.",
                "exit_evidence": "zero unapproved external actions and documented failure cases.",
            },
            {
                "phase": "days_61_90",
                "goal": "Promote only the smallest safe workflow slice after controls are complete.",
                "exit_evidence": "enterprise_readiness.md controls completed and go/no-go review signed off.",
            },
        ],
        "go_no_go_criteria": [
            "Proceed only if measured time saved or handoff reduction is visible without weakening approvals.",
            "Proceed only if license review, dry-run evidence, audit logging, and rollback notes are complete.",
            "Stop if operators cannot explain or review proposed actions reliably.",
        ],
    }


def render_value_realization_plan(plan: dict) -> str:
    workflow = plan["primary_workflow"]
    lines = [
        "# Value Realization Plan",
        "",
        f"- Status: `{plan['status']}`",
        f"- Business area: `{plan['business_area']}`",
        f"- Primary candidate: `{workflow['candidate']}`",
        f"- Decision: `{workflow['decision']}`",
        f"- Use case: {workflow['use_case']}",
        "",
        "## Value Hypotheses",
        "",
    ]
    for item in plan["value_hypotheses"]:
        lines.append(f"- `{item['metric']}`: target {item['target']}; measure by {item['measurement']}.")
    lines.extend(["", "## Measurement Plan", ""])
    for item in plan["measurement_plan"]:
        lines.append(f"- Baseline `{item['baseline']}`: {item['instrumentation']} Review cadence: {item['review_cadence']}.")
    lines.extend(["", "## Rollout Plan", ""])
    for item in plan["rollout_plan"]:
        lines.append(f"- `{item['phase']}`: {item['goal']} Exit evidence: {item['exit_evidence']}")
    lines.extend(["", "## Go/No-Go Criteria", ""])
    lines.extend(f"- {item}" for item in plan["go_no_go_criteria"])
    lines.append("")
    return "\n".join(lines)


def build_stakeholder_rollout_map(summary: dict, candidates: list[dict], shortlist: list[dict]) -> dict:
    top_candidate = shortlist[0] if shortlist else candidates[0] if candidates else {}
    business_area = summary.get("business_area") or top_candidate.get("business_area") or "general"
    if not top_candidate:
        return {
            "status": "discovery_governance",
            "business_area": business_area,
            "primary_candidate": "",
            "roles": [
                {
                    "role": "process_owner",
                    "accountable_for": "workflow pain definition and candidate acceptance criteria",
                    "first_action": "Review query_recovery.md and approve broader discovery terms.",
                },
                {
                    "role": "technical_reviewer",
                    "accountable_for": "repository search quality and reuse feasibility",
                    "first_action": "Rerun discovery and inspect candidate metadata before implementation starts.",
                },
                {
                    "role": "security_owner",
                    "accountable_for": "data boundary, secret handling, and dry-run requirements",
                    "first_action": "Confirm recovery searches do not imply production system access.",
                },
            ],
            "approval_matrix": [
                {
                    "decision": "search_recovery_start",
                    "required_approvers": ["process_owner"],
                    "evidence": "query_recovery.md and value_realization_plan.md",
                }
            ],
            "operating_cadence": [
                {
                    "cadence": "after each query batch",
                    "owner": "technical_reviewer",
                    "review": "candidate count, license clarity, maintenance activity, and automation fit",
                }
            ],
            "escalation_rules": [
                "Escalate to security_owner before collecting private data or credentials.",
                "Stop discovery if no candidate has clear usage evidence after three broader query batches.",
            ],
        }

    return {
        "status": "prototype_governance" if shortlist else "manual_review_governance",
        "business_area": business_area,
        "primary_candidate": top_candidate.get("full_name", ""),
        "roles": [
            {
                "role": "executive_sponsor",
                "accountable_for": "business outcome and adoption funding",
                "first_action": "Confirm the value hypothesis and approve the pilot timebox.",
            },
            {
                "role": "process_owner",
                "accountable_for": "workflow scope, operator acceptance, and go/no-go recommendation",
                "first_action": "Approve the narrow workflow slice and baseline measurement plan.",
            },
            {
                "role": "automation_operator",
                "accountable_for": "dry-run execution, exception handling, and run-log quality",
                "first_action": "Run adapter_starter/smoke_test.py or the manual review checklist.",
            },
            {
                "role": "human_reviewer",
                "accountable_for": "approval decisions before external action or production promotion",
                "first_action": "Review proposed actions and record approval or rejection reason.",
            },
            {
                "role": "security_owner",
                "accountable_for": "data boundary, secrets, audit logs, and rollback evidence",
                "first_action": "Verify dry-run isolation and credential handling before pilot execution.",
            },
            {
                "role": "legal_owner",
                "accountable_for": "license obligations and third-party reuse limits",
                "first_action": "Review license metadata and README obligations before code reuse.",
            },
        ],
        "approval_matrix": [
            {
                "decision": "prototype_start",
                "required_approvers": ["process_owner", "security_owner"],
                "evidence": "value_realization_plan.md, enterprise_readiness.md, and adapter_starter/smoke_test.py",
            },
            {
                "decision": "pilot_with_internal_data",
                "required_approvers": ["process_owner", "security_owner", "legal_owner"],
                "evidence": "license review, dry-run logs, audit log, and rollback notes",
            },
            {
                "decision": "production_promotion",
                "required_approvers": ["executive_sponsor", "process_owner", "security_owner"],
                "evidence": "go/no-go criteria met, measured value, and completed enterprise readiness controls",
            },
        ],
        "operating_cadence": [
            {
                "cadence": "weekly",
                "owner": "process_owner",
                "review": "value metrics, exceptions, rejected actions, and operator feedback",
            },
            {
                "cadence": "per run",
                "owner": "automation_operator",
                "review": "inputs, proposed actions, approvals, errors, and rollback readiness",
            },
            {
                "cadence": "before each promotion",
                "owner": "security_owner",
                "review": "data access, secret isolation, audit evidence, and unresolved risks",
            },
        ],
        "escalation_rules": [
            "Escalate to legal_owner if license metadata is missing, restrictive, or unclear.",
            "Escalate to security_owner if the adapter needs private data, credentials, or external write actions.",
            "Stop rollout if human reviewers cannot explain or confidently reject proposed actions.",
        ],
    }


def render_stakeholder_rollout_map(rollout_map: dict) -> str:
    lines = [
        "# Stakeholder Rollout Map",
        "",
        f"- Status: `{rollout_map['status']}`",
        f"- Business area: `{rollout_map['business_area']}`",
        f"- Primary candidate: `{rollout_map['primary_candidate']}`",
        "",
        "## Roles",
        "",
    ]
    for item in rollout_map["roles"]:
        lines.append(
            f"- `{item['role']}`: accountable for {item['accountable_for']}. First action: {item['first_action']}"
        )
    lines.extend(["", "## Approval Matrix", ""])
    for item in rollout_map["approval_matrix"]:
        approvers = ", ".join(f"`{approver}`" for approver in item["required_approvers"])
        lines.append(f"- `{item['decision']}`: {approvers}. Evidence: {item['evidence']}")
    lines.extend(["", "## Operating Cadence", ""])
    for item in rollout_map["operating_cadence"]:
        lines.append(f"- `{item['cadence']}` by `{item['owner']}`: {item['review']}")
    lines.extend(["", "## Escalation Rules", ""])
    lines.extend(f"- {item}" for item in rollout_map["escalation_rules"])
    lines.append("")
    return "\n".join(lines)


def build_risk_exception_register(summary: dict, candidates: list[dict], shortlist: list[dict]) -> dict:
    top_candidate = shortlist[0] if shortlist else candidates[0] if candidates else {}
    business_area = summary.get("business_area") or top_candidate.get("business_area") or "general"
    exceptions: list[dict] = []

    if not top_candidate:
        exceptions.append(
            {
                "risk": "candidate_discovery_empty",
                "severity": "high",
                "owner": "process_owner",
                "status": "open",
                "evidence_needed": "query_recovery.md shows broader searches and at least one reviewed candidate.",
                "stop_condition": "Do not start implementation until discovery returns a reviewable candidate.",
            }
        )
    elif not shortlist:
        exceptions.append(
            {
                "risk": "prototype_not_allowed",
                "severity": "high",
                "owner": "process_owner",
                "status": "open",
                "evidence_needed": "manual_review_pack.md clears the candidate for controlled prototype work.",
                "stop_condition": "Do not generate or run production-facing adapters for this candidate.",
            }
        )

    if top_candidate and top_candidate.get("license_risk") != "low":
        exceptions.append(
            {
                "risk": "license_review_required",
                "severity": "high",
                "owner": "legal_owner",
                "status": "open",
                "evidence_needed": "Document license obligations, attribution, and allowed reuse scope.",
                "stop_condition": "Do not copy code or promote reuse until legal review is recorded.",
            }
        )

    if top_candidate and _candidate_needs_maintenance_review(top_candidate):
        exceptions.append(
            {
                "risk": "maintenance_review_required",
                "severity": "medium",
                "owner": "technical_reviewer",
                "status": "open",
                "evidence_needed": "Review recent commits, release cadence, open issues, and fork health.",
                "stop_condition": "Do not treat the project as a dependable dependency until maintenance is reviewed.",
            }
        )

    if shortlist:
        exceptions.extend(
            [
                {
                    "risk": "dry_run_evidence_missing",
                    "severity": "high",
                    "owner": "automation_operator",
                    "status": "open",
                    "evidence_needed": "Run adapter_starter/smoke_test.py and record synthetic dry-run output.",
                    "stop_condition": "Do not connect private data or external write actions before dry-run evidence exists.",
                },
                {
                    "risk": "approval_log_missing",
                    "severity": "high",
                    "owner": "human_reviewer",
                    "status": "open",
                    "evidence_needed": "Capture approval, rejection reason, and rollback note for each promoted action.",
                    "stop_condition": "Do not promote actions that lack human review evidence.",
                },
            ]
        )

    status = "pilot_controls_open" if shortlist else "exceptions_open"
    return {
        "status": status,
        "business_area": business_area,
        "primary_candidate": top_candidate.get("full_name", ""),
        "promotion_rule": "Do not promote automation beyond dry-run until every open exception has recorded evidence and owner approval.",
        "exceptions": exceptions,
    }


def render_risk_exception_register(register: dict) -> str:
    lines = [
        "# Risk Exception Register",
        "",
        f"- Status: `{register['status']}`",
        f"- Business area: `{register['business_area']}`",
        f"- Primary candidate: `{register['primary_candidate']}`",
        f"- Promotion rule: {register['promotion_rule']}",
        "",
        "## Open Exceptions",
        "",
    ]
    if register["exceptions"]:
        for item in register["exceptions"]:
            lines.append(
                f"- `{item['risk']}` ({item['severity']}, owner `{item['owner']}`, {item['status']}): "
                f"{item['evidence_needed']} Stop condition: {item['stop_condition']}"
            )
    else:
        lines.append("- No open exceptions recorded.")
    lines.append("")
    return "\n".join(lines)


def build_operational_audit_plan(summary: dict, candidates: list[dict], shortlist: list[dict]) -> dict:
    top_candidate = shortlist[0] if shortlist else candidates[0] if candidates else {}
    business_area = summary.get("business_area") or top_candidate.get("business_area") or "general"
    if not top_candidate:
        return {
            "status": "discovery_audit_required",
            "business_area": business_area,
            "primary_candidate": "",
            "audit_scope": [
                {
                    "area": "query_recovery_trace",
                    "owner": "technical_reviewer",
                    "required_evidence": "empty query, fallback query, result count, inspected candidates, and rejection reason",
                },
                {
                    "area": "business_fit_trace",
                    "owner": "process_owner",
                    "required_evidence": "business area, workflow pain, candidate acceptance criteria, and approved next search batch",
                },
            ],
            "cadence": [
                {
                    "frequency": "per_query_batch",
                    "reviewer": "process_owner",
                    "sample": "all fallback searches until at least one candidate is found",
                }
            ],
            "stop_triggers": [
                "Stop implementation work if no reviewed candidate exists.",
                "Stop discovery if three broader query batches produce no candidate with clear license and maintenance evidence.",
            ],
            "evidence_files": ["query_recovery.md", "value_realization_plan.md", "risk_exception_register.md"],
        }

    return {
        "status": "pilot_audit_required" if shortlist else "manual_review_audit_required",
        "business_area": business_area,
        "primary_candidate": top_candidate.get("full_name", ""),
        "audit_scope": [
            {
                "area": "approval_integrity",
                "owner": "human_reviewer",
                "required_evidence": "approval_request, approval_decision, reviewer, timestamp, rejection reason when applicable",
            },
            {
                "area": "dry_run_integrity",
                "owner": "automation_operator",
                "required_evidence": "synthetic input, proposed output, no external write action, error log, and rollback note",
            },
            {
                "area": "value_measurement",
                "owner": "process_owner",
                "required_evidence": "baseline, prototype run count, handoff count, cycle time, exception rate, and operator feedback",
            },
            {
                "area": "control_completion",
                "owner": "security_owner",
                "required_evidence": "enterprise_readiness.md controls, secret review, audit log path, and unresolved exceptions",
            },
        ],
        "cadence": [
            {
                "frequency": "per_run",
                "reviewer": "automation_operator",
                "sample": "100% of dry-run executions and approval decisions",
            },
            {
                "frequency": "weekly",
                "reviewer": "process_owner",
                "sample": "all exceptions plus at least 10 workflow cases or all cases if fewer than 10",
            },
            {
                "frequency": "before_promotion",
                "reviewer": "security_owner",
                "sample": "all open risks, failed runs, rejected actions, and credential-touching paths",
            },
        ],
        "stop_triggers": [
            "Stop promotion if approval evidence is missing for any action.",
            "Stop promotion if dry-run output cannot be reproduced from recorded inputs.",
            "Stop promotion if measured value cannot be compared with the manual baseline.",
            "Stop promotion if any high-severity exception remains open.",
        ],
        "evidence_files": [
            "value_realization_plan.md",
            "stakeholder_rollout_map.md",
            "risk_exception_register.md",
            "enterprise_readiness.md",
            "adapter_starter/smoke_test.py",
        ],
    }


def render_operational_audit_plan(plan: dict) -> str:
    lines = [
        "# Operational Audit Plan",
        "",
        f"- Status: `{plan['status']}`",
        f"- Business area: `{plan['business_area']}`",
        f"- Primary candidate: `{plan['primary_candidate']}`",
        "",
        "## Audit Scope",
        "",
    ]
    for item in plan["audit_scope"]:
        lines.append(
            f"- `{item['area']}` owned by `{item['owner']}`: {item['required_evidence']}"
        )
    lines.extend(["", "## Cadence", ""])
    for item in plan["cadence"]:
        lines.append(f"- `{item['frequency']}` reviewed by `{item['reviewer']}`: {item['sample']}")
    lines.extend(["", "## Stop Triggers", ""])
    lines.extend(f"- {item}" for item in plan["stop_triggers"])
    lines.extend(["", "## Evidence Files", ""])
    lines.extend(f"- `{item}`" for item in plan["evidence_files"])
    lines.append("")
    return "\n".join(lines)


def build_value_measurement_report(summary: dict, candidates: list[dict], shortlist: list[dict]) -> dict:
    top_candidate = shortlist[0] if shortlist else candidates[0] if candidates else {}
    business_area = summary.get("business_area") or top_candidate.get("business_area") or "general"
    if not top_candidate:
        return {
            "status": "discovery_measurement_required",
            "business_area": business_area,
            "primary_candidate": "",
            "metric_cards": [
                {
                    "metric": "candidate_quality",
                    "baseline_required": "empty_query_count",
                    "pilot_required": "reviewable_candidate_count",
                    "target": "at least one candidate with clear license, examples, recent maintenance, and automation fit",
                },
                {
                    "metric": "search_precision",
                    "baseline_required": "queries_without_candidates",
                    "pilot_required": "candidates_rejected_with_reason",
                    "target": "every query batch has explicit accept or reject rationale",
                },
            ],
            "decision_thresholds": [
                "Continue discovery only if broader searches produce at least one reviewable candidate.",
                "Stop implementation planning if candidate quality remains unmeasurable after three query batches.",
            ],
            "required_inputs": ["query_recovery.md", "github_searches.json", "run_summary.md"],
        }

    return {
        "status": "pilot_measurement_required" if shortlist else "manual_measurement_required",
        "business_area": business_area,
        "primary_candidate": top_candidate.get("full_name", ""),
        "metric_cards": [
            {
                "metric": "manual_handoffs_reduced",
                "baseline_required": "handoff_count_per_case",
                "pilot_required": "prototype_handoff_count_per_case",
                "target": "30% or greater reduction without removing required approvals",
            },
            {
                "metric": "cycle_time_saved",
                "baseline_required": "manual_cycle_time_minutes",
                "pilot_required": "prototype_cycle_time_minutes",
                "target": "25% or greater median cycle-time reduction",
            },
            {
                "metric": "approval_quality",
                "baseline_required": "manual_approval_completeness_rate",
                "pilot_required": "prototype_approval_completeness_rate",
                "target": "100% of promoted actions include reviewer, timestamp, and decision reason",
            },
            {
                "metric": "exception_rate",
                "baseline_required": "manual_exception_rate",
                "pilot_required": "prototype_exception_rate",
                "target": "no increase in unresolved exceptions during pilot",
            },
        ],
        "decision_thresholds": [
            "Continue only if at least one value metric improves without weakening approval quality.",
            "Continue only if high-severity exceptions are closed or explicitly accepted by the accountable owner.",
            "Stop if value cannot be measured against the manual baseline.",
        ],
        "required_inputs": [
            "value_realization_plan.md",
            "operational_audit_plan.md",
            "risk_exception_register.md",
            "run logs from at least 10 workflow cases or all available cases",
        ],
    }


def render_value_measurement_report(report: dict) -> str:
    lines = [
        "# Value Measurement Report",
        "",
        f"- Status: `{report['status']}`",
        f"- Business area: `{report['business_area']}`",
        f"- Primary candidate: `{report['primary_candidate']}`",
        "",
        "## Metric Cards",
        "",
    ]
    for item in report["metric_cards"]:
        lines.append(
            f"- `{item['metric']}`: baseline `{item['baseline_required']}`, pilot `{item['pilot_required']}`, target {item['target']}."
        )
    lines.extend(["", "## Decision Thresholds", ""])
    lines.extend(f"- {item}" for item in report["decision_thresholds"])
    lines.extend(["", "## Required Inputs", ""])
    lines.extend(f"- `{item}`" for item in report["required_inputs"])
    lines.append("")
    return "\n".join(lines)


def build_pilot_scorecard(summary: dict, candidates: list[dict], shortlist: list[dict]) -> dict:
    top_candidate = shortlist[0] if shortlist else candidates[0] if candidates else {}
    business_area = summary.get("business_area") or top_candidate.get("business_area") or "general"
    if not top_candidate:
        return {
            "status": "discovery_scorecard_required",
            "business_area": business_area,
            "primary_candidate": "",
            "rows": [
                {
                    "metric": "candidate_quality",
                    "owner": "technical_reviewer",
                    "baseline_field": "empty_query_count",
                    "pilot_field": "reviewable_candidate_count",
                    "target": ">=1 reviewable candidate",
                    "evidence_file": "query_recovery.md",
                    "decision_rule": "continue only when at least one candidate has clear license, examples, and maintenance evidence",
                },
                {
                    "metric": "search_precision",
                    "owner": "process_owner",
                    "baseline_field": "queries_without_rationale",
                    "pilot_field": "candidates_rejected_with_reason",
                    "target": "100% explicit accept or reject rationale",
                    "evidence_file": "github_candidates.md",
                    "decision_rule": "stop implementation planning when candidate quality remains unmeasurable",
                },
            ],
        }

    return {
        "status": "pilot_scorecard_required" if shortlist else "manual_review_scorecard_required",
        "business_area": business_area,
        "primary_candidate": top_candidate.get("full_name", ""),
        "rows": [
            {
                "metric": "manual_handoffs_reduced",
                "owner": "process_owner",
                "baseline_field": "baseline_handoff_count",
                "pilot_field": "pilot_handoff_count",
                "target": ">=30% reduction",
                "evidence_file": "value_measurement_report.md",
                "decision_rule": "continue only if reduction is visible without removing required approvals",
            },
            {
                "metric": "cycle_time_saved",
                "owner": "process_owner",
                "baseline_field": "baseline_cycle_minutes",
                "pilot_field": "pilot_cycle_minutes",
                "target": ">=25% median reduction",
                "evidence_file": "run logs",
                "decision_rule": "continue only if median cycle time improves against the manual baseline",
            },
            {
                "metric": "approval_quality",
                "owner": "human_reviewer",
                "baseline_field": "baseline_approval_complete_rate",
                "pilot_field": "pilot_approval_complete_rate",
                "target": "100% approval evidence",
                "evidence_file": "risk_exception_register.md",
                "decision_rule": "stop promotion if any promoted action lacks reviewer, timestamp, or reason",
            },
            {
                "metric": "exception_rate",
                "owner": "automation_operator",
                "baseline_field": "baseline_exception_rate",
                "pilot_field": "pilot_exception_rate",
                "target": "no unresolved increase",
                "evidence_file": "operational_audit_plan.md",
                "decision_rule": "stop expansion if unresolved exceptions increase during the pilot",
            },
        ],
    }


def render_pilot_scorecard(scorecard: dict) -> str:
    lines = [
        "# Pilot Scorecard",
        "",
        f"- Status: `{scorecard['status']}`",
        f"- Business area: `{scorecard['business_area']}`",
        f"- Primary candidate: `{scorecard['primary_candidate']}`",
        "",
        "| Metric | Owner | Baseline Field | Pilot Field | Target | Evidence | Decision Rule |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in scorecard["rows"]:
        lines.append(
            "| {metric} | {owner} | `{baseline}` | `{pilot}` | {target} | `{evidence}` | {rule} |".format(
                metric=row["metric"],
                owner=row["owner"],
                baseline=row["baseline_field"],
                pilot=row["pilot_field"],
                target=row["target"],
                evidence=row["evidence_file"],
                rule=row["decision_rule"],
            )
        )
    lines.append("")
    return "\n".join(lines)


def render_pilot_scorecard_csv(scorecard: dict) -> str:
    fields = ["metric", "owner", "baseline_field", "pilot_field", "target", "evidence_file", "decision_rule"]
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(scorecard["rows"])
    return buffer.getvalue()


def _candidate_needs_maintenance_review(candidate: dict) -> bool:
    open_issues = int(candidate.get("open_issues") or 0)
    if open_issues >= 100:
        return True
    updated_at = str(candidate.get("updated_at") or "")
    if len(updated_at) >= 4 and updated_at[:4].isdigit():
        return int(updated_at[:4]) <= 2025
    return False
