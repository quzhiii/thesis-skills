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


if __name__ == "__main__":
    unittest.main()
