from __future__ import annotations

import json
import unittest

from core.checkers import run_content_check
from core.project import ThesisProject
from core.rules import load_rule_pack
from tests.helpers import materialize_project, workspace_tempdir
from tests.test_rules import PACK_ROOT


class ContentCheckTest(unittest.TestCase):
    def test_tsinghua_chinese_required_sections_pass(self) -> None:
        pack = load_rule_pack(PACK_ROOT / "tsinghua-thesis")
        with workspace_tempdir("content-check-zh-") as base:
            materialize_project(
                base,
                {
                    "论文初稿.tex": (
                        "\\documentclass{thuthesis}\n"
                        "\\begin{document}\n"
                        "\\input{chapters/chap01}\n"
                        "\\input{chapters/chap03}\n"
                        "\\end{document}\n"
                    ),
                    "chapters/chap01.tex": "\\chapter{绪论}\n\\section{绪论}\n",
                    "chapters/chap03.tex": "\\chapter{研究方法}\n\\section{研究方法}\n",
                    "ref/refs.bib": "@article{ref1,\n  title = {Reference One},\n}\n",
                },
            )
            project = ThesisProject.discover(
                base,
                pack.rules["project"]["main_tex_candidates"],
                pack.rules["project"]["chapter_globs"],
                pack.rules["project"]["bibliography_files"],
            )
            report = base / "reports" / "check_content-report.json"
            exit_code = run_content_check(project, pack, report)
            data = json.loads(report.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0)
        self.assertEqual(data["summary"]["errors"], 0)
        self.assertEqual(data["findings"], [])

    def test_content_check_reports_missing_chinese_required_section(self) -> None:
        pack = load_rule_pack(PACK_ROOT / "tsinghua-thesis")
        with workspace_tempdir("content-check-missing-zh-") as base:
            materialize_project(
                base,
                {
                    "论文初稿.tex": (
                        "\\documentclass{thuthesis}\n"
                        "\\begin{document}\n"
                        "\\input{chapters/chap01}\n"
                        "\\end{document}\n"
                    ),
                    "chapters/chap01.tex": "\\chapter{绪论}\n\\section{绪论}\n",
                    "ref/refs.bib": "@article{ref1,\n  title = {Reference One},\n}\n",
                },
            )
            project = ThesisProject.discover(
                base,
                pack.rules["project"]["main_tex_candidates"],
                pack.rules["project"]["chapter_globs"],
                pack.rules["project"]["bibliography_files"],
            )
            report = base / "reports" / "check_content-report.json"
            exit_code = run_content_check(project, pack, report)
            data = json.loads(report.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 1)
        messages = [finding["message"] for finding in data["findings"]]
        self.assertIn("Required section not found: 研究方法", messages)


if __name__ == "__main__":
    unittest.main()
