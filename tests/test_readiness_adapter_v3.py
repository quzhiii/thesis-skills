from __future__ import annotations

import json
import unittest

from tests.helpers import materialize_project, workspace_tempdir


class HallucinationRiskDimensionTest(unittest.TestCase):
    def test_high_risk_status_maps_to_warn(self) -> None:
        with workspace_tempdir("hrdim-high-") as base:
            project = materialize_project(
                base / "project",
                {
                    "reports/hallucination-risk-report.json": json.dumps({
                        "module": "citation_hallucination_risk",
                        "status": "HIGH_RISK",
                        "summary": {
                            "pass_entries": 0,
                            "warn_entries": 0,
                            "review_entries": 1,
                            "high_risk_entries": 1,
                            "unsupported_entries": 0,
                        },
                    }),
                },
            )
            from core.citation_integrity.readiness_adapter import hallucination_risk_dimension
            result = hallucination_risk_dimension(str(project))

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result["verdict"], "WARN")
        self.assertEqual(result["evidence_status"], "present")
        self.assertIn("high-risk", str(result["reason"]).lower())
        self.assertEqual(result["source"], "hallucination-risk-report.json")
        self.assertEqual(result["high_risk_entries"], 1)

    def test_pass_status_maps_to_pass(self) -> None:
        with workspace_tempdir("hrdim-pass-") as base:
            project = materialize_project(
                base / "project",
                {
                    "reports/hallucination-risk-report.json": json.dumps({
                        "module": "citation_hallucination_risk",
                        "status": "PASS",
                        "summary": {
                            "pass_entries": 5,
                            "warn_entries": 0,
                            "review_entries": 0,
                            "high_risk_entries": 0,
                            "unsupported_entries": 0,
                        },
                    }),
                },
            )
            from core.citation_integrity.readiness_adapter import hallucination_risk_dimension
            result = hallucination_risk_dimension(str(project))

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result["verdict"], "PASS")
        self.assertEqual(result["pass_entries"], 5)

    def test_unsupported_status_maps_to_pass(self) -> None:
        with workspace_tempdir("hrdim-unsup-") as base:
            project = materialize_project(
                base / "project",
                {
                    "reports/hallucination-risk-report.json": json.dumps({
                        "module": "citation_hallucination_risk",
                        "status": "UNSUPPORTED",
                        "summary": {
                            "pass_entries": 0,
                            "warn_entries": 0,
                            "review_entries": 0,
                            "high_risk_entries": 0,
                            "unsupported_entries": 3,
                        },
                    }),
                },
            )
            from core.citation_integrity.readiness_adapter import hallucination_risk_dimension
            result = hallucination_risk_dimension(str(project))

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result["verdict"], "PASS")
        self.assertEqual(result["unsupported_entries"], 3)

    def test_review_status_maps_to_warn(self) -> None:
        with workspace_tempdir("hrdim-review-") as base:
            project = materialize_project(
                base / "project",
                {
                    "reports/hallucination-risk-report.json": json.dumps({
                        "module": "citation_hallucination_risk",
                        "status": "REVIEW",
                        "summary": {
                            "pass_entries": 1,
                            "warn_entries": 2,
                            "review_entries": 1,
                            "high_risk_entries": 0,
                            "unsupported_entries": 0,
                        },
                    }),
                },
            )
            from core.citation_integrity.readiness_adapter import hallucination_risk_dimension
            result = hallucination_risk_dimension(str(project))

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result["verdict"], "WARN")
        self.assertEqual(result["review_entries"], 1)

    def test_warn_status_maps_to_warn(self) -> None:
        with workspace_tempdir("hrdim-warn-") as base:
            project = materialize_project(
                base / "project",
                {
                    "reports/hallucination-risk-report.json": json.dumps({
                        "module": "citation_hallucination_risk",
                        "status": "WARN",
                        "summary": {
                            "pass_entries": 3,
                            "warn_entries": 2,
                            "review_entries": 0,
                            "high_risk_entries": 0,
                            "unsupported_entries": 0,
                        },
                    }),
                },
            )
            from core.citation_integrity.readiness_adapter import hallucination_risk_dimension
            result = hallucination_risk_dimension(str(project))

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result["verdict"], "WARN")

    def test_report_missing_returns_none(self) -> None:
        with workspace_tempdir("hrdim-none-") as base:
            project = materialize_project(base / "project", {})
            from core.citation_integrity.readiness_adapter import hallucination_risk_dimension
            result = hallucination_risk_dimension(str(project))

        self.assertIsNone(result)

    def test_unparseable_json_returns_warn(self) -> None:
        with workspace_tempdir("hrdim-bad-") as base:
            project = materialize_project(
                base / "project",
                {"reports/hallucination-risk-report.json": "not valid json"},
            )
            from core.citation_integrity.readiness_adapter import hallucination_risk_dimension
            result = hallucination_risk_dimension(str(project))

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result["verdict"], "WARN")
        self.assertEqual(result["evidence_status"], "present")
        self.assertIn("unreadable", str(result["reason"]).lower())


