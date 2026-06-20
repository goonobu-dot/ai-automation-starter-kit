from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAX_REQUIRED_FILE_BYTES = 500_000

REQUIRED_FILES = [
    "README.md",
    "LICENSE",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
    "pyproject.toml",
    "setup.py",
    ".gitignore",
    ".github/dependabot.yml",
    ".github/workflows/ci.yml",
    "docs/PUBLISHING.md",
    "docs/RELEASE_CHECKLIST.md",
    "docs/GITHUB_DATA.md",
    "docs/SHOWCASE.md",
    "docs/OSS_INTEGRATIONS.md",
    "scripts/release_smoke.py",
    "scripts/run_all_demos.py",
]

REQUIRED_EXAMPLE_FILES = [
    "examples/research-agent/sample_research.json",
    "examples/research-agent/github_search.json",
    "examples/docs-rag/sample_docs_rag.json",
    "examples/internal-ai-workflow/sample_inquiry.json",
    "examples/excel-to-internal-app/sample_app.json",
    "examples/delivery-pipeline/sample_delivery_pipeline.json",
]

REQUIRED_TEMPLATE_READMES = [
    "templates/research-agent/README.md",
    "templates/docs-rag/README.md",
    "templates/internal-ai-workflow/README.md",
    "templates/excel-to-internal-app/README.md",
    "templates/delivery-pipeline/README.md",
]

REQUIRED_EXPECTED_OUTPUT_FILES = [
    "examples/research-agent/expected/report.md",
    "examples/docs-rag/expected/answer.md",
    "examples/internal-ai-workflow/expected/draft_reply.md",
    "examples/excel-to-internal-app/expected/migration-report.md",
    "examples/delivery-pipeline/expected/delivery-checklist.md",
    "examples/delivery-pipeline/expected/release-plan.md",
    "examples/delivery-pipeline/expected/rollback-plan.md",
]

REQUIRED_GITIGNORE_PATTERNS = [
    ".tmp/",
    ".venv/",
    "build/",
    "dist/",
    "*.egg-info/",
    "__pycache__/",
]

FORBIDDEN_TRACKED_PATHS = [
    "build",
    "dist",
    ".tmp",
    ".venv",
    ".pytest_cache",
    "__pycache__",
]

REQUIRED_README_SNIPPETS = [
    "ai-automation-kit onboard",
    "ai-automation-kit offer-pack",
    "ai-automation-kit client-ready",
    "ai-automation-kit flows list",
    "ai-automation-kit flows install",
    "ai-automation-kit github-discover",
    "python3 scripts/release_smoke.py",
    "Public Release Readiness",
    "value_measurement_report.md",
    "enterprise_readiness.md",
]

REQUIRED_CLI_DOC_SNIPPETS = [
    "python3 -m pip install -e .",
    "python3 scripts/run_all_demos.py",
    "ai-automation-kit --version",
    "ai-automation-kit doctor",
    "ai-automation-kit onboard --business-area operations",
    "ai-automation-kit offer-pack --business-area operations",
    "ai-automation-kit client-ready --business-area operations",
    "ai-automation-kit flows list",
    "ai-automation-kit flows install",
    "ai-automation-kit github-discover --business-area operations",
    "docs/SHOWCASE.md",
    "docs/demo.html",
]

REQUIRED_GENERATED_ARTIFACT_SNIPPETS = [
    "executive_decision_brief.md",
    "pilot_scorecard.csv",
    "value_measurement_report.md",
    "operational_audit_plan.md",
    "risk_exception_register.md",
    "stakeholder_rollout_map.md",
    "offer_pack/",
    "client-ready/",
    "statement_of_work.md",
    "pricing_model.md",
    "roi_calculator.csv",
    "implementation_readiness_score.json",
    "maintenance_plan.md",
    "flow.yaml",
    "workflow_map.mmd",
    "scripts/run_dry_run.py",
]

REQUIRED_PYPROJECT_SNIPPETS = [
    "keywords =",
    "classifiers =",
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
]

REQUIRED_ENTRYPOINT_SNIPPETS = [
    "[project.scripts]",
    'ai-automation-kit = "ai_automation_kit.cli:main"',
]

REQUIRED_SECURITY_SNIPPETS = [
    "secrets",
    "private network",
    "dry-run",
]

