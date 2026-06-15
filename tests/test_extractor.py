from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class ExtractorBehaviorTests(unittest.TestCase):
    def test_extract_chunk_returns_skill_signal_with_evidence_and_citation(self) -> None:
        from evidenceops_public.extractor import extract_chunk

        chunk = {
            "chunk_id": "chunk_onet",
            "document_id": "doc_onet",
            "source_id": "onet",
            "source_url": "https://services.onetcenter.org/reference/",
            "license_status": "license agreement",
            "is_synthetic": False,
            "text": "O*NET supports occupation skill taxonomy and software skills.",
            "citation": {
                "document_id": "doc_onet",
                "section_id": "doc_onet::section::abc",
                "source_url": "https://services.onetcenter.org/reference/",
                "license_status": "license agreement",
            },
        }

        extractions = extract_chunk(chunk)

        skill_values = {
            item["field_value"]
            for item in extractions
            if item["field_type"] == "skill_signal"
        }
        self.assertIn("skill taxonomy", skill_values)
        self.assertIn("software skills", skill_values)
        first = extractions[0]
        self.assertEqual(first["chunk_id"], "chunk_onet")
        self.assertEqual(first["citation"]["source_url"], "https://services.onetcenter.org/reference/")
        self.assertIn(first["evidence_span"], chunk["text"])
        self.assertGreaterEqual(first["evidence_char_start"], 0)
        self.assertGreater(first["evidence_char_end"], first["evidence_char_start"])

    def test_extract_chunk_returns_empty_when_no_rule_matches(self) -> None:
        from evidenceops_public.extractor import extract_chunk

        chunk = {
            "chunk_id": "chunk_none",
            "text": "Alpha beta gamma.",
            "citation": {},
        }

        self.assertEqual(extract_chunk(chunk), [])

    def test_extract_fields_cli_writes_extractions_and_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            chunks_path = tmp / "chunks.jsonl"
            output_path = tmp / "extractions.jsonl"
            report_path = tmp / "extraction_report.json"
            chunk = {
                "chunk_id": "chunk_sop",
                "document_id": "doc_sop",
                "source_id": "synthetic_enterprise_docs",
                "source_url": "local_generated",
                "license_status": "project-generated synthetic content",
                "is_synthetic": True,
                "text": "The system must retrieve source-backed evidence, attach citation metadata, and mark unsupported claims.",
                "citation": {
                    "document_id": "doc_sop",
                    "section_id": "doc_sop::section::abc",
                    "source_url": "local_generated",
                    "license_status": "project-generated synthetic content",
                },
            }
            chunks_path.write_text(json.dumps(chunk, ensure_ascii=False) + "\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "extract_fields.py"),
                    "--chunks",
                    str(chunks_path),
                    "--output",
                    str(output_path),
                    "--report-output",
                    str(report_path),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            rows = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines()]
            report = json.loads(report_path.read_text(encoding="utf-8"))

            self.assertGreaterEqual(len(rows), 3)
            self.assertEqual(report["status"], "ok")
            self.assertEqual(report["input_chunk_count"], 1)
            self.assertEqual(report["matched_chunk_count"], 1)
            self.assertIn("workflow_signal", report["field_type_counts"])
            self.assertTrue(all(row["citation"]["source_url"] == "local_generated" for row in rows))


if __name__ == "__main__":
    unittest.main()

