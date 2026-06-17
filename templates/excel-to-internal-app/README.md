# excel-to-internal-app

## Purpose

Convert CSV or spreadsheet-based business tracking into a database schema, admin view plan, and workflow outline.

## Inputs

- CSV or XLSX file
- Business process name
- Notification and approval rules

## Outputs

- `artifact_index.md`
- `schema.sql`
- `fields.json`
- `data-quality-report.json`
- `admin-view.md`
- `migration-report.md`
- `app-spec.md`
- Optional n8n/NocoDB/Directus configuration

## Required Connectors

- Later: NocoDB, Directus, Appwrite, n8n

## Safety Defaults

- Uploaded business data is ignored by Git
- Generated schemas are editable text files
- External app creation is dry-run until explicitly approved

## Current Status

Executable. Generates schema, field metadata, data-quality report, admin view plan, migration report, app spec, artifact index, and run history from a CSV config.

## Next Implementation Step

Add optional XLSX input support and export adapters for NocoDB or Directus.
