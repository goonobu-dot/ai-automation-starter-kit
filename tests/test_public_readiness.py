from html.parser import HTMLParser
import importlib.util
from pathlib import Path
import re
import subprocess
import sys

from ai_automation_kit import __version__
from ai_automation_kit.cli import main


def _local_hrefs(text: str) -> list[str]:
    return re.findall(r'href="([^"]+)"', text)


def _assert_no_broken_local_hrefs(path: str, text: str) -> None:
    doc = Path(path)
    for href in _local_hrefs(text):
        if not href or href.startswith(("#", "mailto:", "tel:", "data:")):
            continue
        assert "://" not in href, f"{path} must use relative links only: {href}"
        target = href.split("#", 1)[0]
        if not target:
            continue
        assert (doc.parent / target).exists(), f"{path} has broken local href {href}"


def _published_daily_workflow_docs() -> list[str]:
    return [path for path in ["docs/daily-workflows.ja.html", "docs/daily-workflows.html"] if Path(path).exists()]


class _VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._skip_tags = {"style", "script", "pre", "code"}
        self._skip_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in self._skip_tags:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        attr_map = dict(attrs)
        for key in ("aria-label", "title"):
            value = attr_map.get(key)
            if value:
                self.parts.append(value)

    def handle_endtag(self, tag: str) -> None:
        if tag in self._skip_tags and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        if data and data.strip():
            self.parts.append(data)


def _extract_visible_text(html: str) -> str:
    parser = _VisibleTextParser()
    parser.feed(html)
    text = " ".join(parser.parts)
    text = re.sub(r"\s+", " ", text)
    allowlist = [
        "AI Automation Starter Kit",
        "GitHub Pages",
        "HTML",
        "CSS",
        "CLI",
        "AI",
        "PoC",
        "OCR",
        "PDF",
        "DOCX",
        "XLSX",
        "CSV",
        "JSON",
        "PNG",
        "JPEG",
        "WebP",
        "Word",
        "Mermaid",
        "Markdown",
        "report-automation-wizard-flow.mmd",
        "REPORT_AUTOMATION_GUIDE.ja.md",
        "AI_AGENT_GRILL_ME_SKILL.ja.md",
        "CLOUD_BEGINNER_PLAYBOOK.ja.md",
        "INDEX.md",
        "manual.ja.html",
        "Codex",
        "ChatGPT",
        "Claude",
        "Gemini",
        "Cursor",
    ]
    for value in allowlist:
        text = text.replace(value, "")
    return text


def _load_release_smoke_module():
    spec = importlib.util.spec_from_file_location("release_smoke_module", Path("scripts/release_smoke.py"))
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
        "AGENTS.md",
        "START_WITH_CODEX.md",
        "START_WITH_CODEX.ja.md",
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
    assert "goonobu-dot.github.io/ai-automation-starter-kit/manual.html" in readme
    assert "goonobu-dot.github.io/ai-automation-starter-kit/manual.ja.html" in readme
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
    assert "docs/SIDE_HUSTLE_MARKET_UPDATE_2026.ja.md" in readme
    assert "docs/REPORT_AUTOMATION_GUIDE.md" in readme
    assert "docs/REPORT_AUTOMATION_GUIDE.ja.md" in readme
    # Archived docs must no longer be part of the README entrance.
    assert "docs/START_HERE.md" not in readme
    assert "docs/AI_BEGINNER_SUPPORT_MAP.md" not in readme
    assert "docs/GRILL_ME_PROMPTS.md" not in readme


