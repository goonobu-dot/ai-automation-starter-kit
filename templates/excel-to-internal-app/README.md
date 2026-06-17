# excel-to-internal-app

## Purpose

Convert CSV or spreadsheet-based business tracking into a database schema, admin view plan, and workflow outline.

## Inputs

- CSV or XLSX file
- Business process name
- Notification and approval rules

## Outputs

- `schema.sql`
- `fields.json`
- `admin-view.md`
- `migration-report.md`
- Optional n8n/NocoDB/Directus configuration

## Required Connectors

- Later: NocoDB, Directus, Appwrite, n8n

## Safety Defaults

- Uploaded business data is ignored by Git
- Generated schemas are editable text files
- External app creation is dry-run until explicitly approved

## Current Status

Contract only. Not executable in Phase 1.

## Next Implementation Step

Add a sample customer CSV and deterministic schema inference.

