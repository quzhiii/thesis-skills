from __future__ import annotations

import json
import importlib
import sys
import subprocess
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tests.helpers import materialize_project, readiness_pass_fixture_files, workspace_tempdir


readiness_gate = importlib.import_module("core.readiness_gate")
build_readiness_artifact = readiness_gate.build_readiness_artifact
collect_readiness_sources = readiness_gate.collect_readiness_sources
RUNNER = Path(__file__).resolve().parents[1] / "16-check-readiness" / "check_readiness.py"


class ReadinessGateTest(unittest.TestCase):
    def test_build_readiness_artifact_exposes_required_top_level_fields(self) -> None:
        artifact = build_readiness_artifact(mode="advisor-handoff")

        self.assertEqual(artifact["mode"], "advisor-handoff")
        self.assertIn("overall_verdict", artifact)
        self.assertIn("summary", artifact)
        self.assertIn("dimensions", artifact)
        self.assertIn("blockers", artifact)
        self.assertIn("warnings", artifact)
        self.assertIn("next_actions", artifact)
        self.assertIn("sources", artifact)

    def test_collect_readiness_sources_reads_known_artifacts_and_records_missing_ones(self) -> None:
        with workspace_tempdir("readiness-") as base:
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
                                "compile": {
                                    "status": "parsed",
                                    "report": "reports/check_compile-report.json",
                                },
                            },
                        },
                        ensure_ascii=False,
                    ),
                    "reports/fix-summary.json": json.dumps(
                        {
                            "ruleset": "university-generic",
                            "steps": {
                                "language": {
                                    "exit_code": 0,
                                    "summary": {"changed_files": 1, "applied": False},
                                }
                            },
                        },
                        ensure_ascii=False,
                    ),
                    "reports/check_references-report.json": json.dumps(
                        {
                            "summary": {"checker": "check_references", "errors": 0, "warnings": 1, "status": "PASS"},
                            "findings": [],
                        },
                        ensure_ascii=False,
                    ),
                    "reports/check_compile-report.json": json.dumps(
                        {
                            "summary": {"checker": "check_compile", "errors": 1, "warnings": 0, "status": "FAIL"},
                            "findings": [
                                {"severity": "error", "code": "COMPILE_UNDEFINED_CONTROL_SEQUENCE"}
                            ],
                        },
                        ensure_ascii=False,
                    ),
                    "reports/latex_to_word-report.json": json.dumps(
                        {
                            "profile": "review-friendly",
                            "warnings": ["custom-macro:foo"],
                            "unsupported_constructs": [],
                            "applied": False,
                        },
                        ensure_ascii=False,
                    ),
                    "reports/review-diff-artifact.json": json.dumps(
                        {
                            "artifact_type": "review_package",
                            "summary": {"revision_id": "review-1"},
                            "payload": {
                                "review_digest": {"total_items": 2, "high_priority_items": 1},
                                "review_queue": [
                                    {"priority": "high", "review_required": True, "category": "language"}
                                ],
                            },
                        },
                        ensure_ascii=False,
                    ),
                },
            )

            sources = collect_readiness_sources(project)

        self.assertEqual(sources["run_summary"]["status"], "present")
        self.assertEqual(sources["fix_summary"]["status"], "present")
        self.assertEqual(sources["checker_reports"]["status"], "present")
        self.assertEqual(sources["compile"]["status"], "present")
        self.assertEqual(sources["export"]["status"], "present")
        self.assertEqual(sources["review_loop"]["status"], "present")
        self.assertEqual(sources["checker_reports"]["count"], 2)

    def test_build_readiness_artifact_emits_dimensions_and_missing_evidence_explicitly(self) -> None:
        with workspace_tempdir("readiness-") as base:
            project = materialize_project(
                base / "project",
                {
                    "reports/run-summary.json": json.dumps(
                        {
                            "ruleset": "university-generic",
                            "steps": {
                                "references": {
                                    "exit_code": 1,
                                    "report": "reports/check_references-report.json",
                                },
                                "language": {
                                    "exit_code": 0,
                                    "report": "reports/check_language-report.json",
                                },
                                "format": {
                                    "exit_code": 1,
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
                            "summary": {"checker": "check_references", "errors": 2, "warnings": 0, "status": "FAIL"},
                            "findings": [
                                {"severity": "error", "code": "REF_MISSING_ENTRY"},
                                {"severity": "error", "code": "REF_ORPHANED_BIB"},
                            ],
                        },
                        ensure_ascii=False,
                    ),
                    "reports/check_language-report.json": json.dumps(
                        {
                            "summary": {"checker": "check_language", "errors": 0, "warnings": 1, "status": "PASS"},
                            "findings": [{"severity": "warning", "code": "LANG_STYLE"}],
                        },
                        ensure_ascii=False,
                    ),
                    "reports/check_format-report.json": json.dumps(
                        {
                            "summary": {"checker": "check_format", "errors": 1, "warnings": 1, "status": "FAIL"},
                            "findings": [{"severity": "error", "code": "FMT_BROKEN_REF"}],
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
                    "reports/latex_to_word-report.json": json.dumps(
                        {
                            "profile": "review-friendly",
                            "warnings": ["custom-macro:foo"],
                            "unsupported_constructs": ["tikzpicture"],
                            "applied": False,
                        },
                        ensure_ascii=False,
                    ),
                },
            )

            artifact = build_readiness_artifact(mode="advisor-handoff", project_root=Path(project))

        self.assertEqual(set(artifact["dimensions"]), {"references", "language", "format", "content", "compile", "export", "review_debt"})
        self.assertEqual(artifact["dimensions"]["references"]["verdict"], "BLOCK")
        self.assertEqual(artifact["dimensions"]["language"]["verdict"], "WARN")
        self.assertEqual(artifact["dimensions"]["format"]["verdict"], "BLOCK")
        self.assertEqual(artifact["dimensions"]["content"]["verdict"], "PASS")
        self.assertEqual(artifact["dimensions"]["compile"]["verdict"], "WARN")
        self.assertEqual(artifact["dimensions"]["compile"]["evidence_status"], "missing")
        self.assertEqual(artifact["dimensions"]["export"]["verdict"], "WARN")
        self.assertEqual(artifact["dimensions"]["review_debt"]["evidence_status"], "missing")
        self.assertIn("blockers", artifact)
        self.assertIn("warnings", artifact)
        self.assertIn("sources", artifact)

    def test_build_readiness_artifact_emits_overall_verdict_and_prioritized_guidance(self) -> None:
        with workspace_tempdir("readiness-") as base:
            project = materialize_project(
                base / "project",
                {
                    "reports/run-summary.json": json.dumps(
                        {
                            "ruleset": "university-generic",
                            "steps": {
                                "references": {
                                    "exit_code": 1,
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
                    "reports/fix-summary.json": json.dumps(
                        {
                            "ruleset": "university-generic",
                            "steps": {
                                "language": {
                                    "exit_code": 0,
                                    "summary": {"changed_files": 1, "applied": False},
                                }
                            },
                        },
                        ensure_ascii=False,
                    ),
                    "reports/check_references-report.json": json.dumps(
                        {
                            "summary": {"checker": "check_references", "errors": 1, "warnings": 0, "status": "FAIL"},
                            "findings": [{"severity": "error", "code": "REF_MISSING_ENTRY"}],
                        },
                        ensure_ascii=False,
                    ),
                    "reports/check_language-report.json": json.dumps(
                        {
                            "summary": {"checker": "check_language", "errors": 0, "warnings": 1, "status": "PASS"},
                            "findings": [{"severity": "warning", "code": "LANG_STYLE"}],
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
                    "reports/latex_to_word-report.json": json.dumps(
                        {
                            "profile": "review-friendly",
                            "warnings": ["custom-macro:foo"],
                            "unsupported_constructs": [],
                            "applied": False,
                        },
                        ensure_ascii=False,
                    ),
                    "reports/review-diff-artifact.json": json.dumps(
                        {
                            "artifact_type": "review_package",
                            "summary": {"revision_id": "review-2"},
                            "payload": {
                                "review_digest": {"total_items": 3, "high_priority_items": 2},
                                "review_queue": [
                                    {"priority": "high", "review_required": True, "category": "language"},
                                    {"priority": "medium", "review_required": True, "category": "argument"},
                                ],
                            },
                        },
                        ensure_ascii=False,
                    ),
                },
            )

            artifact = build_readiness_artifact(mode="advisor-handoff", project_root=Path(project))

        self.assertEqual(artifact["overall_verdict"], "BLOCK")
        self.assertGreaterEqual(len(artifact["blockers"]), 1)
        self.assertGreaterEqual(len(artifact["warnings"]), 1)
        self.assertGreaterEqual(len(artifact["next_actions"]), 2)
        self.assertEqual(artifact["blockers"][0]["dimension"], "references")
        self.assertIn("verdict", artifact["blockers"][0])
        self.assertIn("evidence_status", artifact["blockers"][0])
        self.assertIn("verdict", artifact["warnings"][0])
        self.assertIn("evidence_status", artifact["warnings"][0])
        self.assertIn("headline", artifact["summary"])
        self.assertEqual(artifact["summary"]["evidence_status"], "complete")

    def test_ingest_only_review_debt_surfaces_bounded_explanation_detail(self) -> None:
        with workspace_tempdir("readiness-") as base:
            files = readiness_pass_fixture_files()
            files["reports/review-ingest-artifact.json"] = json.dumps(
                {
                    "artifact_type": "feedback_ingest",
                    "summary": {"normalized_count": 4, "ambiguous_count": 2},
                    "payload": {
                        "normalized_items": [
                            {"source_ref": "blocked-1"},
                            {"source_ref": "blocked-2"},
                            {"source_ref": "todo-1"},
                            {"source_ref": "candidate-1"},
                        ],
                        "selective_action": {
                            "todos": [
                                {"source_ref": "todo-1", "category": "argument", "review_required": True}
                            ],
                            "blocked": [
                                {
                                    "source_ref": "blocked-1",
                                    "category": "review",
                                    "review_required": True,
                                    "reason": "ambiguous",
                                },
                                {
                                    "source_ref": "blocked-2",
                                    "category": "review",
                                    "review_required": True,
                                    "reason": "blocked",
                                },
                            ],
                            "candidate_patches": [
                                {"source_ref": "candidate-1", "category": "language"}
                            ],
                            "summary": {
                                "todo_count": 1,
                                "blocked_count": 2,
                                "candidate_patch_count": 1,
                            },
                        },
                    },
                },
                ensure_ascii=False,
            )
            project = materialize_project(base / "project", files)

            artifact = build_readiness_artifact(mode="advisor-handoff", project_root=Path(project))

        review_debt = artifact["dimensions"]["review_debt"]
        self.assertEqual(review_debt["verdict"], "WARN")
        self.assertEqual(review_debt["total_items"], 3)
        self.assertEqual(review_debt["blocked_count"], 2)
        self.assertEqual(review_debt["todo_count"], 1)
        self.assertEqual(review_debt["candidate_patch_count"], 1)
        self.assertIn("blocked", review_debt["reason"])
        self.assertIn("todo", review_debt["reason"])
        self.assertLessEqual(len(review_debt["source_refs"]), 3)
        self.assertCountEqual(review_debt["source_refs"], ["blocked-1", "blocked-2", "todo-1"])

    def test_candidate_patches_do_not_block_readiness_by_themselves(self) -> None:
        with workspace_tempdir("readiness-") as base:
            files = readiness_pass_fixture_files()
            files["reports/review-ingest-artifact.json"] = json.dumps(
                {
                    "artifact_type": "feedback_ingest",
                    "summary": {"normalized_count": 2, "ambiguous_count": 0},
                    "payload": {
                        "normalized_items": [
                            {"source_ref": "candidate-1"},
                            {"source_ref": "candidate-2"},
                        ],
                        "selective_action": {
                            "todos": [],
                            "blocked": [],
                            "candidate_patches": [
                                {"source_ref": "candidate-1", "category": "language"},
                                {"source_ref": "candidate-2", "category": "language"},
                            ],
                            "summary": {
                                "todo_count": 0,
                                "blocked_count": 0,
                                "candidate_patch_count": 2,
                            },
                        },
                    },
                },
                ensure_ascii=False,
            )
            project = materialize_project(base / "project", files)

            artifact = build_readiness_artifact(mode="submission-prep", project_root=Path(project))

        review_debt = artifact["dimensions"]["review_debt"]
        self.assertEqual(review_debt["verdict"], "PASS")
        self.assertEqual(review_debt["candidate_patch_count"], 2)
        self.assertEqual(review_debt["todo_count"], 0)
        self.assertEqual(review_debt["blocked_count"], 0)
        self.assertEqual(artifact["overall_verdict"], "PASS")

    def test_review_diff_digest_remains_primary_when_ingest_also_exists(self) -> None:
        with workspace_tempdir("readiness-") as base:
            files = readiness_pass_fixture_files()
            files["reports/review-diff-artifact.json"] = json.dumps(
                {
                    "artifact_type": "review_package",
                    "summary": {"revision_id": "review-primary-1"},
                    "payload": {
                        "review_digest": {"total_items": 1, "high_priority_items": 1},
                        "review_queue": [
                            {"priority": "high", "review_required": True, "category": "argument"}
                        ],
                    },
                },
                ensure_ascii=False,
            )
            files["reports/review-ingest-artifact.json"] = json.dumps(
                {
                    "artifact_type": "feedback_ingest",
                    "summary": {"normalized_count": 3, "ambiguous_count": 1},
                    "payload": {
                        "normalized_items": [
                            {"source_ref": "blocked-1"},
                            {"source_ref": "todo-1"},
                            {"source_ref": "candidate-1"},
                        ],
                        "selective_action": {
                            "todos": [
                                {"source_ref": "todo-1", "category": "argument", "review_required": True}
                            ],
                            "blocked": [
                                {
                                    "source_ref": "blocked-1",
                                    "category": "review",
                                    "review_required": True,
                                    "reason": "ambiguous",
                                }
                            ],
                            "candidate_patches": [
                                {"source_ref": "candidate-1", "category": "language"}
                            ],
                            "summary": {
                                "todo_count": 1,
                                "blocked_count": 1,
                                "candidate_patch_count": 1,
                            },
                        },
                    },
                },
                ensure_ascii=False,
            )
            project = materialize_project(base / "project", files)

            artifact = build_readiness_artifact(mode="advisor-handoff", project_root=Path(project))

        review_debt = artifact["dimensions"]["review_debt"]
        self.assertEqual(review_debt["verdict"], "WARN")
        self.assertEqual(review_debt["total_items"], 1)
        self.assertEqual(review_debt["high_priority_items"], 1)
        self.assertEqual(review_debt["todo_count"], 1)
        self.assertEqual(review_debt["blocked_count"], 1)
        self.assertEqual(review_debt["candidate_patch_count"], 1)

    def test_readiness_cli_writes_report_for_selected_mode(self) -> None:
        with workspace_tempdir("readiness-cli-") as base:
            project = materialize_project(
                base / "project",
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\nHello\n\\end{document}\n",
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
                        {"summary": {"checker": "check_references", "errors": 0, "warnings": 0, "status": "PASS"}, "findings": []},
                        ensure_ascii=False,
                    ),
                    "reports/check_language-report.json": json.dumps(
                        {"summary": {"checker": "check_language", "errors": 0, "warnings": 0, "status": "PASS"}, "findings": []},
                        ensure_ascii=False,
                    ),
                    "reports/check_format-report.json": json.dumps(
                        {"summary": {"checker": "check_format", "errors": 0, "warnings": 0, "status": "PASS"}, "findings": []},
                        ensure_ascii=False,
                    ),
                    "reports/check_content-report.json": json.dumps(
                        {"summary": {"checker": "check_content", "errors": 0, "warnings": 0, "status": "PASS"}, "findings": []},
                        ensure_ascii=False,
                    ),
                    "reports/check_compile-report.json": json.dumps(
                        {"summary": {"checker": "check_compile", "errors": 0, "warnings": 0, "status": "PASS"}, "findings": []},
                        ensure_ascii=False,
                    ),
                },
            )
            report = project / "reports" / "readiness-report.json"

            result = subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    "--project-root",
                    str(project),
                    "--ruleset",
                    "university-generic",
                    "--mode",
                    "submission-prep",
                    "--report",
                    str(report),
                ],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(report.exists())
            payload = json.loads(report.read_text(encoding="utf-8"))

        self.assertEqual(payload["mode"], "submission-prep")
        self.assertIn("overall_verdict", payload)
        self.assertIn("dimensions", payload)


if __name__ == "__main__":
    unittest.main()
