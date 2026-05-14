from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from tests.helpers import materialize_project, workspace_tempdir

ROOT = Path(__file__).resolve().parents[1]
CLI_SCRIPT = ROOT / "18-verify-references" / "verify_external_references.py"


class CitationExternalCLITest(unittest.TestCase):
    def test_cli_accepts_project_root_and_writes_report(self) -> None:
        with workspace_tempdir("external-cli-") as base:
            project = materialize_project(
                base / "project",
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\cite{smith2024}\n\\end{document}\n",
                    "ref/refs.bib": "@article{smith2024, title={Example Title}, author={Smith, Jane}, year={2024}, journal={J}, doi={10.1000/example}}\n",
                },
            )
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
            report_path = project / "reports" / "external-verification-report.json"
            report_exists = report_path.exists()
            doi_report_exists = (project / "reports" / "missing-doi-candidates.json").exists()
            url_report_exists = (project / "reports" / "url-verification-report.json").exists()

            if report_exists:
                report = json.loads(report_path.read_text(encoding="utf-8"))
            else:
                report = {}

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(report_exists)
        self.assertTrue(doi_report_exists)
        self.assertTrue(url_report_exists)
        self.assertEqual(report["module"], "citation_external_verification")
        self.assertEqual(report["version"], "2.0-alpha")
        self.assertIn(report["status"], ("PASS", "WARN", "REVIEW", "UNAVAILABLE"))
        self.assertEqual(report["summary"]["entries_considered"], 1)

    def test_cli_returns_success_even_when_provider_unavailable(self) -> None:
        with workspace_tempdir("external-cli-offline-") as base:
            project = materialize_project(
                base / "project",
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\cite{offline2024}\n\\end{document}\n",
                    "ref/refs.bib": "@article{offline2024, title={Offline}, author={A}, year={2024}, journal={J}}\n",
                },
            )
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
            report_path = project / "reports" / "external-verification-report.json"
            report = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(report["status"], ("UNAVAILABLE", "WARN", "NO_CANDIDATE", "PASS", "REVIEW"))

    def test_check_references_with_external_flag_writes_both_reports(self) -> None:
        check_script = ROOT / "10-check-references" / "check_references.py"
        with workspace_tempdir("bridge-cli-") as base:
            project = materialize_project(
                base / "project",
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\cite{bridge2024}\n\\end{document}\n",
                    "ref/refs.bib": "@article{bridge2024, title={Bridge}, author={A}, year={2024}, journal={J}, doi={10.1000/bridge}}\n",
                },
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(check_script),
                    "--project-root",
                    str(project),
                    "--ruleset",
                    "university-generic",
                    "--with-external-verification",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            local_report = project / "reports" / "citation-integrity-report.json"
            external_report = project / "reports" / "external-verification-report.json"
            doi_report = project / "reports" / "missing-doi-candidates.json"
            url_report = project / "reports" / "url-verification-report.json"
            local_exists = local_report.exists()
            external_exists = external_report.exists()
            doi_exists = doi_report.exists()
            url_exists = url_report.exists()
            if external_exists:
                ext = json.loads(external_report.read_text(encoding="utf-8"))
            else:
                ext = {}

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(local_exists)
        self.assertTrue(external_exists)
        self.assertTrue(doi_exists)
        self.assertTrue(url_exists)
        self.assertEqual(ext["module"], "citation_external_verification")

    def test_check_references_without_flag_does_not_write_external_report(self) -> None:
        check_script = ROOT / "10-check-references" / "check_references.py"
        with workspace_tempdir("no-bridge-cli-") as base:
            project = materialize_project(
                base / "project",
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\cite{clean2024}\n\\end{document}\n",
                    "ref/refs.bib": "@article{clean2024, title={Clean}, author={A}, year={2024}, journal={J}, doi={10.1000/clean}}\n",
                },
            )
            subprocess.run(
                [
                    sys.executable,
                    str(check_script),
                    "--project-root",
                    str(project),
                    "--ruleset",
                    "university-generic",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            external_report = project / "reports" / "external-verification-report.json"

        self.assertFalse(external_report.exists())

    def test_cli_scope_final_reads_final_reference_set_report(self) -> None:
        with workspace_tempdir("external-cli-final-scope-") as base:
            project = materialize_project(
                base / "project",
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\cite{used2024,unused2024}\n\\end{document}\n",
                    "ref/refs.bib": "@article{used2024, title={Used}, author={A}, year={2024}}\n@article{unused2024, title={Unused}, author={B}, year={2024}}\n",
                    "reports/final-reference-set-report.json": json.dumps(
                        {"final_keys": ["used2024"]},
                        ensure_ascii=False,
                    ),
                },
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(CLI_SCRIPT),
                    "--project-root",
                    str(project),
                    "--ruleset",
                    "university-generic",
                    "--scope",
                    "final",
                    "--limit",
                    "0",
                    "--quiet",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            report = json.loads((project / "reports" / "external-verification-report.json").read_text(encoding="utf-8"))

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(report["summary"]["entries_considered"], 1)
        self.assertEqual(report["entries"][0]["citation_key"], "used2024")

    def test_cli_scope_cited_uses_tex_citations_and_only_key_filter(self) -> None:
        with workspace_tempdir("external-cli-cited-scope-") as base:
            project = materialize_project(
                base / "project",
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\cite{used2024,also2024}\n\\end{document}\n",
                    "ref/refs.bib": "@article{used2024, title={Used}, author={A}, year={2024}}\n@article{also2024, title={Also}, author={B}, year={2024}}\n@article{unused2024, title={Unused}, author={C}, year={2024}}\n",
                },
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(CLI_SCRIPT),
                    "--project-root",
                    str(project),
                    "--ruleset",
                    "university-generic",
                    "--scope",
                    "cited",
                    "--only-key",
                    "also2024",
                    "--limit",
                    "0",
                    "--quiet",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            report = json.loads((project / "reports" / "external-verification-report.json").read_text(encoding="utf-8"))

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(report["summary"]["entries_considered"], 1)
        self.assertEqual(report["entries"][0]["citation_key"], "also2024")

    def test_cli_resume_preserves_existing_entries_and_skips_verified_keys(self) -> None:
        with workspace_tempdir("external-cli-resume-") as base:
            project = materialize_project(
                base / "project",
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\cite{done2024}\n\\end{document}\n",
                    "ref/refs.bib": "@article{done2024, title={Done}, author={A}, year={2024}}\n",
                    "reports/external-verification-report.json": json.dumps(
                        {
                            "module": "citation_external_verification",
                            "version": "2.0-alpha",
                            "status": "PASS",
                            "summary": {"entries_considered": 1},
                            "entries": [
                                {
                                    "citation_key": "done2024",
                                    "local_metadata": {"title": "Done"},
                                    "match_status": "MATCH",
                                    "providers": [],
                                    "consensus": {},
                                    "recommended_action": "Already verified.",
                                }
                            ],
                        },
                        ensure_ascii=False,
                    ),
                },
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(CLI_SCRIPT),
                    "--project-root",
                    str(project),
                    "--ruleset",
                    "university-generic",
                    "--scope",
                    "cited",
                    "--resume",
                    "--quiet",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            report = json.loads((project / "reports" / "external-verification-report.json").read_text(encoding="utf-8"))

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(report["summary"]["entries_considered"], 1)
        self.assertEqual(report["entries"][0]["citation_key"], "done2024")
        self.assertEqual(report["entries"][0]["recommended_action"], "Already verified.")


if __name__ == "__main__":
    unittest.main()
