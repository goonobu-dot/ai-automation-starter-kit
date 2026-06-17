from __future__ import annotations

import json
import re
from base64 import b64decode
from dataclasses import asdict, dataclass
from urllib.parse import urlencode
from urllib.request import Request, urlopen


GITHUB_API_ROOT = "https://api.github.com"


@dataclass(frozen=True)
class GitHubRepo:
    full_name: str
    html_url: str
    description: str
    stars: int
    forks: int
    open_issues: int
    license: str
    topics: list[str]
    language: str
    updated_at: str
    rate_limit_remaining: str

    def to_dict(self) -> dict:
        return asdict(self)


def fetch_github_repo(repo_name: str, token: str | None = None, timeout_seconds: int = 10) -> GitHubRepo:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo_name):
        raise ValueError("GitHub repository must use owner/repo format")

    request = Request(
        f"{GITHUB_API_ROOT}/repos/{repo_name}",
        headers=_headers(token),
    )
    with urlopen(request, timeout=timeout_seconds) as response:
        payload = json.loads(response.read().decode("utf-8"))
        rate_limit_remaining = response.headers.get("X-RateLimit-Remaining", "unknown")

    payload_with_name = dict(payload)
    payload_with_name["full_name"] = payload.get("full_name", repo_name)
    return _repo_from_payload(payload_with_name, rate_limit_remaining)


def search_github_repositories(
    query: str,
    sort: str = "stars",
    order: str = "desc",
    per_page: int = 10,
    token: str | None = None,
    timeout_seconds: int = 10,
) -> dict:
    if not query.strip():
        raise ValueError("GitHub search query must not be empty")
    if sort not in {"stars", "forks", "help-wanted-issues", "updated"}:
        raise ValueError("GitHub repository search sort must be one of stars, forks, help-wanted-issues, updated")
    if order not in {"asc", "desc"}:
        raise ValueError("GitHub repository search order must be asc or desc")
    if not 1 <= per_page <= 100:
        raise ValueError("GitHub repository search per_page must be between 1 and 100")

    params = urlencode({"q": query, "sort": sort, "order": order, "per_page": per_page})
    request = Request(
        f"{GITHUB_API_ROOT}/search/repositories?{params}",
        headers=_headers(token),
    )
    with urlopen(request, timeout=timeout_seconds) as response:
        payload = json.loads(response.read().decode("utf-8"))
        rate_limit_remaining = response.headers.get("X-RateLimit-Remaining", "unknown")

    return {
        "query": query,
        "sort": sort,
        "order": order,
        "per_page": per_page,
        "total_count": int(payload.get("total_count") or 0),
        "incomplete_results": bool(payload.get("incomplete_results")),
        "rate_limit_remaining": rate_limit_remaining,
        "repositories": [_repo_from_payload(item, rate_limit_remaining) for item in payload.get("items", [])],
    }


def fetch_github_readme(repo_name: str, token: str | None = None, timeout_seconds: int = 10) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo_name):
        raise ValueError("GitHub repository must use owner/repo format")

    request = Request(
        f"{GITHUB_API_ROOT}/repos/{repo_name}/readme",
        headers=_headers(token),
    )
    with urlopen(request, timeout=timeout_seconds) as response:
        payload = json.loads(response.read().decode("utf-8"))
        rate_limit_remaining = response.headers.get("X-RateLimit-Remaining", "unknown")

    text = ""
    if payload.get("encoding") == "base64" and payload.get("content"):
        text = b64decode(payload["content"]).decode("utf-8", errors="replace")

    return {
        "repository": repo_name,
        "name": payload.get("name", ""),
        "path": payload.get("path", ""),
        "size": int(payload.get("size") or 0),
        "encoding": payload.get("encoding", ""),
        "html_url": payload.get("html_url", ""),
        "download_url": payload.get("download_url", ""),
        "rate_limit_remaining": rate_limit_remaining,
        "text": text,
    }


def github_repo_to_finding(repo: GitHubRepo) -> dict:
    topic_text = ", ".join(repo.topics[:6]) if repo.topics else "no topics"
    summary = (
        f"{repo.description or 'No description.'} "
        f"Signals: {repo.stars} stars, {repo.forks} forks, {repo.open_issues} open issues, "
        f"{repo.language}, license {repo.license}, topics: {topic_text}."
    )
    return {
        "title": repo.full_name,
        "uri": repo.html_url,
        "summary": summary,
        "retrieved_at": repo.updated_at,
        "metadata": repo.to_dict(),
    }


def _repo_from_payload(payload: dict, rate_limit_remaining: str) -> GitHubRepo:
    license_info = payload.get("license") or {}
    full_name = payload.get("full_name") or ""
    return GitHubRepo(
        full_name=full_name,
        html_url=payload.get("html_url") or f"https://github.com/{full_name}",
        description=payload.get("description") or "",
        stars=int(payload.get("stargazers_count") or 0),
        forks=int(payload.get("forks_count") or 0),
        open_issues=int(payload.get("open_issues_count") or 0),
        license=license_info.get("spdx_id") or "NOASSERTION",
        topics=list(payload.get("topics") or []),
        language=payload.get("language") or "unknown",
        updated_at=payload.get("updated_at") or "",
        rate_limit_remaining=rate_limit_remaining,
    )


def _headers(token: str | None) -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "ai-automation-starter-kit/0.1",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers
