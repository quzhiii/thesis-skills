from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from tests.helpers import materialize_project, workspace_tempdir


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "17-defense-pack" / "generate_talk_prep_notes.py"


class TalkPrepNotesTest(unittest.TestCase):
    def test_generate_talk_prep_notes_artifact(self) -> None:
        with workspace_tempdir("talk-prep-notes-") as base:
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
                        "研究问题。\n"
                    ),
                    "chapters/02-method.tex": (
                        "\\chapter{Method}\n"
                        "方法设计。\n"
                        "实验流程。\n"
                        "\\begin{figure}\n"
                        "\\includegraphics{figures/study-pipeline.pdf}\n"
                        "\\caption{Study pipeline}\n"
                        "\\label{fig:study-pipeline}\n"
                        "\\end{figure}\n"
                    ),
                    "chapters/03-results.tex": (
                        "\\chapter{Results}\n"
                        "实验结果。\n"
                        "结果解释。\n"
                        "\\begin{table}\n"
                        "\\caption{Primary outcomes}\n"
                        "\\label{tab:outcomes}\n"
                        "\\end{table}\n"
                    ),
                    "chapters/04-conclusion.tex": (
                        "\\chapter{Conclusion}\n"
                        "结论摘要。\n"
                        "未来工作。\n"
                    ),
                },
            )
            artifact = project / "reports" / "talk-prep-notes-artifact.json"
            result = subprocess.run(
                [sys.executable, str(RUNNER), "--project-root", str(project), "--artifact", str(artifact)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(artifact.read_text(encoding="utf-8"))

        self.assertEqual(payload["artifact_type"], "talk_prep_notes")
        self.assertEqual(payload["summary"]["chapter_count"], 4)
        self.assertEqual(payload["summary"]["note_count"], 4)
        self.assertIn("notes", payload["payload"])
        self.assertEqual(len(payload["payload"]["notes"]), 4)

        intro = payload["payload"]["notes"][0]
        self.assertEqual(intro["chapter"], "Introduction")
        self.assertEqual(intro["defense_role"], "background")
        self.assertEqual(intro["talk_goal"], "Set up the research context and question.")
        self.assertTrue(intro["talking_points"])
        self.assertLessEqual(len(intro["talking_points"]), 3)
        self.assertEqual(intro["visual_candidates"], [])
        self.assertTrue(isinstance(intro["transition_note"], str) and intro["transition_note"])

        method = payload["payload"]["notes"][1]
        self.assertEqual(method["visual_candidates"], ["fig:study-pipeline"])

        results = payload["payload"]["notes"][2]
        self.assertEqual(results["visual_candidates"], ["tab:outcomes"])

    def test_talk_prep_notes_remain_bounded_and_ordered(self) -> None:
        with workspace_tempdir("talk-prep-notes-") as base:
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
                        "% 注释不能进入 talking points\n"
                        "第一句。\n第二句。\n第三句。\n第四句。\n"
                    ),
                    "chapters/02-method.tex": (
                        "\\chapter{Method}\n"
                        "方法一句。\n方法二句。\n"
                        "\\begin{figure*}\n"
                        "\\includegraphics{figures/architecture-overview.pdf}\n"
                        "\\caption{Architecture overview}\n"
                        "\\label{fig:architecture}\n"
                        "\\end{figure*}\n"
                    ),
                    "chapters/03-results.tex": (
                        "\\chapter{Results and Discussion}\n"
                        "结果一句。\n结果二句。\n结果三句。\n"
                        "\\begin{table}\n"
                        "\\caption{Main outcomes}\n"
                        "\\label{tab:main-outcomes}\n"
                        "\\end{table}\n"
                    ),
                },
            )
            artifact = project / "reports" / "talk-prep-notes-artifact.json"
            subprocess.run(
                [sys.executable, str(RUNNER), "--project-root", str(project), "--artifact", str(artifact)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
            payload = json.loads(artifact.read_text(encoding="utf-8"))

        notes = payload["payload"]["notes"]
        self.assertEqual([item["chapter"] for item in notes], ["Introduction", "Method", "Results and Discussion"])

        goals = {item["chapter"]: item["talk_goal"] for item in notes}
        self.assertEqual(goals["Introduction"], "Set up the research context and question.")
        self.assertEqual(goals["Method"], "Explain the approach and why it is credible.")
        self.assertEqual(goals["Results and Discussion"], "Present the evidence and the main takeaways.")

        for note in notes:
            self.assertIn("chapter", note)
            self.assertIn("defense_role", note)
            self.assertIn("talk_goal", note)
            self.assertIn("talking_points", note)
            self.assertIn("visual_candidates", note)
            self.assertIn("transition_note", note)
            self.assertLessEqual(len(note["talking_points"]), 3)
            self.assertTrue(all(isinstance(item, str) and item for item in note["talking_points"]))
            self.assertTrue(isinstance(note["visual_candidates"], list))


if __name__ == "__main__":
    unittest.main()
