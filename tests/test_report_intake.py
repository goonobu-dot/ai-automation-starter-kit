import builtins
import hashlib
import io
import struct
import sys
import types
import zipfile
from pathlib import Path

from ai_automation_kit.core import report_intake
from ai_automation_kit.core.report_intake import (
    MAX_FILE_BYTES,
    MAX_FILES,
    copy_approved_files,
    extract_text,
    inspect_sources,
)


def accepted_records(payload):
    return [record for record in payload["records"] if record["status"] == "accepted"]


def rejected_records(payload):
    return [record for record in payload["records"] if record["status"] == "rejected"]


def write_zip(path, files):
    with zipfile.ZipFile(path, "w") as archive:
        for name, content in files.items():
            archive.writestr(name, content)


def write_png(path, width=3, height=5):
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + struct.pack(">IIIIBBB", 13, 0x49484452, width, height, 8, 2, 0)
        + struct.pack(">I", 0)
        + struct.pack(">I", 0)
    )


def write_jpeg(path, width=7, height=11):
    path.write_bytes(
        b"\xff\xd8\xff\xc0\x00\x11\x08"
        + struct.pack(">HH", height, width)
        + b"\x03" + b"\x01\x11\x00\x02\x11\x00\x03\x11\x00"
        + b"\xff\xd9"
    )


def write_webp(path, width=13, height=17):
    payload = b"VP8X" + struct.pack("<I", 10) + b"\x00" * 4 + (width - 1).to_bytes(3, "little") + (height - 1).to_bytes(3, "little")
    path.write_bytes(b"RIFF" + struct.pack("<I", len(payload) + 4) + b"WEBP" + payload)


def test_public_limits_are_bounded_and_text_input_is_hashed_and_classified(tmp_path):
    assert MAX_FILE_BYTES == 10 * 1024 * 1024
    assert MAX_FILES == 200

    source = tmp_path / "2024_Q1_売上レポート.md"
    source.write_text("顧客別の売上と改善案", encoding="utf-8")
    before_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    before_mtime = source.stat().st_mtime_ns

    payload = inspect_sources([tmp_path], [], max_files=10)

    record = accepted_records(payload)[0]
    assert record["source_role"] == "past_output"
    assert record["text"] == "顧客別の売上と改善案"
    assert record["sha256"] == before_hash
    assert record["bytes"] == len(source.read_bytes())
    assert record["report_period"] == "2024-Q1"
    assert record["content_role"] == "sales"
    assert record["reason"] is None
    assert source.stat().st_mtime_ns == before_mtime
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before_hash


def test_recursive_discovery_rejects_symlinks_hidden_scripts_archives_and_unknown_binaries(tmp_path):
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "notes.txt").write_text("safe", encoding="utf-8")
    (nested / ".secret.txt").write_text("hidden", encoding="utf-8")
    (nested / "run.py").write_text("print('no')", encoding="utf-8")
    (nested / "bundle.zip").write_bytes(b"PK\x03\x04")
    (nested / "mystery.bin").write_bytes(b"\x00\x01\x02\xff")
    symlink = nested / "link.txt"
    symlink.symlink_to(nested / "notes.txt")

    payload = inspect_sources([tmp_path], [])
    reasons = {record["reason"] for record in rejected_records(payload)}
    assert len(accepted_records(payload)) == 1
    assert {"symlink", "hidden_file", "script_or_executable", "archive", "unknown_binary"} <= reasons


def test_shebang_disguised_text_files_are_rejected(tmp_path):
    for extension in (".txt", ".md"):
        path = tmp_path / ("script" + extension)
        path.write_text("#!/bin/sh\necho unsafe", encoding="utf-8")

        result = extract_text(path)

        assert result["status"] == "rejected"
        assert result["reason"] == "script_or_executable"


