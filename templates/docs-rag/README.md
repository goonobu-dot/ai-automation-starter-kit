# docs-rag

## Purpose

Convert company documents into searchable knowledge with source-backed answers.

## Inputs

- Phase 2 MVP: Markdown files
- Later: PDF, DOCX, XLSX, PPTX, and HTML files
- Optional metadata such as department, owner, and version

## Outputs

- Normalized Markdown documents
- Chunk records
- Source map
- Rooted answers with file references

## Required Connectors

- Phase 2 MVP: local Markdown reader
- Later: MarkItDown, Docling, LangChain, Supabase or local vector store

## Safety Defaults

- Customer documents are never committed
- Local indexes are ignored by Git
- Answers without evidence must be marked as insufficiently grounded

## Current Status

Executable for local Markdown fixtures.

## Next Implementation Step

Add document conversion adapters for PDF/DOCX and improve retrieval beyond deterministic keyword overlap.
