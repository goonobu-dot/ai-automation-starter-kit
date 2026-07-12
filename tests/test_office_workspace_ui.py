import re

import pytest

from ai_automation_kit.core.office_workspace_ui import render_office_workspace_ui


SAFE_TOKEN = "0123456789abcdef" * 4


def test_ui_rejects_unsupported_language_and_unsafe_token():
    with pytest.raises(ValueError, match="language must be 'ja' or 'en'"):
        render_office_workspace_ui("fr", SAFE_TOKEN)

    for token in (
        "",
        "short",
        "with space " + ("0" * 53),
        "g" * 64,
        "<" + ("0" * 63),
        None,
    ):
        with pytest.raises(ValueError, match="token must be a 64-character lowercase hex string"):
            render_office_workspace_ui("ja", token)  # type: ignore[arg-type]


def test_ui_has_two_localized_beginner_views_and_no_language_leakage():
    ja = render_office_workspace_ui("ja", SAFE_TOKEN)
    en = render_office_workspace_ui("en", SAFE_TOKEN)

    assert 'id="workspace-list-view"' in ja
    assert 'id="workspace-detail-view"' in ja
    assert 'id="workspace-list-view"' in en
    assert 'id="workspace-detail-view"' in en

    assert "オフィス作業場所" in ja
    assert "作業場所と最初の期間を作る" in ja
    assert "ワークフローパック" in ja
    assert "資料を確認" in ja
    assert "下書きを作成" in ja
    assert "承認者名" in ja
    assert "承認用PIN" in ja
    assert "次の期間を準備" in ja
    assert "Monthly report workspace" not in ja
    assert "Create workspace and first period" not in ja
    assert "Generate draft" not in ja

    assert "Office workspace" in en
    assert "Create workspace and first period" in en
    assert "Workflow pack" in en
    assert "Inspect materials" in en
    assert "Generate draft" in en
    assert "Approver name" in en
    assert "Approval PIN" in en
    assert "Prepare next period" in en
    assert "月報作業場所" not in en
    assert "作業場所と最初の期間を作る" not in en
    assert "承認して完成版へ保存" not in en


def test_ui_covers_all_task4_routes_with_relative_same_origin_fetch_only():
    html = render_office_workspace_ui("en", SAFE_TOKEN)

    assert 'credentials: "same-origin"' in html
    assert 'cache: "no-store"' in html
    assert 'fetch(path, request)' in html
    assert "validateRelativeApiPath" in html
    expected_pairs = {
        ("GET", "ROUTES.workspaces()"),
        ("POST", "ROUTES.workspaces()"),
        ("GET", "ROUTES.workspace(workspaceId)"),
        ("POST", "ROUTES.inspect(workspace.id)"),
        ("POST", "ROUTES.answer(workspace.id)"),
        ("POST", "ROUTES.generate(workspace.id)"),
        ("POST", "ROUTES.cancel(workspace.id)"),
        ("POST", "ROUTES.approve(workspace.id)"),
        ("POST", "ROUTES.rollover(workspace.id)"),
        ("POST", "ROUTES.openFolder(workspace.id)"),
    }
    for method, route_call in expected_pairs:
        if method == "GET":
            assert 'apiFetch({}, {{ method: "GET"'.format(route_call) in html
        else:
            assert "postJson({},".format(route_call) in html
    assert 'method: "POST"' in html
    assert "action_nonce: state.actionNonce" in html

    assert 'return "/api/workspaces";' in html
    assert 'return "/api/workspaces/" + encodeURIComponent(workspaceId);' in html
    for route_name, suffix in (
        ("inspect", "/inspect"),
        ("answer", "/answer"),
        ("generate", "/generate"),
        ("cancel", "/cancel"),
        ("approve", "/approve"),
        ("rollover", "/rollover"),
        ("openFolder", "/open-folder"),
    ):
        assert '{}: function (workspaceId)'.format(route_name) in html
        assert '+ "{}";'.format(suffix) in html

    assert "http://" not in html
    assert "https://" not in html
    assert "new URL(" not in html
    assert "location.search" not in html
    assert "URLSearchParams" not in html


