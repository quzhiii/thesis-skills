from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from core.compile_parser import parse_compile_log_file
from core.rules import find_rule_pack
from tests.helpers import materialize_project, workspace_tempdir


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "data" / "compile_logs"
CHECKER = ROOT / "15-check-compile" / "check_compile.py"


class CompileParserTest(unittest.TestCase):
    def test_fixture_corpus_exists(self) -> None:
        expected = {
            "undefined-control-sequence.log",
            "missing-package.log",
            "missing-citation-reference.log",
            "bibliography-backend.log",
            "overfull-box.log",
        }
        self.assertTrue((FIXTURES / "README.md").exists())
        actual = {path.name for path in FIXTURES.glob("*.log")}
        self.assertTrue(expected <= actual)

    def test_checker_entrypoint_exists_and_outputs_json(self) -> None:
        self.assertTrue(CHECKER.exists())
        with workspace_tempdir("compile-") as base:
            project = materialize_project(
                base / "project",
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\nHello\n\\end{document}\n",
                    "main.log": (FIXTURES / "undefined-control-sequence.log").read_text(encoding="utf-8"),
                },
            )
            report = project / "reports" / "check_compile-report.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(CHECKER),
                    "--project-root",
                    str(project),
                    "--ruleset",
                    "university-generic",
                    "--report",
                    str(report),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            payload = json.loads(report.read_text(encoding="utf-8"))
            self.assertIn("summary", payload)
            self.assertIn("findings", payload)

    def test_parse_build_blocking_errors_and_warnings(self) -> None:
        undefined = parse_compile_log_file(FIXTURES / "undefined-control-sequence.log")
        missing = parse_compile_log_file(FIXTURES / "missing-package.log")
        warnings = parse_compile_log_file(FIXTURES / "missing-citation-reference.log")

        self.assertEqual(undefined[0].category, "undefined_control_sequence")
        self.assertEqual(undefined[0].severity, "error")
        self.assertEqual(undefined[0].line, 42)
        self.assertEqual(missing[0].category, "missing_file_or_package")
        self.assertEqual(missing[0].line, 3)
        categories = {item.category for item in warnings}
        self.assertIn("missing_citation", categories)
        self.assertIn("missing_reference", categories)

    def test_preserves_unknown_warning_cases(self) -> None:
        findings = parse_compile_log_file(FIXTURES / "unknown-warning.log")
        self.assertEqual(findings[0].category, "compile_warning_unknown")
        self.assertIn("hyperref", findings[0].message)

    def test_checker_report_shape(self) -> None:
        with workspace_tempdir("compile-") as base:
            project = materialize_project(
                base / "project",
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\nHello\n\\end{document}\n",
                    "main.log": "LaTeX Warning: Citation `ref1' on page 1 undefined on input line 7.\n",
                },
            )
            report = project / "reports" / "check_compile-report.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(CHECKER),
                    "--project-root",
                    str(project),
                    "--ruleset",
                    "university-generic",
                    "--report",
                    str(report),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            payload = json.loads(report.read_text(encoding="utf-8"))
            self.assertIn("summary", payload)
            self.assertIn("findings", payload)
            self.assertEqual(payload["summary"]["warnings"], 1)
            self.assertEqual(payload["summary"]["errors"], 0)

    def test_all_rulepacks_include_compile_policy(self) -> None:
        for ruleset in ["university-generic", "tsinghua-thesis", "journal-generic"]:
            pack = find_rule_pack(ROOT, ruleset)
            self.assertIn("compile", pack.rules)
            compile_rules = pack.rules["compile"]
            self.assertIn("enabled", compile_rules)
            self.assertIn("severity", compile_rules)
            self.assertIn("categories", compile_rules)


if __name__ == "__main__":
    unittest.main()
