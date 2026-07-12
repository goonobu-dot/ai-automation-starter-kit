"""Self-contained HTML for the office workspace operator UI."""

from __future__ import annotations

import json
import re


_SAFE_TOKEN_RE = re.compile(r"^[0-9a-f]{64}$")


_TRANSLATIONS = {
    "ja": {
        "title": "オフィス作業場所",
        "subtitle": "作業場所、ワークフローパック、最初の期間を決めてから、この画面で資料確認、下書き作成、ローカル承認、次の期間の準備まで進めます。",
        "list_view": "作業場所一覧",
        "detail_view": "期間詳細",
        "back_to_list": "一覧へ戻る",
        "list_heading": "作業場所一覧",
        "list_help": "作業場所ごとの現在の期間と次の操作をここから確認します。",
        "detail_heading": "期間詳細",
        "detail_help": "現在の期間の状態を確認して、必要な操作だけを進めます。",
        "workspace_name": "作業場所名",
        "active_month": "進行中の期間",
        "active_style_reference": "再利用する承認済み見本",
        "pack_name": "ワークフローパック",
        "codex_preflight": "Codex事前確認",
        "recent_run": "直近の実行",
        "next_action": "次の操作",
        "unresolved_approvals": "未解決の承認",
        "approval_waiting": "承認待ち",
        "approval_clear": "承認待ちはありません",
        "open_workspace": "詳細を開く",
        "create_workspace": "作業場所と最初の期間を作る",
        "name_label": "作業場所名",
        "pack_label": "ワークフローパック",
        "pack_help": "作りたい仕事の種類を選ぶと、期間の入力形式が自動で切り替わります。",
        "pack_draft_boundary": "下書き作成専用です。人が確認して承認します。",
        "pack_category_label": "分類",
        "pack_risk_label": "確認レベル",
        "category_labels": {
            "reports": "報告書",
            "support": "問い合わせ",
            "sales": "営業",
            "finance": "経理・照合",
            "operations": "業務運営",
            "people": "人事・勤怠",
            "people_ops": "人事・勤怠",
            "projects": "プロジェクト",
            "executive": "経営要約",
            "legal": "契約・法務確認",
            "compliance": "規程・統制",
            "procurement": "調達・取引先",
        },
        "risk_labels": {"low": "通常", "medium": "注意", "high": "重要"},
        "first_period_label": "最初の期間",
        "approver_label": "承認者名",
        "pin_label": "承認用PIN",
        "root_choice_label": "保存先",
        "refresh": "状態を更新",
        "folder_panel": "フォルダ",
        "folder_help": "各ボタンで該当フォルダを開きます。",
        "progress_panel": "進行状況",
        "question_panel": "確認質問",
        "question_help": "今の質問を1つずつ解決します。",
        "answer_label": "回答",
        "save_answer": "回答を保存",
        "action_panel": "実行",
        "inspect": "資料を確認",
        "generate": "下書きを作成",
        "cancel": "実行を止める",
        "cancelling": "停止処理中",
        "draft_panel": "下書き状態",
        "draft_not_ready": "下書きはまだ承認されていません。",
        "open_draft": "下書きフォルダを開く",
        "source_panel": "資料確認結果",
        "accepted_formats": "対応形式",
        "accepted_formats_value": ".txt, .md, .csv, .json, .docx, .xlsx, .pdf",
        "accepted_files": "受付済みファイル",
        "rejected_files": "不採用ファイル",
        "skipped_files": "確認対象外ファイル",
        "missing_inputs": "読み取れる今回資料がありません。資料を追加して再確認してください。",
        "manifest_absent": "資料確認記録はまだありません。先に資料を確認してください。",
        "source_provenance": "資料の由来情報",
        "manifest_generated": "確認日時",
        "manifest_period": "対象期間",
        "manifest_hash": "確認記録ハッシュ",
        "no_files": "該当ファイルはありません。",
        "approval_panel": "承認",
        "approval_help": "この承認はこの端末内のローカル記録です。",
        "approval_name": "承認者名",
        "approval_pin": "承認用PIN",
        "approve": "承認して完成版へ保存",
        "approval_honesty": "承認すると外部送信は行わず、完成版をローカル保存します。",
        "rollover_panel": "次月準備",
        "next_period_label": "次の期間",
        "period_help_label": "入力形式",
        "reuse_style": "直前の承認済み完成版を文体見本として使う",
        "rollover": "次の期間を準備",
        "status_ready": "準備完了",
        "status_idle": "未実行",
        "status_busy": "処理中",
        "status_error": "エラー",
        "status_done": "完了",
        "draft_waiting": "下書きを待っています。",
        "draft_ready_prefix": "確認用の下書き:",
        "approved_local": "ローカル承認済み",
        "not_selected": "まだ作業場所が選ばれていません。",
        "missing_period": "先に最初の期間を用意してください。",
        "no_question": "現在の未回答質問はありません。",
        "no_recent_run": "まだ実行はありません。",
        "no_workspaces": "まだ作業場所がありません。",
        "create_first": "最初の作業場所と期間を作成してください。",
        "preflight_ok": "Codexを使えます",
        "preflight_fix": "Codexの準備が必要です",
        "run_running": "実行中",
        "run_cancelling": "停止処理中",
        "run_cancelled": "停止済み",
        "run_failed": "失敗",
        "run_review": "確認待ち",
        "run_approved": "承認後",
        "count_suffix": "件",
        "period_formats": {
            "month": {
                "placeholder": "2026-07",
                "help": "月次パックでは YYYY-MM 形式で入力します。",
            },
            "day": {
                "placeholder": "2026-07-12",
                "help": "日次パックでは YYYY-MM-DD 形式で入力します。",
            },
        },
        "extraction_statuses": {
            "not_attempted": "確認未実施",
            "extracted": "内容を読み取り済み",
            "metadata_only": "基本情報のみ確認",
            "extraction_error": "内容を読み取れませんでした",
            "extraction_limit": "読み取り上限に達しました",
            "optional_isolation_unavailable": "追加の安全な読み取り機能を利用できません",
            "optional_reader_missing": "追加の読み取り機能がありません",
            "generic": "状態を確認できません",
        },
        "next_actions": {
            "create_period": "最初の期間を準備してください。",
            "place_inputs": "今回資料フォルダへ資料を追加してください。",
            "inspect": "資料を確認してください。",
            "answer": "現在の質問に回答してください。",
            "generate": "下書きを作成できます。",
            "wait_run": "下書き作成の完了を待ってください。",
            "wait_cancel": "停止処理の完了を待ってください。",
            "review": "下書きを確認し、承認者とPINで承認してください。",
            "rollover": "承認済みです。次の期間を準備できます。",
            "retry": "状態を確認してから再実行してください。",
            "refresh": "作業場所を更新して再試行してください。",
        },
        "errors": {
            "generic": "処理を完了できませんでした。状態を更新して再試行してください。",
            "approval_denied": "承認者名またはPINを確認してください。",
            "bad_action_nonce": "操作の有効期限が切れました。状態を更新して再試行してください。",
            "bad_content_length": "送信内容の長さが正しくありません。",
            "bad_content_type": "送信形式が正しくありません。",
            "bad_draft_id": "下書きの指定が正しくありません。",
            "bad_folder_role": "フォルダの指定が正しくありません。",
            "bad_json": "入力内容を確認してください。",
            "bad_pack_id": "利用できるワークフローパックを選んでください。",
            "bad_period_id": "期間は表示中の形式に合わせて入力してください。",
            "bad_question_id": "質問の指定が正しくありません。",
            "bad_root_choice": "利用可能な保存先を選んでください。",
            "bad_run_id": "実行の指定が正しくありません。",
            "bad_style_reference": "文体見本の確認情報が正しくありません。",
            "bad_token": "この画面の認証情報が無効です。画面を開き直してください。",
            "codex_not_logged_in": "Codexへログインしてから再試行してください。",
            "codex_unavailable": "Codexを利用できません。インストール状態を確認してください。",
            "environment_not_ready": "実行環境の準備が完了していません。設定を確認してください。",
            "host_not_allowed": "この接続先からは操作できません。",
            "loopback_only": "この画面はこの端末からのみ利用できます。",
            "method_not_allowed": "この操作方法は利用できません。",
            "missing_token": "この画面の認証情報がありません。画面を開き直してください。",
            "not_found": "対象が見つかりませんでした。",
            "open_folder_failed": "フォルダを開けませんでした。",
            "origin_not_allowed": "この画面の接続元からは操作できません。",
            "period_not_found": "対象期間が見つかりませんでした。",
            "question_not_found": "対象の質問が見つかりませんでした。",
            "request_error": "操作を受け付けられませんでした。入力を確認してください。",
            "request_too_large": "送信内容が大きすぎます。",
            "run_not_found": "対象の実行が見つかりませんでした。",
            "short_body": "送信内容をすべて受信できませんでした。再試行してください。",
            "state_conflict": "現在の状態ではこの操作を実行できません。状態を更新してください。",
            "workspace_not_found": "作業場所が見つかりませんでした。",
        },
        "folder_roles": {
            "start_here": "[DIR] 00 はじめに",
            "approved_past_outputs": "[DIR] 01 承認済み過去完成版",
            "past_supporting_files": "[DIR] 02 過去補足資料",
            "current_inputs": "[DIR] 03 今回資料",
            "questions": "[DIR] 04 質問",
            "drafts": "[DIR] 05 下書き",
            "approved_outputs": "[DIR] 06 承認済み完成版",
            "audit": "[DIR] 07 監査",
        },
        "steps": {
            "created": "1. 期間を用意",
            "inputs_ready": "2. 資料配置",
            "reviewed": "3. 資料確認",
            "questioning": "4. 質問回答",
            "ready_for_run": "5. 下書き準備",
            "ready_for_review": "6. 下書き確認",
            "approved": "7. ローカル承認",
            "cancelled": "5. 再実行前の停止",
            "failed": "5. 再確認が必要",
        },
        "step_labels": [
            "1. 期間を用意",
            "2. 資料配置",
            "3. 資料確認",
            "4. 質問回答",
            "5. 下書き準備",
            "6. 下書き確認",
            "7. ローカル承認",
        ],
    },
    "en": {
        "title": "Office workspace",
        "subtitle": "Choose a workspace, a workflow pack, and the first period, then inspect materials, generate a draft, record local approval, and prepare the next period from one screen.",
        "list_view": "Workspace list",
        "detail_view": "Period detail",
        "back_to_list": "Back to list",
        "list_heading": "Workspace list",
        "list_help": "Review the current period and next action for each workspace.",
        "detail_heading": "Period detail",
        "detail_help": "Check the current period, then run only the next required action.",
        "workspace_name": "Workspace name",
        "active_month": "Active period",
        "active_style_reference": "Approved example in use",
        "pack_name": "Workflow pack",
        "codex_preflight": "Codex preflight",
        "recent_run": "Recent run",
        "next_action": "Next action",
        "unresolved_approvals": "Unresolved approvals",
        "approval_waiting": "Waiting for approval",
        "approval_clear": "No approvals are waiting",
        "open_workspace": "Open detail",
        "create_workspace": "Create workspace and first period",
        "name_label": "Workspace name",
        "pack_label": "Workflow pack",
        "pack_help": "Choose the kind of work first. The period format updates automatically.",
        "pack_draft_boundary": "Draft preparation only; a person must review and approve.",
        "pack_category_label": "Category",
        "pack_risk_label": "Review level",
        "category_labels": {
            "reports": "Reports",
            "support": "Support",
            "sales": "Sales",
            "finance": "Finance and reconciliation",
            "operations": "Operations",
            "people": "People and attendance",
            "people_ops": "People operations",
            "projects": "Projects",
            "executive": "Executive review",
            "legal": "Contract and legal review",
            "compliance": "Policy and controls",
            "procurement": "Procurement and vendors",
        },
        "risk_labels": {"low": "Standard", "medium": "Caution", "high": "High attention"},
        "first_period_label": "First period",
        "approver_label": "Approver name",
        "pin_label": "Approval PIN",
        "root_choice_label": "Save location",
        "refresh": "Refresh state",
        "folder_panel": "Folders",
        "folder_help": "Open the matching folder with each button.",
        "progress_panel": "Progress",
        "question_panel": "Current question",
        "question_help": "Resolve one current question at a time.",
        "answer_label": "Answer",
        "save_answer": "Save answer",
        "action_panel": "Actions",
        "inspect": "Inspect materials",
        "generate": "Generate draft",
        "cancel": "Cancel run",
        "cancelling": "Cancelling",
        "draft_panel": "Draft state",
        "draft_not_ready": "The draft is not approved yet.",
        "open_draft": "Open draft folder",
        "source_panel": "Material inspection",
        "accepted_formats": "Accepted formats",
        "accepted_formats_value": ".txt, .md, .csv, .json, .docx, .xlsx, .pdf",
        "accepted_files": "Accepted files",
        "rejected_files": "Rejected files",
        "skipped_files": "Skipped files",
        "missing_inputs": "No readable current-period input is available. Add material and inspect again.",
        "manifest_absent": "No source manifest is available yet. Inspect materials first.",
        "source_provenance": "Source provenance",
        "manifest_generated": "Inspected at",
        "manifest_period": "Period",
        "manifest_hash": "Manifest hash",
        "no_files": "No matching files.",
        "approval_panel": "Approval",
        "approval_help": "This approval is a local record on this device.",
        "approval_name": "Approver name",
        "approval_pin": "Approval PIN",
        "approve": "Approve and save local final copy",
        "approval_honesty": "Approval saves a local approved copy and does not send anything externally.",
        "rollover_panel": "Next period",
        "next_period_label": "Next period",
        "period_help_label": "Format",
        "reuse_style": "Use the latest approved final copy as a style reference",
        "rollover": "Prepare next period",
        "status_ready": "Ready",
        "status_idle": "Idle",
        "status_busy": "Busy",
        "status_error": "Error",
        "status_done": "Done",
        "draft_waiting": "Waiting for a draft.",
        "draft_ready_prefix": "Draft ready for review:",
        "approved_local": "Approved locally",
        "not_selected": "No workspace is selected yet.",
        "missing_period": "Prepare the first period before this action.",
        "no_question": "There is no unanswered question right now.",
        "no_recent_run": "No run yet.",
        "no_workspaces": "No workspace exists yet.",
        "create_first": "Create your first workspace and period.",
        "preflight_ok": "Codex is ready",
        "preflight_fix": "Codex needs attention",
        "run_running": "Running",
        "run_cancelling": "Cancelling",
        "run_cancelled": "Cancelled",
        "run_failed": "Failed",
        "run_review": "Waiting for review",
        "run_approved": "After approval",
        "count_suffix": "files",
        "period_formats": {
            "month": {
                "placeholder": "2026-07",
                "help": "Monthly packs use YYYY-MM.",
            },
            "day": {
                "placeholder": "2026-07-12",
                "help": "Daily packs use YYYY-MM-DD.",
            },
        },
        "extraction_statuses": {
            "not_attempted": "Not inspected",
            "extracted": "Extracted",
            "metadata_only": "Basic information only",
            "extraction_error": "Content could not be read",
            "extraction_limit": "Reading limit reached",
            "optional_isolation_unavailable": "Optional safe reader unavailable",
            "optional_reader_missing": "Optional reader not installed",
            "generic": "Status unavailable",
        },
        "next_actions": {
            "create_period": "Prepare the first reporting period.",
            "place_inputs": "Add files to the current inputs folder.",
            "inspect": "Inspect the source materials.",
            "answer": "Answer the current question.",
            "generate": "The draft is ready to generate.",
            "wait_run": "Wait for draft generation to finish.",
            "wait_cancel": "Wait for cancellation to finish.",
            "review": "Review the draft, then approve with the approver name and PIN.",
            "rollover": "Approval is complete. You can prepare the next period.",
            "retry": "Review the state, then run the action again.",
            "refresh": "Refresh the workspace and retry.",
        },
        "errors": {
            "generic": "The operation could not be completed. Refresh the workspace and retry.",
            "approval_denied": "Check the approver name and PIN.",
            "bad_action_nonce": "This action expired. Refresh the workspace and retry.",
            "bad_content_length": "The submitted content length is invalid.",
            "bad_content_type": "The submitted content format is invalid.",
            "bad_draft_id": "The selected draft is invalid.",
            "bad_folder_role": "The selected folder role is invalid.",
            "bad_json": "Review the entered values.",
            "bad_pack_id": "Choose an available workflow pack.",
            "bad_period_id": "Enter the period using the format shown on screen.",
            "bad_question_id": "The selected question is invalid.",
            "bad_root_choice": "Choose an available save location.",
            "bad_run_id": "The selected run is invalid.",
            "bad_style_reference": "The style-reference confirmation is invalid.",
            "bad_token": "This screen's authorization is invalid. Reopen the screen.",
            "codex_not_logged_in": "Sign in to Codex, then retry.",
            "codex_unavailable": "Codex is unavailable. Check the installation.",
            "environment_not_ready": "The runtime environment is not ready. Review its configuration.",
            "host_not_allowed": "Operations are not allowed from this host.",
            "loopback_only": "This screen can only be used on this device.",
            "method_not_allowed": "That operation method is unavailable.",
            "missing_token": "This screen has no authorization. Reopen the screen.",
            "not_found": "The requested item was not found.",
            "open_folder_failed": "The folder could not be opened.",
            "origin_not_allowed": "Operations are not allowed from this screen origin.",
            "period_not_found": "The reporting period was not found.",
            "question_not_found": "The question was not found.",
            "request_error": "The operation was rejected. Review the entered values.",
            "request_too_large": "The submitted content is too large.",
            "run_not_found": "The run was not found.",
            "short_body": "The full request was not received. Retry the operation.",
            "state_conflict": "This operation is unavailable in the current state. Refresh the workspace.",
            "workspace_not_found": "The workspace was not found.",
        },
        "folder_roles": {
            "start_here": "[DIR] 00 Start Here",
            "approved_past_outputs": "[DIR] 01 Approved Past Outputs",
            "past_supporting_files": "[DIR] 02 Past Supporting Files",
            "current_inputs": "[DIR] 03 Current Inputs",
            "questions": "[DIR] 04 Questions",
            "drafts": "[DIR] 05 Drafts",
            "approved_outputs": "[DIR] 06 Approved Outputs",
            "audit": "[DIR] 07 Audit",
        },
        "steps": {
            "created": "1. Prepare period",
            "inputs_ready": "2. Place inputs",
            "reviewed": "3. Inspect materials",
            "questioning": "4. Answer questions",
            "ready_for_run": "5. Ready to draft",
            "ready_for_review": "6. Review draft",
            "approved": "7. Local approval",
            "cancelled": "5. Cancelled before retry",
            "failed": "5. Needs recheck",
        },
        "step_labels": [
            "1. Prepare period",
            "2. Place inputs",
            "3. Inspect materials",
            "4. Answer questions",
            "5. Ready to draft",
            "6. Review draft",
            "7. Local approval",
        ],
    },
}


