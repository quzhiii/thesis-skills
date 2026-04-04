from __future__ import annotations

import unittest
from pathlib import Path

import json

from core.pack_generator import create_draft_pack, create_rule_pack
from core.rules import load_rule_pack
from tests.helpers import workspace_tempdir


ROOT = Path(__file__).resolve().parents[1]


class PackGeneratorTest(unittest.TestCase):
    def test_create_journal_pack_from_starter(self) -> None:
        with workspace_tempdir("pack-generator-") as output_root:
            pack_path = create_rule_pack(
                repo_root=ROOT,
                output_root=output_root,
                pack_id="my-journal",
                display_name="My Journal",
                starter="journal-generic",
                kind="journal",
            )
            pack = load_rule_pack(pack_path)
        self.assertEqual(pack.pack["id"], "my-journal")
        self.assertEqual(pack.pack["display_name"], "My Journal")
        self.assertIn("project", pack.rules)

    def test_create_draft_pack_from_intake_metadata(self) -> None:
        with workspace_tempdir("pack-generator-") as output_root:
            intake = output_root / "intake.json"
            intake.write_text(
                json.dumps(
                    {
                        "pack_id": "demo-school",
                        "display_name": "Demo School Thesis",
                        "kind": "university-thesis",
                        "starter": "university-generic",
                        "institution": "Demo School",
                        "guide_sources": ["guide.pdf"],
                        "template_sources": ["template.docx", "template.cls"],
                        "sample_sources": ["sample.pdf"],
                        "word_style_mappings": [
                            {
                                "style": "Heading 1",
                                "role": "chapter",
                                "latex_command": "chapter",
                            }
                        ],
                        "chapter_role_mappings": [
                            {
                                "source": "chapter1",
                                "role": "introduction",
                                "target": "chapters/01-introduction.tex",
                            }
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            pack_path = create_draft_pack(ROOT, output_root, intake)
            pack = load_rule_pack(pack_path)
            notes = (pack_path / "draft-notes.md").read_text(encoding="utf-8")
        self.assertEqual(pack.pack["id"], "demo-school")
        self.assertIn("source_template_mappings", pack.mappings)
        self.assertIn("Heading 1", pack.mappings["source_template_mappings"])
        self.assertIn("guide.pdf", notes)


if __name__ == "__main__":
    unittest.main()
