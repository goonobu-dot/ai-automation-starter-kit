from pathlib import Path


def test_project_readme_leads_with_one_paste_beginner_entrance():
    text = Path("README.md").read_text()
    assert "AI Automation Starter Kit" in text
    assert "GitHub-data-driven AI agent skill kit" in text
    # One-paste Japanese entrance near the top.
    assert "日本語の方へ：まず、ダブルクリックだけ" in text
    assert "python3 scripts/first_start.py --open" in text
    assert "START_HERE.command" in text
    assert "START_WITH_AI.ja.txt" in text
    assert "ai-automation-kit start" in text
    assert "my-first-automation/START_HERE.html" in text
    assert "docs/FIRST_PROJECT.ja.html" in text
    assert "docs/FIRST_PROJECT.html" in text
    assert "docs/GETTING_STARTED.ja.md" in text
    assert "docs/INDEX.md" in text
    assert "最初から全部読まないでください" in text
    assert "最初の入口" in text
    # The Japanese section must appear before the English quick start.
    assert text.index("日本語の方へ") < text.index("English Quick Start")
    # English quick start.
    assert "Do not read everything first" in text
    assert "python3 -m venv .venv" in text
    assert "source .venv/bin/activate" in text
    assert "python3 -m ensurepip --upgrade" in text
    assert "python3 -m pip install --upgrade pip setuptools" in text
    assert "pip install -e ." in text
    assert "The CLI is optional" in text
    # Documentation is delegated to the index.
    assert "Documentation" in text
    assert "docs/SHOWCASE.md" in text
    assert "docs/demo.html" in text
    # Compact command reference keeps every command documented.
    assert "Command Reference" in text
    assert "ai-automation-kit onboard --business-area operations" in text
    assert "ai-automation-kit offer-pack --business-area operations" in text
    assert "ai-automation-kit client-ready --business-area operations" in text
    assert "ai-automation-kit github-discover --business-area operations" in text
    assert "ai-automation-kit research-agent" in text
    assert "ai-automation-kit docs-rag" in text
    assert "ai-automation-kit internal-ai-workflow" in text
    assert "ai-automation-kit excel-to-internal-app" in text
    assert "ai-automation-kit delivery-pipeline" in text
    assert "python3 scripts/run_all_demos.py" in text
    assert "examples/research-agent/github_repos.json" in text
    assert "GITHUB_TOKEN" in text
    # Key generated artifacts stay discoverable.
    assert "What You Get" in text
    assert "executive_decision_brief.md" in text
    assert "pilot_scorecard.csv" in text
    assert "offer_pack/" in text
    assert "client-ready/" in text
    assert "statement_of_work.md" in text
    assert "pricing_model.md" in text
    assert "roi_calculator.csv" in text
    assert "implementation_readiness_score.json" in text
    assert "maintenance_plan.md" in text
    assert "value_realization_plan.md" in text
    assert "value_measurement_report.md" in text
    assert "stakeholder_rollout_map.md" in text
    assert "risk_exception_register.md" in text
    assert "operational_audit_plan.md" in text
    assert "artifact_index.md" in text
    assert "adapter_starter/" in text
    assert "How This Fits With Local Agent Workbenches" in text
    assert "Safety Defaults" in text
    assert "Public Release Readiness" in text
    # The old giant feature listing must stay retired.
    assert "3-Minute Walkthrough" not in text
    assert len(text) < 25000


def test_one_command_start_has_separate_japanese_and_english_browser_guides():
    japanese = Path("docs/FIRST_PROJECT.ja.html").read_text(encoding="utf-8")
    english = Path("docs/FIRST_PROJECT.html").read_text(encoding="utf-8")

    assert '<html lang="ja">' in japanese
    assert "一行を貼り付ける" in japanese
    assert "ダブルクリック" in japanese
    assert "START_HERE.command" in japanese
    assert "START_WITH_AI.ja.txt" in japanese
    assert "python3 scripts/first_start.py --open" in japanese
    assert "見本データ" in japanese
    assert "外部送信しません" in japanese
    assert "収益を保証" in japanese
    assert "Paste one line" in english
    assert "double-click" in english
    assert "START_HERE_WINDOWS.bat" in english
    assert "python3 scripts/first_start.py --open --language en" in english
    assert "sample data" in english
    assert "does not send anything externally" in english
    assert "does not guarantee income" in english
    assert "一行を貼り付ける" not in english


def test_project_readme_and_index_link_the_automation_proof_lab():
    readme = Path("README.md").read_text(encoding="utf-8")
    index = Path("docs/INDEX.md").read_text(encoding="utf-8")

    assert "docs/AUTOMATION_PROOF_LAB.ja.html" in readme
    assert "docs/AUTOMATION_PROOF_LAB.html" in readme
    assert "AUTOMATION_PROOF_LAB.ja.html" in index
    assert "AUTOMATION_PROOF_LAB.html" in index
    assert "autopilot-proof-lab" in readme


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
    assert "offer_pack/" in english
    assert "does not guarantee income" in english

    assert "やさしい解説" in japanese
    assert "このプロジェクトは何か" in japanese
    assert "何のために作ったのか" in japanese
    assert "どうやって使うのか" in japanese
    assert "普通のAIチャットと何が違うのか" in japanese
    assert "run_summary.md" in japanese
    assert "executive_decision_brief.md" in japanese
    assert "pilot_scorecard.csv" in japanese
    assert "offer_pack/" in japanese
    assert "収益を保証するものではありません" in japanese


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
