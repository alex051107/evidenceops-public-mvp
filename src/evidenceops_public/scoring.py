"""Evaluation scoring for retrieval and extraction gold sets."""

from __future__ import annotations

from datetime import datetime, timezone

from evidenceops_public.retriever import search_chunks


def safe_divide(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 6)


def extraction_key(row: dict) -> tuple[str, str, str]:
    return (
        str(row.get("chunk_id")),
        str(row.get("field_type")),
        str(row.get("field_value")),
    )


def score_retrieval_cases(cases: list[dict], chunks: list[dict]) -> dict:
    case_results: list[dict] = []
    status_correct = 0
    supported_cases = 0
    supported_hits = 0
    unsupported_cases = 0
    unsupported_correct = 0

    for case in cases:
        result = search_chunks(str(case["query"]), chunks, top_k=5)
        expected_status = case["expected_status"]
        expected_chunk_ids = set(case.get("expected_chunk_ids", []))
        actual_chunk_ids = {evidence.get("chunk_id") for evidence in result.get("evidence", [])}
        status_match = result["status"] == expected_status
        hit = bool(expected_chunk_ids & actual_chunk_ids) if expected_status == "supported" else result["status"] == "unsupported"

        status_correct += int(status_match)
        if expected_status == "supported":
            supported_cases += 1
            supported_hits += int(hit)
        else:
            unsupported_cases += 1
            unsupported_correct += int(result["status"] == "unsupported")

        case_results.append(
            {
                "case_id": case["case_id"],
                "query": case["query"],
                "expected_status": expected_status,
                "actual_status": result["status"],
                "expected_chunk_ids": sorted(expected_chunk_ids),
                "actual_chunk_ids": sorted(str(chunk_id) for chunk_id in actual_chunk_ids if chunk_id),
                "status_match": status_match,
                "hit": hit,
            }
        )

    return {
        "case_count": len(cases),
        "supported_case_count": supported_cases,
        "unsupported_case_count": unsupported_cases,
        "status_accuracy": safe_divide(status_correct, len(cases)),
        "supported_hit_rate": safe_divide(supported_hits, supported_cases),
        "unsupported_accuracy": safe_divide(unsupported_correct, unsupported_cases),
        "case_results": case_results,
    }


def score_extraction_cases(cases: list[dict], extractions: list[dict]) -> dict:
    actual_keys = {extraction_key(row) for row in extractions}
    case_results: list[dict] = []
    true_positive = 0
    true_negative = 0
    false_positive = 0
    false_negative = 0

    for case in cases:
        key = extraction_key(case)
        expected_present = bool(case["expected_present"])
        actual_present = key in actual_keys
        if expected_present and actual_present:
            true_positive += 1
        elif expected_present and not actual_present:
            false_negative += 1
        elif not expected_present and actual_present:
            false_positive += 1
        else:
            true_negative += 1

        case_results.append(
            {
                "case_id": case["case_id"],
                "chunk_id": case["chunk_id"],
                "field_type": case["field_type"],
                "field_value": case["field_value"],
                "expected_present": expected_present,
                "actual_present": actual_present,
                "match": expected_present == actual_present,
            }
        )

    correct = true_positive + true_negative
    return {
        "case_count": len(cases),
        "presence_accuracy": safe_divide(correct, len(cases)),
        "true_positive_count": true_positive,
        "true_negative_count": true_negative,
        "false_positive_count": false_positive,
        "false_negative_count": false_negative,
        "precision": safe_divide(true_positive, true_positive + false_positive),
        "recall": safe_divide(true_positive, true_positive + false_negative),
        "case_results": case_results,
    }


def build_eval_report(
    *,
    retrieval_cases: list[dict],
    chunks: list[dict],
    extraction_cases: list[dict],
    extractions: list[dict],
    evaluated_at: str | None = None,
) -> dict:
    evaluated_at_value = evaluated_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    retrieval_report = score_retrieval_cases(retrieval_cases, chunks)
    extraction_report = score_extraction_cases(extraction_cases, extractions)
    return {
        "status": "ok",
        "evaluated_at": evaluated_at_value,
        "dataset_size": {
            "retrieval_cases": len(retrieval_cases),
            "chunks": len(chunks),
            "extraction_cases": len(extraction_cases),
            "extractions": len(extractions),
        },
        "retrieval": retrieval_report,
        "extraction": extraction_report,
        "guardrails": [
            "metrics are valid only for this small project-local gold set",
            "report dataset size with every metric",
            "do not claim production quality or broad generalization",
        ],
    }

