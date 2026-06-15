"""Chunk parsed documents while preserving citation metadata."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class ChunkingError(Exception):
    document_id: str
    reason: str

    def __str__(self) -> str:
        return f"{self.document_id}: {self.reason}"


TOKEN_RE = re.compile(r"\S+")


def stable_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def iter_word_windows(word_count: int, max_words: int, overlap_words: int) -> list[tuple[int, int]]:
    if max_words <= 0:
        raise ValueError("max_words must be positive")
    if overlap_words < 0:
        raise ValueError("overlap_words must be non-negative")
    if overlap_words >= max_words:
        raise ValueError("overlap_words must be smaller than max_words")

    windows: list[tuple[int, int]] = []
    start = 0
    step = max_words - overlap_words
    while start < word_count:
        end = min(word_count, start + max_words)
        windows.append((start, end))
        if end == word_count:
            break
        start += step
    return windows


def chunk_document(
    parsed_document: dict,
    *,
    max_words: int = 120,
    overlap_words: int = 20,
    chunked_at: str | None = None,
) -> list[dict]:
    document_id = str(parsed_document.get("document_id", "UNKNOWN_DOCUMENT"))
    try:
        windows_probe = iter_word_windows(1, max_words, overlap_words)
    except ValueError as exc:
        raise ChunkingError(document_id=document_id, reason=str(exc)) from exc
    if not windows_probe:
        raise ChunkingError(document_id=document_id, reason="invalid chunking window")

    chunked_at_value = chunked_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    chunks: list[dict] = []
    global_chunk_index = 0

    for section in parsed_document.get("sections", []):
        section_text = str(section.get("text", "")).strip()
        if not section_text:
            continue
        matches = list(TOKEN_RE.finditer(section_text))
        if not matches:
            continue
        section_char_start = int(section.get("char_start", 0))
        for start_word, end_word in iter_word_windows(len(matches), max_words, overlap_words):
            selected = matches[start_word:end_word]
            chunk_text = " ".join(match.group(0) for match in selected)
            absolute_start = section_char_start + selected[0].start()
            absolute_end = section_char_start + selected[-1].end()
            chunk_hash = stable_hash(
                f"{document_id}\n{section.get('section_id')}\n{start_word}\n{end_word}\n{chunk_text}"
            )[:16]
            citation = {
                "document_id": document_id,
                "section_id": section.get("section_id"),
                "source_id": parsed_document.get("source_id"),
                "source_name": parsed_document.get("source_name"),
                "source_url": parsed_document.get("source_url"),
                "license_status": parsed_document.get("license_status"),
                "char_start": absolute_start,
                "char_end": absolute_end,
                "retrieved_at": parsed_document.get("retrieved_at"),
                "is_synthetic": parsed_document.get("is_synthetic"),
            }
            chunks.append(
                {
                    "chunk_id": f"{document_id}::chunk::{chunk_hash}",
                    "chunk_index": global_chunk_index,
                    "document_id": document_id,
                    "section_id": section.get("section_id"),
                    "section_path": section.get("section_path", []),
                    "source_id": parsed_document.get("source_id"),
                    "source_name": parsed_document.get("source_name"),
                    "source_type": parsed_document.get("source_type"),
                    "source_url": parsed_document.get("source_url"),
                    "license_status": parsed_document.get("license_status"),
                    "is_public_source": parsed_document.get("is_public_source"),
                    "is_synthetic": parsed_document.get("is_synthetic"),
                    "document_type": parsed_document.get("document_type"),
                    "title": parsed_document.get("title"),
                    "text": chunk_text,
                    "text_sha256": stable_hash(chunk_text),
                    "word_start": start_word,
                    "word_end": end_word,
                    "char_start": absolute_start,
                    "char_end": absolute_end,
                    "max_words": max_words,
                    "overlap_words": overlap_words,
                    "not_use_for": parsed_document.get("not_use_for", []),
                    "chunked_at": chunked_at_value,
                    "citation": citation,
                }
            )
            global_chunk_index += 1

    if not chunks:
        raise ChunkingError(document_id=document_id, reason="no non-empty sections to chunk")
    return chunks


def chunk_documents(
    parsed_documents: list[dict],
    *,
    max_words: int = 120,
    overlap_words: int = 20,
    chunked_at: str | None = None,
) -> tuple[list[dict], list[dict]]:
    chunked_at_value = chunked_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    chunks: list[dict] = []
    errors: list[dict] = []

    for document in parsed_documents:
        try:
            chunks.extend(
                chunk_document(
                    document,
                    max_words=max_words,
                    overlap_words=overlap_words,
                    chunked_at=chunked_at_value,
                )
            )
        except ChunkingError as exc:
            errors.append(
                {
                    "document_id": exc.document_id,
                    "source_id": document.get("source_id"),
                    "source_url": document.get("source_url"),
                    "reason": exc.reason,
                    "chunk_status": "error",
                    "chunked_at": chunked_at_value,
                }
            )
    return chunks, errors


def build_chunk_report(
    *,
    input_path: Path,
    chunks_output_path: Path,
    input_document_count: int,
    chunks: list[dict],
    chunk_errors: list[dict],
    max_words: int,
    overlap_words: int,
    chunked_at: str,
) -> dict:
    source_counts: dict[str, int] = {}
    synthetic_count = 0
    for chunk in chunks:
        source_id = str(chunk.get("source_id", "unknown"))
        source_counts[source_id] = source_counts.get(source_id, 0) + 1
        synthetic_count += int(bool(chunk.get("is_synthetic")))

    return {
        "status": "ok",
        "chunked_at": chunked_at,
        "input_path": str(input_path),
        "chunks_output_path": str(chunks_output_path),
        "input_document_count": input_document_count,
        "chunk_count": len(chunks),
        "chunk_error_count": len(chunk_errors),
        "synthetic_chunk_count": synthetic_count,
        "public_chunk_count": len(chunks) - synthetic_count,
        "source_counts": source_counts,
        "max_words": max_words,
        "overlap_words": overlap_words,
        "guardrails": [
            "citation metadata is attached to every chunk",
            "source_url and license_status are preserved",
            "synthetic chunks remain marked",
            "no embedding or retrieval metric is produced in Day 5",
        ],
    }

