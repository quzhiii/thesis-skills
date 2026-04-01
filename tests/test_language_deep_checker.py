from __future__ import annotations

import json
import unittest
from pathlib import Path

from core.checkers import run_language_deep_check
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


class LanguageDeepCheckerTest(unittest.TestCase):
    def test_deep_checker_reports_required_phase2_categories(self) -> None:
        with workspace_tempdir("language-deep-") as base:
            materialize_project(
                base,
                {
                    "main.tex": (
                        "\\documentclass{article}\n"
                        "\\begin{document}\n"
                        "\\input{chapters/01-introduction}\n"
                        "\\input{chapters/02-methods}\n"
                        "\\bibliography{ref/refs}\n"
                        "\\end{document}\n"
                    ),
                    "chapters/01-introduction.tex": (
                        "因此所以，本文继续讨论。\n"
                        "本文使用 DID 识别政策效应。\n"
                        "本研究旨在提升效率水平。\n"
                        "大型语言模型在研究中具有重要作用。\n"
                    ),
                    "chapters/02-methods.tex": (
                        "Difference-in-Differences（DID）模型如下。\n"
                        "后文也称大语言模型。\n"
                    ),
                    "ref/refs.bib": "@article{ref1,\n  title = {Reference One},\n}\n",
                },
            )
            original_intro = (base / "chapters" / "01-introduction.tex").read_text(
                encoding="utf-8"
            )
            original_methods = (base / "chapters" / "02-methods.tex").read_text(
                encoding="utf-8"
            )
            project, pack = _discover_project(base, "university-generic")
            report_path = base / "reports" / "check_language_deep-report.json"
            exit_code = run_language_deep_check(project, pack, report_path)
            report = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 1)
        codes = {item["code"] for item in report["findings"]}
        self.assertTrue(
            {
                "LANG_DEEP_CONNECTOR_MISUSE",
                "LANG_DEEP_COLLOCATION_MISUSE",
                "LANG_DEEP_TERM_INCONSISTENT",
                "LANG_DEEP_ACRONYM_FIRST_USE",
            }.issubset(codes)
        )
        self.assertEqual(report["summary"]["checker"], "check_language_deep")
        self.assertEqual(
            report["summary"]["coverage_mode"], "partial_latex_aware_screening"
        )
        self.assertEqual(report["summary"]["review_mode"], "manual_first")
        self.assertIn("stratified_counts", report["summary"])
        self.assertIn("coverage", report)
        self.assertIn("uncovered_risks", report)
        self.assertIn("review_guidance", report)
        for finding in report["findings"]:
            for key in (
                "span",
                "evidence",
                "suggestions",
                "confidence",
                "review_required",
                "category",
                "original_text",
                "rationale",
                "risk_level",
            ):
                self.assertIn(key, finding)
        self.assertEqual(original_intro, "因此所以，本文继续讨论。\n本文使用 DID 识别政策效应。\n本研究旨在提升效率水平。\n大型语言模型在研究中具有重要作用。\n")
        self.assertEqual(original_methods, "Difference-in-Differences（DID）模型如下。\n后文也称大语言模型。\n")

    def test_deep_checker_stays_quiet_when_terms_and_acronyms_are_introduced_cleanly(self) -> None:
        with workspace_tempdir("language-deep-") as base:
            materialize_project(
                base,
                {
                    "main.tex": (
                        "\\documentclass{article}\n"
                        "\\begin{document}\n"
                        "\\input{chapters/01-introduction}\n"
                        "\\bibliography{ref/refs}\n"
                        "\\end{document}\n"
                    ),
                    "chapters/01-introduction.tex": (
                        "双重差分（Difference-in-Differences, DID）模型如下。\n"
                        "大型语言模型在研究中具有重要作用。\n"
                    ),
                    "ref/refs.bib": "@article{ref1,\n  title = {Reference One},\n}\n",
                },
            )
            project, pack = _discover_project(base, "university-generic")
            report_path = base / "reports" / "check_language_deep-report.json"
            exit_code = run_language_deep_check(project, pack, report_path)
            report = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0)
        self.assertEqual(report["summary"]["warnings"], 0)
        self.assertFalse(report["findings"])
        self.assertEqual(
            report["summary"]["coverage_mode"], "partial_latex_aware_screening"
        )
        self.assertTrue(report["uncovered_risks"])
        self.assertIn("Zero findings only means", report["uncovered_risks"][-1])

    def test_deep_checker_masks_latex_command_and_environment_noise(self) -> None:
        with workspace_tempdir("language-deep-") as base:
            materialize_project(
                base,
                {
                    "main.tex": (
                        "\\documentclass{article}\n"
                        "\\begin{document}\n"
                        "\\input{chapters/01-introduction}\n"
                        "\\bibliography{ref/refs}\n"
                        "\\end{document}\n"
                    ),
                    "chapters/01-introduction.tex": (
                        "\\section{Difference-in-Differences (DID)}\n"
                        "\\begin{figure}\n"
                        "\\caption{\\u56e0\\u6b64\\u6240\\u4ee5}\n"
                        "\\end{figure}\n"
                        "\\cite{ref1}\n"
                    ),
                    "ref/refs.bib": "@article{ref1,\n  title = {Reference One},\n}\n",
                },
            )
            project, pack = _discover_project(base, "university-generic")
            report_path = base / "reports" / "check_language_deep-report.json"
            exit_code = run_language_deep_check(project, pack, report_path)
            report = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0)
        self.assertFalse(report["findings"])
        self.assertGreater(
            report["coverage"]["masked_construct_counts"]["latex_commands"], 0
        )
        self.assertGreater(
            report["coverage"]["masked_construct_counts"]["structured_environments"], 0
        )


if __name__ == "__main__":
    unittest.main()
