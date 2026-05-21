from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from tests.helpers import materialize_project, workspace_tempdir

ROOT = Path(__file__).resolve().parents[1]
CLI_SCRIPT = ROOT / "20-check-claim-citation" / "check_claim_citation.py"


class ClaimCitationCLITest(unittest.TestCase):
    def test_cli_writes_reports_and_returns_0_when_no_orphans(self) -> None:
        with workspace_tempdir("cc-cli-ok-") as base:
            project = materialize_project(
                base / "project",
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\nA well-supported claim \\cite{smith2024}.\n\\end{document}\n",
                    "ref/refs.bib": "@article{smith2024, title={Example Title}, author={Smith, Jane}, year={2024}, journal={J}, doi={10.1000/example}}\n",
                    "reports/hallucination-risk-report.json": json.dumps({
                        "module": "citation_hallucination_risk",
                        "entries": [
                            {
                                "citation_key": "smith2024",
                                "risk_label": "PASS",
                                "hallucination_risk_score": 0.0,
                            }
                        ],
                    }),
                },
            )
            result = subprocess.run(
                [sys.executable, str(CLI_SCRIPT), "--project-root", str(project), "--ruleset", "university-generic"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            json_report = project / "reports" / "claim-citation-triage-report.json"
            md_report = project / "reports" / "claim-citation-triage.md"
            csv_report = project / "reports" / "claim-citation-triage.csv"
            json_exists = json_report.exists()
            md_exists = md_report.exists()
            csv_exists = csv_report.exists()
            report = json.loads(json_report.read_text(encoding="utf-8")) if json_exists else {}

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(json_exists)
        self.assertTrue(md_exists)
        self.assertTrue(csv_exists)
        self.assertEqual(report.get("module"), "claim_citation_triage")

    def test_cli_exits_1_on_orphaned_key(self) -> None:
        with workspace_tempdir("cc-cli-orphan-") as base:
            project = materialize_project(
                base / "project",
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\cite{fake2024}\n\\end{document}\n",
                    "ref/refs.bib": "@article{other2024, title={Other}, author={A}, year={2024}, journal={J}}\n",
                },
            )
            result = subprocess.run(
                [sys.executable, str(CLI_SCRIPT), "--project-root", str(project), "--ruleset", "university-generic"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            report = json.loads((project / "reports" / "claim-citation-triage-report.json").read_text(encoding="utf-8"))
            labels = [e["triage_label"] for e in report["entries"]]
            status = report["status"]

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(status, "ORPHANED")
        self.assertIn("ORPHANED", labels)

    def test_cli_handles_missing_hallucination_report(self) -> None:
        with workspace_tempdir("cc-cli-nohr-") as base:
            project = materialize_project(
                base / "project",
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\nA claim \\cite{smith2024}.\n\\end{document}\n",
                    "ref/refs.bib": "@article{smith2024, title={T}, author={A}, year={2024}, journal={J}}\n",
                },
            )
            result = subprocess.run(
                [sys.executable, str(CLI_SCRIPT), "--project-root", str(project), "--ruleset", "university-generic"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            report = json.loads((project / "reports" / "claim-citation-triage-report.json").read_text(encoding="utf-8"))
            module_name = report["module"]
            entry_count = len(report["entries"])

        self.assertEqual(result.returncode, 0)
        self.assertEqual(module_name, "claim_citation_triage")
        self.assertGreaterEqual(entry_count, 1)

    def test_cli_outputs_three_report_formats(self) -> None:
        with workspace_tempdir("cc-cli-formats-") as base:
            project = materialize_project(
                base / "project",
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\cite{a2024}\n\\end{document}\n",
                    "ref/refs.bib": "@article{a2024, title={A}, author={B}, year={2024}, journal={J}}\n",
                },
            )
            result = subprocess.run(
                [sys.executable, str(CLI_SCRIPT), "--project-root", str(project), "--ruleset", "university-generic"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            json_exists = (project / "reports" / "claim-citation-triage-report.json").exists()
            md_exists = (project / "reports" / "claim-citation-triage.md").exists()
            csv_exists = (project / "reports" / "claim-citation-triage.csv").exists()

        self.assertEqual(result.returncode, 0)
        self.assertTrue(json_exists)
        self.assertTrue(md_exists)
        self.assertTrue(csv_exists)


if __name__ == "__main__":
    unittest.main()


class ClaimCitationDemoTest(unittest.TestCase):
    def test_mixed_demo_produces_all_triage_labels(self) -> None:
        demo = ROOT / "examples" / "claim-citation-mixed"
        result = subprocess.run(
            [sys.executable, str(CLI_SCRIPT), "--project-root", str(demo), "--ruleset", "university-generic"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        report = json.loads((demo / "reports" / "claim-citation-triage-report.json").read_text(encoding="utf-8"))
        labels = {e["triage_label"] for e in report["entries"]}

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertTrue(labels.issubset({"WELL_SUPPORTED", "SUPPORTED", "WEAK", "ORPHANED", "UNVERIFIABLE"}))
        self.assertIn("ORPHANED", labels)

    def test_orphaned_demo_exits_1_and_has_orphaned_labels(self) -> None:
        demo = ROOT / "examples" / "claim-citation-orphaned"
        result = subprocess.run(
            [sys.executable, str(CLI_SCRIPT), "--project-root", str(demo), "--ruleset", "university-generic"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        report = json.loads((demo / "reports" / "claim-citation-triage-report.json").read_text(encoding="utf-8"))
        labels = [e["triage_label"] for e in report["entries"]]

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("ORPHANED", labels)

    def test_chinese_demo_exits_0_all_unverifiable(self) -> None:
        demo = ROOT / "examples" / "claim-citation-chinese"
        result = subprocess.run(
            [sys.executable, str(CLI_SCRIPT), "--project-root", str(demo), "--ruleset", "university-generic"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        report = json.loads((demo / "reports" / "claim-citation-triage-report.json").read_text(encoding="utf-8"))
        labels = {e["triage_label"] for e in report["entries"]}

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("UNVERIFIABLE", labels)
        self.assertEqual(report["status"], "UNVERIFIABLE")