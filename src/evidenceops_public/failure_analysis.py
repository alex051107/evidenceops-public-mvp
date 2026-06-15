"""Failure taxonomy and lightweight ablation analysis."""

from __future__ import annotations

from datetime import datetime, timezone

from evidenceops_public.scoring import score_retrieval_cases


FAILURE_TYPES = (
    "retrieval_miss",
    "unsupported_false_positive",
    "retrieval_status_mismatch",
    "extraction_false_negative",
    "extraction_false_positive",
)


def build_failure_taxonomy(eval_report: dict, *, analyzed_at: str | None = None) -> dict:
    analyzed_at_value = analyzed_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    counts = {failure_type: 0 for failure_type in FAILURE_TYPES}
    examples = {failure_type: [] for failure_type in FAILURE_TYPES}
    failed_case_ids: set[str] = set()

    for result in eval_report.get("retrieval", {}).get("case_results", []):
        expected_status = result.get("expected_status")
        actual_status = result.get("actual_status")
        hit = bool(result.get("hit"))
        if expected_status == "supported" and not hit:
            counts["retrieval_miss"] += 1
            examples["retrieval_miss"].append(result)
            failed_case_ids.add(str(result.get("case_id")))
        if expected_status == "unsupported" and actual_status == "supported":
            counts["unsupported_false_positive"] += 1
            examples["unsupported_false_positive"].append(result)
            failed_case_ids.add(str(result.get("case_id")))
        if expected_status != actual_status:
            counts["retrieval_status_mismatch"] += 1
            examples["retrieval_status_mismatch"].append(result)
            failed_case_ids.add(str(result.get("case_id")))

    for result in eval_report.get("extraction", {}).get("case_results", []):
        expected_present = bool(result.get("expected_present"))
        actual_present = bool(result.get("actual_present"))
        if expected_present and not actual_present:
            counts["extraction_false_negative"] += 1
            examples["extraction_false_negative"].append(result)
            failed_case_ids.add(str(result.get("case_id")))
        if not expected_present and actual_present:
            counts["extraction_false_positive"] += 1
            examples["extraction_false_positive"].append(result)
            failed_case_ids.add(str(result.get("case_id")))

    total_events = sum(counts.values())
    return {
        "status": "ok",
        "analyzed_at": analyzed_at_value,
        "failure_counts": counts,
        "total_failure_count": len(failed_case_ids),
        "total_failure_event_count": total_events,
        "examples": {key: value[:5] for key, value in examples.items()},
        "taxonomy_notes": {
            "retrieval_miss": "Expected a supported chunk but retrieval did not hit any expected chunk.",
            "unsupported_false_positive": "Expected unsupported but retrieval returned evidence.",
            "retrieval_status_mismatch": "Predicted supported/unsupported status differed from expected status.",
            "extraction_false_negative": "Expected field was not extracted.",
            "extraction_false_positive": "Unexpected field was extracted.",
        },
    }


def score_retrieval_cases_with_top_k(cases: list[dict], chunks: list[dict], top_k: int) -> dict:
    from evidenceops_public import retriever as retriever_module

    original_search = retriever_module.search_chunks

    def search_with_fixed_top_k(query: str, chunk_rows: list[dict], *, top_k: int = 5, searched_at: str | None = None) -> dict:
        return original_search(query, chunk_rows, top_k=top_k, searched_at=searched_at)

    # Reimplement a small top-k-aware scoring loop instead of monkeypatching.
    case_results = []
    status_correct = 0
    supported_cases = 0
    supported_hits = 0
    unsupported_cases = 0
    unsupported_correct = 0
    for case in cases:
        result = search_with_fixed_top_k(str(case["query"]), chunks, top_k=top_k)
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

    def safe_divide(numerator: int, denominator: int) -> float:
        return round(numerator / denominator, 6) if denominator else 0.0

    return {
        "case_count": len(cases),
        "supported_case_count": supported_cases,
        "unsupported_case_count": unsupported_cases,
        "status_accuracy": safe_divide(status_correct, len(cases)),
        "supported_hit_rate": safe_divide(supported_hits, supported_cases),
        "unsupported_accuracy": safe_divide(unsupported_correct, unsupported_cases),
        "case_results": case_results,
    }


def run_retrieval_topk_ablation(
    cases: list[dict],
    chunks: list[dict],
    *,
    top_k_values: list[int] | None = None,
    analyzed_at: str | None = None,
) -> dict:
    analyzed_at_value = analyzed_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    top_k_values = top_k_values or [1, 3, 5]
    runs = []
    for top_k in top_k_values:
        report = score_retrieval_cases_with_top_k(cases, chunks, top_k)
        runs.append(
            {
                "top_k": top_k,
                "case_count": report["case_count"],
                "status_accuracy": report["status_accuracy"],
                "supported_hit_rate": report["supported_hit_rate"],
                "unsupported_accuracy": report["unsupported_accuracy"],
            }
        )

    return {
        "status": "ok",
        "analyzed_at": analyzed_at_value,
        "dataset_size": {
            "retrieval_cases": len(cases),
            "chunks": len(chunks),
        },
        "ablation_type": "retrieval_top_k",
        "runs": runs,
        "guardrails": [
            "ablation is run on the small project-local gold set",
            "do not generalize beyond the recorded dataset size",
            "top_k ablation does not evaluate semantic embedding quality",
        ],
    }
