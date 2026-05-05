from __future__ import annotations

import csv
import unittest

from core.citation_integrity.report import (
    build_citation_integrity_report,
    render_citation_integrity_markdown,
    write_citation_integrity_csv,
)
from tests.helpers import workspace_tempdir


class CitationIntegrityReportOutputTest(unittest.TestCase):
    def test_renders_markdown_report_with_status_summary_and_next_actions(self) -> None:
        report = build_citation_integrity_report(
            {"main.tex": "\\cite{present,missing}\n"},
            {"ref/refs.bib": "@article{present, title={Present}, author={A}, year={2024}, journal={J}, doi={10.1000/p}}\n"},
            current_year=2026,
        )

        markdown = render_citation_integrity_markdown(report)

        self.assertIn("# Citation Integrity Report", markdown)
        self.assertIn("**Status:** BLOCK", markdown)
        self.assertIn("## Summary", markdown)
        self.assertIn("missing_cited_keys", markdown)
        self.assertIn("## Blocking Issues", markdown)
        self.assertIn("CI-MISSING-KEY", markdown)
        self.assertIn("## Next Actions", markdown)

    def test_writes_csv_risk_list_for_non_pass_issues(self) -> None:
        report = build_citation_integrity_report(
            {"main.tex": "\\cite{missing}\n"},
            {"ref/refs.bib": "@article{unused, title={Unused}, author={A}, year={2024}, journal={J}}\n"},
            current_year=2026,
        )

        with workspace_tempdir("citation-csv-") as tempdir:
            output = tempdir / "reports" / "citation-issues.csv"
            write_citation_integrity_csv(report, output)
            rows = list(csv.DictReader(output.read_text(encoding="utf-8").splitlines()))

        self.assertGreaterEqual(len(rows), 2)
        self.assertEqual(rows[0]["severity"], "BLOCK")
        self.assertEqual(rows[0]["code"], "CI-MISSING-KEY")
        self.assertIn("suggested_action", rows[0])


if __name__ == "__main__":
    unittest.main()