class ClaimCitationDimensionTest(unittest.TestCase):
    def test_orphaned_status_maps_to_block(self) -> None:
        with workspace_tempdir("ccdim-orphan-") as base:
            project = materialize_project(
                base / "project",
                {
                    "reports/claim-citation-triage-report.json": json.dumps({
                        "module": "claim_citation_triage",
                        "status": "ORPHANED",
                        "summary": {
                            "claim_citation_pairs": 3,
                            "orphaned_pairs": 2,
                            "weak_pairs": 0,
                            "unverifiable_pairs": 0,
                        },
                    }),
                },
            )
            from core.citation_integrity.readiness_adapter import claim_citation_dimension
            result = claim_citation_dimension(str(project))

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result["verdict"], "BLOCK")
        self.assertEqual(result["evidence_status"], "present")
        self.assertEqual(result["source"], "claim-citation-triage-report.json")
        self.assertEqual(result["orphaned_pairs"], 2)

    def test_well_supported_status_maps_to_pass(self) -> None:
        with workspace_tempdir("ccdim-well-") as base:
            project = materialize_project(
                base / "project",
                {
                    "reports/claim-citation-triage-report.json": json.dumps({
                        "module": "claim_citation_triage",
                        "status": "WELL_SUPPORTED",
                        "summary": {
                            "claim_citation_pairs": 5,
                            "orphaned_pairs": 0,
                            "weak_pairs": 0,
                            "unverifiable_pairs": 0,
                        },
                    }),
                },
            )
            from core.citation_integrity.readiness_adapter import claim_citation_dimension
            result = claim_citation_dimension(str(project))

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result["verdict"], "PASS")

    def test_supported_status_maps_to_pass(self) -> None:
        with workspace_tempdir("ccdim-sup-") as base:
            project = materialize_project(
                base / "project",
                {
                    "reports/claim-citation-triage-report.json": json.dumps({
                        "module": "claim_citation_triage",
                        "status": "SUPPORTED",
                        "summary": {
                            "claim_citation_pairs": 4,
                            "orphaned_pairs": 0,
                            "weak_pairs": 0,
                            "unverifiable_pairs": 0,
                        },
                    }),
                },
            )
            from core.citation_integrity.readiness_adapter import claim_citation_dimension
            result = claim_citation_dimension(str(project))

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result["verdict"], "PASS")

    def test_weak_status_maps_to_warn(self) -> None:
        with workspace_tempdir("ccdim-weak-") as base:
            project = materialize_project(
                base / "project",
                {
                    "reports/claim-citation-triage-report.json": json.dumps({
                        "module": "claim_citation_triage",
                        "status": "WEAK",
                        "summary": {
                            "claim_citation_pairs": 4,
                            "orphaned_pairs": 0,
                            "weak_pairs": 2,
                            "unverifiable_pairs": 0,
                        },
                    }),
                },
            )
            from core.citation_integrity.readiness_adapter import claim_citation_dimension
            result = claim_citation_dimension(str(project))

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result["verdict"], "WARN")
        self.assertEqual(result["weak_pairs"], 2)

    def test_unverifiable_status_maps_to_warn(self) -> None:
        with workspace_tempdir("ccdim-unv-") as base:
            project = materialize_project(
                base / "project",
                {
                    "reports/claim-citation-triage-report.json": json.dumps({
                        "module": "claim_citation_triage",
                        "status": "UNVERIFIABLE",
                        "summary": {
                            "claim_citation_pairs": 3,
                            "orphaned_pairs": 0,
                            "weak_pairs": 0,
                            "unverifiable_pairs": 3,
                        },
                    }),
                },
            )
            from core.citation_integrity.readiness_adapter import claim_citation_dimension
            result = claim_citation_dimension(str(project))

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result["verdict"], "WARN")
        self.assertEqual(result["unverifiable_pairs"], 3)

    def test_report_missing_returns_none(self) -> None:
        with workspace_tempdir("ccdim-none-") as base:
            project = materialize_project(base / "project", {})
            from core.citation_integrity.readiness_adapter import claim_citation_dimension
            result = claim_citation_dimension(str(project))

        self.assertIsNone(result)

    def test_unparseable_json_returns_warn(self) -> None:
        with workspace_tempdir("ccdim-bad-") as base:
            project = materialize_project(
                base / "project",
                {"reports/claim-citation-triage-report.json": "garbage"},
            )
            from core.citation_integrity.readiness_adapter import claim_citation_dimension
            result = claim_citation_dimension(str(project))

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result["verdict"], "WARN")
        self.assertIn("unreadable", str(result["reason"]).lower())


if __name__ == "__main__":
    unittest.main()