def test_ui_uses_nonce_and_in_memory_token_without_xss_primitives():
    html = render_office_workspace_ui("ja", SAFE_TOKEN)

    assert html.count(SAFE_TOKEN) == 1
    assert 'const SESSION_TOKEN = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef";' in html
    assert "action_nonce" in html
    assert "state.actionNonce" in html
    assert '"X-Office-Workspace-Token"' in html
    assert "localStorage" not in html
    assert "sessionStorage" not in html
    assert "document.cookie" not in html
    assert "console.log" not in html
    assert "innerHTML" not in html
    assert "outerHTML" not in html
    assert "insertAdjacentHTML" not in html
    assert "eval(" not in html
    assert "Function(" not in html
    assert "document.write" not in html


def test_ui_uses_textcontent_createelement_and_accessible_responsive_css():
    html = render_office_workspace_ui("en", SAFE_TOKEN)

    assert "createElement(" in html
    assert ".textContent =" in html
    assert 'aria-live="polite"' in html
    assert 'aria-live="assertive"' in html
    assert 'role="tablist"' in html
    assert html.count('role="tab"') == 2
    assert html.count('role="tabpanel"') == 2
    assert 'aria-labelledby="show-list-button"' in html
    assert 'aria-labelledby="show-detail-button"' in html
    assert 'aria-selected="true" tabindex="0"' in html
    assert 'aria-selected="false" tabindex="-1"' in html
    for key in ("ArrowLeft", "ArrowRight", "Home", "End"):
        assert '"{}"'.format(key) in html
    assert ".focus()" in html
    for control_id in (
        "workspace-name-input",
        "workflow-pack-select",
        "first-period-input",
        "approver-input",
        "pin-input",
        "answer-input",
        "approve-name-input",
        "approve-pin-input",
        "next-period-input",
    ):
        assert 'for="{}"'.format(control_id) in html

    assert "@media (max-width: 900px)" in html
    assert "@media (max-width: 540px)" in html
    assert "minmax(0, 1fr)" in html
    assert "overflow-wrap: anywhere" in html
    assert "width: min(100%, 1440px)" in html
    assert "flex-wrap: wrap" in html
    assert "max-width: 100%" in html
    assert "overflow-x: hidden" in html
    assert "min-width: 0" in html
    assert "linear-gradient" not in html
    assert "<img" not in html
    assert "<svg" not in html
    assert "@import" not in html


def test_ui_honestly_labels_draft_and_local_approval_states():
    ja = render_office_workspace_ui("ja", SAFE_TOKEN)
    en = render_office_workspace_ui("en", SAFE_TOKEN)

    assert "下書きはまだ承認されていません。" in ja
    assert "この承認はこの端末内のローカル記録です。" in ja
    assert "承認すると外部送信は行わず、完成版をローカル保存します。" in ja

    assert "The draft is not approved yet." in en
    assert "This approval is a local record on this device." in en
    assert "Approval saves a local approved copy and does not send anything externally." in en


def test_ui_script_escapes_data_through_json_literals():
    html = render_office_workspace_ui("en", SAFE_TOKEN)

    match = re.search(r"const STRINGS = (\{.*?\});\s+const PAGE_LANG = .*?;\s+const SESSION_TOKEN =", html, re.S)
    assert match, "STRINGS JSON literal was not embedded"
    payload = match.group(1)
    assert "</script>" not in payload
    assert '\\"' not in SAFE_TOKEN


def test_ui_never_displays_server_human_strings_and_localizes_stable_states():
    ja = render_office_workspace_ui("ja", SAFE_TOKEN)
    en = render_office_workspace_ui("en", SAFE_TOKEN)

    for html in (ja, en):
        assert "payload.next_action" not in html
        assert "payload.error.message" not in html
        assert "error.message" not in html
        assert "formatNextAction" in html
        assert "formatApiError" in html
        for state in (
            "created",
            "inputs_ready",
            "reviewed",
            "questioning",
            "ready_for_run",
            "ready_for_review",
            "approved",
            "cancelled",
            "failed",
            "running",
            "cancelling",
        ):
            assert '"{}"'.format(state) in html

    assert "Create the first reporting period." not in ja
    assert "Refresh the workspace and retry." not in ja
    assert "requested action is not allowed" not in ja
    assert "最初の期間を準備" not in en
    assert "作業場所を更新して再試行" not in en