def render_office_workspace_ui(language: str, token: str) -> str:
    if language not in _TRANSLATIONS:
        raise ValueError("language must be 'ja' or 'en'")
    if not isinstance(token, str) or not _SAFE_TOKEN_RE.fullmatch(token):
        raise ValueError("token must be a 64-character lowercase hex string")
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
      --bg: #f3f5f7;
      --panel: #ffffff;
      --line: #c9d1d9;
      --text: #16202a;
      --muted: #576675;
      --accent: #1f5fa8;
      --accent-soft: #e6effa;
      --ok: #2b6f48;
      --ok-soft: #e6f4ea;
      --warn: #946200;
      --warn-soft: #fff4d8;
      --danger: #a53232;
      --danger-soft: #fce8e8;
      --radius: 8px;
      --shadow: 0 1px 2px rgba(15, 23, 42, 0.06);
    }}
    * {{
      box-sizing: border-box;
    }}
    body {{
      margin: 0;
      max-width: 100%;
      overflow-x: hidden;
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.5;
    }}
    main {{
      width: min(100%, 1440px);
      margin: 0 auto;
      padding: 20px;
      display: grid;
      gap: 16px;
    }}
    h1, h2, h3, p {{
      margin: 0;
    }}
    button, input, select, textarea {{
      font: inherit;
      color: inherit;
      max-width: 100%;
    }}
    section {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
    }}
    .hero {{
      padding: 20px;
      display: grid;
      gap: 8px;
    }}
    .toolbar {{
      padding: 0 20px 20px 20px;
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
    }}
    .view-toggle {{
      display: inline-grid;
      grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
      border: 1px solid var(--line);
      border-radius: 6px;
      overflow: hidden;
    }}
    .view-toggle button {{
      min-height: 40px;
      border: 0;
      border-right: 1px solid var(--line);
      background: #f8fafc;
      padding: 0 12px;
    }}
    .view-toggle button:last-child {{
      border-right: 0;
    }}
    .view-toggle button[aria-selected="true"] {{
      background: var(--accent-soft);
      color: var(--accent);
      font-weight: 600;
    }}
    .secondary-button,
    .primary-button,
    .danger-button,
    .success-button {{
      min-height: 40px;
      border-radius: 6px;
      border: 1px solid var(--line);
      background: #ffffff;
      padding: 0 14px;
      cursor: pointer;
    }}
    .primary-button {{
      background: var(--accent);
      border-color: var(--accent);
      color: #ffffff;
    }}
    .danger-button {{
      background: var(--danger);
      border-color: var(--danger);
      color: #ffffff;
    }}
    .success-button {{
      background: var(--ok);
      border-color: var(--ok);
      color: #ffffff;
    }}
    button:disabled {{
      cursor: not-allowed;
      opacity: 0.6;
    }}
    input[type="text"],
    input[type="password"],
    select,
    textarea {{
      width: 100%;
      min-height: 40px;
      border-radius: 6px;
      border: 1px solid var(--line);
      background: #ffffff;
      padding: 8px 10px;
    }}
    textarea {{
      min-height: 112px;
      resize: vertical;
    }}
    label {{
      display: block;
      font-size: 14px;
      color: var(--muted);
      margin-bottom: 6px;
    }}
    .view {{
      padding: 20px;
      display: grid;
      gap: 16px;
    }}
    .view[hidden] {{
      display: none;
    }}
    .panel-grid {{
      display: grid;
      gap: 16px;
      grid-template-columns: minmax(0, 1.15fr) minmax(0, 0.85fr);
    }}
    .stack {{
      display: grid;
      gap: 16px;
    }}
    .panel {{
      padding: 16px;
      display: grid;
      gap: 12px;
      align-content: start;
    }}
    .panel-header {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
      justify-content: space-between;
    }}
    .muted {{
      color: var(--muted);
    }}
    .message {{
      min-height: 42px;
      border-radius: 6px;
      border: 1px solid var(--line);
      background: #fbfcfd;
      padding: 10px 12px;
      overflow-wrap: anywhere;
    }}
    .message.success {{
      background: var(--ok-soft);
      color: var(--ok);
      border-color: #bcd9c8;
    }}
    .message.warning {{
      background: var(--warn-soft);
      color: var(--warn);
      border-color: #efd994;
    }}
    .message.error {{
      background: var(--danger-soft);
      color: var(--danger);
      border-color: #e8bcbc;
    }}
    .status-pill {{
      display: inline-flex;
      align-items: center;
      min-height: 32px;
      border-radius: 999px;
      border: 1px solid var(--line);
      padding: 0 10px;
      background: #f8fafc;
      color: var(--muted);
      overflow-wrap: anywhere;
    }}
    .form-grid {{
      display: grid;
      gap: 12px;
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }}
    .form-grid.form-grid-compact {{
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }}
    .button-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .workspace-table {{
      display: grid;
      gap: 0;
      border: 1px solid var(--line);
      border-radius: 6px;
      overflow: hidden;
    }}
    .workspace-row {{
      display: grid;
      gap: 8px 12px;
      grid-template-columns: minmax(0, 1.3fr) repeat(5, minmax(0, 1fr)) auto;
      align-items: center;
      padding: 12px;
      border-bottom: 1px solid var(--line);
      background: #ffffff;
    }}
    .workspace-row:last-child {{
      border-bottom: 0;
    }}
    .workspace-row.workspace-head {{
      background: #f8fafc;
      font-size: 14px;
      color: var(--muted);
      font-weight: 600;
    }}
    .workspace-cell {{
      min-width: 0;
      overflow-wrap: anywhere;
    }}
    .folder-grid {{
      display: grid;
      gap: 8px;
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }}
    .folder-button {{
      width: 100%;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 8px;
      text-align: left;
    }}
    .count-badge {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 44px;
      min-height: 28px;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: #f8fafc;
      color: var(--muted);
      padding: 0 8px;
      flex: 0 0 auto;
    }}
    .progress-list {{
      list-style: none;
      margin: 0;
      padding: 0;
      display: grid;
      gap: 8px;
      grid-template-columns: repeat(7, minmax(0, 1fr));
    }}
    .progress-list li {{
      min-height: 74px;
      border-radius: 6px;
      border: 1px solid var(--line);
      background: #fbfcfd;
      padding: 10px;
      display: grid;
      gap: 6px;
      align-content: start;
      overflow-wrap: anywhere;
    }}
    .progress-list li[data-complete="true"] {{
      background: var(--ok-soft);
      border-color: #bcd9c8;
    }}
    .meta-list {{
      list-style: none;
      margin: 0;
      padding: 0;
      display: grid;
      gap: 8px;
    }}
    .meta-list li {{
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px;
      background: #fbfcfd;
      overflow-wrap: anywhere;
    }}
    .file-columns {{
      display: grid;
      gap: 12px;
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }}
    .file-group {{
      min-width: 0;
      display: grid;
      gap: 8px;
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
    :focus-visible {{
      outline: 3px solid rgba(31, 95, 168, 0.28);
      outline-offset: 2px;
    }}
    @media (max-width: 900px) {{
      main {{
        padding: 14px;
      }}
      .panel-grid,
      .form-grid,
      .form-grid.form-grid-compact,
      .folder-grid,
      .workspace-row,
      .progress-list {{
        grid-template-columns: minmax(0, 1fr);
      }}
      .file-columns {{
        grid-template-columns: minmax(0, 1fr);
      }}
      .workspace-row.workspace-head {{
        display: none;
      }}
    }}
    @media (max-width: 540px) {{
      .hero,
      .view {{
        padding: 16px;
      }}
      .toolbar {{
        padding: 0 16px 16px 16px;
      }}
      .view-toggle {{
        width: 100%;
      }}
      .view-toggle button {{
        min-width: 0;
      }}
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
      <p class="muted">{subtitle}</p>
      <div class="toolbar">
        <div class="view-toggle" role="tablist" aria-label="{title}">
          <button id="show-list-button" type="button" role="tab" aria-controls="workspace-list-view" aria-selected="true" tabindex="0">{list_view}</button>
          <button id="show-detail-button" type="button" role="tab" aria-controls="workspace-detail-view" aria-selected="false" tabindex="-1">{detail_view}</button>
        </div>
        <button id="refresh-button" class="secondary-button" type="button">{refresh}</button>
        <button id="back-to-list-button" class="secondary-button" type="button">{back_to_list}</button>
      </div>
    </section>

    <section id="workspace-list-view" class="view" role="tabpanel" aria-labelledby="show-list-button">
      <div class="panel">
        <div class="panel-header">
          <div>
            <h2 id="workspace-list-title">{list_heading}</h2>
            <p class="muted">{list_help}</p>
          </div>
          <span id="list-preflight-pill" class="status-pill">{status_idle}</span>
        </div>
        <div id="workspace-list-message" class="message" role="status" aria-live="polite"></div>
        <div class="workspace-table" aria-label="{list_heading}">
          <div class="workspace-row workspace-head">
            <div class="workspace-cell">{workspace_name}</div>
            <div class="workspace-cell">{active_month}</div>
            <div class="workspace-cell">{codex_preflight}</div>
            <div class="workspace-cell">{recent_run}</div>
            <div class="workspace-cell">{next_action}</div>
            <div class="workspace-cell">{unresolved_approvals}</div>
            <div class="workspace-cell">{open_workspace}</div>
          </div>
          <div id="workspace-list-rows"></div>
        </div>
      </div>

      <div class="panel">
        <div class="panel-header">
          <h2>{create_workspace}</h2>
        </div>
        <div class="form-grid form-grid-compact">
          <div>
            <label for="workspace-name-input">{name_label}</label>
            <input id="workspace-name-input" type="text" autocomplete="organization">
          </div>
          <div>
            <label for="workflow-pack-select">{pack_label}</label>
            <select id="workflow-pack-select"></select>
            <p id="workflow-pack-help" class="muted">{pack_help}</p>
          </div>
          <div>
            <label for="first-period-input">{first_period_label}</label>
            <input id="first-period-input" type="text" inputmode="numeric" autocomplete="off">
            <p id="first-period-help" class="muted"></p>
          </div>
          <div>
            <label for="approver-input">{approver_label}</label>
            <input id="approver-input" type="text" autocomplete="name">
          </div>
          <div>
            <label for="pin-input">{pin_label}</label>
            <input id="pin-input" type="password" inputmode="numeric" autocomplete="off">
          </div>
          <div style="grid-column: 1 / -1;">
            <p class="muted">{pack_help}</p>
          </div>
          <div style="grid-column: 1 / -1;">
            <label for="root-choice-select">{root_choice_label}</label>
            <select id="root-choice-select"></select>
          </div>
        </div>
        <div class="button-row">
          <button id="create-workspace-button" class="primary-button" type="button">{create_workspace}</button>
        </div>
      </div>
    </section>

    <section id="workspace-detail-view" class="view" role="tabpanel" aria-labelledby="show-detail-button" hidden>
      <div class="panel">
        <div class="panel-header">
          <div>
            <h2 id="workspace-detail-title">{detail_heading}</h2>
            <p class="muted">{detail_help}</p>
          </div>
          <span id="detail-stage-pill" class="status-pill">{status_idle}</span>
        </div>
        <div id="workspace-detail-message" class="message" role="alert" aria-live="assertive"></div>
        <ul id="workspace-meta-list" class="meta-list"></ul>
      </div>

      <div class="panel-grid">
        <div class="stack">
          <div class="panel">
            <div class="panel-header">
              <div>
                <h3>{folder_panel}</h3>
                <p class="muted">{folder_help}</p>
              </div>
            </div>
            <div id="folder-grid" class="folder-grid"></div>
          </div>

          <div class="panel">
            <div class="panel-header">
              <h3>{progress_panel}</h3>
            </div>
            <ol id="progress-steps" class="progress-list"></ol>
          </div>

          <div class="panel">
            <div class="panel-header">
              <h3>{source_panel}</h3>
            </div>
            <p id="accepted-formats" class="muted">{accepted_formats}: {accepted_formats_value}</p>
            <div id="manifest-absent" class="message warning"></div>
            <div id="missing-input-warning" class="message warning" hidden></div>
            <ul id="source-provenance" class="meta-list"></ul>
            <div class="file-columns">
              <div class="file-group"><h3>{accepted_files}</h3><ul id="accepted-files" class="meta-list"></ul></div>
              <div class="file-group"><h3>{rejected_files}</h3><ul id="rejected-files" class="meta-list"></ul></div>
              <div class="file-group"><h3>{skipped_files}</h3><ul id="skipped-files" class="meta-list"></ul></div>
            </div>
          </div>

          <div class="panel">
            <div class="panel-header">
              <h3>{question_panel}</h3>
            </div>
            <p class="muted">{question_help}</p>
            <div id="question-text" class="message"></div>
            <div>
              <label for="answer-input">{answer_label}</label>
              <textarea id="answer-input"></textarea>
            </div>
            <div class="button-row">
              <button id="save-answer-button" class="primary-button" type="button">{save_answer}</button>
            </div>
          </div>
        </div>

        <div class="stack">
          <div class="panel">
            <div class="panel-header">
              <h3>{action_panel}</h3>
            </div>
            <div class="button-row">
              <button id="inspect-button" class="primary-button" type="button">{inspect}</button>
              <button id="generate-button" class="primary-button" type="button">{generate}</button>
              <button id="cancel-button" class="danger-button" type="button">{cancel}</button>
            </div>
          </div>

          <div class="panel">
            <div class="panel-header">
              <h3>{draft_panel}</h3>
            </div>
            <div id="draft-message" class="message">{draft_not_ready}</div>
            <div class="button-row">
              <button id="open-draft-button" class="secondary-button" type="button">{open_draft}</button>
            </div>
          </div>

          <div class="panel">
            <div class="panel-header">
              <h3>{approval_panel}</h3>
            </div>
            <p class="muted">{approval_help}</p>
            <div class="form-grid">
              <div>
                <label for="approve-name-input">{approval_name}</label>
                <input id="approve-name-input" type="text" autocomplete="name">
              </div>
              <div>
                <label for="approve-pin-input">{approval_pin}</label>
                <input id="approve-pin-input" type="password" inputmode="numeric" autocomplete="off">
              </div>
            </div>
            <div id="approval-honesty" class="message">{approval_honesty}</div>
            <div class="button-row">
              <button id="approve-button" class="success-button" type="button">{approve}</button>
            </div>
          </div>

          <div class="panel">
            <div class="panel-header">
              <h3>{rollover_panel}</h3>
            </div>
            <div>
              <label for="next-period-input">{next_period_label}</label>
              <input id="next-period-input" type="text" inputmode="numeric" autocomplete="off">
              <p id="next-period-help" class="muted"></p>
            </div>
            <div>
              <label for="reuse-style-checkbox">{reuse_style}</label>
              <input id="reuse-style-checkbox" type="checkbox" checked>
            </div>
            <div class="button-row">
              <button id="rollover-button" class="secondary-button" type="button">{rollover}</button>
            </div>
          </div>
        </div>
      </div>
    </section>
  </main>

  <script>
    (function () {{
      const STRINGS = {strings};
      const PAGE_LANG = {page_lang_json};
      const SESSION_TOKEN = {token};
      const state = {{
        workspaces: [],
        packCatalog: [],
        rootChoices: [],
        preflight: null,
        selectedWorkspaceId: "",
        selectedWorkspace: null,
        actionNonce: "",
      }};

      const FOLDER_ROLES = [
        "start_here",
        "approved_past_outputs",
        "past_supporting_files",
        "current_inputs",
        "questions",
        "drafts",
        "approved_outputs",
        "audit",
      ];
      const INSPECTABLE_STAGES = ["created", "questioning", "ready_for_run", "failed", "cancelled"];

      const ROUTES = {{
        workspaces: function () {{
          return "/api/workspaces";
        }},
        workspace: function (workspaceId) {{
          return "/api/workspaces/" + encodeURIComponent(workspaceId);
        }},
        inspect: function (workspaceId) {{
          return ROUTES.workspace(workspaceId) + "/inspect";
        }},
        answer: function (workspaceId) {{
          return ROUTES.workspace(workspaceId) + "/answer";
        }},
        generate: function (workspaceId) {{
          return ROUTES.workspace(workspaceId) + "/generate";
        }},
        cancel: function (workspaceId) {{
          return ROUTES.workspace(workspaceId) + "/cancel";
        }},
        approve: function (workspaceId) {{
          return ROUTES.workspace(workspaceId) + "/approve";
        }},
        rollover: function (workspaceId) {{
          return ROUTES.workspace(workspaceId) + "/rollover";
        }},
        openFolder: function (workspaceId) {{
          return ROUTES.workspace(workspaceId) + "/open-folder";
        }},
      }};

      function byId(id) {{
        return document.getElementById(id);
      }}

      function text(value) {{
        return typeof value === "string" ? value : "";
      }}

      function setSelectedTab(activeView) {{
        const listButton = byId("show-list-button");
        const detailButton = byId("show-detail-button");
        const listSelected = activeView === "list";
        listButton.setAttribute("aria-selected", listSelected ? "true" : "false");
        detailButton.setAttribute("aria-selected", listSelected ? "false" : "true");
        listButton.tabIndex = listSelected ? 0 : -1;
        detailButton.tabIndex = listSelected ? -1 : 0;
      }}

      function showView(viewName) {{
        const listView = byId("workspace-list-view");
        const detailView = byId("workspace-detail-view");
        listView.hidden = viewName !== "list";
        detailView.hidden = viewName !== "detail";
        setSelectedTab(viewName);
      }}

      function setMessage(id, message, tone) {{
        const node = byId(id);
        node.className = "message" + (tone ? " " + tone : "");
        node.textContent = text(message);
      }}

      function setBusy(button, busy) {{
        if (!button.dataset.baseLabel) {{
          button.dataset.baseLabel = button.textContent;
        }}
        button.disabled = !!busy;
        button.setAttribute("aria-busy", busy ? "true" : "false");
        button.textContent = busy ? STRINGS.status_busy : button.dataset.baseLabel;
      }}

      function clearChildren(id) {{
        byId(id).replaceChildren();
      }}

      function appendTextRow(parent, parts) {{
        const item = document.createElement("li");
        item.textContent = parts.join(" ");
        parent.appendChild(item);
      }}

      function appendMetaItem(parent, label, value) {{
        const item = document.createElement("li");
        item.textContent = label + ": " + text(value);
        parent.appendChild(item);
      }}

      function validateRelativeApiPath(path) {{
        if (typeof path !== "string" || path.indexOf("/api/") !== 0 || path.indexOf("://") !== -1 || path.indexOf("//") === 0) {{
          throw new Error("invalid api path");
        }}
        return path;
      }}

      function updateNonceFromPayload(payload) {{
        if (payload && payload.data && typeof payload.data.action_nonce === "string") {{
          state.actionNonce = payload.data.action_nonce;
        }}
      }}

      async function apiFetch(path, options) {{
        path = validateRelativeApiPath(path);
        const request = Object.assign({{
          method: "GET",
          credentials: "same-origin",
          cache: "no-store",
        }}, options || {{}});
        const headers = new Headers(request.headers || {{}});
        headers.set("X-Office-Workspace-Token", SESSION_TOKEN);
        headers.set("Accept", "application/json");
        request.headers = headers;
        const response = await fetch(path, request);
        const payload = await response.json();
        updateNonceFromPayload(payload);
        if (!response.ok || !payload.ok) {{
          const error = new Error(STRINGS.errors.generic);
          error.payload = payload;
          throw error;
        }}
        return payload;
      }}

      async function postJson(path, data) {{
        const payload = Object.assign({{}}, data || {{}}, {{ action_nonce: state.actionNonce }});
        return apiFetch(path, {{
          method: "POST",
          headers: {{ "Content-Type": "application/json" }},
          body: JSON.stringify(payload),
        }});
      }}

      function formatPreflight(preflight) {{
        if (preflight && preflight.ok) {{
          return STRINGS.preflight_ok;
        }}
        return STRINGS.preflight_fix;
      }}

      function formatRun(run) {{
        if (!run) {{
          return STRINGS.no_recent_run;
        }}
        const status = text(run.status);
        if (status === "running") {{
          return STRINGS.run_running;
        }}
        if (status === "cancelling") {{
          return STRINGS.run_cancelling;
        }}
        if (status === "cancelled") {{
          return STRINGS.run_cancelled;
        }}
        if (status === "failed") {{
          return STRINGS.run_failed;
        }}
        if (status === "ready_for_review") {{
          return STRINGS.run_review;
        }}
        if (status === "approved") {{
          return STRINGS.run_approved;
        }}
        return STRINGS.no_recent_run;
      }}

      function workspaceStage(workspace) {{
        if (workspace && workspace.period && typeof workspace.period.stage === "string") {{
          return workspace.period.stage;
        }}
        return workspace && typeof workspace.period_stage === "string" ? workspace.period_stage : "";
      }}

      function formatNextAction(workspace, preflight) {{
        if (preflight && preflight.ok === false) {{
          return STRINGS.preflight_fix;
        }}
        if (!workspace || !workspace.current_period) {{
          return STRINGS.next_actions.create_period;
        }}
        const runStatus = workspace.run ? text(workspace.run.status) : "";
        if (runStatus === "running") {{
          return STRINGS.next_actions.wait_run;
        }}
        if (runStatus === "cancelling") {{
          return STRINGS.next_actions.wait_cancel;
        }}
        const actions = {{
          created: STRINGS.next_actions.place_inputs,
          inputs_ready: STRINGS.next_actions.inspect,
          reviewed: STRINGS.next_actions.answer,
          questioning: STRINGS.next_actions.answer,
          ready_for_run: STRINGS.next_actions.generate,
          ready_for_review: STRINGS.next_actions.review,
          approved: STRINGS.next_actions.rollover,
          cancelled: STRINGS.next_actions.retry,
          failed: STRINGS.next_actions.retry,
        }};
        return actions[workspaceStage(workspace)] || STRINGS.next_actions.refresh;
      }}

      function formatApiError(error) {{
        const payload = error && error.payload ? error.payload : null;
        const code = payload && payload.error ? text(payload.error.code) : "";
        return STRINGS.errors[code] || STRINGS.errors.generic;
      }}

      function unresolvedApprovalCount(workspaces) {{
        return workspaces.reduce(function (count, workspace) {{
          return count + (workspace && workspace.period_stage === "ready_for_review" ? 1 : 0);
        }}, 0);
      }}

      function currentQuestion(workspace) {{
        if (!workspace || !workspace.period) {{
          return null;
        }}
        const pending = Array.isArray(workspace.period.pending_question_ids) ? workspace.period.pending_question_ids : [];
        const questions = Array.isArray(workspace.period.questions) ? workspace.period.questions : [];
        if (!pending.length) {{
          return null;
        }}
        return questions.find(function (item) {{
          return item && item.id === pending[0];
        }}) || null;
      }}

      function localizedDisplayName(entry) {{
        if (!entry || typeof entry !== "object") {{
          return "";
        }}
        const displayName = entry.display_name;
        if (displayName && typeof displayName === "object") {{
          return text(displayName[PAGE_LANG] || displayName.en || displayName.ja || "");
        }}
        return "";
      }}

      function localizedCategory(entry) {{
        const category = entry && typeof entry === "object" ? text(entry.category) : "";
        const labels = STRINGS.category_labels || {{}};
        return text(labels[category] || category || STRINGS.pack_category_label);
      }}

      function localizedRisk(entry) {{
        const risk = entry && typeof entry === "object" ? text(entry.risk_tier) : "";
        const labels = STRINGS.risk_labels || {{}};
        return text(labels[risk] || risk || "-");
      }}

      function periodFormat(periodType) {{
        const formats = STRINGS.period_formats || {{}};
        return formats[periodType] || formats.month || {{ placeholder: "", help: "" }};
      }}

      function suggestedNextPeriod(currentPeriod, periodType) {{
        const value = text(currentPeriod);
        if (periodType === "day" && /^[0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}}$/.test(value)) {{
          const parts = value.split("-").map(Number);
          return new Date(Date.UTC(parts[0], parts[1] - 1, parts[2] + 1)).toISOString().slice(0, 10);
        }}
        if (periodType === "month" && /^[0-9]{{4}}-[0-9]{{2}}$/.test(value)) {{
          const parts = value.split("-").map(Number);
          return new Date(Date.UTC(parts[0], parts[1], 1)).toISOString().slice(0, 7);
        }}
        return "";
      }}

      function applyPeriodFormat(inputId, helpId, periodType) {{
        const format = periodFormat(periodType);
        byId(inputId).placeholder = text(format.placeholder);
        byId(helpId).textContent = STRINGS.period_help_label + ": " + text(format.help);
      }}

      function currentCreatePackId() {{
        return byId("workflow-pack-select").value;
      }}

      function selectedCreatePack() {{
        const packId = currentCreatePackId();
        return (state.packCatalog || []).find(function (pack) {{
          return pack && pack.id === packId;
        }}) || null;
      }}

      function latestApprovedOutput(workspace) {{
        if (!workspace || !workspace.period || !Array.isArray(workspace.period.approved_outputs)) {{
          return null;
        }}
        if (!workspace.period.approved_outputs.length) {{
          return null;
        }}
        return workspace.period.approved_outputs[workspace.period.approved_outputs.length - 1];
      }}

      function renderRootChoices() {{
        const select = byId("root-choice-select");
        select.replaceChildren();
        (state.rootChoices || []).forEach(function (choice) {{
          const option = document.createElement("option");
          option.value = text(choice.id);
          option.textContent = text(choice.path || choice.id);
          select.appendChild(option);
        }});
      }}

      function updatePackChoiceHelp(pack) {{
        const outcome = pack && PAGE_LANG === "en" ? text(pack.business_outcome) : "";
        byId("workflow-pack-help").textContent = pack
          ? STRINGS.pack_category_label + ": " + localizedCategory(pack) + " / " +
            STRINGS.pack_risk_label + ": " + localizedRisk(pack) + ". " +
            (outcome ? outcome + ". " : "") + STRINGS.pack_draft_boundary
          : STRINGS.pack_help;
      }}

      function renderPackChoices() {{
        const select = byId("workflow-pack-select");
        const previous = select.value;
        select.replaceChildren();
        const groups = {{}};
        const groupOrder = [];
        (state.packCatalog || []).forEach(function (pack) {{
          const category = text(pack.category || "other");
          if (!groups[category]) {{
            const group = document.createElement("optgroup");
            group.label = localizedCategory(pack);
            groups[category] = group;
            groupOrder.push(category);
          }}
          const option = document.createElement("option");
          option.value = text(pack.id);
          option.textContent = (localizedDisplayName(pack) || text(pack.id)) + " · " + localizedRisk(pack);
          groups[category].appendChild(option);
        }});
        groupOrder.forEach(function (category) {{
          select.appendChild(groups[category]);
        }});
        if (previous) {{
          select.value = previous;
        }}
        if (!select.value && select.options.length) {{
          select.selectedIndex = 0;
        }}
        const pack = selectedCreatePack();
        applyPeriodFormat("first-period-input", "first-period-help", pack ? text(pack.period_type) : "month");
        updatePackChoiceHelp(pack);
      }}

      function renderWorkspaceRows() {{
        const container = byId("workspace-list-rows");
        container.replaceChildren();
        if (!state.workspaces.length) {{
          const empty = document.createElement("div");
          empty.className = "workspace-row";
          const cell = document.createElement("div");
          cell.className = "workspace-cell";
          cell.textContent = STRINGS.no_workspaces;
          empty.appendChild(cell);
          container.appendChild(empty);
          setMessage("workspace-list-message", STRINGS.create_first, "warning");
          return;
        }}
        const unresolved = unresolvedApprovalCount(state.workspaces);
        state.workspaces.forEach(function (workspace) {{
          const row = document.createElement("div");
          row.className = "workspace-row";

          const fields = [
            text(workspace.name) + (localizedDisplayName(workspace) ? " / " + localizedDisplayName(workspace) : ""),
            text(workspace.current_period || "-"),
            formatPreflight(state.preflight),
            formatRun(workspace.run || null),
            formatNextAction(workspace, state.preflight),
            workspace.period_stage === "ready_for_review" ? STRINGS.approval_waiting : STRINGS.approval_clear,
          ];

          fields.forEach(function (value) {{
            const cell = document.createElement("div");
            cell.className = "workspace-cell";
            cell.textContent = value;
            row.appendChild(cell);
          }});

          const actionCell = document.createElement("div");
          actionCell.className = "workspace-cell";
          const button = document.createElement("button");
          button.type = "button";
          button.className = "secondary-button";
          button.textContent = STRINGS.open_workspace;
          button.addEventListener("click", function () {{
            loadWorkspaceDetail(workspace.id);
          }});
          actionCell.appendChild(button);
          row.appendChild(actionCell);
          container.appendChild(row);
        }});
        setMessage(
          "workspace-list-message",
          STRINGS.unresolved_approvals + ": " + String(unresolved),
          unresolved ? "warning" : "success"
        );
      }}

      function renderWorkspaceMeta(workspace) {{
        const list = byId("workspace-meta-list");
        list.replaceChildren();
        appendMetaItem(list, STRINGS.workspace_name, workspace ? workspace.name : STRINGS.not_selected);
        appendMetaItem(list, STRINGS.pack_name, workspace ? (localizedDisplayName(workspace) || text(workspace.pack_id)) : "-");
        appendMetaItem(list, STRINGS.active_month, workspace && workspace.current_period ? workspace.current_period : "-");
        const styleReference = workspace && workspace.period ? workspace.period.style_reference : null;
        appendMetaItem(
          list,
          STRINGS.active_style_reference,
          styleReference && styleReference.relative_path ? text(styleReference.relative_path) : "-"
        );
        appendMetaItem(list, STRINGS.codex_preflight, formatPreflight(state.preflight));
        appendMetaItem(list, STRINGS.recent_run, formatRun(workspace ? workspace.run : null));
        appendMetaItem(list, STRINGS.next_action, workspace ? formatNextAction(workspace, state.preflight) : STRINGS.status_idle);
      }}

      function renderFolderButtons(workspace) {{
        const grid = byId("folder-grid");
        grid.replaceChildren();
        const folders = workspace && workspace.folders ? workspace.folders : {{}};
        FOLDER_ROLES.forEach(function (role) {{
          const details = folders[role] || {{}};
          const button = document.createElement("button");
          button.type = "button";
          button.className = "secondary-button folder-button";
          button.disabled = !workspace || !details.path;
          button.addEventListener("click", function () {{
            if (!workspace) {{
              return;
            }}
            runFolderOpen(role);
          }});

          const label = document.createElement("span");
          label.textContent = STRINGS.folder_roles[role] || role;
          button.appendChild(label);

          const count = document.createElement("span");
          count.className = "count-badge";
          count.textContent = String(details.file_count || 0);
          button.appendChild(count);
          grid.appendChild(button);
        }});
      }}

      function completedStepCount(stage) {{
        const order = [
          "created",
          "inputs_ready",
          "reviewed",
          "questioning",
          "ready_for_run",
          "ready_for_review",
          "approved",
        ];
        const index = order.indexOf(stage);
        return index >= 0 ? index + 1 : 0;
      }}

      function renderProgress(workspace) {{
        const stage = workspace && workspace.period ? workspace.period.stage : "";
        const completed = completedStepCount(stage);
        const list = byId("progress-steps");
        list.replaceChildren();
        (STRINGS.step_labels || []).forEach(function (label, index) {{
          const item = document.createElement("li");
          item.setAttribute("data-complete", index < completed ? "true" : "false");
          const title = document.createElement("strong");
          title.textContent = label;
          item.appendChild(title);
          const note = document.createElement("span");
          note.className = "muted";
          note.textContent = index === completed - 1 && stage ? (STRINGS.steps[stage] || label) : "";
          item.appendChild(note);
          list.appendChild(item);
        }});
      }}

      function renderQuestion(workspace) {{
        const question = currentQuestion(workspace);
        const input = byId("answer-input");
        const answers = workspace && workspace.period && workspace.period.answers ? workspace.period.answers : {{}};
        if (!question) {{
          byId("question-text").textContent = STRINGS.no_question;
          input.value = "";
          input.disabled = true;
          byId("save-answer-button").disabled = true;
          return;
        }}
        byId("question-text").textContent = text(question.question || question.id);
        input.disabled = false;
        input.value = text(answers[question.id] || "");
        byId("save-answer-button").disabled = false;
      }}

      function renderDraft(workspace) {{
        const period = workspace && workspace.period ? workspace.period : null;
        const draft = period ? period.current_draft : null;
        const audit = workspace && workspace.approval ? workspace.approval.audit : null;
        let message = STRINGS.draft_not_ready;
        let tone = "";
        if (draft) {{
          message = STRINGS.draft_ready_prefix + " " + draft.name;
          tone = "warning";
        }}
        if (audit && audit.status === "approved") {{
          message = STRINGS.approved_local;
          tone = "success";
        }}
        setMessage("draft-message", message, tone);
      }}

      function formatExtractionStatus(status) {{
        return STRINGS.extraction_statuses[text(status)] || STRINGS.extraction_statuses.generic;
      }}

      function appendManifestRecords(listId, records) {{
        const list = byId(listId);
        list.replaceChildren();
        if (!Array.isArray(records) || !records.length) {{
          appendTextRow(list, [STRINGS.no_files]);
          return;
        }}
        records.forEach(function (record) {{
          const parts = [];
          if (record && typeof record === "object") {{
            parts.push(text(record.name || record.source_role));
            if (record.extraction_status) {{
              parts.push("[" + formatExtractionStatus(record.extraction_status) + "]");
            }}
            if (Number.isFinite(record.bytes)) {{
              parts.push(String(record.bytes) + " B");
            }}
          }} else {{
            parts.push(text(record));
          }}
          appendTextRow(list, [parts.filter(Boolean).join(" ") || STRINGS.no_files]);
        }});
      }}

      function renderSourceManifest(workspace) {{
        const manifest = workspace ? workspace.source_manifest : null;
        const absent = byId("manifest-absent");
        const warning = byId("missing-input-warning");
        const provenance = byId("source-provenance");
        absent.textContent = manifest ? "" : STRINGS.manifest_absent;
        absent.hidden = !!manifest;
        warning.hidden = true;
        warning.textContent = "";
        provenance.replaceChildren();
        if (!manifest) {{
          appendManifestRecords("accepted-files", []);
          appendManifestRecords("rejected-files", []);
          appendManifestRecords("skipped-files", []);
          return;
        }}
        appendMetaItem(provenance, STRINGS.manifest_period, text(manifest.period_id));
        appendMetaItem(provenance, STRINGS.manifest_generated, text(manifest.generated_at));
        const period = workspace && workspace.period ? workspace.period : null;
        appendMetaItem(provenance, STRINGS.manifest_hash, period ? text(period.source_manifest_hash) : "");
        appendManifestRecords("accepted-files", manifest.accepted);
        appendManifestRecords("rejected-files", manifest.rejected);
        appendManifestRecords("skipped-files", manifest.skipped);
        const accepted = Array.isArray(manifest.accepted) ? manifest.accepted.length : 0;
        warning.hidden = accepted > 0;
        warning.textContent = accepted > 0 ? "" : STRINGS.missing_inputs;
      }}

      function updateDetailControls(workspace) {{
        const period = workspace && workspace.period ? workspace.period : null;
        const run = workspace ? workspace.run : null;
        const stage = period ? period.stage : "";
        const periodType = workspace ? text(workspace.period_type || "month") : "month";
        const hasPeriod = !!(workspace && workspace.current_period);
        const isCancelling = !!(run && run.status === "cancelling");
        const canCancel = !!(run && (run.status === "running" || run.status === "cancelling"));
        const canInspect = hasPeriod && INSPECTABLE_STAGES.indexOf(stage) !== -1;
        const runActive = !!(run && (run.status === "running" || run.status === "cancelling"));
        const inspectBusy = byId("inspect-button").getAttribute("aria-busy") === "true";
        byId("inspect-button").disabled = !canInspect || runActive || inspectBusy;
        byId("generate-button").disabled = stage !== "ready_for_run";
        byId("cancel-button").disabled = !canCancel || isCancelling;
        byId("cancel-button").textContent = isCancelling ? STRINGS.cancelling : STRINGS.cancel;
        byId("cancel-button").dataset.baseLabel = byId("cancel-button").textContent;
        byId("approve-button").disabled = stage !== "ready_for_review";
        byId("rollover-button").disabled = stage !== "approved";
        byId("approve-name-input").disabled = stage !== "ready_for_review";
        byId("approve-pin-input").disabled = stage !== "ready_for_review";
        byId("reuse-style-checkbox").disabled = stage !== "approved" || !latestApprovedOutput(workspace);
        byId("open-draft-button").disabled = !workspace || !hasPeriod;
        byId("detail-stage-pill").textContent = stage ? (STRINGS.steps[stage] || stage) : STRINGS.status_idle;
        applyPeriodFormat("next-period-input", "next-period-help", periodType);
      }}

      function renderDetail(workspace) {{
        state.selectedWorkspace = workspace || null;
        byId("next-period-input").value = workspace && workspace.period && workspace.period.stage === "approved"
          ? suggestedNextPeriod(workspace.current_period, workspace.period_type)
          : "";
        renderWorkspaceMeta(workspace);
        renderFolderButtons(workspace);
        renderProgress(workspace);
        renderSourceManifest(workspace);
        renderQuestion(workspace);
        renderDraft(workspace);
        updateDetailControls(workspace);
        setMessage("workspace-detail-message", workspace ? formatNextAction(workspace, state.preflight) : STRINGS.not_selected, workspace ? "" : "warning");
        if (workspace && workspace.approval) {{
          byId("approve-name-input").value = text(workspace.approval.approver || "");
        }}
      }}

      async function refreshWorkspaceList() {{
        const payload = await apiFetch(ROUTES.workspaces(), {{ method: "GET" }});
        state.workspaces = Array.isArray(payload.data.workspaces) ? payload.data.workspaces : [];
        state.packCatalog = Array.isArray(payload.data.pack_catalog) ? payload.data.pack_catalog : [];
        state.rootChoices = Array.isArray(payload.data.root_choices) ? payload.data.root_choices : [];
        state.preflight = payload.data.preflight || null;
        renderRootChoices();
        renderPackChoices();
        byId("list-preflight-pill").textContent = formatPreflight(state.preflight);
        renderWorkspaceRows();
        if (state.selectedWorkspaceId) {{
          await loadWorkspaceDetail(state.selectedWorkspaceId, true);
        }}
        return payload;
      }}

      async function loadWorkspaceDetail(workspaceId, keepView) {{
        const payload = await apiFetch(ROUTES.workspace(workspaceId), {{ method: "GET" }});
        state.selectedWorkspaceId = workspaceId;
        state.preflight = payload.data.preflight || state.preflight;
        renderDetail(payload.data.workspace);
        if (!keepView) {{
          showView("detail");
        }}
        return payload;
      }}

      async function withButton(buttonId, work) {{
        const button = byId(buttonId);
        setBusy(button, true);
        try {{
          return await work();
        }} finally {{
          setBusy(button, false);
          if (buttonId !== "create-workspace-button") {{
            updateDetailControls(state.selectedWorkspace);
          }}
        }}
      }}

      async function createWorkspace() {{
        await withButton("create-workspace-button", async function () {{
          const pack = selectedCreatePack();
          const payload = await postJson(ROUTES.workspaces(), {{
            name: byId("workspace-name-input").value,
            pack_id: pack ? pack.id : "",
            period_id: byId("first-period-input").value,
            root_choice: byId("root-choice-select").value,
            approver: byId("approver-input").value,
            pin: byId("pin-input").value,
          }});
          state.selectedWorkspaceId = payload.data.workspace.id;
          await refreshWorkspaceList();
          await loadWorkspaceDetail(state.selectedWorkspaceId);
          byId("first-period-input").value = "";
          byId("pin-input").value = "";
          setMessage("workspace-list-message", STRINGS.status_done, "success");
        }});
      }}

      async function inspectWorkspace() {{
        const workspace = state.selectedWorkspace;
        if (!workspace || !workspace.current_period) {{
          setMessage("workspace-detail-message", STRINGS.missing_period, "warning");
          return;
        }}
        await withButton("inspect-button", async function () {{
          const payload = await postJson(ROUTES.inspect(workspace.id), {{ period_id: workspace.current_period }});
          renderDetail(payload.data.workspace);
        }});
      }}

      async function saveAnswer() {{
        const workspace = state.selectedWorkspace;
        const question = currentQuestion(workspace);
        if (!workspace || !question) {{
          setMessage("workspace-detail-message", STRINGS.no_question, "warning");
          return;
        }}
        await withButton("save-answer-button", async function () {{
          const payload = await postJson(ROUTES.answer(workspace.id), {{
            question_id: question.id,
            answer: byId("answer-input").value,
          }});
          renderDetail(payload.data.workspace);
          setMessage("workspace-detail-message", STRINGS.status_done, "success");
        }});
      }}

      async function generateDraft() {{
        const workspace = state.selectedWorkspace;
        if (!workspace || !workspace.current_period) {{
          setMessage("workspace-detail-message", STRINGS.missing_period, "warning");
          return;
        }}
        await withButton("generate-button", async function () {{
          const payload = await postJson(ROUTES.generate(workspace.id), {{ period_id: workspace.current_period }});
          renderDetail(payload.data.workspace);
        }});
      }}

      async function cancelRun() {{
        const workspace = state.selectedWorkspace;
        if (!workspace || !workspace.run || !workspace.run.run_id) {{
          setMessage("workspace-detail-message", STRINGS.no_recent_run, "warning");
          return;
        }}
        await withButton("cancel-button", async function () {{
          const payload = await postJson(ROUTES.cancel(workspace.id), {{ run_id: workspace.run.run_id }});
          renderDetail(payload.data.workspace);
        }});
      }}

      async function approveDraft() {{
        const workspace = state.selectedWorkspace;
        const draft = workspace && workspace.period ? workspace.period.current_draft : null;
        if (!workspace || !draft) {{
          setMessage("workspace-detail-message", STRINGS.draft_not_ready, "warning");
          return;
        }}
        await withButton("approve-button", async function () {{
          const payload = await postJson(ROUTES.approve(workspace.id), {{
            draft_id: draft.name,
            approver: byId("approve-name-input").value,
            pin: byId("approve-pin-input").value,
          }});
          byId("approve-pin-input").value = "";
          renderDetail(payload.data.workspace);
        }});
      }}

      async function prepareNextPeriod() {{
        const workspace = state.selectedWorkspace;
        if (!workspace) {{
          setMessage("workspace-detail-message", STRINGS.not_selected, "warning");
          return;
        }}
        let styleReference = null;
        if (byId("reuse-style-checkbox").checked) {{
          const approved = latestApprovedOutput(workspace);
          if (approved) {{
            styleReference = {{
              confirmed: true,
              relative_path: approved.path,
              sha256: approved.sha256,
            }};
          }}
        }}
        await withButton("rollover-button", async function () {{
          const payload = await postJson(ROUTES.rollover(workspace.id), {{
            next_period_id: byId("next-period-input").value,
            style_reference: styleReference,
          }});
          renderDetail(payload.data.workspace);
        }});
      }}

      async function runFolderOpen(role) {{
        const workspace = state.selectedWorkspace;
        if (!workspace) {{
          return;
        }}
        const payload = await postJson(ROUTES.openFolder(workspace.id), {{ role: role }});
        renderDetail(payload.data.workspace);
      }}

      async function refreshAll() {{
        try {{
          await refreshWorkspaceList();
          if (state.selectedWorkspaceId) {{
            await loadWorkspaceDetail(state.selectedWorkspaceId, true);
          }}
        }} catch (error) {{
          const message = formatApiError(error);
          setMessage("workspace-list-message", message, "error");
          setMessage("workspace-detail-message", message, "error");
        }}
      }}

      byId("show-list-button").addEventListener("click", function () {{
        showView("list");
      }});
      byId("show-detail-button").addEventListener("click", function () {{
        showView("detail");
      }});
      [byId("show-list-button"), byId("show-detail-button")].forEach(function (tab, index, tabs) {{
        tab.addEventListener("keydown", function (event) {{
          let nextIndex = index;
          if (event.key === "ArrowLeft") nextIndex = (index + tabs.length - 1) % tabs.length;
          if (event.key === "ArrowRight") nextIndex = (index + 1) % tabs.length;
          if (event.key === "Home") nextIndex = 0;
          if (event.key === "End") nextIndex = tabs.length - 1;
          if (nextIndex === index) return;
          event.preventDefault();
          tabs[nextIndex].focus();
          tabs[nextIndex].click();
        }});
      }});
      byId("back-to-list-button").addEventListener("click", function () {{
        showView("list");
      }});
      byId("refresh-button").addEventListener("click", refreshAll);
      byId("workflow-pack-select").addEventListener("change", function () {{
        const pack = selectedCreatePack();
        applyPeriodFormat("first-period-input", "first-period-help", pack ? text(pack.period_type) : "month");
        updatePackChoiceHelp(pack);
      }});
      byId("create-workspace-button").addEventListener("click", function () {{
        createWorkspace().catch(function (error) {{
          setMessage("workspace-list-message", formatApiError(error), "error");
        }});
      }});
      byId("inspect-button").addEventListener("click", function () {{
        inspectWorkspace().catch(function (error) {{
          setMessage("workspace-detail-message", formatApiError(error), "error");
        }});
      }});
      byId("save-answer-button").addEventListener("click", function () {{
        saveAnswer().catch(function (error) {{
          setMessage("workspace-detail-message", formatApiError(error), "error");
        }});
      }});
      byId("generate-button").addEventListener("click", function () {{
        generateDraft().catch(function (error) {{
          setMessage("workspace-detail-message", formatApiError(error), "error");
        }});
      }});
      byId("cancel-button").addEventListener("click", function () {{
        cancelRun().catch(function (error) {{
          setMessage("workspace-detail-message", formatApiError(error), "error");
        }});
      }});
      byId("approve-button").addEventListener("click", function () {{
        approveDraft().catch(function (error) {{
          setMessage("workspace-detail-message", formatApiError(error), "error");
        }});
      }});
      byId("rollover-button").addEventListener("click", function () {{
        prepareNextPeriod().catch(function (error) {{
          setMessage("workspace-detail-message", formatApiError(error), "error");
        }});
      }});
      byId("open-draft-button").addEventListener("click", function () {{
        runFolderOpen("drafts").catch(function (error) {{
          setMessage("workspace-detail-message", formatApiError(error), "error");
        }});
      }});

      renderDetail(null);
      refreshAll();
    }})();
  </script>
</body>
</html>
""".format(
        page_lang=language,
        page_lang_json=json.dumps(language),
        title=strings["title"],
        subtitle=strings["subtitle"],
        list_view=strings["list_view"],
        detail_view=strings["detail_view"],
        back_to_list=strings["back_to_list"],
        refresh=strings["refresh"],
        list_heading=strings["list_heading"],
        list_help=strings["list_help"],
        workspace_name=strings["workspace_name"],
        active_month=strings["active_month"],
        active_style_reference=strings["active_style_reference"],
        codex_preflight=strings["codex_preflight"],
        recent_run=strings["recent_run"],
        next_action=strings["next_action"],
        unresolved_approvals=strings["unresolved_approvals"],
        open_workspace=strings["open_workspace"],
        create_workspace=strings["create_workspace"],
        name_label=strings["name_label"],
        pack_label=strings["pack_label"],
        pack_help=strings["pack_help"],
        first_period_label=strings["first_period_label"],
        approver_label=strings["approver_label"],
        pin_label=strings["pin_label"],
        root_choice_label=strings["root_choice_label"],
        status_idle=strings["status_idle"],
        detail_heading=strings["detail_heading"],
        detail_help=strings["detail_help"],
        folder_panel=strings["folder_panel"],
        folder_help=strings["folder_help"],
        progress_panel=strings["progress_panel"],
        source_panel=strings["source_panel"],
        accepted_formats=strings["accepted_formats"],
        accepted_formats_value=strings["accepted_formats_value"],
        accepted_files=strings["accepted_files"],
        rejected_files=strings["rejected_files"],
        skipped_files=strings["skipped_files"],
        question_panel=strings["question_panel"],
        question_help=strings["question_help"],
        answer_label=strings["answer_label"],
        save_answer=strings["save_answer"],
        action_panel=strings["action_panel"],
        inspect=strings["inspect"],
        generate=strings["generate"],
        cancel=strings["cancel"],
        draft_panel=strings["draft_panel"],
        draft_not_ready=strings["draft_not_ready"],
        open_draft=strings["open_draft"],
        approval_panel=strings["approval_panel"],
        approval_help=strings["approval_help"],
        approval_name=strings["approval_name"],
        approval_pin=strings["approval_pin"],
        approve=strings["approve"],
        approval_honesty=strings["approval_honesty"],
        rollover_panel=strings["rollover_panel"],
        next_period_label=strings["next_period_label"],
        reuse_style=strings["reuse_style"],
        rollover=strings["rollover"],
        strings=serialized_strings,
        token=serialized_token,
    )


__all__ = ["render_office_workspace_ui"]
