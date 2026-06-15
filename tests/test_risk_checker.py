from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class RiskCheckerBehaviorTests(unittest.TestCase):
    def test_check_search_result_flags_unsupported_query(self) -> None:
        from evidenceops_public.risk_checker import check_search_result

        search_result = {
            "status": "unsupported",
            "query": "unknown thing",
            "evidence_count": 0,
            "evidence": [],
        }

        report = check_search_result(search_result, intended_use="project_demo")

        self.assertEqual(report["status"], "risk_found")
        self.assertEqual(report["risk_count"], 1)
        self.assertEqual(report["risks"][0]["risk_type"], "unsupported_query")
        self.assertEqual(report["risks"][0]["severity"], "warning")

    def test_check_search_result_flags_missing_citation(self) -> None:
        from evidenceops_public.risk_checker import check_search_result

        search_result = {
            "status": "supported",
            "query": "skill taxonomy",
            "evidence_count": 1,
            "evidence": [
                {
                    "chunk_id": "chunk_bad",
                    "text": "skill taxonomy",
                    "citation": {},
                    "not_use_for": [],
                    "is_synthetic": False,
                }
            ],
        }

        report = check_search_result(search_result, intended_use="project_demo")

        self.assertEqual(report["status"], "risk_found")
        self.assertEqual(report["risks"][0]["risk_type"], "missing_citation")
        self.assertEqual(report["risks"][0]["severity"], "error")

    def test_risk_check_cli_flags_synthetic_and_not_use_for_conflict(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            search_path = tmp / "search_result.json"
            output_path = tmp / "risk_report.json"
            search_result = {
                "status": "supported",
                "query": "customer workflow",
                "evidence_count": 1,
                "evidence": [
                    {
                        "chunk_id": "chunk_synthetic",
                        "source_id": "synthetic_enterprise_docs",
                        "source_url": "local_generated",
                        "license_status": "project-generated synthetic content",
                        "is_synthetic": True,
                        "text": "Synthetic SOP text.",
                        "not_use_for": ["real_customer_data"],
                        "citation": {
                            "document_id": "doc_synthetic",
                            "section_id": "doc_synthetic::section::abc",
                            "source_url": "local_generated",
                            "license_status": "project-generated synthetic content",
                        },
                    }
                ],
            }
            search_path.write_text(json.dumps(search_result, ensure_ascii=False), encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "risk_check.py"),
                    "--search-result",
                    str(search_path),
                    "--intended-use",
                    "real_customer_data",
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
            risk_types = {risk["risk_type"] for risk in report["risks"]}
            self.assertEqual(report["status"], "risk_found")
            self.assertIn("synthetic_source_used_for_non_synthetic_context", risk_types)
            self.assertIn("not_use_for_conflict", risk_types)


if __name__ == "__main__":
    unittest.main()

