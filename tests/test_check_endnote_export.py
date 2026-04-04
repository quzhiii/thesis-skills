from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from tests.helpers import workspace_tempdir


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "00-bib-endnote" / "check_endnote_export.py"
DATA = ROOT / "tests" / "data"


class TestCheckEndNoteExport(unittest.TestCase):
    def test_xml_preflight_generates_report_with_warnings(self) -> None:
        with workspace_tempdir("check-endnote-export-") as project_root:
            (project_root / "main.tex").write_text(
                "\\documentclass{article}\n\\begin{document}\nHello\n\\end{document}\n",
                encoding="utf-8",
            )
            report_path = project_root / "reports" / "check_endnote_export-report.json"

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--project-root",
                    str(project_root),
                    "--input",
                    str(DATA / "sample_endnote.xml"),
                    "--format",
                    "auto",
                    "--report",
                    str(report_path),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(report_path.exists())
            payload = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["summary"]["source_format"], "xml")
            self.assertEqual(payload["summary"]["total_refs"], 4)
            self.assertGreaterEqual(payload["summary"]["warnings"], 1)

    def test_ris_preflight_generates_report(self) -> None:
        with workspace_tempdir("check-endnote-export-") as project_root:
            (project_root / "main.tex").write_text(
                "\\documentclass{article}\n\\begin{document}\nHello\n\\end{document}\n",
                encoding="utf-8",
            )
            report_path = project_root / "reports" / "check_endnote_export-report.json"

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--project-root",
                    str(project_root),
                    "--input",
                    str(DATA / "sample_endnote.ris"),
                    "--format",
                    "auto",
                    "--report",
                    str(report_path),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["summary"]["source_format"], "ris")
            self.assertEqual(payload["summary"]["total_refs"], 3)
            self.assertIn("warnings", payload)


if __name__ == "__main__":
    unittest.main()
