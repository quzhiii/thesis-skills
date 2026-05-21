from __future__ import annotations

import unittest
import json
from datetime import datetime

from core.citation_integrity import (
    ExternalProviderEvidence,
    ExternalVerificationEntry,
    ExternalVerificationSummary,
)
from core.citation_integrity.external_report import (
    build_external_verification_report,
    write_external_verification_report,
)
from core.citation_integrity.models import BibEntry
from tests.helpers import workspace_tempdir


class CitationExternalReportTest(unittest.TestCase):
    def test_external_models_serialize_alpha_evidence_entry_and_summary(self) -> None:
        provider = ExternalProviderEvidence(
            source="crossref",
            query_type="doi",
            query="10.1000/example",
            used_cache=True,
            success=True,
            candidate_count=1,
            top_candidate={"title": "Example Title", "doi": "10.1000/example"},
            match_score=1.0,
        )
        result = ExternalVerificationEntry(
            citation_key="smith2024",
            local_metadata={"title": "Example Title", "doi": "10.1000/example"},
            match_status="MATCH",
            providers=[provider],
            recommended_action="Accept external match as supporting evidence.",
        )
        summary = ExternalVerificationSummary(cache_hits=1)

        report_summary = summary.to_dict()
        result_payload = result.to_dict()

        self.assertEqual(provider.source, "crossref")
        self.assertEqual(result.match_status, "MATCH")
        self.assertEqual(report_summary["cache_hits"], 1)
        self.assertEqual(result_payload["providers"][0]["source"], "crossref")

    def test_builds_report_summary_status_and_serializable_payload(self) -> None:
        entry = BibEntry(
            key="smith2024",
            entry_type="article",
            file="ref/refs.bib",
            line=1,
            fields={"title": "Example Title", "doi": "10.1000/example", "year": "2024"},
            body="",
        )
        provider = ExternalProviderEvidence(
            source="crossref",
            query_type="doi",
            query="10.1000/example",
            used_cache=False,
            success=True,
            candidate_count=1,
            top_candidate={"title": "Example Title", "doi": "10.1000/example"},
            candidates=[
                {
                    "title": "Example Title",
                    "doi": "10.1000/example",
                    "doi_exact_match": True,
                    "title_similarity": 1.0,
                }
            ],
            match_score=1.0,
        )

        report = build_external_verification_report([entry], evidence_by_key={"smith2024": [provider]})

        self.assertEqual(report["module"], "citation_external_verification")
        self.assertEqual(report["version"], "2.0-alpha")
        self.assertIn("generated_at", report)
        self.assertIsNotNone(datetime.fromisoformat(str(report["generated_at"])))
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["summary"]["entries_considered"], 1)
        self.assertEqual(report["summary"]["doi_queries"], 1)
        self.assertEqual(report["summary"]["crossref_matches"], 1)
        self.assertEqual(report["summary"]["semantic_scholar_matches"], 0)
        self.assertEqual(report["entries"][0]["match_status"], "MATCH")
        json.dumps(report)

    def test_consensus_merges_same_doi_candidates_across_sources(self) -> None:
        entry = BibEntry(
            key="shared2024",
            entry_type="article",
            file="ref/refs.bib",
            line=1,
            fields={"title": "Shared Title", "doi": "10.1000/shared", "year": "2024"},
            body="",
        )
        crossref = ExternalProviderEvidence(
            source="crossref",
            query_type="doi",
            query="10.1000/shared",
            used_cache=False,
            success=True,
            candidate_count=1,
            top_candidate={"title": "Shared Title", "doi": "10.1000/shared"},
            candidates=[{"title": "Shared Title", "doi": "10.1000/shared", "title_similarity": 1.0, "doi_exact_match": True}],
            match_score=1.0,
        )
        openalex = ExternalProviderEvidence(
            source="openalex",
            query_type="doi",
            query="10.1000/shared",
            used_cache=False,
            success=True,
            candidate_count=1,
            top_candidate={"title": "Shared Title Revised", "doi": "10.1000/shared"},
            candidates=[{"title": "Shared Title Revised", "doi": "10.1000/shared", "title_similarity": 0.88, "doi_exact_match": True}],
            match_score=1.0,
        )

        report = build_external_verification_report(
            [entry],
            evidence_by_key={"shared2024": [crossref, openalex]},
        )

        consensus = report["entries"][0]["consensus"]
        self.assertEqual(report["entries"][0]["match_status"], "MATCH")
        self.assertEqual(consensus["candidate_count"], 1)
        self.assertEqual(consensus["top_candidate"]["doi"], "10.1000/shared")
        self.assertEqual(consensus["top_candidate"]["source_count"], 2)

    def test_consensus_marks_conflicting_title_candidates_for_review(self) -> None:
        entry = BibEntry(
            key="review2024",
            entry_type="article",
            file="ref/refs.bib",
            line=1,
            fields={"title": "Reference Checking in Practice", "year": "2024"},
            body="",
        )
        crossref = ExternalProviderEvidence(
            source="crossref",
            query_type="title",
            query="Reference Checking in Practice",
            used_cache=False,
            success=True,
            candidate_count=1,
            top_candidate={"title": "Reference Checking for Practice"},
            candidates=[{"title": "Reference Checking for Practice", "title_similarity": 0.78}],
            match_score=0.78,
        )
        semantic = ExternalProviderEvidence(
            source="semantic_scholar",
            query_type="title",
            query="Reference Checking in Practice",
            used_cache=False,
            success=True,
            candidate_count=1,
            top_candidate={"title": "A Different Research Topic"},
            candidates=[{"title": "A Different Research Topic", "title_similarity": 0.31}],
            match_score=0.31,
        )

        report = build_external_verification_report(
            [entry],
            evidence_by_key={"review2024": [crossref, semantic]},
        )

        self.assertEqual(report["entries"][0]["match_status"], "REVIEW")
        self.assertEqual(report["status"], "REVIEW")

    def test_report_detects_expanded_metadata_mismatches(self) -> None:
        entry = BibEntry(
            key="diff2024",
            entry_type="article",
            file="ref/refs.bib",
            line=1,
            fields={
                "title": "Main Title: Subtitle",
                "author": "Smith, Jane and Doe, John",
                "year": "2024",
                "journal": "Local Journal",
                "volume": "12",
                "number": "2",
                "pages": "10--20",
            },
            body="",
        )
        provider = ExternalProviderEvidence(
            source="crossref",
            query_type="title",
            query="Main Title: Subtitle",
            used_cache=False,
            success=True,
            candidate_count=1,
            candidates=[
                {
                    "title": "Main Title",
                    "title_similarity": 0.92,
                    "authors": ["Brown Alice"],
                    "year": "2023",
                    "venue": "Remote Journal",
                    "volume": "13",
                    "issue": "3",
                    "pages": "21--30",
                }
            ],
            match_score=0.92,
        )

        report = build_external_verification_report([entry], evidence_by_key={"diff2024": [provider]})

        top = report["entries"][0]["consensus"]["top_candidate"]
        mismatches = top["metadata_mismatches"]
        self.assertIn("subtitle_missing", mismatches)
        self.assertIn("author_count_mismatch", mismatches)
        self.assertIn("author_order_mismatch", mismatches)
        self.assertIn("year_mismatch", mismatches)
        self.assertIn("venue_mismatch", mismatches)
        self.assertIn("volume_issue_pages_mismatch", mismatches)
        self.assertEqual(report["entries"][0]["match_status"], "LIKELY_MATCH_WITH_METADATA_DIFF")

    def test_confirmed_match_status_requires_doi_title_and_year(self) -> None:
        entry = BibEntry(
            key="confirmed2024",
            entry_type="article",
            file="ref/refs.bib",
            line=1,
            fields={"title": "Confirmed Paper", "doi": "10.1000/ok", "year": "2024"},
            body="",
        )
        provider = ExternalProviderEvidence(
            source="crossref",
            query_type="doi",
            query="10.1000/ok",
            used_cache=False,
            success=True,
            candidate_count=1,
            candidates=[{"title": "Confirmed Paper", "doi": "10.1000/ok", "year": "2024", "doi_exact_match": True, "title_similarity": 1.0}],
            match_score=1.0,
        )

        report = build_external_verification_report([entry], evidence_by_key={"confirmed2024": [provider]})

        self.assertEqual(report["entries"][0]["match_status"], "CONFIRMED_MATCH")

    def test_provider_failure_yields_unavailable_report_without_throwing(self) -> None:
        entry = BibEntry(
            key="offline2024",
            entry_type="article",
            file="ref/refs.bib",
            line=1,
            fields={"title": "Offline Title", "doi": "10.1000/offline"},
            body="",
        )
        provider = ExternalProviderEvidence(
            source="openalex",
            query_type="doi",
            query="10.1000/offline",
            used_cache=False,
            success=False,
            candidate_count=0,
            match_score=0.0,
            error="offline",
        )

        report = build_external_verification_report([entry], evidence_by_key={"offline2024": [provider]})

        self.assertEqual(report["status"], "UNAVAILABLE")
        self.assertEqual(report["summary"]["network_failures"], 1)
        self.assertEqual(report["entries"][0]["match_status"], "UNAVAILABLE")

    def test_writes_external_verification_report_json(self) -> None:
        report = build_external_verification_report([], evidence_by_key={})
        with workspace_tempdir("external-report-") as tempdir:
            output = tempdir / "reports" / "external-verification-report.json"
            write_external_verification_report(report, output)
            payload = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(payload["module"], "citation_external_verification")


if __name__ == "__main__":
    unittest.main()