def test_ui_has_complete_localized_error_code_maps_with_generic_fallback():
    expected_codes = {
        "approval_denied",
        "bad_action_nonce",
        "bad_content_length",
        "bad_content_type",
        "bad_draft_id",
        "bad_folder_role",
        "bad_json",
        "bad_pack_id",
        "bad_period_id",
        "bad_question_id",
        "bad_root_choice",
        "bad_run_id",
        "bad_style_reference",
        "bad_token",
        "codex_not_logged_in",
        "codex_unavailable",
        "environment_not_ready",
        "host_not_allowed",
        "loopback_only",
        "method_not_allowed",
        "missing_token",
        "not_found",
        "open_folder_failed",
        "origin_not_allowed",
        "period_not_found",
        "question_not_found",
        "request_error",
        "request_too_large",
        "run_not_found",
        "short_body",
        "state_conflict",
        "workspace_not_found",
    }
    for language in ("ja", "en"):
        html = render_office_workspace_ui(language, SAFE_TOKEN)
        match = re.search(r'"errors":\s*(\{.*?\}),\s*"folder_roles"', html, re.S)
        assert match
        assert expected_codes <= set(re.findall(r'"([a-z_]+)"\s*:', match.group(1)))
        assert '"generic"' in match.group(1)
        assert "STRINGS.errors.generic" in html


def test_ui_renders_manifest_provenance_warnings_and_fixed_draft_open_command():
    ja = render_office_workspace_ui("ja", SAFE_TOKEN)
    en = render_office_workspace_ui("en", SAFE_TOKEN)

    for html in (ja, en):
        for element_id in (
            "accepted-formats",
            "missing-input-warning",
            "source-provenance",
            "accepted-files",
            "rejected-files",
            "skipped-files",
            "manifest-absent",
            "open-draft-button",
        ):
            assert 'id="{}"'.format(element_id) in html
        assert "renderSourceManifest" in html
        assert 'runFolderOpen("drafts")' in html
        assert "source_manifest_hash" in html
        assert "generated_at" in html
        assert "original_path" not in html

    assert "対応形式" in ja
    assert "下書きフォルダを開く" in ja
    assert "資料確認記録はまだありません" in ja
    assert "Accepted formats" in en
    assert "Open draft folder" in en
    assert "No source manifest is available yet" in en


def test_ui_shows_approval_backlog_and_distinct_cancelling_state():
    ja = render_office_workspace_ui("ja", SAFE_TOKEN)
    en = render_office_workspace_ui("en", SAFE_TOKEN)

    for html in (ja, en):
        assert "unresolvedApprovalCount" in html
        assert "period_stage === \"ready_for_review\"" in html
        assert 'id="cancel-button"' in html
        assert "STRINGS.run_cancelling" in html
        assert 'run.status === "cancelling"' in html
        assert 'byId("cancel-button").disabled = !canCancel || isCancelling;' in html
        assert 'byId("cancel-button").textContent = isCancelling ? STRINGS.cancelling : STRINGS.cancel;' in html

    assert "未解決の承認" in ja
    assert "停止処理中" in ja
    assert "Unresolved approvals" in en
    assert "Cancelling" in en


def test_ui_pins_busy_error_and_disabled_control_contracts():
    html = render_office_workspace_ui("en", SAFE_TOKEN)

    assert 'button.setAttribute("aria-busy", busy ? "true" : "false")' in html
    assert "button.dataset.baseLabel" in html
    assert "STRINGS.status_busy" in html
    assert 'setMessage("workspace-detail-message", formatApiError(error), "error")' in html
    assert 'setMessage("workspace-list-message", formatApiError(error), "error")' in html
    assert 'updateDetailControls(state.selectedWorkspace);' in html
    for control in (
        "inspect-button",
        "generate-button",
        "cancel-button",
        "approve-button",
        "rollover-button",
        "save-answer-button",
        "open-draft-button",
    ):
        assert 'byId("{}")'.format(control) in html


