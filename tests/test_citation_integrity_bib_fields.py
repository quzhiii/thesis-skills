from __future__ import annotations

import unittest

from core.citation_integrity.bib_parser import parse_bib_entries_from_text
from core.citation_integrity.field_lint import lint_bib_fields


class CitationIntegrityBibFieldLintTest(unittest.TestCase):
    def test_required_fields_and_type_specific_fields_are_warnings(self) -> None:
        entries = parse_bib_entries_from_text(
            "@article{article1,\n"
            "  title = {Article Without Journal},\n"
            "  author = {Smith, Jane},\n"
            "  year = {2024}\n"
            "}\n"
            "@inproceedings{conf1,\n"
            "  title = {Conference Without Booktitle},\n"
            "  author = {Doe, Jane},\n"
            "  year = {2023}\n"
            "}\n"
            "@book{book1,\n"
            "  title = {Book Without Publisher},\n"
            "  author = {Lee, Jane},\n"
            "  year = {2022}\n"
            "}\n"
            "@misc{misc1,\n"
            "  title = {Missing Author and Year}\n"
            "}\n",
            "ref/refs.bib",
        )

        issues = lint_bib_fields(entries, current_year=2026)

        self.assertEqual({issue.severity for issue in issues}, {"WARN"})
        self.assertIn("CI-MISSING-JOURNAL", {issue.code for issue in issues})
        self.assertIn("CI-MISSING-BOOKTITLE", {issue.code for issue in issues})
        self.assertIn("CI-MISSING-PUBLISHER", {issue.code for issue in issues})
        self.assertIn("CI-MISSING-AUTHOR", {issue.code for issue in issues})
        self.assertIn("CI-MISSING-YEAR", {issue.code for issue in issues})

    def test_doi_and_year_shape_are_non_blocking_warnings(self) -> None:
        entries = parse_bib_entries_from_text(
            "@article{badshape,\n"
            "  title = {Bad Shapes},\n"
            "  author = {Smith, Jane},\n"
            "  year = {soon},\n"
            "  journal = {Demo Journal},\n"
            "  doi = {not a doi}\n"
            "}\n"
            "@article{future,\n"
            "  title = {Future Work},\n"
            "  author = {Doe, Jane},\n"
            "  year = {2029},\n"
            "  journal = {Demo Journal},\n"
            "  doi = {10.1000/demo}\n"
            "}\n"
            "@article{missingdoi,\n"
            "  title = {Missing DOI},\n"
            "  author = {Chen, Jane},\n"
            "  year = {2025},\n"
            "  journal = {Demo Journal}\n"
            "}\n",
            "ref/refs.bib",
        )

        issues = lint_bib_fields(entries, current_year=2026)

        codes = {issue.code for issue in issues}
        self.assertIn("CI-MALFORMED-DOI", codes)
        self.assertIn("CI-INVALID-YEAR", codes)
        self.assertIn("CI-FUTURE-YEAR", codes)
        self.assertIn("CI-MISSING-DOI", codes)
        self.assertEqual({issue.severity for issue in issues}, {"WARN"})


if __name__ == "__main__":
    unittest.main()
