from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from core.fixers import apply_language_deep_fixes
from tests.helpers import materialize_project, workspace_tempdir


ROOT = Path(__file__).resolve().parents[1]


class LanguageDeepFixerTest(unittest.TestCase):
    def test_deep_fixer_preview_only_keeps_source_unchanged(self) -> None:
        with workspace_tempdir("language-deep-fixer-") as base:
            materialize_project(base, {"chapter.tex": "因此所以，本文继续讨论。\n"})
            report = base / "report.json"
            report.write_text(
                json.dumps(
                    {
                        "findings": [
                            {
                                "code": "LANG_DEEP_CONNECTOR_MISUSE",
                                "file": "chapter.tex",
                                "line": 1,
                                "span": {"start": 1, "end": 4},
                                "message": "Connector chain may be redundant",
                                "suggestions": ["因此"],
                                "confidence": 0.72,
                                "review_required": True,
                                "category": "connector_misuse",
                            }
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            summary = apply_language_deep_fixes(base, report, apply=False)
            content = (base / "chapter.tex").read_text(encoding="utf-8")
        self.assertTrue(summary["preview_only"])
        self.assertEqual(summary["preview_count"], 1)
        self.assertEqual(len(summary["patches"]), 1)
        self.assertEqual(len(summary["skipped_review_required"]), 1)
        self.assertEqual(summary["applied_patches"], [])
        self.assertEqual(content, "因此所以，本文继续讨论。\n")

    def test_deep_fixer_supports_selective_apply_with_override(self) -> None:
        with workspace_tempdir("language-deep-fixer-") as base:
            materialize_project(
                base,
                {"chapter.tex": "因此所以，本文继续讨论。\n本研究旨在提升效率水平。\n"},
            )
            report = base / "report.json"
            report.write_text(
                json.dumps(
                    {
                        "findings": [
                            {
                                "code": "LANG_DEEP_CONNECTOR_MISUSE",
                                "file": "chapter.tex",
                                "line": 1,
                                "span": {"start": 1, "end": 4},
                                "message": "Connector chain may be redundant",
                                "suggestions": ["因此"],
                                "confidence": 0.72,
                                "review_required": True,
                                "category": "connector_misuse",
                            },
                            {
                                "code": "LANG_DEEP_COLLOCATION_MISUSE",
                                "file": "chapter.tex",
                                "line": 2,
                                "span": {"start": 6, "end": 11},
                                "message": "Collocation may be awkward or redundant",
                                "suggestions": ["提升效率"],
                                "confidence": 0.75,
                                "review_required": True,
                                "category": "collocation_misuse",
                            },
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            summary = apply_language_deep_fixes(
                base,
                report,
                apply=True,
                include_review_required=True,
                issue_codes={"LANG_DEEP_CONNECTOR_MISUSE"},
            )
            content = (base / "chapter.tex").read_text(encoding="utf-8")
        self.assertEqual(summary["changed_files"], 1)
        self.assertEqual(len(summary["applied_patches"]), 1)
        self.assertEqual(summary["selected_issue_codes"], ["LANG_DEEP_CONNECTOR_MISUSE"])
        self.assertEqual(content, "因此，本文继续讨论。\n本研究旨在提升效率水平。\n")

    def test_run_fix_cycle_suggest_mode_generates_preview_without_writes(self) -> None:
        with workspace_tempdir("language-deep-fixer-") as base:
            project_root = base / "project"
            materialize_project(
                project_root,
                {
                    "main.tex": (
                        "\\documentclass{article}\n"
                        "\\begin{document}\n"
                        "\\input{chapters/01-introduction}\n"
                        "\\bibliography{ref/refs}\n"
                        "\\end{document}\n"
                    ),
                    "chapters/01-introduction.tex": "因此所以，本文继续讨论。\n",
                    "ref/refs.bib": "@article{ref1,\n  title = {Reference One},\n}\n",
                    "reports/check_language_deep-report.json": json.dumps(
                        {
                            "findings": [
                                {
                                    "code": "LANG_DEEP_CONNECTOR_MISUSE",
                                    "file": "chapters/01-introduction.tex",
                                    "line": 1,
                                    "span": {"start": 1, "end": 4},
                                    "message": "Connector chain may be redundant",
                                    "suggestions": ["因此"],
                                    "confidence": 0.72,
                                    "review_required": True,
                                    "category": "connector_misuse",
                                }
                            ]
                        },
                        ensure_ascii=False,
                    ),
                },
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "run_fix_cycle.py"),
                    "--project-root",
                    str(project_root),
                    "--ruleset",
                    "university-generic",
                    "--apply",
                    "false",
                    "--apply-mode",
                    "suggest",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            summary = json.loads(
                (project_root / "reports" / "fix-summary.json").read_text(
                    encoding="utf-8"
                )
            )
            content = (project_root / "chapters" / "01-introduction.tex").read_text(
                encoding="utf-8"
            )
        self.assertEqual(summary["apply_mode"], "suggest")
        self.assertIn("language-deep", summary["steps"])
        self.assertEqual(
            summary["steps"]["language-deep"]["summary"]["preview_count"],
            1,
        )
        self.assertEqual(content, "因此所以，本文继续讨论。\n")


if __name__ == "__main__":
    unittest.main()
