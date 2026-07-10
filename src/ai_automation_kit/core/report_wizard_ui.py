"""Self-contained HTML for the local report wizard browser UI."""

from __future__ import annotations

import json


_TRANSLATIONS = {
    "ja": {
        "title": "レポート設定ウィザード",
        "subtitle": "ローカル環境で資料を確認し、質問を1つずつ解決して、下書きと承認記録を作成します。",
        "goal": "目標",
        "past_reports": "過去レポート",
        "current_materials": "現行資料",
        "review": "確認",
        "questions": "質問",
        "draft": "下書き",
        "approval": "承認",
        "report_type": "レポート種別",
        "language": "言語",
        "daily": "日報",
        "weekly": "週報",
        "monthly": "月報",
        "past_uploads": "過去の完成レポート",
        "current_uploads": "現行資料",
        "upload_past": "過去レポートをアップロード",
        "upload_current": "現行資料をアップロード",
        "review_summary": "検査サマリー",
        "folder_plan": "フォルダ計画",
        "question_title": "確認質問",
        "question_help": "現在の質問だけを表示します。",
        "answer_label": "回答",
        "skip": "この質問をスキップ",
        "submit_answer": "回答を保存",
        "inspect": "資料を検査",
        "confirm": "計画を確定",
        "build": "下書きを作成",
        "approver": "承認者",
        "approve": "承認を記録",
        "next_action": "次の操作",
        "state": "状態",
        "warnings": "警告",
        "artifacts": "生成物",
        "flow_title": "処理フロー",
        "flow_alt": "処理フローのテキスト版",
        "status_idle": "待機中",
        "status_loading": "処理中",
        "status_error": "エラー",
        "status_success": "完了",
        "refresh": "状態を更新",
        "byte_unit": "バイト",
        "runtime": {
            "questions": {
                "report_audience": "このレポートを読む人は誰ですか？",
                "best_style_reference": "書き方の見本にする過去レポートはどれですか？",
                "mandatory_sections": "毎回必ず含める項目は何ですか？",
                "reporting_period": "このレポートの対象期間はいつですか？",
                "final_approver": "最終確認を行う人は誰ですか？",
                "save_destination": "承認済みレポートをどこに保存しますか？",
            },
            "conflict_question": "資料どうしの内容が一致しません。正しい内容を確認してください。",
            "reasons": {
                "Required question has not been answered": "必須の質問にまだ回答していません",
                "Required question was skipped": "必須の質問がスキップされています",
                "No readable accepted source inputs were found": "読み取れる資料が見つかりませんでした",
                "copy rejected": "ファイルをコピーできませんでした",
                "unknown reason": "理由を確認できません",
                "unsafe_destination_path": "保存先を安全に確認できません",
                "unsafe_source_path": "元ファイルを安全に確認できません",
                "copy_failed": "ファイルのコピーに失敗しました",
                "destination_changed_during_copy": "コピー中に保存先が変更されました",
                "cleanup_failed": "一時ファイルの削除に失敗しました",
                "missing_confirmed_destination": "確定した保存先が見つかりません",
                "final path is outside the confirmed destination": "保存先が確定した範囲の外にあります",
                "final copy is missing integrity metadata": "コピー結果の確認情報がありません",
                "final copy failed SHA-256 or byte-count verification": "コピー後の内容確認に失敗しました",
                "final copied input is missing or unsafe": "コピー済み資料が見つからないか、安全に確認できません",
                "rejected": "受け付けられませんでした",
            },
            "actions": {
                "Inspect approved past reports and current materials": "過去の完成レポートと今回の資料を追加し、資料を検査してください",
                "Review the folder plan and confirm it before copying approved files": "フォルダ計画を確認し、問題がなければ計画を確定してください",
                "Resolve required unresolved items before approval": "承認前に、未解決の必須項目を確認してください",
                "Build the report workspace for human review": "人が確認できる下書きを作成してください",
                "Build the report workspace": "レポートの下書きを作成してください",
                "Retry confirmation after destination_changed_during_copy": "保存先を確認して、もう一度計画を確定してください",
                "Resolve unresolved items before approval": "承認前に未解決の項目を確認してください",
                "Review the draft, then approve it": "下書きを確認し、問題がなければ承認を記録してください",
                "Approved locally; no report was sent or uploaded": "ローカルで承認を記録しました。外部への送信やアップロードは行っていません",
            },
            "answer_action": "現在の質問に回答してください",
            "stages": {
                "created": "準備中",
                "inspection_ready": "資料の確認完了",
                "folder_plan_confirmed": "フォルダ計画を確定済み",
                "questioning": "確認質問に回答中",
                "ready_for_draft": "下書きを作成できます",
                "ready_for_human_review": "人による確認待ち",
                "approved": "承認済み",
            },
            "approval_status": {"pending": "承認待ち", "approved": "承認済み"},
            "languages": {"ja": "日本語", "en": "英語"},
        },
    },
    "en": {
        "title": "Report Setup Wizard",
        "subtitle": "Review local materials, resolve one question at a time, then produce a draft and approval record.",
        "goal": "Goal",
        "past_reports": "Past Reports",
        "current_materials": "Current Materials",
        "review": "Review",
        "questions": "Questions",
        "draft": "Draft",
        "approval": "Approval",
        "report_type": "Report Type",
        "language": "Language",
        "daily": "Daily",
        "weekly": "Weekly",
        "monthly": "Monthly",
        "past_uploads": "Past Completed Reports",
        "current_uploads": "Current Materials",
        "upload_past": "Upload Past Reports",
        "upload_current": "Upload Current Materials",
        "review_summary": "Inspection Summary",
        "folder_plan": "Folder Plan",
        "question_title": "Current Question",
        "question_help": "Only one visible question is shown at a time.",
        "answer_label": "Answer",
        "skip": "Skip this question",
        "submit_answer": "Save Answer",
        "inspect": "Inspect Materials",
        "confirm": "Confirm Plan",
        "build": "Build Draft",
        "approver": "Approver",
        "approve": "Record Approval",
        "next_action": "Next Action",
        "state": "State",
        "warnings": "Warnings",
        "artifacts": "Artifacts",
        "flow_title": "Flow",
        "flow_alt": "Text alternative of the flow",
        "status_idle": "Idle",
        "status_loading": "Loading",
        "status_error": "Error",
        "status_success": "Done",
        "refresh": "Refresh State",
        "byte_unit": "bytes",
        "runtime": {
            "questions": {
                "report_audience": "Who is the audience for this report?",
                "best_style_reference": "Which past report is the best style reference?",
                "mandatory_sections": "Which sections must appear in every report?",
                "reporting_period": "What reporting period should the next report cover?",
                "final_approver": "Who is the final approver?",
                "save_destination": "Where should the approved report be saved?",
            },
            "conflict_question": "The current materials disagree. Review the approved sources and confirm the correct value.",
            "reasons": {
                "Required question has not been answered": "Required question has not been answered",
                "Required question was skipped": "Required question was skipped",
            },
            "actions": {},
            "answer_action": "Answer the current question",
            "stages": {},
            "approval_status": {},
            "languages": {"ja": "Japanese", "en": "English"},
        },
    },
}


