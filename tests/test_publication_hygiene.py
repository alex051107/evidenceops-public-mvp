from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _portable_paths import portable_report_path  # noqa: E402


class PublicationHygieneTests(unittest.TestCase):
    def test_repository_paths_are_portable(self) -> None:
        source = ROOT / "data" / "processed" / "chunks.jsonl"
        self.assertEqual(
            "<repo-root>/data/processed/chunks.jsonl",
            portable_report_path(source, ROOT),
        )

    def test_external_paths_do_not_disclose_parent_directories(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "input.jsonl"
            self.assertEqual("<external-path>/input.jsonl", portable_report_path(source, ROOT))

    def test_committed_reports_and_registry_exclude_machine_paths(self) -> None:
        checked = [
            ROOT / "data" / "processed" / "ingestion_report.json",
            ROOT / "data" / "processed" / "parse_report.json",
            ROOT / "data" / "processed" / "chunk_report.json",
            ROOT / "data" / "processed" / "extraction_report.json",
        ]
        for report_path in checked:
            text = report_path.read_text(encoding="utf-8")
            self.assertNotIn("/Users/", text, report_path)
            report = json.loads(text)
            path_values = [value for key, value in report.items() if key.endswith("_path")]
            self.assertTrue(path_values, report_path)
            self.assertTrue(
                all(value.startswith("<repo-root>/") for value in path_values),
                report_path,
            )

        with (ROOT / "data" / "source_registry.csv").open(
            "r", encoding="utf-8", newline=""
        ) as handle:
            registry = {row["source_id"]: row for row in csv.DictReader(handle)}
        private_seed = registry["local_jd_skill_matrix"]
        self.assertEqual("true", private_seed["private_required"])
        self.assertEqual("excluded_from_public_mvp", private_seed["decision"])
        self.assertNotIn("/Users/", private_seed["source_url"])
