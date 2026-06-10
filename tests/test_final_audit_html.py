from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from core.final_audit_html import render_final_audit_html, write_final_audit_html
from tests.helpers import materialize_project, workspace_tempdir


ROOT = Path(__file__).resolve().parents[1]
CLI_SCRIPT = ROOT / "30-final-audit-html" / "build_final_audit_html.py"


class FinalAuditHtmlTest(unittest.TestCase):
    def test_render_outputs_swiss_inspired_sections(self) -> None:
        html = render_final_audit_html(
            {
                "overall_verdict": "WARN",
                "summary": {
                    "headline": "Final audit verdict: WARN",
                    "dimension_count": 3,
                    "blocker_count": 0,
                    "warning_count": 2,
                    "missing_required_evidence_count": 0,
                    "source_of_truth": "JSON remains authoritative.",
                },
                "dimensions": {
                    "final_cleanup": {
                        "title": "Final cleanup",
                        "verdict": "PASS",
                        "evidence_status": "present",
                        "reason": "checker reported no findings",
                        "source": "final-cleanup-report.json",
                        "summary": {"checker": "check_final_cleanup"},
                    },
                    "readiness": {
                        "title": "Readiness gate",
                        "verdict": "WARN",
                        "evidence_status": "missing",
                        "reason": "optional evidence missing",
                        "source": "readiness-report.json",
                    },
                },
                "blockers": [],
                "warnings": [
                    {
                        "dimension": "readiness",
                        "title": "Readiness gate",
                        "verdict": "WARN",
                        "evidence_status": "missing",
                        "reason": "optional evidence missing",
                        "source": "readiness-report.json",
                    }
                ],
                "next_actions": ["Generate or repair evidence for readiness."],
                "sources": [
                    {
                        "id": "final_cleanup",
                        "title": "Final cleanup",
                        "path": "final-cleanup-report.json",
                        "status": "present",
                        "required": True,
                    }
                ],
            }
        )

        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("终稿<br>审计", html)
        self.assertIn("data-lang-btn=\"zh\"", html)
        self.assertIn("data-lang-btn=\"en\"", html)
        self.assertIn("Dimension Matrix", html)
        self.assertIn("维度矩阵", html)
        self.assertIn("Blocking Issues", html)
        self.assertIn("阻断问题", html)
        self.assertIn("Warnings", html)
        self.assertIn("警告问题", html)
        self.assertIn("Source Artifacts", html)
        self.assertIn("源产物", html)
        self.assertIn("Related Reports", html)
        self.assertIn("相关报告", html)
        self.assertIn("readiness-report.json", html)
        self.assertIn("final-cleanup-report.json", html)
        self.assertIn('id="warning-issues-zh"', html)
        self.assertIn('id="warning-issues-en"', html)
        self.assertIn("reference-audit-ledger.html#evidence-rows-zh", html)
        self.assertIn("reference-audit-ledger.html#evidence-rows-en", html)
        self.assertIn("claim-citation-triage.html#zh-review-groups", html)
        self.assertIn("claim-citation-triage.html#en-review-groups", html)
        self.assertIn("终稿清理检查", html)
        self.assertIn("缺少可选证据", html)

    def test_write_and_cli_generate_html(self) -> None:
        with workspace_tempdir("final-audit-html-") as base:
            project = materialize_project(
                base / "project",
                {
                    "reports/final-audit-report.json": json.dumps(
                        {
                            "overall_verdict": "PASS",
                            "summary": {
                                "headline": "Final audit verdict: PASS",
                                "dimension_count": 3,
                                "blocker_count": 0,
                                "warning_count": 0,
                                "missing_required_evidence_count": 0,
                                "source_of_truth": "JSON reports remain authoritative.",
                            },
                            "dimensions": {},
                            "blockers": [],
                            "warnings": [],
                            "next_actions": [],
                            "sources": [],
                        },
                        ensure_ascii=False,
                    )
                },
            )
            write_final_audit_html(
                project / "reports" / "final-audit-report.json",
                project / "reports" / "custom-final-audit-report.html",
            )
            result = subprocess.run(
                [sys.executable, str(CLI_SCRIPT), "--project-root", str(project)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            default_output = project / "reports" / "final-audit-report.html"
            custom_output = project / "reports" / "custom-final-audit-report.html"
            default_exists = default_output.exists()
            custom_exists = custom_output.exists()
            html = default_output.read_text(encoding="utf-8")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(default_exists)
        self.assertTrue(custom_exists)
        self.assertIn("Final audit verdict: PASS", html)
        self.assertIn("终稿<br>审计", html)
        self.assertIn("总体结论", html)


if __name__ == "__main__":
    unittest.main()
