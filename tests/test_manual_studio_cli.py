from ai_automation_kit.cli import build_parser


def test_parser_accepts_manual_studio_commands():
    parser = build_parser()

    create = parser.parse_args(
        ["manual-studio", "create", "--output", "manual", "--name", "Invoice entry", "--language", "en"]
    )
    assert create.command == "manual-studio"
    assert create.manual_studio_command == "create"

    prepare = parser.parse_args(
        ["manual-studio", "prepare", "--workspace", "manual", "--transcribe", "--transcription-model", "small"]
    )
    assert prepare.manual_studio_command == "prepare"

    build = parser.parse_args(
        ["manual-studio", "build", "--workspace", "manual", "--title", "Invoice entry", "--open"]
    )
    assert build.manual_studio_command == "build"

    questions = parser.parse_args(["manual-studio", "questions", "--workspace", "manual", "--json"])
    assert questions.manual_studio_command == "questions"

    answer = parser.parse_args(
        [
            "manual-studio",
            "answer",
            "--workspace",
            "manual",
            "--answer",
            "220 degrees for 18 minutes",
            "--source-kind",
            "document",
            "--source",
            "Standard B-12",
            "--answered-by",
            "Process owner",
        ]
    )
    assert answer.manual_studio_command == "answer"

    complete = parser.parse_args(
        ["manual-studio", "complete", "--workspace", "manual", "--title", "Invoice entry"]
    )
    assert complete.manual_studio_command == "complete"

    approve = parser.parse_args(
        ["manual-studio", "approve", "--workspace", "manual", "--approved-by", "Process owner"]
    )
    assert approve.manual_studio_command == "approve"

    status = parser.parse_args(["manual-studio", "status", "--workspace", "manual", "--json"])
    assert status.manual_studio_command == "status"
