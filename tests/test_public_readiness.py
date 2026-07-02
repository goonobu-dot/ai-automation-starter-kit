from pathlib import Path
import re
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


def test_readme_links_entrance_and_key_docs():
    readme = Path("README.md").read_text()
    assert "docs/GETTING_STARTED.ja.md" in readme
    assert "docs/INDEX.md" in readme
    assert "docs/manual.html" in readme
    assert "docs/manual.ja.html" in readme
    assert "docs/USER_MANUAL.md" in readme
    assert "docs/BEGINNER_ROUTE_MAP.md" in readme
    assert "docs/BEGINNER_ROUTE_MAP.ja.md" in readme
    assert "docs/SELLING_AUTOMATION_GUIDE.md" in readme
    assert "docs/FLOW_SELECTION_GUIDE.md" in readme
    assert "docs/CLIENT_DEMO_SCRIPT.md" in readme
    assert "docs/REAL_WORLD_SETUP_GUIDE.md" in readme
    assert "docs/FAQ.md" in readme
    assert "docs/CLOUD_DEPLOYMENT_GUIDE.md" in readme
    assert "docs/CLOUD_DEPLOYMENT_GUIDE.ja.md" in readme
    assert "docs/CLOUD_BEGINNER_PLAYBOOK.md" in readme
    assert "docs/CLOUD_BEGINNER_PLAYBOOK.ja.md" in readme
    assert "docs/CONNECTOR_SETUP_GUIDE.md" in readme
    assert "docs/CONNECTOR_SETUP_GUIDE.ja.md" in readme
    assert "docs/CLOUD_TROUBLESHOOTING.md" in readme
    assert "docs/CLOUD_TROUBLESHOOTING.ja.md" in readme
    assert "docs/AI_AGENT_GRILL_ME_SKILL.md" in readme
    assert "docs/AI_AGENT_GRILL_ME_SKILL.ja.md" in readme
    assert "docs/AUTOMATION_EXPANSION_GUIDE.md" in readme
    assert "docs/AUTOMATION_EXPANSION_GUIDE.ja.md" in readme
    assert "docs/SIDE_HUSTLE_BLUEPRINTS.md" in readme
    assert "docs/SIDE_HUSTLE_BLUEPRINTS.ja.md" in readme
    # Archived docs must no longer be part of the README entrance.
    assert "docs/START_HERE.md" not in readme
    assert "docs/AI_BEGINNER_SUPPORT_MAP.md" not in readme
    assert "docs/GRILL_ME_PROMPTS.md" not in readme


def test_getting_started_index_and_archive_form_the_single_entrance():
    getting = Path("docs/GETTING_STARTED.ja.md").read_text()
    index = Path("docs/INDEX.md").read_text()
    archive = Path("docs/archive/README.md").read_text()
    assert "唯一の入口" in getting
    assert "ai-automation-kit beginner" in getting
    assert "complete-workspace" in getting
    assert "beginner-sales" in getting
    assert "TUTORIAL_SME_PROPOSAL.ja.md" in getting
    assert "dry-run" in getting
    assert "30分" in getting
    assert "です" in getting
    assert "最初は🔰入門カテゴリ以外読まないでください" in index
    assert "GETTING_STARTED.ja.md" in index
    assert "💼" in index and "⚙️" in index and "☁️" in index and "📚" in index
    assert "archive/README.md" in index
    assert "歴史的資料" in archive
    assert "INDEX.md" in archive


def test_start_here_and_use_cases_docs_are_archived_but_intact():
    english_start = Path("docs/archive/START_HERE.md").read_text()
    japanese_start = Path("docs/archive/START_HERE.ja.md").read_text()
    english_cases = Path("docs/archive/USE_CASES.md").read_text()
    japanese_cases = Path("docs/archive/USE_CASES.ja.md").read_text()
    assert "Start Here" in english_start
    assert "First 3 minutes" in english_start
    assert "Beginner Route Map" in english_start
    assert "Do not read every document first" in english_start
    assert "まずここから" in japanese_start
    assert "最初の3分" in japanese_start
    assert "初心者ルートマップ" in japanese_start
    assert "全部の資料を先に読む必要はありません" in japanese_start
    assert "Use Cases" in english_cases
    assert "business automation" in english_cases
    assert "ユースケース" in japanese_cases
    assert "業務自動化" in japanese_cases


