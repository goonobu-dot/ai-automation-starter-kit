from pathlib import Path
import subprocess
import sys

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
        "docs/RELEASE_CHECKLIST.md",
        ".github/workflows/ci.yml",
    ]
    for path in expected_files:
        assert Path(path).exists(), path


def test_readme_links_start_here_and_use_cases_docs():
    readme = Path("README.md").read_text()
    assert "docs/START_HERE.md" in readme
    assert "docs/START_HERE.ja.md" in readme
    assert "docs/USE_CASES.md" in readme
    assert "docs/USE_CASES.ja.md" in readme
    assert "docs/USER_MANUAL.md" in readme
    assert "docs/SELLING_AUTOMATION_GUIDE.md" in readme
    assert "docs/FLOW_SELECTION_GUIDE.md" in readme
    assert "docs/CLIENT_DEMO_SCRIPT.md" in readme
    assert "docs/REAL_WORLD_SETUP_GUIDE.md" in readme
    assert "docs/FAQ.md" in readme
    assert "docs/AI_RECEPTION_EMPLOYEE_PACK.md" in readme
    assert "docs/AI_RECEPTION_EMPLOYEE_PACK.ja.md" in readme
    assert "docs/AI_EMPLOYEE_ROADMAP.md" in readme
    assert "docs/AI_EMPLOYEE_ROADMAP.ja.md" in readme
    assert "docs/CLOUD_DEPLOYMENT_GUIDE.md" in readme
    assert "docs/CLOUD_DEPLOYMENT_GUIDE.ja.md" in readme
    assert "docs/CLOUD_BEGINNER_PLAYBOOK.md" in readme
    assert "docs/CLOUD_BEGINNER_PLAYBOOK.ja.md" in readme
    assert "docs/CONNECTOR_SETUP_GUIDE.md" in readme
    assert "docs/CONNECTOR_SETUP_GUIDE.ja.md" in readme
    assert "docs/CLOUD_TROUBLESHOOTING.md" in readme
    assert "docs/CLOUD_TROUBLESHOOTING.ja.md" in readme
    assert "docs/AI_GRILL_ME_GUIDE.md" in readme
    assert "docs/AI_GRILL_ME_GUIDE.ja.md" in readme
    assert "docs/GRILL_ME_PROMPTS.md" in readme
    assert "docs/GRILL_ME_PROMPTS.ja.md" in readme
    assert "docs/GRILL_ME_CHECKLISTS.md" in readme
    assert "docs/GRILL_ME_CHECKLISTS.ja.md" in readme


def test_start_here_and_use_cases_docs_help_first_time_users():
    english_start = Path("docs/START_HERE.md").read_text()
    japanese_start = Path("docs/START_HERE.ja.md").read_text()
    english_cases = Path("docs/USE_CASES.md").read_text()
    japanese_cases = Path("docs/USE_CASES.ja.md").read_text()
    assert "Start Here" in english_start
    assert "First 3 minutes" in english_start
    assert "まずここから" in japanese_start
    assert "最初の3分" in japanese_start
    assert "Use Cases" in english_cases
    assert "business automation" in english_cases
    assert "ユースケース" in japanese_cases
    assert "業務自動化" in japanese_cases


def test_english_manuals_match_japanese_business_proposal_coverage():
    expected_docs = {
        "docs/USER_MANUAL.md": ["business-launch", "complete-workspace", "Paid PoC", "share-check"],
        "docs/SELLING_AUTOMATION_GUIDE.md": ["dry-run PoC", "proposal", "human approval", "Do not promise income"],
        "docs/FLOW_SELECTION_GUIDE.md": ["invoice", "support reply", "avoid", "human approver"],
        "docs/CLIENT_DEMO_SCRIPT.md": ["Client Demo Script", "work queue", "approval queue", "continue, revise, or stop"],
        "docs/REAL_WORLD_SETUP_GUIDE.md": ["connector-doctor", "Gmail / Outlook", "Go Live", "rollback"],
        "docs/FAQ.md": ["business-launch", "side business", "dry-run", "production"],
    }
    for path, snippets in expected_docs.items():
        text = Path(path).read_text()
        assert len(text) > 800, path
        for snippet in snippets:
            assert snippet in text, f"{path} missing {snippet}"


