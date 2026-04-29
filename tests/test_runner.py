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
    def test_manifest_registers_readiness_gate_module(self) -> None:
        manifest = json.loads((ROOT / "skills-manifest.json").read_text(encoding="utf-8"))
        modules = {item["id"]: item for item in manifest["modules"]}
        self.assertIn("16-check-readiness", modules)
        self.assertEqual(
            modules["16-check-readiness"]["entry"],
            "16-check-readiness/THESIS_CHECK_READINESS.md",
        )
        self.assertEqual(modules["16-check-readiness"]["type"], "checker")
        self.assertEqual(
            modules["16-check-readiness"]["runner"],
            "16-check-readiness/check_readiness.py",
        )

    def test_manifest_registers_review_loop_workflows(self) -> None:
        manifest = json.loads((ROOT / "skills-manifest.json").read_text(encoding="utf-8"))
        modules = {item["id"]: item for item in manifest["modules"]}
        self.assertIn("03-latex-review-diff", modules)
        self.assertIn("04-word-review-ingest", modules)
        self.assertEqual(
            modules["03-latex-review-diff"]["runner"],
            "03-latex-review-diff/review_diff.py",
        )
        self.assertEqual(
            modules["04-word-review-ingest"]["runner"],
            "04-word-review-ingest/feedback_ingest.py",
        )
    def test_manifest_registers_compile_checker(self) -> None:
        manifest = json.loads((ROOT / "skills-manifest.json").read_text(encoding="utf-8"))
        modules = manifest["modules"]
        compile_checker = next(
            (item for item in modules if item.get("id") == "15-check-compile"), None
        )
        self.assertIsNotNone(compile_checker)
        self.assertEqual(
            compile_checker["entry"], "15-check-compile/THESIS_CHECK_COMPILE.md"
        )
        self.assertEqual(compile_checker["type"], "checker")
        self.assertEqual(
            compile_checker["runner"], "15-check-compile/check_compile.py"
        )

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
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
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

    def test_run_check_once_reports_compile_missing_log_without_artifact(self) -> None:
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
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            data = json.loads(
                (project_root / "reports" / "run-summary.json").read_text(
                    encoding="utf-8"
                )
            )
        self.assertIn("content", data["steps"])
        self.assertEqual(data["steps"]["compile"]["status"], "missing-log")

    def test_run_check_once_parses_compile_log_when_present(self) -> None:
        with workspace_project_copy(SAMPLE, "runner-") as project_root:
            (project_root / "main.log").write_text(
                "! Undefined control sequence.\nl.42 \\fooBar\n", encoding="utf-8"
            )
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
        self.assertEqual(data["steps"]["compile"]["status"], "parsed")
        self.assertEqual(
            data["steps"]["compile"]["report"], "reports/check_compile-report.json"
        )
        self.assertIn("report_summary", data["steps"]["compile"])
        self.assertEqual(data["steps"]["compile"]["report_summary"]["errors"], 1)

    def test_run_check_once_can_focus_on_language_deep(self) -> None:
        with workspace_project_copy(SAMPLE, "runner-") as project_root:
            (project_root / "chapters" / "01-introduction.tex").write_text(
                "\\section{Introduction}\n"
                "本研究使用 DID 识别政策效应。\n"
                "本研究旨在提升效率水平。\n"
                "大型语言模型在研究中具有重要作用。\n",
                encoding="utf-8",
            )
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
        self.assertEqual(data["steps"]["compile"]["status"], "missing-log")

    def test_run_check_once_surfaces_readiness_gate_as_derived_artifact(self) -> None:
        with workspace_project_copy(SAMPLE, "runner-") as project_root:
            (project_root / "main.log").write_text(
                "! Undefined control sequence.\nl.42 \\fooBar\n", encoding="utf-8"
            )
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
            summary = json.loads(
                (project_root / "reports" / "run-summary.json").read_text(
                    encoding="utf-8"
                )
            )
            readiness_report = project_root / "reports" / "readiness-report.json"
            readiness_exists = readiness_report.exists()

        self.assertIn("derived_artifacts", summary)
        self.assertIn("readiness_gate", summary["derived_artifacts"])
        readiness = summary["derived_artifacts"]["readiness_gate"]
        self.assertEqual(readiness["mode"], "advisor-handoff")
        self.assertEqual(readiness["report"], "reports/readiness-report.json")
        self.assertIn("overall_verdict", readiness)
        self.assertTrue(readiness_exists)


if __name__ == "__main__":
    unittest.main()
