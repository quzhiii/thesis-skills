from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from tests.helpers import materialize_project, workspace_project_copy, workspace_tempdir

ROOT = Path(__file__).resolve().parents[1]
CLI_SCRIPT = ROOT / "19-check-hallucination-risk" / "check_hallucination_risk.py"


class HallucinationRiskCLITest(unittest.TestCase):
    def test_cli_accepts_project_root_and_writes_reports(self) -> None:
        with workspace_tempdir("hrisk-cli-") as base:
            project = materialize_project(
                base / "project",
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\cite{smith2024}\n\\end{document}\n",
                    "ref/refs.bib": "@article{smith2024, title={Example Title}, author={Smith, Jane}, year={2024}, journal={J}, doi={10.1000/example}}\n",
                    "reports/external-verification-report.json": json.dumps({
                        "module": "citation_external_verification",
                        "entries": [
                            {
                                "citation_key": "smith2024",
                                "match_status": "MATCH",
                                "providers": [{"source": "crossref", "success": True, "candidate_count": 1, "candidates": [{"doi": "10.1000/example", "doi_exact_match": True, "title_similarity": 1.0}]}],
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
            json_report = project / "reports" / "hallucination-risk-report.json"
            csv_report = project / "reports" / "high-risk-references.csv"
            report_exists = json_report.exists()
            csv_exists = csv_report.exists()
            report = json.loads(json_report.read_text(encoding="utf-8")) if report_exists else {}

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(report_exists)
        self.assertTrue(csv_exists)
        self.assertEqual(report["module"], "citation_hallucination_risk")
        self.assertEqual(report["version"], "3.0")

    def test_cli_exits_1_on_high_risk(self) -> None:
        with workspace_tempdir("hrisk-cli-high-") as base:
            project = materialize_project(
                base / "project",
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\cite{fake2024}\n\\end{document}\n",
                    "ref/refs.bib": "@article{fake2024, title={Totally Fabricated AI Paper}, author={Fake, Author}, year={2024}, journal={Nonexistent Journal}}\n",
                    "reports/external-verification-report.json": json.dumps({
                        "module": "citation_external_verification",
                        "entries": [
                            {
                                "citation_key": "fake2024",
                                "match_status": "NO_CANDIDATE",
                                "providers": [
                                    {"source": "crossref", "success": True, "candidate_count": 0, "candidates": []},
                                    {"source": "openalex", "success": True, "candidate_count": 0, "candidates": []},
                                    {"source": "semantic_scholar", "success": True, "candidate_count": 0, "candidates": []},
                                ],
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
            report = json.loads((project / "reports" / "hallucination-risk-report.json").read_text(encoding="utf-8"))

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(report["status"], "HIGH_RISK")

    def test_cli_returns_0_on_unsupported(self) -> None:
        with workspace_tempdir("hrisk-cli-unsup-") as base:
            project = materialize_project(
                base / "project",
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\cite{zhang2024}\n\\end{document}\n",
                    "ref/refs.bib": "@article{zhang2024, title={中文参考文献测试}, author={张三}, year={2024}, journal={计算机学报}}\n",
                },
            )
            result = subprocess.run(
                [sys.executable, str(CLI_SCRIPT), "--project-root", str(project), "--ruleset", "university-generic"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            report = json.loads((project / "reports" / "hallucination-risk-report.json").read_text(encoding="utf-8"))

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(report["status"], "UNSUPPORTED")

    def test_cli_works_without_external_report(self) -> None:
        with workspace_tempdir("hrisk-cli-noext-") as base:
            project = materialize_project(
                base / "project",
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\cite{plain2024}\n\\end{document}\n",
                    "ref/refs.bib": "@article{plain2024, title={A Normal Paper}, author={Doe, Jane}, year={2024}, journal={J}}\n",
                },
            )
            result = subprocess.run(
                [sys.executable, str(CLI_SCRIPT), "--project-root", str(project), "--ruleset", "university-generic"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            json_report = project / "reports" / "hallucination-risk-report.json"
            report_exists = json_report.exists()

        self.assertIn(result.returncode, (0, 1))
        self.assertTrue(report_exists)


class HallucinationRiskDemoTest(unittest.TestCase):
    def test_demo_cli_tests_do_not_mutate_tracked_reports(self) -> None:
        watched_reports = [
            ROOT / "examples" / "citation-hallucination-field-mismatch" / "reports" / "high-risk-references.csv",
            ROOT / "examples" / "citation-hallucination-fabricated" / "reports" / "high-risk-references.csv",
        ]
        before = {path: path.read_text(encoding="utf-8") for path in watched_reports}

        self.test_field_mismatch_demo_produces_review()
        self.test_fabricated_demo_produces_high_risk()

        after = {path: path.read_text(encoding="utf-8") for path in watched_reports}
        self.assertEqual(after, before)

    def test_field_mismatch_demo_produces_review(self) -> None:
        source_demo = ROOT / "examples" / "citation-hallucination-field-mismatch"
        with workspace_project_copy(source_demo, "hrisk-demo-field-") as demo:
            result = subprocess.run(
                [sys.executable, str(CLI_SCRIPT), "--project-root", str(demo), "--ruleset", "university-generic"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            report = json.loads((demo / "reports" / "hallucination-risk-report.json").read_text(encoding="utf-8"))
        labels = [e["risk_label"] for e in report["entries"]]
        self.assertTrue(any(label in {"REVIEW", "HIGH_RISK"} for label in labels))

    def test_fabricated_demo_produces_high_risk(self) -> None:
        source_demo = ROOT / "examples" / "citation-hallucination-fabricated"
        with workspace_project_copy(source_demo, "hrisk-demo-fabricated-") as demo:
            result = subprocess.run(
                [sys.executable, str(CLI_SCRIPT), "--project-root", str(demo), "--ruleset", "university-generic"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            report = json.loads((demo / "reports" / "hallucination-risk-report.json").read_text(encoding="utf-8"))
            csv_path = demo / "reports" / "high-risk-references.csv"
            csv_exists = csv_path.exists()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(report["status"], "HIGH_RISK")
        self.assertTrue(csv_exists)

    def test_chinese_unsupported_demo_produces_unsupported_not_high_risk(self) -> None:
        source_demo = ROOT / "examples" / "citation-hallucination-chinese-unsupported"
        with workspace_project_copy(source_demo, "hrisk-demo-chinese-") as demo:
            result = subprocess.run(
                [sys.executable, str(CLI_SCRIPT), "--project-root", str(demo), "--ruleset", "university-generic"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            report = json.loads((demo / "reports" / "hallucination-risk-report.json").read_text(encoding="utf-8"))
        labels = [e["risk_label"] for e in report["entries"]]
        self.assertNotIn("HIGH_RISK", labels)
        self.assertIn("UNSUPPORTED", labels)
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