def test_ai_reception_employee_docs_explain_setup_and_monetization_path():
    expected_docs = {
        "docs/AI_RECEPTION_EMPLOYEE_PACK.md": [
            "AI Reception Employee",
            "reception folder",
            "API keys",
            "operator_ui/index.html",
            "Paid dry-run PoC",
        ],
        "docs/AI_RECEPTION_EMPLOYEE_PACK.ja.md": [
            "AI受付社員",
            "受付フォルダ",
            "APIキー",
            "operator_ui/index.html",
            "有料dry-run PoC",
        ],
    }
    for path, snippets in expected_docs.items():
        text = Path(path).read_text()
        assert len(text) > 800, path
        for snippet in snippets:
            assert snippet in text, f"{path} missing {snippet}"


def test_ai_employee_roadmap_docs_explain_priority_and_exclusions():
    expected_docs = {
        "docs/AI_EMPLOYEE_ROADMAP.md": [
            "AI Reception Employee",
            "Internal FAQ",
            "Sales Research",
            "Do not start with outbound sales",
            "multi-department",
        ],
        "docs/AI_EMPLOYEE_ROADMAP.ja.md": [
            "AI受付社員",
            "社内FAQ",
            "営業リサーチ",
            "アウトバウンド営業から始めない",
            "多部門",
        ],
    }
    for path, snippets in expected_docs.items():
        text = Path(path).read_text()
        assert len(text) > 800, path
        for snippet in snippets:
            assert snippet in text, f"{path} missing {snippet}"


def test_cloud_beginner_docs_make_cloud_setup_approachable():
    expected_docs = {
        "docs/CLOUD_DEPLOYMENT_GUIDE.md": [
            "Cloud Deployment Guide",
            "You do not need to understand all cloud services first",
            "AI agent handoff prompt",
            "human approval",
            "cloud-plan",
        ],
        "docs/CLOUD_DEPLOYMENT_GUIDE.ja.md": [
            "クラウド導入ガイド",
            "クラウドを全部理解してから始める必要はありません",
            "AIエージェントへの依頼文",
            "人間の承認",
            "cloud-plan",
        ],
        "docs/CLOUD_BEGINNER_PLAYBOOK.md": [
            "Beginner Cloud Challenge Playbook",
            "first paid PoC",
            "what to prepare",
            "what the AI can do",
            "what the human must approve",
        ],
        "docs/CLOUD_BEGINNER_PLAYBOOK.ja.md": [
            "初心者向けクラウド挑戦プレイブック",
            "最初の有料PoC",
            "用意するもの",
            "AIができること",
            "人間が承認すること",
        ],
        "docs/CONNECTOR_SETUP_GUIDE.md": ["Connector Setup Guide", "Gmail", "Google Sheets", "Slack", "LINE"],
        "docs/CONNECTOR_SETUP_GUIDE.ja.md": ["連携設定ガイド", "Gmail", "Google Sheets", "Slack", "LINE"],
        "docs/CLOUD_TROUBLESHOOTING.md": ["Cloud Troubleshooting", "deployment failed", "secret is missing", "rollback"],
        "docs/CLOUD_TROUBLESHOOTING.ja.md": ["クラウド トラブルシューティング", "デプロイに失敗", "secret が足りない", "rollback"],
    }
    for path, snippets in expected_docs.items():
        text = Path(path).read_text()
        assert len(text) > 1000, path
        for snippet in snippets:
            assert snippet in text, f"{path} missing {snippet}"


def test_grill_me_docs_teach_ai_consultation_for_beginners():
    expected_docs = {
        "docs/AI_GRILL_ME_GUIDE.md": [
            "AI Grill Me Guide",
            "one question at a time",
            "Do not paste real API keys or secrets",
            "challenge vague answers",
            "grill-me",
        ],
        "docs/AI_GRILL_ME_GUIDE.ja.md": [
            "AI Grill Me ガイド",
            "1問ずつ",
            "本物のAPIキーやsecretを貼らない",
            "曖昧な答え",
            "grill-me",
        ],
        "docs/GRILL_ME_PROMPTS.md": ["Grill Me Prompts", "client interview", "cloud readiness", "proposal review"],
        "docs/GRILL_ME_PROMPTS.ja.md": ["Grill Me プロンプト集", "顧客ヒアリング", "クラウド準備", "提案レビュー"],
        "docs/GRILL_ME_CHECKLISTS.md": ["Grill Me Checklists", "workflow fit", "human approval", "stop condition"],
        "docs/GRILL_ME_CHECKLISTS.ja.md": ["Grill Me チェックリスト", "業務適合", "人間の承認", "停止条件"],
    }
    for path, snippets in expected_docs.items():
        text = Path(path).read_text()
        assert len(text) > 1000, path
        for snippet in snippets:
            assert snippet in text, f"{path} missing {snippet}"


