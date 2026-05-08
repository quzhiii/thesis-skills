from __future__ import annotations

import csv
import io
import json
import unittest
from pathlib import Path

from core.citation_integrity.models import BibEntry
from tests.helpers import workspace_tempdir


class HallucinationRiskScoreTest(unittest.TestCase):
    def _entry(self, key: str = "test2024", fields: dict[str, str] | None = None, entry_type: str = "article") -> BibEntry:
        return BibEntry(
            key=key,
            entry_type=entry_type,
            file="ref/refs.bib",
            line=1,
            fields=fields or {"title": "Test Title", "year": "2024"},
            body="",
        )

    def test_match_with_doi_exact_returns_pass(self) -> None:
        from core.citation_integrity.hallucination_risk import score_hallucination_risk

        entry = self._entry(fields={"title": "Test Title", "year": "2024", "doi": "10.1000/test"})
        external_entry = {
            "match_status": "MATCH",
            "providers": [
                {"source": "crossref", "success": True, "candidate_count": 1, "candidates": [{"doi": "10.1000/test", "doi_exact_match": True, "title_similarity": 1.0}]},
            ],
        }
        result = score_hallucination_risk(entry, external_entry)

        self.assertEqual(result["risk_label"], "PASS")
        self.assertLess(result["hallucination_risk_score"], 0.25)

    def test_no_candidate_returns_high_risk(self) -> None:
        from core.citation_integrity.hallucination_risk import score_hallucination_risk

        entry = self._entry(fields={"title": "Fabricated Paper Title", "year": "2024"})
        external_entry = {
            "match_status": "NO_CANDIDATE",
            "providers": [
                {"source": "crossref", "success": True, "candidate_count": 0, "candidates": []},
                {"source": "openalex", "success": True, "candidate_count": 0, "candidates": []},
                {"source": "semantic_scholar", "success": True, "candidate_count": 0, "candidates": []},
            ],
        }
        result = score_hallucination_risk(entry, external_entry)

        self.assertEqual(result["risk_label"], "HIGH_RISK")
        self.assertGreaterEqual(result["hallucination_risk_score"], 0.75)

    def test_cjk_title_is_unsupported_not_high_risk(self) -> None:
        from core.citation_integrity.hallucination_risk import score_hallucination_risk

        entry = self._entry(
            key="zhang2024",
            fields={"title": "人工智能辅助论文写作研究", "year": "2024"},
        )
        result = score_hallucination_risk(entry, {})

        self.assertEqual(result["risk_label"], "UNSUPPORTED")
        self.assertEqual(result["hallucination_risk_score"], 0.0)

    def test_cjk_journal_is_unsupported(self) -> None:
        from core.citation_integrity.hallucination_risk import score_hallucination_risk

        entry = self._entry(
            key="li2023",
            fields={"title": "Some English Title", "journal": "计算机学报", "year": "2023"},
        )
        result = score_hallucination_risk(entry, {})

        self.assertEqual(result["risk_label"], "UNSUPPORTED")
        self.assertEqual(result["hallucination_risk_score"], 0.0)

    def test_thesis_without_doi_is_unsupported(self) -> None:
        from core.citation_integrity.hallucination_risk import score_hallucination_risk

        entry = self._entry(
            key="wang2024master",
            fields={"title": "A Study of Something", "year": "2024"},
            entry_type="mastersthesis",
        )
        result = score_hallucination_risk(entry, {})

        self.assertEqual(result["risk_label"], "UNSUPPORTED")

    def test_metadata_mismatch_returns_review(self) -> None:
        from core.citation_integrity.hallucination_risk import score_hallucination_risk

        entry = self._entry(fields={"title": "Real Title with Slight Variation", "year": "2023"})
        external_entry = {
            "match_status": "REVIEW",
            "providers": [
                {"source": "crossref", "success": True, "candidate_count": 1, "candidates": [{"title": "Real Title with Different Ending", "title_similarity": 0.72}]},
            ],
        }
        result = score_hallucination_risk(entry, external_entry)

        self.assertIn(result["risk_label"], ("REVIEW", "WARN"))
        self.assertGreaterEqual(result["hallucination_risk_score"], 0.25)

    def test_unavailable_providers_returns_warn(self) -> None:
        from core.citation_integrity.hallucination_risk import score_hallucination_risk

        entry = self._entry(fields={"title": "Offline Paper", "year": "2024"})
        external_entry = {
            "match_status": "UNAVAILABLE",
            "providers": [
                {"source": "crossref", "success": False, "candidate_count": 0, "error": "timeout"},
                {"source": "openalex", "success": False, "candidate_count": 0, "error": "timeout"},
            ],
        }
        result = score_hallucination_risk(entry, external_entry)

        self.assertEqual(result["risk_label"], "WARN")

    def test_doi_mismatch_increases_score(self) -> None:
        from core.citation_integrity.hallucination_risk import score_hallucination_risk

        entry = self._entry(fields={"title": "A Paper", "year": "2024", "doi": "10.1000/wrong"})
        external_entry = {
            "match_status": "REVIEW",
            "providers": [
                {"source": "crossref", "success": True, "candidate_count": 1, "candidates": [{"doi": "10.1000/correct", "title_similarity": 0.85}]},
            ],
        }
        result_mismatch = score_hallucination_risk(entry, external_entry)

        entry_match = self._entry(fields={"title": "A Paper", "year": "2024", "doi": "10.1000/correct"})
        external_match = {
            "match_status": "MATCH",
            "providers": [
                {"source": "crossref", "success": True, "candidate_count": 1, "candidates": [{"doi": "10.1000/correct", "doi_exact_match": True, "title_similarity": 1.0}]},
            ],
        }
        result_match = score_hallucination_risk(entry_match, external_match)

        self.assertGreater(result_mismatch["hallucination_risk_score"], result_match["hallucination_risk_score"])

    def test_missing_external_entry_defaults_to_review(self) -> None:
        from core.citation_integrity.hallucination_risk import score_hallucination_risk

        entry = self._entry(fields={"title": "Unknown Paper", "year": "2024"})
        result = score_hallucination_risk(entry, None)

        self.assertNotEqual(result["risk_label"], "PASS")
        self.assertGreaterEqual(result["hallucination_risk_score"], 0.25)

    def test_year_mismatch_increases_score(self) -> None:
        from core.citation_integrity.hallucination_risk import score_hallucination_risk

        entry = self._entry(fields={"title": "Paper", "year": "2024"})
        external_entry = {
            "match_status": "REVIEW",
            "providers": [
                {"source": "crossref", "success": True, "candidate_count": 1, "candidates": [{"title_similarity": 0.9, "year": "2020"}]},
            ],
        }
        result = score_hallucination_risk(entry, external_entry)

        self.assertIn("year", result.get("evidence", {}).get("metadata_mismatches", []))


