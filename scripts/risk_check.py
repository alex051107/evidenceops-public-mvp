#!/usr/bin/env python3
"""Run source-aware risk checks over a search result JSON file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from evidenceops_public.risk_checker import check_search_result, load_search_result, write_risk_report


DEFAULT_SEARCH_RESULT = ROOT / "data" / "processed" / "search_result.json"
DEFAULT_OUTPUT = ROOT / "data" / "processed" / "risk_report.json"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--search-result", type=Path, default=DEFAULT_SEARCH_RESULT)
    parser.add_argument("--intended-use", default="project_demo")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    if not args.search_result.exists():
        print(f"Missing search result: {args.search_result}", file=sys.stderr)
        return 1

    search_result = load_search_result(args.search_result)
    report = check_search_result(search_result, intended_use=args.intended_use)
    write_risk_report(args.output, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

