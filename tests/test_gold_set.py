from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class GoldSetBehaviorTests(unittest.TestCase):
    def test_build_gold_sets_has_required_counts_and_traceability(self) -> None:
        from evidenceops_public.gold_set import build_gold_sets

        chunks = [
            {
                "chunk_id": "chunk_onet",
                "document_id": "doc_onet",
                "source_id": "onet",
                "source_url": "https://services.onetcenter.org/reference/",
                "license_status": "license agreement",
                "is_synthetic": False,
                "text": "O*NET supports skill taxonomy and software skills metadata.",
                "citation": {
                    "document_id": "doc_onet",
                    "section_id": "doc_onet::section::abc",
                    "source_url": "https://services.onetcenter.org/reference/",
                    "license_status": "license agreement",
                },
            },
            {
                "chunk_id": "chunk_sop",
                "document_id": "doc_sop",
                "source_id": "synthetic_enterprise_docs",
                "source_url": "local_generated",
                "license_status": "project-generated synthetic content",
                "is_synthetic": True,
                "text": "The system must retrieve source-backed evidence and attach citation metadata.",
                "citation": {
                    "document_id": "doc_sop",
                    "section_id": "doc_sop::section::abc",
                    "source_url": "local_generated",
                    "license_status": "project-generated synthetic content",
                },
            },
        ]
        extractions = [
            {
                "extraction_id": "extract_skill",
                "chunk_id": "chunk_onet",
                "field_type": "skill_signal",
                "field_value": "skill taxonomy",
                "evidence_span": "skill taxonomy",
                "citation": chunks[0]["citation"],
            },
            {
                "extraction_id": "extract_workflow",
                "chunk_id": "chunk_sop",
                "field_type": "workflow_signal",
                "field_value": "citation metadata",
                "evidence_span": "citation metadata",
                "citation": chunks[1]["citation"],
            },
        ]

        retrieval_cases, extraction_cases, manifest = build_gold_sets(chunks, extractions)

        self.assertGreaterEqual(len(retrieval_cases), 20)
        self.assertGreaterEqual(len(extraction_cases), 50)
        self.assertEqual(manifest["retrieval_case_count"], len(retrieval_cases))
        self.assertEqual(manifest["extraction_case_count"], len(extraction_cases))
        self.assertTrue(all(case["case_id"] for case in retrieval_cases))
        self.assertTrue(all(case["case_id"] for case in extraction_cases))
        self.assertTrue(
            all(case["expected_chunk_ids"] for case in retrieval_cases if case["expected_status"] == "supported")
        )
        self.assertTrue(
            all(
                case["citation"]["source_url"]
                for case in extraction_cases
                if case["expected_present"] is True
            )
        )
        self.assertTrue(any(case["expected_status"] == "unsupported" for case in retrieval_cases))
        self.assertTrue(any(case["expected_present"] is False for case in extraction_cases))

    def test_build_gold_set_cli_writes_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            chunks_path = tmp / "chunks.jsonl"
            extractions_path = tmp / "extractions.jsonl"
            retrieval_output = tmp / "retrieval_gold_set.jsonl"
            extraction_output = tmp / "extraction_gold_set.jsonl"
            manifest_output = tmp / "gold_set_manifest.json"
            chunks = [
                {
                    "chunk_id": "chunk_onet",
                    "document_id": "doc_onet",
                    "source_id": "onet",
                    "source_url": "https://services.onetcenter.org/reference/",
                    "license_status": "license agreement",
                    "is_synthetic": False,
                    "text": "O*NET supports skill taxonomy and software skills metadata.",
                    "citation": {
                        "document_id": "doc_onet",
                        "section_id": "doc_onet::section::abc",
                        "source_url": "https://services.onetcenter.org/reference/",
                        "license_status": "license agreement",
                    },
                }
            ]
            extractions = [
                {
                    "extraction_id": "extract_skill",
                    "chunk_id": "chunk_onet",
                    "field_type": "skill_signal",
                    "field_value": "skill taxonomy",
                    "evidence_span": "skill taxonomy",
                    "citation": chunks[0]["citation"],
                }
            ]
            chunks_path.write_text("\n".join(json.dumps(row) for row in chunks) + "\n", encoding="utf-8")
            extractions_path.write_text("\n".join(json.dumps(row) for row in extractions) + "\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_gold_set.py"),
                    "--chunks",
                    str(chunks_path),
                    "--extractions",
                    str(extractions_path),
                    "--retrieval-output",
                    str(retrieval_output),
                    "--extraction-output",
                    str(extraction_output),
                    "--manifest-output",
                    str(manifest_output),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            retrieval_cases = [json.loads(line) for line in retrieval_output.read_text(encoding="utf-8").splitlines()]
            extraction_cases = [json.loads(line) for line in extraction_output.read_text(encoding="utf-8").splitlines()]
            manifest = json.loads(manifest_output.read_text(encoding="utf-8"))

            self.assertGreaterEqual(len(retrieval_cases), 20)
            self.assertGreaterEqual(len(extraction_cases), 50)
            self.assertEqual(manifest["status"], "ok")


if __name__ == "__main__":
    unittest.main()

