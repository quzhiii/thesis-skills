from __future__ import annotations

import json
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ManifestTest(unittest.TestCase):
    def test_manifest_entries_exist_and_versions_match(self) -> None:
        manifest = json.loads((ROOT / "skills-manifest.json").read_text(encoding="utf-8"))
        pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

        self.assertEqual(manifest["version"], pyproject["project"]["version"])
        module_ids = {module["id"] for module in manifest["modules"]}
        self.assertIn("14-check-language-deep", module_ids)
        self.assertIn("24-fix-language-deep", module_ids)

        for module in manifest["modules"]:
            self.assertTrue((ROOT / module["entry"]).exists(), module["entry"])
            runner = module.get("runner")
            if isinstance(runner, str):
                self.assertTrue((ROOT / runner).exists(), runner)
            draft_runner = module.get("draft_runner")
            if isinstance(draft_runner, str):
                self.assertTrue((ROOT / draft_runner).exists(), draft_runner)


if __name__ == "__main__":
    unittest.main()
