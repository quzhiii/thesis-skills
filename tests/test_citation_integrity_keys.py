from __future__ import annotations

import unittest
import json
import subprocess
import sys

from core.citation_integrity.bib_parser import find_duplicate_key_groups, parse_bib_entries_from_text
from core.citation_integrity.report import build_citation_integrity_report, write_citation_integrity_report
from tests.helpers import materialize_project, workspace_tempdir


ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]
from core.citation_integrity.tex_parser import collect_citations_from_text


class CitationIntegrityKeyParsingTest(unittest.TestCase):
    def test_collects_common_citation_commands_with_multiple_keys_and_lines(self) -> None:
        text = (
            "Intro text \\cite{smith2024}.\n"
            "Prior work \\citep[see][p. 2]{doe2020, wang2021}.\n"
            "Narrative \\citet*{miller2019} and \\parencite{chen2022}.\n"
            "Biblatex commands \\textcite{lee2023} plus \\autocite[45]{garcia2024}.\n"
        )

        occurrences = collect_citations_from_text(text, "chapters/intro.tex")

        self.assertEqual(
            [(item.key, item.command, item.line) for item in occurrences],
            [
                ("smith2024", "cite", 1),
                ("doe2020", "citep", 2),
                ("wang2021", "citep", 2),
                ("miller2019", "citet", 3),
                ("chen2022", "parencite", 3),
                ("lee2023", "textcite", 4),
                ("garcia2024", "autocite", 4),
            ],
        )

    def test_parses_bib_entries_without_collapsing_duplicate_keys(self) -> None:
        text = (
            "@article{smith2024,\n"
            "  title = {First Title},\n"
            "  author = {Smith, Jane},\n"
            "  year = {2024},\n"
            "  journal = {Demo Journal}\n"
            "}\n\n"
            "@book{smith2024,\n"
            "  title = {Different Title},\n"
            "  author = {Smith, Jane},\n"
            "  year = {2024},\n"
            "  publisher = {Demo Press}\n"
            "}\n"
        )

        entries = parse_bib_entries_from_text(text, "ref/refs.bib")

        self.assertEqual([entry.key for entry in entries], ["smith2024", "smith2024"])
        self.assertEqual([entry.entry_type for entry in entries], ["article", "book"])
        self.assertEqual(entries[0].fields["title"], "First Title")
        self.assertEqual(entries[1].fields["publisher"], "Demo Press")
        self.assertEqual(entries[0].line, 1)
        self.assertEqual(entries[1].line, 8)

    def test_duplicate_detection_distinguishes_conflicting_metadata(self) -> None:
        first = parse_bib_entries_from_text(
            "@article{shared,\n"
            "  title = {Same Title},\n"
            "  author = {Smith, Jane},\n"
            "  year = {2024},\n"
            "  journal = {Demo Journal}\n"
            "}\n",
            "ref/a.bib",
        )
        second = parse_bib_entries_from_text(
            "@article{shared,\n"
            "  title = {Different Title},\n"
            "  author = {Smith, Jane},\n"
            "  year = {2024},\n"
            "  journal = {Demo Journal}\n"
            "}\n",
            "ref/b.bib",
        )

        groups = find_duplicate_key_groups([*first, *second])

        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0].key, "shared")
        self.assertTrue(groups[0].has_conflicting_metadata)
        self.assertEqual([entry.file for entry in groups[0].entries], ["ref/a.bib", "ref/b.bib"])

    def test_report_marks_missing_key_and_duplicate_conflict_as_blocking(self) -> None:
        tex_texts = {"main.tex": "\\cite{present,missing}\n"}
        bib_texts = {
            "ref/a.bib": "@article{present, title={A}, author={A}, year={2024}, journal={J}, doi={10.1000/a}}\n",
            "ref/b.bib": "@article{present, title={B}, author={A}, year={2024}, journal={J}, doi={10.1000/b}}\n",
        }

        report = build_citation_integrity_report(tex_texts, bib_texts, current_year=2026)

        self.assertEqual(report["status"], "BLOCK")
        codes = [issue["code"] for issue in report["issues"]]
        self.assertIn("CI-MISSING-KEY", codes)
        self.assertIn("CI-DUPLICATE-KEY-CONFLICT", codes)
        self.assertEqual(codes, sorted(codes))

    def test_rich_report_writer_emits_json_schema(self) -> None:
        report = build_citation_integrity_report(
            {"main.tex": "\\cite{missing}\n"},
            {"ref/refs.bib": ""},
            current_year=2026,
        )
        with workspace_tempdir("citation-report-") as tempdir:
            output = tempdir / "reports" / "citation-integrity-report.json"
            write_citation_integrity_report(report, output)
            payload = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(payload["module"], "citation_integrity")
        self.assertEqual(payload["version"], "1.1")
        self.assertEqual(payload["status"], "BLOCK")
        self.assertEqual(payload["summary"]["missing_cited_keys"], 1)

    def test_check_references_cli_emits_compatibility_and_rich_reports(self) -> None:
        with workspace_tempdir("citation-cli-") as base:
            project = materialize_project(
                base / "project",
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\cite{present,missing}\n\\end{document}\n",
                    "ref/refs.bib": "@article{present, title={Present}, author={A}, year={2024}, journal={J}, doi={10.1000/p}}\n",
                },
            )
            compatibility_report = project / "reports" / "check_references-report.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "10-check-references" / "check_references.py"),
                    "--project-root",
                    str(project),
                    "--ruleset",
                    "university-generic",
                    "--report",
                    str(compatibility_report),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

            rich_report = project / "reports" / "citation-integrity-report.json"
            rich_report_exists = rich_report.exists()
            compatibility = json.loads(compatibility_report.read_text(encoding="utf-8"))
            rich = json.loads(rich_report.read_text(encoding="utf-8"))

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(compatibility["summary"]["checker"], "check_references")
        self.assertTrue(rich_report_exists)
        self.assertEqual(rich["status"], "BLOCK")
        self.assertEqual(rich["summary"]["missing_cited_keys"], 1)


if __name__ == "__main__":
    unittest.main()
