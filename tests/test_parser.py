from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class ParserBehaviorTests(unittest.TestCase):
    def test_parse_document_preserves_source_metadata_and_creates_section(self) -> None:
        from evidenceops_public.parser import parse_document

        raw_doc = {
            "document_id": "doc_test",
            "source_id": "sec_edgar",
            "source_name": "SEC EDGAR data.sec.gov",
            "source_type": "public_enterprise_documents",
            "source_url": "https://www.sec.gov/search-filings/edgar-application-programming-interfaces",
            "retrieved_at": "2026-06-15",
            "ingested_at": "2026-06-15T00:00:00+00:00",
            "document_type": "api_doc_note",
            "title": "SEC API note",
            "license_status": "public filing data",
            "is_public_source": True,
            "is_synthetic": False,
            "section_path": ["api", "submissions"],
            "text": "SEC APIs expose public filing history.\n\nThey are not investment advice.",
            "text_sha256": "placeholder",
            "char_count": 71,
            "token_estimate": 10,
            "not_use_for": ["investment_advice"],
            "mvp_role": "enterprise_document_mode",
            "decision": "selected",
        }

        parsed = parse_document(raw_doc)

        self.assertEqual(parsed["document_id"], "doc_test")
        self.assertEqual(parsed["source_id"], "sec_edgar")
        self.assertEqual(parsed["source_url"], raw_doc["source_url"])
        self.assertEqual(parsed["license_status"], "public filing data")
        self.assertFalse(parsed["is_synthetic"])
        self.assertEqual(parsed["parse_status"], "parsed")
        self.assertEqual(len(parsed["sections"]), 1)
        section = parsed["sections"][0]
        self.assertEqual(section["section_path"], ["api", "submissions"])
        self.assertEqual(section["char_start"], 0)
        self.assertGreater(section["char_end"], section["char_start"])
        self.assertIn("public filing history", section["text"])
        self.assertTrue(section["section_id"].startswith("doc_test::section::"))

    def test_parse_document_rejects_empty_text_with_parse_error(self) -> None:
        from evidenceops_public.parser import ParseError, parse_document

        raw_doc = {
            "document_id": "doc_empty",
            "source_id": "chembl",
            "text": "   ",
            "section_path": ["downloads"],
        }

        with self.assertRaises(ParseError) as context:
            parse_document(raw_doc)

        self.assertEqual(context.exception.document_id, "doc_empty")
        self.assertIn("empty text", context.exception.reason)

    def test_parse_documents_cli_writes_outputs_and_error_log(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            input_path = tmp / "document_store.jsonl"
            parsed_path = tmp / "parsed_documents.jsonl"
            report_path = tmp / "parse_report.json"
            errors_path = tmp / "parse_errors.jsonl"
            docs = [
                {
                    "document_id": "doc_public",
                    "source_id": "onet",
                    "source_name": "O*NET",
                    "source_type": "public_skill_taxonomy",
                    "source_url": "https://services.onetcenter.org/reference/",
                    "retrieved_at": "2026-06-15",
                    "ingested_at": "2026-06-15T00:00:00+00:00",
                    "document_type": "api_doc_note",
                    "title": "O*NET API note",
                    "license_status": "license agreement",
                    "is_public_source": True,
                    "is_synthetic": False,
                    "section_path": ["api"],
                    "text": "O*NET supports skill taxonomy normalization.",
                    "not_use_for": ["real_time_jd_claim"],
                    "mvp_role": "skill_normalization",
                    "decision": "selected",
                },
                {
                    "document_id": "doc_bad",
                    "source_id": "synthetic_enterprise_docs",
                    "source_name": "Synthetic Enterprise SOP FAQ Meeting Notes",
                    "source_type": "synthetic_enterprise_documents",
                    "source_url": "local_generated",
                    "retrieved_at": "2026-06-15",
                    "ingested_at": "2026-06-15T00:00:00+00:00",
                    "document_type": "synthetic_sop",
                    "title": "Empty synthetic doc",
                    "license_status": "project-generated synthetic content",
                    "is_public_source": False,
                    "is_synthetic": True,
                    "section_path": ["sop"],
                    "text": "",
                    "not_use_for": ["real_customer_data"],
                    "mvp_role": "enterprise_workflow_demo",
                    "decision": "selected_as_synthetic",
                },
            ]
            input_path.write_text(
                "\n".join(json.dumps(doc, ensure_ascii=False) for doc in docs) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "parse_documents.py"),
                    "--input",
                    str(input_path),
                    "--parsed-output",
                    str(parsed_path),
                    "--report-output",
                    str(report_path),
                    "--errors-output",
                    str(errors_path),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            parsed_rows = [json.loads(line) for line in parsed_path.read_text(encoding="utf-8").splitlines()]
            error_rows = [json.loads(line) for line in errors_path.read_text(encoding="utf-8").splitlines()]
            report = json.loads(report_path.read_text(encoding="utf-8"))

            self.assertEqual(len(parsed_rows), 1)
            self.assertEqual(parsed_rows[0]["document_id"], "doc_public")
            self.assertEqual(len(error_rows), 1)
            self.assertEqual(error_rows[0]["document_id"], "doc_bad")
            self.assertEqual(report["status"], "ok")
            self.assertEqual(report["input_document_count"], 2)
            self.assertEqual(report["parsed_document_count"], 1)
            self.assertEqual(report["parse_error_count"], 1)


if __name__ == "__main__":
    unittest.main()