def test_ci_runs_tests_from_project_root():
    workflow = Path(".github/workflows/ci.yml").read_text()
    assert "permissions:" in workflow
    assert "contents: read" in workflow
    assert "actions/checkout@v5" in workflow
    assert "actions/setup-python@v6" in workflow
    assert "python3 -m pip install pytest" in workflow
    assert "python3 scripts/release_smoke.py --skip-github" in workflow


def test_dependabot_covers_actions_and_python_packaging():
    dependabot = Path(".github/dependabot.yml").read_text()
    assert 'package-ecosystem: "github-actions"' in dependabot
    assert 'package-ecosystem: "pip"' in dependabot
    assert 'interval: "monthly"' in dependabot
    assert "version-update:semver-major" in dependabot


def test_public_release_audit_script_checks_publish_prerequisites():
    script = Path("scripts/public_release_audit.py")

    result = subprocess.run(
        [sys.executable, str(script)],
        text=True,
        capture_output=True,
        check=True,
    )

    assert "public release audit passed" in result.stdout
    assert "README.md" in result.stdout
    assert "docs/RELEASE_CHECKLIST.md" in result.stdout
    assert ".tmp/" in result.stdout
    assert "dist/" in result.stdout
    assert "pyproject.toml::keywords" in result.stdout
    assert "pyproject.toml::classifiers" in result.stdout
    assert "SECURITY.md::private network" in result.stdout
    assert "docs/OSS_INTEGRATIONS.md::adapter-only" in result.stdout
    assert "README.md::python3 -m pip install -e ." in result.stdout
    assert "README.md::python3 scripts/run_all_demos.py" in result.stdout
    assert "README.md::ai-automation-kit onboard --business-area operations" in result.stdout
    assert "README.md::ai-automation-kit offer-pack --business-area operations" in result.stdout
    assert "README.md::ai-automation-kit client-ready --business-area operations" in result.stdout
    assert "README.md::ai-automation-kit complete-workspace" in result.stdout
    assert "README.md::ai-automation-kit guided-setup" in result.stdout
    assert "README.md::ai-automation-kit guided-review" in result.stdout
    assert "README.md::ai-automation-kit cloud-plan" in result.stdout
    assert "README.md::ai-automation-kit grill-me" in result.stdout
    assert "README.md::ai-automation-kit flows list" in result.stdout
    assert "README.md::ai-automation-kit flows install" in result.stdout
    assert "README.md::ai-automation-kit github-discover --business-area operations" in result.stdout
    assert "docs/PUBLISHING.md::--skip-github" in result.stdout
    assert "docs/PUBLISHING.md::Suggested First Release" in result.stdout
    assert "CHANGELOG.md::Unreleased" in result.stdout
    assert "CONTRIBUTING.md::python3 -m pytest -q" in result.stdout
    assert "LICENSE::MIT License" in result.stdout
    assert "README.md::docs/SHOWCASE.md" in result.stdout
    assert "README.md::docs/demo.html" in result.stdout


