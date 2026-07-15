"""Self-contained browser UI for the local Autopilot Proof Lab."""

from __future__ import annotations

import html
import json


LANGUAGES = {"ja", "en"}


COPY = {
    "ja": {
        "title": "Autopilot Proof Lab",
        "subtitle": "ローカル評価ダッシュボード",
        "next_action_label": "次のアクション",
        "assessment": "評価対象",
        "decision": "判定",
        "counts": "証拠とケース",
        "gates": "ハードゲート",
        "levels": "L0-L4の意味",
        "reports": "レポート",
        "warnings": "注意事項",
        "loading": "状態を読み込んでいます...",
        "refresh": "再読み込み",
        "evaluate": "評価を実行",
        "gate_form": "ゲート更新",
        "gate_name": "ゲート名",
        "gate_status": "状態",
        "gate_owner": "責任者",
        "gate_note": "メモ",
        "gate_evidence": "証拠ID (カンマ区切り)",
        "gate_submit": "ゲートを保存",
        "identity_assessment_id": "評価ID",
        "identity_stage": "ステージ",
        "identity_maximum_level": "到達可能レベル",
        "identity_pack": "パック",
        "identity_org": "組織",
        "identity_objective": "目的",
        "identity_requested": "要求レベル",
        "identity_language": "表示言語",
        "count_evidence": "証拠件数",
        "count_cases": "ケース件数",
        "count_blocking": "未通過ゲート",
        "stale": "古い評価",
        "fresh": "最新",
        "advisory": "この画面は助言専用です。外部アクションは実行されません。承認フローは解除されません。",
        "no_external": "外部アクションは実行されません。",
        "no_approval": "承認フローは解除されません。",
        "cli_intro": "証拠やケースを追加するには、同じワークスペースで次のCLIを実行してください。",
        "cli_evidence": "ai-automation-kit autopilot-proof-lab add-evidence --workspace <workspace> --source <source-file> --role policy --classification internal --provided-by Owner",
        "cli_case": "ai-automation-kit autopilot-proof-lab add-case --workspace <workspace> --case-id <case-id> --input <input> --expected <expected> --proposed <proposed> --risk-tier medium --case-class normal --expected-route standard --proposed-route standard",
        "levels_rows": [
            ("L0", "未準備。入力や完了条件が固まっていません。"),
            ("L1", "補助のみ。人が判断し、システムは材料をそろえます。"),
            ("L2", "シャドー評価。過去事例を比較して差分を確認します。"),
            ("L3", "条件付き自動運転の助言。強い証拠があっても外部実行はしません。"),
            ("L4", "標準経路の高い成熟度。ここでも外部実行や承認解除はしません。"),
        ],
    },
    "en": {
        "title": "Autopilot Proof Lab",
        "subtitle": "Local readiness dashboard",
        "next_action_label": "Next action",
        "assessment": "Assessment",
        "decision": "Decision",
        "counts": "Evidence and cases",
        "gates": "Hard gates",
        "levels": "What L0-L4 means",
        "reports": "Reports",
        "warnings": "Warnings",
        "loading": "Loading current status...",
        "refresh": "Refresh",
        "evaluate": "Run evaluation",
        "gate_form": "Update gate",
        "gate_name": "Gate",
        "gate_status": "Status",
        "gate_owner": "Owner",
        "gate_note": "Note",
        "gate_evidence": "Evidence IDs (comma-separated)",
        "gate_submit": "Save gate",
        "identity_assessment_id": "Assessment ID",
        "identity_stage": "Stage",
        "identity_maximum_level": "Maximum level",
        "identity_pack": "Pack",
        "identity_org": "Organization",
        "identity_objective": "Objective",
        "identity_requested": "Requested level",
        "identity_language": "Language",
        "count_evidence": "Evidence count",
        "count_cases": "Case count",
        "count_blocking": "Blocking gates",
        "stale": "Stale",
        "fresh": "Fresh",
        "advisory": "This screen is advisory only. No external actions run from this screen. No approval removal happens here.",
        "no_external": "No external actions run from this screen.",
        "no_approval": "No approval removal happens here.",
        "cli_intro": "To add evidence or cases, run these CLI commands in the same workspace.",
        "cli_evidence": "ai-automation-kit autopilot-proof-lab add-evidence --workspace <workspace> --source <source-file> --role policy --classification internal --provided-by Owner",
        "cli_case": "ai-automation-kit autopilot-proof-lab add-case --workspace <workspace> --case-id <case-id> --input <input> --expected <expected> --proposed <proposed> --risk-tier medium --case-class normal --expected-route standard --proposed-route standard",
        "levels_rows": [
            ("L0", "Not ready. Inputs or completion rules are still unclear."),
            ("L1", "Assist only. Humans decide and the system prepares evidence."),
            ("L2", "Shadow mode. Historical cases are compared locally."),
            ("L3", "Conditional autopilot advice. Even here, no external execution runs."),
            ("L4", "Higher standard-path maturity. Even here, approvals stay in place."),
        ],
    },
}


