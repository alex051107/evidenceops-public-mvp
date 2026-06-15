#!/usr/bin/env python3
"""Ingest Day 2 sample document cards into a normalized processed store."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "data" / "source_registry.csv"
SAMPLE_DOCS_PATH = ROOT / "data" / "raw" / "samples" / "sample_documents.jsonl"
PROCESSED_DIR = ROOT / "data" / "processed"
DOCUMENT_STORE_PATH = PROCESSED_DIR / "document_store.jsonl"
INGESTION_REPORT_PATH = PROCESSED_DIR / "ingestion_report.json"


def read_registry() -> dict[str, dict]:
    with REGISTRY_PATH.open("r", encoding="utf-8", newline="") as handle:
        return {row["source_id"]: row for row in csv.DictReader(handle)}


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        row["_line_no"] = line_no
        rows.append(row)
    return rows


def stable_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_document(raw_doc: dict, source: dict, ingested_at: str) -> dict:
    text = " ".join(raw_doc["text"].split())
    return {
        "document_id": raw_doc["document_id"],
        "source_id": raw_doc["source_id"],
        "source_name": source["source_name"],
        "source_type": source["source_type"],
        "source_url": raw_doc["source_url"],
        "retrieved_at": raw_doc["retrieved_at"],
        "ingested_at": ingested_at,
        "document_type": raw_doc["document_type"],
        "title": raw_doc["title"],
        "license_status": raw_doc["license_status"],
        "is_public_source": raw_doc["is_public_source"],
        "is_synthetic": raw_doc["is_synthetic"],
        "section_path": raw_doc["section_path"],
        "text": text,
        "text_sha256": stable_hash(text),
        "char_count": len(text),
        "token_estimate": max(1, len(text.split())),
        "not_use_for": raw_doc["not_use_for"],
        "mvp_role": source["mvp_role"],
        "decision": source["decision"],
    }


def main() -> None:
    registry = read_registry()
    raw_docs = read_jsonl(SAMPLE_DOCS_PATH)
    ingested_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    processed: list[dict] = []
    errors: list[dict] = []

    for raw_doc in raw_docs:
        source = registry.get(raw_doc["source_id"])
        if source is None:
            errors.append(
                {
                    "line_no": raw_doc["_line_no"],
                    "document_id": raw_doc.get("document_id"),
                    "error": f"unknown source_id {raw_doc.get('source_id')}",
                }
            )
            continue
        if source["private_required"].lower() == "true":
            errors.append(
                {
                    "line_no": raw_doc["_line_no"],
                    "document_id": raw_doc.get("document_id"),
                    "error": "private-required source cannot be ingested by default",
                }
            )
            continue
        processed.append(normalize_document(raw_doc, source, ingested_at))

    if errors:
        raise SystemExit(json.dumps({"status": "failed", "errors": errors}, ensure_ascii=False, indent=2))

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    DOCUMENT_STORE_PATH.write_text(
        "\n".join(json.dumps(doc, ensure_ascii=False, sort_keys=True) for doc in processed) + "\n",
        encoding="utf-8",
    )

    source_counts: dict[str, int] = {}
    type_counts: dict[str, int] = {}
    synthetic_count = 0
    for doc in processed:
        source_counts[doc["source_id"]] = source_counts.get(doc["source_id"], 0) + 1
        type_counts[doc["document_type"]] = type_counts.get(doc["document_type"], 0) + 1
        synthetic_count += int(doc["is_synthetic"])

    report = {
        "status": "ok",
        "ingested_at": ingested_at,
        "input_path": str(SAMPLE_DOCS_PATH),
        "output_path": str(DOCUMENT_STORE_PATH),
        "document_count": len(processed),
        "public_document_count": len(processed) - synthetic_count,
        "synthetic_document_count": synthetic_count,
        "source_counts": source_counts,
        "document_type_counts": type_counts,
        "guardrails": [
            "private_required sources are rejected",
            "license_status is preserved",
            "source_url is preserved",
            "synthetic documents remain marked",
            "no RAG or metric claim is generated in Day 3",
        ],
    }
    INGESTION_REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

