from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from tests.helpers import materialize_project, workspace_tempdir


ROOT = Path(__file__).resolve().parents[1]


class PackLinterTest(unittest.TestCase):
    def test_lint_pack_passes_for_valid_minimal_pack(self) -> None:
        from core.pack_linter import lint_pack

        with workspace_tempdir("pack-lint-") as tmp:
            pack_root = materialize_project(
                tmp / "demo-pack",
                {
                    "pack.yaml": "\n".join(
                        [
                            "id: demo-pack",
                            "kind: university-thesis",
                            "display_name: Demo Pack",
                            "version: 1",
                            "precedence: guide_over_template",
                            "starter: false",
                            "",
                        ]
                    ),
                    "rules.yaml": "project:\n  main_tex_candidates:\n    - thesis.tex\nreference:\n  missing_key:\n    severity: error\nlanguage:\n  cjk_latin_spacing:\n    enabled: true\n    severity: warning\n",
                    "mappings.yaml": "mappings:\n  source_styles:\n    title: Title\n",
                },
            )

            findings = lint_pack(pack_root)

        self.assertEqual(findings, [])

    def test_lint_pack_reports_missing_required_files_and_fields(self) -> None:
        from core.pack_linter import lint_pack

        with workspace_tempdir("pack-lint-") as tmp:
            pack_root = materialize_project(
                tmp / "broken-pack",
                {
                    "pack.yaml": "\n".join(
                        [
                            "id: wrong-id",
                            "kind: university-thesis",
                            "version: 1",
                            "precedence: guide_over_template",
                            "starter: maybe",
                            "",
                        ]
                    ),
                    "rules.yaml": "project:\n  main_tex_candidates:\n    - thesis.tex\n",
                },
            )

            findings = lint_pack(pack_root)

        codes = {item.code for item in findings}
        self.assertIn("missing_required_file", codes)
        self.assertIn("missing_pack_field", codes)
        self.assertIn("pack_id_directory_mismatch", codes)
        self.assertIn("invalid_pack_field", codes)

    def test_lint_pack_reports_missing_completeness_sections(self) -> None:
        from core.pack_linter import lint_pack

        with workspace_tempdir("pack-lint-") as tmp:
            pack_root = materialize_project(
                tmp / "incomplete-pack",
                {
                    "pack.yaml": "\n".join(
                        [
                            "id: incomplete-pack",
                            "kind: journal",
                            "display_name: Incomplete Pack",
                            "version: 1",
                            "precedence: guide_over_template",
                            "starter: false",
                            "",
                        ]
                    ),
                    "rules.yaml": "project:\n  main_tex_candidates:\n    - manuscript.tex\n",
                    "mappings.yaml": "notes:\n  owner: demo\n",
                },
            )

            findings = lint_pack(pack_root)

        codes = {item.code for item in findings}
        self.assertIn("missing_rules_section", codes)
        self.assertIn("unknown_mappings_schema", codes)

    def test_lint_pack_passes_for_existing_starter_packs(self) -> None:
        from core.pack_linter import lint_pack

        pack_root = ROOT / "90-rules" / "packs"
        for pack_id in ("university-generic", "journal-generic", "tsinghua-thesis"):
            with self.subTest(pack=pack_id):
                findings = lint_pack(pack_root / pack_id)
                self.assertEqual(findings, [])

    def test_lint_pack_passes_for_concrete_non_tsinghua_example_pack(self) -> None:
        from core.pack_linter import lint_pack

        pack_root = ROOT / "90-rules" / "packs" / "demo-university-thesis"
        findings = lint_pack(pack_root)
        self.assertEqual(findings, [])

    def test_lint_pack_accepts_current_draft_mapping_shape(self) -> None:
        from core.pack_linter import lint_pack

        with workspace_tempdir("pack-lint-") as tmp:
            pack_root = materialize_project(
                tmp / "draft-shape-pack",
                {
                    "pack.yaml": "\n".join(
                        [
                            "id: draft-shape-pack",
                            "kind: university-thesis",
                            "display_name: Draft Shape Pack",
                            "version: 1",
                            "precedence: guide_over_template",
                            "starter: false",
                            "",
                        ]
                    ),
                    "rules.yaml": "project:\n  main_tex_candidates:\n    - thesis.tex\nreference:\n  missing_key:\n    severity: error\nlanguage:\n  cjk_latin_spacing:\n    enabled: true\n    severity: warning\n",
                    "mappings.yaml": "source_template_mappings:\n  Heading 1:\n    role: chapter\n    latex_command: chapter\nchapter_role_mappings:\n  chapter1:\n    role: introduction\n    target: chapters/01-introduction.tex\n",
                },
            )

            findings = lint_pack(pack_root)

        self.assertEqual(findings, [])

    def test_lint_pack_reports_unknown_mapping_shape(self) -> None:
        from core.pack_linter import lint_pack

        with workspace_tempdir("pack-lint-") as tmp:
            pack_root = materialize_project(
                tmp / "unknown-shape-pack",
                {
                    "pack.yaml": "\n".join(
                        [
                            "id: unknown-shape-pack",
                            "kind: journal",
                            "display_name: Unknown Shape Pack",
                            "version: 1",
                            "precedence: guide_over_template",
                            "starter: false",
                            "",
                        ]
                    ),
                    "rules.yaml": "project:\n  main_tex_candidates:\n    - manuscript.tex\nreference:\n  missing_key:\n    severity: error\nlanguage:\n  cjk_latin_spacing:\n    enabled: false\n    severity: warning\n",
                    "mappings.yaml": "mapping_roles:\n  title:\n    role: title\n",
                },
            )

            findings = lint_pack(pack_root)

        codes = {item.code for item in findings}
        self.assertIn("unknown_mappings_schema", codes)

    def test_lint_pack_reports_non_mapping_top_level_sections(self) -> None:
        from core.pack_linter import lint_pack

        with workspace_tempdir("pack-lint-") as tmp:
            pack_root = materialize_project(
                tmp / "bad-type-pack",
                {
                    "pack.yaml": "\n".join(
                        [
                            "id: bad-type-pack",
                            "kind: university-thesis",
                            "display_name: Bad Type Pack",
                            "version: 1",
                            "precedence: guide_over_template",
                            "starter: false",
                            "",
                        ]
                    ),
                    "rules.yaml": "project:\n  - thesis.tex\nreference:\n  missing_key:\n    severity: error\nlanguage:\n  cjk_latin_spacing:\n    enabled: true\n    severity: warning\n",
                    "mappings.yaml": "mappings:\n  source_styles:\n    title: Title\n",
                },
            )

            findings = lint_pack(pack_root)

        codes = {item.code for item in findings}
        self.assertIn("invalid_rules_section_type", codes)

    def test_lint_pack_cli_writes_fail_report(self) -> None:
        with workspace_tempdir("pack-lint-cli-") as tmp:
            pack_root = materialize_project(
                tmp / "cli-pack",
                {
                    "pack.yaml": "id: cli-pack\nkind: journal\ndisplay_name: CLI Pack\nversion: 1\nprecedence: guide_over_template\nstarter: false\n",
                    "rules.yaml": "project:\n  main_tex_candidates:\n    - manuscript.tex\n",
                },
            )
            report_path = tmp / "pack-lint-report.json"

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "90-rules" / "lint_pack.py"),
                    "--pack-path",
                    str(pack_root),
                    "--report",
                    str(report_path),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

            payload = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(result.returncode, 1)
        self.assertEqual(payload["summary"]["checker"], "lint_pack")
        self.assertEqual(payload["summary"]["status"], "FAIL")
        self.assertTrue(payload["findings"])

    def test_lint_pack_cli_writes_scorecard_summary(self) -> None:
        with workspace_tempdir("pack-lint-cli-") as tmp:
            pack_root = materialize_project(
                tmp / "scorecard-pack",
                {
                    "pack.yaml": "\n".join(
                        [
                            "id: scorecard-pack",
                            "kind: university-thesis",
                            "display_name: Scorecard Pack",
                            "version: 1",
                            "precedence: guide_over_template",
                            "starter: false",
                            "",
                        ]
                    ),
                    "rules.yaml": "project:\n  main_tex_candidates:\n    - thesis.tex\nreference:\n  missing_key:\n    severity: error\nlanguage:\n  cjk_latin_spacing:\n    enabled: true\n    severity: warning\n",
                    "mappings.yaml": "mappings:\n  source_styles:\n    title: Title\n",
                },
            )
            report_path = tmp / "pack-scorecard-report.json"

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "90-rules" / "lint_pack.py"),
                    "--pack-path",
                    str(pack_root),
                    "--report",
                    str(report_path),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

            payload = json.loads(report_path.read_text(encoding="utf-8"))

        scorecard = payload["scorecard"]
        self.assertEqual(result.returncode, 0)
        self.assertEqual(scorecard["required_files"]["status"], "PASS")
        self.assertEqual(scorecard["metadata_completeness"]["status"], "PASS")
        self.assertEqual(scorecard["baseline_completeness"]["status"], "PASS")
        self.assertEqual(scorecard["schema_consistency"]["status"], "PASS")
        self.assertEqual(scorecard["overall_status"], "PASS")
        self.assertEqual(scorecard["finding_counts"]["errors"], 0)


if __name__ == "__main__":
    unittest.main()
