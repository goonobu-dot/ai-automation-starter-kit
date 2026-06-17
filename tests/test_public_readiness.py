from pathlib import Path

from ai_automation_kit import __version__
from ai_automation_kit.cli import main


def test_cli_prints_version(capsys):
    exit_code = main(["--version"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert __version__ in captured.out


def test_public_repo_metadata_files_exist():
    expected_files = [
        "LICENSE",
        "SECURITY.md",
        "CONTRIBUTING.md",
        "CHANGELOG.md",
        "docs/PUBLISHING.md",
        ".github/workflows/ci.yml",
    ]
    for path in expected_files:
        assert Path(path).exists(), path


def test_ci_runs_tests_from_project_root():
    workflow = Path(".github/workflows/ci.yml").read_text()
    assert "python3 -m pytest -q" in workflow
    assert "python3 scripts/run_all_demos.py" in workflow


def test_security_policy_mentions_secrets_and_private_networks():
    policy = Path("SECURITY.md").read_text()
    assert "secrets" in policy.lower()
    assert "private network" in policy.lower()
    assert "dry-run" in policy.lower()

