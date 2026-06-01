from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from core.final_cleanup import run_final_cleanup_check
from core.project import ThesisProject
from core.rules import load_rule_pack
from tests.helpers import materialize_project, workspace_tempdir
from tests.test_rules import PACK_ROOT


ROOT = Path(__file__).resolve().parents[1]
CLI_SCRIPT = ROOT / "23-check-final-cleanup" / "check_final_cleanup.py"


class FinalCleanupCheckTest(unittest.TestCase):
    def _project(self, base: Path) -> tuple[ThesisProject, object]:
        pack = load_rule_pack(PACK_ROOT / "university-generic")
        project = ThesisProject.discover(
            base,
            pack.rules["project"]["main_tex_candidates"],
            pack.rules["project"]["chapter_globs"],
            pack.rules["project"]["bibliography_files"],
        )
        return project, pack

    def test_reports_all_default_cleanup_markers(self) -> None:
        with workspace_tempdir("final-cleanup-markers-") as base:
            materialize_project(
                base,
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\input{chapters/ch1}\n\\end{document}\n",
                    "chapters/ch1.tex": (
                        "TODO: remove this note.\n"
                        "FIXME: verify the table.\n"
                        "待修改 待核查 见截图 这里再改\n"
                        "临时 占位 ???\n"
                        "\\textcolor{blue}{marked} and {\\color{blue} text}\n"
                        "draft debug\n"
                    ),
                },
            )
            project, pack = self._project(base)
            report = base / "reports" / "final-cleanup-report.json"
            exit_code = run_final_cleanup_check(project, pack, report)
            data = json.loads(report.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 1)
        self.assertEqual(data["summary"]["checker"], "check_final_cleanup")
        self.assertEqual(data["summary"]["status"], "FAIL")
        self.assertEqual(data["summary"]["residue_findings"], 13)
        self.assertEqual(data["summary"]["patterns_scanned"], 13)
        codes = {finding["code"] for finding in data["findings"]}
        self.assertIn("FINAL_CLEANUP_TODO", codes)
        self.assertIn("FINAL_CLEANUP_TEXTCOLOR_BLUE", codes)
        self.assertIn("FINAL_CLEANUP_COLOR_BLUE", codes)
        self.assertIn("FINAL_CLEANUP_DEBUG", codes)
        self.assertTrue(all(finding["review_required"] for finding in data["findings"]))
        self.assertTrue(all(finding["risk_level"] == "P0" for finding in data["findings"]))
        self.assertIn("future_integration", data)

    def test_avoids_embedded_english_token_false_positives(self) -> None:
        with workspace_tempdir("final-cleanup-clean-") as base:
            materialize_project(
                base,
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\input{chapters/ch1}\n\\end{document}\n",
                    "chapters/ch1.tex": "The drafted methods section describes a debugger metaphor and a TODOish label.\n",
                },
            )
            project, pack = self._project(base)
            report = base / "reports" / "final-cleanup-report.json"
            exit_code = run_final_cleanup_check(project, pack, report)
            data = json.loads(report.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0)
        self.assertEqual(data["summary"]["status"], "PASS")
        self.assertEqual(data["findings"], [])

    def test_cli_writes_default_report(self) -> None:
        with workspace_tempdir("final-cleanup-cli-") as base:
            project = materialize_project(
                base / "project",
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\input{chapters/ch1}\n\\end{document}\n",
                    "chapters/ch1.tex": "This line has debug residue.\n",
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
            report = project / "reports" / "final-cleanup-report.json"
            data = json.loads(report.read_text(encoding="utf-8"))

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(data["summary"]["checker"], "check_final_cleanup")
        self.assertEqual(data["findings"][0]["original_text"], "debug")


if __name__ == "__main__":
    unittest.main()
