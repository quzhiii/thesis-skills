from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from core.final_audit import build_final_audit_report, write_final_audit_report
from tests.helpers import materialize_project, workspace_tempdir


ROOT = Path(__file__).resolve().parents[1]
CLI_SCRIPT = ROOT / "27-final-audit-report" / "build_final_audit_report.py"


def _checker_report(checker: str, *, status: str = "PASS", errors: int = 0, warnings: int = 0) -> str:
    return json.dumps(
        {
            "summary": {
                "checker": checker,
                "ruleset": "university-generic",
                "errors": errors,
                "warnings": warnings,
                "infos": 0,
                "status": status,
            },
            "findings": [],
        },
        ensure_ascii=False,
    )


class FinalAuditReportTest(unittest.TestCase):
    def test_aggregates_foundation_reports_and_optional_evidence(self) -> None:
        with workspace_tempdir("final-audit-aggregate-") as base:
            project = materialize_project(
                base / "project",
                {
                    "reports/final-cleanup-report.json": _checker_report("check_final_cleanup"),
                    "reports/statistical-consistency-report.json": _checker_report("check_statistical_consistency", status="FAIL", warnings=1),
                    "reports/manual-anchor-report.json": _checker_report("check_manual_anchor"),
                    "reports/citation-integrity-report.json": json.dumps(
                        {"status": "BLOCK", "summary": {}, "issues": [{"severity": "BLOCK"}]},
                        ensure_ascii=False,
                    ),
                    "reports/hallucination-risk-report.json": json.dumps(
                        {"status": "HIGH_RISK", "summary": {"high_risk_entries": 1}},
                        ensure_ascii=False,
                    ),
                },
            )
            report = build_final_audit_report(project, "university-generic")

        self.assertEqual(report["module"], "final_audit_report")
        self.assertEqual(report["overall_verdict"], "BLOCK")
        self.assertEqual(report["dimensions"]["final_cleanup"]["verdict"], "PASS")
        self.assertEqual(report["dimensions"]["statistical_consistency"]["verdict"], "WARN")
        self.assertEqual(report["dimensions"]["citation_integrity"]["verdict"], "BLOCK")
        self.assertEqual(report["dimensions"]["hallucination_risk"]["verdict"], "WARN")
        self.assertTrue(report["blockers"])
        self.assertTrue(report["warnings"])
        self.assertIn("future_html", report)

    def test_missing_required_foundation_inputs_warn_but_do_not_block(self) -> None:
        with workspace_tempdir("final-audit-missing-") as base:
            project = materialize_project(
                base / "project",
                {
                    "reports/final-cleanup-report.json": _checker_report("check_final_cleanup"),
                },
            )
            report = build_final_audit_report(project, "university-generic")

        self.assertEqual(report["overall_verdict"], "WARN")
        self.assertEqual(report["summary"]["missing_required_evidence_count"], 2)
        self.assertEqual(report["dimensions"]["statistical_consistency"]["evidence_status"], "missing")
        self.assertEqual(report["dimensions"]["manual_anchor"]["evidence_status"], "missing")

    def test_write_and_cli_generate_report(self) -> None:
        with workspace_tempdir("final-audit-cli-") as base:
            project = materialize_project(
                base / "project",
                {
                    "reports/final-cleanup-report.json": _checker_report("check_final_cleanup"),
                    "reports/statistical-consistency-report.json": _checker_report("check_statistical_consistency"),
                    "reports/manual-anchor-report.json": _checker_report("check_manual_anchor"),
                },
            )
            report = build_final_audit_report(project, "university-generic")
            write_final_audit_report(report, project / "reports" / "custom-final-audit.json")
            result = subprocess.run(
                [
                    sys.executable,
                    str(CLI_SCRIPT),
                    "--project-root",
                    str(project),
                    "--ruleset",
                    "university-generic",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            default_report = project / "reports" / "final-audit-report.json"
            custom_exists = (project / "reports" / "custom-final-audit.json").exists()
            data = json.loads(default_report.read_text(encoding="utf-8"))

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(custom_exists)
        self.assertEqual(data["overall_verdict"], "WARN")
        self.assertEqual(data["summary"]["missing_required_evidence_count"], 0)
        self.assertIn("readiness", data["dimensions"])


if __name__ == "__main__":
    unittest.main()
