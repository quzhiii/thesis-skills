from __future__ import annotations

import unittest
from pathlib import Path
from uuid import uuid4

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

    def test_create_rule_pack_rejects_path_traversal_pack_id(self) -> None:
        with workspace_tempdir("pack-generator-") as output_root:
            escaped_name = f"escaped-pack-{uuid4().hex}"
            with self.assertRaises(ValueError):
                create_rule_pack(
                    repo_root=ROOT,
                    output_root=output_root,
                    pack_id=f"../{escaped_name}",
                    display_name="Escaped Pack",
                    starter="journal-generic",
                    kind="journal",
                )

            self.assertFalse((output_root.parent / escaped_name).exists())

    def test_create_rule_pack_rejects_path_traversal_starter(self) -> None:
        with workspace_tempdir("pack-generator-") as output_root:
            with self.assertRaises(ValueError):
                create_rule_pack(
                    repo_root=ROOT,
                    output_root=output_root,
                    pack_id="safe-pack",
                    display_name="Safe Pack",
                    starter="../journal-generic",
                    kind="journal",
                )

            self.assertFalse((output_root / "safe-pack").exists())

    def test_create_rule_pack_rejects_invalid_kind_before_writing(self) -> None:
        with workspace_tempdir("pack-generator-") as output_root:
            with self.assertRaises(ValueError):
                create_rule_pack(
                    repo_root=ROOT,
                    output_root=output_root,
                    pack_id="bad-kind-pack",
                    display_name="Bad Kind Pack",
                    starter="journal-generic",
                    kind="conference",
                )

            self.assertFalse((output_root / "bad-kind-pack").exists())

    def test_create_rule_pack_rejects_empty_display_name_before_writing(self) -> None:
        with workspace_tempdir("pack-generator-") as output_root:
            with self.assertRaises(ValueError):
                create_rule_pack(
                    repo_root=ROOT,
                    output_root=output_root,
                    pack_id="empty-name-pack",
                    display_name="",
                    starter="journal-generic",
                    kind="journal",
                )

            self.assertFalse((output_root / "empty-name-pack").exists())

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

    def test_create_draft_pack_rejects_non_list_source_fields_before_writing(self) -> None:
        with workspace_tempdir("pack-generator-") as output_root:
            intake = output_root / "intake.json"
            intake.write_text(
                json.dumps(
                    {
                        "pack_id": "bad-sources",
                        "display_name": "Bad Sources",
                        "kind": "university-thesis",
                        "starter": "university-generic",
                        "guide_sources": "guide.pdf",
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                create_draft_pack(ROOT, output_root, intake)

            self.assertFalse((output_root / "bad-sources").exists())

    def test_create_draft_pack_rejects_incomplete_word_style_mapping_before_writing(self) -> None:
        with workspace_tempdir("pack-generator-") as output_root:
            intake = output_root / "intake.json"
            intake.write_text(
                json.dumps(
                    {
                        "pack_id": "bad-word-mapping",
                        "display_name": "Bad Word Mapping",
                        "kind": "university-thesis",
                        "starter": "university-generic",
                        "word_style_mappings": [
                            {
                                "role": "chapter",
                                "latex_command": "chapter",
                            }
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                create_draft_pack(ROOT, output_root, intake)

            self.assertFalse((output_root / "bad-word-mapping").exists())

    def test_create_draft_pack_rejects_non_mapping_word_style_entry_before_writing(self) -> None:
        with workspace_tempdir("pack-generator-") as output_root:
            intake = output_root / "intake.json"
            intake.write_text(
                json.dumps(
                    {
                        "pack_id": "bad-word-entry",
                        "display_name": "Bad Word Entry",
                        "kind": "university-thesis",
                        "starter": "university-generic",
                        "word_style_mappings": ["Heading 1"],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                create_draft_pack(ROOT, output_root, intake)

            self.assertFalse((output_root / "bad-word-entry").exists())

    def test_create_draft_pack_rejects_incomplete_chapter_role_mapping_before_writing(self) -> None:
        with workspace_tempdir("pack-generator-") as output_root:
            intake = output_root / "intake.json"
            intake.write_text(
                json.dumps(
                    {
                        "pack_id": "bad-chapter-mapping",
                        "display_name": "Bad Chapter Mapping",
                        "kind": "university-thesis",
                        "starter": "university-generic",
                        "chapter_role_mappings": [
                            {
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

            with self.assertRaises(ValueError):
                create_draft_pack(ROOT, output_root, intake)

            self.assertFalse((output_root / "bad-chapter-mapping").exists())


if __name__ == "__main__":
    unittest.main()
