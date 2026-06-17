from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from ai_automation_kit.core.artifacts import write_artifact_index, write_research_artifacts
from ai_automation_kit.core.fetch import FetchPolicy, fetch_uri
from ai_automation_kit.core.github import (
    fetch_github_readme,
    fetch_github_repo,
    github_repo_to_finding,
    search_github_repositories,
)
from ai_automation_kit.core.github_analysis import score_github_repo, write_github_candidate_artifacts
from ai_automation_kit.core.github_review import (
    build_enterprise_readiness,
    build_executive_decision_brief,
    build_operational_audit_plan,
    build_pilot_scorecard,
    build_risk_exception_register,
    build_run_summary,
    build_stakeholder_rollout_map,
    build_value_measurement_report,
    build_value_realization_plan,
    render_enterprise_readiness,
    render_executive_decision_brief,
    render_operational_audit_plan,
    render_pilot_scorecard,
    render_pilot_scorecard_csv,
    render_risk_exception_register,
    render_run_summary,
    render_stakeholder_rollout_map,
    render_value_measurement_report,
    render_value_realization_plan,
)
from ai_automation_kit.core.html import extract_html_content
from ai_automation_kit.core.models import FailedFetch, RunRecord, SourceRecord
from ai_automation_kit.core.store import JsonRunStore


