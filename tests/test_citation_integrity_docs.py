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

    def test_readmes_have_v20_title_and_citation_integrity_parity(self) -> None:
        self._assert_contains_all(
            "README.md",
            [
            "# Thesis Skills v3.4.1",
            "citation-integrity-report.json",
            "citation-integrity-report.md",
            "citation-issues.csv",
            "Citation Integrity preview",
            "## What's new in v3.4.1",
                "I want to screen AI-generated or suspicious references",
                "## Release history",
                "## Updating your local copy",
                "git pull origin main",
                "download a fresh ZIP",
            ],
        )
        self._assert_contains_all(
            "README.zh-CN.md",
            [
            "# Thesis Skills v3.4.1",
            "citation-integrity-report.json",
            "citation-integrity-report.md",
            "citation-issues.csv",
            "Citation Integrity 预览",
            "## v3.4.1 有哪些更新",
                "我想筛查 AI 生成或可疑的参考文献",
                "## 历史迭代记录",
                "## 如何同步后续更新",
                "git pull origin main",
                "ZIP 只是一个快照",
            ],
        )

    def test_roadmap_positions_v341_as_current_release_line(self) -> None:
        self._assert_contains_all(
            "docs/roadmap.md",
            [
                "`v1.0.0` was the public-story stabilization milestone",
                "`v3.4.1` is the current documented public release line",
                "| v1.2.0 | Citation Integrity Markdown/CSV reports, clean demo, and public-example expansion |",
                "| v2.0.0 | CrossRef / OpenAlex / Semantic Scholar external verification",
            ],
        )

    def test_primary_site_pages_show_v341_version_line(self) -> None:
        for relative_path in [
            "site/index.html",
            "site/quickstart.html",
            "site/scenario-entry.html",
        ]:
            with self.subTest(path=relative_path):
                self._assert_contains_all(relative_path, ["v3.4.1"])

    def test_current_supporting_docs_reference_v12_not_v10_as_current(self) -> None:
        checks = {
            "site/copy-source.md": [
                "### v1.2.0 已包含",
                "Thesis Skills v1.2.0 — MIT License — quzhiii/thesis-skills",
            ],
            "site/README.md": [
                "# Thesis Skills 静态站点",
                "历史 v1.0 页面备份",
                "历史 v1.1 设计迭代目录（保留参考）",
            ],
            "docs/architecture.md": [
                "current v1.2.0 public contract",
            ],
            "90-rules/STARTER_PACK_BASELINE.md": [
                "current v3.4.1 public contract",
                "Current v3.4.1 baseline summary",
            ],
            "02-latex-to-word/THESIS_LATEX_TO_WORD.md": [
                "current v1.2.0 first-class export promise",
            ],
            "site/index-product-redraft.html": [
                "current v3.3.0 public story",
                "当前 v3.3.0 公开入口请看正式首页",
                "当前版本已包含",
            ],
        }
        for relative_path, snippets in checks.items():
            with self.subTest(path=relative_path):
                self._assert_contains_all(relative_path, snippets)


if __name__ == "__main__":
    unittest.main()
