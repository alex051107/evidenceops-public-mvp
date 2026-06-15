#!/usr/bin/env python3
"""Run small rule-based structured extraction over evidence chunks."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from evidenceops_public.extractor import build_extraction_report, extract_chunks
from evidenceops_public.parser import read_jsonl, write_jsonl


DEFAULT_CHUNKS = ROOT / "data" / "processed" / "chunks.jsonl"
DEFAULT_OUTPUT = ROOT / "data" / "processed" / "extractions.jsonl"
DEFAULT_UNMATCHED_OUTPUT = ROOT / "data" / "processed" / "extraction_unmatched_chunks.jsonl"
DEFAULT_REPORT_OUTPUT = ROOT / "data" / "processed" / "extraction_report.json"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chunks", type=Path, default=DEFAULT_CHUNKS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--unmatched-output", type=Path, default=DEFAULT_UNMATCHED_OUTPUT)
    parser.add_argument("--report-output", type=Path, default=DEFAULT_REPORT_OUTPUT)
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    if not args.chunks.exists():
        print(f"Missing chunks file: {args.chunks}", file=sys.stderr)
        return 1

    extracted_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    chunks = read_jsonl(args.chunks)
    extractions, unmatched_chunks = extract_chunks(chunks, extracted_at=extracted_at)
    write_jsonl(args.output, extractions)
    write_jsonl(args.unmatched_output, unmatched_chunks)
    report = build_extraction_report(
        chunks_path=args.chunks,
        output_path=args.output,
        input_chunk_count=len(chunks),
        extractions=extractions,
        unmatched_chunks=unmatched_chunks,
        extracted_at=extracted_at,
    )
    args.report_output.parent.mkdir(parents=True, exist_ok=True)
    args.report_output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

