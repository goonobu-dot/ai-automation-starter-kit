import json
from base64 import b64encode
from urllib.error import HTTPError

import pytest

from ai_automation_kit.core.github import (
    GitHubRepo,
    fetch_github_readme,
    fetch_github_repo,
    github_repo_to_finding,
    search_github_repositories,
)


class FakeResponse:
    def __init__(self, payload, status=200, headers=None):
        self.payload = payload
        self.status = status
        self.headers = headers or {"X-RateLimit-Remaining": "59"}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return None

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def test_fetch_github_repo_reads_public_repo_metadata(monkeypatch):
    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["headers"] = dict(request.header_items())
        return FakeResponse(
            {
                "full_name": "octocat/Hello-World",
                "html_url": "https://github.com/octocat/Hello-World",
                "description": "Example repo",
                "stargazers_count": 42,
                "forks_count": 7,
                "open_issues_count": 3,
                "license": {"spdx_id": "MIT"},
                "topics": ["example", "demo"],
                "language": "Python",
                "updated_at": "2026-06-17T00:00:00Z",
            }
        )

    monkeypatch.setattr("ai_automation_kit.core.github.urlopen", fake_urlopen)

    repo = fetch_github_repo("octocat/Hello-World", token="token-value")

    assert captured["url"] == "https://api.github.com/repos/octocat/Hello-World"
    assert captured["headers"]["Authorization"] == "Bearer token-value"
    assert repo.full_name == "octocat/Hello-World"
    assert repo.stars == 42
    assert repo.license == "MIT"


def test_fetch_github_repo_rejects_invalid_repo_name():
    with pytest.raises(ValueError, match="owner/repo"):
        fetch_github_repo("not-a-repo")


def test_fetch_github_readme_decodes_repository_readme(monkeypatch):
    captured = {}
    encoded = b64encode(b"# Example\n\nInstall with pip.").decode("ascii")

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        return FakeResponse(
            {
                "name": "README.md",
                "path": "README.md",
                "encoding": "base64",
                "size": 27,
                "html_url": "https://github.com/octocat/Hello-World/blob/main/README.md",
                "download_url": "https://raw.githubusercontent.com/octocat/Hello-World/main/README.md",
                "content": encoded,
            }
        )

    monkeypatch.setattr("ai_automation_kit.core.github.urlopen", fake_urlopen)

    readme = fetch_github_readme("octocat/Hello-World")

    assert captured["url"] == "https://api.github.com/repos/octocat/Hello-World/readme"
    assert readme["path"] == "README.md"
    assert readme["text"] == "# Example\n\nInstall with pip."
    assert readme["html_url"].endswith("/README.md")


def test_search_github_repositories_returns_star_sorted_results(monkeypatch):
    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["headers"] = dict(request.header_items())
        return FakeResponse(
            {
                "total_count": 2,
                "incomplete_results": False,
                "items": [
                    {
                        "full_name": "modelcontextprotocol/servers",
                        "html_url": "https://github.com/modelcontextprotocol/servers",
                        "description": "MCP servers",
                        "stargazers_count": 50000,
                        "forks_count": 4000,
                        "open_issues_count": 120,
                        "license": {"spdx_id": "MIT"},
                        "topics": ["mcp", "automation"],
                        "language": "Python",
                        "updated_at": "2026-06-17T00:00:00Z",
                    },
                    {
                        "full_name": "langchain-ai/langgraph",
                        "html_url": "https://github.com/langchain-ai/langgraph",
                        "description": "Agent orchestration",
                        "stargazers_count": 40000,
                        "forks_count": 3000,
                        "open_issues_count": 90,
                        "license": None,
                        "topics": [],
                        "language": "Python",
                        "updated_at": "2026-06-16T00:00:00Z",
                    },
                ],
            },
            headers={"X-RateLimit-Remaining": "28"},
        )

    monkeypatch.setattr("ai_automation_kit.core.github.urlopen", fake_urlopen)

    result = search_github_repositories(
        query="topic:ai-agents stars:>1000",
        sort="stars",
        order="desc",
        per_page=2,
        token="token-value",
    )

    assert captured["url"].startswith("https://api.github.com/search/repositories?")
    assert "q=topic%3Aai-agents+stars%3A%3E1000" in captured["url"]
    assert "sort=stars" in captured["url"]
    assert captured["headers"]["Authorization"] == "Bearer token-value"
    assert result["total_count"] == 2
    assert result["incomplete_results"] is False
    assert result["rate_limit_remaining"] == "28"
    assert [repo.full_name for repo in result["repositories"]] == [
        "modelcontextprotocol/servers",
        "langchain-ai/langgraph",
    ]


def test_search_github_repositories_rejects_invalid_sort():
    with pytest.raises(ValueError, match="sort"):
        search_github_repositories("topic:ai-agents", sort="created")


def test_github_repo_to_finding_summarizes_repo():
    repo = GitHubRepo(
        full_name="octocat/Hello-World",
        html_url="https://github.com/octocat/Hello-World",
        description="Example repo",
        stars=42,
        forks=7,
        open_issues=3,
        license="MIT",
        topics=["example"],
        language="Python",
        updated_at="2026-06-17T00:00:00Z",
        rate_limit_remaining="59",
    )

    finding = github_repo_to_finding(repo)

    assert finding["title"] == "octocat/Hello-World"
    assert finding["uri"] == "https://github.com/octocat/Hello-World"
    assert "42 stars" in finding["summary"]
    assert finding["metadata"]["rate_limit_remaining"] == "59"
