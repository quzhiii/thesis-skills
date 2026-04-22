from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from tests.helpers import materialize_project, workspace_tempdir


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "data" / "review_loop"
RUNNER = ROOT / "04-word-review-ingest" / "feedback_ingest.py"


class FeedbackIngestTest(unittest.TestCase):
    def test_feedback_fixture_corpus_exists(self) -> None:
        self.assertTrue((FIXTURES / "README.md").exists())
        self.assertTrue((FIXTURES / "structured-feedback.json").exists())
        self.assertTrue((FIXTURES / "ambiguous-feedback.json").exists())

    def test_feedback_ingest_emits_structured_json(self) -> None:
        with workspace_tempdir("feedback-") as base:
            project = materialize_project(
                base / "project",
                {"chapters/01-introduction.tex": "因此所以，本文继续讨论。\n"},
            )
            artifact = project / "reports" / "review-ingest-artifact.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    "--project-root",
                    str(project),
                    "--input",
                    str(FIXTURES / "structured-feedback.json"),
                    "--artifact",
                    str(artifact),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(artifact.read_text(encoding="utf-8"))
        self.assertEqual(payload["artifact_type"], "feedback_ingest")
        self.assertIn("normalized_items", payload["payload"])
        self.assertIn("selective_action", payload["payload"])

    def test_ambiguity_is_preserved_explicitly(self) -> None:
        with workspace_tempdir("feedback-") as base:
            project = materialize_project(
                base / "project",
                {"chapters/01-introduction.tex": "需要修改。\n"},
            )
            artifact = project / "reports" / "review-ingest-artifact.json"
            subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    "--project-root",
                    str(project),
                    "--input",
                    str(FIXTURES / "ambiguous-feedback.json"),
                    "--artifact",
                    str(artifact),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
            payload = json.loads(artifact.read_text(encoding="utf-8"))
        item = payload["payload"]["normalized_items"][0]
        self.assertTrue(item["ambiguous"])
        self.assertTrue(item["review_required"])


if __name__ == "__main__":
    unittest.main()
