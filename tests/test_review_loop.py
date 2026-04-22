from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from core.reports import write_review_artifact
from core.review_loop import split_review_actions
from tests.helpers import workspace_tempdir


ROOT = Path(__file__).resolve().parents[1]


class ReviewLoopTest(unittest.TestCase):
    def test_review_artifact_contract(self) -> None:
        with workspace_tempdir("review-loop-") as base:
            artifact = base / "artifact.json"
            write_review_artifact(
                artifact,
                artifact_type="review_package",
                summary={"revision_id": "round-1"},
                payload={"items": []},
            )
            data = json.loads(artifact.read_text(encoding="utf-8"))
        self.assertEqual(data["artifact_type"], "review_package")
        self.assertIn("summary", data)
        self.assertIn("payload", data)

    def test_selective_action_splits_todos_candidate_patches_and_blocked(self) -> None:
        with workspace_tempdir("review-loop-") as base:
            chapters = base / "chapters"
            chapters.mkdir(parents=True)
            (chapters / "01-introduction.tex").write_text("因此所以，本文继续讨论。\n", encoding="utf-8")
            items = [
                {
                    "source_ref": "comment-1",
                    "text": "Tighten local wording",
                    "category": "language",
                    "confidence": 0.95,
                    "ambiguous": False,
                    "review_required": False,
                    "file": "chapters/01-introduction.tex",
                    "line": 1,
                    "old_text": "因此所以",
                    "suggestions": ["因此"],
                    "span": {"start": 1, "end": 4},
                    "code": "REVIEW_LANGUAGE_LOCAL",
                },
                {
                    "source_ref": "comment-2",
                    "text": "Reconsider the evidence framing",
                    "category": "argument",
                    "confidence": 0.7,
                    "ambiguous": False,
                    "review_required": True,
                    "file": "chapters/01-introduction.tex",
                    "line": 1,
                    "code": "REVIEW_ARGUMENT_SCOPE",
                },
                {
                    "source_ref": "comment-3",
                    "text": "Maybe revise this",
                    "category": "review",
                    "confidence": 0.4,
                    "ambiguous": True,
                    "review_required": True,
                    "file": "chapters/01-introduction.tex",
                    "line": 1,
                    "code": "REVIEW_AMBIGUOUS",
                },
            ]
            result = split_review_actions(str(base), items)
        self.assertEqual(result["summary"]["candidate_patch_count"], 1)
        self.assertEqual(result["summary"]["todo_count"], 1)
        self.assertEqual(result["summary"]["blocked_count"], 1)

    def test_revision_summary_artifact_is_emitted_through_fix_cycle(self) -> None:
        with workspace_tempdir("review-loop-") as base:
            project_root = base / "project"
            chapters = project_root / "chapters"
            reports = project_root / "reports"
            chapters.mkdir(parents=True)
            reports.mkdir(parents=True)
            (chapters / "01-introduction.tex").write_text("因此所以，本文继续讨论。\n", encoding="utf-8")
            (reports / "review-ingest-artifact.json").write_text(
                json.dumps(
                    {
                        "artifact_type": "feedback_ingest",
                        "summary": {"normalized_count": 2},
                        "payload": {
                            "selective_action": {
                                "candidate_patches": [
                                    {
                                        "code": "REVIEW_LANGUAGE_LOCAL",
                                        "file": "chapters/01-introduction.tex",
                                        "line": 1,
                                        "span": {"start": 1, "end": 4},
                                        "old_text": "因此所以",
                                        "suggestions": ["因此"],
                                        "confidence": 0.95,
                                        "review_required": False,
                                        "ambiguous": False,
                                        "category": "language",
                                    }
                                ],
                                "todos": [
                                    {"source_ref": "todo-1", "category": "argument"}
                                ],
                                "blocked": [
                                    {"source_ref": "blocked-1", "category": "review", "review_required": True}
                                ],
                            }
                        },
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "run_fix_cycle.py"),
                    "--project-root",
                    str(project_root),
                    "--ruleset",
                    "university-generic",
                    "--apply",
                    "false",
                    "--apply-mode",
                    "safe",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            summary = json.loads((reports / "fix-summary.json").read_text(encoding="utf-8"))
        self.assertIn("review-revision", summary["steps"])
        revision = summary["steps"]["review-revision"]["summary"]
        self.assertEqual(revision["accepted_items_count"], 1)
        self.assertEqual(revision["pending_items_count"], 1)
        self.assertEqual(revision["blocked_items_count"], 1)


if __name__ == "__main__":
    unittest.main()
