from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class StaticSiteBehaviorTests(unittest.TestCase):
    def test_build_static_payload_contains_summary_and_default_search(self) -> None:
        from evidenceops_public.static_site import build_static_payload

        payload = build_static_payload(ROOT)

        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["default_search"]["search"]["status"], "supported")
        self.assertIn("eval", payload["summary"])
        self.assertIn("risk", payload["default_search"])
        self.assertGreaterEqual(payload["summary"]["eval"]["dataset_size"]["retrieval_cases"], 20)

    def test_render_static_index_contains_embedded_data_file_reference(self) -> None:
        from evidenceops_public.static_site import render_static_index

        html = render_static_index()

        self.assertIn("EvidenceOps Static Console", html)
        self.assertIn("evidenceops-data.json", html)
        self.assertIn("No citation, no claim", html)

    def test_build_static_site_cli_writes_public_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "public"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_static_site.py"),
                    "--output-dir",
                    str(output_dir),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            index_path = output_dir / "index.html"
            data_path = output_dir / "evidenceops-data.json"
            nojekyll_path = output_dir / ".nojekyll"
            self.assertTrue(index_path.exists())
            self.assertTrue(data_path.exists())
            self.assertTrue(nojekyll_path.exists())
            payload = json.loads(data_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "ok")


if __name__ == "__main__":
    unittest.main()

