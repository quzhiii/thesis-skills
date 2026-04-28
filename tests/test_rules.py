from __future__ import annotations

import unittest
from pathlib import Path

from core.language_rules import get_language_rule
from core.rules import load_rule_pack
from core.yamlish import load_yaml_file
from tests.helpers import workspace_tempdir


ROOT = Path(__file__).resolve().parents[1]
PACK_ROOT = ROOT / "90-rules" / "packs"
PHASE1_LANGUAGE_RULES = {
    "cjk_latin_spacing",
    "repeated_punctuation",
    "mixed_quote_style",
    "weak_phrases",
    "bracket_mismatch",
    "quote_mismatch",
    "booktitle_mixed_style",
    "unit_spacing",
    "ellipsis_style",
    "dash_style",
    "zh_en_symbol_spacing",
    "number_range_style",
    "enum_punctuation_style",
    "connector_blacklist_simple",
    "fullwidth_halfwidth_mix",
}


class YamlishTest(unittest.TestCase):
    def test_load_nested_yaml(self) -> None:
        with workspace_tempdir("yamlish-") as tmp:
            path = tmp / "rules.yaml"
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
        pack = load_rule_pack(PACK_ROOT / "university-generic")
        self.assertEqual(pack.pack["id"], "university-generic")
        self.assertIn("project", pack.rules)
        self.assertIn("mappings", pack.mappings)
        self.assertIn("language_deep", pack.rules)
        self.assertIn("consistency", pack.rules)

    def test_phase1_language_rules_exist_in_all_packs(self) -> None:
        for pack_id in (
            "tsinghua-thesis",
            "university-generic",
            "journal-generic",
            "demo-university-thesis",
        ):
            with self.subTest(pack=pack_id):
                pack = load_rule_pack(PACK_ROOT / pack_id)
                language = pack.rules["language"]
                self.assertTrue(PHASE1_LANGUAGE_RULES.issubset(language))
                for key in PHASE1_LANGUAGE_RULES:
                    self.assertIsInstance(language[key], dict)

        university = load_rule_pack(PACK_ROOT / "university-generic").rules["language"]
        journal = load_rule_pack(PACK_ROOT / "journal-generic").rules["language"]
        self.assertTrue(university["unit_spacing"]["autofix_safe"])
        self.assertTrue(university["connector_blacklist_simple"]["patterns"])
        self.assertFalse(journal["cjk_latin_spacing"]["enabled"])
        self.assertFalse(journal["connector_blacklist_simple"]["enabled"])
        self.assertFalse(journal["fullwidth_halfwidth_mix"]["enabled"])

        university_pack = load_rule_pack(PACK_ROOT / "university-generic").rules
        self.assertTrue(university_pack["language_deep"]["connector_misuse"]["enabled"])
        self.assertIn(
            "DID",
            university_pack["language_deep"]["acronym_first_use"]["acronyms"],
        )
        self.assertTrue(university_pack["consistency"]["terminology_consistency"]["enabled"])

    def test_get_language_rule_defaults_and_patterns(self) -> None:
        rule = get_language_rule(
            {
                "connector_blacklist_simple": {
                    "enabled": True,
                    "severity": "info",
                    "autofix_safe": False,
                    "patterns": ["因此所以"],
                }
            },
            "connector_blacklist_simple",
            default_severity="warning",
        )
        self.assertTrue(rule.enabled)
        self.assertEqual(rule.severity, "info")
        self.assertEqual(rule.patterns, ("因此所以",))

        missing = get_language_rule({}, "missing_rule", default_enabled=True)
        self.assertTrue(missing.enabled)
        self.assertEqual(missing.severity, "warning")
        self.assertFalse(missing.autofix_safe)
        self.assertEqual(missing.patterns, ())


if __name__ == "__main__":
    unittest.main()
