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
            ],
        )

    def test_examples_describe_final_cleanup_as_current_final_audit_input(self) -> None:
        self._assert_contains_all(
            "docs/examples.md",
            [
                "The JSON report can be aggregated as the `final_cleanup` section of `reports/final-audit-report.json`",
                "rendered through the current static HTML report surfaces as issue cards grouped by risk level",
            ],
        )
        examples = (ROOT / "docs" / "examples.md").read_text(encoding="utf-8")
        self.assertNotIn("future `reports/final-audit-report.json`", examples)
        self.assertNotIn("intended to become the `final_cleanup` section", examples)
        self.assertNotIn("rendered later as static HTML issue cards", examples)

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

    def test_readmes_describe_final_cleanup_as_current_final_audit_input(self) -> None:
        self._assert_contains_all(
            "README.md",
            [
                "The final-audit workflow can aggregate this JSON into `reports/final-audit-report.json`",
                "render it through `reports/final-audit-report.html` and the local report index",
            ],
        )
        self._assert_contains_all(
            "README.zh-CN.md",
            [
                "当前终稿审计流程可以把这个 JSON artifact 并入 `reports/final-audit-report.json`",
                "再通过 `reports/final-audit-report.html` 和本地报告索引展示",
            ],
        )

        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        readme_zh = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
        self.assertNotIn("folded later into", readme)
        self.assertNotIn("后续可以并入", readme_zh)

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
