from __future__ import annotations

import json
import unittest
from pathlib import Path

from core.checkers import run_language_check
from core.project import ThesisProject
from core.rules import load_rule_pack
from tests.helpers import materialize_project, workspace_tempdir


ROOT = Path(__file__).resolve().parents[1]
PACK_ROOT = ROOT / "90-rules" / "packs"


def _discover_project(project_root: Path, pack_name: str) -> tuple[ThesisProject, object]:
    pack = load_rule_pack(PACK_ROOT / pack_name)
    project = ThesisProject.discover(
        project_root,
        pack.rules["project"]["main_tex_candidates"],
        pack.rules["project"]["chapter_globs"],
        pack.rules["project"]["bibliography_files"],
    )
    return project, pack


class LanguagePhase1Test(unittest.TestCase):
    def test_university_generic_detects_phase1_language_codes(self) -> None:
        with workspace_tempdir("language-phase1-") as base:
            materialize_project(
                base,
                {
                    "main.tex": (
                        "\\documentclass{article}\n"
                        "\\begin{document}\n"
                        "\\input{chapters/01-language}\n"
                        "\\bibliography{ref/refs}\n"
                        "\\end{document}\n"
                    ),
                    "chapters/01-language.tex": (
                        "括号不匹配（测试。\n"
                        "引号不匹配“测试。\n"
                        "《论文题目》与“教材名称”并列出现。\n"
                        "实验剂量为10kg。\n"
                        "这里需要...\n"
                        "变化趋势--明显。\n"
                        "中文,English\n"
                        "范围为3-5。\n"
                        "1) 第一项\n"
                        "因此所以，我们继续。\n"
                        "中文,中文\n"
                    ),
                    "ref/refs.bib": "@article{ref1,\n  title = {Reference One},\n}\n",
                },
            )
            project, pack = _discover_project(base, "university-generic")
            report_path = base / "reports" / "check_language-report.json"
            exit_code = run_language_check(project, pack, report_path)
            report = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 1)
        codes = {item["code"] for item in report["findings"]}
        self.assertTrue(
            {
                "LANG_BRACKET_MISMATCH",
                "LANG_QUOTE_MISMATCH",
                "LANG_BOOKTITLE_MIXED_STYLE",
                "LANG_UNIT_SPACING",
                "LANG_ELLIPSIS_STYLE",
                "LANG_DASH_STYLE",
                "LANG_ZH_EN_SYMBOL_SPACING",
                "LANG_NUMBER_RANGE_STYLE",
                "LANG_ENUM_STYLE",
                "LANG_CONNECTOR_BLACKLIST",
                "LANG_FULLWIDTH_HALFWIDTH_MIX",
            }.issubset(codes)
        )

    def test_journal_generic_keeps_conservative_rules_disabled(self) -> None:
        with workspace_tempdir("language-phase1-") as base:
            materialize_project(
                base,
                {
                    "main.tex": (
                        "\\documentclass{article}\n"
                        "\\begin{document}\n"
                        "\\input{sections/01-language}\n"
                        "\\bibliography{ref/refs}\n"
                        "\\end{document}\n"
                    ),
                    "sections/01-language.tex": (
                        "这是Example文本。\n"
                        "中文,English\n"
                        "1) 第一项\n"
                        "因此所以，我们继续。\n"
                        "这里需要...\n"
                        "ABC，XYZ\n"
                    ),
                    "ref/refs.bib": "@article{ref1,\n  title = {Reference One},\n}\n",
                },
            )
            project, pack = _discover_project(base, "journal-generic")
            report_path = base / "reports" / "check_language-report.json"
            run_language_check(project, pack, report_path)
            report = json.loads(report_path.read_text(encoding="utf-8"))

        codes = {item["code"] for item in report["findings"]}
        self.assertNotIn("LANG_CJK_LATIN_SPACING", codes)
        self.assertNotIn("LANG_ZH_EN_SYMBOL_SPACING", codes)
        self.assertNotIn("LANG_ENUM_STYLE", codes)
        self.assertNotIn("LANG_CONNECTOR_BLACKLIST", codes)
        self.assertNotIn("LANG_ELLIPSIS_STYLE", codes)
        self.assertNotIn("LANG_FULLWIDTH_HALFWIDTH_MIX", codes)

    def test_balanced_and_normalized_text_stays_quiet(self) -> None:
        with workspace_tempdir("language-phase1-") as base:
            materialize_project(
                base,
                {
                    "main.tex": (
                        "\\documentclass{article}\n"
                        "\\begin{document}\n"
                        "\\input{chapters/01-language}\n"
                        "\\bibliography{ref/refs}\n"
                        "\\end{document}\n"
                    ),
                    "chapters/01-language.tex": (
                        "实验剂量为 10 kg。\n"
                        "这里需要……\n"
                        "这是“平衡引号”与（平衡括号）。\n"
                        "1. 第一项\n"
                    ),
                    "ref/refs.bib": "@article{ref1,\n  title = {Reference One},\n}\n",
                },
            )
            project, pack = _discover_project(base, "university-generic")
            report_path = base / "reports" / "check_language-report.json"
            exit_code = run_language_check(project, pack, report_path)
            report = json.loads(report_path.read_text(encoding="utf-8"))

        codes = {item["code"] for item in report["findings"]}
        self.assertEqual(exit_code, 0)
        self.assertFalse(
            {
                "LANG_BRACKET_MISMATCH",
                "LANG_QUOTE_MISMATCH",
                "LANG_UNIT_SPACING",
                "LANG_ELLIPSIS_STYLE",
                "LANG_ENUM_STYLE",
            }
            & codes
        )


if __name__ == "__main__":
    unittest.main()