def test_ui_uses_pack_catalog_and_period_type_to_drive_beginner_period_inputs():
    html = render_office_workspace_ui("en", SAFE_TOKEN)

    for element_id in (
        "workflow-pack-select",
        "workflow-pack-help",
        "first-period-input",
        "first-period-help",
        "next-period-help",
    ):
        assert 'id="{}"'.format(element_id) in html
    assert "state.packCatalog" in html
    assert "payload.data.pack_catalog" in html
    assert "renderPackChoices" in html
    assert "localizedDisplayName" in html
    assert "localizedCategory" in html
    assert "localizedRisk" in html
    assert 'document.createElement("optgroup")' in html
    assert "pack.category" in html
    assert "risk_tier" in html
    assert "pack.business_outcome" in html
    assert "Draft preparation only; a person must review and approve." in html
    assert "下書き作成専用です。人が確認して承認します。" in render_office_workspace_ui("ja", SAFE_TOKEN)
    assert "applyPeriodFormat" in html
    assert 'pack_id: pack ? pack.id : ""' in html
    assert 'period_id: byId("first-period-input").value' in html
    assert 'applyPeriodFormat("first-period-input", "first-period-help"' in html
    assert 'applyPeriodFormat("next-period-input", "next-period-help"' in html
    assert 'id="reuse-style-checkbox" type="checkbox" checked' in html
    assert "function suggestedNextPeriod" in html
    assert "suggestedNextPeriod(workspace.current_period, workspace.period_type)" in html
    assert "Approved example in use" in html
    assert "workspace.period.style_reference" in html
    assert "Monthly packs use YYYY-MM." in html
    assert "Daily packs use YYYY-MM-DD." in html


def test_ui_localizes_every_extraction_status_without_rendering_raw_enums():
    supported = {
        "not_attempted",
        "extracted",
        "metadata_only",
        "extraction_error",
        "extraction_limit",
        "optional_isolation_unavailable",
        "optional_reader_missing",
    }
    ja = render_office_workspace_ui("ja", SAFE_TOKEN)
    en = render_office_workspace_ui("en", SAFE_TOKEN)

    for html in (ja, en):
        assert "formatExtractionStatus" in html
        assert "STRINGS.extraction_statuses.generic" in html
        assert "text(record.extraction_status)" not in html
        match = re.search(r'"extraction_statuses":\s*(\{.*?\}),\s*"next_actions"', html, re.S)
        assert match
        assert supported <= set(re.findall(r'"([a-z_]+)"\s*:', match.group(1)))

    assert "内容を読み取り済み" in ja
    assert "状態を確認できません" in ja
    assert "Extracted" in en
    assert "Status unavailable" in en


def test_ui_list_uses_bounded_server_run_and_inspect_has_exact_stage_table():
    html = render_office_workspace_ui("en", SAFE_TOKEN)

    assert "formatRun(workspace.run || null)" in html
    assert 'const INSPECTABLE_STAGES = ["created", "questioning", "ready_for_run", "failed", "cancelled"];' in html
    assert "INSPECTABLE_STAGES.indexOf(stage) !== -1" in html
    assert 'run.status === "running" || run.status === "cancelling"' in html
    assert 'byId("inspect-button").getAttribute("aria-busy") === "true"' in html
    assert 'byId("inspect-button").disabled = !canInspect || runActive || inspectBusy;' in html

    match = re.search(r"const INSPECTABLE_STAGES = \[(.*?)\];", html)
    assert match
    assert set(re.findall(r'"([a-z_]+)"', match.group(1))) == {
        "created",
        "questioning",
        "ready_for_run",
        "failed",
        "cancelled",
    }
    for forbidden in ("inputs_ready", "reviewed", "running", "ready_for_review", "approved"):
        assert 'const INSPECTABLE_STAGES = ["{}"'.format(forbidden) not in html
