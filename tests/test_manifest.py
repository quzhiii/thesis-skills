from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ManifestTest(unittest.TestCase):
    def test_manifest_entries_exist(self) -> None:
        manifest = json.loads(
            (ROOT / "skills-manifest.json").read_text(encoding="utf-8")
        )
        for module in manifest["modules"]:
            entry = ROOT / module["entry"]
            self.assertTrue(
                entry.exists(),
                f"Missing manifest entry: {module['id']} -> {module['entry']}",
            )


if __name__ == "__main__":
    unittest.main()