def test_size_count_and_missing_path_limits_are_explicit(tmp_path):
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    first.write_text("1", encoding="utf-8")
    second.write_text("2", encoding="utf-8")
    missing = tmp_path / "missing.txt"

    payload = inspect_sources(
        [first, second, missing],
        [],
        max_file_bytes=1,
        max_files=1,
    )
    assert len(accepted_records(payload)) == 1
    assert payload["truncated"] is True

    missing_payload = inspect_sources([missing], [], max_files=10)
    assert rejected_records(missing_payload)[0]["reason"] == "missing_path"

    oversized = tmp_path / "oversized.txt"
    oversized.write_text("too large", encoding="utf-8")
    oversized_payload = inspect_sources([oversized], [], max_file_bytes=3)
    assert rejected_records(oversized_payload)[0]["reason"] == "file_too_large"


def test_max_file_count_is_bounded_and_reports_truncation_as_metadata(tmp_path):
    for index in range(3):
        (tmp_path / "{}.txt".format(index)).write_text(str(index), encoding="utf-8")

    payload = inspect_sources([tmp_path], [], max_files=2)

    assert len(payload["records"]) == 2
    assert payload["truncated"] is True
    assert payload["counts"]["inspected"] == 2
    assert all(record.get("reason") != "max_files_exceeded" for record in payload["records"])


def test_hidden_directories_are_skipped_without_recursing(tmp_path):
    hidden = tmp_path / ".private"
    hidden.mkdir()
    (hidden / "secret.txt").write_text("secret", encoding="utf-8")
    (tmp_path / "visible.txt").write_text("visible", encoding="utf-8")

    payload = inspect_sources([tmp_path], [])

    assert [record["name"] for record in accepted_records(payload)] == ["visible.txt"]
    assert {item["reason"] for item in payload["skipped"]} == {"hidden_directory"}
    assert str(hidden) in {item["path"] for item in payload["skipped"]}


def test_accepted_content_is_deduplicated_across_source_roles(tmp_path):
    past = tmp_path / "past.txt"
    current = tmp_path / "current.txt"
    past.write_text("same", encoding="utf-8")
    current.write_text("same", encoding="utf-8")

    payload = inspect_sources([past], [current])

    assert len(accepted_records(payload)) == 1
    duplicates = [record for record in payload["records"] if record.get("reason") == "duplicate_content"]
    assert len(duplicates) == 1
    assert duplicates[0]["source_role"] == "current_material"


def test_docx_and_xlsx_are_extracted_with_stdlib_zip_xml(tmp_path):
    docx = tmp_path / "2023_summary.docx"
    write_zip(
        docx,
        {
            "word/document.xml": (
                '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                "<w:body><w:p><w:r><w:t>第一段</w:t></w:r></w:p>"
                "<w:p><w:r><w:t>Second paragraph</w:t></w:r></w:p></w:body></w:document>"
            )
        },
    )
    xlsx = tmp_path / "2023_metrics.xlsx"
    write_zip(
        xlsx,
        {
            "xl/sharedStrings.xml": (
                '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                "<si><t>Revenue</t></si><si><t>100</t></si></sst>"
            ),
            "xl/worksheets/sheet1.xml": (
                '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                '<sheetData><row><c r="A1" t="s"><v>0</v></c>'
                '<c r="B1" t="s"><v>1</v></c></row></sheetData></worksheet>'
            ),
        },
    )

    docx_result = extract_text(docx)
    xlsx_result = extract_text(xlsx)

    assert docx_result["extraction_status"] == "extracted"
    assert "第一段" in docx_result["text"] and "Second paragraph" in docx_result["text"]
    assert xlsx_result["extraction_status"] == "extracted"
    assert "Revenue" in xlsx_result["text"] and "100" in xlsx_result["text"]


def test_empty_or_unrelated_zip_files_are_not_documents(tmp_path):
    cases = {
        "empty.docx": {},
        "unrelated.docx": {"other/file.txt": "text"},
        "empty.xlsx": {},
        "unrelated.xlsx": {"other/file.txt": "text"},
    }

    for name, members in cases.items():
        path = tmp_path / name
        write_zip(path, members)

        result = extract_text(path)

        assert result["status"] == "rejected"
        assert result["reason"] == "invalid_container"


