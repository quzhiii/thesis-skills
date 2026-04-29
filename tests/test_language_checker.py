from __future__ import annotations

import json
import unittest
from pathlib import Path

from core.checkers import run_language_check
from core.project import ThesisProject
from core.rules import load_rule_pack
from tests.helpers import materialize_project, workspace_tempdir


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "90-rules" / "packs" / "university-generic"
SAMPLE = ROOT / "examples" / "minimal-latex-project"


def _language_issue_project(root: Path) -> Path:
    return materialize_project(
        root,
        {
            "main.tex": (
                "\\documentclass{article}\n"
                "\\begin{document}\n"
                "\\input{chapters/01-introduction}\n"
                "\\end{document}\n"
            ),
            "chapters/01-introduction.tex": "\\section{Introduction}\n这是Example文本。。\n",
            "ref/refs.bib": (
                "@article{ref1,\n"
                "  title = {Reference One},\n"
                "  author = {Doe, Jane},\n"
                "  year = {2024}\n"
                "}\n"
            ),
        },
    )


class LanguageCheckerTest(unittest.TestCase):
    def test_language_check_uses_yaml_flags(self) -> None:
        rules = load_rule_pack(PACK)
        with workspace_tempdir("language-checker-") as tmp:
            project_root = _language_issue_project(tmp / "sample")
            project = ThesisProject.discover(
                project_root,
                rules.rules["project"]["main_tex_candidates"],
                rules.rules["project"]["chapter_globs"],
                rules.rules["project"]["bibliography_files"],
            )
            report_path = tmp / "language-report.json"
            exit_code = run_language_check(project, rules, report_path)
            report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(exit_code, 1)
        self.assertEqual(report["summary"]["checker"], "check_language")
        self.assertEqual(report["summary"]["ruleset"], "university-generic")
        codes = {item["code"] for item in report["findings"]}
        self.assertIn("LANG_CJK_LATIN_SPACING", codes)
        self.assertIn("LANG_REPEAT_PUNC", codes)
        finding = next(
            item
            for item in report["findings"]
            if item["code"] == "LANG_CJK_LATIN_SPACING"
        )
        self.assertIn("file", finding)
        self.assertGreater(finding["line"], 0)
        self.assertTrue(finding["message"])

    def test_language_check_respects_disabled_rule(self) -> None:
        rules = load_rule_pack(PACK)
        rules.rules["language"]["repeated_punctuation"]["enabled"] = False
        project = ThesisProject.discover(
            SAMPLE,
            rules.rules["project"]["main_tex_candidates"],
            rules.rules["project"]["chapter_globs"],
            rules.rules["project"]["bibliography_files"],
        )
        with workspace_tempdir("language-checker-") as tmp:
            report_path = tmp / "language-report.json"
            run_language_check(project, rules, report_path)
            report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["summary"]["checker"], "check_language")
        codes = {item["code"] for item in report["findings"]}
        self.assertNotIn("LANG_REPEAT_PUNC", codes)


if __name__ == "__main__":
    unittest.main()
