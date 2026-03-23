from __future__ import annotations

import importlib
import unittest

from core.citation_models import CanonicalRef, PersonName


match_refs = importlib.import_module("core.match_refs")
dedupe_refs = match_refs.dedupe_refs
PotentialMatch = match_refs.PotentialMatch


class TestMatchRefs(unittest.TestCase):
    def test_dedupe_refs_merges_exact_duplicate_doi(self) -> None:
        refs = [
            CanonicalRef(
                source_system="endnote",
                source_id="1",
                canonical_id="doi:10.1000/xyz",
                entry_type="article",
                title="Deep Learning 中文",
                authors=[PersonName(family="Doe", given="Jane")],
                year="2024",
                doi="10.1000/xyz",
                isbn=None,
                issn=None,
                journal="Journal of Tests",
                booktitle=None,
                publisher=None,
                langid="chinese",
                raw={},
            ),
            CanonicalRef(
                source_system="endnote",
                source_id="4",
                canonical_id="doi:10.1000/xyz",
                entry_type="article",
                title="Deep Learning 中文 Duplicate",
                authors=[PersonName(family="Doe", given="Jane")],
                year="2024",
                doi="10.1000/xyz",
                isbn=None,
                issn=None,
                journal="Journal of Tests",
                booktitle=None,
                publisher=None,
                langid="chinese",
                raw={},
            ),
        ]

        deduped, warnings = dedupe_refs(refs)

        self.assertEqual(len(deduped), 1)
        self.assertEqual(len(warnings), 1)
        self.assertIn("duplicate doi", warnings[0].lower())

    def test_dedupe_refs_warns_high_title_similarity(self) -> None:
        """Refs without DOI but very similar titles should trigger warning."""
        refs = [
            CanonicalRef(
                source_system="endnote",
                source_id="1",
                canonical_id="title:deep learning|2024|smith",
                entry_type="article",
                title="Deep Learning for Natural Language Processing",
                authors=[PersonName(family="Smith", given="John")],
                year="2024",
                doi=None,
                isbn=None,
                issn=None,
                journal="Journal of AI",
                booktitle=None,
                publisher=None,
                langid="english",
                raw={},
            ),
            CanonicalRef(
                source_system="endnote",
                source_id="2",
                canonical_id="title:deep learning natural language processing|2024|smith",
                entry_type="article",
                title="Deep Learning for Natural Language Processing",
                authors=[PersonName(family="Smith", given="John")],
                year="2024",
                doi=None,
                isbn=None,
                issn=None,
                journal="Journal of AI",
                booktitle=None,
                publisher=None,
                langid="english",
                raw={},
            ),
        ]

        deduped, warnings = dedupe_refs(refs)

        # Both refs kept (no DOI exact match)
        self.assertEqual(len(deduped), 2)
        # But should have low-confidence warning
        self.assertEqual(len(warnings), 1)
        self.assertIn("potential duplicate", warnings[0].lower())

    def test_dedupe_refs_warns_year_and_author_match(self) -> None:
        """Refs with same year and first author but different titles should warn."""
        refs = [
            CanonicalRef(
                source_system="endnote",
                source_id="1",
                canonical_id="title:machine learning basics|2023|zhang",
                entry_type="article",
                title="Machine Learning Basics",
                authors=[PersonName(family="Zhang", given="Wei")],
                year="2023",
                doi=None,
                isbn=None,
                issn=None,
                journal="AI Review",
                booktitle=None,
                publisher=None,
                langid="english",
                raw={},
            ),
            CanonicalRef(
                source_system="endnote",
                source_id="2",
                canonical_id="title:advanced machine learning|2023|zhang",
                entry_type="article",
                title="Advanced Machine Learning Techniques",
                authors=[PersonName(family="Zhang", given="Wei")],
                year="2023",
                doi=None,
                isbn=None,
                issn=None,
                journal="AI Review",
                booktitle=None,
                publisher=None,
                langid="english",
                raw={},
            ),
        ]

        deduped, warnings = dedupe_refs(refs)

        self.assertEqual(len(deduped), 2)
        self.assertEqual(len(warnings), 1)
        self.assertIn("same year and author", warnings[0].lower())

    def test_dedupe_refs_no_warning_for_different_refs(self) -> None:
        """Completely different refs should not trigger warnings."""
        refs = [
            CanonicalRef(
                source_system="endnote",
                source_id="1",
                canonical_id="title:deep learning|2024|smith",
                entry_type="article",
                title="Deep Learning",
                authors=[PersonName(family="Smith", given="John")],
                year="2024",
                doi=None,
                isbn=None,
                issn=None,
                journal="Journal A",
                booktitle=None,
                publisher=None,
                langid="english",
                raw={},
            ),
            CanonicalRef(
                source_system="endnote",
                source_id="2",
                canonical_id="title:quantum computing|2022|johnson",
                entry_type="article",
                title="Quantum Computing",
                authors=[PersonName(family="Johnson", given="Mary")],
                year="2022",
                doi=None,
                isbn=None,
                issn=None,
                journal="Journal B",
                booktitle=None,
                publisher=None,
                langid="english",
                raw={},
            ),
        ]

        deduped, warnings = dedupe_refs(refs)

        self.assertEqual(len(deduped), 2)
        self.assertEqual(len(warnings), 0)


class TestPotentialMatch(unittest.TestCase):
    def test_potential_match_dataclass(self) -> None:
        """Test PotentialMatch dataclass structure."""
        ref1 = CanonicalRef(
            source_system="endnote",
            source_id="1",
            canonical_id="title:test|2024|doe",
            entry_type="article",
            title="Test Paper",
            authors=[PersonName(family="Doe", given="Jane")],
            year="2024",
            doi=None,
            isbn=None,
            issn=None,
            journal=None,
            booktitle=None,
            publisher=None,
            langid="english",
            raw={},
        )
        ref2 = CanonicalRef(
            source_system="endnote",
            source_id="2",
            canonical_id="title:test paper|2024|doe",
            entry_type="article",
            title="Test Paper Extended",
            authors=[PersonName(family="Doe", given="Jane")],
            year="2024",
            doi=None,
            isbn=None,
            issn=None,
            journal=None,
            booktitle=None,
            publisher=None,
            langid="english",
            raw={},
        )

        match = PotentialMatch(
            ref1=ref1,
            ref2=ref2,
            match_type="title_similarity",
            confidence=0.85,
            details="Title similarity: 85%",
        )

        self.assertEqual(match.ref1.source_id, "1")
        self.assertEqual(match.ref2.source_id, "2")
        self.assertEqual(match.match_type, "title_similarity")
        self.assertEqual(match.confidence, 0.85)


if __name__ == "__main__":
    unittest.main()