def test_public_release_audit_script_exposes_loop_quality_checks():
    text = Path("scripts/public_release_audit.py").read_text()

    assert "REQUIRED_PYPROJECT_SNIPPETS" in text
    assert "REQUIRED_SECURITY_SNIPPETS" in text
    assert "REQUIRED_OSS_POLICY_SNIPPETS" in text
    assert "REQUIRED_CI_SNIPPETS" in text
    assert "FORBIDDEN_TRACKED_PATHS" in text
    assert "MAX_REQUIRED_FILE_BYTES" in text
    assert "empty required file" in text
    assert "REQUIRED_CLI_DOC_SNIPPETS" in text
    assert "REQUIRED_ENTRYPOINT_SNIPPETS" in text
    assert "REQUIRED_PUBLISHING_SNIPPETS" in text
    assert "REQUIRED_CHANGELOG_SNIPPETS" in text
    assert "REQUIRED_CONTRIBUTING_SNIPPETS" in text
    assert "REQUIRED_LICENSE_SNIPPETS" in text
    assert "REQUIRED_EXAMPLE_FILES" in text
    assert "REQUIRED_TEMPLATE_READMES" in text
    assert "REQUIRED_DEMO_RUNNER_SNIPPETS" in text
    assert "REQUIRED_PACKAGING_FILES" in text
    assert "FORBIDDEN_SECRET_SNIPPETS" in text
    assert '"/Users/"' in text
    assert "SECRET_SCAN_PATHS" in text
    assert "REQUIRED_EXPECTED_OUTPUT_FILES" in text
    assert "REQUIRED_STATIC_DEMO_SNIPPETS" in text
    assert "REQUIRED_GENERATED_ARTIFACT_SNIPPETS" in text
    assert "REQUIRED_RELEASE_SMOKE_SNIPPETS" in text
    assert "REQUIRED_RELEASE_EVIDENCE_SNIPPETS" in text
    assert "REQUIRED_GITHUB_SMOKE_SNIPPETS" in text


def test_public_release_audit_script_checks_examples_templates_and_packaging():
    result = subprocess.run(
        [sys.executable, "scripts/public_release_audit.py"],
        text=True,
        capture_output=True,
        check=True,
    )

    assert "examples/research-agent/sample_research.json" in result.stdout
    assert "examples/docs-rag/sample_docs_rag.json" in result.stdout
    assert "examples/internal-ai-workflow/sample_inquiry.json" in result.stdout
    assert "examples/excel-to-internal-app/sample_app.json" in result.stdout
    assert "examples/delivery-pipeline/sample_delivery_pipeline.json" in result.stdout
    assert "templates/research-agent/README.md" in result.stdout
    assert "templates/delivery-pipeline/README.md" in result.stdout
    assert "scripts/run_all_demos.py::delivery-pipeline" in result.stdout
    assert "pyproject.toml::setuptools" in result.stdout
    assert "setup.py::setuptools" in result.stdout


def test_public_release_audit_script_checks_secret_safety_and_demo_artifacts():
    result = subprocess.run(
        [sys.executable, "scripts/public_release_audit.py"],
        text=True,
        capture_output=True,
        check=True,
    )

    assert "secret-scan::README.md" in result.stdout
    assert "secret-scan::docs/PUBLISHING.md" in result.stdout
    assert "examples/research-agent/expected/report.md" in result.stdout
    assert "examples/docs-rag/expected/answer.md" in result.stdout
    assert "examples/delivery-pipeline/expected/release-plan.md" in result.stdout
    assert "docs/demo.html::AI Automation Starter Kit Demo" in result.stdout
    assert "README.md::value_measurement_report.md" in result.stdout
    assert "README.md::executive_decision_brief.md" in result.stdout
    assert "README.md::pilot_scorecard.csv" in result.stdout
    assert "README.md::operational_audit_plan.md" in result.stdout
    assert "README.md::offer_pack/" in result.stdout
    assert "README.md::client-ready/" in result.stdout
    assert "README.md::statement_of_work.md" in result.stdout
    assert "README.md::pricing_model.md" in result.stdout
    assert "README.md::roi_calculator.csv" in result.stdout
    assert "README.md::implementation_readiness_score.json" in result.stdout
    assert "README.md::maintenance_plan.md" in result.stdout


