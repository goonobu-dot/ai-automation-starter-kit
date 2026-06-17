from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from ai_automation_kit.core.artifacts import write_research_artifacts
from ai_automation_kit.core.fetch import FetchPolicy, fetch_uri
from ai_automation_kit.core.github import (
    fetch_github_readme,
    fetch_github_repo,
    github_repo_to_finding,
    search_github_repositories,
)
from ai_automation_kit.core.github_analysis import score_github_repo, write_github_candidate_artifacts
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
            github_candidates.append(score_github_repo(repo, business_area=business_area))
            findings.append(github_repo_to_finding(repo))
            if include_readme:
                try:
                    github_readmes.append(_fetch_and_write_github_readme(output, repo.full_name, token))
                except Exception as exc:  # noqa: BLE001 - failures are logged into the run record.
                    failed_fetches.append(FailedFetch(uri=f"https://api.github.com/repos/{repo.full_name}/readme", reason=str(exc)))
        except Exception as exc:  # noqa: BLE001 - failures are logged into the run record.
            failed_fetches.append(FailedFetch(uri=f"https://api.github.com/repos/{repo_name}", reason=str(exc)))

    github_search_records = []
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
            github_search_records.append(
                {
                    **{key: value for key, value in result.items() if key != "repositories"},
                    "repositories": [repo.to_dict() for repo in repositories],
                }
            )
            github_candidates.extend(score_github_repo(repo, business_area=business_area) for repo in repositories)
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
    if github_readmes:
        (output / "github_readmes.json").write_text(
            json.dumps({"readmes": github_readmes}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        artifacts.append({"kind": "github_readmes", "path": "github_readmes.json"})
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


def _first_sentence(text: str) -> str:
    cleaned = " ".join(text.split())
    if not cleaned:
        return "No visible text extracted."
    match = re.search(r"(.+?[.!?。])(?:\s|$)", cleaned)
    return match.group(1) if match else cleaned[:240]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
