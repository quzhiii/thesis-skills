from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from core.fixers import apply_format_fixes, apply_language_fixes


class FixerTest(unittest.TestCase):
    def test_language_fixer_patches_cjk_spacing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            tex = base / "chapter.tex"
            tex.write_text("这是Example文本。。\n", encoding="utf-8")
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
            summary = apply_language_fixes(base, report, apply=True)
            content = tex.read_text(encoding="utf-8")
        self.assertEqual(summary["changed_files"], 1)
        self.assertIn("这是 Example 文本。", content)

    def test_format_fixer_only_removes_flagged_label_line(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
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


if __name__ == "__main__":
    unittest.main()
