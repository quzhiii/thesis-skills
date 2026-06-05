from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from core.report_index import collect_report_index_items, render_report_index_html, write_report_index_html
from tests.helpers import materialize_project, workspace_tempdir


ROOT = Path(__file__).resolve().parents[1]
CLI_SCRIPT = ROOT / "29-report-index" / "build_report_index.py"


class ReportIndexTest(unittest.TestCase):
    def test_collects_present_missing_and_csv_rows(self) -> None:
        with workspace_tempdir("report-index-") as base:
            reports = materialize_project(
                base / "project" / "reports",
                {
                    "final-audit-report.json": json.dumps(
                        {"overall_verdict": "WARN", "summary": {"headline": "Final audit verdict: WARN"}},
                        ensure_ascii=False,
                    ),
                    "reference-audit-ledger.csv": "key,title,authors,year,venue,doi,scope,source_checked,status,issue,action_suggested\na,A,B,2024,J,,bibliography,local_bib,present,,Review\n",
                },
            )
            items = collect_report_index_items(reports)

        by_id = {item["id"]: item for item in items}
        self.assertEqual(by_id["final_audit"]["status"], "present")
        self.assertEqual(by_id["final_audit"]["summary"]["headline"], "Final audit verdict: WARN")
        self.assertEqual(by_id["reference_ledger"]["row_count"], 1)
        self.assertEqual(by_id["readiness"]["status"], "missing")
        self.assertEqual(by_id["final_audit"]["title_zh"], "终稿审计总报告")
        self.assertEqual(by_id["final_audit"]["detail_status"], "missing")

    def test_render_hides_missing_html_detail_links(self) -> None:
        html = render_report_index_html(
            [
                {
                    "id": "final_audit",
                    "title": "Final audit report",
                    "title_zh": "终稿审计总报告",
                    "path": "final-audit-report.json",
                    "role": "JSON source",
                    "role_zh": "JSON 源产物",
                    "description": "Aggregated report",
                    "description_zh": "聚合报告",
                    "status": "present",
                    "summary": {"headline": "Final audit verdict: PASS"},
                    "detail_path": "final-audit-report.html",
                    "detail_status": "missing",
                }
            ],
            project_label="demo-project",
        )

        self.assertIn("final-audit-report.json", html)
        self.assertNotIn("href=\"final-audit-report.html\"", html)
        self.assertIn("Generate HTML detail first", html)

    def test_render_distinguishes_html_detail_and_source_links(self) -> None:
        html = render_report_index_html(
            [
                {
                    "id": "final_audit",
                    "title": "Final audit report",
                    "title_zh": "终稿审计总报告",
                    "path": "final-audit-report.json",
                    "role": "JSON source",
                    "role_zh": "JSON 源产物",
                    "description": "Aggregated report",
                    "description_zh": "聚合报告",
                    "status": "present",
                    "summary": {"headline": "Final audit verdict: PASS"},
                    "detail_path": "final-audit-report.html",
                    "detail_status": "present",
                },
                {
                    "id": "reference_ledger",
                    "title": "Reference audit ledger",
                    "title_zh": "引用审计总表",
                    "path": "reference-audit-ledger.csv",
                    "role": "CSV source",
                    "role_zh": "CSV 源产物",
                    "description": "Spreadsheet handoff",
                    "description_zh": "表格交付",
                    "status": "present",
                    "summary": {},
                    "detail_path": "reference-audit-ledger.html",
                    "detail_status": "present",
                    "row_count": 10,
                },
            ],
            project_label="demo-project",
        )

        self.assertIn("Open HTML detail", html)
        self.assertIn("Open JSON source", html)
        self.assertIn("Open CSV source", html)
        self.assertIn("打开 HTML 详情", html)
        self.assertIn("打开 JSON 源产物", html)
        self.assertIn("打开 CSV 源产物", html)

    def test_renders_static_html_with_source_of_truth_notice(self) -> None:
        html = render_report_index_html(
            [
                {
                    "id": "final_audit",
                    "title": "Final audit report",
                    "title_zh": "终稿审计总报告",
                    "path": "final-audit-report.json",
                    "role": "JSON source",
                    "role_zh": "JSON 源产物",
                    "description": "Aggregated report",
                    "description_zh": "聚合报告",
                    "status": "present",
                    "summary": {"headline": "Final audit verdict: PASS"},
                    "detail_path": "final-audit-report.html",
                    "detail_status": "present",
                }
            ],
            project_label="demo-project",
        )

        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("本地<br>报告入口", html)
        self.assertIn("data-lang-btn=\"zh\"", html)
        self.assertIn("data-lang-btn=\"en\"", html)
        self.assertIn("JSON / CSV", html)
        self.assertIn("final-audit-report.json", html)
        self.assertIn("demo-project", html)
        self.assertIn("终稿审计总报告", html)
        self.assertIn("打开 HTML 详情", html)
        self.assertIn("打开 JSON 源产物", html)
        self.assertIn("final-audit-report.html", html)

    def test_cli_writes_reports_index_html(self) -> None:
        with workspace_tempdir("report-index-cli-") as base:
            project = materialize_project(
                base / "project",
                {
                    "reports/final-audit-report.json": json.dumps(
                        {"overall_verdict": "PASS", "summary": {"headline": "Final audit verdict: PASS"}},
                        ensure_ascii=False,
                    ),
                },
            )
            write_report_index_html(project / "reports", project / "reports" / "custom-index.html")
            result = subprocess.run(
                [sys.executable, str(CLI_SCRIPT), "--project-root", str(project)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            default_output = project / "reports" / "index.html"
            custom_output = project / "reports" / "custom-index.html"
            default_exists = default_output.exists()
            custom_exists = custom_output.exists()
            html = default_output.read_text(encoding="utf-8")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(default_exists)
        self.assertTrue(custom_exists)
        self.assertIn("Final audit verdict: PASS", html)
        self.assertIn("本地<br>报告入口", html)
        self.assertIn("已生成", html)
        self.assertIn("Generate HTML detail first", html)
        self.assertIn("Open JSON source", html)


if __name__ == "__main__":
    unittest.main()
