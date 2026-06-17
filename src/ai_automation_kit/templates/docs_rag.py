from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from ai_automation_kit.core.models import Artifact, RunRecord, SourceRecord
from ai_automation_kit.core.store import JsonRunStore

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "can",
    "for",
    "how",
    "is",
    "of",
    "the",
    "to",
    "what",
    "when",
    "where",
    "who",
    "why",
    "with",
}


def run_docs_rag(config_path: Path | str, output_dir: Path | str) -> RunRecord:
    config_file = Path(config_path)
    output = Path(output_dir)
    config = json.loads(config_file.read_text(encoding="utf-8"))
    question = config["question"]
    documents = config.get("documents", [])

    started_at = _now()
    run_id = f"run-{uuid4().hex[:12]}"
    store = JsonRunStore(output)
    chunks: list[dict] = []
    source_map: list[dict] = []
    source_ids: list[str] = []

    for index, document in enumerate(documents, start=1):
        path = Path(document["path"])
        title = document.get("title") or path.stem
        text = path.read_text(encoding="utf-8")
        source_id = f"doc-{index:03d}-{hashlib.sha256(str(path).encode('utf-8')).hexdigest()[:8]}"
        normalized_path = _write_normalized_document(output, source_id, title, path, text)
        record = SourceRecord(
            source_id=source_id,
            source_type="document",
            uri=str(path),
            title=title,
            retrieved_at=_now(),
            content_hash=hashlib.sha256(text.encode("utf-8")).hexdigest(),
            raw_path=str(path),
            markdown_path=str(normalized_path.relative_to(output)),
            metadata={"rank": index, "format": path.suffix.lstrip(".") or "markdown"},
        )
        store.save_source(record)
        source_ids.append(source_id)
        source_map.append(record.to_dict())
        for chunk_index, chunk_text in enumerate(_chunk_markdown(text), start=1):
            chunks.append(
                {
                    "chunk_id": f"{source_id}-chunk-{chunk_index:03d}",
                    "source_id": source_id,
                    "title": title,
                    "path": str(path),
                    "text": chunk_text,
                }
            )

    selected = _select_best_chunk(question, chunks)
    answer = _answer_from_chunk(question, selected)
    artifacts = _write_docs_rag_artifacts(output, question, answer, chunks, source_map)
    finished_at = _now()
    run = RunRecord(
        run_id=run_id,
        template_name="docs-rag",
        input={"question": question, "document_count": len(documents)},
        started_at=started_at,
        finished_at=finished_at,
        status="succeeded",
        errors=[],
        artifacts=artifacts,
        source_ids=source_ids,
    )
    store.save_run(run)
    return run


def _chunk_markdown(text: str) -> list[str]:
    blocks = [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip()]
    return blocks or [text.strip()]


def _select_best_chunk(question: str, chunks: list[dict]) -> dict | None:
    question_terms = _terms(question)
    best: tuple[int, dict | None] = (0, None)
    for chunk in chunks:
        overlap = len(question_terms & _terms(chunk["text"]))
        if overlap > best[0]:
            best = (overlap, chunk)
    return best[1] if best[0] >= 2 else None


def _answer_from_chunk(question: str, chunk: dict | None) -> dict:
    if chunk is None:
        return {
            "question": question,
            "answer": "Insufficient evidence: no document chunk matched the question strongly enough.",
            "grounded": False,
            "confidence": "low",
            "citations": [],
            "next_actions": [
                "Add more source documents or refine the question.",
                "Do not use this answer for customer or production decisions until evidence is available.",
            ],
        }
    sentence = _first_sentence(chunk["text"])
    return {
        "question": question,
        "answer": sentence,
        "grounded": True,
        "confidence": "high",
        "citations": [
            {
                "title": chunk["title"],
                "path": chunk["path"],
                "chunk_id": chunk["chunk_id"],
            }
        ],
        "next_actions": [
            "Review the cited source before using this answer in production.",
            "If the answer affects customers, route it through an approval workflow.",
        ],
    }


def _write_docs_rag_artifacts(
    output: Path,
    question: str,
    answer: dict,
    chunks: list[dict],
    source_map: list[dict],
) -> list[Artifact]:
    output.mkdir(parents=True, exist_ok=True)
    answer_md = _render_answer_markdown(question, answer)
    (output / "answer.md").write_text(answer_md, encoding="utf-8")
    (output / "answer.json").write_text(json.dumps(answer, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (output / "chunks.jsonl").open("w", encoding="utf-8") as handle:
        for chunk in chunks:
            handle.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    (output / "source_map.json").write_text(json.dumps({"sources": source_map}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return [
        Artifact(kind="markdown", path="answer.md"),
        Artifact(kind="json", path="answer.json"),
        Artifact(kind="chunks", path="chunks.jsonl"),
        Artifact(kind="source_map", path="source_map.json"),
    ]


def _render_answer_markdown(question: str, answer: dict) -> str:
    lines = ["# Docs RAG Answer", "", f"## Question", "", question, "", "## Answer", "", answer["answer"], ""]
    lines.extend(["## Grounding", "", f"- Grounded: `{str(answer['grounded']).lower()}`"])
    lines.extend(["", "## Confidence", "", f"- `{answer.get('confidence', 'unknown')}`"])
    citations = answer.get("citations") or []
    if citations:
        for citation in citations:
            lines.append(f"- {citation['title']} ({citation['path']}) - `{citation['chunk_id']}`")
    else:
        lines.append("- No citations")
    lines.extend(["", "## Next Actions", ""])
    for action in answer.get("next_actions", []):
        lines.append(f"- {action}")
    lines.append("")
    return "\n".join(lines)


def _write_normalized_document(output: Path, source_id: str, title: str, path: Path, text: str) -> Path:
    normalized = output / "sources" / "markdown" / f"{source_id}.md"
    normalized.parent.mkdir(parents=True, exist_ok=True)
    normalized.write_text(f"# {title}\n\nSource: {path}\n\n{text}\n", encoding="utf-8")
    return normalized


def _terms(text: str) -> set[str]:
    return {term for term in re.findall(r"[a-zA-Z0-9]+", text.lower()) if term not in STOPWORDS and len(term) > 1}


def _first_sentence(text: str) -> str:
    cleaned = " ".join(line.strip("# ").strip() for line in text.splitlines() if line.strip())
    match = re.search(r"(.+?[.!?。])(?:\s|$)", cleaned)
    return match.group(1) if match else cleaned[:240]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
