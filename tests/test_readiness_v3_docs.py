from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ReadinessV3DocsTest(unittest.TestCase):
    def _assert_contains_all(self, relative_path: str, snippets: list[str]) -> None:
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        for snippet in snippets:
            self.assertIn(snippet, text, f"{relative_path} missing {snippet!r}")

    def test_readme_mentions_v3_3_integration(self) -> None:
        self._assert_contains_all(
            "README.md",
            [
                "Readiness Gate Integration",
                "hallucination_risk",
                "claim_citation",
                "run_evidence_pipeline.py",
                "v3.3.0",
                "final-reference-set-report.json",
            ],
        )

    def test_readme_zh_mentions_v3_3_integration(self) -> None:
        self._assert_contains_all(
            "README.zh-CN.md",
            [
                "Readiness Gate 集成",
                "run_evidence_pipeline.py",
                "一键跑完四层引用证据流水线",
                "final-reference-set-report.json",
            ],
        )

    def test_changelog_mentions_v3_3(self) -> None:
        self._assert_contains_all(
            "CHANGELOG.md",
            [
                "v3.3.0",
                "run_evidence_pipeline.py",
                "final reference set",
            ],
        )

    def test_roadmap_mentions_v3_3(self) -> None:
        self._assert_contains_all(
            "docs/roadmap.md",
            [
                "v3.3.0",
                "run_evidence_pipeline.py",
                "final reference set",
            ],
        )

    def test_modules_doc_has_evidence_pipeline(self) -> None:
        self._assert_contains_all(
            "docs/modules.md",
            ["run_evidence_pipeline.py"],
        )

    def test_examples_doc_has_pipeline_demo(self) -> None:
        self._assert_contains_all(
            "docs/examples.md",
            [
                "run_evidence_pipeline.py",
                "Unified Evidence Pipeline",
                "final-reference-set-report.json",
            ],
        )

    def test_pyproject_is_3_3_0(self) -> None:
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('version = "3.3.0"', pyproject)


if __name__ == "__main__":
    unittest.main()
