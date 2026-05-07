from __future__ import annotations

import unittest
import json

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
            match_score=1.0,
        )

        report = build_external_verification_report([entry], evidence_by_key={"smith2024": [provider]})

        self.assertEqual(report["module"], "citation_external_verification")
        self.assertEqual(report["version"], "2.0-alpha")
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["summary"]["entries_considered"], 1)
        self.assertEqual(report["summary"]["doi_queries"], 1)
        self.assertEqual(report["summary"]["crossref_matches"], 1)
        self.assertEqual(report["entries"][0]["match_status"], "MATCH")
        json.dumps(report)

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
