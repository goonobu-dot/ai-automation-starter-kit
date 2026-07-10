from __future__ import annotations

import json
from pathlib import Path


REPORT_WORKSPACE_DIRS = [
    "01_past_outputs/daily_reports",
    "01_past_outputs/weekly_reports",
    "01_past_outputs/monthly_reports",
    "02_current_materials/sales_csv",
    "02_current_materials/meeting_notes",
    "02_current_materials/photos",
    "02_current_materials/attachments",
    "02_current_materials/task_logs",
    "03_templates",
    "04_ai_analysis",
    "05_grill_me_questions",
    "06_drafts",
    "07_approval",
    "scripts",
]


def generate_report_automation_pack(
    report_type: str,
    output: Path,
    client_type: str = "local-business",
    niche: str = "operations",
    past_outputs: Path | None = None,
    materials: Path | None = None,
) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    for directory in REPORT_WORKSPACE_DIRS:
        (output / directory).mkdir(parents=True, exist_ok=True)

    payload = {
        "status": "ready",
        "report_type": report_type,
        "client_type": client_type,
        "niche": niche,
        "past_outputs": str(past_outputs) if past_outputs else "",
        "materials": str(materials) if materials else "",
        "principle": "Use past completed reports as style evidence, ask one GrillMe question at a time when facts are unclear, and keep final submission behind human approval.",
        "first_files_to_open": [
            "START_HERE_REPORT_AUTOMATION.md",
            "workspace_map.md",
            "ai_agent_prompt.md",
            "05_grill_me_questions/questions.md",
            "07_approval/approval_checklist.md",
        ],
    }

    (output / "report_automation.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "START_HERE_REPORT_AUTOMATION.md").write_text(_render_start(payload), encoding="utf-8")
    (output / "workspace_map.md").write_text(_render_workspace_map(payload), encoding="utf-8")
    (output / "ai_agent_prompt.md").write_text(_render_ai_agent_prompt(payload), encoding="utf-8")
    (output / "grill_me_report_questions.md").write_text(_render_grill_me_report_questions(payload), encoding="utf-8")
    (output / "missing_info_policy.md").write_text(_render_missing_info_policy(payload), encoding="utf-8")
    (output / "proposal_one_pager.md").write_text(_render_proposal_one_pager(payload), encoding="utf-8")
    (output / "demo_report_automation.html").write_text(_render_demo_html(payload), encoding="utf-8")
    (output / "source_reference_paths.md").write_text(_render_source_reference_paths(payload), encoding="utf-8")
    (output / "03_templates/daily_report_template.md").write_text(_render_daily_template(), encoding="utf-8")
    (output / "03_templates/weekly_report_template.md").write_text(_render_weekly_template(), encoding="utf-8")
    (output / "03_templates/monthly_report_template.md").write_text(_render_monthly_template(), encoding="utf-8")
    (output / "04_ai_analysis/writing_style_profile.md").write_text(_render_style_profile(), encoding="utf-8")
    (output / "04_ai_analysis/required_fields.json").write_text(_render_required_fields(), encoding="utf-8")
    (output / "04_ai_analysis/missing_facts.md").write_text(_render_missing_facts(), encoding="utf-8")
    (output / "04_ai_analysis/contradiction_check.md").write_text(_render_contradiction_check(), encoding="utf-8")
    (output / "05_grill_me_questions/questions.md").write_text(_render_questions_file(payload), encoding="utf-8")
    (output / "05_grill_me_questions/answers.md").write_text(_render_answers_file(), encoding="utf-8")
    (output / "05_grill_me_questions/unresolved_items.md").write_text(_render_unresolved_items(), encoding="utf-8")
    (output / "06_drafts/daily_report_draft.md").write_text(_render_daily_draft(), encoding="utf-8")
    (output / "06_drafts/weekly_report_draft.md").write_text(_render_weekly_draft(), encoding="utf-8")
    (output / "06_drafts/monthly_report_draft.md").write_text(_render_monthly_draft(), encoding="utf-8")
    (output / "07_approval/approval_checklist.md").write_text(_render_approval_checklist(payload), encoding="utf-8")
    (output / "07_approval/final_report.md").write_text(_render_final_report_placeholder(), encoding="utf-8")
    (output / "scripts/run_report_dry_run.py").write_text(_render_dry_run_script(report_type), encoding="utf-8")
    return payload


def _render_start(payload: dict) -> str:
    report_label = _report_label(payload["report_type"])
    return "\n".join(
        [
            f"# {report_label}AI下書き自動化パック",
            "",
            "このフォルダは、過去の完成物と今回の資料を使って、AIに日報・週報・月報の下書きを作らせるための作業場所です。",
            "",
            "最初から完全自動提出を目指しません。AIが判断できないところは GrillMe 方式で1問ずつ確認し、最後は人間が承認します。",
            "",
            "## 最初にやること",
            "",
            "1. 過去に提出済みの日報・週報・月報を `01_past_outputs/` に入れます。",
            "2. 今回使うCSV、議事録、写真、添付資料、作業ログを `02_current_materials/` に入れます。",
            "3. `python3 scripts/run_report_dry_run.py` を実行します。",
            "4. `05_grill_me_questions/questions.md` の質問に1つずつ答えます。",
            "5. `06_drafts/` の下書きを確認し、`07_approval/approval_checklist.md` で承認します。",
            "",
            "## 重要な安全ルール",
            "",
            "- AIは根拠がない数字や理由を作ってはいけません。",
            "- 不明点は `05_grill_me_questions/questions.md` に書き出します。",
            "- 本番提出、送信、共有、クラウド同期は人間承認後に行います。",
            "- APIキー、パスワード、顧客の秘密情報はAIチャットに貼りません。",
            "",
        ]
    )


def _render_workspace_map(payload: dict) -> str:
    return "\n".join(
        [
            "# Workspace Map",
            "",
            "| Folder | Purpose |",
            "|---|---|",
            "| `01_past_outputs/` | Past completed reports used as style and structure evidence. |",
            "| `02_current_materials/` | Current CSVs, notes, attachments, photos, and task logs. |",
            "| `03_templates/` | Report templates the AI should follow. |",
            "| `04_ai_analysis/` | Style profile, required fields, missing facts, and contradiction checks. |",
            "| `05_grill_me_questions/` | One-question-at-a-time interview files. |",
            "| `06_drafts/` | AI draft reports. |",
            "| `07_approval/` | Human approval checklist and final report placeholder. |",
            "| `scripts/` | Local dry-run helper script. |",
            "",
            "## Why This Is Sellable",
            "",
            "Many small teams already have repeated reporting work, but they do not know how to turn past reports and folders into an AI workflow. This pack gives them a safe first step: local files, draft output, GrillMe questions, and human approval.",
            "",
        ]
    )


def _render_ai_agent_prompt(payload: dict) -> str:
    selected_draft = "06_drafts/{}_report_draft.md".format(payload["report_type"])
    selected_report_phrase = "{} business reports".format(payload["report_type"])
    return "\n".join(
        [
            "# AI Agent Prompt For Report Automation",
            "",
            "Use this prompt in ChatGPT, Claude, Gemini, Cursor, Codex, Claude Code, or another AI agent after placing sample files in this workspace.",
            "",
            "```text",
            "You are helping prepare a safe local dry-run for daily, weekly, or monthly business reports.",
            "The selected report type for this workspace is {}.".format(selected_report_phrase),
            "Read the folder structure first.",
            "Use past completed reports only as style, section, and required-field evidence.",
            "Use current materials only as factual evidence for the new report.",
            "If a number, cause, customer claim, task status, or conclusion is unclear, do not invent it.",
            "Instead, write one GrillMe question at a time in 05_grill_me_questions/questions.md.",
            "Keep all final submission, external sharing, and client-facing claims behind human approval.",
            "Never ask the user to paste API keys, passwords, or private customer data into chat.",
            "Produce these files: 04_ai_analysis/writing_style_profile.md, 04_ai_analysis/missing_facts.md, {}, and 07_approval/approval_checklist.md.".format(selected_draft),
            "```",
            "",
            "## GrillMe Behavior",
            "",
            "- Ask one question at a time.",
            "- Challenge vague answers.",
            "- Separate fact questions from opinion questions.",
            "- Stop if the report would require unsupported claims.",
            "- Keep a human approval gate before final submission.",
            "",
        ]
    )


def _render_grill_me_report_questions(payload: dict) -> str:
    return "\n".join(
        [
            "# GrillMe Report Questions",
            "",
            "Use these when the AI cannot confidently finish the report from folder evidence.",
            "",
            "1. Which period should this report cover?",
            "2. Which past report is the best style reference?",
            "3. What must be included every time?",
            "4. Which numbers are final, and which are estimates?",
            "5. What changed compared with the previous period?",
            "6. What is the main reason for any increase or decrease?",
            "7. Which items still need owner confirmation?",
            "8. Which claims must not be written unless a human confirms them?",
            "9. Who approves the final report?",
            "10. Where should the approved report be saved or submitted?",
            "",
        ]
    )


def _render_missing_info_policy(payload: dict) -> str:
    return "\n".join(
        [
            "# Missing Information Policy",
            "",
            "AI may draft the report only when the source folder supports the facts. If evidence is missing, the AI must stop and ask.",
            "",
            "## Must Ask Before Writing",
            "",
            "- Reason for sales, volume, complaint, delay, or quality changes.",
            "- Any customer-facing explanation.",
            "- Any number that conflicts across files.",
            "- Any claim about causes, responsibility, future plans, or commitments.",
            "- Any issue involving money, contracts, legal, medical, HR, or safety decisions.",
            "",
            "## Safe Placeholder",
            "",
            "Use `未確認: 人間確認が必要` instead of inventing missing content.",
            "",
        ]
    )


def _render_proposal_one_pager(payload: dict) -> str:
    return "\n".join(
        [
            "# Proposal: Folder-Based Report Automation",
            "",
            "## Offer",
            "",
            "We prepare a local dry-run system that drafts daily, weekly, or monthly business reports from past completed reports and current source folders.",
            "",
            "## What The Client Gets",
            "",
            "- Folder structure for past reports and current materials.",
            "- AI prompt for drafting reports safely.",
            "- GrillMe question loop for unclear facts.",
            "- Draft report and missing-information list.",
            "- Human approval checklist before final submission.",
            "- Browser demo page for explaining the workflow.",
            "",
            "## First Paid PoC Scope",
            "",
            "- One report type.",
            "- One business unit or location.",
            "- Three to ten past reports.",
            "- One current period's source folder.",
            "- Local dry-run only.",
            "- No automatic submission.",
            "",
            "## Suggested Price Range",
            "",
            "- Starter dry-run PoC: 50,000 to 150,000 JPY.",
            "- Setup plus first month support: 100,000 to 300,000 JPY.",
            "- Monthly maintenance: 30,000 to 100,000 JPY, depending on volume and review cadence.",
            "",
        ]
    )


def _render_demo_html(payload: dict) -> str:
    return """<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>日報・月報AI下書き自動化デモ</title>
  <style>
    body { margin: 0; font-family: Arial, sans-serif; background: #f5f7fb; color: #17202a; }
    header { background: #17324d; color: white; padding: 28px; }
    main { max-width: 1080px; margin: 0 auto; padding: 24px; }
    section { background: white; border: 1px solid #d8dee4; border-radius: 8px; padding: 18px; margin-bottom: 16px; }
    h1, h2 { margin-top: 0; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 16px; }
    .badge { display: inline-block; background: #fff8c5; color: #7d4e00; padding: 4px 8px; border-radius: 6px; font-weight: 700; }
    li { margin: 8px 0; }
  </style>
</head>
<body>
  <header>
    <p class="badge">Local dry-run / Human approval</p>
    <h1>日報・月報AI下書き自動化</h1>
    <p>過去完成物と今回資料をフォルダに入れ、AIが下書きし、不明点だけGrillMe方式で確認します。</p>
  </header>
  <main>
    <div class="grid">
      <section><h2>1. 過去完成物</h2><p>提出済みの日報・月報から書き方、見出し、必須項目を読み取ります。</p></section>
      <section><h2>2. 今回資料</h2><p>CSV、議事録、写真、添付資料、作業ログを根拠として扱います。</p></section>
      <section><h2>3. GrillMe質問</h2><p>理由や数字が不明な場合は、AIが1問ずつ確認します。</p></section>
      <section><h2>4. 人間承認</h2><p>最終提出や共有は人間が確認してから行います。</p></section>
    </div>
    <section>
      <h2>副業で売りやすい理由</h2>
      <ul>
        <li>日報・月報は多くの会社で毎月発生します。</li>
        <li>フォルダ投入型なので初心者にも説明しやすいです。</li>
        <li>完全自動ではなく下書きと承認なので導入リスクを下げられます。</li>
      </ul>
    </section>
  </main>
</body>
</html>
"""


def _render_source_reference_paths(payload: dict) -> str:
    lines = [
        "# Source Reference Paths",
        "",
        "This file records optional external folders. The pack does not copy secrets or production data by default.",
        "",
        f"- Past outputs path: `{payload['past_outputs'] or 'not provided'}`",
        f"- Current materials path: `{payload['materials'] or 'not provided'}`",
        "",
        "Copy only approved sample files into this workspace for the first dry-run.",
        "",
    ]
    return "\n".join(lines)


def _render_daily_template() -> str:
    return "\n".join(["# Daily Report", "", "- Date:", "- Work completed:", "- Numbers / metrics:", "- Issues:", "- Tomorrow's actions:", "- Human confirmation needed:", ""])


def _render_monthly_template() -> str:
    return "\n".join(["# Monthly Report", "", "- Month:", "- Summary:", "- KPI changes:", "- Main achievements:", "- Issues and causes:", "- Next month actions:", "- Human confirmation needed:", ""])


def _render_weekly_template() -> str:
    return "\n".join(["# Weekly Report", "", "- Week:", "- Summary:", "- KPI changes:", "- Main achievements:", "- Issues and causes:", "- Next week actions:", "- Human confirmation needed:", ""])


def _render_style_profile() -> str:
    return "\n".join(["# Writing Style Profile", "", "Run `python3 scripts/run_report_dry_run.py` after adding approved sample files. The AI should update this file with section structure, tone, repeated phrases, and required fields found in past completed reports.", ""])


def _render_required_fields() -> str:
    return json.dumps(
        {
            "daily": ["date", "work_completed", "metrics", "issues", "next_actions", "human_confirmation_needed"],
            "weekly": ["week", "summary", "kpi_changes", "achievements", "issues_and_causes", "next_week_actions", "human_confirmation_needed"],
            "monthly": ["month", "summary", "kpi_changes", "achievements", "issues_and_causes", "next_month_actions", "human_confirmation_needed"],
        },
        ensure_ascii=False,
        indent=2,
    ) + "\n"


def _render_missing_facts() -> str:
    return "# Missing Facts\n\n- Add unresolved facts here after the dry-run.\n"


def _render_contradiction_check() -> str:
    return "# Contradiction Check\n\n- Add conflicting numbers, dates, claims, or source statements here.\n"


def _render_questions_file(payload: dict) -> str:
    return "\n".join(["# Questions", "", "Ask one question at a time. Do not ask for passwords, API keys, or private customer records in chat.", "", "1. Which past report should be treated as the best style reference?", "2. Which facts in the current materials are final and approved?", "3. Who must approve the final report?", ""])


def _render_answers_file() -> str:
    return "# Answers\n\nWrite human answers here. Keep one answer per question.\n"


def _render_unresolved_items() -> str:
    return "# Unresolved Items\n\n- No unresolved items recorded yet.\n"


def _render_daily_draft() -> str:
    return "# Daily Report Draft\n\n未確認: `02_current_materials/` に資料を入れて dry-run を実行してください。\n"


def _render_monthly_draft() -> str:
    return "# Monthly Report Draft\n\n未確認: `02_current_materials/` に資料を入れて dry-run を実行してください。\n"


def _render_weekly_draft() -> str:
    return "# Weekly Report Draft\n\n未確認: `02_current_materials/` に資料を入れて dry-run を実行してください。\n"


def _render_approval_checklist(payload: dict) -> str:
    return "\n".join(["# Approval Checklist", "", "- [ ] Period is correct.", "- [ ] Required source files were reviewed.", "- [ ] Numbers are supported by source files.", "- [ ] Causes and explanations were confirmed by a human.", "- [ ] No unsupported promises, prices, legal claims, or customer-facing statements remain.", "- [ ] Final approver reviewed the draft.", "- [ ] Final report can be saved or submitted manually.", ""])


def _render_final_report_placeholder() -> str:
    return "# Final Report\n\nDo not use this as final until the approval checklist is complete.\n"


def _render_dry_run_script(report_type: str) -> str:
    draft_path = "06_drafts/{}_report_draft.md".format(report_type)
    report_heading = {
        "daily": "Daily",
        "weekly": "Weekly",
        "monthly": "Monthly",
    }.get(report_type, "Report")
    json_report_type = json.dumps(report_type)
    return r'''from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_EXTENSIONS = {".md", ".txt", ".csv", ".json"}
REPORT_TYPE = ''' + json_report_type + r'''
DRAFT_PATH = ROOT / ''' + json.dumps(draft_path) + r'''
REPORT_HEADING = ''' + json.dumps(report_heading) + r'''


def collect_files(base: Path) -> list[Path]:
    if not base.exists():
        return []
    return sorted(path for path in base.rglob("*") if path.is_file() and path.suffix.lower() in TEXT_EXTENSIONS)


def short_preview(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return " / ".join(lines[:3])[:300]


def main() -> int:
    past_files = collect_files(ROOT / "01_past_outputs")
    material_files = collect_files(ROOT / "02_current_materials")
    manifest = {
        "report_type": REPORT_TYPE,
        "past_file_count": len(past_files),
        "material_file_count": len(material_files),
        "past_files": [str(path.relative_to(ROOT)) for path in past_files],
        "material_files": [str(path.relative_to(ROOT)) for path in material_files],
    }
    (ROOT / "04_ai_analysis" / "source_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    style_lines = ["# Writing Style Profile", "", f"- Past completed report files found: {len(past_files)}"]
    for path in past_files[:10]:
        style_lines.append(f"- `{path.relative_to(ROOT)}`: {short_preview(path)}")
    if not past_files:
        style_lines.append("- 未確認: Add past completed reports to learn style, headings, and required fields.")
    (ROOT / "04_ai_analysis" / "writing_style_profile.md").write_text("\n".join(style_lines) + "\n", encoding="utf-8")

    missing = ["# Missing Facts", ""]
    if not past_files:
        missing.append("- Past completed reports are missing. Add at least one approved report.")
    if not material_files:
        missing.append("- Current materials are missing. Add CSVs, notes, attachments, or task logs.")
    if past_files and material_files:
        missing.append("- Confirm the reporting period and final approver before submission.")
        missing.append("- Confirm any causes behind numeric changes before writing them as facts.")
    (ROOT / "04_ai_analysis" / "missing_facts.md").write_text("\n".join(missing) + "\n", encoding="utf-8")

    questions = [
        "# Questions",
        "",
        "Ask one question at a time. Keep final submission behind human approval.",
        "",
    ]
    if not past_files:
        questions.append("1. Which past completed report can be added as the best style reference?")
    elif not material_files:
        questions.append("1. Which current-period materials should be added before drafting?")
    else:
        questions.extend(
            [
                "1. Which reporting period should this draft cover?",
                "2. Which numeric changes need human explanation?",
                "3. Who is the final approver?",
            ]
        )
    (ROOT / "05_grill_me_questions" / "questions.md").write_text("\n".join(questions) + "\n", encoding="utf-8")

    material_summary = "\n".join(f"- `{path.relative_to(ROOT)}`: {short_preview(path)}" for path in material_files[:12])
    if not material_summary:
        material_summary = "- 未確認: Current materials are not available yet."
    draft = "\n".join(
        [
            f"# {REPORT_HEADING} Report Draft",
            "",
            "## Source Summary",
            "",
            material_summary,
            "",
            "## Draft Narrative",
            "",
            "未確認: Use the source summary and GrillMe answers to write the final narrative. Do not invent missing causes or numbers.",
            "",
            "## Human Confirmation Needed",
            "",
            "- Reporting period",
            "- Final numbers",
            "- Causes of major changes",
            "- Final approver",
            "",
        ]
    )
    DRAFT_PATH.write_text(draft, encoding="utf-8")
    print(f"past_files={len(past_files)}")
    print(f"material_files={len(material_files)}")
    print(f"report_type={REPORT_TYPE}")
    print("questions=05_grill_me_questions/questions.md")
    print(f"draft={DRAFT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def _report_label(report_type: str) -> str:
    labels = {"daily": "日報", "weekly": "週報", "monthly": "月報"}
    return labels.get(report_type, "報告書")
