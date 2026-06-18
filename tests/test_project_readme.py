from pathlib import Path


def test_project_readme_has_public_quickstart_and_all_templates():
    text = Path("README.md").read_text()
    assert "AI Automation Starter Kit" in text
    assert "What Is This?" in text
    assert "Who Is This For?" in text
    assert "What You Get" in text
    assert "Beginner-Friendly Guides" in text
    assert "docs/BEGINNER_GUIDE.md" in text
    assert "docs/BEGINNER_GUIDE.ja.md" in text
    assert "3-Minute Walkthrough" in text
    assert "Example Use Cases" in text
    assert "GitHub-data-driven AI automation starter kit" in text
    assert "executive_decision_brief.md" in text
    assert "pilot_scorecard.csv" in text
    assert "python3 -m venv .venv" in text
    assert "source .venv/bin/activate" in text
    assert "python3 -m ensurepip --upgrade" in text
    assert "python3 -m pip install --upgrade pip setuptools" in text
    assert "pip install -e ." in text
    assert "ai-automation-kit onboard --business-area operations" in text
    assert "ai-automation-kit research-agent" in text
    assert "ai-automation-kit github-discover --business-area sales" in text
    assert "business_automation_plan.md" in text
    assert "value_realization_plan.md" in text
    assert "value_measurement_report.md" in text
    assert "stakeholder_rollout_map.md" in text
    assert "risk_exception_register.md" in text
    assert "operational_audit_plan.md" in text
    assert "artifact_index.md" in text
    assert "adoption_shortlist.md" in text
    assert "adapter_blueprint.md" in text
    assert "adapter_starter/" in text
    assert "candidate_briefs/" in text
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


def test_beginner_guides_explain_project_in_english_and_japanese():
    english = Path("docs/BEGINNER_GUIDE.md").read_text()
    japanese = Path("docs/BEGINNER_GUIDE.ja.md").read_text()

    assert "Beginner-Friendly Guide" in english
    assert "What this project is" in english
    assert "Why it exists" in english
    assert "How to use it" in english
    assert "How it is different from normal chat AI" in english
    assert "run_summary.md" in english
    assert "executive_decision_brief.md" in english
    assert "pilot_scorecard.csv" in english

    assert "やさしい解説" in japanese
    assert "このプロジェクトは何か" in japanese
    assert "何のために作ったのか" in japanese
    assert "どうやって使うのか" in japanese
    assert "普通のAIチャットと何が違うのか" in japanese
    assert "run_summary.md" in japanese
    assert "executive_decision_brief.md" in japanese
    assert "pilot_scorecard.csv" in japanese


def test_showcase_doc_explains_demo_flow_and_outputs():
    text = Path("docs/SHOWCASE.md").read_text()
    assert "AI Automation Starter Kit Showcase" in text
    assert "30-Second Summary" in text
    assert "What A Visitor Should Understand" in text
    assert "Audience" in text
    assert "Outcome" in text
    assert "executive_decision_brief.md" in text
    assert "pilot_scorecard.csv" in text
    assert "Discover" in text
    assert "Decide" in text
    assert "Deliver" in text
    assert "business_automation_plan.md" in text
    assert "value_realization_plan.md" in text
    assert "value_measurement_report.md" in text
    assert "stakeholder_rollout_map.md" in text
    assert "risk_exception_register.md" in text
    assert "operational_audit_plan.md" in text
    assert "go/no-go criteria" in text
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


def test_publishing_doc_uses_release_smoke_entrypoint():
    text = Path("docs/PUBLISHING.md").read_text()
    assert "python3 scripts/public_release_audit.py" in text
    assert "python3 scripts/release_smoke.py" in text
    assert "--skip-github" in text
    assert "release-smoke" in text
    assert "release-smoke-discovery" not in text


def test_pyproject_exposes_console_script():
    text = Path("pyproject.toml").read_text()
    assert "[build-system]" in text
    assert "setuptools" in text
    assert 'readme = "README.md"' in text
    assert 'license = {file = "LICENSE"}' in text
    assert "keywords =" in text
    assert "Programming Language :: Python :: 3" in text
    assert "[project.scripts]" in text
    assert 'ai-automation-kit = "ai_automation_kit.cli:main"' in text


def test_legacy_editable_install_setup_py_exists():
    text = Path("setup.py").read_text()
    assert "setuptools" in text
    assert "long_description" in text
    assert 'license="MIT"' in text
    assert 'description="Starter kit for reusable AI automation workflows."' in text
    assert "ai_automation_kit.cli:main" in text
