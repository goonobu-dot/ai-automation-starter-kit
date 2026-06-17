# research-agent

## Purpose

Generate a cited Markdown, HTML, and JSON research report from explicit source URLs or local files.

## Inputs

- Research topic
- Explicit `file://`, `http://`, or `https://` source URIs
- Output directory

## Outputs

- `report.md`
- `report.html`
- `report.json`
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

Executable in Phase 1.

## Next Implementation Step

Add optional search provider adapters after the explicit-URL workflow is stable.

