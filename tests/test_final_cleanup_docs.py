from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class FinalCleanupDocsTest(unittest.TestCase):
    def _assert_contains_all(self, relative_path: str, snippets: list[str]) -> None:
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        for snippet in snippets:
            self.assertIn(snippet, text, f"{relative_path} missing {snippet!r}")

    def test_docs_surface_final_cleanup_checker(self) -> None:
        self._assert_contains_all(
            "docs/modules.md",
            [
                "23-check-final-cleanup",
                "final-cleanup-report.json",
                "Process residue scanning",
            ],
        )
        self._assert_contains_all(
            "docs/examples.md",
            [
                "Final cleanup checker",
                "23-check-final-cleanup/check_final_cleanup.py",
                "reports/final-cleanup-report.json",
                "statistical-consistency-report.json",
                "manual-anchor-report.json",
                "future `reports/final-audit-report.json`",
            ],
        )

    def test_readmes_mention_final_cleanup_artifact(self) -> None:
        self._assert_contains_all(
            "README.md",
            [
                "Final Cleanup Checker",
                "23-check-final-cleanup/check_final_cleanup.py",
                "reports/final-cleanup-report.json",
                "reports/statistical-consistency-report.json",
                "reports/manual-anchor-report.json",
            ],
        )
        self._assert_contains_all(
            "README.zh-CN.md",
            [
                "23-check-final-cleanup/check_final_cleanup.py",
                "25-check-statistical-consistency/check_statistical_consistency.py",
                "26-check-manual-anchor/check_manual_anchor.py",
                "reports/final-cleanup-report.json",
                "不自动删除、不改写正文",
            ],
        )

    def test_roadmap_marks_foundation_without_major_bump(self) -> None:
        self._assert_contains_all(
            "docs/roadmap.md",
            [
                "v3.3.0` is the current product baseline",
                "Final cleanup residue scanning",
                "23-check-final-cleanup/check_final_cleanup.py",
                "final-cleanup-report.json",
                "statistical-consistency-report.json",
                "manual-anchor-report.json",
            ],
        )


if __name__ == "__main__":
    unittest.main()
