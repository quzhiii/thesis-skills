from __future__ import annotations

import importlib
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tests.helpers import materialize_project, workspace_tempdir


readiness_gate = importlib.import_module("core.readiness_gate")
build_readiness_artifact = readiness_gate.build_readiness_artifact


class ReadinessModesTest(unittest.TestCase):
    def test_build_readiness_artifact_accepts_known_modes_and_rejects_unknown_ones(self) -> None:
        advisor = build_readiness_artifact(mode="advisor-handoff")
        submission = build_readiness_artifact(mode="submission-prep")

        self.assertEqual(advisor["mode"], "advisor-handoff")
        self.assertEqual(submission["mode"], "submission-prep")

        with self.assertRaises(ValueError):
            build_readiness_artifact(mode="final-defense")

    def test_mode_policy_differs_for_missing_compile_evidence(self) -> None:
        with workspace_tempdir("readiness-mode-") as base:
            project = materialize_project(
                base / "project",
                {
                    "reports/run-summary.json": json.dumps(
                        {
                            "ruleset": "university-generic",
                            "steps": {
                                "references": {
                                    "exit_code": 0,
                                    "report": "reports/check_references-report.json",
                                },
                                "language": {
                                    "exit_code": 0,
                                    "report": "reports/check_language-report.json",
                                },
                                "format": {
                                    "exit_code": 0,
                                    "report": "reports/check_format-report.json",
                                },
                                "content": {
                                    "exit_code": 0,
                                    "report": "reports/check_content-report.json",
                                },
                                "compile": {
                                    "status": "missing-log",
                                    "reason": "No compile log discovered for the main TeX file",
                                },
                            },
                        },
                        ensure_ascii=False,
                    ),
                    "reports/check_references-report.json": json.dumps(
                        {
                            "summary": {"checker": "check_references", "errors": 0, "warnings": 0, "status": "PASS"},
                            "findings": [],
                        },
                        ensure_ascii=False,
                    ),
                    "reports/check_language-report.json": json.dumps(
                        {
                            "summary": {"checker": "check_language", "errors": 0, "warnings": 0, "status": "PASS"},
                            "findings": [],
                        },
                        ensure_ascii=False,
                    ),
                    "reports/check_format-report.json": json.dumps(
                        {
                            "summary": {"checker": "check_format", "errors": 0, "warnings": 0, "status": "PASS"},
                            "findings": [],
                        },
                        ensure_ascii=False,
                    ),
                    "reports/check_content-report.json": json.dumps(
                        {
                            "summary": {"checker": "check_content", "errors": 0, "warnings": 0, "status": "PASS"},
                            "findings": [],
                        },
                        ensure_ascii=False,
                    ),
                },
            )

            advisor = build_readiness_artifact(
                mode="advisor-handoff", project_root=Path(project)
            )
            submission = build_readiness_artifact(
                mode="submission-prep", project_root=Path(project)
            )

        self.assertEqual(advisor["dimensions"]["compile"]["verdict"], "WARN")
        self.assertEqual(submission["dimensions"]["compile"]["verdict"], "BLOCK")
        self.assertEqual(advisor["overall_verdict"], "WARN")
        self.assertEqual(submission["overall_verdict"], "BLOCK")

    def test_mode_policy_differs_for_review_debt(self) -> None:
        with workspace_tempdir("readiness-mode-") as base:
            project = materialize_project(
                base / "project",
                {
                    "reports/run-summary.json": json.dumps(
                        {
                            "ruleset": "university-generic",
                            "steps": {
                                "references": {
                                    "exit_code": 0,
                                    "report": "reports/check_references-report.json",
                                },
                                "language": {
                                    "exit_code": 0,
                                    "report": "reports/check_language-report.json",
                                },
                                "format": {
                                    "exit_code": 0,
                                    "report": "reports/check_format-report.json",
                                },
                                "content": {
                                    "exit_code": 0,
                                    "report": "reports/check_content-report.json",
                                },
                                "compile": {
                                    "status": "parsed",
                                    "report": "reports/check_compile-report.json",
                                },
                            },
                        },
                        ensure_ascii=False,
                    ),
                    "reports/check_references-report.json": json.dumps(
                        {
                            "summary": {"checker": "check_references", "errors": 0, "warnings": 0, "status": "PASS"},
                            "findings": [],
                        },
                        ensure_ascii=False,
                    ),
                    "reports/check_language-report.json": json.dumps(
                        {
                            "summary": {"checker": "check_language", "errors": 0, "warnings": 0, "status": "PASS"},
                            "findings": [],
                        },
                        ensure_ascii=False,
                    ),
                    "reports/check_format-report.json": json.dumps(
                        {
                            "summary": {"checker": "check_format", "errors": 0, "warnings": 0, "status": "PASS"},
                            "findings": [],
                        },
                        ensure_ascii=False,
                    ),
                    "reports/check_content-report.json": json.dumps(
                        {
                            "summary": {"checker": "check_content", "errors": 0, "warnings": 0, "status": "PASS"},
                            "findings": [],
                        },
                        ensure_ascii=False,
                    ),
                    "reports/check_compile-report.json": json.dumps(
                        {
                            "summary": {"checker": "check_compile", "errors": 0, "warnings": 0, "status": "PASS"},
                            "findings": [],
                        },
                        ensure_ascii=False,
                    ),
                    "reports/review-diff-artifact.json": json.dumps(
                        {
                            "artifact_type": "review_package",
                            "summary": {"revision_id": "review-mode-1"},
                            "payload": {
                                "review_digest": {"total_items": 1, "high_priority_items": 1},
                                "review_queue": [
                                    {"priority": "high", "review_required": True, "category": "argument"}
                                ],
                            },
                        },
                        ensure_ascii=False,
                    ),
                },
            )

            advisor = build_readiness_artifact(
                mode="advisor-handoff", project_root=Path(project)
            )
            submission = build_readiness_artifact(
                mode="submission-prep", project_root=Path(project)
            )

        self.assertEqual(advisor["dimensions"]["review_debt"]["verdict"], "WARN")
        self.assertEqual(submission["dimensions"]["review_debt"]["verdict"], "BLOCK")


if __name__ == "__main__":
    unittest.main()
