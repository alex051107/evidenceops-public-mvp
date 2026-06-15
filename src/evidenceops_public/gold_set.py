"""Build small auditable gold sets from current chunks and extractions."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone


RETRIEVAL_QUERY_TEMPLATES = (
    "source license metadata",
    "citation metadata",
    "synthetic evidence",
    "skill taxonomy",
    "software skills",
    "public filing history",
    "registered GET JSON",
    "text mining eligible",
    "human review unsupported claims",
    "bioactivity downloads",
)

UNSUPPORTED_QUERIES = (
    "astrophysics volcano telescope",
    "patient diagnosis insulin dose",
    "private customer revenue forecast",
    "hipaa compliant production deployment",
    "stock investment recommendation",
    "unpublished ligamd trajectory",
)

NEGATIVE_FIELD_VALUES = (
    ("skill_signal", "clinical diagnosis"),
    ("skill_signal", "production deployment"),
    ("workflow_signal", "high concurrency cluster"),
    ("workflow_signal", "patient treatment advice"),
    ("source_constraint", "real customer data"),
    ("source_constraint", "hipaa compliance"),
)


def stable_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def case_id(prefix: str, payload: str, index: int) -> str:
    return f"{prefix}_{index:03d}_{stable_hash(payload)[:10]}"


def chunk_matches_query(chunk: dict, query: str) -> bool:
    text = str(chunk.get("text", "")).lower()
    return any(term in text for term in query.lower().split())


def build_retrieval_cases(chunks: list[dict], *, minimum_cases: int = 20) -> list[dict]:
    cases: list[dict] = []
    index = 1

    for query in RETRIEVAL_QUERY_TEMPLATES:
        expected_ids = [chunk["chunk_id"] for chunk in chunks if chunk_matches_query(chunk, query)]
        if not expected_ids:
            continue
        cases.append(
            {
                "case_id": case_id("retrieval", query, index),
                "task_type": "retrieval",
                "query": query,
                "expected_status": "supported",
                "expected_chunk_ids": expected_ids,
                "expected_source_ids": sorted({chunk["source_id"] for chunk in chunks if chunk["chunk_id"] in expected_ids}),
                "citation_required": True,
                "notes": "Generated from current audited chunks; manually review before using as a resume metric.",
            }
        )
        index += 1

    for query in UNSUPPORTED_QUERIES:
        cases.append(
            {
                "case_id": case_id("retrieval", query, index),
                "task_type": "retrieval",
                "query": query,
                "expected_status": "unsupported",
                "expected_chunk_ids": [],
                "expected_source_ids": [],
                "citation_required": False,
                "notes": "Negative query should not fabricate evidence.",
            }
        )
        index += 1

    seed_queries = [case["query"] for case in cases] or ["source"]
    while len(cases) < minimum_cases:
        base_query = seed_queries[len(cases) % len(seed_queries)]
        query = f"{base_query} case {len(cases) + 1}"
        expected_ids = [chunk["chunk_id"] for chunk in chunks if chunk_matches_query(chunk, base_query)]
        cases.append(
            {
                "case_id": case_id("retrieval", query, index),
                "task_type": "retrieval",
                "query": query,
                "expected_status": "supported" if expected_ids else "unsupported",
                "expected_chunk_ids": expected_ids,
                "expected_source_ids": sorted({chunk["source_id"] for chunk in chunks if chunk["chunk_id"] in expected_ids}),
                "citation_required": bool(expected_ids),
                "notes": "Padded deterministic audit case; manually review before reporting metrics externally.",
            }
        )
        index += 1

    return cases


def build_extraction_cases(chunks: list[dict], extractions: list[dict], *, minimum_cases: int = 50) -> list[dict]:
    chunk_by_id = {chunk["chunk_id"]: chunk for chunk in chunks}
    cases: list[dict] = []
    index = 1

    for extraction in extractions:
        chunk = chunk_by_id.get(extraction.get("chunk_id"), {})
        payload = f"{extraction.get('chunk_id')}:{extraction.get('field_type')}:{extraction.get('field_value')}"
        cases.append(
            {
                "case_id": case_id("extract", payload, index),
                "task_type": "extraction",
                "chunk_id": extraction.get("chunk_id"),
                "document_id": extraction.get("document_id") or chunk.get("document_id"),
                "source_id": extraction.get("source_id") or chunk.get("source_id"),
                "field_type": extraction.get("field_type"),
                "field_value": extraction.get("field_value"),
                "expected_present": True,
                "evidence_span": extraction.get("evidence_span"),
                "citation": extraction.get("citation") or chunk.get("citation", {}),
                "notes": "Positive case from current extractor output; manually review before external reporting.",
            }
        )
        index += 1

    chunk_ids = [chunk["chunk_id"] for chunk in chunks]
    if not chunk_ids:
        return cases

    while len(cases) < minimum_cases:
        chunk = chunks[len(cases) % len(chunks)]
        field_type, field_value = NEGATIVE_FIELD_VALUES[len(cases) % len(NEGATIVE_FIELD_VALUES)]
        payload = f"{chunk['chunk_id']}:{field_type}:{field_value}:negative:{len(cases)}"
        cases.append(
            {
                "case_id": case_id("extract", payload, index),
                "task_type": "extraction",
                "chunk_id": chunk["chunk_id"],
                "document_id": chunk.get("document_id"),
                "source_id": chunk.get("source_id"),
                "field_type": field_type,
                "field_value": field_value,
                "expected_present": False,
                "evidence_span": "",
                "citation": chunk.get("citation", {}),
                "notes": "Negative case; field should not be extracted from this chunk.",
            }
        )
        index += 1

    return cases


def build_gold_sets(chunks: list[dict], extractions: list[dict], *, built_at: str | None = None) -> tuple[list[dict], list[dict], dict]:
    built_at_value = built_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    retrieval_cases = build_retrieval_cases(chunks)
    extraction_cases = build_extraction_cases(chunks, extractions)
    manifest = {
        "status": "ok",
        "built_at": built_at_value,
        "retrieval_case_count": len(retrieval_cases),
        "extraction_case_count": len(extraction_cases),
        "positive_extraction_case_count": sum(1 for case in extraction_cases if case["expected_present"] is True),
        "negative_extraction_case_count": sum(1 for case in extraction_cases if case["expected_present"] is False),
        "supported_retrieval_case_count": sum(1 for case in retrieval_cases if case["expected_status"] == "supported"),
        "unsupported_retrieval_case_count": sum(1 for case in retrieval_cases if case["expected_status"] == "unsupported"),
        "guardrails": [
            "gold set is small and project-local",
            "metrics from this set must report dataset size",
            "cases are generated from audited chunks and require manual review before resume use",
            "no claim of broad production quality is implied",
        ],
    }
    return retrieval_cases, extraction_cases, manifest

