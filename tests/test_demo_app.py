from __future__ import annotations

import json
import importlib.util
import signal
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class DemoAppBehaviorTests(unittest.TestCase):
    def test_build_search_response_returns_evidence_and_risk(self) -> None:
        from evidenceops_public.demo_app import build_search_response

        chunks = [
            {
                "chunk_id": "chunk_skill",
                "document_id": "doc_onet",
                "source_id": "onet",
                "source_url": "https://services.onetcenter.org/reference/",
                "license_status": "license agreement",
                "is_synthetic": False,
                "text": "O*NET supports skill taxonomy metadata.",
                "not_use_for": ["real_time_jd_claim"],
                "citation": {
                    "document_id": "doc_onet",
                    "section_id": "doc_onet::section::abc",
                    "source_url": "https://services.onetcenter.org/reference/",
                    "license_status": "license agreement",
                },
            }
        ]

        response = build_search_response("skill taxonomy", chunks, intended_use="project_demo")

        self.assertEqual(response["search"]["status"], "supported")
        self.assertEqual(response["search"]["evidence_count"], 1)
        self.assertEqual(response["risk"]["status"], "ok")
        self.assertEqual(response["search"]["evidence"][0]["citation"]["source_url"], "https://services.onetcenter.org/reference/")

    def test_build_summary_payload_reads_eval_and_failure_reports(self) -> None:
        from evidenceops_public.demo_app import build_summary_payload

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "data" / "eval").mkdir(parents=True)
            (root / "data" / "processed").mkdir(parents=True)
            (root / "data" / "eval" / "eval_report.json").write_text(
                json.dumps(
                    {
                        "status": "ok",
                        "dataset_size": {"retrieval_cases": 20, "chunks": 5},
                        "retrieval": {"status_accuracy": 1.0},
                        "extraction": {"presence_accuracy": 1.0},
                    }
                ),
                encoding="utf-8",
            )
            (root / "data" / "eval" / "failure_taxonomy.json").write_text(
                json.dumps({"status": "ok", "total_failure_count": 0}),
                encoding="utf-8",
            )
            (root / "data" / "eval" / "ablation_report.json").write_text(
                json.dumps({"status": "ok", "runs": [{"top_k": 1}]}),
                encoding="utf-8",
            )

            payload = build_summary_payload(root)

            self.assertEqual(payload["status"], "ok")
            self.assertEqual(payload["eval"]["dataset_size"]["retrieval_cases"], 20)
            self.assertEqual(payload["failure_taxonomy"]["total_failure_count"], 0)
            self.assertEqual(len(payload["ablation"]["runs"]), 1)

    def test_render_index_contains_operational_console_elements(self) -> None:
        from evidenceops_public.demo_app import render_index

        html = render_index()

        self.assertIn("Evidence Console", html)
        self.assertIn("Search evidence", html)
        self.assertIn("/api/search", html)
        self.assertIn("No citation, no claim", html)

    def test_demo_server_can_bind_without_reverse_dns_hang(self) -> None:
        module_path = ROOT / "scripts" / "run_demo_server.py"
        spec = importlib.util.spec_from_file_location("run_demo_server", module_path)
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)

        def timeout_handler(signum, frame):  # type: ignore[no-untyped-def]
            raise TimeoutError("server bind timed out")

        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(2)
        try:
            server = module.EvidenceOpsServer(("127.0.0.1", 0), module.EvidenceOpsHandler)
            server.server_close()
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)


if __name__ == "__main__":
    unittest.main()