def test_public_release_audit_script_checks_final_release_evidence():
    result = subprocess.run(
        [sys.executable, "scripts/public_release_audit.py"],
        text=True,
        capture_output=True,
        check=True,
    )

    assert "scripts/release_smoke.py::public_release_audit.py" in result.stdout
    assert "scripts/release_smoke.py::pip wheel" in result.stdout
    assert "scripts/release_smoke.py::_verify_wheel_install" in result.stdout
    assert "scripts/release_smoke.py::onboard" in result.stdout
    assert "scripts/release_smoke.py::onboarding_summary.md" in result.stdout
    assert "scripts/release_smoke.py::offer-pack" in result.stdout
    assert "scripts/release_smoke.py::offer_pack/README.md" in result.stdout
    assert "scripts/release_smoke.py::proposal.md" in result.stdout
    assert "scripts/release_smoke.py::pricing_model.md" in result.stdout
    assert "scripts/release_smoke.py::client-ready" in result.stdout
    assert "scripts/release_smoke.py::complete-workspace" in result.stdout
    assert "scripts/release_smoke.py::guided-setup" in result.stdout
    assert "scripts/release_smoke.py::START_HERE_GUIDED_SETUP.md" in result.stdout
    assert "scripts/release_smoke.py::guided_setup_questions.md" in result.stdout
    assert "scripts/release_smoke.py::ai_agent_instruction.md" in result.stdout
    assert "scripts/release_smoke.py::guided-review" in result.stdout
    assert "scripts/release_smoke.py::START_HERE_GUIDED_REVIEW.md" in result.stdout
    assert "scripts/release_smoke.py::setup_readiness_report.md" in result.stdout
    assert "scripts/release_smoke.py::next_commands.md" in result.stdout
    assert "scripts/release_smoke.py::cloud-plan" in result.stdout
    assert "scripts/release_smoke.py::START_HERE_CLOUD_PLAN.md" in result.stdout
    assert "scripts/release_smoke.py::workload_architecture.md" in result.stdout
    assert "scripts/release_smoke.py::deploy_runbook.md" in result.stdout
    assert "scripts/release_smoke.py::human_approval_required.md" in result.stdout
    assert "scripts/release_smoke.py::grill-me" in result.stdout
    assert "scripts/release_smoke.py::START_HERE_GRILL_ME.md" in result.stdout
    assert "scripts/release_smoke.py::questions_to_answer.md" in result.stdout
    assert "scripts/release_smoke.py::ai_agent_prompt.md" in result.stdout
    assert "scripts/release_smoke.py::FINAL_DELIVERY_GUIDE.md" in result.stdout
    assert "scripts/release_smoke.py::completion_checklist.md" in result.stdout
    assert "scripts/release_smoke.py::roi_calculator.csv" in result.stdout
    assert "scripts/release_smoke.py::implementation_readiness_score.json" in result.stdout
    assert "scripts/release_smoke.py::maintenance_plan.md" in result.stdout
    assert "scripts/release_smoke.py::marketplace_profile.md" in result.stdout
    assert "scripts/release_smoke.py::flows install" in result.stdout
    assert "scripts/release_smoke.py::flows run" in result.stdout
    assert "scripts/release_smoke.py::flows approve" in result.stdout
    assert "scripts/release_smoke.py::flow.yaml" in result.stdout
    assert "scripts/release_smoke.py::workflow_map.mmd" in result.stdout
    assert "scripts/release_smoke.py::ai-reception-line-inquiry" in result.stdout
    assert "scripts/release_smoke.py::setup_requirements.md" in result.stdout
    assert "scripts/release_smoke.py::ai_action_procedure.md" in result.stdout
    assert "scripts/release_smoke.py::operator_ui/index.html" in result.stdout
    assert "scripts/release_smoke.py::automation_output" in result.stdout
    assert "scripts/release_smoke.py::local_outbox" in result.stdout
    assert "scripts/release_smoke.py::github-discover" in result.stdout
    assert "scripts/release_smoke.py::adapter_starter/smoke_test.py" in result.stdout
    assert "scripts/release_smoke.py::manual_review_pack.md" in result.stdout
    assert "scripts/release_smoke.py::executive_decision_brief.md" in result.stdout
    assert "scripts/release_smoke.py::pilot_scorecard.csv" in result.stdout
    assert "docs/RELEASE_CHECKLIST.md::doctor_report.md" in result.stdout
    assert "docs/RELEASE_CHECKLIST.md::installed-doctor" in result.stdout
    assert "docs/RELEASE_CHECKLIST.md::value_measurement_report.md" in result.stdout
    assert "docs/RELEASE_CHECKLIST.md::Release Decision" in result.stdout


