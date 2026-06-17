from __future__ import annotations

from dataclasses import dataclass
from ipaddress import ip_address
from pathlib import Path
from urllib.parse import unquote, urlsplit
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class FetchPolicy:
    max_bytes: int = 1_000_000
    timeout_seconds: int = 10
    user_agent: str = "ai-automation-starter-kit/0.1"


@dataclass(frozen=True)
class FetchedContent:
    uri: str
    content: str
    content_type: str


def fetch_uri(uri: str, policy: FetchPolicy) -> FetchedContent:
    parts = urlsplit(uri)
    if parts.scheme == "file":
        path = Path(unquote(parts.path))
        content = path.read_text(encoding="utf-8")
        return FetchedContent(uri=uri, content=content, content_type="text/html")

    if parts.scheme in {"http", "https"}:
        _reject_private_network_target(parts.hostname)
        request = Request(uri, headers={"User-Agent": policy.user_agent})
        with urlopen(request, timeout=policy.timeout_seconds) as response:
            content_type = response.headers.get("Content-Type", "application/octet-stream")
            raw = response.read(policy.max_bytes + 1)
        if len(raw) > policy.max_bytes:
            raise ValueError("response exceeds max bytes")
        if not _is_text_content(content_type):
            raise ValueError(f"unsupported content type: {content_type}")
        return FetchedContent(uri=uri, content=raw.decode("utf-8", errors="replace"), content_type=content_type)

    raise ValueError(f"unsupported URI scheme: {parts.scheme}")


def _reject_private_network_target(hostname: str | None) -> None:
    if not hostname:
        raise ValueError("missing hostname")

    lowered = hostname.lower()
    if lowered in {"localhost", "metadata.google.internal"} or lowered.endswith(".localhost"):
        raise ValueError("private network target rejected")

    try:
        address = ip_address(lowered)
    except ValueError:
        return

    if (
        address.is_loopback
        or address.is_private
        or address.is_link_local
        or address.is_reserved
        or address.is_unspecified
    ):
        raise ValueError("private network target rejected")


def _is_text_content(content_type: str) -> bool:
    lowered = content_type.lower()
    return (
        lowered.startswith("text/")
        or "application/json" in lowered
        or "application/xhtml+xml" in lowered
        or "application/xml" in lowered
    )
