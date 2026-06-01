from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from core.reference_audit_ledger_html import render_reference_audit_ledger_html, write_reference_audit_ledger_html
from tests.helpers import materialize_project, workspace_tempdir


ROOT = Path(__file__).resolve().parents[1]
CLI_SCRIPT = ROOT / "31-reference-ledger-html" / "build_reference_audit_ledger_html.py"


class ReferenceAuditLedgerHtmlTest(unittest.TestCase):
    def test_render_outputs_bilingual_sections(self) -> None:
        html = render_reference_audit_ledger_html(
            [
                {
                    "key": "ref1",
                    "title": "Reference One",
                    "authors": "Doe, Jane",
                    "year": "2024",
                    "venue": "J",
                    "doi": "",
                    "scope": "bibliography",
                    "source_checked": "local_bib",
                    "status": "present",
                    "issue": "",
                    "action_suggested": "Review only if flagged.",
                }
            ]
        )

        self.assertIn("引用<br>审计总表", html)
        self.assertIn("Reference<br>Audit Ledger", html)
        self.assertIn("按 scope 查看", html)
        self.assertIn("Browse by scope", html)
        self.assertIn("引用证据总表", html)
        self.assertIn("data-lang-btn=\"zh\"", html)

    def test_write_and_cli_generate_html(self) -> None:
        with workspace_tempdir("reference-ledger-html-") as base:
            project = materialize_project(
                base / "project",
                {
                    "reports/reference-audit-ledger.csv": "key,title,authors,year,venue,doi,scope,source_checked,status,issue,action_suggested\nref1,Reference One,Doe,2024,J,,bibliography,local_bib,present,,Review\n",
                },
            )
            write_reference_audit_ledger_html(
                project / "reports" / "reference-audit-ledger.csv",
                project / "reports" / "custom-reference-audit-ledger.html",
            )
            result = subprocess.run(
                [sys.executable, str(CLI_SCRIPT), "--project-root", str(project)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            default_output = project / "reports" / "reference-audit-ledger.html"
            custom_output = project / "reports" / "custom-reference-audit-ledger.html"
            default_exists = default_output.exists()
            custom_exists = custom_output.exists()
            html = default_output.read_text(encoding="utf-8")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(default_exists)
        self.assertTrue(custom_exists)
        self.assertIn("引用<br>审计总表", html)
        self.assertIn("Reference One", html)


if __name__ == "__main__":
    unittest.main()
