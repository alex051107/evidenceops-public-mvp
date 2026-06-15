from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class ChunkerBehaviorTests(unittest.TestCase):
    def test_chunk_document_preserves_citation_metadata(self) -> None:
        from evidenceops_public.chunker import chunk_document

        parsed_doc = {
            "document_id": "doc_sec",
            "source_id": "sec_edgar",
            "source_name": "SEC EDGAR data.sec.gov",
            "source_type": "public_enterprise_documents",
            "source_url": "https://www.sec.gov/search-filings/edgar-application-programming-interfaces",
            "retrieved_at": "2026-06-15",
            "parsed_at": "2026-06-15T00:00:00+00:00",
            "document_type": "api_doc_note",
            "title": "SEC API note",
            "license_status": "public filing data",
            "is_public_source": True,
            "is_synthetic": False,
            "not_use_for": ["investment_advice"],
            "mvp_role": "enterprise_document_mode",
            "decision": "selected",
            "sections": [
                {
                    "section_id": "doc_sec::section::abc",
                    "section_index": 0,
                    "section_path": ["api", "submissions"],
                    "heading": "api / submissions",
                    "text": "alpha beta gamma delta epsilon zeta eta theta",
                    "char_start": 0,
                    "char_end": 45,
                    "text_sha256": "placeholder",
                }
            ],
        }

        chunks = chunk_document(parsed_doc, max_words=4, overlap_words=1)

        self.assertEqual(len(chunks), 3)
        first = chunks[0]
        self.assertEqual(first["document_id"], "doc_sec")
        self.assertEqual(first["source_id"], "sec_edgar")
        self.assertEqual(first["source_url"], parsed_doc["source_url"])
        self.assertEqual(first["license_status"], "public filing data")
        self.assertFalse(first["is_synthetic"])
        self.assertEqual(first["section_id"], "doc_sec::section::abc")
        self.assertEqual(first["chunk_index"], 0)
        self.assertEqual(first["text"], "alpha beta gamma delta")
        self.assertTrue(first["chunk_id"].startswith("doc_sec::chunk::"))
        self.assertEqual(first["citation"]["document_id"], "doc_sec")
        self.assertEqual(first["citation"]["section_id"], "doc_sec::section::abc")
        self.assertEqual(first["citation"]["source_url"], parsed_doc["source_url"])
        self.assertEqual(first["citation"]["license_status"], "public filing data")
        self.assertIn("investment_advice", first["not_use_for"])

    def test_chunk_document_rejects_invalid_overlap(self) -> None:
        from evidenceops_public.chunker import ChunkingError, chunk_document

        parsed_doc = {
            "document_id": "doc_bad",
            "sections": [{"section_id": "s1", "text": "alpha beta"}],
        }

        with self.assertRaises(ChunkingError):
            chunk_document(parsed_doc, max_words=3, overlap_words=3)

    def test_chunk_documents_cli_writes_chunk_store_and_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            input_path = tmp / "parsed_documents.jsonl"
            chunks_path = tmp / "chunks.jsonl"
            report_path = tmp / "chunk_report.json"
            parsed_doc = {
                "document_id": "doc_public",
                "source_id": "onet",
                "source_name": "O*NET",
                "source_type": "public_skill_taxonomy",
                "source_url": "https://services.onetcenter.org/reference/",
                "retrieved_at": "2026-06-15",
                "parsed_at": "2026-06-15T00:00:00+00:00",
                "document_type": "api_doc_note",
                "title": "O*NET API note",
                "license_status": "license agreement",
                "is_public_source": True,
                "is_synthetic": False,
                "not_use_for": ["real_time_jd_claim"],
                "mvp_role": "skill_normalization",
                "decision": "selected",
                "sections": [
                    {
                        "section_id": "doc_public::section::abc",
                        "section_index": 0,
                        "section_path": ["api"],
                        "heading": "api",
                        "text": "one two three four five six seven eight nine ten",
                        "char_start": 0,
                        "char_end": 48,
                        "text_sha256": "placeholder",
                    }
                ],
            }
            input_path.write_text(json.dumps(parsed_doc, ensure_ascii=False) + "\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "chunk_documents.py"),
                    "--input",
                    str(input_path),
                    "--chunks-output",
                    str(chunks_path),
                    "--report-output",
                    str(report_path),
                    "--max-words",
                    "4",
                    "--overlap-words",
                    "1",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            chunks = [json.loads(line) for line in chunks_path.read_text(encoding="utf-8").splitlines()]
            report = json.loads(report_path.read_text(encoding="utf-8"))

            self.assertEqual(len(chunks), 3)
            self.assertEqual(report["status"], "ok")
            self.assertEqual(report["input_document_count"], 1)
            self.assertEqual(report["chunk_count"], 3)
            self.assertEqual(report["synthetic_chunk_count"], 0)
            self.assertEqual(chunks[0]["citation"]["source_url"], parsed_doc["source_url"])


if __name__ == "__main__":
    unittest.main()
