#!/usr/bin/env python3
"""Build failure taxonomy and retrieval top-k ablation report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from evidenceops_public.failure_analysis import build_failure_taxonomy, run_retrieval_topk_ablation
from evidenceops_public.parser import read_jsonl


DEFAULT_EVAL_REPORT = ROOT / "data" / "eval" / "eval_report.json"
DEFAULT_CHUNKS = ROOT / "data" / "processed" / "chunks.jsonl"
DEFAULT_RETRIEVAL_CASES = ROOT / "data" / "eval" / "retrieval_gold_set.jsonl"
DEFAULT_TAXONOMY_OUTPUT = ROOT / "data" / "eval" / "failure_taxonomy.json"
DEFAULT_ABLATION_OUTPUT = ROOT / "data" / "eval" / "ablation_report.json"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eval-report", type=Path, default=DEFAULT_EVAL_REPORT)
    parser.add_argument("--chunks", type=Path, default=DEFAULT_CHUNKS)
    parser.add_argument("--retrieval-cases", type=Path, default=DEFAULT_RETRIEVAL_CASES)
    parser.add_argument("--taxonomy-output", type=Path, default=DEFAULT_TAXONOMY_OUTPUT)
    parser.add_argument("--ablation-output", type=Path, default=DEFAULT_ABLATION_OUTPUT)
    return parser


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    args = build_arg_parser().parse_args()
    for path in [args.eval_report, args.chunks, args.retrieval_cases]:
        if not path.exists():
            print(f"Missing required input: {path}", file=sys.stderr)
            return 1

    eval_report = json.loads(args.eval_report.read_text(encoding="utf-8"))
    taxonomy = build_failure_taxonomy(eval_report)
    ablation = run_retrieval_topk_ablation(read_jsonl(args.retrieval_cases), read_jsonl(args.chunks))
    write_json(args.taxonomy_output, taxonomy)
    write_json(args.ablation_output, ablation)
    print(
        json.dumps(
            {
                "status": "ok",
                "total_failure_count": taxonomy["total_failure_count"],
                "ablation_runs": len(ablation["runs"]),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

