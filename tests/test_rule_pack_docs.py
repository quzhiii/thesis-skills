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
                "-> reusable rule-pack creation, linting, and export handoff",
                "starter-pack linting, baseline completeness checks, schema-consistency checks, scorecard output, and linted export bundles",
                "| Rule-pack export bundle | Stable | `90-rules/export_pack.py` |",
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

    def test_rule_pack_export_bundle_is_discoverable_from_public_docs(self) -> None:
        self._assert_contains_all(
            "README.md",
            [
                "90-rules/export_pack.py",
                "--pack-path 90-rules/packs/my-university",
                "--output dist/my-university.zip",
                "minimal versioned export bundle",
                "no formal registry or publish command",
            ],
        )
        self._assert_contains_all(
            "README.zh-CN.md",
            [
                "90-rules/export_pack.py",
                "--pack-path 90-rules/packs/my-university",
                "--output dist/my-university.zip",
                "最小版本化导出包",
                "没有正式 registry 或发布命令",
            ],
        )
        self._assert_contains_all(
            "90-rules/THESIS_RULE_PACKS.md",
            [
                "python 90-rules/export_pack.py \\",
                "--pack-path 90-rules/packs/<pack-id>",
                "--output dist/<pack-id>.zip",
                "manifest.json",
            ],
        )

    def test_rule_pack_artifact_contract_fields_are_documented(self) -> None:
        manifest_contract = "`manifest.json` records `bundle_version`, `pack_id`, `pack_version`, `pack_kind`, `display_name`, `required_files`, and `scorecard_summary`."
        lint_metadata_contract = "When required files and metadata completeness pass, the lint report summary also includes `pack_version`, `pack_kind`, and `display_name`."

        for relative_path in [
            "90-rules/THESIS_RULE_PACKS.md",
            "90-rules/MIXED_PACK_WORKFLOWS.md",
        ]:
            with self.subTest(path=relative_path):
                self._assert_contains_all(relative_path, [manifest_contract, lint_metadata_contract])

        self._assert_contains_all(
            "90-rules/STARTER_PACK_BASELINE.md",
            [
                "Export bundle manifests carry pack identity metadata and the lint scorecard summary.",
                lint_metadata_contract,
            ],
        )
        self._assert_contains_all(
            "README.md",
            [
                "The ZIP includes `manifest.json` with pack metadata and the lint scorecard summary.",
            ],
        )
        self._assert_contains_all(
            "README.zh-CN.md",
            [
                "ZIP 内的 `manifest.json` 会记录规则包元数据和 lint scorecard 摘要。",
            ],
        )
        self._assert_contains_all(
            "docs/modules.md",
            [
                "`lint_pack.py` | Validate rule-pack structure and write scorecard summaries",
                "`export_pack.py` | Export linted rule-pack handoff bundles",
            ],
        )
        self._assert_contains_none("docs/modules.md", ["`scorecard.py`"])

    def test_starter_pack_baseline_uses_current_release_contract_label(self) -> None:
        self._assert_contains_all(
            "90-rules/STARTER_PACK_BASELINE.md",
            [
                "current v3.5.0 public contract",
                "Current v3.5.0 baseline summary",
                "For the current v3.5.0 line",
            ],
        )
        self._assert_contains_none(
            "90-rules/STARTER_PACK_BASELINE.md",
            [
                "current v1.2.0 public contract",
                "Current v1.2.0 baseline summary",
                "For the current v1.2.0 line",
            ],
        )


if __name__ == "__main__":
    unittest.main()
