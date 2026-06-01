from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from core.manual_anchor import run_manual_anchor_check
from core.project import ThesisProject
from core.rules import load_rule_pack
from tests.helpers import materialize_project, workspace_tempdir
from tests.test_rules import PACK_ROOT


ROOT = Path(__file__).resolve().parents[1]
CLI_SCRIPT = ROOT / "26-check-manual-anchor" / "check_manual_anchor.py"


class ManualAnchorTest(unittest.TestCase):
    def _project(self, base: Path) -> tuple[ThesisProject, object]:
        pack = load_rule_pack(PACK_ROOT / "university-generic")
        project = ThesisProject.discover(
            base,
            pack.rules["project"]["main_tex_candidates"],
            pack.rules["project"]["chapter_globs"],
            pack.rules["project"]["bibliography_files"],
        )
        return project, pack

    def test_reports_addcontentsline_without_preceding_phantomsection(self) -> None:
        with workspace_tempdir("manual-anchor-missing-") as base:
            materialize_project(
                base,
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\input{chapters/ch1}\n\\end{document}\n",
                    "chapters/ch1.tex": "\\chapter*{Appendix}\n\\addcontentsline{toc}{chapter}{Appendix}\n",
                },
            )
            project, pack = self._project(base)
            report = base / "reports" / "manual-anchor-report.json"
            exit_code = run_manual_anchor_check(project, pack, report)
            data = json.loads(report.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 1)
        self.assertEqual(data["summary"]["checker"], "check_manual_anchor")
        self.assertEqual(data["summary"]["status"], "FAIL")
        self.assertEqual(data["summary"]["manual_contents_lines"], 1)
        self.assertEqual(data["summary"]["missing_phantomsection"], 1)
        self.assertEqual(data["findings"][0]["code"], "ANCHOR_MISSING_PHANTOMSECTION")
        self.assertEqual(data["findings"][0]["risk_level"], "P1")

    def test_accepts_nearby_preceding_phantomsection(self) -> None:
        with workspace_tempdir("manual-anchor-clean-") as base:
            materialize_project(
                base,
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\input{chapters/ch1}\n\\end{document}\n",
                    "chapters/ch1.tex": "\\chapter*{Appendix}\n\\phantomsection\n\\addcontentsline{toc}{chapter}{Appendix}\n",
                },
            )
            project, pack = self._project(base)
            report = base / "reports" / "manual-anchor-report.json"
            exit_code = run_manual_anchor_check(project, pack, report)
            data = json.loads(report.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0)
        self.assertEqual(data["summary"]["status"], "PASS")
        self.assertEqual(data["findings"], [])
        self.assertTrue(data["manual_contents_lines"][0]["has_phantomsection"])

    def test_cli_writes_default_report(self) -> None:
        with workspace_tempdir("manual-anchor-cli-") as base:
            project = materialize_project(
                base / "project",
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\input{chapters/ch1}\n\\end{document}\n",
                    "chapters/ch1.tex": "\\addcontentsline{lof}{figure}{Figure A}\n",
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
            report = project / "reports" / "manual-anchor-report.json"
            data = json.loads(report.read_text(encoding="utf-8"))

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(data["summary"]["checker"], "check_manual_anchor")


if __name__ == "__main__":
    unittest.main()
