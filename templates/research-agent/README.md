# research-agent

## Purpose

Generate a cited Markdown, HTML, and JSON research report from explicit source URLs or local files.

## Inputs

- Research topic
- Explicit `file://`, `http://`, or `https://` source URIs
- Output directory

## Outputs

- `artifact_index.md`
- `report.md`
- `report.html`
- `report.json`
- `failed_fetches.json`
- Optional GitHub ranking artifacts such as `github_candidates.md`, `adoption_shortlist.md`, `adapter_blueprint.md`, and `adapter_starter/`
- `runs/<run_id>.json`
- `sources/<source_id>.json`

## Required Connectors

- Phase 1: local file and safe HTTP(S) fetcher
- Later: Firecrawl, Crawl4AI, browser-use, Playwright, MCP

## Safety Defaults

- No broad crawling in Phase 1
- Private network URLs are rejected
- Secret query values are masked in logs
- Runtime outputs are ignored by Git defaults

## Current Status

Executable. Supports explicit sources, known GitHub repositories, GitHub repository search, candidate ranking, adapter blueprint generation, adapter starter generation, and query recovery when searches return no candidates.

## Next Implementation Step

Add optional non-GitHub search provider adapters after the current GitHub discovery workflow is stable.
