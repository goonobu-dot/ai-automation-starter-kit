# internal-ai-workflow

## Purpose

Turn a single internal business task, such as inquiry reply drafting, into an AI-assisted workflow with approval.

## Inputs

- Inquiry text, meeting notes, daily reports, or customer notes
- Optional knowledge sources from `docs-rag`

## Outputs

- `artifact_index.md`
- `draft_reply.md`
- `draft_reply.json`
- `review-checklist.md`
- `approval_request.json`
- Run history under `runs/`
- Optional n8n/Dify export

## Required Connectors

- Later: n8n, Dify, Open WebUI, Ollama, email or chat adapters

## Safety Defaults

- External send/write actions are dry-run by default
- Human approval is required before external actions
- Secrets must come from environment variables only

## Current Status

Executable inquiry-reply fixture. It reads a JSON config with `inquiry_text` and optional `customer_name`, then writes draft, approval, SLA, owner role, escalation path, review checklist, artifact index, and run history.

## Next Implementation Step

Add optional connector exports while keeping send/write actions dry-run until approved.
