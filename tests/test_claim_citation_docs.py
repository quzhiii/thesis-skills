from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ClaimCitationDocsTest(unittest.TestCase):
    def _assert_contains_all(self, relative_path: str, snippets: list[str]) -> None:
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        for snippet in snippets:
            self.assertIn(snippet, text, f"{relative_path} missing {snippet!r}")

    def test_readme_mentions_claim_citation_triage(self) -> None:
        self._assert_contains_all(
            "README.md",
            [
                "claim-citation-triage-report.json",
                "Claim-Citation Support Triage",
                "WELL_SUPPORTED",
                "UNVERIFIABLE",
                "20-check-claim-citation",
            ],
        )

    def test_readme_zh_mentions_claim_citation_triage(self) -> None:
        self._assert_contains_all(
            "README.zh-CN.md",
            [
                "claim-citation-triage-report.json",
                "声明-引用支撑分级",
                "20-check-claim-citation",
            ],
        )

    def test_changelog_mentions_v3_1(self) -> None:
        self._assert_contains_all(
            "CHANGELOG.md",
            [
                "v3.1.0",
                "20-check-claim-citation",
                "claim-citation-triage-report.json",
                "WELL_SUPPORTED",
            ],
        )

    def test_modules_doc_mentions_claim_citation(self) -> None:
        self._assert_contains_all(
            "docs/modules.md",
            [
                "20-check-claim-citation",
                "Claim-citation support triage",
                "claim-citation",
            ],
        )

    def test_examples_doc_mentions_claim_citation_demos(self) -> None:
        self._assert_contains_all(
            "docs/examples.md",
            [
                "examples/claim-citation-mixed/",
                "examples/claim-citation-orphaned/",
                "examples/claim-citation-chinese/",
                "claim-citation-triage-report.json",
            ],
        )

    def test_roadmap_mentions_v3_1(self) -> None:
        self._assert_contains_all(
            "docs/roadmap.md",
            [
                "v3.1.0",
                "20-check-claim-citation",
                "Claim-citation support triage",
                "claim-citation-triage-report.json",
            ],
        )

    def test_pyproject_toml_is_3_4_0(self) -> None:
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('version = "3.4.0"', pyproject)

    def test_manifest_has_claim_citation_module(self) -> None:
        import json
        manifest = json.loads((ROOT / "skills-manifest.json").read_text(encoding="utf-8"))
        modules = manifest.get("modules")
        self.assertIsInstance(modules, list)
        ids = [m["id"] for m in modules if isinstance(m, dict)]
        self.assertIn("20-check-claim-citation", ids)
        self.assertEqual(manifest.get("version"), "3.4.0")


if __name__ == "__main__":
    unittest.main()
