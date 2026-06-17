# Security Policy

## Supported Scope

This project is a local starter kit. The default templates are designed to run on explicit local files or user-provided configs.

## Default Protections

- Do not commit real secrets. Use `.env` locally and keep `.env.example` placeholder-only.
- Runtime data under `.tmp/`, local sources, delivery archives, `.venv`, and egg-info files are ignored by Git.
- The `research-agent` safe fetcher rejects localhost, loopback, private network, link-local, reserved, and metadata IP targets before network access.
- Failed URL logs mask sensitive query parameters such as `api_key`, `token`, `secret`, `key`, and `password`.
- External write/send workflows must be dry-run by default.
- Approval records must start as `pending` and `dry-run`.

## Reporting Issues

Open a GitHub issue with:

- affected template
- reproduction steps using sample data when possible
- expected behavior
- actual behavior

Do not include real API keys, private customer documents, or sensitive personal data in issue reports.