REQUIRED_OSS_POLICY_SNIPPETS = [
    "adapter-only",
    "does not vendor",
    "license review",
]

REQUIRED_CI_SNIPPETS = [
    "permissions:",
    "contents: read",
    "actions/checkout@v5",
    "actions/setup-python@v6",
    "python3 scripts/release_smoke.py --skip-github",
]

REQUIRED_PUBLISHING_SNIPPETS = [
    "--skip-github",
    "Suggested First Release",
    "v0.1.0",
]

REQUIRED_CHANGELOG_SNIPPETS = [
    "Unreleased",
    "0.1.0",
]

REQUIRED_CONTRIBUTING_SNIPPETS = [
    "python3 -m pytest -q",
    "python3 scripts/run_all_demos.py",
    "Add or update tests",
]

REQUIRED_LICENSE_SNIPPETS = [
    "MIT License",
    "Permission is hereby granted",
]

REQUIRED_DEMO_RUNNER_SNIPPETS = [
    "research-agent",
    "docs-rag",
    "internal-ai-workflow",
    "excel-to-internal-app",
    "delivery-pipeline",
]

REQUIRED_PACKAGING_FILES = [
    "pyproject.toml",
    "setup.py",
]

REQUIRED_PACKAGING_SNIPPETS = {
    "pyproject.toml": ["setuptools", "[project.scripts]", "ai-automation-kit"],
    "setup.py": ["setuptools", "console_scripts", "ai-automation-kit"],
}

REQUIRED_STATIC_DEMO_SNIPPETS = [
    "AI Automation Starter Kit Demo",
    "GitHub Discovery",
    "Business Automation Plan",
    "Five Reusable Templates",
]

SECRET_SCAN_PATHS = [
    "README.md",
    "docs/PUBLISHING.md",
    "docs/RELEASE_CHECKLIST.md",
    "docs/GITHUB_DATA.md",
    "docs/SHOWCASE.md",
    "examples",
    "templates",
]

FORBIDDEN_SECRET_SNIPPETS = [
    "sk-",
    "ghp_",
    "BEGIN PRIVATE KEY",
    "AWS_SECRET_ACCESS_KEY=",
    "/Users/",
    "file:///Users/",
]

REQUIRED_RELEASE_SMOKE_SNIPPETS = [
    ("public_release_audit.py", "public_release_audit.py"),
    ("pip wheel", '"pip", "wheel"'),
    ("_verify_wheel_install", "_verify_wheel_install"),
    ("onboard", "onboard"),
    ("onboarding_summary.md", "onboarding_summary.md"),
    ("offer-pack", "offer-pack"),
    ("offer_pack/README.md", '"offer_pack" / "README.md"'),
    ("proposal.md", "proposal.md"),
    ("pricing_model.md", "pricing_model.md"),
    ("client-ready", "client-ready"),
    ("roi_calculator.csv", "roi_calculator.csv"),
    ("implementation_readiness_score.json", "implementation_readiness_score.json"),
    ("maintenance_plan.md", "maintenance_plan.md"),
    ("marketplace_profile.md", "marketplace_profile.md"),
    ("flows install", "flows"),
    ("flow.yaml", "flow.yaml"),
    ("workflow_map.mmd", "workflow_map.mmd"),
    ("github-discover", "github-discover"),
    ("adapter_starter/smoke_test.py", "adapter_starter/smoke_test.py"),
    ("manual_review_pack.md", "manual_review_pack.md"),
    ("executive_decision_brief.md", "executive_decision_brief.md"),
    ("pilot_scorecard.csv", "pilot_scorecard.csv"),
]

REQUIRED_GITHUB_SMOKE_SNIPPETS = [
    ("executive_decision_brief.md", "executive_decision_brief.md"),
    ("pilot_scorecard.csv", "pilot_scorecard.csv"),
    ("enterprise_readiness.md", "enterprise_readiness.md"),
    ("value_realization_plan.md", "value_realization_plan.md"),
    ("value_measurement_report.md", "value_measurement_report.md"),
    ("stakeholder_rollout_map.md", "stakeholder_rollout_map.md"),
    ("risk_exception_register.md", "risk_exception_register.md"),
    ("operational_audit_plan.md", "operational_audit_plan.md"),
]

