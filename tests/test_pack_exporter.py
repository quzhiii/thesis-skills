from __future__ import annotations

import json
import unittest
import zipfile
from pathlib import Path

from tests.helpers import materialize_project, workspace_tempdir


ROOT = Path(__file__).resolve().parents[1]


class PackExporterTest(unittest.TestCase):
    def test_export_rule_pack_bundle_writes_versioned_manifest_and_required_files(self) -> None:
        from core.pack_exporter import export_rule_pack_bundle

        pack_root = ROOT / "90-rules" / "packs" / "journal-generic"
        with workspace_tempdir("pack-export-") as tmp:
            output = tmp / "journal-generic.zip"

            bundle_path = export_rule_pack_bundle(pack_root, output)

            self.assertEqual(bundle_path, output)
            with zipfile.ZipFile(output, "r") as archive:
                names = set(archive.namelist())
                manifest = json.loads(archive.read("manifest.json").decode("utf-8"))

        self.assertEqual(
            names,
            {
                "manifest.json",
                "pack.yaml",
                "rules.yaml",
                "mappings.yaml",
            },
        )
        self.assertEqual(manifest["bundle_version"], 1)
        self.assertEqual(manifest["pack_id"], "journal-generic")
        self.assertEqual(manifest["required_files"], ["pack.yaml", "rules.yaml", "mappings.yaml"])

    def test_export_rule_pack_bundle_rejects_pack_that_fails_lint_before_writing(self) -> None:
        from core.pack_exporter import export_rule_pack_bundle

        with workspace_tempdir("pack-export-") as tmp:
            pack_root = materialize_project(
                tmp / "bad-pack",
                {
                    "pack.yaml": "id: bad-pack\nkind: conference\ndisplay_name: Bad Pack\nversion: 1\nprecedence: guide_over_template\nstarter: false\n",
                    "rules.yaml": "project:\n  main_tex_candidates:\n    - manuscript.tex\nreference:\n  missing_key:\n    severity: error\nlanguage:\n  cjk_latin_spacing:\n    enabled: true\n    severity: warning\n",
                    "mappings.yaml": "mappings:\n  source_styles:\n    title: Title\n",
                },
            )
            output = tmp / "bad-pack.zip"

            with self.assertRaises(ValueError):
                export_rule_pack_bundle(pack_root, output)

            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