class HallucinationRiskReportTest(unittest.TestCase):
    def _entry(self, key: str, fields: dict[str, str] | None = None, entry_type: str = "article") -> BibEntry:
        return BibEntry(
            key=key,
            entry_type=entry_type,
            file="ref/refs.bib",
            line=1,
            fields=fields or {"title": "Test", "year": "2024"},
            body="",
        )

    def test_builds_report_with_module_version_status_summary_entries(self) -> None:
        from core.citation_integrity.hallucination_risk import build_hallucination_risk_report

        entries = [self._entry("pass2024", {"title": "Real Paper", "year": "2024", "doi": "10.1000/real"})]
        external_report = {
            "entries": [
                {
                    "citation_key": "pass2024",
                    "match_status": "MATCH",
                    "providers": [{"source": "crossref", "success": True, "candidate_count": 1, "candidates": [{"doi": "10.1000/real", "doi_exact_match": True, "title_similarity": 1.0}]}],
                    "consensus": {"top_candidate": {"doi": "10.1000/real", "doi_exact_match": True}},
                }
            ],
        }
        report = build_hallucination_risk_report(entries, external_report)

        self.assertEqual(report["module"], "citation_hallucination_risk")
        self.assertEqual(report["version"], "3.0")
        self.assertIn("generated_at", report)
        self.assertIn("status", report)
        self.assertIn("summary", report)
        self.assertIn("entries", report)
        self.assertEqual(report["summary"]["entries_considered"], 1)
        self.assertEqual(report["summary"]["pass_entries"], 1)

    def test_status_becomes_high_risk_if_any_entry_is_high_risk(self) -> None:
        from core.citation_integrity.hallucination_risk import build_hallucination_risk_report

        entries = [
            self._entry("ok2024", {"title": "Real Paper", "year": "2024"}),
            self._entry("fake2024", {"title": "Completely Fabricated Title", "year": "2024"}),
        ]
        external_report = {
            "entries": [
                {
                    "citation_key": "ok2024",
                    "match_status": "MATCH",
                    "providers": [{"source": "crossref", "success": True, "candidate_count": 1, "candidates": [{"doi_exact_match": True, "title_similarity": 1.0}]}],
                },
                {
                    "citation_key": "fake2024",
                    "match_status": "NO_CANDIDATE",
                    "providers": [
                        {"source": "crossref", "success": True, "candidate_count": 0, "candidates": []},
                        {"source": "openalex", "success": True, "candidate_count": 0, "candidates": []},
                        {"source": "semantic_scholar", "success": True, "candidate_count": 0, "candidates": []},
                    ],
                },
            ],
        }
        report = build_hallucination_risk_report(entries, external_report)

        self.assertEqual(report["status"], "HIGH_RISK")
        self.assertEqual(report["summary"]["high_risk_entries"], 1)

    def test_missing_external_report_produces_conservative_entries(self) -> None:
        from core.citation_integrity.hallucination_risk import build_hallucination_risk_report

        entries = [self._entry("noext2024", {"title": "Paper Without External Data", "year": "2024"})]
        report = build_hallucination_risk_report(entries, None)

        self.assertGreaterEqual(len(report["entries"]), 1)
        self.assertNotEqual(report["entries"][0]["risk_label"], "PASS")

    def test_write_hallucination_risk_report_json(self) -> None:
        from core.citation_integrity.hallucination_risk import build_hallucination_risk_report, write_hallucination_risk_report

        entries = [self._entry("w2024", {"title": "Paper", "year": "2024"})]
        report = build_hallucination_risk_report(entries, None)
        with workspace_tempdir("hrisk-report-") as tmp:
            output = tmp / "reports" / "hallucination-risk-report.json"
            write_hallucination_risk_report(report, output)
            payload = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(payload["module"], "citation_hallucination_risk")

    def test_all_unsupported_entries_yields_unsupported_status(self) -> None:
        from core.citation_integrity.hallucination_risk import build_hallucination_risk_report

        entries = [self._entry("cn1", {"title": "中文论文一", "year": "2024"})]
        report = build_hallucination_risk_report(entries, None)

        self.assertEqual(report["status"], "UNSUPPORTED")
        self.assertEqual(report["summary"]["unsupported_entries"], 1)