def test_english_manuals_match_japanese_business_proposal_coverage():
    expected_docs = {
        "docs/USER_MANUAL.md": ["business-launch", "complete-workspace", "paid PoC", "share-check"],
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


def test_beginner_route_maps_prevent_manual_overload():
    expected_docs = {
        "docs/BEGINNER_ROUTE_MAP.md": [
            "Beginner Route Map",
            "30-second version",
            "Stop here for today",
            "Read this like a signboard",
            "Do not read everything first",
            "One workflow, one sample input, one draft output, one human approver",
            "No-CLI path",
            "CLI path",
            "Side-hustle path",
            "Company internal path",
            "Website project path",
            "Cloud and API path",
            "What to open first",
            "What to ignore at first",
            "command-center",
            "complete-workspace",
            "guided-setup",
            "human approval",
        ],
        "docs/BEGINNER_ROUTE_MAP.ja.md": [
            "初心者ルートマップ",
            "30秒でわかる結論",
            "今日はここまで",
            "案内板として読んでください",
            "最初から全部読まない",
            "1つの業務、1つのサンプル入力、1つの下書き出力、1人の承認者",
            "CLIを使わないルート",
            "CLIを使うルート",
            "副業・受託ルート",
            "社内導入ルート",
            "ホームページ案件ルート",
            "クラウド・APIルート",
            "最初に開くもの",
            "最初は無視してよいもの",
            "command-center",
            "complete-workspace",
            "guided-setup",
            "人間承認",
        ],
    }
    for path, snippets in expected_docs.items():
        text = Path(path).read_text()
        assert len(text) > 2500, path
        first_screen = text[:1400]
        assert "command-center" not in first_screen, f"{path} starts with tool details too early"
        assert first_screen.count("`") <= 8, f"{path} first screen is too code/file heavy"
        for snippet in snippets:
            assert snippet in text, f"{path} missing {snippet}"


def test_html_manuals_are_language_separated_visual_entrypoints():
    english = Path("docs/manual.html").read_text()
    japanese = Path("docs/manual.ja.html").read_text()
    english_snippets = [
        "<!doctype html>",
        '<html lang="en">',
        "Operating Manual",
        "How the automation works",
        "The kit drafts",
        "A human reviews",
        "A human sends",
        "5-step side-business roadmap",
        "flows approve",
        "share-check",
        "USER_MANUAL.md",
        "INDEX.md",
        "manual.ja.html",
    ]
    japanese_snippets = [
        "<!doctype html>",
        '<html lang="ja">',
        "操作マニュアル",
        "5段階ロードマップ",
        "生成する",
        "人間が確認・承認",
        "人間が送る",
        "ドライラン",
        "flows approve",
        "share-check",
        "TUTORIAL_SME_PROPOSAL.ja.md",
        "USER_MANUAL.ja.md",
        "INDEX.md",
        "manual.html",
    ]
    assert len(english) > 7000
    assert len(japanese) > 7000
    assert "<script" not in english.lower()
    assert "<script" not in japanese.lower()
    assert not re.search(r"[\u3040-\u30ff\u4e00-\u9fff]", english)
    for forbidden in ["How the automation works", "Core commands", "What humans do"]:
        assert forbidden not in japanese
    for snippet in english_snippets:
        assert snippet in english, f"docs/manual.html missing {snippet}"
    for snippet in japanese_snippets:
        assert snippet in japanese, f"docs/manual.ja.html missing {snippet}"


def test_ai_reception_employee_docs_explain_setup_and_monetization_path():
    expected_docs = {
        "docs/archive/AI_RECEPTION_EMPLOYEE_PACK.md": [
            "AI Reception Employee",
            "reception folder",
            "API keys",
            "operator_ui/index.html",
            "Paid dry-run PoC",
        ],
        "docs/archive/AI_RECEPTION_EMPLOYEE_PACK.ja.md": [
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
        "docs/archive/AI_EMPLOYEE_ROADMAP.md": [
            "AI Reception Employee",
            "Internal FAQ",
            "Sales Research",
            "Do not start with outbound sales",
            "multi-department",
        ],
        "docs/archive/AI_EMPLOYEE_ROADMAP.ja.md": [
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


def test_website_side_hustle_docs_are_bilingual_and_linked():
    expected_docs = {
        "docs/archive/WEBSITE_SIDE_HUSTLE_GUIDE.md": [
            "Website Side Hustle Guide",
            "Website Project Agent Guide",
            "website-side-hustle",
            "beginner_human_guide.md",
            "client_kickoff_questions.md",
            "delivery_acceptance_checklist.md",
            "inquiry_dashboard.html",
        ],
        "docs/archive/WEBSITE_SIDE_HUSTLE_GUIDE.ja.md": [
            "ホームページ副業ガイド",
            "ホームページ制作プロジェクト AIエージェント利用ガイド",
            "website-side-hustle",
            "beginner_human_guide.ja.md",
            "client_kickoff_questions.md",
            "delivery_acceptance_checklist.md",
            "inquiry_dashboard.html",
        ],
        "docs/archive/WEBSITE_PROJECT_AGENT_GUIDE.md": [
            "Website Project Agent Guide",
            "docs/WEBSITE_SIDE_HUSTLE_GUIDE.md",
            "Do not clone competitors",
            "START_HERE_WEBSITE_SIDE_HUSTLE.md",
        ],
        "docs/archive/WEBSITE_PROJECT_AGENT_GUIDE.ja.md": [
            "ホームページ制作プロジェクト AIエージェント利用ガイド",
            "docs/WEBSITE_SIDE_HUSTLE_GUIDE.ja.md",
            "競合サイトの丸ごとコピーはしない",
            "START_HERE_WEBSITE_SIDE_HUSTLE.md",
        ],
    }
    for path, snippets in expected_docs.items():
        text = Path(path).read_text()
        assert len(text) > 800, path
        for snippet in snippets:
            assert snippet in text, f"{path} missing {snippet}"


def test_side_hustle_blueprint_docs_are_bilingual_and_beginner_friendly():
    expected_docs = {
        "docs/SIDE_HUSTLE_BLUEPRINTS.md": [
            "Side Hustle Blueprints Guide",
            "side-hustle-blueprints",
            "START_HERE_SIDE_HUSTLE_BLUEPRINTS.md",
            "first_client_picker.md",
            "risk_boundaries.md",
            "AI agent",
        ],
        "docs/SIDE_HUSTLE_BLUEPRINTS.ja.md": [
            "副業ブループリントガイド",
            "side-hustle-blueprints",
            "START_HERE_SIDE_HUSTLE_BLUEPRINTS.md",
            "first_client_picker.md",
            "risk_boundaries.md",
            "AIエージェント",
        ],
    }
    for path, snippets in expected_docs.items():
        text = Path(path).read_text()
        assert len(text) > 800, path
        for snippet in snippets:
            assert snippet in text, f"{path} missing {snippet}"


def test_automation_expansion_docs_are_bilingual_and_beginner_friendly():
    expected_docs = {
        "docs/AUTOMATION_EXPANSION_GUIDE.md": [
            "Automation Expansion Guide",
            "command-center",
            "skill-pack",
            "approval-gate",
            "mcp-connector-plan",
            "workflow-explainer",
            "eval-loop",
            "self-host-pack",
            "connector-catalog",
            "script-ui-pack",
            "knowledge-rag-pack",
            "automation-hooks",
            "governance-pack",
            "OpenAI",
            "Anthropic",
        ],
        "docs/AUTOMATION_EXPANSION_GUIDE.ja.md": [
            "業務自動化 拡充機能ガイド",
            "command-center",
            "skill-pack",
            "approval-gate",
            "mcp-connector-plan",
            "workflow-explainer",
            "eval-loop",
            "self-host-pack",
            "connector-catalog",
            "script-ui-pack",
            "knowledge-rag-pack",
            "automation-hooks",
            "governance-pack",
            "AIエージェント",
        ],
    }
    for path, snippets in expected_docs.items():
        text = Path(path).read_text()
        assert len(text) > 1000, path
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
        "docs/AI_AGENT_GRILL_ME_SKILL.md": [
            "AI Agent Grill Me Skill",
            "not tied to a CLI agent",
            "Copy this skill into ChatGPT, Claude, Gemini, Cursor, Codex, Claude Code, or another AI agent",
            "ask exactly one question at a time",
            "Do not ask for real secrets",
            "human approval gate",
        ],
        "docs/AI_AGENT_GRILL_ME_SKILL.ja.md": [
            "AIエージェント Grill Me スキル",
            "CLI版AIエージェント専用ではありません",
            "ChatGPT、Claude、Gemini、Cursor、Codex、Claude Code など",
            "必ず1問ずつ質問する",
            "本物のsecretを求めない",
            "人間承認ゲート",
        ],
        "docs/archive/AI_GRILL_ME_GUIDE.md": [
            "AI Grill Me Guide",
            "You can use the skill without running the CLI",
            "one question at a time",
            "Do not paste real API keys or secrets",
            "challenge vague answers",
            "grill-me",
        ],
        "docs/archive/AI_GRILL_ME_GUIDE.ja.md": [
            "AI Grill Me ガイド",
            "CLIを実行しなくても使えます",
            "1問ずつ",
            "本物のAPIキーやsecretを貼らない",
            "曖昧な答え",
            "grill-me",
        ],
        "docs/archive/GRILL_ME_PROMPTS.md": ["Grill Me Prompts", "client interview", "cloud readiness", "proposal review"],
        "docs/archive/GRILL_ME_PROMPTS.ja.md": ["Grill Me プロンプト集", "顧客ヒアリング", "クラウド準備", "提案レビュー"],
        "docs/archive/GRILL_ME_CHECKLISTS.md": ["Grill Me Checklists", "workflow fit", "human approval", "stop condition"],
        "docs/archive/GRILL_ME_CHECKLISTS.ja.md": ["Grill Me チェックリスト", "業務適合", "人間の承認", "停止条件"],
    }
    for path, snippets in expected_docs.items():
        text = Path(path).read_text()
        assert len(text) > 1000, path
        for snippet in snippets:
            assert snippet in text, f"{path} missing {snippet}"


def test_ai_beginner_support_docs_cover_current_practical_follow_up():
    expected_docs = {
        "docs/archive/AI_BEGINNER_SUPPORT_MAP.md": [
            "AI Beginner Support Map",
            "what AI can do now",
            "what a human must still do",
            "API keys",
            "reception folder",
            "cloud account",
            "rollback",
            "paid dry-run PoC",
        ],
        "docs/archive/AI_BEGINNER_SUPPORT_MAP.ja.md": [
            "AI初心者サポートマップ",
            "今の技術でAIが支援できること",
            "人間が必ず行うこと",
            "APIキー",
            "受付フォルダ",
            "クラウドアカウント",
            "rollback",
            "有料dry-run PoC",
        ],
        "docs/archive/AI_AGENT_SETUP_ASSISTANT_PLAYBOOK.md": [
            "AI Agent Setup Assistant Playbook",
            "intake mode",
            "connector mode",
            "cloud mode",
            "troubleshooting mode",
            "never collect secrets in chat",
            "safe substitute",
        ],
        "docs/archive/AI_AGENT_SETUP_ASSISTANT_PLAYBOOK.ja.md": [
            "AIエージェント セットアップ補助プレイブック",
            "ヒアリングモード",
            "連携設定モード",
            "クラウドモード",
            "トラブル対応モード",
            "チャットでsecretを集めない",
            "安全な代替情報",
        ],
        "docs/archive/CLIENT_DELIVERY_SUPPORT_RUNBOOK.md": [
            "Client Delivery Support Runbook",
            "before the sales call",
            "during the discovery call",
            "after the first demo",
            "go-live gate",
            "monthly operation",
            "do not promise revenue",
        ],
        "docs/archive/CLIENT_DELIVERY_SUPPORT_RUNBOOK.ja.md": [
            "顧客導入サポート運用手順書",
            "営業前",
            "ヒアリング中",
            "初回デモ後",
            "go-liveゲート",
            "月次運用",
            "収益保証しない",
        ],
    }
    for path, snippets in expected_docs.items():
        text = Path(path).read_text()
        assert len(text) > 1500, path
        for snippet in snippets:
            assert snippet in text, f"{path} missing {snippet}"


def test_beginner_docs_are_written_for_non_developers_first():
    expected_docs = {
        "README.md": [
            "\u65e5\u672c\u8a9e\u306e\u65b9\u3078\uff1a3\u30b9\u30c6\u30c3\u30d7\u3067\u59cb\u3081\u308b",
            "\u521d\u5fc3\u8005\u30ca\u30d3",
            "\u552f\u4e00\u306e\u5165\u53e3",
            "ai-automation-kit beginner",
        ],
        "docs/archive/AI_BEGINNER_SUPPORT_MAP.md": [
            "First, do this",
            "Words in plain language",
            "API key means",
            "Cloud account means",
            "Dry-run means",
            "Human approval means",
        ],
        "docs/archive/AI_BEGINNER_SUPPORT_MAP.ja.md": [
            "まず、これだけやってください",
            "やさしい言葉での説明",
            "APIキーとは",
            "クラウドアカウントとは",
            "dry-runとは",
            "人間承認とは",
        ],
        "docs/archive/AI_AGENT_SETUP_ASSISTANT_PLAYBOOK.md": [
            "Beginner first rule",
            "Do not start with technical setup",
            "Ask what the user wants to improve",
            "explain the word before using it",
        ],
        "docs/archive/AI_AGENT_SETUP_ASSISTANT_PLAYBOOK.ja.md": [
            "初心者ファーストのルール",
            "技術設定から始めない",
            "何を改善したいかを先に聞く",
            "専門用語は使う前に説明する",
        ],
        "docs/archive/CLIENT_DELIVERY_SUPPORT_RUNBOOK.md": [
            "Plain client explanation",
            "Do not sound like a developer manual",
            "The client should understand the before and after",
        ],
        "docs/archive/CLIENT_DELIVERY_SUPPORT_RUNBOOK.ja.md": [
            "顧客に伝わる説明",
            "開発者向けマニュアルのように話さない",
            "顧客がbefore/afterを理解できる",
        ],
    }
    for path, snippets in expected_docs.items():
        text = Path(path).read_text()
        for snippet in snippets:
            assert snippet in text, f"{path} missing beginner-first wording: {snippet}"


def test_readme_positions_project_as_ai_agent_skill_kit_not_cli_only():
    readme = Path("README.md").read_text()
    assert "AI agent skill kit" in readme
    assert "The CLI is optional" in readme
    assert "not a requirement to use a CLI-based AI agent" in readme
    assert "AI Agent Grill Me Skill" in readme
    assert "ask the AI to read the skill document" in readme
    assert "local Python CLI for turning public GitHub signals" not in readme


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
    assert "scripts/release_smoke.py::command-center" in result.stdout
    assert "scripts/release_smoke.py::START_HERE_COMMAND_CENTER.md" in result.stdout
    assert "scripts/release_smoke.py::command_center.html" in result.stdout
    assert "scripts/release_smoke.py::skill-pack" in result.stdout
    assert "scripts/release_smoke.py::SKILL.md" in result.stdout
    assert "scripts/release_smoke.py::approval-gate" in result.stdout
    assert "scripts/release_smoke.py::approval_gate.json" in result.stdout
    assert "scripts/release_smoke.py::mcp-connector-plan" in result.stdout
    assert "scripts/release_smoke.py::mcp_connector_plan.md" in result.stdout
    assert "scripts/release_smoke.py::agent-team" in result.stdout
    assert "scripts/release_smoke.py::agent_team_roles.md" in result.stdout
    assert "scripts/release_smoke.py::workflow-explainer" in result.stdout
    assert "scripts/release_smoke.py::workflow_explainer.html" in result.stdout
    assert "scripts/release_smoke.py::eval-loop" in result.stdout
    assert "scripts/release_smoke.py::eval_dataset.csv" in result.stdout
    assert "scripts/release_smoke.py::self-host-pack" in result.stdout
    assert "scripts/release_smoke.py::self_host_runbook.md" in result.stdout
    assert "scripts/release_smoke.py::connector-catalog" in result.stdout
    assert "scripts/release_smoke.py::connector_piece_catalog.md" in result.stdout
    assert "scripts/release_smoke.py::script-ui-pack" in result.stdout
    assert "scripts/release_smoke.py::script_to_ui_plan.md" in result.stdout
    assert "scripts/release_smoke.py::knowledge-rag-pack" in result.stdout
    assert "scripts/release_smoke.py::knowledge_base_pack.md" in result.stdout
    assert "scripts/release_smoke.py::automation-hooks" in result.stdout
    assert "scripts/release_smoke.py::automation_hooks.md" in result.stdout
    assert "scripts/release_smoke.py::governance-pack" in result.stdout
    assert "scripts/release_smoke.py::governance_pack.md" in result.stdout
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
