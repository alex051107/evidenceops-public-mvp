"""Source-aware risk checks for EvidenceOps search outputs."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


SYNTHETIC_SAFE_USES = {"synthetic_demo", "schema_test", "internal_project_demo"}


def make_risk(
    *,
    risk_type: str,
    severity: str,
    message: str,
    query: str | None = None,
    chunk_id: str | None = None,
    source_id: str | None = None,
) -> dict:
    return {
        "risk_type": risk_type,
        "severity": severity,
        "message": message,
        "query": query,
        "chunk_id": chunk_id,
        "source_id": source_id,
    }


def evidence_has_citation(evidence: dict) -> bool:
    citation = evidence.get("citation")
    return isinstance(citation, dict) and bool(citation.get("source_url")) and bool(citation.get("license_status"))


def check_search_result(
    search_result: dict,
    *,
    intended_use: str,
    checked_at: str | None = None,
) -> dict:
    checked_at_value = checked_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    query = search_result.get("query")
    risks: list[dict] = []

    if search_result.get("status") == "unsupported":
        risks.append(
            make_risk(
                risk_type="unsupported_query",
                severity="warning",
                message="Search returned unsupported; do not turn this into an answer or resume claim.",
                query=query,
            )
        )

    for evidence in search_result.get("evidence", []):
        chunk_id = evidence.get("chunk_id")
        source_id = evidence.get("source_id")

        if not evidence_has_citation(evidence):
            risks.append(
                make_risk(
                    risk_type="missing_citation",
                    severity="error",
                    message="Evidence item is missing citation source_url or license_status.",
                    query=query,
                    chunk_id=chunk_id,
                    source_id=source_id,
                )
            )

        if evidence.get("is_synthetic") is True and intended_use not in SYNTHETIC_SAFE_USES:
            risks.append(
                make_risk(
                    risk_type="synthetic_source_used_for_non_synthetic_context",
                    severity="warning",
                    message="Synthetic evidence must not be presented as real customer/company/source data.",
                    query=query,
                    chunk_id=chunk_id,
                    source_id=source_id,
                )
            )

        not_use_for = evidence.get("not_use_for") or []
        if intended_use in not_use_for:
            risks.append(
                make_risk(
                    risk_type="not_use_for_conflict",
                    severity="error",
                    message=f"Intended use '{intended_use}' conflicts with source not_use_for metadata.",
                    query=query,
                    chunk_id=chunk_id,
                    source_id=source_id,
                )
            )

    severity_counts: dict[str, int] = {}
    for risk in risks:
        severity = risk["severity"]
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

    return {
        "status": "risk_found" if risks else "ok",
        "checked_at": checked_at_value,
        "intended_use": intended_use,
        "query": query,
        "risk_count": len(risks),
        "severity_counts": severity_counts,
        "risks": risks,
        "guardrails": [
            "risk check is a project guardrail, not legal/medical/compliance advice",
            "unsupported search results must not become claims",
            "synthetic evidence must stay labeled",
            "not_use_for conflicts are treated as errors",
        ],
    }


def load_search_result(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_risk_report(path: Path, report: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