def test_release_checklist_mentions_doctor_and_live_github_smoke():
    checklist = Path("docs/RELEASE_CHECKLIST.md").read_text()
    assert "python3 scripts/public_release_audit.py" in checklist
    assert "python3 scripts/release_smoke.py" in checklist
    assert "--skip-github" in checklist
    assert ".tmp/release-smoke/doctor/doctor_report.md" in checklist
    assert ".tmp/release-smoke/installed-doctor/doctor_report.md" in checklist
    assert ".tmp/release-smoke/onboard-operations/onboarding_summary.md" in checklist
    assert ".tmp/release-smoke/onboard-operations/doctor/doctor_report.md" in checklist
    assert ".tmp/release-smoke/onboard-operations/offer_pack/README.md" in checklist
    assert ".tmp/release-smoke/offer-pack-operations/proposal.md" in checklist
    assert ".tmp/release-smoke/offer-pack-operations/pricing_model.md" in checklist
    assert ".tmp/release-smoke/client-ready-accounting/README.md" in checklist
    assert ".tmp/release-smoke/client-ready-accounting/roi_calculator.csv" in checklist
    assert ".tmp/release-smoke/client-ready-accounting/implementation_readiness_score.json" in checklist
    assert ".tmp/release-smoke/client-ready-accounting/maintenance_plan.md" in checklist
    assert ".tmp/release-smoke/guided-review-ai-reception/setup_readiness_report.md" in checklist
    assert ".tmp/release-smoke/guided-review-ai-reception/next_commands.md" in checklist
    assert ".tmp/release-smoke/cloud-plan-aws-scheduled-job/workload_architecture.md" in checklist
    assert ".tmp/release-smoke/cloud-plan-aws-scheduled-job/human_approval_required.md" in checklist
    assert ".tmp/release-smoke/grill-me-invoice-cloud/START_HERE_GRILL_ME.md" in checklist
    assert ".tmp/release-smoke/grill-me-invoice-cloud/ai_agent_prompt.md" in checklist
    assert ".tmp/release-smoke/flow-invoice-document-followup/flow.yaml" in checklist
    assert ".tmp/release-smoke/flow-invoice-document-followup/workflow_map.mmd" in checklist
    assert ".tmp/release-smoke/flow-invoice-document-followup/config/connectors.json" in checklist
    assert ".tmp/release-smoke/flow-invoice-document-followup/docs/SYSTEM_RUNBOOK.md" in checklist
    assert ".tmp/release-smoke/flow-invoice-document-followup/automation_output/draft_outputs.md" in checklist
    assert ".tmp/release-smoke/flow-invoice-document-followup/automation_output/approval_queue.csv" in checklist
    assert ".tmp/release-smoke/flow-invoice-document-followup/local_outbox/email_drafts.md" in checklist
    assert ".tmp/release-smoke/github-operations/run_summary.md" in checklist
    assert ".tmp/release-smoke/github-operations/enterprise_readiness.md" in checklist
    assert ".tmp/release-smoke/github-operations/value_realization_plan.md" in checklist
    assert ".tmp/release-smoke/github-operations/value_measurement_report.md" in checklist
    assert ".tmp/release-smoke/github-operations/executive_decision_brief.md" in checklist
    assert ".tmp/release-smoke/github-operations/pilot_scorecard.csv" in checklist
    assert ".tmp/release-smoke/github-operations/stakeholder_rollout_map.md" in checklist
    assert ".tmp/release-smoke/github-operations/risk_exception_register.md" in checklist
    assert ".tmp/release-smoke/github-operations/operational_audit_plan.md" in checklist
    assert ".tmp/release-smoke/github-operations/adapter_starter/README.md" in checklist
    assert ".tmp/release-smoke/github-support/run_summary.md" in checklist
    assert ".tmp/release-smoke/github-support/enterprise_readiness.md" in checklist
    assert ".tmp/release-smoke/github-support/value_realization_plan.md" in checklist
    assert ".tmp/release-smoke/github-support/value_measurement_report.md" in checklist
    assert ".tmp/release-smoke/github-support/executive_decision_brief.md" in checklist
    assert ".tmp/release-smoke/github-support/pilot_scorecard.csv" in checklist
    assert ".tmp/release-smoke/github-support/stakeholder_rollout_map.md" in checklist
    assert ".tmp/release-smoke/github-support/risk_exception_register.md" in checklist
    assert ".tmp/release-smoke/github-support/operational_audit_plan.md" in checklist
    assert ".tmp/release-smoke/github-support/manual_review_pack.md" in checklist


def test_security_policy_mentions_secrets_and_private_networks():
    policy = Path("SECURITY.md").read_text()
    assert "secrets" in policy.lower()
    assert "private network" in policy.lower()
    assert "dry-run" in policy.lower()
