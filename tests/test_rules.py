from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from core.rules import load_rule_pack
from core.yamlish import load_yaml_file


class YamlishTest(unittest.TestCase):
    def test_load_nested_yaml(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rules.yaml"
            path.write_text(
                """
project:
  bibliography_files:
    - ref/refs.bib
    - ref/refs-import.bib
language:
  cjk_latin_spacing:
    enabled: true
    severity: warning
  weak_phrases:
    patterns:
      - 众所周知
      - 不难看出
""".strip()
                + "\n",
                encoding="utf-8",
            )
            data = load_yaml_file(path)
        self.assertEqual(
            data["project"]["bibliography_files"][1], "ref/refs-import.bib"
        )
        self.assertTrue(data["language"]["cjk_latin_spacing"]["enabled"])
        self.assertEqual(data["language"]["weak_phrases"]["patterns"][0], "众所周知")

    def test_load_rule_pack(self) -> None:
        pack = load_rule_pack(
            Path(__file__).resolve().parents[1]
            / "90-rules"
            / "packs"
            / "university-generic"
        )
        self.assertEqual(pack.pack["id"], "university-generic")
        self.assertIn("project", pack.rules)
        self.assertIn("mappings", pack.mappings)


if __name__ == "__main__":
    unittest.main()
