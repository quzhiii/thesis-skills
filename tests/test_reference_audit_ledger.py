from __future__ import annotations

import csv
import json
import subprocess
import sys
import unittest
from pathlib import Path

from core.project import ThesisProject
from core.reference_audit_ledger import build_reference_audit_ledger_rows, write_reference_audit_ledger_csv
from core.rules import load_rule_pack
from tests.helpers import materialize_project, workspace_tempdir
from tests.test_rules import PACK_ROOT


ROOT = Path(__file__).resolve().parents[1]
CLI_SCRIPT = ROOT / "28-reference-audit-ledger" / "build_reference_audit_ledger.py"


class ReferenceAuditLedgerTest(unittest.TestCase):
    def _project(self, base: Path) -> tuple[ThesisProject, object]:
        pack = load_rule_pack(PACK_ROOT / "university-generic")
        project = ThesisProject.discover(
            base,
            pack.rules["project"]["main_tex_candidates"],
            pack.rules["project"]["chapter_globs"],
            pack.rules["project"]["bibliography_files"],
        )
        return project, pack

    def test_builds_rows_from_bib_and_reference_evidence(self) -> None:
        with workspace_tempdir("reference-ledger-") as base:
            materialize_project(
                base,
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\cite{smith2024}\n\\end{document}\n",
                    "ref/refs.bib": "@article{smith2024, title={Local Title}, author={Smith, Jane}, year={2024}, journal={J}, doi={10.1000/local}}\n",
                    "reports/citation-integrity-report.json": json.dumps(
                        {
                            "issues": [
                                {
                                    "severity": "WARN",
                                    "message": "Bibliography entry needs review.",
                                    "suggested_action": "Check metadata.",
                                    "evidence": {"citation_key": "smith2024"},
                                }
                            ]
                        },
                        ensure_ascii=False,
                    ),
                    "reports/final-reference-set-report.json": json.dumps(
                        {"final_keys": ["smith2024"], "issues": []},
                        ensure_ascii=False,
                    ),
                    "reports/external-verification-report.json": json.dumps(
                        {
                            "entries": [
                                {
                                    "citation_key": "smith2024",
                                    "local_metadata": {"title": "Local Title", "year": "2024", "doi": "10.1000/local"},
                                    "match_status": "NO_CANDIDATE",
                                    "recommended_action": "Verify manually.",
                                }
                            ]
                        },
                        ensure_ascii=False,
                    ),
                    "reports/missing-doi-candidates.json": json.dumps(
                        {
                            "entries": [
                                {
                                    "citation_key": "missingdoi2024",
                                    "candidate_doi": "10.1000/candidate",
                                    "recommended_action": "Verify DOI manually.",
                                }
                            ]
                        },
                        ensure_ascii=False,
                    ),
                    "reports/url-verification-report.json": json.dumps(
                        {
                            "entries": [
                                {
                                    "citation_key": "smith2024",
                                    "url": "https://example.invalid/paper",
                                    "status": "URL_NOT_FOUND",
                                }
                            ]
                        },
                        ensure_ascii=False,
                    ),
                    "reports/hallucination-risk-report.json": json.dumps(
                        {
                            "entries": [
                                {
                                    "citation_key": "smith2024",
                                    "risk_label": "HIGH_RISK",
                                    "hallucination_risk_score": 0.9,
                                    "recommended_action": "Verify source manually.",
                                }
                            ]
                        },
                        ensure_ascii=False,
                    ),
                },
            )
            project, _pack = self._project(base)
            rows = build_reference_audit_ledger_rows(project)

        row_dicts = [row.to_dict() for row in rows]
        scopes = {row["scope"] for row in row_dicts}
        self.assertIn("bibliography", scopes)
        self.assertIn("local_citation_integrity", scopes)
        self.assertIn("final_reference_set", scopes)
        self.assertIn("external_metadata", scopes)
        self.assertIn("doi_candidate", scopes)
        self.assertIn("url_verification", scopes)
        self.assertIn("hallucination_risk", scopes)
        external = [row for row in row_dicts if row["scope"] == "external_metadata"][0]
        self.assertEqual(external["status"], "NO_CANDIDATE")
        self.assertNotIn("fake", external["issue"].lower())

    def test_writes_csv_with_expected_columns(self) -> None:
        with workspace_tempdir("reference-ledger-csv-") as base:
            materialize_project(
                base,
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\cite{a2024}\n\\end{document}\n",
                    "ref/refs.bib": "@article{a2024, title={A}, author={B}, year={2024}, journal={J}}\n",
                },
            )
            project, _pack = self._project(base)
            output = base / "reports" / "reference-audit-ledger.csv"
            write_reference_audit_ledger_csv(build_reference_audit_ledger_rows(project), output)
            with output.open("r", encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))

        self.assertEqual(rows[0]["key"], "a2024")
        self.assertEqual(rows[0]["scope"], "bibliography")
        self.assertEqual(
            list(rows[0].keys()),
            ["key", "title", "authors", "year", "venue", "doi", "scope", "source_checked", "status", "issue", "action_suggested"],
        )

    def test_cli_writes_default_ledger(self) -> None:
        with workspace_tempdir("reference-ledger-cli-") as base:
            project_root = materialize_project(
                base / "project",
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\cite{a2024}\n\\end{document}\n",
                    "ref/refs.bib": "@article{a2024, title={A}, author={B}, year={2024}, journal={J}}\n",
                },
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(CLI_SCRIPT),
                    "--project-root",
                    str(project_root),
                    "--ruleset",
                    "university-generic",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            output = project_root / "reports" / "reference-audit-ledger.csv"
            exists = output.exists()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(exists)


if __name__ == "__main__":
    unittest.main()
