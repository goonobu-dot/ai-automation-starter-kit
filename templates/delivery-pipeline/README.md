# delivery-pipeline

## Purpose

Generate repeatable delivery assets for AI automation projects: README, environment sample, operations guide, smoke test, and checklist.

## Inputs

- Project type
- Customer-safe project name
- Required environment variables
- Selected template
- Operational notes

## Outputs

- `README.md`
- `.env.example`
- `docker-compose.yml`
- `docs/operation-manual.md`
- `docs/delivery-checklist.md`
- `tests/smoke-test.md`

## Required Connectors

- Later: Docker Compose, GitHub Actions, Terraform, Ansible

## Safety Defaults

- `.env` is never generated with real secrets
- Delivery archives are ignored by Git
- Customer identifiers should be scrubbed in public examples

## Current Status

Executable. Generates a delivery package from JSON config with placeholder-only environment samples.

## Next Implementation Step

Add CLI routing when the command surface is opened for template expansion.
