from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CitationIntegrityDocsTest(unittest.TestCase):
    def _assert_contains_all(self, relative_path: str, snippets: list[str]) -> None:
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        for snippet in snippets:
            self.assertIn(snippet, text, f"{relative_path} missing {snippet!r}")

    def test_examples_doc_mentions_v12_outputs_and_both_demos(self) -> None:
        self._assert_contains_all(
            "docs/examples.md",
            [
                "citation-integrity-report.json",
                "citation-integrity-report.md",
                "citation-issues.csv",
                "examples/citation-integrity-broken/",
                "examples/citation-integrity-clean/",
            ],
        )

    def test_quickstart_doc_mentions_rich_citation_artifacts(self) -> None:
        self._assert_contains_all(
            "docs/quickstart.md",
            [
                "citation-integrity-report.json",
                "citation-integrity-report.md",
                "citation-issues.csv",
            ],
        )

    def test_artifact_gallery_mentions_citation_integrity_markdown_and_csv_outputs(self) -> None:
        self._assert_contains_all(
            "site/artifact-gallery.html",
            [
                "citation-integrity-report.json",
                "citation-integrity-report.md",
                "citation-issues.csv",
                "Citation Integrity",
            ],
        )

    def test_main_site_pages_surface_citation_integrity_bundle(self) -> None:
        required_snippets = [
            "citation-integrity-report.json",
            "citation-integrity-report.md",
            "citation-issues.csv",
        ]
        for relative_path in [
            "site/index.html",
            "site/quickstart.html",
            "site/scenario-entry.html",
        ]:
            with self.subTest(path=relative_path):
                self._assert_contains_all(relative_path, required_snippets)


if __name__ == "__main__":
    unittest.main()
