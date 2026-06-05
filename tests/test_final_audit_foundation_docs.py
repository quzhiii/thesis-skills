from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class FinalAuditFoundationDocsTest(unittest.TestCase):
    def _assert_contains_all(self, relative_path: str, snippets: list[str]) -> None:
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        for snippet in snippets:
            self.assertIn(snippet, text, f"{relative_path} missing {snippet!r}")

    def test_docs_surface_statistical_and_manual_anchor_checkers(self) -> None:
        self._assert_contains_all(
            "docs/modules.md",
            [
                "25-check-statistical-consistency",
                "26-check-manual-anchor",
                "statistical-consistency-report.json",
                "manual-anchor-report.json",
                "27-final-audit-report",
                "28-reference-audit-ledger",
                "final-audit-report.json",
                "reference-audit-ledger.csv",
                "29-report-index",
                "30-final-audit-html",
                "31-reference-ledger-html",
                "32-claim-citation-html",
                "reports/index.html",
                "reports/final-audit-report.html",
                "reports/reference-audit-ledger.html",
                "reports/claim-citation-triage.html",
            ],
        )
        self._assert_contains_all(
            "docs/examples.md",
            [
                "Statistical consistency checker",
                "Manual anchor checker",
                "Final audit report",
                "Reference audit ledger",
                "Static report index",
                "Final audit HTML",
                "Reference audit ledger HTML",
                "Claim-citation HTML",
                "25-check-statistical-consistency/check_statistical_consistency.py",
                "26-check-manual-anchor/check_manual_anchor.py",
                "27-final-audit-report/build_final_audit_report.py",
                "28-reference-audit-ledger/build_reference_audit_ledger.py",
                "29-report-index/build_report_index.py",
                "30-final-audit-html/build_final_audit_html.py",
                "31-reference-ledger-html/build_reference_audit_ledger_html.py",
                "32-claim-citation-html/build_claim_citation_html.py",
            ],
        )

    def test_readmes_surface_new_final_audit_foundations(self) -> None:
        self._assert_contains_all(
            "README.md",
            [
                "Statistical Consistency Checker",
                "Manual Anchor Checker",
                "reports/statistical-consistency-report.json",
                "reports/manual-anchor-report.json",
                "reports/final-audit-report.json",
                "reports/reference-audit-ledger.csv",
                "reports/index.html",
                "reports/final-audit-report.html",
                "reports/reference-audit-ledger.html",
                "reports/claim-citation-triage.html",
            ],
        )
        self._assert_contains_all(
            "README.zh-CN.md",
            [
                "reports/statistical-consistency-report.json",
                "reports/manual-anchor-report.json",
                "reports/final-audit-report.json",
                "reports/reference-audit-ledger.csv",
                "reports/index.html",
                "reports/final-audit-report.html",
                "reports/reference-audit-ledger.html",
                "reports/claim-citation-triage.html",
                "不自动改写统计表达",
            ],
        )

    def test_public_overview_lists_all_local_html_surfaces(self) -> None:
        self._assert_contains_all(
            "README.md",
            [
                "**Static local report UX**: `reports/index.html`, `reports/final-audit-report.html`, `reports/reference-audit-ledger.html`, and `reports/claim-citation-triage.html`",
            ],
        )
        self._assert_contains_all(
            "README.zh-CN.md",
            [
                "**本地静态报告 UX**：新增 `reports/index.html`、`reports/final-audit-report.html`、`reports/reference-audit-ledger.html`、`reports/claim-citation-triage.html`",
            ],
        )
        self._assert_contains_all(
            "docs/roadmap.md",
            [
                "claim-citation detail page: `32-claim-citation-html/build_claim_citation_html.py`, writing `reports/claim-citation-triage.html` from `claim-citation-triage-report.json` as a local reading surface",
            ],
        )


if __name__ == "__main__":
    unittest.main()
