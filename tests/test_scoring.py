from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class ScoringBehaviorTests(unittest.TestCase):
    def test_score_retrieval_cases_computes_status_and_hit_rate(self) -> None:
        from evidenceops_public.scoring import score_retrieval_cases

        chunks = [
            {
                "chunk_id": "chunk_skill",
                "source_id": "onet",
                "text": "skill taxonomy metadata",
                "citation": {"source_url": "https://services.onetcenter.org/reference/", "license_status": "license"},
            }
        ]
        cases = [
            {
                "case_id": "retrieval_supported",
                "query": "skill taxonomy",
                "expected_status": "supported",
                "expected_chunk_ids": ["chunk_skill"],
            },
            {
                "case_id": "retrieval_unsupported",
                "query": "volcano telescope",
                "expected_status": "unsupported",
                "expected_chunk_ids": [],
            },
        ]

        report = score_retrieval_cases(cases, chunks)

        self.assertEqual(report["case_count"], 2)
        self.assertEqual(report["status_accuracy"], 1.0)
        self.assertEqual(report["supported_hit_rate"], 1.0)
        self.assertEqual(report["unsupported_accuracy"], 1.0)
        self.assertEqual(len(report["case_results"]), 2)

    def test_score_extraction_cases_computes_presence_accuracy(self) -> None:
        from evidenceops_public.scoring import score_extraction_cases

        extractions = [
            {
                "chunk_id": "chunk_skill",
                "field_type": "skill_signal",
                "field_value": "skill taxonomy",
                "citation": {"source_url": "https://services.onetcenter.org/reference/", "license_status": "license"},
            }
        ]
        cases = [
            {
                "case_id": "extract_positive",
                "chunk_id": "chunk_skill",
                "field_type": "skill_signal",
                "field_value": "skill taxonomy",
                "expected_present": True,
            },
            {
                "case_id": "extract_negative",
                "chunk_id": "chunk_skill",
                "field_type": "skill_signal",
                "field_value": "clinical diagnosis",
                "expected_present": False,
            },
        ]

        report = score_extraction_cases(cases, extractions)

        self.assertEqual(report["case_count"], 2)
        self.assertEqual(report["presence_accuracy"], 1.0)
        self.assertEqual(report["true_positive_count"], 1)
        self.assertEqual(report["true_negative_count"], 1)
        self.assertEqual(report["false_positive_count"], 0)
        self.assertEqual(report["false_negative_count"], 0)

    def test_scoring_cli_writes_eval_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            chunks_path = tmp / "chunks.jsonl"
            retrieval_cases_path = tmp / "retrieval_gold_set.jsonl"
            extractions_path = tmp / "extractions.jsonl"
            extraction_cases_path = tmp / "extraction_gold_set.jsonl"
            output_path = tmp / "eval_report.json"

            chunks_path.write_text(
                json.dumps(
                    {
                        "chunk_id": "chunk_skill",
                        "source_id": "onet",
                        "text": "skill taxonomy metadata",
                        "citation": {
                            "source_url": "https://services.onetcenter.org/reference/",
                            "license_status": "license",
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            retrieval_cases_path.write_text(
                json.dumps(
                    {
                        "case_id": "retrieval_supported",
                        "query": "skill taxonomy",
                        "expected_status": "supported",
                        "expected_chunk_ids": ["chunk_skill"],
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            extractions_path.write_text(
                json.dumps(
                    {
                        "chunk_id": "chunk_skill",
                        "field_type": "skill_signal",
                        "field_value": "skill taxonomy",
                        "citation": {
                            "source_url": "https://services.onetcenter.org/reference/",
                            "license_status": "license",
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            extraction_cases_path.write_text(
                json.dumps(
                    {
                        "case_id": "extract_positive",
                        "chunk_id": "chunk_skill",
                        "field_type": "skill_signal",
                        "field_value": "skill taxonomy",
                        "expected_present": True,
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "score_eval.py"),
                    "--chunks",
                    str(chunks_path),
                    "--retrieval-cases",
                    str(retrieval_cases_path),
                    "--extractions",
                    str(extractions_path),
                    "--extraction-cases",
                    str(extraction_cases_path),
                    "--output",
                    str(output_path),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            report = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "ok")
            self.assertEqual(report["retrieval"]["case_count"], 1)
            self.assertEqual(report["extraction"]["case_count"], 1)
            self.assertIn("dataset_size", report)


if __name__ == "__main__":
    unittest.main()

