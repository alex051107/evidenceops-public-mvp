#!/usr/bin/env python3
"""Score retrieval and extraction outputs against project-local gold sets."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from evidenceops_public.parser import read_jsonl
from evidenceops_public.scoring import build_eval_report


DEFAULT_CHUNKS = ROOT / "data" / "processed" / "chunks.jsonl"
DEFAULT_RETRIEVAL_CASES = ROOT / "data" / "eval" / "retrieval_gold_set.jsonl"
DEFAULT_EXTRACTIONS = ROOT / "data" / "processed" / "extractions.jsonl"
DEFAULT_EXTRACTION_CASES = ROOT / "data" / "eval" / "extraction_gold_set.jsonl"
DEFAULT_OUTPUT = ROOT / "data" / "eval" / "eval_report.json"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chunks", type=Path, default=DEFAULT_CHUNKS)
    parser.add_argument("--retrieval-cases", type=Path, default=DEFAULT_RETRIEVAL_CASES)
    parser.add_argument("--extractions", type=Path, default=DEFAULT_EXTRACTIONS)
    parser.add_argument("--extraction-cases", type=Path, default=DEFAULT_EXTRACTION_CASES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    required_paths = [args.chunks, args.retrieval_cases, args.extractions, args.extraction_cases]
    for path in required_paths:
        if not path.exists():
            print(f"Missing required input: {path}", file=sys.stderr)
            return 1

    report = build_eval_report(
        retrieval_cases=read_jsonl(args.retrieval_cases),
        chunks=read_jsonl(args.chunks),
        extraction_cases=read_jsonl(args.extraction_cases),
        extractions=read_jsonl(args.extractions),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = {
        "status": report["status"],
        "dataset_size": report["dataset_size"],
        "retrieval": {
            "status_accuracy": report["retrieval"]["status_accuracy"],
            "supported_hit_rate": report["retrieval"]["supported_hit_rate"],
            "unsupported_accuracy": report["retrieval"]["unsupported_accuracy"],
        },
        "extraction": {
            "presence_accuracy": report["extraction"]["presence_accuracy"],
            "precision": report["extraction"]["precision"],
            "recall": report["extraction"]["recall"],
        },
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

