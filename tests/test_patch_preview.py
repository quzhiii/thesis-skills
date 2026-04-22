from __future__ import annotations

import unittest

from core.patches import (
    TextPatch,
    apply_patch_to_text,
    build_patch_from_finding,
    build_patch_from_review_item,
    detect_patch_conflicts,
    validate_patch_text,
)
from tests.helpers import materialize_project, workspace_tempdir


class PatchPreviewTest(unittest.TestCase):
    def test_build_patch_from_finding_generates_required_fields(self) -> None:
        with workspace_tempdir("patch-preview-") as base:
            materialize_project(
                base,
                {"chapter.tex": "因此所以，本文继续讨论。\n"},
            )
            patch, reason = build_patch_from_finding(
                base,
                {
                    "code": "LANG_DEEP_CONNECTOR_MISUSE",
                    "file": "chapter.tex",
                    "line": 1,
                    "span": {"start": 1, "end": 4},
                    "suggestions": ["因此"],
                    "confidence": 0.72,
                    "review_required": True,
                    "category": "connector_misuse",
                },
            )
        self.assertIsNone(reason)
        assert patch is not None
        self.assertEqual(patch.old_text, "因此所以")
        self.assertEqual(patch.new_text, "因此")
        self.assertEqual(
            patch.as_dict().keys(),
            {
                "file",
                "start",
                "end",
                "old_text",
                "new_text",
                "issue_code",
                "confidence",
                "review_required",
                "category",
            },
        )

    def test_detect_patch_conflicts_rejects_overlaps(self) -> None:
        with workspace_tempdir("patch-preview-") as base:
            materialize_project(base, {"chapter.tex": "因此所以，本文继续讨论。\n"})
            patches = [
                TextPatch(
                    file="chapter.tex",
                    start={"line": 1, "column": 1},
                    end={"line": 1, "column": 4},
                    old_text="因此所以",
                    new_text="因此",
                    issue_code="LANG_DEEP_CONNECTOR_MISUSE",
                    confidence=0.72,
                ),
                TextPatch(
                    file="chapter.tex",
                    start={"line": 1, "column": 3},
                    end={"line": 1, "column": 4},
                    old_text="所以",
                    new_text="因而",
                    issue_code="LANG_DEEP_CONNECTOR_MISUSE",
                    confidence=0.7,
                ),
            ]
            accepted, conflicts = detect_patch_conflicts(base, patches)
        self.assertFalse(accepted)
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0]["reason"], "overlap")

    def test_patch_validation_rejects_mismatched_old_text(self) -> None:
        patch = TextPatch(
            file="chapter.tex",
            start={"line": 1, "column": 1},
            end={"line": 1, "column": 4},
            old_text="因此所以",
            new_text="因此",
            issue_code="LANG_DEEP_CONNECTOR_MISUSE",
            confidence=0.72,
        )
        self.assertFalse(validate_patch_text("但是同时，本文继续讨论。\n", patch))
        self.assertEqual(
            apply_patch_to_text("因此所以，本文继续讨论。\n", patch),
            "因此，本文继续讨论。\n",
        )

    def test_build_patch_from_review_item_reuses_patch_safety_rules(self) -> None:
        with workspace_tempdir("patch-preview-") as base:
            materialize_project(base, {"chapter.tex": "因此所以，本文继续讨论。\n"})
            patch, reason = build_patch_from_review_item(
                base,
                {
                    "code": "REVIEW_LANGUAGE_LOCAL",
                    "file": "chapter.tex",
                    "line": 1,
                    "span": {"start": 1, "end": 4},
                    "old_text": "因此所以",
                    "suggestions": ["因此"],
                    "confidence": 0.95,
                    "review_required": False,
                    "ambiguous": False,
                    "category": "language",
                },
            )
        self.assertIsNone(reason)
        assert patch is not None
        self.assertEqual(patch.old_text, "因此所以")
        self.assertFalse(patch.review_required)


if __name__ == "__main__":
    unittest.main()