REQUIRED_RELEASE_EVIDENCE_SNIPPETS = [
    "doctor_report.md",
    "installed-doctor",
    "value_measurement_report.md",
    "Release Decision",
]


def main() -> int:
    failures: list[str] = []
    checks: list[str] = []

    for relative_path in REQUIRED_FILES:
        path = ROOT / relative_path
        if not path.exists():
            failures.append(f"missing required file: {relative_path}")
        elif path.stat().st_size == 0:
            failures.append(f"empty required file: {relative_path}")
        elif path.stat().st_size > MAX_REQUIRED_FILE_BYTES:
            failures.append(f"required file too large: {relative_path}")
        checks.append(relative_path)

    for relative_path in REQUIRED_EXAMPLE_FILES:
        if not (ROOT / relative_path).exists():
            failures.append(f"missing example file: {relative_path}")
        checks.append(relative_path)

    for relative_path in REQUIRED_TEMPLATE_READMES:
        if not (ROOT / relative_path).exists():
            failures.append(f"missing template README: {relative_path}")
        checks.append(relative_path)

    for relative_path in REQUIRED_EXPECTED_OUTPUT_FILES:
        if not (ROOT / relative_path).exists():
            failures.append(f"missing expected output file: {relative_path}")
        checks.append(relative_path)

    for relative_path in FORBIDDEN_TRACKED_PATHS:
        if not _is_ignored(relative_path):
            failures.append(f"forbidden generated path is not ignored: {relative_path}")
        checks.append(f"ignored::{relative_path}")

    gitignore = _read_text(".gitignore")
    for pattern in REQUIRED_GITIGNORE_PATTERNS:
        if pattern not in gitignore:
            failures.append(f".gitignore missing pattern: {pattern}")
        checks.append(pattern)

    readme = _read_text("README.md")
    for snippet in REQUIRED_README_SNIPPETS:
        if snippet not in readme:
            failures.append(f"README.md missing snippet: {snippet}")
        checks.append(f"README.md::{snippet}")

    for snippet in REQUIRED_CLI_DOC_SNIPPETS:
        if snippet not in readme:
            failures.append(f"README.md missing CLI snippet: {snippet}")
        checks.append(f"README.md::{snippet}")

    for snippet in REQUIRED_GENERATED_ARTIFACT_SNIPPETS:
        if snippet not in readme:
            failures.append(f"README.md missing generated artifact snippet: {snippet}")
        checks.append(f"README.md::{snippet}")

    pyproject = _read_text("pyproject.toml")
    for snippet in REQUIRED_PYPROJECT_SNIPPETS:
        if snippet not in pyproject:
            failures.append(f"pyproject.toml missing snippet: {snippet}")
        checks.append(f"pyproject.toml::{_label(snippet)}")

    for snippet in REQUIRED_ENTRYPOINT_SNIPPETS:
        if snippet not in pyproject:
            failures.append(f"pyproject.toml missing entrypoint snippet: {snippet}")
        checks.append(f"pyproject.toml::{_label(snippet)}")

    security = _read_text("SECURITY.md").lower()
    for snippet in REQUIRED_SECURITY_SNIPPETS:
        if snippet.lower() not in security:
            failures.append(f"SECURITY.md missing snippet: {snippet}")
        checks.append(f"SECURITY.md::{snippet}")

    oss_policy = _read_text("docs/OSS_INTEGRATIONS.md").lower()
    for snippet in REQUIRED_OSS_POLICY_SNIPPETS:
        if snippet.lower() not in oss_policy:
            failures.append(f"docs/OSS_INTEGRATIONS.md missing snippet: {snippet}")
        checks.append(f"docs/OSS_INTEGRATIONS.md::{snippet}")

    workflow = _read_text(".github/workflows/ci.yml")
    for snippet in REQUIRED_CI_SNIPPETS:
        if snippet not in workflow:
            failures.append(f".github/workflows/ci.yml missing snippet: {snippet}")
        checks.append(f".github/workflows/ci.yml::{_label(snippet)}")

    publishing = _read_text("docs/PUBLISHING.md")
    for snippet in REQUIRED_PUBLISHING_SNIPPETS:
        if snippet not in publishing:
            failures.append(f"docs/PUBLISHING.md missing snippet: {snippet}")
        checks.append(f"docs/PUBLISHING.md::{snippet}")

    changelog = _read_text("CHANGELOG.md")
    for snippet in REQUIRED_CHANGELOG_SNIPPETS:
        if snippet not in changelog:
            failures.append(f"CHANGELOG.md missing snippet: {snippet}")
        checks.append(f"CHANGELOG.md::{snippet}")

    contributing = _read_text("CONTRIBUTING.md")
    for snippet in REQUIRED_CONTRIBUTING_SNIPPETS:
        if snippet not in contributing:
            failures.append(f"CONTRIBUTING.md missing snippet: {snippet}")
        checks.append(f"CONTRIBUTING.md::{snippet}")

    license_text = _read_text("LICENSE")
    for snippet in REQUIRED_LICENSE_SNIPPETS:
        if snippet not in license_text:
            failures.append(f"LICENSE missing snippet: {snippet}")
        checks.append(f"LICENSE::{snippet}")

    demo_runner = _read_text("scripts/run_all_demos.py")
    for snippet in REQUIRED_DEMO_RUNNER_SNIPPETS:
        if snippet not in demo_runner:
            failures.append(f"scripts/run_all_demos.py missing snippet: {snippet}")
        checks.append(f"scripts/run_all_demos.py::{snippet}")

    for relative_path in REQUIRED_PACKAGING_FILES:
        packaging_text = _read_text(relative_path)
        for snippet in REQUIRED_PACKAGING_SNIPPETS[relative_path]:
            if snippet not in packaging_text:
                failures.append(f"{relative_path} missing packaging snippet: {snippet}")
            checks.append(f"{relative_path}::{_label(snippet)}")

    demo_html = _read_text("docs/demo.html")
    for snippet in REQUIRED_STATIC_DEMO_SNIPPETS:
        if snippet not in demo_html:
            failures.append(f"docs/demo.html missing snippet: {snippet}")
        checks.append(f"docs/demo.html::{snippet}")

    for relative_path in SECRET_SCAN_PATHS:
        scanned_text = _read_tree_text(relative_path)
        for snippet in FORBIDDEN_SECRET_SNIPPETS:
            if snippet in scanned_text:
                failures.append(f"potential secret marker found in {relative_path}: {snippet}")
        checks.append(f"secret-scan::{relative_path}")

    release_smoke = _read_text("scripts/release_smoke.py")
    for label, snippet in REQUIRED_RELEASE_SMOKE_SNIPPETS:
        if snippet not in release_smoke:
            failures.append(f"scripts/release_smoke.py missing snippet: {snippet}")
        checks.append(f"scripts/release_smoke.py::{label}")

    for label, snippet in REQUIRED_GITHUB_SMOKE_SNIPPETS:
        if snippet not in release_smoke:
            failures.append(f"scripts/release_smoke.py missing GitHub smoke snippet: {snippet}")
        checks.append(f"scripts/release_smoke.py::{label}")

    release_checklist = _read_text("docs/RELEASE_CHECKLIST.md")
    for snippet in REQUIRED_RELEASE_EVIDENCE_SNIPPETS:
        if snippet not in release_checklist:
            failures.append(f"docs/RELEASE_CHECKLIST.md missing evidence snippet: {snippet}")
        checks.append(f"docs/RELEASE_CHECKLIST.md::{snippet}")

    if failures:
        print("public release audit failed")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("public release audit passed")
    for item in checks:
        print(f"- {item}")
    return 0


def _read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def _label(snippet: str) -> str:
    return snippet.split("=", 1)[0].strip() if "=" in snippet else snippet


def _is_ignored(relative_path: str) -> bool:
    gitignore = _read_text(".gitignore").splitlines()
    normalized = relative_path.rstrip("/") + "/"
    return any(line.strip() == normalized for line in gitignore)


def _read_tree_text(relative_path: str) -> str:
    path = ROOT / relative_path
    if path.is_file():
        return path.read_text(encoding="utf-8")
    chunks: list[str] = []
    for child in sorted(path.rglob("*")):
        if child.is_file():
            chunks.append(child.read_text(encoding="utf-8"))
    return "\n".join(chunks)


if __name__ == "__main__":
    sys.exit(main())
