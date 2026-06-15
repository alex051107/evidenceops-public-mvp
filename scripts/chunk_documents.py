#!/usr/bin/env python3
"""Create citation-aware chunks from parsed documents."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from evidenceops_public.chunker import build_chunk_report, chunk_documents
from evidenceops_public.parser import read_jsonl, write_jsonl


DEFAULT_INPUT = ROOT / "data" / "processed" / "parsed_documents.jsonl"
DEFAULT_CHUNKS_OUTPUT = ROOT / "data" / "processed" / "chunks.jsonl"
DEFAULT_REPORT_OUTPUT = ROOT / "data" / "processed" / "chunk_report.json"
DEFAULT_ERRORS_OUTPUT = ROOT / "data" / "processed" / "chunk_errors.jsonl"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--chunks-output", type=Path, default=DEFAULT_CHUNKS_OUTPUT)
    parser.add_argument("--report-output", type=Path, default=DEFAULT_REPORT_OUTPUT)
    parser.add_argument("--errors-output", type=Path, default=DEFAULT_ERRORS_OUTPUT)
    parser.add_argument("--max-words", type=int, default=60)
    parser.add_argument("--overlap-words", type=int, default=10)
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    if not args.input.exists():
        print(f"Missing parsed document store: {args.input}", file=sys.stderr)
        return 1

    chunked_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    documents = read_jsonl(args.input)
    chunks, errors = chunk_documents(
        documents,
        max_words=args.max_words,
        overlap_words=args.overlap_words,
        chunked_at=chunked_at,
    )
    write_jsonl(args.chunks_output, chunks)
    write_jsonl(args.errors_output, errors)
    report = build_chunk_report(
        input_path=args.input,
        chunks_output_path=args.chunks_output,
        input_document_count=len(documents),
        chunks=chunks,
        chunk_errors=errors,
        max_words=args.max_words,
        overlap_words=args.overlap_words,
        chunked_at=chunked_at,
    )
    args.report_output.parent.mkdir(parents=True, exist_ok=True)
    args.report_output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

