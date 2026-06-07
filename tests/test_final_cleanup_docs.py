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
                "v3.4.1` is the current product baseline",
                "Final cleanup residue scanning",
                "23-check-final-cleanup/check_final_cleanup.py",
                "final-cleanup-report.json",
                "statistical-consistency-report.json",
                "manual-anchor-report.json",
            ],
        )

    def test_roadmap_separates_shipped_v341_work_from_next_iteration(self) -> None:
        text = (ROOT / "docs" / "roadmap.md").read_text(encoding="utf-8")
        required_snippets = [
            "The current final-audit foundation turns existing deterministic checks into clearer pre-submission deliverables.",
            "## Recent Execution Status",
            "**Build claim-citation HTML**: completed",
            "**Polish cross-report navigation**: completed",
            "**Calibrate support-risk heuristics**: completed",
            "**Harden rule-pack packaging**: completed",
            "**Run cross-release verification**: completed for the current hardening sequence",
            "Next incremental work should focus on public-surface and generated-artifact consistency before opening a new product track.",
        ]
        for snippet in required_snippets:
            self.assertIn(snippet, text, f"docs/roadmap.md missing {snippet!r}")
        self.assertNotIn(
            "The next missing product layer is a **final-audit workflow**",
            text,
        )
        self.assertNotIn(
            "Given the current repository state at `v3.4.1`, the next work should proceed in this order:",
            text,
        )


if __name__ == "__main__":
    unittest.main()
