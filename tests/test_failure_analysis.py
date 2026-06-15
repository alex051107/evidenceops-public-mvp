from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class FailureAnalysisBehaviorTests(unittest.TestCase):
    def test_build_failure_taxonomy_counts_retrieval_and_extraction_failures(self) -> None:
        from evidenceops_public.failure_analysis import build_failure_taxonomy

        eval_report = {
            "retrieval": {
                "case_results": [
                    {
                        "case_id": "r1",
                        "expected_status": "supported",
                        "actual_status": "unsupported",
                        "hit": False,
                    },
                    {
                        "case_id": "r2",
                        "expected_status": "unsupported",
                        "actual_status": "supported",
                        "hit": False,
                    },
                ]
            },
            "extraction": {
                "case_results": [
                    {
                        "case_id": "e1",
                        "expected_present": True,
                        "actual_present": False,
                    },
                    {
                        "case_id": "e2",
                        "expected_present": False,
                        "actual_present": True,
                    },
                ]
            },
        }

        taxonomy = build_failure_taxonomy(eval_report)

        counts = taxonomy["failure_counts"]
        self.assertEqual(counts["retrieval_miss"], 1)
        self.assertEqual(counts["unsupported_false_positive"], 1)
        self.assertEqual(counts["extraction_false_negative"], 1)
        self.assertEqual(counts["extraction_false_positive"], 1)
        self.assertEqual(taxonomy["total_failure_count"], 4)

    def test_run_retrieval_topk_ablation_reports_each_config(self) -> None:
        from evidenceops_public.failure_analysis import run_retrieval_topk_ablation

        chunks = [
            {
                "chunk_id": "chunk_skill",
                "text": "skill taxonomy metadata",
                "citation": {"source_url": "https://services.onetcenter.org/reference/", "license_status": "license"},
            }
        ]
        cases = [
            {
                "case_id": "r1",
                "query": "skill taxonomy",
                "expected_status": "supported",
                "expected_chunk_ids": ["chunk_skill"],
            }
        ]

        report = run_retrieval_topk_ablation(cases, chunks, top_k_values=[1, 3])

        self.assertEqual(report["status"], "ok")
        self.assertEqual(report["dataset_size"]["retrieval_cases"], 1)
        self.assertEqual([row["top_k"] for row in report["runs"]], [1, 3])
        self.assertTrue(all(row["supported_hit_rate"] == 1.0 for row in report["runs"]))

    def test_failure_analysis_cli_writes_taxonomy_and_ablation(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            eval_report_path = tmp / "eval_report.json"
            chunks_path = tmp / "chunks.jsonl"
            retrieval_cases_path = tmp / "retrieval_gold_set.jsonl"
            taxonomy_output = tmp / "failure_taxonomy.json"
            ablation_output = tmp / "ablation_report.json"

            eval_report_path.write_text(
                json.dumps(
                    {
                        "retrieval": {"case_results": []},
                        "extraction": {"case_results": []},
                    }
                ),
                encoding="utf-8",
            )
            chunks_path.write_text(
                json.dumps(
                    {
                        "chunk_id": "chunk_skill",
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
                        "case_id": "r1",
                        "query": "skill taxonomy",
                        "expected_status": "supported",
                        "expected_chunk_ids": ["chunk_skill"],
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "analyze_failures.py"),
                    "--eval-report",
                    str(eval_report_path),
                    "--chunks",
                    str(chunks_path),
                    "--retrieval-cases",
                    str(retrieval_cases_path),
                    "--taxonomy-output",
                    str(taxonomy_output),
                    "--ablation-output",
                    str(ablation_output),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            taxonomy = json.loads(taxonomy_output.read_text(encoding="utf-8"))
            ablation = json.loads(ablation_output.read_text(encoding="utf-8"))
            self.assertEqual(taxonomy["status"], "ok")
            self.assertEqual(ablation["status"], "ok")
            self.assertGreaterEqual(len(ablation["runs"]), 1)


if __name__ == "__main__":
    unittest.main()