def test_report_wizard_navigation_is_linked_from_public_entry_docs():
    readme = Path("README.md").read_text(encoding="utf-8")
    index = Path("docs/INDEX.md").read_text(encoding="utf-8")
    manual_en = Path("docs/USER_MANUAL.md").read_text(encoding="utf-8")
    manual_ja = Path("docs/USER_MANUAL.ja.md").read_text(encoding="utf-8")
    browser_manual_en = Path("docs/manual.html").read_text(encoding="utf-8")
    browser_manual_ja = Path("docs/manual.ja.html").read_text(encoding="utf-8")
    report_guide_en = Path("docs/REPORT_AUTOMATION_GUIDE.md").read_text(encoding="utf-8")
    report_guide_ja = Path("docs/REPORT_AUTOMATION_GUIDE.ja.md").read_text(encoding="utf-8")

    for snippet in [
        "docs/report-automation-wizard.ja.html",
        "docs/report-automation-wizard.html",
        "ai-automation-kit report-wizard init",
        "ai-automation-kit report-wizard serve",
    ]:
        assert snippet in readme, f"README.md missing report wizard navigation: {snippet}"

    getting_started_index = index.split("## 💼", 1)[0]
    sales_index = index.split("## 💼", 1)[1]
    assert "report-automation-wizard.ja.html" in getting_started_index
    assert "report-automation-wizard.html" in getting_started_index
    assert "REPORT_AUTOMATION_GUIDE.ja.md" not in getting_started_index
    assert "REPORT_AUTOMATION_GUIDE.ja.md" in sales_index
    assert "REPORT_AUTOMATION_GUIDE.md" in sales_index

    for text, manual_path in [
        (manual_en, "report-automation-wizard.html"),
        (manual_ja, "report-automation-wizard.ja.html"),
    ]:
        assert "report-wizard" in text
        assert manual_path in text

    assert 'href="report-automation-wizard.html"' in browser_manual_en
    assert 'href="report-automation-wizard.ja.html"' in browser_manual_ja
    assert "Report wizard manual" in browser_manual_en
    assert "レポートウィザード" in browser_manual_ja

    assert "use report-wizard when" in report_guide_en
    assert "report-wizard を使ってください" in report_guide_ja


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
    assert "SIDE_HUSTLE_MARKET_UPDATE_2026.ja.md" in index
    assert "REPORT_AUTOMATION_GUIDE.ja.md" in index
    assert "歴史的資料" in archive
    assert "INDEX.md" in archive


def test_report_automation_guides_explain_folder_based_grill_me_workflow():
    expected_docs = {
        "docs/REPORT_AUTOMATION_GUIDE.ja.md": [
            "日報・月報AI下書き自動化ガイド",
            "過去の完成物",
            "今回の資料",
            "GrillMe",
            "1問ずつ",
            "人間が承認",
            "ai-automation-kit report-automation",
            "01_past_outputs",
            "02_current_materials",
            "売らない方がよい言い方",
        ],
        "docs/REPORT_AUTOMATION_GUIDE.md": [
            "Report Automation Guide",
            "past completed reports",
            "current materials",
            "GrillMe-style",
            "one question at a time",
            "human approval",
            "ai-automation-kit report-automation",
            "01_past_outputs",
            "02_current_materials",
            "Do Not Promise",
        ],
    }
    for path, snippets in expected_docs.items():
        text = Path(path).read_text()
        assert len(text) > 1500, path
        for snippet in snippets:
            assert snippet in text, f"{path} missing {snippet}"


def test_side_hustle_market_update_turns_github_signals_into_sellable_offers():
    text = Path("docs/SIDE_HUSTLE_MARKET_UPDATE_2026.ja.md").read_text()
    expected = [
        "副業向けGitHub市場アップデート",
        "2026-07-09",
        "n8n-io/n8n",
        "langgenius/dify",
        "browser-use/browser-use",
        "activepieces/activepieces",
        "Skyvern-AI/skyvern",
        "modelcontextprotocol/servers",
        "github/github-mcp-server",
        "売るべきもの",
        "売らないもの",
        "人間承認",
        "dry-run PoC",
        "5つの商品メニュー",
        "提案トーク",
        "このキットに反映する判断",
    ]
    assert len(text) > 5000
    for snippet in expected:
        assert snippet in text, f"docs/SIDE_HUSTLE_MARKET_UPDATE_2026.ja.md missing {snippet}"


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


