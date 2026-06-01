from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from core.project import ThesisProject
from core.rules import load_rule_pack
from core.statistical_consistency import run_statistical_consistency_check
from tests.helpers import materialize_project, workspace_tempdir
from tests.test_rules import PACK_ROOT


ROOT = Path(__file__).resolve().parents[1]
CLI_SCRIPT = ROOT / "25-check-statistical-consistency" / "check_statistical_consistency.py"


class StatisticalConsistencyTest(unittest.TestCase):
    def _project(self, base: Path) -> tuple[ThesisProject, object]:
        pack = load_rule_pack(PACK_ROOT / "university-generic")
        project = ThesisProject.discover(
            base,
            pack.rules["project"]["main_tex_candidates"],
            pack.rules["project"]["chapter_globs"],
            pack.rules["project"]["bibliography_files"],
        )
        return project, pack

    def test_reports_deviations_from_dominant_statistical_style(self) -> None:
        with workspace_tempdir("stat-consistency-mixed-") as base:
            materialize_project(
                base,
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\input{chapters/ch1}\n\\end{document}\n",
                    "chapters/ch1.tex": (
                        "The main test reports p值 twice, p值 again, and P值 once.\n"
                        "Models use p=0.01 and P=0.02.\n"
                        "Intervals include 95%CI and 95\\%CI.\n"
                        "Bootstrap is also called 自助法.\n"
                        "SMD is also described as 标准化均数差.\n"
                    ),
                },
            )
            project, pack = self._project(base)
            report = base / "reports" / "statistical-consistency-report.json"
            exit_code = run_statistical_consistency_check(project, pack, report)
            data = json.loads(report.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 1)
        self.assertEqual(data["summary"]["checker"], "check_statistical_consistency")
        self.assertEqual(data["summary"]["status"], "FAIL")
        self.assertGreaterEqual(data["summary"]["mixed_families"], 5)
        self.assertTrue(data["findings"])
        messages = [finding["message"] for finding in data["findings"]]
        self.assertTrue(any("dominant style p值" in message for message in messages))
        self.assertTrue(all(finding["risk_level"] == "P1" for finding in data["findings"]))
        self.assertIn("families", data)
        self.assertIn("future_integration", data)

    def test_clean_single_style_passes(self) -> None:
        with workspace_tempdir("stat-consistency-clean-") as base:
            materialize_project(
                base,
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\input{chapters/ch1}\n\\end{document}\n",
                    "chapters/ch1.tex": "The study reports p值, p值, and 95%CI consistently.\n",
                },
            )
            project, pack = self._project(base)
            report = base / "reports" / "statistical-consistency-report.json"
            exit_code = run_statistical_consistency_check(project, pack, report)
            data = json.loads(report.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0)
        self.assertEqual(data["summary"]["status"], "PASS")
        self.assertEqual(data["findings"], [])

    def test_cli_writes_default_report(self) -> None:
        with workspace_tempdir("stat-consistency-cli-") as base:
            project = materialize_project(
                base / "project",
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\input{chapters/ch1}\n\\end{document}\n",
                    "chapters/ch1.tex": "The model reports p值 and P值.\n",
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
            report = project / "reports" / "statistical-consistency-report.json"
            data = json.loads(report.read_text(encoding="utf-8"))

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(data["summary"]["checker"], "check_statistical_consistency")


if __name__ == "__main__":
    unittest.main()
