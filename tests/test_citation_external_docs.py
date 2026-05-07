from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CitationExternalDocsTest(unittest.TestCase):
    def test_readme_mentions_external_verification_alpha(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for required in (
            "external-verification-report.json",
            "CrossRef",
            "OpenAlex",
        ):
            self.assertIn(required, readme, f"README.md missing: {required}")
        self.assertIn("alpha", readme.lower())

    def test_readme_zh_mentions_external_verification_alpha(self) -> None:
        readme_zh = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
        for required in (
            "external-verification-report.json",
            "CrossRef",
            "OpenAlex",
        ):
            self.assertIn(required, readme_zh, f"README.zh-CN.md missing: {required}")
        self.assertIn("alpha", readme_zh.lower())

    def test_modules_doc_includes_verify_references(self) -> None:
        modules = (ROOT / "docs" / "modules.md").read_text(encoding="utf-8")
        self.assertIn("18-verify-references", modules)
        self.assertIn("external-verification-report.json", modules)

    def test_changelog_has_v2_alpha_entry(self) -> None:
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn("v2.0.0-alpha", changelog)

    def test_examples_doc_mentions_v2_stable_external_verification(self) -> None:
        examples = (ROOT / "docs" / "examples.md").read_text(encoding="utf-8")
        for required in (
            "18-verify-references/verify_external_references.py",
            "Semantic Scholar",
            "external_verification",
            "readiness",
        ):
            self.assertIn(required, examples)

    def test_roadmap_marks_v2_external_verification_released(self) -> None:
        roadmap = (ROOT / "docs" / "roadmap.md").read_text(encoding="utf-8")
        for required in (
            "v2.0.0",
            "CrossRef / OpenAlex / Semantic Scholar",
            "external_verification",
            "V3.0",
        ):
            self.assertIn(required, roadmap)

    def test_artifact_gallery_surfaces_external_verification_report(self) -> None:
        gallery = (ROOT / "site" / "artifact-gallery.html").read_text(encoding="utf-8")
        for required in (
            "external-verification-report.json",
            "Semantic Scholar",
            "external_verification",
            "readiness",
        ):
            self.assertIn(required, gallery)


if __name__ == "__main__":
    unittest.main()