def test_report_wizard_html_manuals_are_bilingual_self_contained_and_actionable():
    expected = {
        "docs/report-automation-wizard.html": {
            "lang": "en",
            "required": [
                "<!doctype html>",
                '<html lang="en">',
                'id="report-wizard"',
                'id="flow-diagram"',
                'id="human-approval"',
                'id="troubleshooting"',
                "Outcome and honest limits",
                "Files to prepare",
                "Full extraction support",
                "Metadata-only intake",
                "Seven-step flow",
                "Text alternative",
                "AI can decide",
                "Human must decide",
                "Privacy and local processing",
                "Exact CLI commands",
                "Exact AI-agent prompt",
                "First paid PoC example",
                "No income guarantee",
                "Related manuals",
                "Original files stay unchanged",
                "Approved copies only",
                "Images are metadata-only, with no OCR",
                "PDF intake is optional and should stay isolated",
                "Never send automatically",
                "Construction monthly report",
                "Codex, ChatGPT, Claude, Gemini, Cursor",
                "ai-automation-kit report-wizard init",
                "ai-automation-kit report-wizard inspect",
                "ai-automation-kit report-wizard confirm",
                "ai-automation-kit report-wizard answer",
                "ai-automation-kit report-wizard status --workspace",
                "ai-automation-kit report-wizard build",
                "ai-automation-kit report-wizard approve",
                "ai-automation-kit report-wizard serve",
                "report-automation-wizard-flow.mmd",
                "REPORT_AUTOMATION_GUIDE.md",
                "AI_AGENT_GRILL_ME_SKILL.md",
                "CLOUD_BEGINNER_PLAYBOOK.md",
            ],
            "forbidden": [
                "目的と正直な限界",
                "用意するファイル",
                "人間承認",
            ],
        },
        "docs/report-automation-wizard.ja.html": {
            "lang": "ja",
            "required": [
                "<!doctype html>",
                '<html lang="ja">',
                'id="report-wizard"',
                'id="flow-diagram"',
                'id="human-approval"',
                'id="troubleshooting"',
                "目的と正直な限界",
                "用意するファイル",
                "全文を扱える形式",
                "メタデータのみ扱う形式",
                "7段階フロー",
                "テキスト版",
                "AIが判断できること",
                "人間が判断すること",
                "プライバシーとローカル処理",
                "CLIコマンド",
                "AIエージェント向けプロンプト",
                "最初の有料PoC例",
                "収入保証はありません",
                "関連マニュアル",
                "原本ファイルは変更しません",
                "承認したコピーだけを使います",
                "画像はOCRせずメタデータのみ扱います",
                "PDFは任意で分離して扱います",
                "自動送信はしません",
                "建設会社の月報",
                "ai-automation-kit report-wizard init",
                "ai-automation-kit report-wizard inspect",
                "ai-automation-kit report-wizard confirm",
                "ai-automation-kit report-wizard answer",
                "ai-automation-kit report-wizard status --workspace",
                "ai-automation-kit report-wizard build",
                "ai-automation-kit report-wizard approve",
                "ai-automation-kit report-wizard serve",
                "report-automation-wizard-flow.mmd",
                "REPORT_AUTOMATION_GUIDE.ja.md",
                "AI_AGENT_GRILL_ME_SKILL.ja.md",
                "CLOUD_BEGINNER_PLAYBOOK.ja.md",
            ],
            "forbidden": [
                "Outcome and honest limits",
                "Files to prepare",
                "Human approval",
            ],
        },
    }
    for path, rules in expected.items():
        text = Path(path).read_text(encoding="utf-8")
        assert len(text) > 12000, path
        assert '<meta name="viewport" content="width=device-width, initial-scale=1"' in text
        assert "<header" in text and "<nav" in text and "<main" in text and "<section" in text and "<footer" in text
        assert 'class="skip-link"' in text
        assert "prefers-reduced-motion" in text
        assert "@media print" in text
        assert ":focus-visible" in text
        assert 'href="#main"' in text
        assert re.search(r'<main[^>]*id="main"[^>]*tabindex="-1"', text), f"{path} must make main focusable for skip links"
        assert "main:focus-visible" in text or "main#main:focus-visible" in text
        assert "main:target" in text or "main#main:target" in text
        assert text.count('data-flow-step="') == 7, f"{path} must render exactly seven visual flow steps"
        assert 'class="flow-text-alt"' in text
        assert "linear-gradient" not in text
        assert "radial-gradient" not in text
        assert "innerHTML" not in text
        assert "<script" not in text.lower()
        assert re.search(r"border-radius:\s*[1-8]px", text), f"{path} should keep radii quiet"
        assert not re.search(r"font-size\s*:\s*[^;]*vw", text), f"{path} must not use viewport font scaling"
        assert "fonts.googleapis.com" not in text
        assert "@import" not in text
        assert "src=" not in text.lower()
        if rules["lang"] == "en":
            assert not re.search(r"[\u3040-\u30ff\u4e00-\u9fff]", text), path
        for snippet in rules["required"]:
            assert snippet in text, f"{path} missing {snippet}"
        for snippet in rules["forbidden"]:
            assert snippet not in text, f"{path} should not mix language with {snippet}"
        _assert_no_broken_local_hrefs(path, text)


def test_report_wizard_japanese_manual_visible_text_stays_localized():
    text = Path("docs/report-automation-wizard.ja.html").read_text(encoding="utf-8")
    visible = _extract_visible_text(text)
    forbidden = [
        "Report wizard manual",
        "Local-only workflow",
        "Step 1:",
        "Step 2:",
        "Step 3:",
        "Step 4:",
        "Step 5:",
        "Step 6:",
        "Step 7:",
        "metadata-only",
        "plain text",
        "Generated wording requiring review",
        "ready_for_human_review",
        "schema",
        "provenance",
        "conflicts",
        "local-only",
    ]
    for snippet in forbidden:
        assert snippet not in visible, f"docs/report-automation-wizard.ja.html leaks English visible text: {snippet}"


