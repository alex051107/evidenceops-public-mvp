#!/usr/bin/env python3
"""Validate Day 0-Day 2 public-source scaffolding.

The validator intentionally uses only the Python standard library so Day 0-Day 2
can run before dependency setup. It checks metadata completeness and guards the
public-data boundary before later ingestion/RAG work starts.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "data" / "source_registry.csv"
SOURCE_CARDS_PATH = ROOT / "data" / "raw" / "samples" / "public_source_cards.jsonl"
SAMPLE_DOCS_PATH = ROOT / "data" / "raw" / "samples" / "sample_documents.jsonl"

REQUIRED_REGISTRY_FIELDS = {
    "source_id",
    "source_name",
    "source_type",
    "source_url",
    "retrieved_at",
    "license_status",
    "access_method",
    "mvp_role",
    "private_required",
    "is_synthetic_source",
    "not_use_for",
    "decision",
}

REQUIRED_SOURCE_CARD_FIELDS = {
    "source_id",
    "source_name",
    "retrieved_at",
    "source_url",
    "source_type",
    "access_method",
    "license_status",
    "mvp_decision",
    "confidence",
    "not_use_for",
    "private_required",
}

REQUIRED_DOCUMENT_FIELDS = {
    "document_id",
    "source_id",
    "source_url",
    "retrieved_at",
    "document_type",
    "title",
    "license_status",
    "is_public_source",
    "is_synthetic",
    "section_path",
    "text",
    "not_use_for",
}

BANNED_DEFAULT_PHRASES = {
    "production deployment",
    "HIPAA",
    "GDPR",
    "real patient",
    "真实患者",
    "真实客户",
    "clinical decision support",
    "medical advice",
    "ChEMBL-scale",
    "high-concurrency",
}


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        fail(f"Missing file: {path}")
    rows: list[dict] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            fail(f"{path}:{line_no} is not valid JSON: {exc}")
    if not rows:
        fail(f"{path} has no JSONL records")
    return rows


def validate_registry() -> list[dict]:
    if not REGISTRY_PATH.exists():
        fail(f"Missing file: {REGISTRY_PATH}")

    with REGISTRY_PATH.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        missing_headers = REQUIRED_REGISTRY_FIELDS - set(reader.fieldnames or [])
        if missing_headers:
            fail(f"source_registry.csv missing headers: {sorted(missing_headers)}")
        rows = list(reader)

    if not rows:
        fail("source_registry.csv has no rows")

    selected_public = 0
    for index, row in enumerate(rows, start=2):
        for field in REQUIRED_REGISTRY_FIELDS:
            if row.get(field, "").strip() == "":
                fail(f"source_registry.csv row {index} missing {field}")
        if row["decision"].startswith("selected") and row["private_required"].lower() == "true":
            fail(f"source_registry.csv row {index} selects private-required source {row['source_id']}")
        if row["decision"].startswith("selected") and row["is_synthetic_source"].lower() == "false":
            selected_public += 1
        if "ligamd" in row["source_id"].lower() and row["decision"].startswith("selected"):
            fail("LiGaMD/private logs cannot be a default selected source")

    if selected_public < 5:
        fail("Need at least 5 selected non-synthetic public sources")

    return rows


def validate_source_cards(registry_ids: set[str]) -> None:
    rows = load_jsonl(SOURCE_CARDS_PATH)
    for index, row in enumerate(rows, start=1):
        missing = REQUIRED_SOURCE_CARD_FIELDS - set(row)
        if missing:
            fail(f"public_source_cards.jsonl record {index} missing fields: {sorted(missing)}")
        if row["source_id"] not in registry_ids:
            fail(f"public_source_cards.jsonl record {index} has unknown source_id {row['source_id']}")
        if row["private_required"] is True:
            fail(f"public_source_cards.jsonl record {index} is private-required")
        if not row["source_url"]:
            fail(f"public_source_cards.jsonl record {index} missing source_url")
        if not row["license_status"]:
            fail(f"public_source_cards.jsonl record {index} missing license_status")


def validate_sample_documents(registry_ids: set[str]) -> None:
    rows = load_jsonl(SAMPLE_DOCS_PATH)
    synthetic_count = 0
    public_count = 0

    for index, row in enumerate(rows, start=1):
        missing = REQUIRED_DOCUMENT_FIELDS - set(row)
        if missing:
            fail(f"sample_documents.jsonl record {index} missing fields: {sorted(missing)}")
        if row["source_id"] not in registry_ids:
            fail(f"sample_documents.jsonl record {index} has unknown source_id {row['source_id']}")
        if not isinstance(row["is_synthetic"], bool):
            fail(f"sample_documents.jsonl record {index} is_synthetic must be boolean")
        if not isinstance(row["is_public_source"], bool):
            fail(f"sample_documents.jsonl record {index} is_public_source must be boolean")
        if not isinstance(row["section_path"], list) or not row["section_path"]:
            fail(f"sample_documents.jsonl record {index} section_path must be a non-empty list")
        if not isinstance(row["not_use_for"], list) or not row["not_use_for"]:
            fail(f"sample_documents.jsonl record {index} not_use_for must be a non-empty list")
        if row["is_synthetic"]:
            synthetic_count += 1
            if row["is_public_source"]:
                fail(f"sample_documents.jsonl record {index} synthetic doc cannot be public_source=true")
        else:
            public_count += 1
            if not row["is_public_source"]:
                fail(f"sample_documents.jsonl record {index} non-synthetic doc must be public_source=true")
        if "ligamd" in row["text"].lower() or "private md" in row["text"].lower():
            fail(f"sample_documents.jsonl record {index} mentions private LiGaMD/MD content")
        text_blob = " ".join(str(row.get(field, "")) for field in ("title", "text", "license_status"))
        for phrase in BANNED_DEFAULT_PHRASES:
            if phrase.lower() in text_blob.lower() and "not" not in text_blob.lower():
                fail(f"sample_documents.jsonl record {index} may contain banned unsupported phrase: {phrase}")

    if public_count < 4:
        fail("Need at least 4 public sample documents")
    if synthetic_count < 1:
        fail("Need at least 1 explicitly synthetic enterprise sample document")


def main() -> None:
    registry = validate_registry()
    registry_ids = {row["source_id"] for row in registry}
    validate_source_cards(registry_ids)
    validate_sample_documents(registry_ids)
    print("OK: public source registry, source cards, and sample document cards passed validation.")


if __name__ == "__main__":
    main()

