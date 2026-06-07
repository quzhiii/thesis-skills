from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RulePackDocsTest(unittest.TestCase):
    def _read(self, relative_path: str) -> str:
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def _assert_contains_all(self, relative_path: str, snippets: list[str]) -> None:
        text = self._read(relative_path)
        for snippet in snippets:
            self.assertIn(snippet, text, f"{relative_path} missing {snippet!r}")

    def _assert_contains_none(self, relative_path: str, snippets: list[str]) -> None:
        text = self._read(relative_path)
        for snippet in snippets:
            self.assertNotIn(snippet, text, f"{relative_path} still contains stale wording {snippet!r}")

    def test_rule_pack_docs_describe_minimal_export_bundle_without_registry_claims(self) -> None:
        self._assert_contains_all(
            "docs/roadmap.md",
            [
                "Rule packs have local/Git/handoff workflows and a minimal versioned export bundle; there is no formal registry or publish command yet",
                "maintain the minimal versioned export bundle for sharing rule packs outside a local checkout",
            ],
        )
        self._assert_contains_all(
            "90-rules/STARTER_PACK_BASELINE.md",
            [
                "A minimal versioned export bundle exists through `90-rules/export_pack.py`.",
                "A pack registry or publish command.",
            ],
        )
        self._assert_contains_all(
            "90-rules/MIXED_PACK_WORKFLOWS.md",
            [
                "python 90-rules/export_pack.py \\",
                "--pack-path 90-rules/packs/<pack-id>",
                "--output dist/<pack-id>.zip",
                "The bundle contains:",
                "manifest.json",
                "This is still not a pack registry or publish pipeline.",
            ],
        )

        stale_snippets = [
            "there is no formal registry or versioned export bundle yet",
            "does not yet implement a dedicated pack exporter",
            "- a versioned export bundle format",
        ]
        for relative_path in [
            "docs/roadmap.md",
            "90-rules/STARTER_PACK_BASELINE.md",
            "90-rules/MIXED_PACK_WORKFLOWS.md",
        ]:
            with self.subTest(path=relative_path):
                self._assert_contains_none(relative_path, stale_snippets)


if __name__ == "__main__":
    unittest.main()
