from __future__ import annotations

import json
import unittest
from pathlib import Path

from core.readiness_gate import build_readiness_artifact
from tests.helpers import materialize_project, readiness_pass_fixture_files, workspace_tempdir


class CitationIntegrityReadinessTest(unittest.TestCase):
    def test_readiness_prefers_citation_integrity_report_over_compatibility_report(self) -> None:
        with workspace_tempdir("citation-readiness-") as base:
            files = readiness_pass_fixture_files()
            files["reports/check_references-report.json"] = json.dumps(
                {
                    "summary": {"checker": "check_references", "errors": 0, "warnings": 0, "status": "PASS"},
                    "findings": [],
                },
                ensure_ascii=False,
            )
            files["reports/citation-integrity-report.json"] = json.dumps(
                {
                    "module": "citation_integrity",
                    "version": "1.1",
                    "status": "BLOCK",
                    "summary": {"missing_cited_keys": 1},
                    "issues": [
                        {
                            "code": "CI-MISSING-KEY",
                            "severity": "BLOCK",
                            "category": "missing_cited_key",
                            "message": "missing",
                            "file": "main.tex",
                            "line": 3,
                            "evidence": {},
                            "suggested_action": "fix",
                        }
                    ],
                },
                ensure_ascii=False,
            )
            project = materialize_project(base / "project", files)

            artifact = build_readiness_artifact(mode="advisor-handoff", project_root=Path(project))

        self.assertEqual(artifact["dimensions"]["references"]["verdict"], "BLOCK")
        self.assertEqual(artifact["dimensions"]["references"]["source"], "citation-integrity-report.json")

    def test_readiness_falls_back_to_old_reference_report_when_rich_report_missing(self) -> None:
        with workspace_tempdir("citation-readiness-") as base:
            files = readiness_pass_fixture_files()
            files["reports/check_references-report.json"] = json.dumps(
                {
                    "summary": {"checker": "check_references", "errors": 0, "warnings": 1, "status": "PASS"},
                    "findings": [{"severity": "warning", "code": "REF_ORPHAN_BIB"}],
                },
                ensure_ascii=False,
            )
            project = materialize_project(base / "project", files)

            artifact = build_readiness_artifact(mode="advisor-handoff", project_root=Path(project))

        self.assertEqual(artifact["dimensions"]["references"]["verdict"], "WARN")
        self.assertNotIn("source", artifact["dimensions"]["references"])

    def test_readiness_includes_external_verification_as_advisory_dimension(self) -> None:
        with workspace_tempdir("citation-readiness-") as base:
            files = readiness_pass_fixture_files()
            files["reports/citation-integrity-report.json"] = json.dumps(
                {
                    "module": "citation_integrity",
                    "version": "1.2",
                    "status": "PASS",
                    "summary": {},
                    "issues": [],
                },
                ensure_ascii=False,
            )
            files["reports/external-verification-report.json"] = json.dumps(
                {
                    "module": "citation_external_verification",
                    "version": "2.0-stable",
                    "status": "REVIEW",
                    "summary": {
                        "entries_considered": 3,
                        "matched_entries": 1,
                        "review_entries": 2,
                        "network_failures": 0,
                    },
                    "entries": [],
                },
                ensure_ascii=False,
            )
            project = materialize_project(base / "project", files)

            artifact = build_readiness_artifact(mode="advisor-handoff", project_root=Path(project))

        self.assertEqual(artifact["dimensions"]["references"]["verdict"], "PASS")
        self.assertEqual(artifact["dimensions"]["external_verification"]["verdict"], "WARN")
        self.assertEqual(
            artifact["dimensions"]["external_verification"]["source"],
            "external-verification-report.json",
        )
        self.assertEqual(artifact["dimensions"]["external_verification"]["review_entries"], 2)

    def test_readiness_treats_unavailable_external_verification_as_advisory_warn(self) -> None:
        with workspace_tempdir("citation-readiness-") as base:
            files = readiness_pass_fixture_files()
            files["reports/external-verification-report.json"] = json.dumps(
                {
                    "module": "citation_external_verification",
                    "version": "2.0-stable",
                    "status": "UNAVAILABLE",
                    "summary": {
                        "entries_considered": 1,
                        "matched_entries": 0,
                        "review_entries": 0,
                        "network_failures": 2,
                    },
                    "entries": [],
                },
                ensure_ascii=False,
            )
            project = materialize_project(base / "project", files)

            artifact = build_readiness_artifact(mode="submission-prep", project_root=Path(project))

        self.assertEqual(artifact["dimensions"]["external_verification"]["verdict"], "WARN")
        self.assertEqual(artifact["dimensions"]["external_verification"]["network_failures"], 2)
        self.assertEqual(artifact["overall_verdict"], "WARN")


if __name__ == "__main__":
    unittest.main()