def test_valid_empty_documents_are_accepted_with_warning(tmp_path):
    docx = tmp_path / "empty.docx"
    write_zip(
        docx,
        {
            "word/document.xml": (
                '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                "<w:body/></w:document>"
            )
        },
    )
    xlsx = tmp_path / "empty.xlsx"
    write_zip(
        xlsx,
        {
            "xl/worksheets/sheet1.xml": (
                '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                "<sheetData/></worksheet>"
            )
        },
    )

    for path in (docx, xlsx):
        result = extract_text(path)
        assert result["status"] == "accepted"
        assert result["text"] == ""
        assert "empty_extracted_text" in result["warnings"]


def test_zip_declared_member_and_aggregate_limits_fail_without_large_allocations(tmp_path, monkeypatch):
    path = tmp_path / "declared.docx"
    path.write_bytes(b"small")

    class FakeArchive:
        def __init__(self, infos):
            self.infos = infos

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

        def infolist(self):
            return self.infos

        def getinfo(self, name):
            return next(info for info in self.infos if info.filename == name)

        def open(self, info, mode):
            return io.BytesIO(b"not reached")

    declared_large = types.SimpleNamespace(
        filename="word/document.xml",
        file_size=MAX_FILE_BYTES * report_intake.MAX_CONTAINER_MEMBER_BYTES_MULTIPLIER + 1,
    )
    monkeypatch.setattr(report_intake.zipfile, "ZipFile", lambda *args, **kwargs: FakeArchive([declared_large]))
    result = extract_text(path)
    assert result["reason"] == "expanded_content_too_large"
    assert "zip_member_size_limit" in result["warnings"]

    aggregate_infos = [
        types.SimpleNamespace(filename="word/document.xml", file_size=MAX_FILE_BYTES * 3),
        types.SimpleNamespace(filename="word/header.xml", file_size=MAX_FILE_BYTES * 3),
        types.SimpleNamespace(filename="word/footer.xml", file_size=MAX_FILE_BYTES * 3),
    ]
    monkeypatch.setattr(report_intake.zipfile, "ZipFile", lambda *args, **kwargs: FakeArchive(aggregate_infos))
    result = extract_text(path)
    assert result["reason"] == "expanded_content_too_large"
    assert "zip_total_size_limit" in result["warnings"]


def test_zip_member_count_and_extracted_text_limits_fail_boundedly(tmp_path, monkeypatch):
    path = tmp_path / "many.docx"
    path.write_bytes(b"small")

    class FakeArchive:
        def __init__(self, infos, contents=None):
            self.infos = infos
            self.contents = contents or {}

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

        def infolist(self):
            return self.infos

        def getinfo(self, name):
            return next(info for info in self.infos if info.filename == name)

        def open(self, info, mode):
            return io.BytesIO(self.contents[info.filename])

    many = [types.SimpleNamespace(filename="word/{:03d}.xml".format(index), file_size=1) for index in range(report_intake.MAX_CONTAINER_MEMBERS + 1)]
    monkeypatch.setattr(report_intake.zipfile, "ZipFile", lambda *args, **kwargs: FakeArchive(many))
    result = extract_text(path)
    assert result["reason"] == "expanded_content_too_large"
    assert "zip_member_count_limit" in result["warnings"]

    text_path = tmp_path / "long.docx"
    text_path.write_bytes(b"small")
    text = "x" * (100 * report_intake.MAX_CONTAINER_TEXT_BYTES_MULTIPLIER + 1)
    xml = (
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body><w:p><w:r><w:t>{}</w:t></w:r></w:p></w:body></w:document>".format(text)
    ).encode("utf-8")
    info = types.SimpleNamespace(filename="word/document.xml", file_size=len(xml))
    monkeypatch.setattr(report_intake.zipfile, "ZipFile", lambda *args, **kwargs: FakeArchive([info], {info.filename: xml}))
    result = extract_text(text_path, max_file_bytes=100)
    assert result["reason"] == "expanded_content_too_large"
    assert "extracted_text_size_limit" in result["warnings"]


