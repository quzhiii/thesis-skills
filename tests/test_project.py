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


if __name__ == "__main__":
    unittest.main()