def test_report_wizard_mermaid_source_matches_the_documented_loop():
    path = Path("docs/report-automation-wizard-flow.mmd")
    text = path.read_text(encoding="utf-8")
    required = [
        "flowchart TD",
        'goal["Set report goal"]',
        'past["Approved past completed reports"]',
        'current["Approved current-period materials"]',
        'review["Review schema and folder plan"]',
        'missing{"Missing required information?"}',
        'question["Ask one question"]',
        'draft["Build draft workspace"]',
        'approval["Human approval"]',
        "goal --> past",
        "past --> current",
        "current --> review",
        "review --> missing",
        'missing -- "Yes" --> question',
        "question --> review",
        'missing -- "No" --> draft',
        "draft --> approval",
    ]
    assert path.exists()
    for snippet in required:
        assert snippet in text, f"{path} missing {snippet}"


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


def test_codex_monthly_setup_docs_and_agent_contract_are_present_and_beginner_friendly():
    expected_docs = {
        "START_WITH_CODEX.md": [
            "Read this repository's AGENTS.md and help me create a monthly report workspace.",
            "Ask only one question at a time.",
            "codex login status",
            "ai-automation-kit office-workspace create",
            "Do not ask for an API key",
            "Do not send anything externally",
            "validate the setup before opening the local UI",
            "01_APPROVED_PAST_OUTPUTS",
            "02_PAST_SUPPORTING_FILES",
            "03_CURRENT_INPUTS",
            "macOS or Linux",
            "manual recovery",
        ],
        "START_WITH_CODEX.ja.md": [
            "このリポジトリの AGENTS.md を読み、月報自動化の作業場所を作ってください。",
            "質問は1回に1つだけ",
            "codex login status",
            "ai-automation-kit office-workspace create",
            "APIキーを要求しない",
            "外部送信しない",
            "ローカルUIを開く前に検証",
            "01_APPROVED_PAST_OUTPUTS",
            "02_PAST_SUPPORTING_FILES",
            "03_CURRENT_INPUTS",
            "macOS または Linux",
            "手動復旧",
        ],
        "AGENTS.md": [
            "one question at a time",
            "codex login status",
            "ai-automation-kit office-workspace create",
            "Do not ask for an API key",
            "Do not send anything externally",
            "Validate the setup before opening the local UI",
            "01_APPROVED_PAST_OUTPUTS",
            "02_PAST_SUPPORTING_FILES",
            "03_CURRENT_INPUTS",
            "manual recovery",
            "Phase 1A",
        ],
    }
    for path, snippets in expected_docs.items():
        text = Path(path).read_text(encoding="utf-8")
        assert len(text) > 1200, path
        for snippet in snippets:
            assert snippet in text, f"{path} missing {snippet}"


def test_readme_and_start_docs_link_daily_workflow_manuals_when_published():
    published_docs = _published_daily_workflow_docs()
    if not published_docs:
        return

    readme = Path("README.md").read_text(encoding="utf-8")
    start_en = Path("START_WITH_CODEX.md").read_text(encoding="utf-8")
    start_ja = Path("START_WITH_CODEX.ja.md").read_text(encoding="utf-8")

    for doc_path in published_docs:
        assert doc_path in readme, f"README.md missing daily workflow manual link: {doc_path}"
        assert doc_path in start_en, f"START_WITH_CODEX.md missing daily workflow manual link: {doc_path}"
        assert doc_path in start_ja, f"START_WITH_CODEX.ja.md missing daily workflow manual link: {doc_path}"


def test_office_workspace_manuals_define_mobile_overflow_contracts():
    for path in ["docs/office-workspace.html", "docs/office-workspace.ja.html"]:
        text = Path(path).read_text(encoding="utf-8")

        assert "overflow-wrap: anywhere" in text, f"{path} must break long inline code"
        assert "white-space: pre-wrap" in text, f"{path} must wrap copyable preformatted text"
        assert "min-width: 0" in text, f"{path} grid and content children must be shrinkable"
        assert 'class="troubleshooting-table"' in text
        assert ".troubleshooting-table thead" in text
        assert ".troubleshooting-table td::before" in text
        assert "content: attr(data-label)" in text
        assert text.count('data-label="') >= 18, f"{path} needs a mobile label for every troubleshooting cell"
        troubleshooting = text.split('id="troubleshooting"', 1)[1]
        assert '<table class="troubleshooting-table">' in troubleshooting


