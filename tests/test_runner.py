from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from tests.helpers import workspace_project_copy


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "examples" / "minimal-latex-project"


class RunnerTest(unittest.TestCase):
    def test_run_check_once_generates_summary(self) -> None:
        with workspace_project_copy(SAMPLE, "runner-") as project_root:
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "run_check_once.py"),
                    "--project-root",
                    str(project_root),
                    "--ruleset",
                    "university-generic",
                    "--skip-compile",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            summary = project_root / "reports" / "run-summary.json"
            self.assertTrue(summary.exists())
            data = json.loads(summary.read_text(encoding="utf-8"))
        self.assertEqual(data["ruleset"], "university-generic")
        self.assertEqual(
            list(data["steps"]),
            [
                "bib-quality",
                "references",
                "language",
                "language-deep",
                "format",
                "content",
                "compile",
            ],
        )
        self.assertIn("language", data["steps"])
        self.assertIn("language-deep", data["steps"])
        self.assertEqual(
            data["steps"]["language"]["report"], "reports/check_language-report.json"
        )
        self.assertEqual(
            data["steps"]["language-deep"]["report"],
            "reports/check_language_deep-report.json",
        )
        self.assertIn("report_summary", data["steps"]["language-deep"])
        self.assertEqual(
            data["steps"]["language-deep"]["report_summary"]["coverage_mode"],
            "partial_latex_aware_screening",
        )
        self.assertEqual(data["steps"]["compile"]["status"], "skipped")

    def test_run_check_once_reports_compile_unavailable_without_adapter(self) -> None:
        with workspace_project_copy(SAMPLE, "runner-") as project_root:
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "run_check_once.py"),
                    "--project-root",
                    str(project_root),
                    "--ruleset",
                    "university-generic",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            data = json.loads(
                (project_root / "reports" / "run-summary.json").read_text(
                    encoding="utf-8"
                )
            )
        self.assertIn("content", data["steps"])
        self.assertEqual(data["steps"]["compile"]["status"], "unavailable")

    def test_run_check_once_can_focus_on_language_deep(self) -> None:
        with workspace_project_copy(SAMPLE, "runner-") as project_root:
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "run_check_once.py"),
                    "--project-root",
                    str(project_root),
                    "--ruleset",
                    "university-generic",
                    "--only",
                    "language-deep",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            data = json.loads(
                (project_root / "reports" / "run-summary.json").read_text(
                    encoding="utf-8"
                )
            )
        self.assertEqual(list(data["steps"]), ["language-deep", "compile"])
        self.assertEqual(
            data["steps"]["language-deep"]["report"],
            "reports/check_language_deep-report.json",
        )
        self.assertEqual(
            data["steps"]["language-deep"]["report_summary"]["review_mode"],
            "manual_first",
        )
        self.assertEqual(data["steps"]["compile"]["status"], "unavailable")


if __name__ == "__main__":
    unittest.main()
