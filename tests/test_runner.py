from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "examples" / "minimal-latex-project"


class RunnerTest(unittest.TestCase):
    def test_run_check_once_generates_summary(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "run_check_once.py"),
                "--project-root",
                str(SAMPLE),
                "--ruleset",
                "university-generic",
                "--skip-compile",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        summary = SAMPLE / "reports" / "run-summary.json"
        self.assertTrue(summary.exists())
        data = json.loads(summary.read_text(encoding="utf-8"))
        self.assertEqual(data["ruleset"], "university-generic")
        self.assertIn("language", data["steps"])

    def test_run_check_once_reports_compile_unavailable_without_adapter(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "run_check_once.py"),
                "--project-root",
                str(SAMPLE),
                "--ruleset",
                "university-generic",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        data = json.loads(
            (SAMPLE / "reports" / "run-summary.json").read_text(encoding="utf-8")
        )
        self.assertEqual(data["steps"]["compile"]["status"], "unavailable")


if __name__ == "__main__":
    unittest.main()