def test_office_workspace_manuals_are_published_with_localized_beginner_flows():
    expected = {
        "docs/office-workspace.html": {
            "lang": "en",
            "required": [
                "<!doctype html>",
                '<html lang="en">',
                'id="install-login"',
                'id="ask-codex"',
                'id="folders"',
                'id="three-file-types"',
                'id="inspect"',
                'id="answer"',
                'id="generate"',
                'id="cancel-retry"',
                'id="approve"',
                'id="rollover"',
                'id="boundaries"',
                'id="troubleshooting"',
                "Monthly operator workspace manual",
                "Install and confirm Codex login",
                "Ask Codex to set up the workspace",
                "The three file types",
                "Inspect the month",
                "Answer one question at a time",
                "Generate the draft",
                "Cancel and retry safely",
                "Approve the local copy",
                "Prepare the next month",
                "What AI can do",
                "What a human must decide",
                "No API key is required",
                "No external sending occurs",
                "macOS or Linux only for workspace mutation",
                "START_WITH_CODEX.md",
                "../START_WITH_CODEX.md",
                "../AGENTS.md",
                "INDEX.md",
                "codex login status",
                "ai-automation-kit office-workspace create",
                "ai-automation-kit office-workspace status --workspace",
                "ai-automation-kit office-workspace inspect --workspace",
                "ai-automation-kit office-workspace serve --root",
                "01_APPROVED_PAST_OUTPUTS",
                "02_PAST_SUPPORTING_FILES",
                "03_CURRENT_INPUTS",
                "05_DRAFTS",
                "06_APPROVED_OUTPUTS",
                "07_AUDIT",
                "screen-example",
            ],
            "forbidden": [
                "月報オペレーター作業場所マニュアル",
                "AIが判断できること",
                "人間が判断すること",
                "外部送信はしません",
                "手動復旧",
            ],
        },
        "docs/office-workspace.ja.html": {
            "lang": "ja",
            "required": [
                "<!doctype html>",
                '<html lang="ja">',
                'id="install-login"',
                'id="ask-codex"',
                'id="folders"',
                'id="three-file-types"',
                'id="inspect"',
                'id="answer"',
                'id="generate"',
                'id="cancel-retry"',
                'id="approve"',
                'id="rollover"',
                'id="boundaries"',
                'id="troubleshooting"',
                "月報オペレーター作業場所マニュアル",
                "インストールと Codex ログイン確認",
                "Codex へ作業場所作成を依頼",
                "3種類のファイル置き場",
                "対象月を確認する",
                "質問へ1つずつ答える",
                "下書きを作る",
                "停止してやり直す",
                "ローカル承認して保存する",
                "次の月を準備する",
                "AIが判断できること",
                "人間が判断すること",
                "APIキーは不要です",
                "外部送信はしません",
                "作成と承認更新は macOS または Linux のみ",
                "START_WITH_CODEX.ja.md",
                "../START_WITH_CODEX.ja.md",
                "../AGENTS.md",
                "INDEX.md",
                "codex login status",
                "ai-automation-kit office-workspace create",
                "ai-automation-kit office-workspace status --workspace",
                "ai-automation-kit office-workspace inspect --workspace",
                "ai-automation-kit office-workspace serve --root",
                "01_APPROVED_PAST_OUTPUTS",
                "02_PAST_SUPPORTING_FILES",
                "03_CURRENT_INPUTS",
                "05_DRAFTS",
                "06_APPROVED_OUTPUTS",
                "07_AUDIT",
                "screen-example",
            ],
            "forbidden": [
                "Monthly operator workspace manual",
                "What AI can do",
                "What a human must decide",
                "No external sending occurs",
                "manual recovery",
            ],
        },
    }
    for path, rules in expected.items():
        text = Path(path).read_text(encoding="utf-8")
        assert len(text) > 12000, path
        assert '<meta name="viewport" content="width=device-width, initial-scale=1"' in text
        assert "<header" in text and "<nav" in text and "<main" in text and "<section" in text and "<footer" in text
        assert 'class="skip-link"' in text
        assert "prefers-reduced-motion" in text
        assert "@media print" in text
        assert ":focus-visible" in text
        assert 'href="#main"' in text
        assert re.search(r'<main[^>]*id="main"[^>]*tabindex="-1"', text), f"{path} must make main focusable for skip links"
        assert "main:focus-visible" in text or "main#main:focus-visible" in text
        assert "main:target" in text or "main#main:target" in text
        assert text.count('data-flow-step="') == 9, f"{path} must render exactly nine visual flow steps"
        assert 'class="flow-text-alt"' in text
        assert "linear-gradient" not in text
        assert "radial-gradient" not in text
        assert "innerHTML" not in text
        assert "<script" not in text.lower()
        assert re.search(r"border-radius:\s*[1-8]px", text), f"{path} should keep radii quiet"
        assert not re.search(r"font-size\s*:\s*[^;]*vw", text), f"{path} must not use viewport font scaling"
        assert "fonts.googleapis.com" not in text
        assert "@import" not in text
        assert "src=" not in text.lower()
        if rules["lang"] == "en":
            assert not re.search(r"[\u3040-\u30ff\u4e00-\u9fff]", text), path
        for snippet in rules["required"]:
            assert snippet in text, f"{path} missing {snippet}"
        for snippet in rules["forbidden"]:
            assert snippet not in text, f"{path} should not mix language with {snippet}"
        _assert_no_broken_local_hrefs(path, text)