def run_research_agent(config_path: Path | str, output_dir: Path | str) -> RunRecord:
    config_file = Path(config_path)
    output = Path(output_dir)
    config = json.loads(config_file.read_text(encoding="utf-8"))
    topic = config["topic"]
    sources = config.get("sources", [])
    github_repositories = config.get("github_repositories", [])
    github_searches = config.get("github_searches", [])
    include_readme = bool(config.get("include_readme", False))
    business_context = config.get("business_context", {})
    business_area = business_context.get("business_area")

    started_at = _now()
    run_id = f"run-{uuid4().hex[:12]}"
    store = JsonRunStore(output)
    findings: list[dict] = []
    source_ids: list[str] = []
    failed_fetches: list[FailedFetch] = []

    for index, source in enumerate(sources, start=1):
        uri = source["uri"]
        try:
            fetched = fetch_uri(uri, FetchPolicy())
            content = extract_html_content(fetched.content)
            source_id = f"src-{index:03d}-{hashlib.sha256(uri.encode('utf-8')).hexdigest()[:8]}"
            markdown_path = _write_source_markdown(output, source_id, content.title, uri, content.text)
            raw_path = _write_source_raw(output, source_id, fetched.content)
            record = SourceRecord(
                source_id=source_id,
                source_type="web" if uri.startswith(("http://", "https://")) else "file",
                uri=uri,
                title=content.title or uri,
                retrieved_at=_now(),
                content_hash=hashlib.sha256(fetched.content.encode("utf-8")).hexdigest(),
                raw_path=str(raw_path.relative_to(output)),
                markdown_path=str(markdown_path.relative_to(output)),
                metadata={"rank": index, "content_type": fetched.content_type},
            )
            store.save_source(record)
            source_ids.append(source_id)
            findings.append(
                {
                    "title": record.title,
                    "uri": record.to_dict()["uri"],
                    "summary": _first_sentence(content.text),
                    "retrieved_at": record.retrieved_at,
                }
            )
        except Exception as exc:  # noqa: BLE001 - failures are logged into the run record.
            failed_fetches.append(FailedFetch(uri=uri, reason=str(exc)))

    github_records = []
    github_readmes = []
    github_candidates = []
    token = os.environ.get("GITHUB_TOKEN")
    for repo_name in github_repositories:
        try:
            repo = fetch_github_repo(repo_name, token=token)
            github_records.append(repo.to_dict())
            candidate = score_github_repo(repo, business_area=business_area)
            candidate["source_query"] = "direct_repository_input"
            github_candidates.append(candidate)
            findings.append(github_repo_to_finding(repo))
            if include_readme:
                try:
                    github_readmes.append(_fetch_and_write_github_readme(output, repo.full_name, token))
                except Exception as exc:  # noqa: BLE001 - failures are logged into the run record.
                    failed_fetches.append(FailedFetch(uri=f"https://api.github.com/repos/{repo.full_name}/readme", reason=str(exc)))
        except Exception as exc:  # noqa: BLE001 - failures are logged into the run record.
            failed_fetches.append(FailedFetch(uri=f"https://api.github.com/repos/{repo_name}", reason=str(exc)))

    github_search_records = []
    empty_github_search_queries = []
    for search in github_searches:
        query = search["query"]
        sort = search.get("sort", "stars")
        order = search.get("order", "desc")
        per_page = int(search.get("per_page", 10))
        try:
            result = search_github_repositories(
                query=query,
                sort=sort,
                order=order,
                per_page=per_page,
                token=token,
            )
            repositories = result["repositories"]
            if not repositories:
                empty_github_search_queries.append(query)
            github_search_records.append(
                {
                    **{key: value for key, value in result.items() if key != "repositories"},
                    "repositories": [repo.to_dict() for repo in repositories],
                }
            )
            for repo in repositories:
                candidate = score_github_repo(repo, business_area=business_area)
                candidate["source_query"] = query
                github_candidates.append(candidate)
            findings.extend(github_repo_to_finding(repo) for repo in repositories)
            if include_readme:
                for repo in repositories:
                    try:
                        github_readmes.append(_fetch_and_write_github_readme(output, repo.full_name, token))
                    except Exception as exc:  # noqa: BLE001 - failures are logged into the run record.
                        failed_fetches.append(FailedFetch(uri=f"https://api.github.com/repos/{repo.full_name}/readme", reason=str(exc)))
        except Exception as exc:  # noqa: BLE001 - failures are logged into the run record.
            failed_fetches.append(FailedFetch(uri=f"https://api.github.com/search/repositories?q={query}", reason=str(exc)))

    finished_at = _now()
    recovery_payload = None
    if github_searches and not github_candidates:
        recovery_payload = _build_query_recovery(business_area=business_area, empty_queries=empty_github_search_queries)
        findings.append(
            {
                "title": "GitHub query recovery",
                "uri": "local://query_recovery.md",
                "summary": "No GitHub candidates were found. Review query_recovery.md for safer fallback searches.",
                "retrieved_at": finished_at,
            }
        )

    status = "succeeded" if findings else "failed"
    draft_run = RunRecord(
        run_id=run_id,
        template_name="research-agent",
        input={
            "topic": topic,
            "source_count": len(sources),
            "github_repository_count": len(github_repositories),
            "github_search_count": len(github_searches),
        },
        started_at=started_at,
        finished_at=finished_at,
        status=status,
        errors=[] if findings else ["no sources were fetched successfully"],
        artifacts=[],
        source_ids=source_ids,
        failed_fetches=failed_fetches,
    )

    artifacts = write_research_artifacts(
        output_dir=output,
        topic=topic,
        findings=findings,
        run=draft_run.to_dict(),
        rerun_command=f"PYTHONPATH=src python3 -m ai_automation_kit.cli research-agent --config {config_file} --output {output}",
    )
    if github_records:
        (output / "github_repositories.json").write_text(
            json.dumps({"repositories": github_records}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        artifacts.append({"kind": "github_repositories", "path": "github_repositories.json"})
    if github_search_records:
        (output / "github_searches.json").write_text(
            json.dumps({"searches": github_search_records}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        artifacts.append({"kind": "github_searches", "path": "github_searches.json"})
    if github_candidates:
        artifacts.extend(write_github_candidate_artifacts(output, github_candidates, business_area=business_area))
    if recovery_payload:
        run_summary = build_run_summary([], [], business_area)
        (output / "run_summary.json").write_text(
            json.dumps(run_summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (output / "run_summary.md").write_text(render_run_summary(run_summary), encoding="utf-8")
        executive_brief = build_executive_decision_brief(run_summary, [], [])
        (output / "executive_decision_brief.json").write_text(
            json.dumps(executive_brief, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (output / "executive_decision_brief.md").write_text(
            render_executive_decision_brief(executive_brief),
            encoding="utf-8",
        )
        enterprise_readiness = build_enterprise_readiness(run_summary, [], [])
        (output / "enterprise_readiness.json").write_text(
            json.dumps(enterprise_readiness, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (output / "enterprise_readiness.md").write_text(
            render_enterprise_readiness(enterprise_readiness),
            encoding="utf-8",
        )
        value_plan = build_value_realization_plan(run_summary, [], [])
        (output / "value_realization_plan.json").write_text(
            json.dumps(value_plan, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (output / "value_realization_plan.md").write_text(
            render_value_realization_plan(value_plan),
            encoding="utf-8",
        )
        stakeholder_map = build_stakeholder_rollout_map(run_summary, [], [])
        (output / "stakeholder_rollout_map.json").write_text(
            json.dumps(stakeholder_map, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (output / "stakeholder_rollout_map.md").write_text(
            render_stakeholder_rollout_map(stakeholder_map),
            encoding="utf-8",
        )
        risk_register = build_risk_exception_register(run_summary, [], [])
        (output / "risk_exception_register.json").write_text(
            json.dumps(risk_register, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (output / "risk_exception_register.md").write_text(
            render_risk_exception_register(risk_register),
            encoding="utf-8",
        )
        audit_plan = build_operational_audit_plan(run_summary, [], [])
        (output / "operational_audit_plan.json").write_text(
            json.dumps(audit_plan, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (output / "operational_audit_plan.md").write_text(
            render_operational_audit_plan(audit_plan),
            encoding="utf-8",
        )
        measurement_report = build_value_measurement_report(run_summary, [], [])
        (output / "value_measurement_report.json").write_text(
            json.dumps(measurement_report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (output / "value_measurement_report.md").write_text(
            render_value_measurement_report(measurement_report),
            encoding="utf-8",
        )
        pilot_scorecard = build_pilot_scorecard(run_summary, [], [])
        (output / "pilot_scorecard.json").write_text(
            json.dumps(pilot_scorecard, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (output / "pilot_scorecard.md").write_text(render_pilot_scorecard(pilot_scorecard), encoding="utf-8")
        (output / "pilot_scorecard.csv").write_text(render_pilot_scorecard_csv(pilot_scorecard), encoding="utf-8")
        artifacts.extend(
            [
                {"kind": "run_summary_json", "path": "run_summary.json"},
                {"kind": "run_summary", "path": "run_summary.md"},
                {"kind": "executive_decision_brief_json", "path": "executive_decision_brief.json"},
                {"kind": "executive_decision_brief", "path": "executive_decision_brief.md"},
                {"kind": "enterprise_readiness_json", "path": "enterprise_readiness.json"},
                {"kind": "enterprise_readiness", "path": "enterprise_readiness.md"},
                {"kind": "value_realization_plan_json", "path": "value_realization_plan.json"},
                {"kind": "value_realization_plan", "path": "value_realization_plan.md"},
                {"kind": "stakeholder_rollout_map_json", "path": "stakeholder_rollout_map.json"},
                {"kind": "stakeholder_rollout_map", "path": "stakeholder_rollout_map.md"},
                {"kind": "risk_exception_register_json", "path": "risk_exception_register.json"},
                {"kind": "risk_exception_register", "path": "risk_exception_register.md"},
                {"kind": "operational_audit_plan_json", "path": "operational_audit_plan.json"},
                {"kind": "operational_audit_plan", "path": "operational_audit_plan.md"},
                {"kind": "value_measurement_report_json", "path": "value_measurement_report.json"},
                {"kind": "value_measurement_report", "path": "value_measurement_report.md"},
                {"kind": "pilot_scorecard_json", "path": "pilot_scorecard.json"},
                {"kind": "pilot_scorecard", "path": "pilot_scorecard.md"},
                {"kind": "pilot_scorecard_csv", "path": "pilot_scorecard.csv"},
            ]
        )
        artifacts.extend(_write_query_recovery_artifacts(output, recovery_payload))
    if github_readmes:
        (output / "github_readmes.json").write_text(
            json.dumps({"readmes": github_readmes}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        artifacts.append({"kind": "github_readmes", "path": "github_readmes.json"})
    artifacts.extend(write_artifact_index(output, "research-agent", artifacts))
    run = RunRecord(
        run_id=run_id,
        template_name="research-agent",
        input=draft_run.input,
        started_at=started_at,
        finished_at=finished_at,
        status=status,
        errors=draft_run.errors,
        artifacts=artifacts,
        source_ids=source_ids,
        failed_fetches=failed_fetches,
    )
    store.save_run(run)
    return run


def _write_source_markdown(output: Path, source_id: str, title: str, uri: str, text: str) -> Path:
    path = output / "sources" / "markdown" / f"{source_id}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# {title or uri}\n\nSource: {uri}\n\n{text}\n", encoding="utf-8")
    return path


def _write_source_raw(output: Path, source_id: str, raw: str) -> Path:
    path = output / "sources" / "raw" / f"{source_id}.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(raw, encoding="utf-8")
    return path


def _fetch_and_write_github_readme(output: Path, repo_name: str, token: str | None) -> dict:
    readme = fetch_github_readme(repo_name, token=token)
    safe_repo_name = repo_name.replace("/", "__")
    path = output / "github_readmes" / f"{safe_repo_name}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(readme["text"], encoding="utf-8")
    return {
        "repository": repo_name,
        "path": str(path.relative_to(output)),
        "source_path": readme["path"],
        "html_url": readme["html_url"],
        "download_url": readme["download_url"],
        "size": readme["size"],
    }


def _build_query_recovery(business_area: str | None, empty_queries: list[str]) -> dict:
    area = business_area or "operations"
    base_terms = {
        "sales": ["sales automation stars:>50", "crm automation stars:>50", "lead workflow stars:>50"],
        "support": ["support automation stars:>50", "helpdesk automation stars:>50", "customer support workflow stars:>50"],
        "finance": ["finance automation stars:>50", "invoice automation stars:>50", "accounting workflow stars:>50"],
        "operations": ["workflow automation stars:>50", "business process automation stars:>50", "orchestration stars:>50"],
        "marketing": ["marketing automation stars:>50", "content automation stars:>50", "campaign workflow stars:>50"],
        "hr": ["hr automation stars:>50", "recruiting automation stars:>50", "onboarding workflow stars:>50"],
    }
    return {
        "business_area": area,
        "empty_queries": empty_queries,
        "suggested_queries": base_terms.get(area, [f"{area} automation stars:>50", f"{area} workflow stars:>50"]),
        "next_actions": [
            "Lower the star threshold.",
            "Remove rare exact keywords.",
            "Search by workflow outcome instead of implementation technology.",
            "Run github-discover again with --query.",
        ],
    }


def _write_query_recovery_artifacts(output: Path, recovery: dict) -> list[dict]:
    output.mkdir(parents=True, exist_ok=True)
    (output / "query_recovery.json").write_text(
        json.dumps(recovery, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# GitHub Query Recovery",
        "",
        "No GitHub candidates were found for the configured searches.",
        "",
        f"- Business area: `{recovery['business_area']}`",
        "",
        "## Empty Queries",
        "",
    ]
    lines.extend(f"- `{query}`" for query in recovery["empty_queries"])
    lines.extend(["", "## Suggested Queries", ""])
    lines.extend(f"- `{query}`" for query in recovery["suggested_queries"])
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- {action}" for action in recovery["next_actions"])
    lines.append("")
    (output / "query_recovery.md").write_text("\n".join(lines), encoding="utf-8")
    return [
        {"kind": "query_recovery_json", "path": "query_recovery.json"},
        {"kind": "query_recovery", "path": "query_recovery.md"},
    ]


def _first_sentence(text: str) -> str:
    cleaned = " ".join(text.split())
    if not cleaned:
        return "No visible text extracted."
    match = re.search(r"(.+?[.!?。])(?:\s|$)", cleaned)
    return match.group(1) if match else cleaned[:240]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
