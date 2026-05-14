from __future__ import annotations

import csv
import io
import json
import unittest

from core.citation_integrity.doi_candidates import (
    build_doi_candidate_report,
    write_doi_candidate_csv,
    write_doi_candidate_json,
)
from core.citation_integrity.models import BibEntry
from tests.helpers import workspace_tempdir


class DoiCandidateReportTest(unittest.TestCase):
    def _entry(self, key: str, entry_type: str = "article", fields: dict[str, str] | None = None) -> BibEntry:
        return BibEntry(
            key=key,
            entry_type=entry_type,
            file="ref/refs.bib",
            line=1,
            fields=fields or {"title": "Missing DOI", "year": "2024"},
            body="",
        )

    def test_entry_without_doi_and_confident_candidate_is_included(self) -> None:
        entries = [self._entry("missing2024", fields={"title": "Missing DOI", "year": "2024"})]
        external_report = {
            "entries": [
                {
                    "citation_key": "missing2024",
                    "providers": [
                        {
                            "source": "crossref",
                            "success": True,
                            "candidates": [
                                {
                                    "doi": "10.1000/missing",
                                    "title": "Missing DOI",
                                    "year": "2024",
                                    "authors": ["Jane Smith"],
                                    "title_similarity": 0.92,
                                }
                            ],
                        }
                    ],
                }
            ]
        }

        report = build_doi_candidate_report(entries, external_report)

        self.assertEqual(report["module"], "missing_doi_candidates")
        self.assertEqual(report["version"], "3.3")
        self.assertEqual(report["summary"]["candidate_count"], 1)
        self.assertEqual(report["entries"][0]["citation_key"], "missing2024")
        self.assertEqual(report["entries"][0]["candidate_doi"], "10.1000/missing")
        self.assertEqual(report["entries"][0]["provider"], "crossref")

    def test_entry_with_doi_non_article_and_low_confidence_are_excluded(self) -> None:
        entries = [
            self._entry("hasdoi2024", fields={"title": "Has DOI", "year": "2024", "doi": "10.1000/local"}),
            self._entry("book2024", entry_type="book", fields={"title": "Book", "year": "2024"}),
            self._entry("low2024", fields={"title": "Low", "year": "2024"}),
        ]
        external_report = {
            "entries": [
                {"citation_key": "hasdoi2024", "providers": [{"source": "crossref", "success": True, "candidates": [{"doi": "10.1000/has", "title_similarity": 1.0}]}]},
                {"citation_key": "book2024", "providers": [{"source": "crossref", "success": True, "candidates": [{"doi": "10.1000/book", "title_similarity": 1.0}]}]},
                {"citation_key": "low2024", "providers": [{"source": "crossref", "success": True, "candidates": [{"doi": "10.1000/low", "title_similarity": 0.69}]}]},
            ]
        }

        report = build_doi_candidate_report(entries, external_report)

        self.assertEqual(report["entries"], [])
        self.assertEqual(report["summary"]["candidate_count"], 0)

    def test_inproceedings_without_doi_can_be_included(self) -> None:
        entries = [self._entry("conf2024", entry_type="inproceedings", fields={"title": "Conference", "year": "2024"})]
        external_report = {
            "entries": [
                {"citation_key": "conf2024", "providers": [{"source": "openalex", "success": True, "candidates": [{"doi": "10.1000/conf", "title": "Conference", "title_similarity": 0.8}]}]}
            ]
        }

        report = build_doi_candidate_report(entries, external_report)

        self.assertEqual(len(report["entries"]), 1)
        self.assertEqual(report["entries"][0]["candidate_doi"], "10.1000/conf")

    def test_writes_json_and_csv_reports(self) -> None:
        report = {
            "module": "missing_doi_candidates",
            "version": "3.3",
            "summary": {"candidate_count": 1},
            "entries": [
                {
                    "citation_key": "missing2024",
                    "local_title": "Missing DOI",
                    "local_year": "2024",
                    "candidate_doi": "10.1000/missing",
                    "candidate_title": "Missing DOI",
                    "candidate_year": "2024",
                    "candidate_authors": "Jane Smith",
                    "provider": "crossref",
                    "confidence": 0.92,
                    "recommended_action": "Verify DOI manually and add to bib entry if confirmed.",
                }
            ],
        }
        with workspace_tempdir("doi-candidates-") as tmp:
            json_path = tmp / "reports" / "missing-doi-candidates.json"
            csv_path = tmp / "reports" / "missing-doi-candidates.csv"
            write_doi_candidate_json(report, json_path)
            write_doi_candidate_csv(report, csv_path)
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            rows = list(csv.DictReader(io.StringIO(csv_path.read_text(encoding="utf-8"))))

        self.assertEqual(payload["module"], "missing_doi_candidates")
        self.assertEqual(rows[0]["citation_key"], "missing2024")


if __name__ == "__main__":
    unittest.main()