def test_readme_index_and_changelog_publish_the_office_workspace_beginner_route():
    readme = Path("README.md").read_text(encoding="utf-8")
    index = Path("docs/INDEX.md").read_text(encoding="utf-8")
    changelog = Path("CHANGELOG.md").read_text(encoding="utf-8")

    for snippet in [
        "Phase 1A",
        "monthly office workspace",
        "docs/office-workspace.html",
        "docs/office-workspace.ja.html",
        "START_WITH_CODEX.md",
        "START_WITH_CODEX.ja.md",
        "ai-automation-kit office-workspace create",
        "ai-automation-kit office-workspace status --workspace",
        "ai-automation-kit office-workspace inspect --workspace",
        "ai-automation-kit office-workspace serve --root",
        "macOS or Linux",
    ]:
        assert snippet in readme, f"README.md missing office workspace route: {snippet}"

    getting_started_index = index.split("## 💼", 1)[0]
    for snippet in [
        "office-workspace.ja.html",
        "office-workspace.html",
        "../START_WITH_CODEX.ja.md".replace("../", ""),
        "../START_WITH_CODEX.md".replace("../", ""),
    ]:
        assert snippet in getting_started_index, f"docs/INDEX.md missing office workspace entry: {snippet}"

    for snippet in [
        "office-workspace",
        "docs/office-workspace.ja.html",
        "docs/office-workspace.html",
        "installed-wheel",
        "release smoke",
    ]:
        assert snippet in changelog, f"CHANGELOG.md missing office workspace release note: {snippet}"


def test_cli_release_surface_includes_safe_office_workspace_commands():
    cli_text = Path("src/ai_automation_kit/cli.py").read_text(encoding="utf-8")

    for snippet in [
        'add_parser("office-workspace")',
        'add_parser("create")',
        'add_parser("status")',
        'add_parser("inspect")',
        'add_parser("serve")',
        'add_argument("--root", required=True)',
        'add_argument("--workspace", required=True)',
        'add_argument("--period", required=True)',
        'add_argument("--no-open", action="store_true")',
    ]:
        assert snippet in cli_text, f"cli.py missing office workspace surface: {snippet}"

    for forbidden in [
        "--dangerously-bypass-approvals-and-sandbox",
        "--yolo",
        "--api-key",
    ]:
        assert forbidden not in cli_text, f"cli.py must not expose unsafe office workspace flag {forbidden}"


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
    assert "README.md::ai-automation-kit report-automation" in result.stdout
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


def test_public_release_audit_script_checks_report_wizard_public_navigation():
    result = subprocess.run(
        [sys.executable, "scripts/public_release_audit.py"],
        text=True,
        capture_output=True,
        check=True,
    )

    for snippet in [
        "docs/report-automation-wizard.html",
        "docs/report-automation-wizard.ja.html",
        "docs/report-automation-wizard-flow.mmd",
        "README.md::docs/report-automation-wizard.html",
        "README.md::docs/report-automation-wizard.ja.html",
        "README.md::ai-automation-kit report-wizard serve",
        "docs/manual.html::report-automation-wizard.html",
        "docs/manual.ja.html::report-automation-wizard.ja.html",
    ]:
        assert snippet in result.stdout


