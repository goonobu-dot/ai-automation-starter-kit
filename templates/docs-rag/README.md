# docs-rag

## Purpose

Convert company documents into searchable knowledge with source-backed answers.

## Inputs

- Phase 2 MVP: Markdown files
- Later: PDF, DOCX, XLSX, PPTX, and HTML files
- Optional metadata such as department, owner, and version

## Outputs

- `artifact_index.md`
- `answer.md`
- `answer.json`
- Normalized Markdown documents
- `chunks.jsonl`
- `source_map.json`

## Required Connectors

- Phase 2 MVP: local Markdown reader
- Later: MarkItDown, Docling, LangChain, Supabase or local vector store

## Safety Defaults

- Customer documents are never committed
- Local indexes are ignored by Git
- Answers without evidence must be marked as insufficiently grounded

## Current Status

Executable for local Markdown fixtures. Answers include citations, confidence, usage gate, operator checklist, and insufficient-evidence handling.

## Next Implementation Step

Add document conversion adapters for PDF/DOCX and improve retrieval beyond deterministic keyword overlap.
