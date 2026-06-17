from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from ai_automation_kit.core.models import Artifact, RunRecord
from ai_automation_kit.core.store import JsonRunStore


def run_delivery_pipeline(config_path: Path | str, output_dir: Path | str) -> RunRecord:
    config_file = Path(config_path)
    output = Path(output_dir)
    config = json.loads(config_file.read_text(encoding="utf-8"))

    project_name = config["project_name"]
    template_name = config["template_name"]
    env_vars = list(config.get("env_vars", []))
    services = list(config.get("services", []))

    started_at = _now()
    run_id = f"run-{uuid4().hex[:12]}"
    artifacts = _write_delivery_artifacts(
        output=output,
        project_name=project_name,
        template_name=template_name,
        env_vars=env_vars,
        services=services,
    )
    finished_at = _now()
    run = RunRecord(
        run_id=run_id,
        template_name="delivery-pipeline",
        input={
            "project_name": project_name,
            "template_name": template_name,
            "env_var_count": len(env_vars),
            "service_count": len(services),
        },
        started_at=started_at,
        finished_at=finished_at,
        status="succeeded",
        errors=[],
        artifacts=artifacts,
    )
    JsonRunStore(output).save_run(run)
    return run


def _write_delivery_artifacts(
    output: Path,
    project_name: str,
    template_name: str,
    env_vars: list[str],
    services: list[str],
) -> list[Artifact]:
    files = {
        "README.md": _render_readme(project_name, template_name, env_vars, services),
        ".env.example": _render_env_example(env_vars),
        "docker-compose.yml": _render_compose(project_name, env_vars, services),
        "docs/operation-manual.md": _render_operation_manual(project_name, template_name, env_vars, services),
        "docs/delivery-checklist.md": _render_delivery_checklist(project_name, env_vars, services),
        "docs/success-metrics.md": _render_success_metrics(project_name, template_name),
        "tests/smoke-test.md": _render_smoke_test(project_name, services),
    }
    artifacts: list[Artifact] = []
    for relative_path, content in files.items():
        path = output / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        artifacts.append(Artifact(kind=_artifact_kind(relative_path), path=relative_path))
    return artifacts


def _render_readme(project_name: str, template_name: str, env_vars: list[str], services: list[str]) -> str:
    env_lines = "\n".join(f"- `{name}`" for name in env_vars) or "- No environment variables configured."
    service_lines = "\n".join(f"- `{name}`" for name in services) or "- No services configured."
    return (
        f"# {project_name}\n\n"
        f"Generated delivery package for the `{template_name}` template.\n\n"
        "## Environment\n\n"
        "Copy `.env.example` to `.env` and replace every `replace_me` placeholder in the target deployment environment.\n\n"
        f"{env_lines}\n\n"
        "## Services\n\n"
        f"{service_lines}\n\n"
        "## Delivery Assets\n\n"
        "- `docker-compose.yml`\n"
        "- `docs/operation-manual.md`\n"
        "- `docs/delivery-checklist.md`\n"
        "- `docs/success-metrics.md`\n"
        "- `tests/smoke-test.md`\n"
    )


def _render_env_example(env_vars: list[str]) -> str:
    if not env_vars:
        return "# No environment variables required.\n"
    return "".join(f"{name}=replace_me\n" for name in env_vars)


def _render_compose(project_name: str, env_vars: list[str], services: list[str]) -> str:
    lines = ["services:"]
    for service in services:
        lines.extend(
            [
                f"  {service}:",
                "    image: python:3.12-slim",
                f"    container_name: {_slug(project_name)}-{service}",
                "    working_dir: /workspace",
                "    volumes:",
                "      - .:/workspace",
            ]
        )
        if env_vars:
            lines.append("    environment:")
            for env_var in env_vars:
                lines.append(f"      {env_var}: ${{{env_var}}}")
        lines.extend(["    command: python --version", ""])
    return "\n".join(lines).rstrip() + "\n"


