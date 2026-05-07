from __future__ import annotations

import unittest

from core.citation_integrity import (
    ExternalProviderEvidence,
    ExternalVerificationEntry,
    ExternalVerificationSummary,
)


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


if __name__ == "__main__":
    unittest.main()