def render_autopilot_proof_lab_ui(language: str, session_token: str) -> str:
    if language not in LANGUAGES:
        raise ValueError("language must be 'ja' or 'en'")
    text = COPY[language]
    token_json = json.dumps(session_token)
    copy_json = json.dumps(text, ensure_ascii=False)
    levels_rows = "".join(
        "<tr><th>{}</th><td>{}</td></tr>".format(html.escape(level), html.escape(description))
        for level, description in text["levels_rows"]
    )
    return """<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f4f7fb;
      --panel: #ffffff;
      --line: #d6deea;
      --text: #16202d;
      --muted: #5a6675;
      --accent: #1459c7;
      --accent-strong: #0f4cad;
      --warn: #9a5b00;
      --warn-bg: #fff3db;
      --ok-bg: #e8f5eb;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--text);
    }}
    .page {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 24px;
    }}
    .hero {{
      display: grid;
      gap: 12px;
      margin-bottom: 20px;
    }}
    .hero h1 {{
      margin: 0;
      font-size: 2rem;
    }}
    .hero p {{
      margin: 0;
      color: var(--muted);
    }}
    .notice {{
      background: var(--warn-bg);
      border: 1px solid #efcf8e;
      border-radius: 8px;
      padding: 14px 16px;
      font-weight: 600;
    }}
    .grid {{
      display: grid;
      grid-template-columns: minmax(0, 1.3fr) minmax(320px, 0.7fr);
      gap: 20px;
    }}
    .stack {{
      display: grid;
      gap: 20px;
    }}
    section {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
    }}
    h2 {{
      margin: 0 0 12px;
      font-size: 1rem;
    }}
    .next-action {{
      background: #0d3d86;
      color: #ffffff;
    }}
    .next-action strong {{
      display: block;
      font-size: 1.25rem;
      margin-bottom: 6px;
    }}
    .identity-grid, .count-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }}
    .metric {{
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fbfdff;
    }}
    .metric-label {{
      display: block;
      color: var(--muted);
      font-size: 0.88rem;
      margin-bottom: 4px;
    }}
    .metric-value {{
      font-size: 1rem;
      font-weight: 700;
      word-break: break-word;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
    }}
    th, td {{
      text-align: left;
      padding: 10px 8px;
      border-top: 1px solid var(--line);
      vertical-align: top;
    }}
    th {{
      font-size: 0.9rem;
    }}
    .badge {{
      display: inline-block;
      padding: 3px 8px;
      border-radius: 999px;
      background: var(--ok-bg);
      font-size: 0.82rem;
      font-weight: 700;
    }}
    .warn-list {{
      margin: 0;
      padding-left: 18px;
    }}
    .actions {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-top: 12px;
    }}
    button {{
      border: 0;
      border-radius: 8px;
      padding: 10px 14px;
      background: var(--accent);
      color: #fff;
      font: inherit;
      font-weight: 700;
      cursor: pointer;
    }}
    button:hover {{
      background: var(--accent-strong);
    }}
    form {{
      display: grid;
      gap: 10px;
    }}
    label {{
      display: grid;
      gap: 6px;
      font-size: 0.92rem;
      color: var(--muted);
    }}
    input, select, textarea {{
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px 12px;
      font: inherit;
      color: var(--text);
      background: #fff;
    }}
    textarea {{
      min-height: 92px;
      resize: vertical;
    }}
    pre {{
      margin: 8px 0 0;
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #f8fbff;
      white-space: pre-wrap;
      word-break: break-word;
    }}
    .report-list, .report-list li {{
      margin: 0;
      padding: 0;
      list-style: none;
    }}
    .report-list {{
      display: grid;
      gap: 10px;
    }}
    .report-link {{
      display: grid;
      gap: 4px;
      padding: 10px 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      text-decoration: none;
      color: inherit;
      background: #fbfdff;
    }}
    .report-path {{
      color: var(--muted);
      font-size: 0.85rem;
      word-break: break-all;
    }}
    .status-pill {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-size: 0.9rem;
      color: var(--muted);
    }}
    .status-dot {{
      width: 10px;
      height: 10px;
      border-radius: 999px;
      background: #2d8a46;
    }}
    .status-dot.stale {{
      background: #b56a00;
    }}
    @media (max-width: 900px) {{
      .grid {{
        grid-template-columns: 1fr;
      }}
      .identity-grid, .count-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <div class="hero">
      <div>
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </div>
      <div class="notice">{advisory}</div>
    </div>

    <div class="grid">
      <div class="stack">
        <section class="next-action">
          <div>{next_action_label}</div>
          <strong id="next-action">{loading}</strong>
          <div id="decision-line"></div>
          <div class="actions">
            <button id="refresh-button" type="button">{refresh}</button>
            <button id="evaluate-button" type="button">{evaluate}</button>
          </div>
        </section>

        <section>
          <h2>{assessment}</h2>
          <div class="identity-grid" id="identity-grid"></div>
        </section>

        <section>
          <h2>{counts}</h2>
          <div class="count-grid" id="count-grid"></div>
        </section>

        <section>
          <h2>{gates}</h2>
          <table>
            <thead>
              <tr>
                <th>{gate_name}</th>
                <th>{gate_status}</th>
                <th>{gate_owner}</th>
                <th>{gate_note}</th>
              </tr>
            </thead>
            <tbody id="gate-table-body">
              <tr><td colspan="4">{loading}</td></tr>
            </tbody>
          </table>
        </section>

        <section>
          <h2>{levels}</h2>
          <table>{levels_rows}</table>
        </section>
      </div>

      <div class="stack">
        <section>
          <h2>{reports}</h2>
          <ul class="report-list" id="report-list"></ul>
        </section>

        <section>
          <h2>{warnings}</h2>
          <div class="status-pill"><span id="status-dot" class="status-dot"></span><span id="freshness-label">{fresh}</span></div>
          <ul class="warn-list" id="warning-list"></ul>
        </section>

        <section>
          <h2>{gate_form}</h2>
          <form id="gate-form">
            <label>{gate_name}<select name="gate" id="gate-input"></select></label>
            <label>{gate_status}
              <select name="status">
                <option value="unknown">unknown</option>
                <option value="pass">pass</option>
                <option value="fail">fail</option>
              </select>
            </label>
            <label>{gate_owner}<input name="owner" type="text" required></label>
            <label>{gate_evidence}<input name="evidence_ids" type="text"></label>
            <label>{gate_note}<textarea name="note"></textarea></label>
            <button type="submit">{gate_submit}</button>
          </form>
        </section>

        <section>
          <h2>CLI</h2>
          <p>{cli_intro}</p>
          <pre>{cli_evidence}
{cli_case}</pre>
          <p>{no_external} {no_approval}</p>
        </section>
      </div>
    </div>
  </div>

  <script>
    const SESSION_TOKEN = {token_json};
    const COPY = {copy_json};

    function escapeHtml(value) {{
      return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;");
    }}

    async function api(path, options = {{}}) {{
      const headers = Object.assign({{
        "Accept": "application/json",
        "X-Autopilot-Proof-Lab-Token": SESSION_TOKEN,
      }}, options.headers || {{}});
      const response = await fetch(path, Object.assign({{}}, options, {{ headers }}));
      if (response.headers.get("content-type")?.includes("application/json")) {{
        return await response.json();
      }}
      return {{
        ok: false,
        data: {{}},
        next_action: "",
        error: {{ code: "bad_response", message: "Unexpected response type" }},
      }};
    }}

    function metric(label, value) {{
      return `<div class="metric"><span class="metric-label">${{escapeHtml(label)}}</span><span class="metric-value">${{escapeHtml(value)}}</span></div>`;
    }}

    function renderWarnings(status) {{
      const warnings = [];
      for (const item of status.blocking_gates || []) warnings.push(`Blocking gate: ${{item}}`);
      for (const item of status.stale_reasons || []) warnings.push(item);
      const target = document.getElementById("warning-list");
      if (!warnings.length) {{
        target.innerHTML = "<li>None</li>";
      }} else {{
        target.innerHTML = warnings.map((item) => `<li>${{escapeHtml(item)}}</li>`).join("");
      }}
      const stale = Boolean(status.stale);
      document.getElementById("status-dot").classList.toggle("stale", stale);
      document.getElementById("freshness-label").textContent = stale ? COPY.stale : COPY.fresh;
    }}

    function renderGates(assessment) {{
      const gates = assessment.gates || {{}};
      const names = Object.keys(gates);
      document.getElementById("gate-input").innerHTML = names
        .map((name) => `<option value="${{escapeHtml(name)}}">${{escapeHtml(name)}}</option>`)
        .join("");
      const rows = names.map((name) => {{
        const gate = gates[name] || {{}};
        return `<tr>
          <td>${{escapeHtml(name)}}</td>
          <td>${{escapeHtml(gate.status || "unknown")}}</td>
          <td>${{escapeHtml(gate.owner || "")}}</td>
          <td>${{escapeHtml(gate.note || "")}}</td>
        </tr>`;
      }}).join("");
      document.getElementById("gate-table-body").innerHTML = rows || `<tr><td colspan="4">${{escapeHtml(COPY.loading)}}</td></tr>`;
    }}

    function renderReports(paths, links) {{
      const names = Object.keys(paths || {{}});
      const items = names.map((name) => {{
        const link = links[name];
        const path = paths[name];
        return `<li><a class="report-link" href="${{escapeHtml(link)}}" target="_blank" rel="noopener noreferrer">
          <strong>${{escapeHtml(name)}}</strong>
          <span class="report-path">${{escapeHtml(path)}}</span>
        </a></li>`;
      }}).join("");
      document.getElementById("report-list").innerHTML = items;
    }}

    function renderStatus(payload) {{
      const data = payload.data || {{}};
      const assessment = data.assessment || {{}};
      const status = data.status || {{}};
      document.getElementById("next-action").textContent = payload.next_action || COPY.loading;
      document.getElementById("decision-line").textContent =
        `${{COPY.decision}}: ${{status.decision || "not_evaluated"}} (${{
          status.maximum_level || "L0"
        }})`;

      document.getElementById("identity-grid").innerHTML = [
        [COPY.identity_assessment_id, status.assessment_id || assessment.assessment_id || ""],
        [COPY.identity_stage, status.stage || assessment.stage || ""],
        [COPY.identity_maximum_level, status.maximum_level || "L0"],
        [COPY.identity_pack, assessment.pack_id || ""],
        [COPY.identity_org, assessment.organization || ""],
        [COPY.identity_objective, assessment.objective || ""],
        [COPY.identity_requested, assessment.requested_level || ""],
        [COPY.identity_language, assessment.language || ""],
      ].map(([label, value]) => metric(label, value)).join("");

      document.getElementById("count-grid").innerHTML = [
        [COPY.count_evidence, status.evidence_count ?? 0],
        [COPY.count_cases, status.shadow_case_count ?? 0],
        [COPY.count_blocking, (status.blocking_gates || []).length],
      ].map(([label, value]) => metric(label, value)).join("");

      renderGates(assessment);
      renderWarnings(status);
      renderReports(data.report_paths || {{}}, data.report_links || {{}});
    }}

    async function refreshStatus() {{
      const payload = await api("/api/status");
      renderStatus(payload);
    }}

    async function runEvaluate() {{
      const payload = await api("/api/evaluate", {{
        method: "POST",
        headers: {{
          "Content-Type": "application/json",
        }},
        body: JSON.stringify({{}}),
      }});
      renderStatus(payload);
    }}

    async function submitGate(event) {{
      event.preventDefault();
      const form = new FormData(event.currentTarget);
      const evidenceIds = String(form.get("evidence_ids") || "")
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean);
      const payload = await api("/api/gate", {{
        method: "POST",
        headers: {{
          "Content-Type": "application/json",
        }},
        body: JSON.stringify({{
          gate: form.get("gate"),
          status: form.get("status"),
          owner: form.get("owner"),
          evidence_ids: evidenceIds,
          note: form.get("note") || "",
        }}),
      }});
      renderStatus(payload);
    }}

    document.getElementById("refresh-button").addEventListener("click", refreshStatus);
    document.getElementById("evaluate-button").addEventListener("click", runEvaluate);
    document.getElementById("gate-form").addEventListener("submit", submitGate);
    refreshStatus();
  </script>
</body>
</html>
""".format(
        lang=html.escape(language),
        title=html.escape(text["title"]),
        subtitle=html.escape(text["subtitle"]),
        advisory=html.escape(text["advisory"]),
        next_action_label=html.escape(text["next_action_label"]),
        loading=html.escape(text["loading"]),
        refresh=html.escape(text["refresh"]),
        evaluate=html.escape(text["evaluate"]),
        assessment=html.escape(text["assessment"]),
        counts=html.escape(text["counts"]),
        gates=html.escape(text["gates"]),
        levels=html.escape(text["levels"]),
        reports=html.escape(text["reports"]),
        warnings=html.escape(text["warnings"]),
        gate_form=html.escape(text["gate_form"]),
        gate_name=html.escape(text["gate_name"]),
        gate_status=html.escape(text["gate_status"]),
        gate_owner=html.escape(text["gate_owner"]),
        gate_note=html.escape(text["gate_note"]),
        gate_evidence=html.escape(text["gate_evidence"]),
        gate_submit=html.escape(text["gate_submit"]),
        fresh=html.escape(text["fresh"]),
        cli_intro=html.escape(text["cli_intro"]),
        cli_evidence=html.escape(text["cli_evidence"]),
        cli_case=html.escape(text["cli_case"]),
        no_external=html.escape(text["no_external"]),
        no_approval=html.escape(text["no_approval"]),
        levels_rows=levels_rows,
        token_json=token_json,
        copy_json=copy_json,
    )
