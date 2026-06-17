from __future__ import annotations

import json
from pathlib import Path

from ai_automation_kit.core.github_scoring import deployment_shape as infer_deployment_shape


def write_adapter_artifacts(output: Path, candidate: dict, business_area: str | None) -> list[dict]:
    blueprint = build_adapter_blueprint(candidate, business_area)
    (output / "adapter_blueprint.json").write_text(
        json.dumps(blueprint, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output / "adapter_blueprint.md").write_text(render_adapter_blueprint(blueprint), encoding="utf-8")
    write_adapter_starter(output, blueprint)
    return [
        {"kind": "adapter_blueprint_json", "path": "adapter_blueprint.json"},
        {"kind": "adapter_blueprint", "path": "adapter_blueprint.md"},
        {"kind": "adapter_starter", "path": "adapter_starter/README.md"},
        {"kind": "adapter_starter_code", "path": "adapter_starter/adapter.py"},
        {"kind": "adapter_starter_smoke_test", "path": "adapter_starter/smoke_test.py"},
        {"kind": "adapter_starter_sample_input", "path": "adapter_starter/sample_input.json"},
    ]


def build_adapter_blueprint(candidate: dict, business_area: str | None) -> dict:
    area = business_area or candidate.get("business_area") or "operations"
    return {
        "candidate": {
            "full_name": candidate["full_name"],
            "url": candidate["url"],
            "score": candidate["score"],
            "license": candidate["license"],
            "deployment_shape": candidate.get("deployment_shape") or infer_deployment_shape(candidate.get("language")),
            "business_area": area,
        },
        "contract": {
            "mode": "adapter_only",
            "goal": f"Wrap the useful {area} workflow pattern without copying project internals.",
            "inputs": [
                "workflow_request",
                "operator_context",
                "dry_run=true",
            ],
            "outputs": [
                "proposed_actions",
                "run_log",
                "approval_request",
                "rollback_notes",
            ],
        },
        "controls": {
            "required": [
                "dry-run mode before any external action",
                "human approval before production execution",
                "source repository license review",
                "structured run log for audit",
                "rollback notes for every promoted workflow",
            ],
            "blocked_actions": [
                "copying third-party internals before license review",
                "sending customer-facing messages without approval",
                "using real customer data in the first prototype",
            ],
        },
        "acceptance_criteria": [
            "One representative workflow runs with synthetic data.",
            "The adapter records inputs, outputs, approvals, and errors.",
            "The project owner can explain the saved time or reduced handoff.",
            "Production rollout remains blocked until license and secret checks pass.",
        ],
    }


def render_adapter_blueprint(blueprint: dict) -> str:
    candidate = blueprint["candidate"]
    contract = blueprint["contract"]
    controls = blueprint["controls"]
    lines = [
        f"# Adapter Blueprint: {candidate['full_name']}",
        "",
        f"- URL: {candidate['url']}",
        f"- Business area: `{candidate['business_area']}`",
        f"- Score: `{candidate['score']}`",
        f"- License: `{candidate['license']}`",
        f"- Deployment shape: `{candidate['deployment_shape']}`",
        "",
        "## Adapter Contract",
        "",
        f"- Mode: `{contract['mode']}`",
        f"- Goal: {contract['goal']}",
        "",
        "### Inputs",
        "",
    ]
    lines.extend(f"- `{item}`" for item in contract["inputs"])
    lines.extend(["", "### Outputs", ""])
    lines.extend(f"- `{item}`" for item in contract["outputs"])
    lines.extend(["", "## Controls", ""])
    lines.extend(f"- [ ] {item}" for item in controls["required"])
    lines.extend(["", "## Blocked Actions", ""])
    lines.extend(f"- {item}" for item in controls["blocked_actions"])
    lines.extend(["", "## Acceptance Criteria", ""])
    lines.extend(f"- [ ] {item}" for item in blueprint["acceptance_criteria"])
    lines.append("")
    return "\n".join(lines)


def write_adapter_starter(output: Path, blueprint: dict) -> None:
    starter = output / "adapter_starter"
    starter.mkdir(parents=True, exist_ok=True)
    sample_input = _adapter_sample_input(blueprint)
    (starter / "README.md").write_text(_render_adapter_starter_readme(blueprint), encoding="utf-8")
    (starter / "adapter.py").write_text(_render_adapter_starter_code(), encoding="utf-8")
    (starter / "smoke_test.py").write_text(_render_adapter_smoke_test(), encoding="utf-8")
    (starter / "sample_input.json").write_text(json.dumps(sample_input, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _adapter_sample_input(blueprint: dict) -> dict:
    candidate = blueprint["candidate"]
    return {
        "workflow_request": {
            "business_area": candidate["business_area"],
            "goal": f"Prototype an adapter for {candidate['full_name']} using synthetic data.",
            "source_repository": candidate["url"],
        },
        "operator_context": {
            "operator": "example-operator",
            "approval_owner": "workflow-owner",
            "environment": "dry-run",
        },
        "dry_run": True,
    }


def _render_adapter_starter_readme(blueprint: dict) -> str:
    candidate = blueprint["candidate"]
    return "\n".join(
        [
            f"# Adapter Starter: {candidate['full_name']}",
            "",
            "This starter is intentionally adapter-only. It does not copy third-party project internals.",
            "",
            "## Files",
            "",
            "- `adapter.py`: dry-run adapter skeleton",
            "- `sample_input.json`: synthetic input payload",
            "- `smoke_test.py`: local smoke test for the adapter contract",
            "",
            "## Run",
            "",
            "```bash",
            "python3 adapter_starter/smoke_test.py",
            "```",
            "",
            "## Promotion Rules",
            "",
            "- Keep `dry_run=true` until the workflow owner approves production use.",
            "- Complete license review before copying code or examples from the source repository.",
            "- Record run logs, approval request, rollback notes, and measured business value.",
            "",
        ]
    )


def _render_adapter_starter_code() -> str:
    return '''from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def run_adapter(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a safe dry-run adapter result without external side effects."""
    if payload.get("dry_run") is not True:
        raise ValueError("This starter only supports dry_run=true.")

    workflow_request = payload.get("workflow_request", {})
    operator_context = payload.get("operator_context", {})
    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return {
        "status": "dry_run_ready",
        "proposed_actions": [
            {
                "type": "inspect_workflow",
                "description": f"Review adapter goal: {workflow_request.get('goal', 'No goal supplied')}",
            },
            {
                "type": "collect_approval",
                "description": "Ask the workflow owner to approve the first synthetic-data prototype.",
            },
        ],
        "approval_request": {
            "status": "pending",
            "owner": operator_context.get("approval_owner", "workflow-owner"),
            "dry_run": True,
        },
        "run_log": {
            "timestamp": timestamp,
            "operator": operator_context.get("operator", "unknown"),
            "business_area": workflow_request.get("business_area", "operations"),
        },
        "rollback_notes": [
            "No external side effects were performed.",
            "Delete generated outputs if the prototype is rejected.",
        ],
    }


def main() -> int:
    payload = json.loads(Path(__file__).with_name("sample_input.json").read_text(encoding="utf-8"))
    result = run_adapter(payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def _render_adapter_smoke_test() -> str:
    return '''from __future__ import annotations

import json
from pathlib import Path

from adapter import run_adapter


def main() -> int:
    payload = json.loads(Path(__file__).with_name("sample_input.json").read_text(encoding="utf-8"))
    result = run_adapter(payload)
    assert result["status"] == "dry_run_ready"
    assert result["approval_request"]["status"] == "pending"
    assert result["approval_request"]["dry_run"] is True
    assert result["proposed_actions"]
    assert result["rollback_notes"]
    print("adapter smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''
