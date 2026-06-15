from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class RetrieverBehaviorTests(unittest.TestCase):
    def test_search_chunks_ranks_overlap_and_preserves_citation(self) -> None:
        from evidenceops_public.retriever import search_chunks

        chunks = [
            {
                "chunk_id": "chunk_skill",
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
            },
            {
                "chunk_id": "chunk_sec",
                "document_id": "doc_sec",
                "source_id": "sec_edgar",
                "source_url": "https://www.sec.gov/search-filings/edgar-application-programming-interfaces",
                "license_status": "public filing data",
                "is_synthetic": False,
                "text": "SEC APIs expose public company filing history and XBRL facts.",
                "citation": {
                    "document_id": "doc_sec",
                    "section_id": "doc_sec::section::abc",
                    "source_url": "https://www.sec.gov/search-filings/edgar-application-programming-interfaces",
                    "license_status": "public filing data",
                },
            },
        ]

        result = search_chunks("skill taxonomy", chunks, top_k=2)

        self.assertEqual(result["status"], "supported")
        self.assertEqual(result["query"], "skill taxonomy")
        self.assertEqual(result["evidence_count"], 1)
        self.assertEqual(result["evidence"][0]["chunk_id"], "chunk_skill")
        self.assertEqual(result["evidence"][0]["rank"], 1)
        self.assertGreater(result["evidence"][0]["score"], 0)
        self.assertEqual(result["evidence"][0]["citation"]["source_url"], "https://services.onetcenter.org/reference/")

    def test_search_chunks_returns_unsupported_when_no_terms_match(self) -> None:
        from evidenceops_public.retriever import search_chunks

        chunks = [
            {
                "chunk_id": "chunk_sec",
                "text": "SEC APIs expose public filing history.",
                "citation": {"source_url": "https://www.sec.gov"},
            }
        ]

        result = search_chunks("protein structure ligand", chunks, top_k=3)

        self.assertEqual(result["status"], "unsupported")
        self.assertEqual(result["evidence_count"], 0)
        self.assertEqual(result["evidence"], [])
        self.assertIn("No chunk matched", result["reason"])

    def test_search_chunks_cli_writes_result_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            chunks_path = tmp / "chunks.jsonl"
            output_path = tmp / "search_result.json"
            chunk = {
                "chunk_id": "chunk_label",
                "document_id": "doc_label",
                "source_id": "dailymed",
                "source_url": "https://dailymed.nlm.nih.gov/",
                "license_status": "NLM public service",
                "is_synthetic": False,
                "text": "DailyMed labels can include boxed warning sections and drug names.",
                "citation": {
                    "document_id": "doc_label",
                    "section_id": "doc_label::section::abc",
                    "source_url": "https://dailymed.nlm.nih.gov/",
                    "license_status": "NLM public service",
                },
            }
            chunks_path.write_text(json.dumps(chunk, ensure_ascii=False) + "\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "search_chunks.py"),
                    "--chunks",
                    str(chunks_path),
                    "--query",
                    "boxed warning label",
                    "--output",
                    str(output_path),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            search_result = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(search_result["status"], "supported")
            self.assertEqual(search_result["evidence_count"], 1)
            self.assertEqual(search_result["evidence"][0]["citation"]["source_url"], "https://dailymed.nlm.nih.gov/")


if __name__ == "__main__":
    unittest.main()

