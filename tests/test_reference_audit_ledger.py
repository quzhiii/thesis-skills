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
            [
                "key",
                "title",
                "authors",
                "year",
                "venue",
                "doi",
                "scope",
                "source_checked",
                "status",
                "issue",
                "action_suggested",
                "is_final_reference",
                "is_cited_in_tex",
                "is_unused_bib_entry",
            ],
        )

    def test_marks_template_bib_entries_outside_final_reference_set(self) -> None:
        with workspace_tempdir("reference-ledger-unused-template-") as base:
            materialize_project(
                base,
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\cite{actual2024}\n\\end{document}\n",
                    "ref/refs.bib": "@book{zhukezhen1973, title={Template Reference}, author={Zhu}, year={1973}}\n",
                    "ref/refs-import.bib": "@article{actual2024, title={Actual Reference}, author={A}, year={2024}, journal={J}}\n",
                    "reports/final-reference-set-report.json": json.dumps(
                        {
                            "final_keys": ["actual2024"],
                            "issues": [
                                {
                                    "code": "FRS-UNUSED-BIB",
                                    "key": "zhukezhen1973",
                                    "severity": "info",
                                    "message": "Citation key 'zhukezhen1973' is present in .bib files but not in the final reference set.",
                                }
                            ],
                        },
                        ensure_ascii=False,
                    ),
                    "reports/citation-integrity-report.json": json.dumps(
                        {
                            "issues": [
                                {
                                    "severity": "WARN",
                                    "category": "unused_bib_entry",
                                    "message": "Bibliography entry `zhukezhen1973` is not cited in discovered TeX files.",
                                    "evidence": {"citation_key": "zhukezhen1973"},
                                    "suggested_action": "Remove unused bibliography entries or cite them if they are required.",
                                }
                            ]
                        },
                        ensure_ascii=False,
                    ),
                    "reports/hallucination-risk-report.json": json.dumps(
                        {
                            "entries": [
                                {"citation_key": "actual2024", "risk_label": "LOW_RISK", "hallucination_risk_score": 0.1},
                                {"citation_key": "zhukezhen1973", "risk_label": "REVIEW", "hallucination_risk_score": 0.6},
                            ]
                        },
                        ensure_ascii=False,
                    ),
                },
            )
            project, _pack = self._project(base)
            output = base / "reports" / "reference-audit-ledger.csv"
            write_reference_audit_ledger_csv(build_reference_audit_ledger_rows(project), output)
            with output.open("r", encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))

        actual_rows = [row for row in rows if row["key"] == "actual2024"]
        template_rows = [row for row in rows if row["key"] == "zhukezhen1973"]
        template_bib = [row for row in template_rows if row["scope"] == "bibliography"][0]

        self.assertTrue(actual_rows)
        self.assertTrue(template_rows)
        self.assertTrue(any(row["scope"] == "hallucination_risk" for row in template_rows))
        self.assertTrue(all(row["is_final_reference"] == "true" for row in actual_rows))
        self.assertTrue(all(row["is_cited_in_tex"] == "true" for row in actual_rows))
        self.assertEqual(template_bib["is_final_reference"], "false")
        self.assertEqual(template_bib["is_cited_in_tex"], "false")
        self.assertEqual(template_bib["is_unused_bib_entry"], "true")
        self.assertIn("unused_bib_entry", template_bib["status"])
        self.assertIn("not_in_final_reference_set", template_bib["status"])
        self.assertIn("Remove unused bibliography entries", template_bib["action_suggested"])

    def test_cited_bib_entry_missing_from_final_set_is_not_unused(self) -> None:
        with workspace_tempdir("reference-ledger-cited-not-final-") as base:
            materialize_project(
                base,
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\cite{cited2024}\n\\end{document}\n",
                    "ref/refs.bib": "@article{cited2024, title={Cited But Missing Final}, author={A}, year={2024}, journal={J}}\n",
                    "reports/final-reference-set-report.json": json.dumps(
                        {
                            "final_keys": [],
                            "issues": [
                                {
                                    "code": "FRS-AUX-NO-BBL",
                                    "key": "cited2024",
                                    "severity": "warn",
                                    "message": "Citation key 'cited2024' appears in .aux but not in .bbl.",
                                }
                            ],
                        },
                        ensure_ascii=False,
                    ),
                },
            )
            project, _pack = self._project(base)
            output = base / "reports" / "reference-audit-ledger.csv"
            write_reference_audit_ledger_csv(build_reference_audit_ledger_rows(project), output)
            with output.open("r", encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))

        bib_row = [row for row in rows if row["key"] == "cited2024" and row["scope"] == "bibliography"][0]

        self.assertEqual(bib_row["is_final_reference"], "false")
        self.assertEqual(bib_row["is_cited_in_tex"], "true")
        self.assertEqual(bib_row["is_unused_bib_entry"], "false")
        self.assertIn("not_in_final_reference_set", bib_row["status"])
        self.assertNotIn("unused_bib_entry", bib_row["status"])
        self.assertIn("Check why this cited key did not enter the final reference set", bib_row["action_suggested"])

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