def render_report_wizard_ui(language: str, token: str) -> str:
    if language not in _TRANSLATIONS:
        raise ValueError("language must be 'ja' or 'en'")
    strings = _TRANSLATIONS[language]
    serialized_strings = json.dumps(strings, ensure_ascii=False)
    serialized_token = json.dumps(token, ensure_ascii=False)
    return """<!doctype html>
<html lang="{page_lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f4f6f8;
      --panel: #ffffff;
      --line: #c7d2dc;
      --text: #16202a;
      --muted: #51606e;
      --accent: #2f6fb2;
      --accent-soft: #e0ecfb;
      --ok: #2f7d4a;
      --ok-soft: #e6f4ea;
      --warn: #9a6700;
      --warn-soft: #fff3d6;
      --danger: #b33b3b;
      --danger-soft: #fde8e8;
      --goal: #2f6fb2;
      --past: #4f7f5f;
      --current: #7a5fa8;
      --review: #8a6f2b;
      --question: #7a4d4d;
      --draft: #2d7a79;
      --approval: #56697d;
      --radius: 8px;
      --shadow: 0 1px 2px rgba(15, 23, 42, 0.06);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
    }}
    main {{
      max-width: 1440px;
      margin: 0 auto;
      padding: 20px;
      display: grid;
      gap: 16px;
    }}
    h1, h2, h3, p {{ margin: 0; }}
    .hero, .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
    }}
    .hero {{ padding: 20px; }}
    .hero p {{ color: var(--muted); margin-top: 8px; max-width: 72ch; }}
    .grid {{
      display: grid;
      gap: 16px;
      grid-template-columns: minmax(0, 1.45fr) minmax(320px, 0.95fr);
    }}
    .stack {{ display: grid; gap: 16px; }}
    .panel {{ padding: 16px; }}
    .panel-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 12px;
    }}
    .muted {{ color: var(--muted); }}
    .progress {{
      list-style: none;
      padding: 0;
      margin: 0;
      display: grid;
      gap: 8px;
      grid-template-columns: repeat(4, minmax(0, 1fr));
    }}
    .progress li {{
      min-width: 0;
      min-height: 72px;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px;
      background: #fbfcfd;
      display: grid;
      gap: 6px;
      align-content: start;
      overflow-wrap: anywhere;
    }}
    .progress .step-index {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 24px;
      height: 24px;
      border-radius: 999px;
      color: #fff;
      font-size: 13px;
      font-weight: 600;
    }}
    .progress li[data-step="goal"] .step-index {{ background: var(--goal); }}
    .progress li[data-step="past"] .step-index {{ background: var(--past); }}
    .progress li[data-step="current"] .step-index {{ background: var(--current); }}
    .progress li[data-step="review"] .step-index {{ background: var(--review); }}
    .progress li[data-step="questions"] .step-index {{ background: var(--question); }}
    .progress li[data-step="draft"] .step-index {{ background: var(--draft); }}
    .progress li[data-step="approval"] .step-index {{ background: var(--approval); }}
    .segmented {{
      display: inline-grid;
      grid-auto-flow: column;
      grid-auto-columns: minmax(92px, 1fr);
      border: 1px solid var(--line);
      border-radius: 6px;
      overflow: hidden;
    }}
    .segmented button {{
      min-height: 40px;
      border: 0;
      border-right: 1px solid var(--line);
      background: #f8fafc;
      color: var(--text);
      padding: 0 12px;
      font: inherit;
    }}
    .segmented button:last-child {{ border-right: 0; }}
    .segmented button[aria-pressed="true"] {{
      background: var(--accent-soft);
      color: var(--accent);
      font-weight: 600;
    }}
    .button-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    button, input[type="text"], textarea, select {{
      font: inherit;
      color: inherit;
    }}
    button {{
      min-height: 40px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      padding: 0 14px;
      cursor: pointer;
    }}
    button.primary {{
      background: var(--accent);
      border-color: var(--accent);
      color: #fff;
    }}
    button.success {{
      background: var(--ok);
      border-color: var(--ok);
      color: #fff;
    }}
    button:disabled {{
      cursor: not-allowed;
      opacity: 0.55;
    }}
    input[type="file"], input[type="text"], textarea {{
      width: 100%;
      min-height: 40px;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 8px 10px;
      background: #fff;
    }}
    textarea {{ min-height: 112px; resize: vertical; }}
    .status-strip {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .status-pill {{
      display: inline-flex;
      align-items: center;
      min-height: 32px;
      padding: 0 10px;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: #f8fafc;
      color: var(--muted);
    }}
    .status-pill.success {{ background: var(--ok-soft); color: var(--ok); border-color: #b8d9c2; }}
    .status-pill.error {{ background: var(--danger-soft); color: var(--danger); border-color: #efc0c0; }}
    .status-pill.warning {{ background: var(--warn-soft); color: var(--warn); border-color: #f0dc9a; }}
    .upload-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
    }}
    .list {{
      list-style: none;
      padding: 0;
      margin: 0;
      display: grid;
      gap: 8px;
    }}
    .list li {{
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px;
      background: #fbfcfd;
      word-break: break-word;
    }}
    .meta {{
      display: grid;
      gap: 6px;
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }}
    .meta strong {{ display: block; font-size: 13px; color: var(--muted); }}
    .flowchart {{
      display: grid;
      gap: 8px;
      grid-template-columns: repeat(7, minmax(0, 1fr));
      align-items: center;
    }}
    .flowchart .node {{
      min-height: 48px;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 8px;
      background: #fff;
      display: grid;
      place-items: center;
      text-align: center;
    }}
    .flowchart .arrow {{
      height: 2px;
      background: var(--line);
      position: relative;
    }}
    .flowchart .arrow::after {{
      content: "";
      position: absolute;
      top: -4px;
      right: 0;
      width: 10px;
      height: 10px;
      border-top: 2px solid var(--line);
      border-right: 2px solid var(--line);
      transform: rotate(45deg);
    }}
    .sr-only {{
      position: absolute;
      width: 1px;
      height: 1px;
      padding: 0;
      margin: -1px;
      overflow: hidden;
      clip: rect(0, 0, 0, 0);
      white-space: nowrap;
      border: 0;
    }}
    .message {{
      min-height: 40px;
      padding: 10px 12px;
      border-radius: 6px;
      border: 1px solid var(--line);
      background: #fbfcfd;
    }}
    .message.error {{ border-color: #efc0c0; background: var(--danger-soft); color: var(--danger); }}
    .message.success {{ border-color: #b8d9c2; background: var(--ok-soft); color: var(--ok); }}
    .message.warning {{ border-color: #f0dc9a; background: var(--warn-soft); color: var(--warn); }}
    :focus-visible {{
      outline: 3px solid rgba(47, 111, 178, 0.28);
      outline-offset: 2px;
    }}
    @media (max-width: 1080px) {{
      .grid, .upload-grid {{ grid-template-columns: 1fr; }}
      .progress {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .flowchart {{ grid-template-columns: 1fr; }}
      .flowchart .arrow {{ width: 2px; height: 20px; margin: 0 auto; }}
      .flowchart .arrow::after {{
        top: auto;
        bottom: 0;
        left: -4px;
        right: auto;
        transform: rotate(135deg);
      }}
    }}
    @media (max-width: 480px) {{
      main {{ padding: 14px; }}
      .progress {{ grid-template-columns: 1fr; }}
      .meta {{ grid-template-columns: 1fr; }}
    }}
    @media (prefers-reduced-motion: reduce) {{
      *, *::before, *::after {{
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
      }}
    }}
  </style>
</head>
<body>
  <main>
    <section class="hero" aria-labelledby="page-title">
      <h1 id="page-title">{title}</h1>
      <p>{subtitle}</p>
    </section>

    <section class="panel" aria-labelledby="progress-title">
      <div class="panel-header">
        <h2 id="progress-title">{flow_title}</h2>
        <button id="refresh-button" type="button">{refresh}</button>
      </div>
      <ol class="progress" id="progress-steps">
        <li data-step="goal"><span class="step-index">1</span><strong>{goal}</strong><span class="muted" id="step-goal-state"></span></li>
        <li data-step="past"><span class="step-index">2</span><strong>{past_reports}</strong><span class="muted" id="step-past-state"></span></li>
        <li data-step="current"><span class="step-index">3</span><strong>{current_materials}</strong><span class="muted" id="step-current-state"></span></li>
        <li data-step="review"><span class="step-index">4</span><strong>{review}</strong><span class="muted" id="step-review-state"></span></li>
        <li data-step="questions"><span class="step-index">5</span><strong>{questions}</strong><span class="muted" id="step-question-state"></span></li>
        <li data-step="draft"><span class="step-index">6</span><strong>{draft}</strong><span class="muted" id="step-draft-state"></span></li>
        <li data-step="approval"><span class="step-index">7</span><strong>{approval}</strong><span class="muted" id="step-approval-state"></span></li>
      </ol>
      <div class="panel-header" style="margin-top: 16px;">
        <h3>{flow_title}</h3>
      </div>
      <div class="flowchart" aria-hidden="true">
        <div class="node">{goal}</div>
        <div class="arrow"></div>
        <div class="node">{review}</div>
        <div class="arrow"></div>
        <div class="node">{questions}</div>
        <div class="arrow"></div>
        <div class="node">{approval}</div>
      </div>
      <h3 class="sr-only">{flow_alt}</h3>
      <ol>
        <li>{goal}</li>
        <li>{past_reports}</li>
        <li>{current_materials}</li>
        <li>{review}</li>
        <li>{questions}</li>
        <li>{draft}</li>
        <li>{approval}</li>
      </ol>
    </section>

    <div class="grid">
      <div class="stack">
        <section class="panel" aria-labelledby="goal-title">
          <div class="panel-header">
            <h2 id="goal-title">{goal}</h2>
            <span class="status-pill" id="stage-pill">{status_idle}</span>
          </div>
          <div class="meta">
            <div>
              <strong>{report_type}</strong>
              <div class="segmented" role="group" aria-label="{report_type}">
                <button type="button" data-report-type="daily" aria-pressed="false">{daily}</button>
                <button type="button" data-report-type="weekly" aria-pressed="false">{weekly}</button>
                <button type="button" data-report-type="monthly" aria-pressed="true">{monthly}</button>
              </div>
            </div>
            <div>
              <strong>{language}</strong>
              <div class="status-strip">
                <span class="status-pill">{language}</span>
                <span class="status-pill" id="language-value">{language}</span>
              </div>
            </div>
          </div>
          <div class="message" id="goal-message">{next_action}</div>
        </section>

        <section class="panel" aria-labelledby="uploads-title">
          <div class="panel-header">
            <h2 id="uploads-title">{past_reports} / {current_materials}</h2>
          </div>
          <div class="upload-grid">
            <div class="stack">
              <h3>{past_uploads}</h3>
              <input id="past-input" type="file" multiple aria-label="{upload_past}">
              <div class="button-row">
                <button id="past-upload-button" class="primary" type="button">{upload_past}</button>
              </div>
              <ul class="list" id="past-upload-list"></ul>
            </div>
            <div class="stack">
              <h3>{current_uploads}</h3>
              <input id="current-input" type="file" multiple aria-label="{upload_current}">
              <div class="button-row">
                <button id="current-upload-button" class="primary" type="button">{upload_current}</button>
              </div>
              <ul class="list" id="current-upload-list"></ul>
            </div>
          </div>
          <div class="status-strip" id="upload-status"></div>
        </section>

        <section class="panel" aria-labelledby="review-title">
          <div class="panel-header">
            <h2 id="review-title">{review_summary}</h2>
            <div class="button-row">
              <button id="inspect-button" class="primary" type="button">{inspect}</button>
              <button id="confirm-button" type="button">{confirm}</button>
            </div>
          </div>
          <div class="stack">
            <div class="message" id="review-message">{state}</div>
            <h3>{warnings}</h3>
            <ul class="list" id="warning-list"></ul>
            <h3>{folder_plan}</h3>
            <ul class="list" id="folder-plan-list"></ul>
          </div>
        </section>
      </div>

      <div class="stack">
        <section class="panel" id="question-panel" aria-labelledby="question-title">
          <div class="panel-header">
            <h2 id="question-title">{question_title}</h2>
          </div>
          <p class="muted">{question_help}</p>
          <div class="message" id="question-text">{questions}</div>
          <label for="answer-input" class="muted">{answer_label}</label>
          <textarea id="answer-input"></textarea>
          <div class="button-row">
            <button id="answer-button" class="primary" type="button">{submit_answer}</button>
            <button id="skip-button" type="button">{skip}</button>
          </div>
        </section>

        <section class="panel" aria-labelledby="draft-title">
          <div class="panel-header">
            <h2 id="draft-title">{draft}</h2>
            <button id="build-button" type="button">{build}</button>
          </div>
          <div class="message" id="draft-message">{draft}</div>
          <h3>{artifacts}</h3>
          <ul class="list" id="artifact-list"></ul>
        </section>

        <section class="panel" aria-labelledby="approval-title">
          <div class="panel-header">
            <h2 id="approval-title">{approval}</h2>
            <button id="approve-button" class="success" type="button">{approve}</button>
          </div>
          <label for="approver-input" class="muted">{approver}</label>
          <input id="approver-input" type="text" autocomplete="name">
          <div class="message" id="approval-message">{approval}</div>
        </section>
      </div>
    </div>
  </main>
  <script>
    (function () {{
      const STRINGS = {strings};
      const SESSION_TOKEN = {token};
      const state = {{
        reportType: "monthly",
        session: null,
      }};

      function byId(id) {{
        return document.getElementById(id);
      }}

      function setMessage(id, text, tone) {{
        const node = byId(id);
        node.className = "message" + (tone ? " " + tone : "");
        node.textContent = text || "";
      }}

      function setBusy(button, busy) {{
        button.disabled = busy;
        button.dataset.busy = busy ? "true" : "false";
      }}

      function clearList(id) {{
        byId(id).replaceChildren();
      }}

      function appendListItem(id, text) {{
        const item = document.createElement("li");
        item.textContent = text;
        byId(id).appendChild(item);
      }}

      function runtimeGroup(name) {{
        return (STRINGS.runtime && STRINGS.runtime[name]) || {{}};
      }}

      function translateReason(reason) {{
        let translated = reason || runtimeGroup("reasons").rejected || "rejected";
        Object.keys(runtimeGroup("reasons")).forEach(function (source) {{
          translated = translated.split(source).join(runtimeGroup("reasons")[source]);
        }});
        return translated;
      }}

      function translateQuestion(question) {{
        if (!question) {{
          return STRINGS.status_success;
        }}
        if (String(question.id || "").indexOf("conflict_") === 0) {{
          return STRINGS.runtime.conflict_question;
        }}
        return runtimeGroup("questions")[question.id] || question.prompt;
      }}

      function translateNextAction(action) {{
        const text = action || "";
        const direct = runtimeGroup("actions")[text];
        if (direct) {{
          return direct;
        }}
        if (text.indexOf("Answer current question:") === 0 || text.indexOf("Answer the current question:") === 0) {{
          return STRINGS.runtime.answer_action;
        }}
        return text;
      }}

      function translateStage(stage) {{
        return runtimeGroup("stages")[stage] || stage;
      }}

      function renderUploads(uploads) {{
        clearList("past-upload-list");
        clearList("current-upload-list");
        (uploads.past || []).forEach(function (item) {{
          appendListItem("past-upload-list", item.name + " [" + item.bytes + " " + STRINGS.byte_unit + "]");
        }});
        (uploads.current || []).forEach(function (item) {{
          appendListItem("current-upload-list", item.name + " [" + item.bytes + " " + STRINGS.byte_unit + "]");
        }});
      }}

      function renderWarnings(statePayload) {{
        clearList("warning-list");
        const warnings = [];
        (statePayload.rejected || []).forEach(function (item) {{
          warnings.push((item.name || item.original_path || "item") + ": " + translateReason(item.reason));
        }});
        (statePayload.unresolved_items || []).forEach(function (item) {{
          warnings.push(item.id + ": " + translateReason(item.reason));
        }});
        if (!warnings.length) {{
          warnings.push(STRINGS.status_success);
        }}
        warnings.forEach(function (text) {{
          appendListItem("warning-list", text);
        }});
      }}

      function renderFolderPlan(statePayload) {{
        clearList("folder-plan-list");
        const groups = ["past_completed_reports", "current_materials"];
        groups.forEach(function (group) {{
          (statePayload.folder_plan[group] || []).forEach(function (item) {{
            appendListItem("folder-plan-list", (item.name || item.source_path || "item") + " -> " + item.destination);
          }});
        }});
      }}

      function renderArtifacts(statePayload) {{
        clearList("artifact-list");
        Object.keys(statePayload.artifacts || {{}}).forEach(function (key) {{
          appendListItem("artifact-list", key + ": " + statePayload.artifacts[key]);
        }});
      }}

      function renderQuestion(statePayload) {{
        const current = statePayload.current_question;
        byId("answer-input").value = "";
        byId("answer-input").disabled = !current;
        byId("answer-button").disabled = !current;
        byId("skip-button").disabled = !current;
        byId("question-text").textContent = translateQuestion(current);
      }}

      function renderProgress(stage) {{
        const mapping = {{
          created: ["step-goal-state"],
          inspection_ready: ["step-goal-state", "step-past-state", "step-current-state", "step-review-state"],
          folder_plan_confirmed: ["step-goal-state", "step-past-state", "step-current-state", "step-review-state"],
          questioning: ["step-goal-state", "step-past-state", "step-current-state", "step-review-state", "step-question-state"],
          ready_for_draft: ["step-goal-state", "step-past-state", "step-current-state", "step-review-state", "step-question-state", "step-draft-state"],
          ready_for_human_review: ["step-goal-state", "step-past-state", "step-current-state", "step-review-state", "step-question-state", "step-draft-state"],
          approved: ["step-goal-state", "step-past-state", "step-current-state", "step-review-state", "step-question-state", "step-draft-state", "step-approval-state"],
        }};
        [
          "step-goal-state",
          "step-past-state",
          "step-current-state",
          "step-review-state",
          "step-question-state",
          "step-draft-state",
          "step-approval-state",
        ].forEach(function (id) {{
          byId(id).textContent = "";
        }});
        (mapping[stage] || []).forEach(function (id) {{
          byId(id).textContent = STRINGS.status_success;
        }});
      }}

      function renderState(payload) {{
        state.session = payload.data.state;
        state.reportType = state.session.report_type;
        renderUploads(payload.data.uploads);
        renderWarnings(state.session);
        renderFolderPlan(state.session);
        renderArtifacts(state.session);
        renderQuestion(state.session);
        renderProgress(state.session.stage);
        setMessage("goal-message", translateNextAction(payload.next_action), "");
        setMessage("review-message", STRINGS.state + ": " + translateStage(state.session.stage), "");
        setMessage("draft-message", state.session.artifacts.draft || STRINGS.draft, state.session.artifacts.draft ? "success" : "");
        setMessage("approval-message", runtimeGroup("approval_status")[state.session.approval.status] || state.session.approval.status || STRINGS.approval, state.session.approval.status === "approved" ? "success" : "");
        byId("stage-pill").textContent = translateStage(state.session.stage);
        byId("language-value").textContent = runtimeGroup("languages")[state.session.language] || state.session.language;
        Array.prototype.forEach.call(document.querySelectorAll("[data-report-type]"), function (button) {{
          button.setAttribute("aria-pressed", button.dataset.reportType === state.reportType ? "true" : "false");
        }});
      }}

      async function apiFetch(path, options) {{
        const merged = Object.assign({{ method: "GET", credentials: "same-origin" }}, options || {{}});
        const headers = new Headers(merged.headers || {{}});
        headers.set("X-Report-Wizard-Token", SESSION_TOKEN);
        headers.set("Accept", "application/json");
        merged.headers = headers;
        const response = await fetch(path, merged);
        const payload = await response.json();
        if (!response.ok || !payload.ok) {{
          throw new Error((payload.error && payload.error.message) || STRINGS.status_error);
        }}
        return payload;
      }}

      async function refreshState() {{
        try {{
          renderState(await apiFetch("/api/state"));
        }} catch (error) {{
          setMessage("review-message", translateReason(error.message), "error");
        }}
      }}

      async function postJson(path, data, messageId, successTone) {{
        try {{
          const payload = await apiFetch(path, {{
            method: "POST",
            headers: {{ "Content-Type": "application/json" }},
            body: JSON.stringify(data || {{}}),
          }});
          renderState(payload);
          if (messageId) {{
            setMessage(messageId, translateNextAction(payload.next_action), successTone || "success");
          }}
        }} catch (error) {{
          if (messageId) {{
            setMessage(messageId, translateReason(error.message), "error");
          }}
        }}
      }}

      async function upload(role, inputId, messageId) {{
        const input = byId(inputId);
        const files = input.files;
        if (!files || !files.length) {{
          setMessage(messageId, STRINGS.warnings, "warning");
          return;
        }}
        const body = new FormData();
        Array.prototype.forEach.call(files, function (file) {{
          body.append("files", file, file.name);
        }});
        try {{
          const payload = await apiFetch("/api/upload?role=" + encodeURIComponent(role), {{
            method: "POST",
            body: body,
          }});
          renderState(payload);
          setMessage(messageId, payload.data.saved.length + " " + STRINGS.status_success, "success");
          input.value = "";
        }} catch (error) {{
          setMessage(messageId, translateReason(error.message), "error");
        }}
      }}

      Array.prototype.forEach.call(document.querySelectorAll("[data-report-type]"), function (button) {{
        button.addEventListener("click", function () {{
          postJson("/api/goal", {{ report_type: button.dataset.reportType, language: document.documentElement.lang }}, "goal-message", "success");
        }});
      }});
      byId("refresh-button").addEventListener("click", refreshState);
      byId("past-upload-button").addEventListener("click", function () {{ upload("past", "past-input", "goal-message"); }});
      byId("current-upload-button").addEventListener("click", function () {{ upload("current", "current-input", "goal-message"); }});
      byId("inspect-button").addEventListener("click", function () {{ postJson("/api/inspect", {{}}, "review-message", "success"); }});
      byId("confirm-button").addEventListener("click", function () {{ postJson("/api/confirm", {{}}, "review-message", "success"); }});
      byId("build-button").addEventListener("click", function () {{ postJson("/api/build", {{}}, "draft-message", "success"); }});
      byId("answer-button").addEventListener("click", function () {{
        postJson("/api/answer", {{ answer: byId("answer-input").value, skipped: false }}, "question-text", "success");
      }});
      byId("skip-button").addEventListener("click", function () {{
        postJson("/api/answer", {{ answer: "", skipped: true }}, "question-text", "warning");
      }});
      byId("approve-button").addEventListener("click", function () {{
        postJson("/api/approve", {{ approver: byId("approver-input").value }}, "approval-message", "success");
      }});

      refreshState();
    }})();
  </script>
</body>
</html>
""".format(
        page_lang=language,
        title=strings["title"],
        subtitle=strings["subtitle"],
        flow_title=strings["flow_title"],
        refresh=strings["refresh"],
        goal=strings["goal"],
        past_reports=strings["past_reports"],
        current_materials=strings["current_materials"],
        review=strings["review"],
        questions=strings["questions"],
        draft=strings["draft"],
        approval=strings["approval"],
        report_type=strings["report_type"],
        language=strings["language"],
        daily=strings["daily"],
        weekly=strings["weekly"],
        monthly=strings["monthly"],
        next_action=strings["next_action"],
        state=strings["state"],
        status_idle=strings["status_idle"],
        status_success=strings["status_success"],
        warnings=strings["warnings"],
        past_uploads=strings["past_uploads"],
        current_uploads=strings["current_uploads"],
        upload_past=strings["upload_past"],
        upload_current=strings["upload_current"],
        review_summary=strings["review_summary"],
        folder_plan=strings["folder_plan"],
        question_title=strings["question_title"],
        question_help=strings["question_help"],
        answer_label=strings["answer_label"],
        skip=strings["skip"],
        submit_answer=strings["submit_answer"],
        inspect=strings["inspect"],
        confirm=strings["confirm"],
        build=strings["build"],
        approver=strings["approver"],
        approve=strings["approve"],
        artifacts=strings["artifacts"],
        flow_alt=strings["flow_alt"],
        strings=serialized_strings,
        token=serialized_token,
    )
