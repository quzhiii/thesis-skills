from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PublicSurfaceAlignmentTest(unittest.TestCase):
    def _assert_contains_all(self, relative_path: str, snippets: list[str]) -> None:
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        for snippet in snippets:
            self.assertIn(snippet, text, f"{relative_path} missing {snippet!r}")

    def test_public_docs_describe_shipped_html_review_surfaces(self) -> None:
        shared_snippets = [
            "P0 / P1 / P2 / P3 review groups",
            "issue-card style summaries",
            "readiness / references / claim-citation / final-audit",
            "mobile-readable local HTML bundle",
            "JSON / CSV remain the source of truth",
        ]
        self._assert_contains_all("README.md", shared_snippets)
        self._assert_contains_all(
            "README.zh-CN.md",
            [
                "P0 / P1 / P2 / P3 复核分组",
                "issue-card 风格摘要",
                "readiness / references / claim-citation / final-audit",
                "手机窄屏可读的本地 HTML bundle",
                "JSON / CSV 仍然是 source of truth",
            ],
        )

    def test_docs_and_examples_name_current_report_ux_contract(self) -> None:
        self._assert_contains_all(
            "docs/roadmap.md",
            [
                "Current shipped HTML behavior:",
                "claim-citation P0 / P1 / P2 / P3 review groups",
                "issue-card summaries with evidence, rationale, and suggested action",
                "symmetric deep links between readiness, references, claim-citation, and final-audit report surfaces",
                "narrow-screen readability improvements for local HTML review",
            ],
        )
        self._assert_contains_all(
            "docs/examples.md",
            [
                "The mixed demo can also be rendered as `reports/claim-citation-triage.html`",
                "P0 / P1 / P2 / P3 review groups",
                "issue-card style summaries",
                "deep links to readiness, final-audit, and reference-ledger surfaces",
            ],
        )
        self._assert_contains_all(
            "docs/quickstart.md",
            [
                "claim-citation-triage.html",
                "P0 / P1 / P2 / P3 review groups",
                "readiness / references / claim-citation / final-audit",
            ],
        )

    def test_site_copy_surfaces_current_html_review_language(self) -> None:
        self._assert_contains_all(
            "site/copy-source.md",
            [
                "claim-citation P0 / P1 / P2 / P3 复核分组",
                "issue-card 风格摘要",
                "readiness / references / claim-citation / final-audit 深链",
                "手机窄屏可读的本地 HTML bundle",
            ],
        )
        self._assert_contains_all(
            "site/artifact-gallery.html",
            [
                "claim-citation P0 / P1 / P2 / P3 复核分组",
                "issue-card 风格摘要",
                "readiness / references / claim-citation / final-audit 深链",
                "手机窄屏可读",
            ],
        )
        self._assert_contains_all(
            "site/quickstart.html",
            [
                "claim-citation-triage.html",
                "P0 / P1 / P2 / P3 复核分组",
                "readiness / references / claim-citation / final-audit",
            ],
        )

    def test_modules_and_site_entry_pages_match_report_surface_contract(self) -> None:
        self._assert_contains_all(
            "docs/modules.md",
            [
                "P0 / P1 / P2 / P3 review groups",
                "issue-card summaries",
                "deep links to readiness / references / claim-citation / final-audit",
                "JSON / CSV source artifacts",
            ],
        )
        self._assert_contains_all(
            "site/index.html",
            [
                "claim-citation P0 / P1 / P2 / P3 复核分组",
                "issue-card 风格摘要",
                "readiness / references / claim-citation / final-audit 深链",
            ],
        )
        self._assert_contains_all(
            "site/scenario-entry.html",
            [
                "claim-citation HTML 复核页",
                "P0 / P1 / P2 / P3 复核分组",
                "不自动判断真假",
            ],
        )
        self._assert_contains_all(
            "site/docs-home.html",
            [
                "本地 HTML 报告界面",
                "claim-citation 复核分组",
                "readiness / references / claim-citation / final-audit",
            ],
        )


if __name__ == "__main__":
    unittest.main()
