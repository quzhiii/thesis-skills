from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from core.reference_audit_ledger_html import render_reference_audit_ledger_html, write_reference_audit_ledger_html
from tests.helpers import materialize_project, workspace_tempdir


ROOT = Path(__file__).resolve().parents[1]
CLI_SCRIPT = ROOT / "31-reference-ledger-html" / "build_reference_audit_ledger_html.py"


def _section(html: str, section_id: str) -> str:
    marker = f'id="{section_id}"'
    start = html.index(marker)
    section_start = html.rfind("<section", 0, start)
    return html[section_start : html.index("</section>", start)]


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
                    "is_final_reference": "true",
                    "is_cited_in_tex": "true",
                    "is_unused_bib_entry": "false",
                }
            ]
        )

        self.assertIn("引用<br>审计总表", html)
        self.assertIn("Reference<br>Audit Ledger", html)
        self.assertIn("按 scope 查看", html)
        self.assertIn("Browse by scope", html)
        self.assertIn("引用证据总表", html)
        self.assertIn("相关报告", html)
        self.assertIn("Related Reports", html)
        self.assertIn("readiness-report.json", html)
        self.assertIn("final-audit-report.html", html)
        self.assertIn("claim-citation-triage.html", html)
        self.assertIn("data-lang-btn=\"zh\"", html)

    def test_render_separates_final_references_from_unused_bibliography(self) -> None:
        rows = [
            {
                "key": "actual2024",
                "title": "Actual Reference",
                "authors": "A",
                "year": "2024",
                "venue": "J",
                "doi": "",
                "scope": "bibliography",
                "source_checked": "local_bib",
                "status": "present",
                "issue": "",
                "action_suggested": "Review only if flagged.",
                "is_final_reference": "true",
                "is_cited_in_tex": "true",
                "is_unused_bib_entry": "false",
            },
            {
                "key": "actual2024",
                "title": "Actual Reference",
                "authors": "A",
                "year": "2024",
                "venue": "J",
                "doi": "",
                "scope": "final_reference_set",
                "source_checked": "final-reference-set-report.json",
                "status": "included_final",
                "issue": "Reference appears in final compiled/reference-set scope.",
                "action_suggested": "Use this row as final-scope reference evidence.",
                "is_final_reference": "true",
                "is_cited_in_tex": "true",
                "is_unused_bib_entry": "false",
            },
            {
                "key": "zhukezhen1973",
                "title": "Template Reference",
                "authors": "Zhu",
                "year": "1973",
                "venue": "",
                "doi": "",
                "scope": "bibliography",
                "source_checked": "local_bib",
                "status": "present; unused_bib_entry; not_in_final_reference_set",
                "issue": "Present in .bib files but not in the final reference set; not cited in discovered TeX files.",
                "action_suggested": "Remove unused bibliography entries or cite them if they are required.",
                "is_final_reference": "false",
                "is_cited_in_tex": "false",
                "is_unused_bib_entry": "true",
            },
            {
                "key": "zhukezhen1973",
                "title": "Template Reference",
                "authors": "Zhu",
                "year": "1973",
                "venue": "",
                "doi": "",
                "scope": "hallucination_risk",
                "source_checked": "hallucination-risk-report.json",
                "status": "REVIEW",
                "issue": "Hallucination risk label: REVIEW; score: 0.6",
                "action_suggested": "Review hallucination risk evidence manually.",
                "is_final_reference": "false",
                "is_cited_in_tex": "false",
                "is_unused_bib_entry": "true",
            },
        ]

        html = render_reference_audit_ledger_html(rows)
        final_section = _section(html, "final-references-zh")
        unused_section = _section(html, "unused-bibliography-zh")
        all_bib_section = _section(html, "all-bibliography-zh")
        evidence_section = _section(html, "evidence-rows-zh")

        self.assertIn("Final references only", html)
        self.assertIn("All bibliography entries", html)
        self.assertIn("Unused bibliography entries", html)
        self.assertIn("Evidence rows", html)
        self.assertIn("<strong>1</strong><span>Final references</span>", html)
        self.assertIn("<strong>2</strong><span>All bibliography entries</span>", html)
        self.assertIn("actual2024", final_section)
        self.assertNotIn("zhukezhen1973", final_section)
        self.assertIn("zhukezhen1973", unused_section)
        self.assertIn("zhukezhen1973", all_bib_section)
        self.assertIn("zhukezhen1973", evidence_section)

    def test_render_keeps_hallucination_only_rows_out_of_final_table(self) -> None:
        rows = [
            {
                "key": "riskonly2024",
                "title": "Risk Only",
                "authors": "A",
                "year": "2024",
                "venue": "",
                "doi": "",
                "scope": "hallucination_risk",
                "source_checked": "hallucination-risk-report.json",
                "status": "REVIEW",
                "issue": "Hallucination risk label: REVIEW; score: 0.6",
                "action_suggested": "Review hallucination risk evidence manually.",
                "is_final_reference": "true",
                "is_cited_in_tex": "true",
                "is_unused_bib_entry": "false",
            }
        ]

        html = render_reference_audit_ledger_html(rows)
        final_section = _section(html, "final-references-zh")
        evidence_section = _section(html, "evidence-rows-zh")

        self.assertNotIn("riskonly2024", final_section)
        self.assertIn("riskonly2024", evidence_section)

    def test_render_keeps_cited_not_final_rows_out_of_unused_section(self) -> None:
        rows = [
            {
                "key": "cited2024",
                "title": "Cited But Missing Final",
                "authors": "A",
                "year": "2024",
                "venue": "J",
                "doi": "",
                "scope": "bibliography",
                "source_checked": "local_bib",
                "status": "present; not_in_final_reference_set",
                "issue": "Present in .bib files but not in the final reference set.",
                "action_suggested": "Check why this cited key did not enter the final reference set before removing it.",
                "is_final_reference": "false",
                "is_cited_in_tex": "true",
                "is_unused_bib_entry": "false",
            },
            {
                "key": "cited2024",
                "title": "Cited But Missing Final",
                "authors": "A",
                "year": "2024",
                "venue": "J",
                "doi": "",
                "scope": "final_reference_set",
                "source_checked": "final-reference-set-report.json",
                "status": "warn",
                "issue": "Citation key 'cited2024' appears in .aux but not in .bbl.",
                "action_suggested": "Review final reference set issue before submission.",
                "is_final_reference": "false",
                "is_cited_in_tex": "true",
                "is_unused_bib_entry": "false",
            },
        ]

        html = render_reference_audit_ledger_html(rows)
        unused_section = _section(html, "unused-bibliography-zh")
        all_bib_section = _section(html, "all-bibliography-zh")
        evidence_section = _section(html, "evidence-rows-zh")

        self.assertNotIn("cited2024", unused_section)
        self.assertIn("cited2024", all_bib_section)
        self.assertIn("cited2024", evidence_section)

    def test_write_and_cli_generate_html(self) -> None:
        with workspace_tempdir("reference-ledger-html-") as base:
            project = materialize_project(
                base / "project",
                {
                    "reports/reference-audit-ledger.csv": "key,title,authors,year,venue,doi,scope,source_checked,status,issue,action_suggested,is_final_reference,is_cited_in_tex,is_unused_bib_entry\nref1,Reference One,Doe,2024,J,,bibliography,local_bib,present,,Review,true,true,false\n",
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