def test_public_release_audit_script_checks_office_workspace_manuals_packs_and_setup_docs():
    result = subprocess.run(
        [sys.executable, "scripts/public_release_audit.py"],
        text=True,
        capture_output=True,
        check=True,
    )

    for snippet in [
        "docs/office-workspace.html",
        "docs/office-workspace.ja.html",
        "START_WITH_CODEX.md",
        "START_WITH_CODEX.ja.md",
        "AGENTS.md",
        "src/ai_automation_kit/packs/manifest.json",
        "src/ai_automation_kit/packs/monthly_report.json",
        "src/ai_automation_kit/packs/monthly_report_output.schema.json",
        "src/ai_automation_kit/packs/monthly_report_prompt.json",
        "README.md::docs/office-workspace.html",
        "README.md::docs/office-workspace.ja.html",
        "README.md::ai-automation-kit office-workspace create",
        "README.md::ai-automation-kit office-workspace status --workspace",
        "README.md::ai-automation-kit office-workspace inspect --workspace",
        "README.md::ai-automation-kit office-workspace serve --root",
        "scripts/release_smoke.py::office-workspace create",
        "scripts/release_smoke.py::office-workspace inspect",
        "scripts/release_smoke.py::office-workspace serve",
        "scripts/release_smoke.py::start_codex_run",
        "scripts/release_smoke.py::approve_draft",
        "scripts/release_smoke.py::create_period",
        "scripts/release_smoke.py::X-Office-Workspace-Token",
        "scripts/release_smoke.py::approved_sha256",
    ]:
        assert snippet in result.stdout


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


def test_release_smoke_uses_installed_cli_subprocess_for_report_wizard_server():
    text = Path("scripts/release_smoke.py").read_text(encoding="utf-8")

    assert '"report-wizard"' in text
    assert '"serve"' in text
    assert "--no-open" in text
    assert "subprocess.Popen(" in text
    assert "PYTHONUNBUFFERED" in text
    assert "signal.SIGINT" in text
    assert ".kill()" in text
    assert "TimeoutExpired" in text
    assert "/api/state" in text
    assert "report_sha256" in text
    assert "payload['data']['state']['approval']['report_sha256']" in text or 'payload["data"]["state"]["approval"]["report_sha256"]' in text
    assert "create_report_wizard_server(" not in text


def test_release_smoke_covers_installed_office_workspace_flow_without_source_tree_leakage():
    text = Path("scripts/release_smoke.py").read_text(encoding="utf-8")

    for snippet in [
        '"office-workspace"',
        '"packs"',
        '"create"',
        '"inspect"',
        '"serve"',
        '"--pack"',
        '"inquiry-daily"',
        '"2026-07-12"',
        "YYYY-MM-DD",
        "02_PAST_SUPPORTING_FILES",
        "recurring-notes.md",
        "past_supporting",
        "docs/office-workspace.html",
        "docs/office-workspace.ja.html",
        "START_WITH_CODEX.md",
        "START_WITH_CODEX.ja.md",
        "AGENTS.md",
        "manifest.json",
        "OFFICE_WORKSPACE_PACK_IDS",
        "pack_file",
        "output_schema_file",
        "prompt_template_file",
        "load_bundled_output_schema",
        "load_bundled_prompt_template",
        "save_answer",
        "start_codex_run",
        "wait_for_run",
        "approve_draft",
        "create_period",
        "X-Office-Workspace-Token",
        "/api/workspaces",
        "approved_sha256",
        "PYTHONPATH",
        "_reserve_local_port",
        "_wait_for_http_ready",
    ]:
        assert snippet in text, f"scripts/release_smoke.py missing office workspace smoke snippet: {snippet}"


def test_release_smoke_installed_wheel_flow_keeps_virtualenv_entrypoints(tmp_path, monkeypatch):
    release_smoke = _load_release_smoke_module()
    wheelhouse = tmp_path / "wheelhouse"
    wheelhouse.mkdir()
    (wheelhouse / "ai_automation_starter_kit-0.1.0-py3-none-any.whl").write_text("placeholder", encoding="utf-8")
    output = tmp_path / "smoke-output"
    commands: list[list[str]] = []
    report_calls: list[tuple[Path, Path, Path]] = []
    office_calls: list[tuple[Path, Path, Path]] = []

    def fake_run(command, cwd=None, env=None):
        normalized = [str(part) for part in command]
        commands.append(normalized)
        if normalized[:3] == [sys.executable, "-m", "venv"]:
            venv_dir = Path(normalized[3])
            (venv_dir / "bin").mkdir(parents=True, exist_ok=True)
            (venv_dir / "bin" / "python").symlink_to(Path(sys.executable))
            return
        if len(normalized) >= 4 and normalized[1:4] == ["-m", "pip", "install"]:
            cli_bin = Path(normalized[0]).parent / "ai-automation-kit"
            cli_bin.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")

    monkeypatch.setattr(release_smoke, "_run", fake_run)
    monkeypatch.setattr(
        release_smoke,
        "_run_report_wizard_installed_smoke",
        lambda cli_bin, python_bin, output_path: report_calls.append((cli_bin, python_bin, output_path)),
    )
    monkeypatch.setattr(
        release_smoke,
        "_run_office_workspace_installed_smoke",
        lambda cli_bin, python_bin, output_path: office_calls.append((cli_bin, python_bin, output_path)),
    )

    release_smoke._verify_wheel_install(wheelhouse, output)

    install_command = commands[1]
    version_command = commands[2]
    expected_output = output.resolve()

    assert install_command[0].endswith("/install-venv/bin/python")
    assert install_command[0] != str(Path(sys.executable).resolve())
    assert Path(install_command[0]).resolve() == Path(sys.executable).resolve()
    assert version_command[0].endswith("/install-venv/bin/ai-automation-kit")
    assert report_calls == [(Path(version_command[0]), Path(install_command[0]), expected_output)]
    assert office_calls == [(Path(version_command[0]), Path(install_command[0]), expected_output)]


