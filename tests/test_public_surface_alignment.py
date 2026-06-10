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

    def test_module_docs_name_current_claim_citation_checker_contract(self) -> None:
        self._assert_contains_all(
            "20-check-claim-citation/THESIS_CLAIM_CITATION.md",
            [
                "support_review_label",
                "support_review_reason",
                "support_signals",
                "risk_signals",
                "cluster_keys",
                "cluster_risk_summary",
                "next_actions",
                "citation_needed_candidates",
                "uncited_references",
                "Suggested actions are advisory review cues",
                "No automatic citation rewrite or bibliography insertion",
            ],
        )
        text = (ROOT / "20-check-claim-citation/THESIS_CLAIM_CITATION.md").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("No automatic citation rewrite or suggestion.", text)

    def test_module_docs_name_current_report_html_contract(self) -> None:
        self._assert_contains_all(
            "32-claim-citation-html/THESIS_CLAIM_CITATION_HTML.md",
            [
                "P0 / P1 / P2 / P3 review groups",
                "issue-card style summaries",
                "evidence, rationale, and suggested action",
                "readiness / references / claim-citation / final-audit",
                "mobile-readable",
                "JSON / Markdown / CSV / CLI contracts remain unchanged",
            ],
        )
        self._assert_contains_all(
            "30-final-audit-html/THESIS_FINAL_AUDIT_HTML.md",
            [
                "related report links",
                "readiness-report.json",
                "reference-audit-ledger.html",
                "claim-citation-triage.html",
                "narrow-screen",
            ],
        )
        self._assert_contains_all(
            "31-reference-ledger-html/THESIS_REFERENCE_AUDIT_LEDGER_HTML.md",
            [
                "Final references only",
                "All bibliography entries",
                "Unused bibliography entries",
                "Evidence rows",
                "readiness / references / claim-citation / final-audit",
                "narrow-screen",
            ],
        )

    def test_report_index_and_final_audit_docs_do_not_keep_future_html_language(self) -> None:
        report_index = (ROOT / "29-report-index/THESIS_REPORT_INDEX.md").read_text(
            encoding="utf-8"
        )
        final_audit = (ROOT / "27-final-audit-report/THESIS_FINAL_AUDIT_REPORT.md").read_text(
            encoding="utf-8"
        )

        self.assertNotIn("Individual HTML detail pages can be added later", report_index)
        self.assertNotIn("future static HTML report surfaces", final_audit)
        self._assert_contains_all(
            "29-report-index/THESIS_REPORT_INDEX.md",
            [
                "final-audit-report.html",
                "reference-audit-ledger.html",
                "claim-citation-triage.html",
                "HTML detail",
            ],
        )

    def test_reference_ledger_module_doc_lists_full_csv_contract(self) -> None:
        self._assert_contains_all(
            "28-reference-audit-ledger/THESIS_REFERENCE_AUDIT_LEDGER.md",
            [
                "key,title,authors,year,venue,doi,scope,source_checked,status,issue,action_suggested,is_final_reference,is_cited_in_tex,is_unused_bib_entry",
            ],
        )

    def test_changelog_names_current_html_review_contract(self) -> None:
        self._assert_contains_all(
            "CHANGELOG.md",
            [
                "P0 / P1 / P2 / P3 review groups",
                "evidence, rationale, and suggested action",
                "narrow-screen",
                "JSON / Markdown / CSV / CLI",
            ],
        )

    def test_architecture_maps_current_evidence_and_report_modules(self) -> None:
        self._assert_contains_all(
            "docs/architecture.md",
            [
                "17-final-reference-set",
                "18-verify-references",
                "19-check-hallucination-risk",
                "20-check-claim-citation",
                "23-check-final-cleanup",
                "25-check-statistical-consistency",
                "26-check-manual-anchor",
                "27-final-audit-report",
                "28-reference-audit-ledger",
                "29-report-index",
                "30-final-audit-html",
                "31-reference-ledger-html",
                "32-claim-citation-html",
                "run_evidence_pipeline.py",
            ],
        )

    def test_getting_started_zh_qualifies_basic_workflow_and_links_current_extensions(self) -> None:
        self._assert_contains_all(
            "docs/getting-started-zh.md",
            [
                "基础工作流一览",
                "16-check-readiness",
                "run_evidence_pipeline.py",
                "27-final-audit-report",
                "32-claim-citation-html",
            ],
        )

    def test_commercialization_doc_points_to_v341_public_alignment(self) -> None:
        text = (ROOT / "docs/commercialization-v0.1.md").read_text(encoding="utf-8")
        self.assertIn("v3.4.1 public alignment", text)
        self.assertNotIn("v3.4.0 public alignment", text)


if __name__ == "__main__":
    unittest.main()
