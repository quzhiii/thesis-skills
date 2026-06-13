from __future__ import annotations

import json
import zipfile
import unittest
from pathlib import Path

from core.pack_exporter import export_pack
from tests.helpers import workspace_tempdir


class PackExporterTest(unittest.TestCase):
    def test_export_creates_zip_with_pack_files_and_manifest(self) -> None:
        with workspace_tempdir("pack-export-") as base:
            pack_dir = base / "pack"
            pack_dir.mkdir()
            (pack_dir / "pack.yaml").write_text(
                "id: test-pack\nkind: university-thesis\ndisplay_name: Test Pack\nversion: '1.0'\nprecedence: 1\nstarter: false\n",
                encoding="utf-8",
            )
            (pack_dir / "rules.yaml").write_text(
                "project:\n  main_tex_candidates:\n    - main.tex\nreference:\n  missing_key: error\nlanguage:\n  cjk_latin_spacing:\n    enabled: true\n    severity: warning\n",
                encoding="utf-8",
            )
            (pack_dir / "mappings.yaml").write_text(
                "mappings:\n  latex_roles:\n    main_tex: main.tex\n",
                encoding="utf-8",
            )
            output = base / "test-pack.zip"
            result = export_pack(pack_dir, output)

            self.assertTrue(output.exists())
            self.assertTrue(result["success"])
            self.assertIn("test-pack.zip", str(output))

            with zipfile.ZipFile(output, "r") as zf:
                names = zf.namelist()
                self.assertIn("test-pack/pack.yaml", names)
                self.assertIn("test-pack/rules.yaml", names)
                self.assertIn("test-pack/mappings.yaml", names)
                self.assertIn("manifest.json", names)
                manifest = json.loads(zf.read("manifest.json"))
                self.assertEqual(manifest["pack_id"], "test-pack")
                self.assertIn("lint_status", manifest)

    def test_export_includes_lint_report_when_available(self) -> None:
        with workspace_tempdir("pack-export-") as base:
            pack_dir = base / "pack"
            pack_dir.mkdir()
            (pack_dir / "pack.yaml").write_text(
                "id: test-pack\nkind: university-thesis\ndisplay_name: Test Pack\nversion: '1.0'\nprecedence: 1\nstarter: false\n",
                encoding="utf-8",
            )
            (pack_dir / "rules.yaml").write_text(
                "project:\n  main_tex_candidates:\n    - main.tex\nreference:\n  missing_key: error\nlanguage:\n  cjk_latin_spacing:\n    enabled: true\n    severity: warning\n",
                encoding="utf-8",
            )
            (pack_dir / "mappings.yaml").write_text(
                "mappings:\n  latex_roles:\n    main_tex: main.tex\n",
                encoding="utf-8",
            )
            lint_report = base / "lint-report.json"
            lint_report.write_text(
                json.dumps({"summary": {"status": "PASS"}, "scorecard": {"overall_status": "PASS"}}),
                encoding="utf-8",
            )
            output = base / "test-pack.zip"
            result = export_pack(pack_dir, output, lint_report=lint_report)

            self.assertTrue(result["success"])
            with zipfile.ZipFile(output, "r") as zf:
                names = zf.namelist()
                self.assertIn("test-pack/pack-lint-report.json", names)


if __name__ == "__main__":
    unittest.main()
