from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from tests.helpers import materialize_project, workspace_tempdir


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "17-defense-pack" / "generate_chapter_highlights.py"


class ChapterHighlightsTest(unittest.TestCase):
    def test_generate_chapter_highlights_artifact(self) -> None:
        with workspace_tempdir("chapter-highlights-") as base:
            project = materialize_project(
                base / "project",
                {
                    "main.tex": (
                        "\\documentclass{report}\n"
                        "\\begin{document}\n"
                        "\\input{chapters/01-introduction}\n"
                        "\\input{chapters/02-method}\n"
                        "\\input{chapters/03-results}\n"
                        "\\input{chapters/04-conclusion}\n"
                        "\\end{document}\n"
                    ),
                    "chapters/01-introduction.tex": (
                        "\\chapter{Introduction}\n"
                        "研究背景。\n"
                        "问题定义。\n"
                    ),
                    "chapters/02-method.tex": (
                        "\\chapter{Method}\n"
                        "方法设计。\n"
                        "实验流程。\n"
                    ),
                    "chapters/03-results.tex": (
                        "\\chapter{Results}\n"
                        "实验结果。\n"
                        "结果解释。\n"
                    ),
                    "chapters/04-conclusion.tex": (
                        "\\chapter{Conclusion}\n"
                        "结论摘要。\n"
                        "未来工作。\n"
                    ),
                },
            )
            artifact = project / "reports" / "chapter-highlights-artifact.json"
            result = subprocess.run(
                [sys.executable, str(RUNNER), "--project-root", str(project), "--artifact", str(artifact)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(artifact.read_text(encoding="utf-8"))

        self.assertEqual(payload["artifact_type"], "chapter_highlights")
        self.assertEqual(payload["summary"]["chapter_count"], 4)
        self.assertEqual(payload["summary"]["highlight_sections"], 4)
        self.assertIn("sections", payload["payload"])
        self.assertEqual(len(payload["payload"]["sections"]), 4)

        intro = payload["payload"]["sections"][0]
        self.assertEqual(intro["chapter"], "Introduction")
        self.assertEqual(intro["source_chapter"], "chapters/01-introduction.tex")
        self.assertEqual(intro["defense_role"], "background")
        self.assertTrue(intro["highlight_points"])
        self.assertLessEqual(len(intro["highlight_points"]), 3)

    def test_highlight_sections_remain_bounded_and_classified(self) -> None:
        with workspace_tempdir("chapter-highlights-") as base:
            project = materialize_project(
                base / "project",
                {
                    "main.tex": (
                        "\\documentclass{report}\n"
                        "\\begin{document}\n"
                        "\\input{chapters/01-introduction}\n"
                        "\\input{chapters/02-method}\n"
                        "\\input{chapters/03-results}\n"
                        "\\input{chapters/04-conclusion}\n"
                        "\\end{document}\n"
                    ),
                    "chapters/01-introduction.tex": (
                        "\\chapter{Introduction}\n"
                        "% 注释不应进入高亮\n"
                        "第一句。\n第二句。\n第三句。\n第四句。\n"
                    ),
                    "chapters/02-method.tex": (
                        "\\chapter{Method}\n"
                        "方法一句。\n方法二句。\n方法三句。\n"
                    ),
                    "chapters/03-results.tex": (
                        "\\chapter{Results and Discussion}\n"
                        "结果一句。\n结果二句。\n结果三句。\n结果四句。\n"
                    ),
                    "chapters/04-conclusion.tex": (
                        "\\chapter{Conclusion}\n"
                        "结论一句。\n结论二句。\n"
                    ),
                },
            )
            artifact = project / "reports" / "chapter-highlights-artifact.json"
            subprocess.run(
                [sys.executable, str(RUNNER), "--project-root", str(project), "--artifact", str(artifact)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
            payload = json.loads(artifact.read_text(encoding="utf-8"))

        roles = {section["chapter"]: section["defense_role"] for section in payload["payload"]["sections"]}
        self.assertEqual(roles["Introduction"], "background")
        self.assertEqual(roles["Method"], "approach")
        self.assertEqual(roles["Results and Discussion"], "evidence")
        self.assertEqual(roles["Conclusion"], "takeaway")

        for section in payload["payload"]["sections"]:
            self.assertIn("chapter", section)
            self.assertIn("source_chapter", section)
            self.assertIn("defense_role", section)
            self.assertIn("highlight_points", section)
            self.assertLessEqual(len(section["highlight_points"]), 3)
            self.assertTrue(all(isinstance(item, str) and item for item in section["highlight_points"]))


if __name__ == "__main__":
    unittest.main()
