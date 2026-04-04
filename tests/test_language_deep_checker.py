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
                        "\u56e0\u6b64\u6240\u4ee5\uff0c\u672c\u6587\u7ee7\u7eed\u8ba8\u8bba\u3002\n"
                        "\u503c\u5f97\u6ce8\u610f\u7684\u662f\uff0c\u8fd9\u91cc\u9700\u8981\u8fdb\u4e00\u6b65\u8bf4\u660e\u3002\n"
                        "\u672c\u6587\u4f7f\u7528 DID \u8bc6\u522b\u653f\u7b56\u6548\u5e94\u3002\n"
                        "\u672c\u7814\u7a76\u65e8\u5728\u63d0\u5347\u6548\u7387\u6c34\u5e73\u3002\n"
                        "\u5927\u578b\u8bed\u8a00\u6a21\u578b\u5728\u7814\u7a76\u4e2d\u5177\u6709\u91cd\u8981\u4f5c\u7528\u3002\n"
                    ),
                    "chapters/02-methods.tex": (
                        "Difference-in-Differences\uff08DID\uff09\u6a21\u578b\u5982\u4e0b\u3002\n"
                        "\u7531\u6b64\u53ef\u89c1\uff0c\u8fd9\u4e9b\u7ed3\u679c\u53ef\u4ee5\u8bc1\u660e\u653f\u7b56\u5fc5\u7136\u6709\u6548\u3002\n"
                        "\u540e\u6587\u4e5f\u79f0\u5927\u8bed\u8a00\u6a21\u578b\u3002\n"
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
                "LANG_DEEP_FORMULAIC_PHRASE",
                "LANG_DEEP_INFERENCE_OVERCLAIM",
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
        self.assertIn("review_queue", report)
        self.assertIn("review_clusters", report)
        self.assertIn("review_digest", report["summary"])
        for cluster in report["review_clusters"]:
            for key in ("recommended_action", "rewrite_hint", "review_focus"):
                self.assertIn(key, cluster)
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
        self.assertEqual(
            original_intro,
            "\u56e0\u6b64\u6240\u4ee5\uff0c\u672c\u6587\u7ee7\u7eed\u8ba8\u8bba\u3002\n"
            "\u503c\u5f97\u6ce8\u610f\u7684\u662f\uff0c\u8fd9\u91cc\u9700\u8981\u8fdb\u4e00\u6b65\u8bf4\u660e\u3002\n"
            "\u672c\u6587\u4f7f\u7528 DID \u8bc6\u522b\u653f\u7b56\u6548\u5e94\u3002\n"
            "\u672c\u7814\u7a76\u65e8\u5728\u63d0\u5347\u6548\u7387\u6c34\u5e73\u3002\n"
            "\u5927\u578b\u8bed\u8a00\u6a21\u578b\u5728\u7814\u7a76\u4e2d\u5177\u6709\u91cd\u8981\u4f5c\u7528\u3002\n",
        )
        self.assertEqual(
            original_methods,
            "Difference-in-Differences\uff08DID\uff09\u6a21\u578b\u5982\u4e0b\u3002\n"
            "\u7531\u6b64\u53ef\u89c1\uff0c\u8fd9\u4e9b\u7ed3\u679c\u53ef\u4ee5\u8bc1\u660e\u653f\u7b56\u5fc5\u7136\u6709\u6548\u3002\n"
            "\u540e\u6587\u4e5f\u79f0\u5927\u8bed\u8a00\u6a21\u578b\u3002\n",
        )
        self.assertEqual(report["review_queue"][0]["priority"], "high")
        self.assertLessEqual(
            report["summary"]["review_digest"]["deduplicated_action_items"],
            len(report["findings"]),
        )

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
                        "\u53cc\u91cd\u5dee\u5206\uff08Difference-in-Differences, DID\uff09\u6a21\u578b\u5982\u4e0b\u3002\n"
                        "\u5927\u578b\u8bed\u8a00\u6a21\u578b\u5728\u7814\u7a76\u4e2d\u5177\u6709\u91cd\u8981\u4f5c\u7528\u3002\n"
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
        self.assertFalse(report["review_queue"])
        self.assertFalse(report["review_clusters"])
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
                        "\\caption{\u56e0\u6b64\u6240\u4ee5}\n"
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

    def test_deep_checker_reports_formulaic_phrase_and_real_sample_term_drift(self) -> None:
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
                        "\u503c\u5f97\u6ce8\u610f\u7684\u662f\uff0c\u7814\u7a76\u7ed3\u8bba\u4ecd\u9700\u8fdb\u4e00\u6b65\u8fa8\u6790\u3002\n"
                        "\u7814\u7a76\u91c7\u7528\u76ee\u6807\u8bd5\u9a8c\u6a21\u62df\u7684\u601d\u8def\u3002\n"
                        "\u540e\u7eed\u53c8\u5c06\u5176\u79f0\u4e3a\u76ee\u6807\u5b9e\u9a8c\u6a21\u62df\u3002\n"
                        "\u63a8\u65ad\u9636\u6bb5\u4f7f\u7528\u589e\u5e7f\u9006\u6982\u7387\u52a0\u6743\u3002\n"
                    ),
                    "chapters/02-methods.tex": (
                        "\u7531\u6b64\u53ef\u89c1\uff0c\u6a21\u578b\u8bbe\u5b9a\u4e0e\u4f30\u8ba1\u53e3\u5f84\u9700\u8981\u533a\u5206\u3002\n"
                        "\u654f\u611f\u6027\u5206\u6790\u4e2d\u4e5f\u4f7f\u7528\u589e\u5f3a\u9006\u6982\u7387\u52a0\u6743\u3002\n"
                    ),
                    "ref/refs.bib": "@article{ref1,\n  title = {Reference One},\n}\n",
                },
            )
            project, pack = _discover_project(base, "tsinghua-thesis")
            report_path = base / "reports" / "check_language_deep-report.json"
            exit_code = run_language_deep_check(project, pack, report_path)
            report = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 1)
        codes = [item["code"] for item in report["findings"]]
        self.assertIn("LANG_DEEP_FORMULAIC_PHRASE", codes)
        self.assertIn("LANG_DEEP_TERM_INCONSISTENT", codes)
        messages = [item["message"] for item in report["findings"]]
        self.assertTrue(any("目标试验模拟" in message for message in messages), messages)
        self.assertTrue(any("增广逆概率加权" in message for message in messages), messages)
        self.assertTrue(report["review_clusters"])
        self.assertTrue(
            any(cluster["recommended_action"] for cluster in report["review_clusters"])
        )

    def test_deep_checker_reports_boundary_and_inference_phrases(self) -> None:
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
                        "\u7531\u6b64\u53ef\u89c1\uff0c\u8be5\u7ed3\u679c\u53ef\u4ee5\u8bc1\u660e\u653f\u7b56\u4e00\u5b9a\u6709\u6548\u3002\n"
                        "\u9700\u8981\u6307\u51fa\u7684\u662f\uff0c\u8fd9\u4e00\u63a8\u65ad\u4ecd\u4f9d\u8d56\u6837\u672c\u8303\u56f4\u3002\n"
                    ),
                    "ref/refs.bib": "@article{ref1,\n  title = {Reference One},\n}\n",
                },
            )
            project, pack = _discover_project(base, "university-generic")
            report_path = base / "reports" / "check_language_deep-report.json"
            exit_code = run_language_deep_check(project, pack, report_path)
            report = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 1)
        codes = [item["code"] for item in report["findings"]]
        self.assertIn("LANG_DEEP_INFERENCE_OVERCLAIM", codes)
        self.assertIn("LANG_DEEP_BOUNDARY_SIGNPOST", codes)
        priorities = {item["priority"] for item in report["review_queue"]}
        self.assertTrue({"medium", "low"} & priorities)
        self.assertTrue(
            any(
                "Soften the claim" in cluster["recommended_action"]
                for cluster in report["review_clusters"]
            )
        )


if __name__ == "__main__":
    unittest.main()
