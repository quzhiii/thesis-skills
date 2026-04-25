from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Any

from core.chapter_summary import build_chapter_summaries
from core.review_clusters import build_review_clusters
from core.review_queue import build_review_queue
from tests.helpers import materialize_project, workspace_tempdir


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "03-latex-review-diff" / "review_diff.py"


class ReviewDiffTest(unittest.TestCase):
    def test_review_package_generation(self) -> None:
        with workspace_tempdir("review-diff-") as base:
            project = materialize_project(
                base / "project",
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\input{chapters/01-introduction}\n\\end{document}\n",
                    "chapters/01-introduction.tex": "因此所以，本文继续讨论。\n",
                    "reports/check_language_deep-report.json": json.dumps(
                        {
                            "summary": {"checker": "check_language_deep"},
                            "findings": [
                                {
                                    "severity": "warning",
                                    "code": "LANG_DEEP_CONNECTOR_MISUSE",
                                    "message": "Connector chain may be redundant",
                                    "file": "chapters/01-introduction.tex",
                                    "line": 1,
                                    "review_required": True,
                                    "category": "language",
                                    "confidence": 0.88,
                                }
                            ],
                        },
                        ensure_ascii=False,
                    ),
                },
            )
            artifact = project / "reports" / "review-diff-artifact.json"
            result = subprocess.run(
                [sys.executable, str(RUNNER), "--project-root", str(project), "--artifact", str(artifact)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(artifact.read_text(encoding="utf-8"))
        self.assertEqual(payload["artifact_type"], "review_package")
        self.assertIn("revision_id", payload["summary"])
        self.assertIn("report_references", payload["payload"])
        self.assertIn("changed_scope", payload["payload"])

    def test_review_queue_logic(self) -> None:
        queue = build_review_queue(
            [
                {"severity": "warning", "review_required": True, "category": "language", "confidence": 0.7, "file": "a.tex", "line": 2},
                {"severity": "info", "review_required": False, "category": "language", "confidence": 0.4, "file": "b.tex", "line": 1},
            ]
        )
        self.assertEqual(queue[0]["priority"], "high")

    def test_review_cluster_logic(self) -> None:
        clusters = build_review_clusters(
            [
                {"category": "language", "file": "a.tex"},
                {"category": "language", "file": "b.tex"},
                {"category": "argument", "file": "c.tex"},
            ]
        )
        by_category = {item["category"]: item for item in clusters}
        self.assertEqual(by_category["language"]["affected_files_count"], 2)
        self.assertIn("recommended_action", by_category["language"])

    def test_triage_artifact_emits_queue_clusters_digest(self) -> None:
        with workspace_tempdir("review-diff-") as base:
            project = materialize_project(
                base / "project",
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\input{chapters/01-introduction}\n\\end{document}\n",
                    "chapters/01-introduction.tex": "因此所以，本文继续讨论。\n",
                    "reports/check_language_deep-report.json": json.dumps(
                        {
                            "summary": {"checker": "check_language_deep"},
                            "findings": [
                                {
                                    "severity": "warning",
                                    "code": "LANG_DEEP_CONNECTOR_MISUSE",
                                    "message": "Connector chain may be redundant",
                                    "file": "chapters/01-introduction.tex",
                                    "line": 1,
                                    "review_required": True,
                                    "category": "language",
                                    "confidence": 0.88,
                                }
                            ],
                        },
                        ensure_ascii=False,
                    ),
                },
            )
            artifact = project / "reports" / "review-diff-artifact.json"
            subprocess.run(
                [sys.executable, str(RUNNER), "--project-root", str(project), "--artifact", str(artifact)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
            payload = json.loads(artifact.read_text(encoding="utf-8"))
        self.assertIn("review_queue", payload["payload"])
        self.assertIn("review_clusters", payload["payload"])
        self.assertIn("review_digest", payload["payload"])

    def test_chapter_summaries_present_in_artifact(self) -> None:
        with workspace_tempdir("review-diff-") as base:
            project = materialize_project(
                base / "project",
                {
                    "main.tex": "\\documentclass{article}\n\\begin{document}\n\\input{chapters/01-introduction}\n\\end{document}\n",
                    "chapters/01-introduction.tex": "因此所以，本文继续讨论。\n",
                    "reports/check_language_deep-report.json": json.dumps(
                        {
                            "summary": {"checker": "check_language_deep"},
                            "findings": [
                                {
                                    "severity": "warning",
                                    "code": "LANG_DEEP_CONNECTOR_MISUSE",
                                    "message": "Connector chain may be redundant",
                                    "file": "chapters/01-introduction.tex",
                                    "line": 1,
                                    "review_required": True,
                                    "category": "language",
                                    "confidence": 0.88,
                                }
                            ],
                        },
                        ensure_ascii=False,
                    ),
                },
            )
            artifact = project / "reports" / "review-diff-artifact.json"
            subprocess.run(
                [sys.executable, str(RUNNER), "--project-root", str(project), "--artifact", str(artifact)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
            payload = json.loads(artifact.read_text(encoding="utf-8"))
        self.assertIn("chapter_summaries", payload["payload"])
        self.assertIsInstance(payload["payload"]["chapter_summaries"], list)
        self.assertEqual(len(payload["payload"]["chapter_summaries"]), 1)
        summary = payload["payload"]["chapter_summaries"][0]
        self.assertEqual(summary["chapter_file"], "chapters/01-introduction.tex")
        self.assertEqual(summary["issue_count"], 1)
        self.assertIn("language", summary["categories"])
        self.assertIn("priority_breakdown", summary)
        self.assertIn("summary_text", summary)

    def test_chapter_summary_shape_and_content(self) -> None:
        queue = build_review_queue(
            [
                {"severity": "warning", "review_required": True, "category": "language", "confidence": 0.88, "file": "chapters/01-introduction.tex", "line": 1},
                {"severity": "warning", "review_required": False, "category": "language", "confidence": 0.6, "file": "chapters/01-introduction.tex", "line": 2},
                {"severity": "error", "review_required": True, "category": "argument", "confidence": 0.95, "file": "chapters/02-related-work.tex", "line": 1},
            ]
        )
        summaries = build_chapter_summaries(queue)
        self.assertEqual(len(summaries), 2)
        by_file = {s["chapter_file"]: s for s in summaries}
        intro = by_file["chapters/01-introduction.tex"]
        self.assertEqual(intro["issue_count"], 2)
        self.assertEqual(intro["priority_breakdown"]["high"], 1)
        self.assertEqual(intro["priority_breakdown"]["medium"], 1)
        self.assertEqual(intro["priority_breakdown"]["low"], 0)
        self.assertIn("language", intro["categories"])
        related = by_file["chapters/02-related-work.tex"]
        self.assertEqual(related["issue_count"], 1)
        self.assertEqual(related["priority_breakdown"]["high"], 1)
        self.assertIn("argument", related["categories"])
        for s in summaries:
            self.assertIn("summary_text", s)
            self.assertIsInstance(s["summary_text"], str)
            self.assertTrue(s["summary_text"])


if __name__ == "__main__":
    unittest.main()
