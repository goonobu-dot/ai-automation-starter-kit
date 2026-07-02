from ai_automation_kit.core.beginner_guide import BEGINNER_STEPS
from ai_automation_kit.core.beginner_guide import render_beginner_overview
from ai_automation_kit.core.beginner_guide import render_beginner_step

import pytest


def test_beginner_steps_cover_five_stages_in_order():
    assert sorted(BEGINNER_STEPS.keys()) == [1, 2, 3, 4, 5]
    assert BEGINNER_STEPS[1]["title"] == "環境準備"
    assert BEGINNER_STEPS[2]["title"] == "最初のデモ"
    assert BEGINNER_STEPS[3]["title"] == "営業準備"
    assert BEGINNER_STEPS[4]["title"] == "最初の案件実行"
    assert BEGINNER_STEPS[5]["title"] == "納品と請求"


def test_overview_lists_all_steps_with_numbers_and_next_command():
    overview = render_beginner_overview()
    for number, step in BEGINNER_STEPS.items():
        assert f"{number}." in overview
        assert step["title"] in overview
    # TTY 対話に依存せず、次に打つコマンドを案内する。
    assert "ai-automation-kit beginner --step 1" in overview
    assert "input(" not in overview


def test_each_step_has_required_sections():
    for number in BEGINNER_STEPS:
        text = render_beginner_step(number)
        assert "この段階でやること" in text
        assert "実行するコマンド" in text
        assert "開くファイル" in text
        assert "次の一歩" in text


def test_step_1_guides_environment_setup():
    text = render_beginner_step(1)
    assert "環境準備" in text
    assert "ai-automation-kit doctor" in text
    assert "docs/GETTING_STARTED.ja.md" in text


def test_step_2_uses_complete_workspace():
    text = render_beginner_step(2)
    assert "complete-workspace" in text


def test_step_3_prepares_sales_materials():
    text = render_beginner_step(3)
    assert "beginner-sales" in text
    assert "docs/TUTORIAL_SME_PROPOSAL.ja.md" in text


def test_step_4_uses_flow_lifecycle_commands():
    text = render_beginner_step(4)
    assert "flows list" in text
    assert "flows install" in text
    assert "flows run" in text
    assert "flows approve" in text


def test_step_5_covers_delivery_and_billing():
    text = render_beginner_step(5)
    assert "client-report" in text
    assert "package-client-demo" in text


def test_all_referenced_kit_commands_exist_in_cli():
    from ai_automation_kit.cli import build_parser

    parser = build_parser()
    subparsers_action = next(
        action for action in parser._actions if hasattr(action, "choices") and action.choices
    )
    known_commands = set(subparsers_action.choices.keys())
    for step in BEGINNER_STEPS.values():
        for command in step["commands"]:
            if not command.startswith("ai-automation-kit "):
                continue
            subcommand = command.split()[1]
            assert subcommand in known_commands, f"unknown subcommand in guide: {subcommand}"


def test_render_beginner_step_rejects_out_of_range():
    with pytest.raises(ValueError):
        render_beginner_step(0)
    with pytest.raises(ValueError):
        render_beginner_step(6)


def test_output_is_polite_japanese_with_term_explanations():
    text = render_beginner_step(4)
    # です・ます調と、専門用語への一言説明（ドライラン）が含まれる。
    assert "ます" in text
    assert "ドライラン" in text
