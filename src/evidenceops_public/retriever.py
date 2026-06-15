"""Lexical retrieval baseline for citation-aware evidence chunks."""

from __future__ import annotations

import math
import re
from datetime import datetime, timezone


TOKEN_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_\-]*")


def tokenize(text: str) -> list[str]:
    return [match.group(0).lower() for match in TOKEN_RE.finditer(text)]


def score_chunk(query_terms: set[str], chunk: dict) -> float:
    chunk_terms = set(tokenize(str(chunk.get("text", ""))))
    if not query_terms or not chunk_terms:
        return 0.0
    overlap = query_terms & chunk_terms
    if not overlap:
        return 0.0
    return len(overlap) / math.sqrt(len(query_terms) * len(chunk_terms))


def search_chunks(query: str, chunks: list[dict], *, top_k: int = 5, searched_at: str | None = None) -> dict:
    searched_at_value = searched_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    query_terms = set(tokenize(query))
    if not query_terms:
        return {
            "status": "unsupported",
            "query": query,
            "searched_at": searched_at_value,
            "evidence_count": 0,
            "evidence": [],
            "reason": "No query terms were provided.",
        }

    scored: list[tuple[float, dict]] = []
    for chunk in chunks:
        score = score_chunk(query_terms, chunk)
        if score > 0:
            scored.append((score, chunk))
    scored.sort(key=lambda item: (-item[0], str(item[1].get("chunk_id", ""))))
    top_matches = scored[:top_k]

    if not top_matches:
        return {
            "status": "unsupported",
            "query": query,
            "searched_at": searched_at_value,
            "evidence_count": 0,
            "evidence": [],
            "reason": "No chunk matched the query terms. Return unsupported instead of fabricating evidence.",
        }

    evidence = []
    for rank, (score, chunk) in enumerate(top_matches, start=1):
        evidence.append(
            {
                "rank": rank,
                "score": round(score, 6),
                "chunk_id": chunk.get("chunk_id"),
                "document_id": chunk.get("document_id"),
                "section_id": chunk.get("section_id"),
                "source_id": chunk.get("source_id"),
                "source_url": chunk.get("source_url"),
                "license_status": chunk.get("license_status"),
                "is_synthetic": chunk.get("is_synthetic"),
                "text": chunk.get("text"),
                "not_use_for": chunk.get("not_use_for", []),
                "citation": chunk.get("citation", {}),
            }
        )

    return {
        "status": "supported",
        "query": query,
        "searched_at": searched_at_value,
        "retrieval_method": "lexical_term_overlap",
        "top_k": top_k,
        "evidence_count": len(evidence),
        "evidence": evidence,
        "guardrails": [
            "results are evidence chunks, not generated answers",
            "citation metadata is returned with each chunk",
            "no recall@k claim is made without a gold set",
        ],
    }