class HallucinationRiskCSVTest(unittest.TestCase):
    def _entry(self, key: str, fields: dict[str, str] | None = None) -> BibEntry:
        return BibEntry(
            key=key,
            entry_type="article",
            file="ref/refs.bib",
            line=1,
            fields=fields or {"title": "Test", "year": "2024"},
            body="",
        )

    def test_csv_has_correct_header_and_excludes_pass_entries(self) -> None:
        from core.citation_integrity.hallucination_risk import build_hallucination_risk_report, write_high_risk_csv

        entries = [
            self._entry("ok2024", {"title": "Real Paper", "year": "2024", "doi": "10.1000/real"}),
            self._entry("cn2024", {"title": "中文论文", "year": "2024"}),
        ]
        external_report = {
            "entries": [
                {
                    "citation_key": "ok2024",
                    "match_status": "MATCH",
                    "providers": [{"source": "crossref", "success": True, "candidate_count": 1, "candidates": [{"doi": "10.1000/real", "doi_exact_match": True, "title_similarity": 1.0}]}],
                },
                {"citation_key": "cn2024", "match_status": "NO_CANDIDATE", "providers": []},
            ],
        }
        report = build_hallucination_risk_report(entries, external_report)
        with workspace_tempdir("hrisk-csv-") as tmp:
            output = tmp / "reports" / "high-risk-references.csv"
            write_high_risk_csv(report, output)
            text = output.read_text(encoding="utf-8")

        reader = csv.DictReader(io.StringIO(text))
        rows = list(reader)
        keys = [row["citation_key"] for row in rows]

        self.assertIn("cn2024", keys)
        self.assertNotIn("ok2024", keys)
        self.assertEqual(reader.fieldnames, ["citation_key", "risk_label", "hallucination_risk_score", "title", "year", "doi", "evidence_summary", "recommended_action"])

    def test_csv_includes_review_high_risk_and_unsupported(self) -> None:
        from core.citation_integrity.hallucination_risk import build_hallucination_risk_report, write_high_risk_csv

        entries = [
            self._entry("rev2024", {"title": "Uncertain Paper", "year": "2024"}),
            self._entry("fake2024", {"title": "Totally Made Up Title", "year": "2024"}),
            self._entry("cn2024", {"title": "中文论文", "year": "2024"}),
        ]
        external_report = {
            "entries": [
                {
                    "citation_key": "rev2024",
                    "match_status": "REVIEW",
                    "providers": [{"source": "crossref", "success": True, "candidate_count": 1, "candidates": [{"title_similarity": 0.6}]}],
                },
                {
                    "citation_key": "fake2024",
                    "match_status": "NO_CANDIDATE",
                    "providers": [
                        {"source": "crossref", "success": True, "candidate_count": 0, "candidates": []},
                        {"source": "openalex", "success": True, "candidate_count": 0, "candidates": []},
                    ],
                },
                {"citation_key": "cn2024", "match_status": "NO_CANDIDATE", "providers": []},
            ],
        }
        report = build_hallucination_risk_report(entries, external_report)
        with workspace_tempdir("hrisk-csv-all-") as tmp:
            output = tmp / "reports" / "high-risk-references.csv"
            write_high_risk_csv(report, output)
            text = output.read_text(encoding="utf-8")

        reader = csv.DictReader(io.StringIO(text))
        rows = list(reader)
        labels = {row["citation_key"]: row["risk_label"] for row in rows}

        self.assertIn("rev2024", labels)
        self.assertIn("fake2024", labels)
        self.assertIn("cn2024", labels)
        self.assertEqual(labels["cn2024"], "UNSUPPORTED")

    def test_csv_handles_commas_in_titles(self) -> None:
        from core.citation_integrity.hallucination_risk import build_hallucination_risk_report, write_high_risk_csv

        entries = [self._entry("comma2024", {"title": "A, Title With, Commas", "year": "2024"})]
        report = build_hallucination_risk_report(entries, None)
        with workspace_tempdir("hrisk-csv-commas-") as tmp:
            output = tmp / "reports" / "high-risk-references.csv"
            write_high_risk_csv(report, output)
            text = output.read_text(encoding="utf-8")

        reader = csv.DictReader(io.StringIO(text))
        rows = list(reader)
        self.assertEqual(rows[0]["title"], "A, Title With, Commas")


if __name__ == "__main__":
    unittest.main()
