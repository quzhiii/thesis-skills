from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from tests.helpers import materialize_project, workspace_tempdir
from tests.test_rules import PACK_ROOT


ROOT = Path(__file__).resolve().parents[1]
CLI_SCRIPT = ROOT / "33-final-delivery" / "run_final_delivery.py"


class FinalDeliveryTest(unittest.TestCase):
    def test_final_delivery_workflow_rebuilds_bundle(self) -> None:
        with workspace_tempdir("final-delivery-") as base:
            materialize_project(
                base,
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\input{chapters/ch1}\n\\end{document}\n",
                    "chapters/ch1.tex": "TODO: remove this.\nNormal text.\n",
                    "ref/refs.bib": "@article{a2024, title={A}, author={B}, year={2024}, journal={J}}\n",
                },
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(CLI_SCRIPT),
                    "--project-root",
                    str(base),
                    "--ruleset",
                    "university-generic",
                    "--skip-evidence",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            summary = json.loads(result.stdout)

            self.assertIn("steps", summary)
            self.assertIn("final-audit-checks", summary["steps"])
            self.assertIn("bundle-rebuild", summary["steps"])

            final_audit_json = base / "reports" / "final-audit-report.json"
            self.assertTrue(final_audit_json.exists(), "final-audit-report.json should exist")

            final_audit_html = base / "reports" / "final-audit-report.html"
            self.assertTrue(final_audit_html.exists(), "final-audit-report.html should exist")

            index_html = base / "reports" / "index.html"
            self.assertTrue(index_html.exists(), "index.html should exist")

    def test_final_delivery_workflow_with_preview_fixes(self) -> None:
        with workspace_tempdir("final-delivery-fix-") as base:
            materialize_project(
                base,
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\input{chapters/ch1}\n\\end{document}\n",
                    "chapters/ch1.tex": "TODO: remove this.\nNormal text.\n",
                },
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(CLI_SCRIPT),
                    "--project-root",
                    str(base),
                    "--ruleset",
                    "university-generic",
                    "--skip-evidence",
                    "--fix-preview",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            summary = json.loads(result.stdout)
            self.assertIn("fix-preview", summary["steps"])


if __name__ == "__main__":
    unittest.main()
