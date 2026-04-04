from __future__ import annotations

import unittest
from pathlib import Path

from core.project import ThesisProject


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "examples" / "minimal-latex-project"


class ProjectTest(unittest.TestCase):
    def test_project_discovery(self) -> None:
        project = ThesisProject.discover(
            SAMPLE,
            ["main.tex", "thesis.tex"],
            ["chapters/*.tex"],
            ["ref/refs.bib", "ref/refs-import.bib"],
        )
        self.assertEqual(project.main_tex.relative_to(SAMPLE).as_posix(), "main.tex")
        self.assertEqual(
            [path.relative_to(SAMPLE).as_posix() for path in project.chapter_files],
            ["chapters/01-introduction.tex", "chapters/02-methods.tex"],
        )
        self.assertEqual(
            project.bibliography_files[0].relative_to(SAMPLE).as_posix(), "ref/refs.bib"
        )

    def test_project_discovery_prefers_main_tex_inputs_over_backup_files(self) -> None:
        from tests.helpers import materialize_project, workspace_tempdir

        with workspace_tempdir("project-discovery-") as base:
            materialize_project(
                base,
                {
                    "main.tex": (
                        "\\documentclass{article}\n"
                        "\\begin{document}\n"
                        "\\input{data/chap01}\n"
                        "\\input{data/chap02}\n"
                        "\\end{document}\n"
                    ),
                    "data/chap01.tex": "A\n",
                    "data/chap02.tex": "B\n",
                    "data/chap01.bak1.tex": "backup\n",
                    "data/from_word_full.tex": "merged\n",
                    "ref/refs.bib": "@article{ref1,\n  title = {Reference One},\n}\n",
                },
            )
            project = ThesisProject.discover(
                base,
                ["main.tex", "thesis.tex"],
                ["data/*.tex"],
                ["ref/refs.bib"],
            )

        self.assertEqual(
            [path.relative_to(base).as_posix() for path in project.chapter_files],
            ["data/chap01.tex", "data/chap02.tex"],
        )


if __name__ == "__main__":
    unittest.main()
