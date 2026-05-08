from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class HallucinationRiskDocsTest(unittest.TestCase):
    def _assert_contains_all(self, relative_path: str, snippets: list[str]) -> None:
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        for snippet in snippets:
            self.assertIn(snippet, text, f"{relative_path} missing {snippet!r}")

    def test_readme_mentions_hallucination_risk(self) -> None:
        self._assert_contains_all(
            "README.md",
            [
                "hallucination-risk-report.json",
                "high-risk-references.csv",
                "hallucination_risk_score",
                "UNSUPPORTED",
                "19-check-hallucination-risk",
            ],
        )

    def test_readme_zh_mentions_hallucination_risk(self) -> None:
        self._assert_contains_all(
            "README.zh-CN.md",
            [
                "hallucination-risk-report.json",
                "high-risk-references.csv",
                "hallucination_risk_score",
                "UNSUPPORTED",
                "19-check-hallucination-risk",
            ],
        )

    def test_readme_states_no_llm_no_auto_rewrite(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertNotIn("LLM", readme.split("hallucination")[1].split("\n")[0:5])
        self.assertIn("no automatic citation rewriting", readme.lower())

    def test_examples_doc_mentions_v3_demos(self) -> None:
        self._assert_contains_all(
            "docs/examples.md",
            [
                "examples/citation-hallucination-field-mismatch/",
                "examples/citation-hallucination-fabricated/",
                "examples/citation-hallucination-chinese-unsupported/",
                "hallucination-risk-report.json",
            ],
        )

    def test_modules_doc_includes_hallucination_risk(self) -> None:
        self._assert_contains_all(
            "docs/modules.md",
            [
                "19-check-hallucination-risk",
                "hallucination-risk-report.json",
            ],
        )

    def test_roadmap_mentions_v3(self) -> None:
        self._assert_contains_all(
            "docs/roadmap.md",
            [
                "v3.0",
                "hallucination",
            ],
        )

    def test_changelog_has_v3_entry(self) -> None:
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn("v3.0.0", changelog)
        self.assertIn("hallucination", changelog.lower())


if __name__ == "__main__":
    unittest.main()