def test_release_smoke_office_workspace_flow_uses_local_cryptography_fallback_without_source_tree(
    tmp_path, monkeypatch
):
    release_smoke = _load_release_smoke_module()
    site_packages = tmp_path / "site-packages"
    cryptography_package = site_packages / "cryptography"
    cryptography_package.mkdir(parents=True)
    fake_spec = type(
        "FakeSpec",
        (),
        {
            "submodule_search_locations": [str(cryptography_package)],
            "origin": str(cryptography_package / "__init__.py"),
        },
    )()

    monkeypatch.delattr(release_smoke.hashlib, "scrypt", raising=False)
    monkeypatch.setattr(release_smoke.importlib.util, "find_spec", lambda name: fake_spec if name == "cryptography" else None)

    python_paths = release_smoke._office_workspace_python_paths()
    env = release_smoke._isolated_installed_env(
        tmp_path / "install-venv" / "bin" / "ai-automation-kit",
        python_paths=python_paths,
    )

    assert python_paths == [site_packages.resolve()]
    assert env["PYTHONNOUSERSITE"] == "1"
    assert env["PYTHONPATH"] == str(site_packages.resolve())
    assert "/src" not in env["PYTHONPATH"]


def test_public_release_audit_script_checks_report_wizard_release_smoke_snippets():
    result = subprocess.run(
        [sys.executable, "scripts/public_release_audit.py"],
        text=True,
        capture_output=True,
        check=True,
    )

    for snippet in [
        "scripts/release_smoke.py::report-wizard session",
        "scripts/release_smoke.py::report_wizard_state.json",
        "scripts/release_smoke.py::source_manifest.json",
        "scripts/release_smoke.py::schema_proposal.json",
        "scripts/release_smoke.py::provenance.json",
        "scripts/release_smoke.py::weekly_report_draft.md",
        "scripts/release_smoke.py::approval.json",
        "scripts/release_smoke.py::report_sha256",
        "scripts/release_smoke.py::report-wizard serve",
        "scripts/release_smoke.py::subprocess.Popen",
        "scripts/release_smoke.py::PYTHONUNBUFFERED",
        "scripts/release_smoke.py::signal.SIGINT",
        "scripts/release_smoke.py::clean serve exit",
        "scripts/release_smoke.py::kill fallback",
        "scripts/release_smoke.py::close files",
        "scripts/release_smoke.py::HTTP approval hash",
        "scripts/release_smoke.py::/api/state",
    ]:
        assert snippet in result.stdout

    for snippet in [
        "scripts/release_smoke.py::office-workspace create",
        "scripts/release_smoke.py::office-workspace inspect",
        "scripts/release_smoke.py::office-workspace serve",
        "scripts/release_smoke.py::start_codex_run",
        "scripts/release_smoke.py::approve_draft",
        "scripts/release_smoke.py::create_period",
        "scripts/release_smoke.py::X-Office-Workspace-Token",
        "scripts/release_smoke.py::approved_sha256",
    ]:
        assert snippet in result.stdout


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
    assert "scripts/release_smoke.py::report-automation" in result.stdout
    assert "scripts/release_smoke.py::START_HERE_REPORT_AUTOMATION.md" in result.stdout
    assert "scripts/release_smoke.py::grill_me_report_questions.md" in result.stdout
    assert "scripts/release_smoke.py::demo_report_automation.html" in result.stdout
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
    assert "scripts/release_smoke.py::daily-monthly-report-automation" in result.stdout
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
