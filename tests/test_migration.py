from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from core.migration import run_word_to_latex_migration


ROOT = Path(__file__).resolve().parents[1]


class MigrationTest(unittest.TestCase):
    def test_word_to_latex_migration_maps_assets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / "intake"
            target = base / "project"
            (source / "chapters").mkdir(parents=True)
            (target / "chapters").mkdir(parents=True)
            (target / "ref").mkdir(parents=True)
            (source / "chapters" / "chapter1.tex").write_text(
                "\\section{Intro}\n", encoding="utf-8"
            )
            (source / "refs-import.bib").write_text(
                "@article{ref1, title={A}}\n", encoding="utf-8"
            )
            spec = source / "migration.json"
            spec.write_text(
                json.dumps(
                    {
                        "chapter_mappings": [
                            {
                                "from": "chapters/chapter1.tex",
                                "to": "chapters/01-introduction.tex",
                            }
                        ],
                        "bibliography_mappings": [
                            {"from": "refs-import.bib", "to": "ref/refs-import.bib"}
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            summary = run_word_to_latex_migration(source, target, spec, apply=True)
            migrated = (target / "chapters" / "01-introduction.tex").read_text(
                encoding="utf-8"
            )
        self.assertEqual(summary["copied_files"], 2)
        self.assertIn("\\section{Intro}", migrated)

    def test_word_to_latex_migration_supports_style_and_role_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / "intake"
            target = base / "project"
            (source / "chapters").mkdir(parents=True)
            (target / "chapters").mkdir(parents=True)
            (source / "chapters" / "chapter1.tex").write_text(
                "Raw chapter\n", encoding="utf-8"
            )
            spec = source / "migration.json"
            spec.write_text(
                json.dumps(
                    {
                        "document_metadata": {
                            "source_format": "word-exported-tex",
                            "bibliography_source": "zotero",
                        },
                        "word_style_mappings": [
                            {
                                "style": "Heading 1",
                                "role": "chapter",
                                "latex_command": "chapter",
                            }
                        ],
                        "chapter_role_mappings": [
                            {
                                "source": "chapters/chapter1.tex",
                                "role": "introduction",
                                "target": "chapters/01-introduction.tex",
                            }
                        ],
                        "chapter_mappings": [
                            {
                                "from": "chapters/chapter1.tex",
                                "to": "chapters/01-introduction.tex",
                                "role": "introduction",
                                "word_style": "Heading 1",
                            }
                        ],
                        "bibliography_mappings": [],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            summary = run_word_to_latex_migration(source, target, spec, apply=False)
        self.assertEqual(
            summary["document_metadata"]["source_format"], "word-exported-tex"
        )
        self.assertEqual(summary["word_style_mappings"][0]["style"], "Heading 1")
        self.assertEqual(summary["chapter_role_mappings"][0]["role"], "introduction")


if __name__ == "__main__":
    unittest.main()
