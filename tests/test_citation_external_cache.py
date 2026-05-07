from __future__ import annotations

import unittest

from core.citation_integrity.external_cache import (
    build_cache_key,
    read_cache,
    write_cache,
)
from tests.helpers import workspace_tempdir


class CitationExternalCacheTest(unittest.TestCase):
    def test_cache_key_is_stable_for_normalized_provider_query(self) -> None:
        first = build_cache_key("CrossRef", "DOI", " 10.1000/Example ")
        second = build_cache_key("crossref", "doi", "10.1000/example")

        self.assertEqual(first, second)
        self.assertTrue(first.startswith("crossref-doi-"))

    def test_cache_file_stores_and_retrieves_payload(self) -> None:
        with workspace_tempdir("external-cache-") as tempdir:
            payload = {"source": "crossref", "candidate_count": 1}

            write_cache(tempdir, "crossref", "doi", "10.1000/example", payload)
            cache_hit = read_cache(tempdir, "crossref", "doi", "10.1000/example")

        self.assertTrue(cache_hit.hit)
        self.assertEqual(cache_hit.payload["source"], "crossref")

    def test_missing_or_unreadable_cache_returns_miss(self) -> None:
        with workspace_tempdir("external-cache-miss-") as tempdir:
            cache_miss = read_cache(tempdir, "crossref", "doi", "missing")

            broken_file = tempdir / build_cache_key("crossref", "doi", "broken")
            broken_file.write_text("not json", encoding="utf-8")
            unreadable = read_cache(tempdir, "crossref", "doi", "broken")

        self.assertFalse(cache_miss.hit)
        self.assertFalse(unreadable.hit)


if __name__ == "__main__":
    unittest.main()
