#!/usr/bin/env python3
"""Build project-local retrieval and extraction gold sets."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from evidenceops_public.gold_set import build_gold_sets
from evidenceops_public.parser import read_jsonl, write_jsonl


DEFAULT_CHUNKS = ROOT / "data" / "processed" / "chunks.jsonl"
DEFAULT_EXTRACTIONS = ROOT / "data" / "processed" / "extractions.jsonl"
DEFAULT_RETRIEVAL_OUTPUT = ROOT / "data" / "eval" / "retrieval_gold_set.jsonl"
DEFAULT_EXTRACTION_OUTPUT = ROOT / "data" / "eval" / "extraction_gold_set.jsonl"
DEFAULT_MANIFEST_OUTPUT = ROOT / "data" / "eval" / "gold_set_manifest.json"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chunks", type=Path, default=DEFAULT_CHUNKS)
    parser.add_argument("--extractions", type=Path, default=DEFAULT_EXTRACTIONS)
    parser.add_argument("--retrieval-output", type=Path, default=DEFAULT_RETRIEVAL_OUTPUT)
    parser.add_argument("--extraction-output", type=Path, default=DEFAULT_EXTRACTION_OUTPUT)
    parser.add_argument("--manifest-output", type=Path, default=DEFAULT_MANIFEST_OUTPUT)
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    if not args.chunks.exists():
        print(f"Missing chunks file: {args.chunks}", file=sys.stderr)
        return 1
    if not args.extractions.exists():
        print(f"Missing extractions file: {args.extractions}", file=sys.stderr)
        return 1

    chunks = read_jsonl(args.chunks)
    extractions = read_jsonl(args.extractions)
    retrieval_cases, extraction_cases, manifest = build_gold_sets(chunks, extractions)
    write_jsonl(args.retrieval_output, retrieval_cases)
    write_jsonl(args.extraction_output, extraction_cases)
    args.manifest_output.parent.mkdir(parents=True, exist_ok=True)
    args.manifest_output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

