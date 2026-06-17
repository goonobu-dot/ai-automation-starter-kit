from pathlib import Path


def test_project_readme_has_public_quickstart_and_all_templates():
    text = Path("README.md").read_text()
    assert "AI Automation Starter Kit" in text
    assert "python3 -m venv .venv" in text
    assert "source .venv/bin/activate" in text
    assert "python3 -m ensurepip --upgrade" in text
    assert "python3 -m pip install --upgrade pip setuptools" in text
    assert "pip install -e ." in text
    assert "ai-automation-kit research-agent" in text
    assert "ai-automation-kit github-discover --business-area sales" in text
    assert "business_automation_plan.md" in text
    assert "examples/research-agent/github_repos.json" in text
    assert "GITHUB_TOKEN" in text
    assert "ai-automation-kit docs-rag" in text
    assert "ai-automation-kit internal-ai-workflow" in text
    assert "ai-automation-kit excel-to-internal-app" in text
    assert "ai-automation-kit delivery-pipeline" in text
    assert "python3 scripts/run_all_demos.py" in text
    assert "How This Differs From Chat AI" in text
    assert "1-Minute Demo" in text
    assert "Example Output" in text
    assert "How This Fits With Local Agent Workbenches" in text
    assert "Public Release Readiness" in text
    assert "docs/SHOWCASE.md" in text
    assert "docs/demo.html" in text


def test_showcase_doc_explains_demo_flow_and_outputs():
    text = Path("docs/SHOWCASE.md").read_text()
    assert "AI Automation Starter Kit Showcase" in text
    assert "Discover" in text
    assert "Decide" in text
    assert "Deliver" in text
    assert "business_automation_plan.md" in text
    assert "local-agent-workbench" in text
    assert "claude-code-workbench" in text


def test_static_demo_html_exists_and_shows_value_story():
    text = Path("docs/demo.html").read_text()
    assert "<title>AI Automation Starter Kit Demo</title>" in text
    assert "GitHub Discovery" in text
    assert "Business Automation Plan" in text
    assert "Five Reusable Templates" in text
    assert "Run This Demo" in text
    assert "ai-automation-kit github-discover --business-area operations" in text
    assert "Manual handoffs reduced" in text
    assert "No external services required for local examples" in text


def test_pyproject_exposes_console_script():
    text = Path("pyproject.toml").read_text()
    assert "[build-system]" in text
    assert "setuptools" in text
    assert "[project.scripts]" in text
    assert 'ai-automation-kit = "ai_automation_kit.cli:main"' in text


def test_legacy_editable_install_setup_py_exists():
    text = Path("setup.py").read_text()
    assert "setuptools" in text
    assert "ai_automation_kit.cli:main" in text
