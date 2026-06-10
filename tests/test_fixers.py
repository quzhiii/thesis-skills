from __future__ import annotations

import json
import unittest

from core.fixers import apply_format_fixes, apply_language_fixes, apply_review_patches
from tests.helpers import materialize_project, workspace_tempdir


class FixerTest(unittest.TestCase):
    def test_final_cleanup_fixer_previews_and_applies_exact_marker_removals(self) -> None:
        from core.final_cleanup import run_final_cleanup_check
        from core.fixers import apply_final_cleanup_fixes
        from core.project import ThesisProject
        from core.rules import load_rule_pack
        from tests.test_rules import PACK_ROOT

        with workspace_tempdir("fixers-") as base:
            pack = load_rule_pack(PACK_ROOT / "university-generic")
            materialize_project(
                base,
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\input{chapters/ch1}\n\\end{document}\n",
                    "chapters/ch1.tex": "TODO FIXME ??? debug draft\nKeep this sentence.\n",
                },
            )
            project = ThesisProject.discover(
                base,
                pack.rules["project"]["main_tex_candidates"],
                pack.rules["project"]["chapter_globs"],
                pack.rules["project"]["bibliography_files"],
            )
            report = base / "reports" / "final-cleanup-report.json"
            run_final_cleanup_check(project, pack, report)
            tex = base / "chapters" / "ch1.tex"
            original = tex.read_text(encoding="utf-8")

            preview = apply_final_cleanup_fixes(base, report, apply=False)
            self.assertEqual(preview["preview_count"], 5)
            self.assertEqual(tex.read_text(encoding="utf-8"), original)

            applied = apply_final_cleanup_fixes(base, report, apply=True)
            content = tex.read_text(encoding="utf-8")

        self.assertEqual(applied["changed_files"], 1)
        self.assertEqual(len(applied["applied_patches"]), 5)
        self.assertEqual(content, "    \nKeep this sentence.\n")

    def test_manual_anchor_fixer_previews_and_applies_phantomsection_insertion(self) -> None:
        from core.fixers import apply_manual_anchor_fixes
        from core.manual_anchor import run_manual_anchor_check
        from core.project import ThesisProject
        from core.rules import load_rule_pack
        from tests.test_rules import PACK_ROOT

        with workspace_tempdir("fixers-") as base:
            pack = load_rule_pack(PACK_ROOT / "university-generic")
            materialize_project(
                base,
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\input{chapters/ch1}\n\\end{document}\n",
                    "chapters/ch1.tex": "\\chapter*{Appendix}\n\\addcontentsline{toc}{chapter}{Appendix}\n",
                },
            )
            project = ThesisProject.discover(
                base,
                pack.rules["project"]["main_tex_candidates"],
                pack.rules["project"]["chapter_globs"],
                pack.rules["project"]["bibliography_files"],
            )
            report = base / "reports" / "manual-anchor-report.json"
            run_manual_anchor_check(project, pack, report)
            tex = base / "chapters" / "ch1.tex"
            original = tex.read_text(encoding="utf-8")

            preview = apply_manual_anchor_fixes(base, report, apply=False)
            self.assertEqual(preview["preview_count"], 1)
            self.assertEqual(tex.read_text(encoding="utf-8"), original)

            applied = apply_manual_anchor_fixes(base, report, apply=True)
            content = tex.read_text(encoding="utf-8")

        self.assertEqual(applied["changed_files"], 1)
        self.assertEqual(len(applied["applied_patches"]), 1)
        self.assertEqual(content, "\\chapter*{Appendix}\n\\phantomsection\n\\addcontentsline{toc}{chapter}{Appendix}\n")

    def test_statistical_consistency_fixer_previews_and_applies_dominant_normalization(self) -> None:
        from core.fixers import apply_statistical_consistency_fixes
        from core.project import ThesisProject
        from core.rules import load_rule_pack
        from core.statistical_consistency import run_statistical_consistency_check
        from tests.test_rules import PACK_ROOT

        with workspace_tempdir("fixers-") as base:
            pack = load_rule_pack(PACK_ROOT / "university-generic")
            materialize_project(
                base,
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\input{chapters/ch1}\n\\end{document}\n",
                    "chapters/ch1.tex": "p值 and p值 and p值 and P值 here.\n",
                },
            )
            project = ThesisProject.discover(
                base,
                pack.rules["project"]["main_tex_candidates"],
                pack.rules["project"]["chapter_globs"],
                pack.rules["project"]["bibliography_files"],
            )
            report = base / "reports" / "statistical-consistency-report.json"
            run_statistical_consistency_check(project, pack, report)
            tex = base / "chapters" / "ch1.tex"
            original = tex.read_text(encoding="utf-8")

            preview = apply_statistical_consistency_fixes(base, report, apply=False)
            self.assertEqual(preview["preview_count"], 1)
            self.assertEqual(tex.read_text(encoding="utf-8"), original)

            applied = apply_statistical_consistency_fixes(base, report, apply=True)
            content = tex.read_text(encoding="utf-8")

        self.assertEqual(applied["changed_files"], 1)
        self.assertEqual(len(applied["applied_patches"]), 1)
        self.assertEqual(content, "p值 and p值 and p值 and p值 here.\n")

    def test_language_fixer_applies_safe_phase1_fixes(self) -> None:
        with workspace_tempdir("fixers-") as base:
            tex = base / "chapter.tex"
            tex.write_text(
                (
                    "\u8fd9\u662fExample\u6587\u672c\u3002\u3002\n"
                    "\u8d28\u91cf\u4e3a10kg\u3002\n"
                    "\u4e2d\u6587,\u4e2d\u6587\n"
                    "ABC\uff0cXYZ\n"
                    "\u8fd9\u91cc\u9700\u8981...\n"
                ),
                encoding="utf-8",
            )
            report = base / "report.json"
            report.write_text(
                json.dumps(
                    {
                        "findings": [
                            {
                                "code": "LANG_CJK_LATIN_SPACING",
                                "file": "chapter.tex",
                                "line": 1,
                                "message": "space needed",
                            },
                            {
                                "code": "LANG_REPEAT_PUNC",
                                "file": "chapter.tex",
                                "line": 1,
                                "message": "repeat punctuation",
                            },
                            {
                                "code": "LANG_UNIT_SPACING",
                                "file": "chapter.tex",
                                "line": 2,
                                "message": "unit spacing",
                            },
                            {
                                "code": "LANG_FULLWIDTH_HALFWIDTH_MIX",
                                "file": "chapter.tex",
                                "line": 3,
                                "message": "mixed punctuation width",
                            },
                            {
                                "code": "LANG_ELLIPSIS_STYLE",
                                "file": "chapter.tex",
                                "line": 5,
                                "message": "ellipsis style",
                            },
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            summary = apply_language_fixes(base, report, apply=True)
            content = tex.read_text(encoding="utf-8")
        self.assertEqual(summary["changed_files"], 1)
        self.assertEqual(summary["changed"], ["chapter.tex"])
        self.assertEqual(
            content,
            (
                "\u8fd9\u662f Example \u6587\u672c\u3002\n"
                "\u8d28\u91cf\u4e3a10 kg\u3002\n"
                "\u4e2d\u6587\uff0c\u4e2d\u6587\n"
                "ABC,XYZ\n"
                "\u8fd9\u91cc\u9700\u8981\u2026\u2026\n"
            ),
        )

    def test_language_fixer_dry_run_does_not_write(self) -> None:
        with workspace_tempdir("fixers-") as base:
            tex = base / "chapter.tex"
            original = "\u8fd9\u662fExample\u6587\u672c\u3002\u3002\n"
            tex.write_text(original, encoding="utf-8")
            report = base / "report.json"
            report.write_text(
                json.dumps(
                    {
                        "findings": [
                            {
                                "code": "LANG_CJK_LATIN_SPACING",
                                "file": "chapter.tex",
                                "line": 1,
                                "message": "space needed",
                            },
                            {
                                "code": "LANG_REPEAT_PUNC",
                                "file": "chapter.tex",
                                "line": 1,
                                "message": "repeat punctuation",
                            },
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            summary = apply_language_fixes(base, report, apply=False)
            content = tex.read_text(encoding="utf-8")
        self.assertEqual(summary["changed_files"], 1)
        self.assertFalse(summary["applied"])
        self.assertEqual(content, original)

    def test_format_fixer_only_removes_flagged_label_line(self) -> None:
        with workspace_tempdir("fixers-") as base:
            tex = base / "chapter.tex"
            tex.write_text(
                "\\begin{figure}\n\\label{keep-me}\n\\caption{A}\n\\end{figure}\n\\label{remove-me}\n",
                encoding="utf-8",
            )
            report = base / "report.json"
            report.write_text(
                json.dumps(
                    {
                        "findings": [
                            {
                                "code": "FMT_ORPHAN_LABEL",
                                "file": "chapter.tex",
                                "line": 5,
                                "message": "label not referenced",
                            }
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            apply_format_fixes(base, report, apply=True)
            content = tex.read_text(encoding="utf-8")
        self.assertIn("\\label{keep-me}", content)
        self.assertNotIn("\\label{remove-me}", content)

    def test_review_fixer_supports_preview_and_apply(self) -> None:
        with workspace_tempdir("fixers-") as base:
            chapters = base / "chapters"
            chapters.mkdir(parents=True)
            tex = chapters / "01-introduction.tex"
            tex.write_text("因此所以，本文继续讨论。\n", encoding="utf-8")
            artifact = base / "review-ingest-artifact.json"
            artifact.write_text(
                json.dumps(
                    {
                        "artifact_type": "feedback_ingest",
                        "summary": {"normalized_count": 1},
                        "payload": {
                            "selective_action": {
                                "candidate_patches": [
                                    {
                                        "code": "REVIEW_LANGUAGE_LOCAL",
                                        "file": "chapters/01-introduction.tex",
                                        "line": 1,
                                        "span": {"start": 1, "end": 4},
                                        "old_text": "因此所以",
                                        "suggestions": ["因此"],
                                        "confidence": 0.95,
                                        "review_required": False,
                                        "ambiguous": False,
                                        "category": "language",
                                    }
                                ]
                            }
                        },
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            preview = apply_review_patches(base, artifact, apply=False)
            self.assertEqual(preview["preview_count"], 1)
            self.assertEqual(tex.read_text(encoding="utf-8"), "因此所以，本文继续讨论。\n")
            applied = apply_review_patches(base, artifact, apply=True)
            content = tex.read_text(encoding="utf-8")
        self.assertEqual(applied["changed_files"], 1)
        self.assertEqual(len(applied["applied_patches"]), 1)
        self.assertEqual(content, "因此，本文继续讨论。\n")


if __name__ == "__main__":
    unittest.main()
