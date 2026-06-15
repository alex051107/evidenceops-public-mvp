"""Small rule-based structured extraction for evidence chunks."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path


EXTRACTION_RULES: tuple[tuple[str, str], ...] = (
    ("skill_signal", "skill taxonomy"),
    ("skill_signal", "software skills"),
    ("workflow_signal", "source-backed evidence"),
    ("workflow_signal", "citation metadata"),
    ("workflow_signal", "unsupported claims"),
    ("workflow_signal", "human review"),
    ("workflow_signal", "metadata"),
    ("source_constraint", "license"),
    ("source_constraint", "not as"),
    ("source_constraint", "only"),
)


def stable_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def find_case_insensitive_span(text: str, phrase: str) -> tuple[int, int] | None:
    start = text.lower().find(phrase.lower())
    if start < 0:
        return None
    return start, start + len(phrase)


def extract_chunk(chunk: dict, *, extracted_at: str | None = None) -> list[dict]:
    text = str(chunk.get("text", ""))
    extracted_at_value = extracted_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    extractions: list[dict] = []

    for field_type, phrase in EXTRACTION_RULES:
        span = find_case_insensitive_span(text, phrase)
        if span is None:
            continue
        start, end = span
        evidence_span = text[start:end]
        extraction_hash = stable_hash(f"{chunk.get('chunk_id')}\n{field_type}\n{phrase}\n{start}\n{end}")[:16]
        extractions.append(
            {
                "extraction_id": f"{chunk.get('chunk_id')}::extract::{extraction_hash}",
                "chunk_id": chunk.get("chunk_id"),
                "document_id": chunk.get("document_id"),
                "section_id": chunk.get("section_id"),
                "source_id": chunk.get("source_id"),
                "source_url": chunk.get("source_url"),
                "license_status": chunk.get("license_status"),
                "is_synthetic": chunk.get("is_synthetic"),
                "field_type": field_type,
                "field_value": phrase,
                "evidence_span": evidence_span,
                "evidence_char_start": start,
                "evidence_char_end": end,
                "rule_name": f"phrase::{phrase}",
                "extracted_at": extracted_at_value,
                "citation": chunk.get("citation", {}),
                "not_use_for": chunk.get("not_use_for", []),
            }
        )

    return extractions


def extract_chunks(chunks: list[dict], *, extracted_at: str | None = None) -> tuple[list[dict], list[dict]]:
    extracted_at_value = extracted_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    rows: list[dict] = []
    unmatched: list[dict] = []

    for chunk in chunks:
        chunk_rows = extract_chunk(chunk, extracted_at=extracted_at_value)
        if chunk_rows:
            rows.extend(chunk_rows)
        else:
            unmatched.append(
                {
                    "chunk_id": chunk.get("chunk_id"),
                    "document_id": chunk.get("document_id"),
                    "source_id": chunk.get("source_id"),
                    "reason": "no extraction rule matched",
                    "extracted_at": extracted_at_value,
                }
            )
    return rows, unmatched


def build_extraction_report(
    *,
    chunks_path: Path,
    output_path: Path,
    input_chunk_count: int,
    extractions: list[dict],
    unmatched_chunks: list[dict],
    extracted_at: str,
) -> dict:
    field_type_counts: dict[str, int] = {}
    source_counts: dict[str, int] = {}
    synthetic_count = 0
    for row in extractions:
        field_type = str(row.get("field_type", "unknown"))
        source_id = str(row.get("source_id", "unknown"))
        field_type_counts[field_type] = field_type_counts.get(field_type, 0) + 1
        source_counts[source_id] = source_counts.get(source_id, 0) + 1
        synthetic_count += int(bool(row.get("is_synthetic")))

    matched_chunk_ids = {row.get("chunk_id") for row in extractions}
    return {
        "status": "ok",
        "extracted_at": extracted_at,
        "chunks_path": str(chunks_path),
        "output_path": str(output_path),
        "input_chunk_count": input_chunk_count,
        "matched_chunk_count": len(matched_chunk_ids),
        "unmatched_chunk_count": len(unmatched_chunks),
        "extraction_count": len(extractions),
        "synthetic_extraction_count": synthetic_count,
        "public_extraction_count": len(extractions) - synthetic_count,
        "field_type_counts": field_type_counts,
        "source_counts": source_counts,
        "guardrails": [
            "only rule-matched fields are extracted",
            "each extraction has evidence_span and citation",
            "no LLM-generated missing field is fabricated",
            "no extraction quality metric is claimed without a gold set",
        ],
    }

