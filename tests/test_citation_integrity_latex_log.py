from __future__ import annotations

import unittest

from core.citation_integrity.latex_log_parser import lint_latex_log_text
from core.citation_integrity.cross_reference_lint import lint_cross_references


class CitationIntegrityLatexLogTest(unittest.TestCase):
    def test_undefined_citation_in_log_is_blocking(self) -> None:
        issues = lint_latex_log_text(
            "LaTeX Warning: Citation `missing2024' on page 1 undefined on input line 7.\n",
            "main.log",
            default_file="main.tex",
        )

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].severity, "BLOCK")
        self.assertEqual(issues[0].code, "CI-LOG-UNDEFINED-CITATION")
        self.assertEqual(issues[0].category, "latex_log_warning")

    def test_missing_ref_target_is_advisory_warning(self) -> None:
        issues = lint_cross_references(
            {"main.tex": "See Figure~\\ref{fig:missing}.\n\\label{fig:unused}\n"}
        )

        codes = {issue.code for issue in issues}
        self.assertIn("CI-MISSING-LABEL", codes)
        self.assertIn("CI-UNUSED-LABEL", codes)
        self.assertEqual({issue.severity for issue in issues}, {"WARN"})


if __name__ == "__main__":
    unittest.main()
