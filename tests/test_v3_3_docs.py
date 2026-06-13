from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class V33DocsTest(unittest.TestCase):
    def _assert_contains_all(self, relative_path: str, snippets: list[str]) -> None:
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        for snippet in snippets:
            self.assertIn(snippet, text, f"{relative_path} missing {snippet!r}")

    def test_readme_mentions_v3_3_reference_hardening(self) -> None:
        self._assert_contains_all(
            "README.md",
            [
                "# Thesis Skills v3.5.0",
                "What's new in v3.5.0",
                "final-reference-set-report.json",
                "missing-doi-candidates.json",
                "url-verification-report.json",
            ],
        )

    def test_readme_zh_mentions_v3_3_reference_hardening(self) -> None:
        self._assert_contains_all(
            "README.zh-CN.md",
            [
                "# Thesis Skills v3.5.0",
                "v3.5.0 有哪些更新",
                "final-reference-set-report.json",
                "missing-doi-candidates.json",
                "url-verification-report.json",
            ],
        )

    def test_changelog_mentions_v3_3(self) -> None:
        self._assert_contains_all(
            "CHANGELOG.md",
            [
                "## v3.3.0",
                "final reference set",
                "missing-doi-candidates.json",
                "url-verification-report.json",
            ],
        )

    def test_roadmap_mentions_v3_3(self) -> None:
        self._assert_contains_all(
            "docs/roadmap.md",
            [
                "v3.3.0",
                "final reference set",
                "URL verification",
                "DOI candidates",
            ],
        )

    def test_modules_doc_mentions_new_artifacts(self) -> None:
        self._assert_contains_all(
            "docs/modules.md",
            [
                "final-reference-set-report.json",
                "missing-doi-candidates.json",
                "url-verification-report.json",
            ],
        )

    def test_examples_doc_mentions_new_reports(self) -> None:
        self._assert_contains_all(
            "docs/examples.md",
            [
                "final-reference-set-report.json",
                "missing-doi-candidates.json",
                "url-verification-report.json",
            ],
        )

    def test_versions_bumped_to_v3_5_0(self) -> None:
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        manifest = (ROOT / "skills-manifest.json").read_text(encoding="utf-8")
        self.assertIn('version = "3.5.0"', pyproject)
        self.assertIn('"version": "3.5.0"', manifest)


if __name__ == "__main__":
    unittest.main()
