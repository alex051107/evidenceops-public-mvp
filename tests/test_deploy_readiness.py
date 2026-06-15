from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class DeployReadinessBehaviorTests(unittest.TestCase):
    def clean_pycache(self) -> None:
        for path in ROOT.rglob("__pycache__"):
            if path.is_dir():
                shutil.rmtree(path)

    def test_check_deploy_readiness_passes_for_current_project(self) -> None:
        self.clean_pycache()
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check_deploy_readiness.py"), "--root", str(ROOT)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn('"status": "ok"', result.stdout)

    def test_check_deploy_readiness_fails_when_public_index_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            shutil.copytree(ROOT / "public", tmp / "public")
            for filename in ["Dockerfile", "render.yaml"]:
                shutil.copy2(ROOT / filename, tmp / filename)
            (tmp / "data" / "eval").mkdir(parents=True)
            (tmp / "data" / "eval" / "eval_report.json").write_text("{}", encoding="utf-8")
            (tmp / "data" / "eval" / "failure_taxonomy.json").write_text("{}", encoding="utf-8")
            (tmp / "data" / "eval" / "ablation_report.json").write_text("{}", encoding="utf-8")
            (tmp / "public" / "index.html").unlink()

            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "check_deploy_readiness.py"), "--root", str(tmp)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("public/index.html", result.stdout)


if __name__ == "__main__":
    unittest.main()
