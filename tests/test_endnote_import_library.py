from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "00-bib-endnote" / "import_library.py"
DATA = ROOT / "tests" / "data"


class TestEndNoteImportLibrary(unittest.TestCase):
    def test_dry_run_import_generates_report_without_writing_bib(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "main.tex").write_text(
                "\\documentclass{article}\n\\begin{document}\nHello\n\\end{document}\n",
                encoding="utf-8",
            )
            report_path = project_root / "reports" / "endnote-import-report.json"

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
            self.assertFalse((project_root / "ref" / "refs-import.bib").exists())

            data = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(data["summary"]["mode"], "dry-run")
            self.assertEqual(data["summary"]["source_format"], "xml")
            self.assertEqual(data["summary"]["total_refs"], 4)
            self.assertEqual(data["summary"]["rendered_refs"], 3)
            self.assertEqual(data["summary"]["deduped_refs"], 1)

    def test_dry_run_import_reuses_existing_mapping_for_matching_canonical_id(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "main.tex").write_text(
                "\\documentclass{article}\n\\begin{document}\nHello\n\\end{document}\n",
                encoding="utf-8",
            )
            mapping_path = project_root / "ref" / "citation-mapping.json"
            mapping_path.parent.mkdir(parents=True)
            mapping_path.write_text(
                json.dumps(
                    {"mappings": {"doi:10.1000/xyz": "ref009"}},
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            report_path = project_root / "reports" / "endnote-import-report.json"

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
            data = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(data["mapping_preview"]["doi:10.1000/xyz"], "ref009")

    def test_apply_mode_writes_bib_and_mapping_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "main.tex").write_text(
                "\\documentclass{article}\n\\begin{document}\nHello\n\\end{document}\n",
                encoding="utf-8",
            )

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
                    "--apply",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            bib_path = project_root / "ref" / "refs-import.bib"
            mapping_path = project_root / "ref" / "citation-mapping.json"
            self.assertTrue(bib_path.exists())
            self.assertTrue(mapping_path.exists())

            mapping_data = json.loads(mapping_path.read_text(encoding="utf-8"))
            self.assertIn("doi:10.1000/xyz", mapping_data["mappings"])
            self.assertEqual(mapping_data["mappings"]["doi:10.1000/xyz"], "ref001")

    def test_apply_mode_reuses_existing_keys_and_keeps_new_keys_stable(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "main.tex").write_text(
                "\\documentclass{article}\n\\begin{document}\nHello\n\\end{document}\n",
                encoding="utf-8",
            )
            mapping_path = project_root / "ref" / "citation-mapping.json"
            mapping_path.parent.mkdir(parents=True)
            mapping_path.write_text(
                json.dumps(
                    {
                        "mappings": {
                            "doi:10.1000/xyz": "ref009",
                            "title:legacy|2020|chen": "ref010",
                        }
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            first = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--project-root",
                    str(project_root),
                    "--input",
                    str(DATA / "sample_endnote.xml"),
                    "--format",
                    "auto",
                    "--apply",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            second = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--project-root",
                    str(project_root),
                    "--input",
                    str(DATA / "sample_endnote.xml"),
                    "--format",
                    "auto",
                    "--apply",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)

            first_mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
            self.assertEqual(first_mapping["mappings"]["doi:10.1000/xyz"], "ref009")
            self.assertEqual(
                first_mapping["mappings"]["title:fallback entry|2023|li"], "ref011"
            )
            first_new_entries = {
                key: value
                for key, value in first_mapping["mappings"].items()
                if key not in {"doi:10.1000/xyz", "title:legacy|2020|chen"}
            }

            second_mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
            second_new_entries = {
                key: value
                for key, value in second_mapping["mappings"].items()
                if key not in {"doi:10.1000/xyz", "title:legacy|2020|chen"}
            }
            self.assertEqual(first_new_entries, second_new_entries)


if __name__ == "__main__":
    unittest.main()
