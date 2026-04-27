from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from tests.helpers import materialize_project, workspace_tempdir


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "17-defense-pack" / "generate_outline.py"


class DefenseOutlineTest(unittest.TestCase):
    def test_generate_defense_outline_artifact(self) -> None:
        with workspace_tempdir("defense-outline-") as base:
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
                        "研究背景。\n"
                        "研究问题。\n"
                    ),
                    "chapters/02-method.tex": (
                        "\\chapter{Method}\n"
                        "方法设计。\n"
                        "实验流程。\n"
                    ),
                    "chapters/03-results.tex": (
                        "\\chapter{Results}\n"
                        "实验结果。\n"
                        "结论摘要。\n"
                    ),
                },
            )
            artifact = project / "reports" / "defense-outline-artifact.json"
            result = subprocess.run(
                [sys.executable, str(RUNNER), "--project-root", str(project), "--artifact", str(artifact)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(artifact.read_text(encoding="utf-8"))

        self.assertEqual(payload["artifact_type"], "defense_outline")
        self.assertEqual(payload["summary"]["chapter_count"], 3)
        self.assertEqual(payload["summary"]["outline_sections"], 3)
        self.assertEqual(payload["summary"]["source_chapter_count"], 3)
        self.assertIn("sections", payload["payload"])
        self.assertEqual(len(payload["payload"]["sections"]), 3)

        intro = payload["payload"]["sections"][0]
        self.assertEqual(intro["section"], "Introduction")
        self.assertEqual(intro["source_chapters"], ["chapters/01-introduction.tex"])
        self.assertTrue(intro["key_points"])
        self.assertLessEqual(len(intro["key_points"]), 3)

    def test_outline_sections_remain_bounded(self) -> None:
        with workspace_tempdir("defense-outline-") as base:
            project = materialize_project(
                base / "project",
                {
                    "main.tex": (
                        "\\documentclass{report}\n"
                        "\\begin{document}\n"
                        "\\input{chapters/01-introduction}\n"
                        "\\input{chapters/02-method}\n"
                        "\\end{document}\n"
                    ),
                    "chapters/01-introduction.tex": (
                        "\\chapter{Introduction}\n"
                        "第一句。\n第二句。\n第三句。\n第四句。\n"
                    ),
                    "chapters/02-method.tex": (
                        "\\chapter{Method}\n"
                        "方法一句。\n方法二句。\n方法三句。\n"
                    ),
                },
            )
            artifact = project / "reports" / "defense-outline-artifact.json"
            subprocess.run(
                [sys.executable, str(RUNNER), "--project-root", str(project), "--artifact", str(artifact)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
            payload = json.loads(artifact.read_text(encoding="utf-8"))

        for section in payload["payload"]["sections"]:
            self.assertIn("section", section)
            self.assertIn("source_chapters", section)
            self.assertIn("key_points", section)
            self.assertLessEqual(len(section["key_points"]), 3)
            self.assertTrue(all(isinstance(item, str) and item for item in section["key_points"]))


if __name__ == "__main__":
    unittest.main()
