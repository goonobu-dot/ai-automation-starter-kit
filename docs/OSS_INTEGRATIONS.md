# OSS Integrations Policy

This starter kit references popular OSS and source-available tools as integration targets. Phase 1 is adapter-only: it does not vendor, redistribute, or bundle those projects.

## Policy

- Review each integration license before bundling code, Docker images, workflow exports, or templates derived from that project.
- Keep third-party API keys in environment variables or `.env`; never commit real secrets.
- Treat n8n, Dify, Directus, Open WebUI, Supabase, Ollama, Firecrawl, Crawl4AI, browser-use, Playwright, MarkItDown, Docling, FFmpeg, and whisper.cpp as external integrations unless a later license review says otherwise.
- Document commercial-use and redistribution notes before publishing packaged deployments.

## Initial Status

| Integration | Phase 1 status | Bundled? | License note |
|---|---|---:|---|
| Firecrawl | referenced | no | review before hosted/API adapter release |
| Crawl4AI | referenced | no | review before adapter release |
| browser-use | referenced | no | review before adapter release |
| Playwright | referenced | no | review before browser automation release |
| MarkItDown | referenced | no | review before document pipeline release |
| Docling | referenced | no | review before document pipeline release |
| n8n | referenced | no | source-available/fair-code terms require review |
| Dify | referenced | no | license terms require review |
| Directus | referenced | no | source-available terms require review |
| Open WebUI | referenced | no | license/branding terms require review |
| FFmpeg | optional local executable | no | obtain separately and review the selected build configuration |
| whisper.cpp | optional local executable | no | MIT-licensed upstream; model files are downloaded separately and integrity-checked |
