from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from tests.helpers import workspace_tempdir


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "00-bib-endnote" / "import_library.py"
DATA = ROOT / "tests" / "data"


class TestEndNoteImportWorkflow(unittest.TestCase):
    def test_dry_run_then_apply_keeps_mapping_and_bib_stable(self) -> None:
        with workspace_tempdir("endnote-import-workflow-") as project_root:
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
            report_path = project_root / "reports" / "endnote-import-report.json"

            dry_run = subprocess.run(
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
            self.assertEqual(dry_run.returncode, 0, dry_run.stdout + dry_run.stderr)
            self.assertFalse((project_root / "ref" / "refs-import.bib").exists())

            dry_payload = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(dry_payload["summary"]["mode"], "dry-run")
            self.assertEqual(dry_payload["summary"]["deduped_refs"], 1)
            self.assertEqual(
                dry_payload["mapping_preview"]["doi:10.1000/xyz"], "ref009"
            )

            apply_first = subprocess.run(
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
                    "--report",
                    str(report_path),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                apply_first.returncode, 0, apply_first.stdout + apply_first.stderr
            )

            bib_path = project_root / "ref" / "refs-import.bib"
            self.assertTrue(bib_path.exists())
            first_bib = bib_path.read_text(encoding="utf-8")
            first_mapping = json.loads(mapping_path.read_text(encoding="utf-8"))

            self.assertIn("@article{ref009,", first_bib)
            self.assertEqual(first_mapping["mappings"]["doi:10.1000/xyz"], "ref009")
            self.assertEqual(
                first_mapping["mappings"]["title:fallback entry|2023|li"], "ref011"
            )

            apply_second = subprocess.run(
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
                    "--report",
                    str(report_path),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                apply_second.returncode, 0, apply_second.stdout + apply_second.stderr
            )

            second_bib = bib_path.read_text(encoding="utf-8")
            second_mapping = json.loads(mapping_path.read_text(encoding="utf-8"))

            self.assertEqual(first_bib, second_bib)
            self.assertEqual(first_mapping, second_mapping)


if __name__ == "__main__":
    unittest.main()
