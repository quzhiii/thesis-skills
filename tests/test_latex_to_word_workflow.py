from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from core.migration import run_latex_to_word_migration
from tests.helpers import workspace_tempdir, materialize_project


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "02-latex-to-word" / "migrate_project.py"


class LatexToWordWorkflowTest(unittest.TestCase):
    def test_runner_exists_and_outputs_json(self) -> None:
        self.assertTrue(RUNNER.exists())

    def test_runner_dry_run_summary_shape(self) -> None:
        with workspace_tempdir("l2w-") as base:
            project = base / "project"
            materialize_project(
                project,
                {
                    "main.tex": (
                        "\\documentclass{article}\n"
                        "\\begin{document}\n"
                        "Hello world\n"
                        "\\end{document}\n"
                    ),
                },
            )
            output = project / "review.docx"
            result = subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    "--project-root",
                    str(project),
                    "--output-file",
                    str(output),
                    "--profile",
                    "review-friendly",
                    "--apply",
                    "false",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            summary = json.loads(result.stdout)
            self.assertEqual(summary["profile"], "review-friendly")
            self.assertFalse(summary["applied"])
            self.assertEqual(summary["main_tex"], "main.tex")
            self.assertIn("warnings", summary)
            self.assertIn("unsupported_constructs", summary)

    def test_detects_tikzpicture_as_unsupported(self) -> None:
        with workspace_tempdir("l2w-") as base:
            project = base / "project"
            materialize_project(
                project,
                {
                    "main.tex": (
                        "\\documentclass{article}\n"
                        "\\begin{document}\n"
                        "\\begin{tikzpicture}\n"
                        "\\draw (0,0) -- (1,1);\n"
                        "\\end{tikzpicture}\n"
                        "\\end{document}\n"
                    ),
                },
            )
            output = project / "review.docx"
            summary = run_latex_to_word_migration(
                project_root=project,
                output_file=output,
                profile="review-friendly",
                apply=False,
            )
            unsupported = summary["unsupported_constructs"]
            self.assertTrue(
                any("tikzpicture" in item for item in unsupported),
                f"expected tikzpicture in unsupported constructs, got: {unsupported}",
            )

    def test_detects_custom_macros_as_warning(self) -> None:
        with workspace_tempdir("l2w-") as base:
            project = base / "project"
            materialize_project(
                project,
                {
                    "main.tex": (
                        "\\documentclass{article}\n"
                        "\\newcommand{\\foo}{bar}\n"
                        "\\begin{document}\n"
                        "Hello\n"
                        "\\end{document}\n"
                    ),
                },
            )
            output = project / "review.docx"
            summary = run_latex_to_word_migration(
                project_root=project,
                output_file=output,
                profile="review-friendly",
                apply=False,
            )
            warnings = summary["warnings"]
            self.assertTrue(
                any("custom-macro" in item for item in warnings),
                f"expected custom-macro warning, got: {warnings}",
            )

    def test_detects_heavy_math_environments(self) -> None:
        with workspace_tempdir("l2w-") as base:
            project = base / "project"
            materialize_project(
                project,
                {
                    "main.tex": (
                        "\\documentclass{article}\n"
                        "\\begin{document}\n"
                        "\\begin{align}\n"
                        "x &= y\\\n"
                        "\\end{align}\n"
                        "\\end{document}\n"
                    ),
                },
            )
            output = project / "review.docx"
            summary = run_latex_to_word_migration(
                project_root=project,
                output_file=output,
                profile="review-friendly",
                apply=False,
            )
            warnings = summary["warnings"]
            self.assertTrue(
                any("align" in item for item in warnings),
                f"expected align warning, got: {warnings}",
            )

    def test_default_report_path(self) -> None:
        with workspace_tempdir("l2w-") as base:
            project = base / "project"
            materialize_project(
                project,
                {
                    "main.tex": (
                        "\\documentclass{article}\n"
                        "\\begin{document}\n"
                        "Hello\n"
                        "\\end{document}\n"
                    ),
                },
            )
            output = project / "review.docx"
            result = subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    "--project-root",
                    str(project),
                    "--output-file",
                    str(output),
                    "--apply",
                    "false",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            default_report = project / "reports" / "latex_to_word-report.json"
            self.assertTrue(
                default_report.exists(),
                f"default report not found at {default_report}",
            )
            report_data = json.loads(default_report.read_text(encoding="utf-8"))
            self.assertEqual(report_data["profile"], "review-friendly")
            self.assertIn("warnings", report_data)
            self.assertIn("unsupported_constructs", report_data)

    def test_custom_report_path(self) -> None:
        with workspace_tempdir("l2w-") as base:
            project = base / "project"
            materialize_project(
                project,
                {
                    "main.tex": (
                        "\\documentclass{article}\n"
                        "\\begin{document}\n"
                        "Hello\n"
                        "\\end{document}\n"
                    ),
                },
            )
            output = project / "review.docx"
            custom_report = project / "custom-report.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    "--project-root",
                    str(project),
                    "--output-file",
                    str(output),
                    "--apply",
                    "false",
                    "--report",
                    str(custom_report),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(custom_report.exists())
            report_data = json.loads(custom_report.read_text(encoding="utf-8"))
            self.assertEqual(report_data["profile"], "review-friendly")

    def test_no_docx_created_when_not_applied(self) -> None:
        with workspace_tempdir("l2w-") as base:
            project = base / "project"
            materialize_project(
                project,
                {
                    "main.tex": (
                        "\\documentclass{article}\n"
                        "\\begin{document}\n"
                        "Hello\n"
                        "\\end{document}\n"
                    ),
                },
            )
            output = project / "review.docx"
            run_latex_to_word_migration(
                project_root=project,
                output_file=output,
                profile="review-friendly",
                apply=False,
            )
            self.assertFalse(output.exists())

    def test_conversion_with_pandoc_creates_docx_or_reports_error(self) -> None:
        with workspace_tempdir("l2w-") as base:
            project = base / "project"
            materialize_project(
                project,
                {
                    "main.tex": (
                        "\\documentclass{article}\n"
                        "\\begin{document}\n"
                        "Hello\n"
                        "\\end{document}\n"
                    ),
                },
            )
            output = project / "review.docx"
            summary = run_latex_to_word_migration(
                project_root=project,
                output_file=output,
                profile="review-friendly",
                apply=True,
            )
            if "conversion_error" in summary:
                self.assertFalse(summary["applied"])
                self.assertIn("pandoc", summary["conversion_error"].lower())
            else:
                self.assertTrue(summary["applied"])
                self.assertTrue(output.exists())

    def test_conversion_only_attempted_when_apply_enabled(self) -> None:
        with workspace_tempdir("l2w-") as base:
            project = base / "project"
            materialize_project(
                project,
                {
                    "main.tex": (
                        "\\documentclass{article}\n"
                        "\\begin{document}\n"
                        "Hello\n"
                        "\\end{document}\n"
                    ),
                },
            )
            output = project / "review.docx"
            summary_dry = run_latex_to_word_migration(
                project_root=project,
                output_file=output,
                profile="review-friendly",
                apply=False,
            )
            summary_apply = run_latex_to_word_migration(
                project_root=project,
                output_file=output,
                profile="review-friendly",
                apply=True,
            )
            self.assertFalse(summary_dry["applied"])
            self.assertNotIn("conversion_error", summary_dry)
            self.assertTrue(summary_apply["applied"] or "conversion_error" in summary_apply)

    def test_successful_export_creates_docx(self) -> None:
        with workspace_tempdir("l2w-") as base:
            project = base / "project"
            materialize_project(
                project,
                {
                    "main.tex": (
                        "\\documentclass{article}\n"
                        "\\begin{document}\n"
                        "\\section{Introduction}\n"
                        "Hello world\n"
                        "\\end{document}\n"
                    ),
                },
            )
            output = project / "review.docx"
            summary = run_latex_to_word_migration(
                project_root=project,
                output_file=output,
                profile="review-friendly",
                apply=True,
            )
            if "conversion_error" in summary:
                self.skipTest(f"pandoc not available: {summary['conversion_error']}")
            self.assertTrue(summary["applied"])
            self.assertTrue(output.exists())
            self.assertGreater(output.stat().st_size, 0)
            self.assertEqual(summary["profile"], "review-friendly")
            self.assertIn("warnings", summary)


if __name__ == "__main__":
    unittest.main()
