"""Document parsing primitives for the public-first EvidenceOps MVP."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class ParseError(Exception):
    """A recoverable per-document parse failure."""

    document_id: str
    reason: str

    def __str__(self) -> str:
        return f"{self.document_id}: {self.reason}"


PASSTHROUGH_FIELDS = (
    "document_id",
    "source_id",
    "source_name",
    "source_type",
    "source_url",
    "retrieved_at",
    "ingested_at",
    "document_type",
    "title",
    "license_status",
    "is_public_source",
    "is_synthetic",
    "not_use_for",
    "mvp_role",
    "decision",
)


def stable_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_text(text: str) -> str:
    return "\n\n".join(" ".join(block.split()) for block in text.splitlines() if block.strip())


def parse_document(document: dict, *, parsed_at: str | None = None) -> dict:
    """Parse one normalized document-store record into a sectioned document.

    Day 4 intentionally keeps parsing conservative: one clean text section per
    input record. Later stages can split into finer chunks without losing source
    and license metadata.
    """

    document_id = str(document.get("document_id", "UNKNOWN_DOCUMENT"))
    text = normalize_text(str(document.get("text", "")))
    if not text:
        raise ParseError(document_id=document_id, reason="empty text cannot be parsed")

    section_path = document.get("section_path") or ["body"]
    if not isinstance(section_path, list):
        section_path = [str(section_path)]

    parsed_at_value = parsed_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    section_hash = stable_hash(f"{document_id}\n{text}")[:16]
    section = {
        "section_id": f"{document_id}::section::{section_hash}",
        "section_index": 0,
        "section_path": section_path,
        "heading": " / ".join(str(part) for part in section_path),
        "text": text,
        "char_start": 0,
        "char_end": len(text),
        "text_sha256": stable_hash(text),
    }

    parsed = {field: document.get(field) for field in PASSTHROUGH_FIELDS}
    parsed.update(
        {
            "parse_status": "parsed",
            "parsed_at": parsed_at_value,
            "section_count": 1,
            "char_count": len(text),
            "sections": [section],
        }
    )
    return parsed


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        row["_line_no"] = line_no
        rows.append(row)
    return rows


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    rows = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows)
    path.write_text((content + "\n") if content else "", encoding="utf-8")


def parse_documents(documents: Iterable[dict], *, parsed_at: str | None = None) -> tuple[list[dict], list[dict]]:
    parsed_docs: list[dict] = []
    errors: list[dict] = []
    parsed_at_value = parsed_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    for document in documents:
        try:
            parsed_docs.append(parse_document(document, parsed_at=parsed_at_value))
        except ParseError as exc:
            errors.append(
                {
                    "document_id": exc.document_id,
                    "source_id": document.get("source_id"),
                    "source_url": document.get("source_url"),
                    "document_type": document.get("document_type"),
                    "line_no": document.get("_line_no"),
                    "reason": exc.reason,
                    "parse_status": "error",
                    "parsed_at": parsed_at_value,
                }
            )

    return parsed_docs, errors


def build_parse_report(
    *,
    input_path: Path,
    parsed_output_path: Path,
    errors_output_path: Path,
    input_document_count: int,
    parsed_documents: list[dict],
    parse_errors: list[dict],
    parsed_at: str,
) -> dict:
    source_counts: dict[str, int] = {}
    synthetic_count = 0
    for document in parsed_documents:
        source_id = str(document.get("source_id", "unknown"))
        source_counts[source_id] = source_counts.get(source_id, 0) + 1
        synthetic_count += int(bool(document.get("is_synthetic")))

    return {
        "status": "ok",
        "parsed_at": parsed_at,
        "input_path": str(input_path),
        "parsed_output_path": str(parsed_output_path),
        "errors_output_path": str(errors_output_path),
        "input_document_count": input_document_count,
        "parsed_document_count": len(parsed_documents),
        "parse_error_count": len(parse_errors),
        "synthetic_document_count": synthetic_count,
        "public_document_count": len(parsed_documents) - synthetic_count,
        "source_counts": source_counts,
        "guardrails": [
            "source metadata is preserved",
            "license_status is preserved",
            "synthetic documents remain marked",
            "empty text becomes parse error instead of silent success",
            "no retrieval or LLM metric is produced in Day 4",
        ],
    }