def _render_operation_manual(project_name: str, template_name: str, env_vars: list[str], services: list[str]) -> str:
    env_lines = "\n".join(f"- `{name}`: set in deployment secrets manager; never commit a real value." for name in env_vars)
    if not env_lines:
        env_lines = "- No environment variables configured."
    service_lines = "\n".join(f"- `{name}`: validate startup and logs before handoff." for name in services)
    if not service_lines:
        service_lines = "- No services configured."
    return (
        f"# Operation Manual: {project_name}\n\n"
        f"Template: `{template_name}`\n\n"
        "## Secret Handling\n\n"
        f"{env_lines}\n\n"
        "## Services\n\n"
        f"{service_lines}\n\n"
        "## Handoff Routine\n\n"
        "1. Review `.env.example` for placeholder-only values.\n"
        "2. Start services with Docker Compose in the delivery environment.\n"
        "3. Complete `docs/delivery-checklist.md`.\n"
        "4. Record smoke test evidence in `tests/smoke-test.md`.\n"
    )


def _render_delivery_checklist(project_name: str, env_vars: list[str], services: list[str]) -> str:
    lines = [
        f"# Delivery Checklist: {project_name}",
        "",
        "## Safety",
        "",
        "- [ ] Confirm `.env.example` contains placeholders only.",
        "- [ ] Confirm no real customer secrets are committed.",
        "",
        "## Configuration",
        "",
    ]
    if env_vars:
        lines.extend(f"- [ ] Confirm `{name}` is set in the deployment environment." for name in env_vars)
    else:
        lines.append("- [ ] Confirm no deployment environment variables are required.")
    lines.extend(["", "## Smoke Tests", ""])
    if services:
        lines.extend(f"- [ ] Run smoke test for `{service}`." for service in services)
    else:
        lines.append("- [ ] Confirm no service smoke tests are required.")
    lines.extend(["", "## Handoff", "", "- [ ] Share operation manual with the project owner.", "- [ ] Archive delivery evidence outside the public repository.", ""])
    return "\n".join(lines)


def _render_smoke_test(project_name: str, services: list[str]) -> str:
    lines = [
        f"# Smoke Test: {project_name}",
        "",
        "## Commands",
        "",
        "```bash",
        "docker compose config",
        "docker compose up --abort-on-container-exit",
        "```",
        "",
        "## Service Results",
        "",
    ]
    if services:
        lines.extend(f"- `{service}`: pending" for service in services)
    else:
        lines.append("- No services configured.")
    lines.append("")
    return "\n".join(lines)


def _render_success_metrics(project_name: str, template_name: str) -> str:
    return (
        f"# Success Metrics: {project_name}\n\n"
        f"Template: `{template_name}`\n\n"
        "## Baseline\n\n"
        "- Manual time spent per week: pending\n"
        "- Number of handoffs per workflow: pending\n"
        "- Number of repeated errors or missed follow-ups: pending\n"
        "- Average time from request to completed output: pending\n\n"
        "## Target Metrics\n\n"
        "- Manual time saved per week\n"
        "- Fewer manual handoffs\n"
        "- Faster request-to-output cycle time\n"
        "- More decisions backed by saved source artifacts\n"
        "- Zero committed secrets or unapproved external actions\n\n"
        "## Review Rhythm\n\n"
        "1. Capture baseline before deployment.\n"
        "2. Run the workflow in dry-run mode for one week.\n"
        "3. Compare saved time, error reduction, and approval completion.\n"
        "4. Promote only if safety checks and business value are both visible.\n"
    )


def _artifact_kind(relative_path: str) -> str:
    suffix = Path(relative_path).suffix
    if suffix in {".md", ""}:
        return "markdown"
    if suffix in {".yml", ".yaml"}:
        return "compose"
    if relative_path == ".env.example":
        return "env_example"
    return suffix.lstrip(".") or "file"


def _slug(value: str) -> str:
    cleaned = "".join(character.lower() if character.isalnum() else "-" for character in value)
    return "-".join(part for part in cleaned.split("-") if part) or "delivery"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