def test_images_return_metadata_without_claiming_ocr(tmp_path):
    paths = [tmp_path / "one.png", tmp_path / "two.jpg", tmp_path / "three.webp"]
    write_png(paths[0])
    write_jpeg(paths[1])
    write_webp(paths[2])

    for path in paths:
        result = extract_text(path)
        assert result["extraction_status"] == "metadata_only"
        assert result["text"] is None
        assert result["metadata"]["width"] > 0
        assert result["metadata"]["height"] > 0
        assert any("ocr" in warning.lower() for warning in result["warnings"])


def test_malformed_binary_signatures_are_rejected(tmp_path):
    for extension in (".png", ".jpg", ".webp", ".pdf"):
        path = tmp_path / ("bad" + extension)
        path.write_bytes(b"not a valid binary file")

        result = extract_text(path)

        assert result["status"] == "rejected"
        assert result["reason"] == "invalid_format"


def test_invalid_utf8_and_executable_text_are_rejected(tmp_path):
    invalid_utf8 = tmp_path / "invalid.txt"
    invalid_utf8.write_bytes(b"\xff\xfe")
    executable = tmp_path / "executable.txt"
    executable.write_text("safe-looking", encoding="utf-8")
    executable.chmod(0o755)

    assert extract_text(invalid_utf8)["reason"] == "invalid_utf8"
    assert extract_text(executable)["reason"] == "script_or_executable"


def test_unreadable_and_malformed_containers_have_explicit_reasons(tmp_path, monkeypatch):
    unreadable = tmp_path / "unreadable.txt"
    unreadable.write_text("content", encoding="utf-8")
    malformed_docx = tmp_path / "broken.docx"
    malformed_docx.write_bytes(b"not a zip")
    malformed_xlsx = tmp_path / "broken.xlsx"
    malformed_xlsx.write_bytes(b"also not a zip")

    monkeypatch.setattr(report_intake, "_read_limited", lambda path, limit: (None, "unreadable"))
    assert extract_text(unreadable)["reason"] == "unreadable"
    monkeypatch.undo()

    assert extract_text(malformed_docx)["reason"] == "invalid_container"
    assert extract_text(malformed_xlsx)["reason"] == "invalid_container"


def test_pdf_reader_is_optional_and_does_not_add_a_dependency(tmp_path, monkeypatch):
    pdf = tmp_path / "report.pdf"
    pdf.write_bytes(b"%PDF-1.4\nnot a complete document\n%%EOF")
    real_import = builtins.__import__

    def missing_pypdf(name, *args, **kwargs):
        if name == "pypdf":
            raise ImportError("optional reader is absent")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", missing_pypdf)
    result = extract_text(pdf)

    assert result["extraction_status"] == "optional_reader_missing"
    assert result["text"] is None


def test_pdf_reader_returns_extracted_page_text_without_a_real_dependency(tmp_path, monkeypatch):
    pdf = tmp_path / "report.pdf"
    pdf.write_bytes(b"%PDF-1.4\nfake\n%%EOF")

    class FakePage:
        def __init__(self, text):
            self.text = text

        def extract_text(self):
            return self.text

    class FakeReader:
        def __init__(self, stream, strict=False):
            self.pages = [FakePage("page one"), FakePage("page two")]

    monkeypatch.setitem(sys.modules, "pypdf", types.SimpleNamespace(PdfReader=FakeReader))
    result = extract_text(pdf)

    assert result["status"] == "accepted"
    assert result["extraction_status"] == "extracted"
    assert result["text"] == "page one\npage two"


