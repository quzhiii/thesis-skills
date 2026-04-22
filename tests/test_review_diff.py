from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
