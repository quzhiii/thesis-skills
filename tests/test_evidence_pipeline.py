from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from tests.helpers import materialize_project, workspace_tempdir

ROOT = Path(__file__).resolve().parents[1]


class EvidencePipelineTest(unittest.TestCase):
    def test_pipeline_runs_all_steps_and_writes_reports(self) -> None:
        with workspace_tempdir("ep-full-") as base:
            project = materialize_project(
                base / "project",
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\nA claim \\cite{smith2024}.\n\\end{document}\n",
                    "main.aux": "\\citation{smith2024}\n\\bibdata{ref/refs}\n\\bibcite{smith2024}{1}\n",
                    "main.bbl": "\\bibitem{smith2024} Test\n",
                    "ref/refs.bib": "@article{smith2024, title={Test Title}, author={Author}, year={2024}, journal={J}, doi={10.1000/test}}\n",
                    "reports/external-verification-report.json": json.dumps({
                        "module": "citation_external_verification",
                        "entries": [
                            {
                                "citation_key": "smith2024",
                                "match_status": "MATCH",
                                "providers": [{"source": "crossref", "success": True, "candidate_count": 1, "candidates": [{"doi": "10.1000/test", "doi_exact_match": True, "title_similarity": 1.0}]}],
                            }
                        ],
                    }),
                },
            )
            runner = ROOT / "run_evidence_pipeline.py"
            result = subprocess.run(
                [sys.executable, str(runner), "--project-root", str(project), "--ruleset", "university-generic", "--skip-external"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            ref_exists = (project / "reports" / "check_references-report.json").exists()
            final_ref_exists = (project / "reports" / "final-reference-set-report.json").exists()
            risk_exists = (project / "reports" / "hallucination-risk-report.json").exists()
            cc_exists = (project / "reports" / "claim-citation-triage-report.json").exists()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(ref_exists)
        self.assertTrue(final_ref_exists)
        self.assertTrue(risk_exists)
        self.assertTrue(cc_exists)

    def test_pipeline_exits_1_on_orphaned(self) -> None:
        with workspace_tempdir("ep-orphan-") as base:
            project = materialize_project(
                base / "project",
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\cite{missing2024}\n\\end{document}\n",
                    "ref/refs.bib": "@article{other2024, title={T}, author={A}, year={2024}, journal={J}}\n",
                },
            )
            runner = ROOT / "run_evidence_pipeline.py"
            result = subprocess.run(
                [sys.executable, str(runner), "--project-root", str(project), "--ruleset", "university-generic", "--skip-external"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        summary = json.loads(result.stdout)
        self.assertGreaterEqual(summary["claim_citation"]["exit_code"], 1)

    def test_pipeline_skip_external_does_not_run_verify(self) -> None:
        with workspace_tempdir("ep-skip-") as base:
            project = materialize_project(
                base / "project",
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\cite{smith2024}\n\\end{document}\n",
                    "ref/refs.bib": "@article{smith2024, title={T}, author={A}, year={2024}, journal={J}}\n",
                },
            )
            runner = ROOT / "run_evidence_pipeline.py"
            result = subprocess.run(
                [sys.executable, str(runner), "--project-root", str(project), "--ruleset", "university-generic", "--skip-external"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            summary = json.loads(result.stdout)
            self.assertNotIn("external_verification", summary)

    def test_pipeline_prints_step_summary(self) -> None:
        with workspace_tempdir("ep-summary-") as base:
            project = materialize_project(
                base / "project",
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\cite{s2024}\n\\end{document}\n",
                    "ref/refs.bib": "@article{s2024, title={T}, author={A}, year={2024}, journal={J}}\n",
                },
            )
            runner = ROOT / "run_evidence_pipeline.py"
            result = subprocess.run(
                [sys.executable, str(runner), "--project-root", str(project), "--ruleset", "university-generic", "--skip-external"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            summary = json.loads(result.stdout)

        self.assertIn("references", summary)
        self.assertIn("final_reference_set", summary)
        self.assertIn("hallucination_risk", summary)
        self.assertIn("claim_citation", summary)


if __name__ == "__main__":
    unittest.main()
