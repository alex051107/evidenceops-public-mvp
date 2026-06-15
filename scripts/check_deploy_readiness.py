#!/usr/bin/env python3
"""Check whether the project has the artifacts needed for deployment."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REQUIRED_FILES = (
    "Dockerfile",
    "render.yaml",
    ".github/workflows/pages.yml",
    "public/index.html",
    "public/evidenceops-data.json",
    "public/.nojekyll",
    "data/eval/eval_report.json",
    "data/eval/failure_taxonomy.json",
    "data/eval/ablation_report.json",
)


def check_deploy_readiness(root: Path) -> dict:
    missing = [path for path in REQUIRED_FILES if not (root / path).exists()]
    pycache_dirs = [str(path.relative_to(root)) for path in root.rglob("__pycache__") if path.is_dir()]
    status = "ok" if not missing and not pycache_dirs else "failed"
    return {
        "status": status,
        "root": str(root),
        "required_files": list(REQUIRED_FILES),
        "missing": missing,
        "pycache_dirs": pycache_dirs,
        "static_url_path": "public/index.html",
        "docker_entrypoint": "Dockerfile",
        "github_pages_workflow": ".github/workflows/pages.yml",
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    report = check_deploy_readiness(args.root)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())

