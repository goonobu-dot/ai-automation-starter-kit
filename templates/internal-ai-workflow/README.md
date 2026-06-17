# internal-ai-workflow

## Purpose

Turn a single internal business task, such as inquiry reply drafting, into an AI-assisted workflow with approval.

## Inputs

- Inquiry text, meeting notes, daily reports, or customer notes
- Optional knowledge sources from `docs-rag`

## Outputs

- Draft reply or task list
- Approval request
- Run history
- Optional n8n/Dify export

## Required Connectors

- Later: n8n, Dify, Open WebUI, Ollama, email or chat adapters

## Safety Defaults

- External send/write actions are dry-run by default
- Human approval is required before external actions
- Secrets must come from environment variables only

## Current Status

Executable inquiry-reply fixture. It reads a JSON config with `inquiry_text` and optional `customer_name`, then writes `draft_reply.md`, `draft_reply.json`, `approval_request.json`, and `runs/<run_id>.json`.

## Next Implementation Step

Wire the executable fixture into CLI scaffolding and optional connector exports.
