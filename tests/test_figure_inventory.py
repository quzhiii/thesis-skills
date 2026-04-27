from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from tests.helpers import materialize_project, workspace_tempdir


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "17-defense-pack" / "generate_figure_inventory.py"


class FigureInventoryTest(unittest.TestCase):
    def test_generate_figure_inventory_artifact(self) -> None:
        with workspace_tempdir("figure-inventory-") as base:
            project = materialize_project(
                base / "project",
                {
                    "main.tex": (
                        "\\documentclass{report}\n"
                        "\\begin{document}\n"
                        "\\input{chapters/01-introduction}\n"
                        "\\input{chapters/02-method}\n"
                        "\\input{chapters/03-results}\n"
                        "\\end{document}\n"
                    ),
                    "chapters/01-introduction.tex": (
                        "\\chapter{Introduction}\n"
                        "引言内容。\n"
                        "\\begin{figure}\n"
                        "\\centering\n"
                        "\\includegraphics[width=0.8\\textwidth]{figures/system-overview.pdf}\n"
                        "\\caption{System overview}\n"
                        "\\label{fig:system-overview}\n"
                        "\\end{figure}\n"
                    ),
                    "chapters/02-method.tex": (
                        "\\chapter{Method}\n"
                        "方法内容。\n"
                        "\\begin{figure}\n"
                        "\\includegraphics{figures/pipeline-a.png}\n"
                        "\\includegraphics{figures/pipeline-b.png}\n"
                        "\\caption{Study pipeline}\n"
                        "\\label{fig:study-pipeline}\n"
                        "\\end{figure}\n"
                        "\\begin{table}\n"
                        "\\caption{Not a figure}\n"
                        "\\label{tab:ignored}\n"
                        "\\end{table}\n"
                    ),
                    "chapters/03-results.tex": (
                        "\\chapter{Results}\n"
                        "结果内容。\n"
                    ),
                },
            )
            artifact = project / "reports" / "figure-inventory-artifact.json"
            result = subprocess.run(
                [sys.executable, str(RUNNER), "--project-root", str(project), "--artifact", str(artifact)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(artifact.read_text(encoding="utf-8"))

        self.assertEqual(payload["artifact_type"], "figure_inventory")
        self.assertEqual(payload["summary"]["chapter_count"], 3)
        self.assertEqual(payload["summary"]["figure_count"], 2)
        self.assertEqual(payload["summary"]["chapters_with_figures"], 2)
        self.assertIn("figures", payload["payload"])
        self.assertEqual(len(payload["payload"]["figures"]), 2)

        intro = payload["payload"]["figures"][0]
        self.assertEqual(intro["chapter"], "Introduction")
        self.assertEqual(intro["source_chapter"], "chapters/01-introduction.tex")
        self.assertEqual(intro["caption"], "System overview")
        self.assertEqual(intro["label"], "fig:system-overview")
        self.assertEqual(intro["asset_paths"], ["figures/system-overview.pdf"])
        self.assertGreaterEqual(intro["source_line"], 1)

    def test_figure_inventory_remains_bounded_to_figures_and_cleans_fields(self) -> None:
        with workspace_tempdir("figure-inventory-") as base:
            project = materialize_project(
                base / "project",
                {
                    "main.tex": (
                        "\\documentclass{report}\n"
                        "\\begin{document}\n"
                        "\\input{chapters/01-introduction}\n"
                        "\\input{chapters/02-results}\n"
                        "\\end{document}\n"
                    ),
                    "chapters/01-introduction.tex": (
                        "\\chapter{Introduction}\n"
                        "% \\begin{figure}\n"
                        "% \\includegraphics{figures/commented-out.pdf}\n"
                        "% \\caption{Commented out}\n"
                        "% \\end{figure}\n"
                        "\\begin{figure*}\n"
                        "\\includegraphics[width=0.45\\textwidth]{figures/roc-a.pdf}\n"
                        "\\includegraphics[width=0.45\\textwidth]{figures/roc-b.pdf}\n"
                        "\\caption[Short]{\\textbf{ROC} comparison}\n"
                        "\\end{figure*}\n"
                    ),
                    "chapters/02-results.tex": (
                        "\\chapter{Results}\n"
                        "\\begin{table}\n"
                        "\\caption{Ignored table}\n"
                        "\\end{table}\n"
                        "\\begin{figure}\n"
                        "\\caption{Outcome plot}\n"
                        "\\label{fig:outcome-plot}\n"
                        "\\includegraphics{figures/outcome-plot.png}\n"
                        "\\end{figure}\n"
                    ),
                },
            )
            artifact = project / "reports" / "figure-inventory-artifact.json"
            subprocess.run(
                [sys.executable, str(RUNNER), "--project-root", str(project), "--artifact", str(artifact)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
            payload = json.loads(artifact.read_text(encoding="utf-8"))

        figures = payload["payload"]["figures"]
        self.assertEqual(len(figures), 2)

        first = figures[0]
        self.assertEqual(first["caption"], "ROC comparison")
        self.assertEqual(first["label"], "")
        self.assertEqual(first["asset_paths"], ["figures/roc-a.pdf", "figures/roc-b.pdf"])

        second = figures[1]
        self.assertEqual(second["caption"], "Outcome plot")
        self.assertEqual(second["label"], "fig:outcome-plot")

        for item in figures:
            self.assertIn("chapter", item)
            self.assertIn("source_chapter", item)
            self.assertIn("source_line", item)
            self.assertIn("caption", item)
            self.assertIn("label", item)
            self.assertIn("asset_paths", item)
            self.assertTrue(isinstance(item["asset_paths"], list))


if __name__ == "__main__":
    unittest.main()
