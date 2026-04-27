from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from tests.helpers import materialize_project, workspace_tempdir


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "17-defense-pack" / "generate_candidate_tables_diagrams.py"


class CandidateTablesDiagramsTest(unittest.TestCase):
    def test_generate_candidate_tables_diagrams_artifact(self) -> None:
        with workspace_tempdir("candidate-tables-diagrams-") as base:
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
                        "\\begin{table}\n"
                        "\\caption{Baseline characteristics}\n"
                        "\\label{tab:baseline}\n"
                        "\\begin{tabular}{ll}\n"
                        "A & B \\\n"
                        "\\end{tabular}\n"
                        "\\end{table}\n"
                    ),
                    "chapters/02-method.tex": (
                        "\\chapter{Method}\n"
                        "\\begin{figure}\n"
                        "\\includegraphics{figures/study-pipeline.pdf}\n"
                        "\\caption{Study pipeline}\n"
                        "\\label{fig:study-pipeline}\n"
                        "\\end{figure}\n"
                    ),
                    "chapters/03-results.tex": (
                        "\\chapter{Results}\n"
                        "\\begin{figure}\n"
                        "\\includegraphics{figures/outcome-plot.png}\n"
                        "\\caption{Outcome plot}\n"
                        "\\label{fig:outcome-plot}\n"
                        "\\end{figure}\n"
                    ),
                },
            )
            artifact = project / "reports" / "candidate-tables-diagrams-artifact.json"
            result = subprocess.run(
                [sys.executable, str(RUNNER), "--project-root", str(project), "--artifact", str(artifact)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(artifact.read_text(encoding="utf-8"))

        self.assertEqual(payload["artifact_type"], "candidate_tables_diagrams")
        self.assertEqual(payload["summary"]["chapter_count"], 3)
        self.assertEqual(payload["summary"]["table_count"], 1)
        self.assertEqual(payload["summary"]["diagram_count"], 1)
        self.assertEqual(payload["summary"]["candidate_count"], 2)
        self.assertIn("tables", payload["payload"])
        self.assertIn("diagrams", payload["payload"])
        self.assertEqual(len(payload["payload"]["tables"]), 1)
        self.assertEqual(len(payload["payload"]["diagrams"]), 1)

        table = payload["payload"]["tables"][0]
        self.assertEqual(table["chapter"], "Introduction")
        self.assertEqual(table["source_chapter"], "chapters/01-introduction.tex")
        self.assertEqual(table["caption"], "Baseline characteristics")
        self.assertEqual(table["label"], "tab:baseline")
        self.assertGreaterEqual(table["source_line"], 1)

        diagram = payload["payload"]["diagrams"][0]
        self.assertEqual(diagram["chapter"], "Method")
        self.assertEqual(diagram["source_chapter"], "chapters/02-method.tex")
        self.assertEqual(diagram["caption"], "Study pipeline")
        self.assertEqual(diagram["label"], "fig:study-pipeline")
        self.assertEqual(diagram["asset_paths"], ["figures/study-pipeline.pdf"])
        self.assertEqual(diagram["candidate_reason"], "caption_keyword:pipeline")

    def test_inventory_remains_bounded_and_uses_asset_based_diagram_signal(self) -> None:
        with workspace_tempdir("candidate-tables-diagrams-") as base:
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
                        "% \\begin{table}\n"
                        "% \\caption{Commented table}\n"
                        "% \\end{table}\n"
                        "\\begin{table*}\n"
                        "\\caption[Short]{\\textit{Primary} endpoints}\n"
                        "\\end{table*}\n"
                    ),
                    "chapters/02-method.tex": (
                        "\\chapter{Method}\n"
                        "\\begin{figure*}\n"
                        "\\includegraphics{figures/architecture-overview.pdf}\n"
                        "\\caption{\\textbf{Main} visual}\n"
                        "\\end{figure*}\n"
                    ),
                    "chapters/03-results.tex": (
                        "\\chapter{Results}\n"
                        "\\begin{figure}\n"
                        "\\includegraphics{figures/outcome-plot.png}\n"
                        "\\caption{Outcome plot}\n"
                        "\\label{fig:outcome-plot}\n"
                        "\\end{figure}\n"
                    ),
                },
            )
            artifact = project / "reports" / "candidate-tables-diagrams-artifact.json"
            subprocess.run(
                [sys.executable, str(RUNNER), "--project-root", str(project), "--artifact", str(artifact)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
            payload = json.loads(artifact.read_text(encoding="utf-8"))

        self.assertEqual(len(payload["payload"]["tables"]), 1)
        self.assertEqual(len(payload["payload"]["diagrams"]), 1)

        table = payload["payload"]["tables"][0]
        self.assertEqual(table["caption"], "Primary endpoints")
        self.assertEqual(table["label"], "")

        diagram = payload["payload"]["diagrams"][0]
        self.assertEqual(diagram["caption"], "Main visual")
        self.assertEqual(diagram["label"], "")
        self.assertEqual(diagram["asset_paths"], ["figures/architecture-overview.pdf"])
        self.assertEqual(diagram["candidate_reason"], "asset_keyword:architecture")

        for item in payload["payload"]["tables"]:
            self.assertIn("chapter", item)
            self.assertIn("source_chapter", item)
            self.assertIn("source_line", item)
            self.assertIn("caption", item)
            self.assertIn("label", item)

        for item in payload["payload"]["diagrams"]:
            self.assertIn("chapter", item)
            self.assertIn("source_chapter", item)
            self.assertIn("source_line", item)
            self.assertIn("caption", item)
            self.assertIn("label", item)
            self.assertIn("asset_paths", item)
            self.assertIn("candidate_reason", item)


if __name__ == "__main__":
    unittest.main()
