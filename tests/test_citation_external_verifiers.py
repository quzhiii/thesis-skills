from __future__ import annotations

import io
import json
import unittest
from unittest.mock import patch

from core.citation_integrity.crossref_verifier import verify_with_crossref
from tests.helpers import workspace_tempdir


class _MockResponse(io.BytesIO):
    def __enter__(self) -> "_MockResponse":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()


def _response(payload: dict[str, object]) -> _MockResponse:
    return _MockResponse(json.dumps(payload).encode("utf-8"))


class CitationExternalVerifierTest(unittest.TestCase):
    def test_crossref_doi_lookup_success(self) -> None:
        payload = {
            "message": {
                "title": ["Example Title"],
                "DOI": "10.1000/example",
                "published-print": {"date-parts": [[2024]]},
                "container-title": ["Journal Name"],
            }
        }
        with workspace_tempdir("crossref-cache-") as cache_dir:
            with patch("urllib.request.urlopen", return_value=_response(payload)) as urlopen:
                evidence = verify_with_crossref(
                    {"title": "Example Title", "doi": "10.1000/example"}, cache_dir=cache_dir
                )

        self.assertTrue(evidence.success)
        self.assertFalse(evidence.used_cache)
        self.assertEqual(evidence.query_type, "doi")
        self.assertEqual(evidence.candidate_count, 1)
        self.assertEqual(evidence.top_candidate["title"], "Example Title")
        self.assertEqual(evidence.top_candidate["year"], 2024)
        urlopen.assert_called_once()

    def test_crossref_title_lookup_success_when_doi_absent(self) -> None:
        payload = {
            "message": {
                "items": [
                    {
                        "title": ["Title Only"],
                        "DOI": "10.1000/title",
                        "published-online": {"date-parts": [[2023]]},
                        "container-title": ["Proceedings"],
                    }
                ]
            }
        }
        with workspace_tempdir("crossref-title-cache-") as cache_dir:
            with patch("urllib.request.urlopen", return_value=_response(payload)):
                evidence = verify_with_crossref({"title": "Title Only"}, cache_dir=cache_dir)

        self.assertTrue(evidence.success)
        self.assertEqual(evidence.query_type, "title")
        self.assertEqual(evidence.query, "Title Only")
        self.assertEqual(evidence.top_candidate["doi"], "10.1000/title")

    def test_crossref_empty_result_has_no_candidate(self) -> None:
        with workspace_tempdir("crossref-empty-cache-") as cache_dir:
            with patch("urllib.request.urlopen", return_value=_response({"message": {}})):
                evidence = verify_with_crossref({"doi": "10.1000/missing"}, cache_dir=cache_dir)

        self.assertTrue(evidence.success)
        self.assertEqual(evidence.candidate_count, 0)
        self.assertIsNone(evidence.top_candidate)
        self.assertEqual(evidence.match_score, 0.0)

    def test_crossref_network_failure_returns_unavailable_evidence(self) -> None:
        with workspace_tempdir("crossref-failure-cache-") as cache_dir:
            with patch("urllib.request.urlopen", side_effect=OSError("offline")):
                evidence = verify_with_crossref({"doi": "10.1000/fail"}, cache_dir=cache_dir)

        self.assertFalse(evidence.success)
        self.assertEqual(evidence.candidate_count, 0)
        self.assertIn("offline", evidence.error)

    def test_crossref_cache_hit_skips_network(self) -> None:
        with workspace_tempdir("crossref-hit-cache-") as cache_dir:
            first = verify_with_crossref({"doi": "10.1000/cached"}, cache_dir=cache_dir)
            with patch("urllib.request.urlopen") as urlopen:
                second = verify_with_crossref({"doi": "10.1000/cached"}, cache_dir=cache_dir)

        self.assertFalse(first.success)
        self.assertTrue(second.used_cache)
        self.assertFalse(second.success)
        urlopen.assert_not_called()


if __name__ == "__main__":
    unittest.main()
