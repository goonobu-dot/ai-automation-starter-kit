from __future__ import annotations

from dataclasses import asdict, dataclass, field
from urllib.parse import parse_qsl, quote_plus, urlsplit, urlunsplit

SENSITIVE_QUERY_KEYS = {"api_key", "key", "token", "secret", "password"}


def mask_sensitive_uri(uri: str) -> str:
    parts = urlsplit(uri)
    if not parts.query:
        return uri
    masked_pairs = []
    for key, value in parse_qsl(parts.query, keep_blank_values=True):
        safe_value = "***" if key.lower() in SENSITIVE_QUERY_KEYS else quote_plus(value)
        masked_pairs.append(f"{quote_plus(key)}={safe_value}")
    masked_query = "&".join(masked_pairs)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, masked_query, parts.fragment))


@dataclass(frozen=True)
class Artifact:
    kind: str
    path: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class SourceRecord:
    source_id: str
    source_type: str
    uri: str
    title: str
    retrieved_at: str
    content_hash: str
    raw_path: str
    markdown_path: str
    metadata: dict

    def to_dict(self) -> dict:
        data = asdict(self)
        data["uri"] = mask_sensitive_uri(self.uri)
        return data


@dataclass(frozen=True)
class FailedFetch:
    uri: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {"uri": mask_sensitive_uri(self.uri), "reason": self.reason}


@dataclass(frozen=True)
class ApprovalRequest:
    action_id: str
    action_type: str
    payload: dict
    status: str = "pending"
    dry_run: bool = True

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class RunRecord:
    run_id: str
    template_name: str
    input: dict
    started_at: str
    finished_at: str | None
    status: str
    errors: list[str]
    artifacts: list[Artifact | dict] = field(default_factory=list)
    source_ids: list[str] = field(default_factory=list)
    failed_fetches: list[FailedFetch | dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["artifacts"] = [
            artifact.to_dict() if hasattr(artifact, "to_dict") else artifact
            for artifact in self.artifacts
        ]
        data["failed_fetches"] = [
            failed.to_dict() if hasattr(failed, "to_dict") else failed
            for failed in self.failed_fetches
        ]
        return data
