from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from core.claim_citation_html import render_claim_citation_html, write_claim_citation_html
from tests.helpers import materialize_project, workspace_tempdir


ROOT = Path(__file__).resolve().parents[1]
CLI_SCRIPT = ROOT / "32-claim-citation-html" / "build_claim_citation_html.py"


class ClaimCitationHtmlTest(unittest.TestCase):
    def test_render_outputs_bilingual_sections(self) -> None:
        html = render_claim_citation_html(
            {
                "status": "WEAK",
                "summary": {
                    "claim_citation_pairs": 1,
                    "weak_pairs": 1,
                    "citation_needed_candidates": 1,
                    "unique_references_never_cited": 1,
                },
                "entries": [
                    {
                        "citation_key": "ref1",
                        "triage_label": "WEAK",
                        "support_review_label": "NEEDS_MANUAL_REVIEW",
                        "support_review_reason": "Conservative support-risk heuristic flagged this claim-citation pair for manual review.",
                        "claim_type": "empirical_result",
                        "file": "chapters/01-introduction.tex",
                        "line": 7,
                        "hallucination_risk_label": "REVIEW",
                        "cluster_keys": ["ref1", "ref2"],
                        "cluster_review_reason": "Review the grouped citations together.",
                        "risk_signals": ["possible_overclaim"],
                        "support_signals": ["complete_metadata"],
                        "next_actions": ["Verify whether the cited source supports the strength of the claim before final submission."],
                        "claim_context": "The method significantly improves accuracy.",
                    }
                ],
                "citation_needed_candidates": [
                    {
                        "file": "main.tex",
                        "line": 3,
                        "claim_type": "empirical_result",
                        "risk_signal": "uncited_empirical_result",
                        "sentence": "The method significantly improves accuracy.",
                    }
                ],
                "uncited_references": [
                    {
                        "citation_key": "unused2024",
                        "title": "Unused Reference",
                        "hallucination_risk_label": "HIGH_RISK",
                    }
                ],
            }
        )

        self.assertIn("声明-引用<br>支撑分级", html)
        self.assertIn("Claim-Citation<br>Triage", html)
        self.assertIn("Citation-Needed Candidates", html)
        self.assertIn("Citation-needed 候选句", html)
        self.assertIn("Browse by triage label", html)
        self.assertIn("按 triage_label 查看", html)
        self.assertIn("Related Reports", html)
        self.assertIn("相关报告", html)
        self.assertIn("claim-citation-triage-report.json", html)
        self.assertIn("final-audit-report.html", html)
        self.assertIn("reference-audit-ledger.html", html)
        self.assertIn("possible_overclaim", html)

    def test_write_and_cli_generate_html(self) -> None:
        with workspace_tempdir("claim-citation-html-") as base:
            project = materialize_project(
                base / "project",
                {
                    "reports/claim-citation-triage-report.json": json.dumps(
                        {
                            "status": "SUPPORTED",
                            "summary": {"claim_citation_pairs": 1, "citation_needed_candidates": 0, "unique_references_never_cited": 0},
                            "entries": [],
                            "citation_needed_candidates": [],
                            "uncited_references": [],
                        },
                        ensure_ascii=False,
                    )
                },
            )
            write_claim_citation_html(
                project / "reports" / "claim-citation-triage-report.json",
                project / "reports" / "custom-claim-citation-triage.html",
            )
            result = subprocess.run(
                [sys.executable, str(CLI_SCRIPT), "--project-root", str(project)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            default_output = project / "reports" / "claim-citation-triage.html"
            custom_output = project / "reports" / "custom-claim-citation-triage.html"
            default_exists = default_output.exists()
            custom_exists = custom_output.exists()
            html = default_output.read_text(encoding="utf-8")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(default_exists)
        self.assertTrue(custom_exists)
        self.assertIn("Claim-Citation<br>Triage", html)
        self.assertIn("声明-引用<br>支撑分级", html)


if __name__ == "__main__":
    unittest.main()
