#!/usr/bin/env python3
"""Parse normalized document-store records into sectioned parsed documents."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from evidenceops_public.parser import build_parse_report, parse_documents, read_jsonl, write_jsonl


DEFAULT_INPUT = ROOT / "data" / "processed" / "document_store.jsonl"
DEFAULT_PARSED_OUTPUT = ROOT / "data" / "processed" / "parsed_documents.jsonl"
DEFAULT_REPORT_OUTPUT = ROOT / "data" / "processed" / "parse_report.json"
DEFAULT_ERRORS_OUTPUT = ROOT / "data" / "processed" / "parse_errors.jsonl"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--parsed-output", type=Path, default=DEFAULT_PARSED_OUTPUT)
    parser.add_argument("--report-output", type=Path, default=DEFAULT_REPORT_OUTPUT)
    parser.add_argument("--errors-output", type=Path, default=DEFAULT_ERRORS_OUTPUT)
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    if not args.input.exists():
        print(f"Missing input document store: {args.input}", file=sys.stderr)
        return 1

    parsed_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    documents = read_jsonl(args.input)
    parsed_documents, parse_errors = parse_documents(documents, parsed_at=parsed_at)

    write_jsonl(args.parsed_output, parsed_documents)
    write_jsonl(args.errors_output, parse_errors)
    report = build_parse_report(
        input_path=args.input,
        parsed_output_path=args.parsed_output,
        errors_output_path=args.errors_output,
        input_document_count=len(documents),
        parsed_documents=parsed_documents,
        parse_errors=parse_errors,
        parsed_at=parsed_at,
    )
    args.report_output.parent.mkdir(parents=True, exist_ok=True)
    args.report_output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

