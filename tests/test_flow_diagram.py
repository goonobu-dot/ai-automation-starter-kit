from ai_automation_kit.cli import build_parser
from ai_automation_kit.cli import main
from ai_automation_kit.core.flow_diagram import render_flow_diagram_html
from ai_automation_kit.core.flows import get_flow


def _sample_flow() -> dict:
    return get_flow("invoice-document-followup")


def test_diagram_html_contains_flow_name_and_all_step_names():
    flow = _sample_flow()
    html = render_flow_diagram_html(flow)
    assert flow["name"] in html
    for step in flow["steps"]:
        assert step["name"] in html


def test_diagram_html_numbers_steps_and_shows_input_output():
    flow = _sample_flow()
    html = render_flow_diagram_html(flow)
    for number, step in enumerate(flow["steps"], start=1):
        assert f"STEP {number}" in html
        assert step["input"] in html
        assert step["output"] in html
        assert step["tool"] in html


def test_diagram_html_marks_human_approval_steps():
    flow = _sample_flow()
    html = render_flow_diagram_html(flow)
    approval_count = sum(1 for step in flow["steps"] if step["human_approval"])
    assert approval_count > 0
    assert html.count("人の承認が必要") == approval_count


def test_diagram_html_includes_tools_before_after_and_safety_note():
    flow = _sample_flow()
    html = render_flow_diagram_html(flow)
    for tool in flow["tools"]:
        assert tool in html
    assert "自動化前" in html
    assert "自動化後" in html
    # 安全設計の説明（自動送信しない）を必ず含める。
    assert "送信は必ず人が行います" in html


def test_diagram_html_is_self_contained_without_cdn():
    html = render_flow_diagram_html(_sample_flow())
    lowered = html.lower()
    assert "https://" not in lowered
    assert "http://" not in lowered
    assert "<script" not in lowered
    assert "<link" not in lowered
    assert "@import" not in lowered
    # 日本語で正しく表示されるよう文字コード指定を含む単一 HTML。
    assert "<meta charset=" in lowered
    assert lowered.startswith("<!doctype html>")


def test_parser_accepts_flows_diagram_command():
    parser = build_parser()
    args = parser.parse_args(["flows", "diagram", "invoice-document-followup", "--output", "out"])
    assert args.command == "flows"
    assert args.flow_command == "diagram"
    assert args.flow_id == "invoice-document-followup"
    assert args.output == "out"


def test_main_runs_flows_diagram_and_writes_html(tmp_path, capsys):
    output = tmp_path / "diagram"

    exit_code = main(["flows", "diagram", "invoice-document-followup", "--output", str(output)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "flow_diagram=" in captured.out
    html = (output / "flow_diagram.html").read_text(encoding="utf-8")
    assert "Invoice and Document Follow-up" in html
    assert "人の承認が必要" in html


def test_main_flows_diagram_rejects_unknown_flow(tmp_path, capsys):
    exit_code = main(["flows", "diagram", "no-such-flow", "--output", str(tmp_path / "x")])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "no-such-flow" in captured.err


def test_flows_install_also_generates_flow_diagram(tmp_path):
    output = tmp_path / "installed"

    exit_code = main(["flows", "install", "invoice-document-followup", "--output", str(output)])

    assert exit_code == 0
    # 既存の生成物はそのまま、flow_diagram.html が追加される。
    assert (output / "flow.yaml").exists()
    assert (output / "workflow_map.mmd").exists()
    diagram = (output / "flow_diagram.html").read_text(encoding="utf-8")
    assert "人の承認が必要" in diagram
    assert "送信は必ず人が行います" in diagram
