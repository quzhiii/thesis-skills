from __future__ import annotations

import unittest
import csv
import io
import json

from core.citation_integrity.final_reference_set import (
    build_final_reference_set_report,
    parse_aux_file,
    parse_bbl_file,
    write_final_reference_set_csv,
    write_final_reference_set_json,
)
from core.project import ThesisProject
from tests.helpers import materialize_project, workspace_tempdir


class FinalReferenceSetTest(unittest.TestCase):
    def test_parse_aux_file_collects_citations_bibdata_and_bibcite_keys(self) -> None:
        with workspace_tempdir("final-ref-aux-") as base:
            aux = materialize_project(
                base / "project",
                {
                    "main.aux": "\\citation{smith2024,doe2020}\n\\citation{wang2021}\n\\bibdata{ref/refs,extra}\n\\bibcite{smith2024}{1}\n",
                },
            ) / "main.aux"

            data = parse_aux_file(aux)

        self.assertEqual(data.citation_keys, ["smith2024", "doe2020", "wang2021"])
        self.assertEqual(data.bibdata_sources, ["ref/refs", "extra"])
        self.assertEqual(data.bibcite_keys, ["smith2024"])

    def test_parse_bbl_file_collects_plain_and_optional_bibitems(self) -> None:
        with workspace_tempdir("final-ref-bbl-") as base:
            bbl = materialize_project(
                base / "project",
                {
                    "main.bbl": "\\begin{thebibliography}{9}\n\\bibitem[Smith(2024)]{smith2024} A\n\\bibitem{doe2020} B\n\\bibitem[Wang et al.(2021)]{wang2021} C\n\\end{thebibliography}\n",
                },
            ) / "main.bbl"

            keys = parse_bbl_file(bbl)

        self.assertEqual(keys, ["smith2024", "doe2020", "wang2021"])

    def test_report_uses_aux_bbl_and_marks_consistency_issues(self) -> None:
        with workspace_tempdir("final-ref-report-") as base:
            root = materialize_project(
                base / "project",
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\cite{smith2024,doe2020}\n\\end{document}\n",
                    "main.aux": "\\citation{smith2024,doe2020}\n\\bibdata{ref/refs}\n",
                    "main.bbl": "\\bibitem{smith2024}\n\\bibitem{stale2022}\n",
                    "ref/refs.bib": "@article{smith2024, title={Smith}, author={A}, year={2024}}\n@article{unused2023, title={Unused}, author={B}, year={2023}}\n",
                },
            )
            project = ThesisProject.discover(root, ["main.tex"], ["*.tex"], ["ref/refs.bib"])

            report = build_final_reference_set_report(project)

        self.assertEqual(report["source"], "aux+bbl")
        self.assertEqual(report["final_keys"], ["smith2024", "stale2022"])
        self.assertEqual(report["summary"]["unused_bib_entries"], 1)
        self.assertEqual(report["summary"]["aux_only_keys"], 1)
        self.assertEqual(report["summary"]["bbl_only_keys"], 1)
        self.assertEqual(report["summary"]["missing_from_bib"], 1)
        self.assertEqual(
            [issue["code"] for issue in report["issues"]],
            ["FRS-AUX-NO-BBL", "FRS-MISSING-FROM-BIB", "FRS-UNUSED-BIB"],
        )

    def test_report_falls_back_to_tex_citations_when_aux_or_bbl_missing(self) -> None:
        with workspace_tempdir("final-ref-fallback-") as base:
            root = materialize_project(
                base / "project",
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\cite{smith2024}\n\\end{document}\n",
                    "chapter.tex": "More \\citep{doe2020}.\n",
                    "ref/refs.bib": "@article{smith2024, title={Smith}, author={A}, year={2024}}\n@article{doe2020, title={Doe}, author={B}, year={2020}}\n",
                },
            )
            project = ThesisProject.discover(root, ["main.tex"], ["*.tex"], ["ref/refs.bib"])

            report = build_final_reference_set_report(project)

        self.assertEqual(report["source"], "tex_fallback")
        self.assertEqual(report["final_keys"], ["doe2020", "smith2024"])
        self.assertEqual(report["final_reference_count"], 2)
        self.assertEqual(report["issues"], [])

    def test_report_writers_emit_json_and_csv(self) -> None:
        report = {
            "module": "final_reference_set",
            "version": "3.3",
            "summary": {"aux_citation_keys": 1},
            "final_keys": ["smith2024"],
            "issues": [
                {
                    "code": "FRS-AUX-NO-BBL",
                    "key": "smith2024",
                    "severity": "warn",
                    "message": "demo",
                }
            ],
        }
        with workspace_tempdir("final-ref-write-") as base:
            json_path = base / "project" / "reports" / "final-reference-set-report.json"
            csv_path = base / "project" / "reports" / "final-reference-set-report.csv"
            write_final_reference_set_json(report, json_path)
            write_final_reference_set_csv(report, csv_path)
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            rows = list(csv.DictReader(io.StringIO(csv_path.read_text(encoding="utf-8"))))

        self.assertEqual(payload["module"], "final_reference_set")
        self.assertEqual(rows[0]["code"], "FRS-AUX-NO-BBL")


if __name__ == "__main__":
    unittest.main()