def test_copy_creates_nested_workspace_parents(tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("nested", encoding="utf-8")
    workspace = tmp_path / "one" / "two" / "workspace"

    outcomes = copy_approved_files(
        [{"status": "accepted", "source_role": "past_output", "original_path": str(source), "name": "nested.txt"}],
        workspace,
    )

    assert [item["status"] for item in outcomes] == ["copied"]
    assert (workspace / "00_intake" / "past" / "nested.txt").read_text(encoding="utf-8") == "nested"


def test_copy_requires_explicit_accepted_status(tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("content", encoding="utf-8")

    outcomes = copy_approved_files(
        [{"source_role": "past_output", "original_path": str(source), "name": "source.txt"}],
        tmp_path / "workspace",
    )

    assert outcomes == [{
        "status": "copy_rejected",
        "source_role": "past_output",
        "original_path": str(source),
        "name": "source.txt",
        "reason": "missing_status",
    }]


def test_copy_sanitizes_names_prevents_collisions_and_rejects_symlink_sources(tmp_path):
    source_a = tmp_path / "a.txt"
    source_b = tmp_path / "b.txt"
    source_a.write_text("A", encoding="utf-8")
    source_b.write_text("B", encoding="utf-8")
    linked = tmp_path / "linked.txt"
    linked.symlink_to(source_a)
    workspace = tmp_path / "workspace"

    records = [
        {"status": "accepted", "source_role": "past_output", "original_path": str(source_a), "name": "../same.txt", "sha256": hashlib.sha256(b"A").hexdigest(), "bytes": 1},
        {"status": "accepted", "source_role": "past_output", "original_path": str(source_b), "name": "same.txt", "sha256": hashlib.sha256(b"B").hexdigest(), "bytes": 1},
        {"status": "accepted", "source_role": "current_material", "original_path": str(linked), "name": "linked.txt", "sha256": hashlib.sha256(b"A").hexdigest(), "bytes": 1},
    ]

    outcomes = copy_approved_files(records, workspace)
    copied = [item for item in outcomes if item["status"] == "copied"]
    rejected = [item for item in outcomes if item["status"] == "copy_rejected"]

    assert len(copied) == 2
    assert len(rejected) == 1
    assert rejected[0]["reason"] == "symlink"
    copied_paths = [Path(item["copied_path"]) for item in copied]
    assert all(path.parent == workspace / "00_intake" / "past" for path in copied_paths)
    assert {path.name for path in copied_paths} == {"same.txt", "same__2.txt"}
    assert all(workspace / "00_intake" not in path.parents or path.resolve().is_relative_to(workspace.resolve()) for path in copied_paths)
    assert sorted(path.read_text(encoding="utf-8") for path in copied_paths) == ["A", "B"]


def test_copy_reports_missing_and_hash_mismatched_accepted_records(tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("actual", encoding="utf-8")
    workspace = tmp_path / "workspace"

    outcomes = copy_approved_files(
        [
            {"status": "accepted", "source_role": "past_output"},
            {"status": "accepted", "source_role": "past_output", "original_path": str(source), "name": "bad.txt", "sha256": "0" * 64},
        ],
        workspace,
    )

    assert [item["reason"] for item in outcomes if item["status"] == "copy_rejected"] == [
        "missing_original_path",
        "source_hash_mismatch",
    ]


def test_copy_fails_closed_when_source_parent_changes_to_symlink(tmp_path, monkeypatch):
    source_parent = tmp_path / "source-parent"
    source_parent.mkdir()
    source = source_parent / "source.txt"
    source.write_text("content", encoding="utf-8")
    moved_parent = tmp_path / "moved-source-parent"
    workspace = tmp_path / "workspace"
    original_open = report_intake._open_file_no_follow
    swapped = False

    def swap_parent_before_open(path):
        nonlocal swapped
        if Path(path) == source and not swapped:
            swapped = True
            source_parent.rename(moved_parent)
            source_parent.symlink_to(moved_parent, target_is_directory=True)
        return original_open(path)

    monkeypatch.setattr(report_intake, "_open_file_no_follow", swap_parent_before_open)
    try:
        outcomes = copy_approved_files(
            [{"status": "accepted", "source_role": "past_output", "original_path": str(source), "name": "source.txt"}],
            workspace,
        )
    finally:
        source_parent.unlink()
        moved_parent.rename(source_parent)

    assert outcomes[0]["status"] == "copy_rejected"
    assert outcomes[0]["reason"] == "unsafe_source_path"
    assert not (workspace / "00_intake" / "past" / "source.txt").exists()


def test_copy_fails_closed_when_destination_parent_changes_to_symlink(tmp_path, monkeypatch):
    source = tmp_path / "source.txt"
    source.write_text("content", encoding="utf-8")
    workspace = tmp_path / "workspace"
    destination_parent = workspace / "00_intake" / "past"
    moved_parent = tmp_path / "moved-destination-parent"
    original_open_directory = report_intake._open_directory_fd
    swapped = False

    def swap_destination_parent(path, create=False):
        nonlocal swapped
        if Path(path) == destination_parent and not create and not swapped:
            swapped = True
            destination_parent.rename(moved_parent)
            destination_parent.symlink_to(moved_parent, target_is_directory=True)
        return original_open_directory(path, create=create)

    monkeypatch.setattr(report_intake, "_open_directory_fd", swap_destination_parent)
    try:
        outcomes = copy_approved_files(
            [{"status": "accepted", "source_role": "past_output", "original_path": str(source), "name": "source.txt"}],
            workspace,
        )
    finally:
        destination_parent.unlink()
        moved_parent.rename(destination_parent)

    assert outcomes[0]["status"] == "copy_rejected"
    assert outcomes[0]["reason"] == "unsafe_destination_path"
    assert not (moved_parent / "source.txt").exists()


def test_copy_rejects_and_cleans_when_destination_directory_is_renamed_after_open(tmp_path, monkeypatch):
    source = tmp_path / "source.txt"
    source.write_text("content", encoding="utf-8")
    workspace = tmp_path / "workspace"
    destination_parent = workspace / "00_intake" / "past"
    moved_parent = tmp_path / "moved-destination-parent"
    original_open_directory = report_intake._open_directory_fd
    opened_and_renamed = False

    def rename_after_open(path, create=False):
        nonlocal opened_and_renamed
        descriptor = original_open_directory(path, create=create)
        if Path(path) == destination_parent and not create and not opened_and_renamed:
            opened_and_renamed = True
            destination_parent.rename(moved_parent)
            destination_parent.symlink_to(moved_parent, target_is_directory=True)
        return descriptor

    monkeypatch.setattr(report_intake, "_open_directory_fd", rename_after_open)
    try:
        outcomes = copy_approved_files(
            [{"status": "accepted", "source_role": "past_output", "original_path": str(source), "name": "source.txt"}],
            workspace,
        )
    finally:
        destination_parent.unlink()
        moved_parent.rename(destination_parent)

    assert outcomes[0]["status"] == "copy_rejected"
    assert outcomes[0]["reason"] == "destination_changed_during_copy"
    assert not (destination_parent / "source.txt").exists()


def test_copy_does_not_overwrite_existing_collision(tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("new", encoding="utf-8")
    workspace = tmp_path / "workspace"
    destination = workspace / "00_intake" / "current"
    destination.mkdir(parents=True)
    (destination / "report.txt").write_text("existing", encoding="utf-8")

    outcomes = copy_approved_files(
        [{"status": "accepted", "source_role": "current_material", "original_path": str(source), "name": "report.txt"}],
        workspace,
    )
    copied = [item for item in outcomes if item["status"] == "copied"]

    assert len(copied) == 1
    assert (destination / "report.txt").read_text(encoding="utf-8") == "existing"
    assert (destination / "report__2.txt").read_text(encoding="utf-8") == "new"
