"""Tests for Zotero extraction and citation mapping."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from core.citation_mapping import (
    CitationMapping,
    generate_citation_lock,
    parse_bib_keys,
    parse_tex_citations,
)
from core.zotero_extract import (
    ZoteroCitation,
    ZoteroExtractionResult,
    compare_citations,
    extract_zotero_citations,
)
from tests.helpers import workspace_tempdir


class TestCitationMapping(unittest.TestCase):
    """Tests for CitationMapping class."""

    def test_load_empty(self):
        """Test loading when no mapping file exists."""
        with workspace_tempdir("zotero-extract-") as tmpdir:
            mapping = CitationMapping.load(tmpdir)
            self.assertEqual(mapping.mappings, {})
            self.assertEqual(mapping.next_ref_number, 1)

    def test_load_existing(self):
        """Test loading existing mapping file."""
        with workspace_tempdir("zotero-extract-") as tmpdir:
            mapping_path = tmpdir / "ref" / "citation-mapping.json"
            mapping_path.parent.mkdir(parents=True)
            mapping_path.write_text(json.dumps({
                "mappings": {
                    "KeyA": "ref001",
                    "KeyB": "ref002"
                }
            }))

            mapping = CitationMapping.load(tmpdir)
            self.assertEqual(mapping.mappings["KeyA"], "ref001")
            self.assertEqual(mapping.mappings["KeyB"], "ref002")
            self.assertEqual(mapping.next_ref_number, 3)

    def test_get_or_create_latex_key(self):
        """Test getting or creating LaTeX keys."""
        with workspace_tempdir("zotero-extract-") as tmpdir:
            mapping = CitationMapping.load(tmpdir)

            # First key should be ref001
            key1 = mapping.get_or_create_latex_key("ZoteroA")
            self.assertEqual(key1, "ref001")

            # Same Zotero key should return same LaTeX key
            key1_again = mapping.get_or_create_latex_key("ZoteroA")
            self.assertEqual(key1_again, "ref001")

            # New Zotero key should get new LaTeX key
            key2 = mapping.get_or_create_latex_key("ZoteroB")
            self.assertEqual(key2, "ref002")

    def test_save(self):
        """Test saving mapping to file."""
        with workspace_tempdir("zotero-extract-") as tmpdir:
            mapping = CitationMapping.load(tmpdir)
            mapping.get_or_create_latex_key("ZoteroA")
            mapping.get_or_create_latex_key("ZoteroB")
            mapping.save("Test mapping")

            # Verify file was created
            mapping_path = tmpdir / "ref" / "citation-mapping.json"
            self.assertTrue(mapping_path.exists())

            # Verify content
            data = json.loads(mapping_path.read_text())
            self.assertEqual(data["mappings"]["ZoteroA"], "ref001")
            self.assertEqual(data["mappings"]["ZoteroB"], "ref002")

    def test_to_citation_lock_content(self):
        """Test generating citation-lock.tex content."""
        with workspace_tempdir("zotero-extract-") as tmpdir:
            mapping = CitationMapping.load(tmpdir)
            mapping.mappings = {
                "KeyA": "ref001",
                "KeyB": "ref002",
                "KeyC": "ref010"
            }

            content = mapping.to_citation_lock_content()
            self.assertIn("ref001", content)
            self.assertIn("ref002", content)
            self.assertIn("ref010", content)
            self.assertIn("\\nocite{", content)


class TestParseBibKeys(unittest.TestCase):
    """Tests for BibTeX key parsing."""

    def test_parse_simple(self):
        """Test parsing simple bib entries."""
        bib = """
@article{ref001,
  author = {Test Author},
  title = {Test Title}
}
@book{ref002,
  author = {Another Author}
}
"""
        keys = parse_bib_keys(bib)
        self.assertEqual(keys, {"ref001", "ref002"})

    def test_parse_empty(self):
        """Test parsing empty content."""
        keys = parse_bib_keys("")
        self.assertEqual(keys, set())


class TestParseTexCitations(unittest.TestCase):
    """Tests for LaTeX citation parsing."""

    def test_parse_single(self):
        """Test parsing single citation."""
        tex = r"Some text \cite{ref001} more text"
        citations = parse_tex_citations(tex)
        self.assertEqual(citations, ["ref001"])

    def test_parse_multiple(self):
        """Test parsing multiple citations."""
        tex = r"\cite{ref001,ref002,ref003}"
        citations = parse_tex_citations(tex)
        self.assertEqual(citations, ["ref001", "ref002", "ref003"])

    def test_parse_with_options(self):
        """Test parsing citations with options."""
        tex = r"\cite[p. 123]{ref001}"
        citations = parse_tex_citations(tex)
        self.assertEqual(citations, ["ref001"])


class TestZoteroCitation(unittest.TestCase):
    """Tests for ZoteroCitation dataclass."""

    def test_properties(self):
        """Test citation properties."""
        citation = ZoteroCitation(
            zotero_key="TestKey2020",
            item_data={
                "title": "Test Title",
                "author": [
                    {"given": "John", "family": "Doe"},
                    {"family": "Smith", "given": "Jane"}
                ],
                "issued": {"date-parts": [[2020]]},
                "type": "article-journal"
            }
        )

        self.assertEqual(citation.title, "Test Title")
        self.assertEqual(citation.authors, ["Doe John", "Smith Jane"])
        self.assertEqual(citation.year, 2020)
        self.assertEqual(citation.entry_type, "article-journal")

    def test_to_bibtex_stub(self):
        """Test generating BibTeX stub."""
        citation = ZoteroCitation(
            zotero_key="TestKey2020",
            item_data={
                "title": "Test Title",
                "author": [{"given": "John", "family": "Doe"}],
                "issued": {"date-parts": [[2020]]},
                "type": "article"
            }
        )

        stub = citation.to_bibtex_stub("ref001")
        self.assertIn("@article{ref001", stub)
        self.assertIn("Doe John", stub)
        self.assertIn("Test Title", stub)
        self.assertIn("2020", stub)


class TestCompareCitations(unittest.TestCase):
    """Tests for citation comparison."""

    def test_compare_all_new(self):
        """Test when all citations are new."""
        extraction = ZoteroExtractionResult(
            source_file=Path("test.docx"),
            citations=[
                ZoteroCitation(zotero_key="KeyA", item_data={}),
                ZoteroCitation(zotero_key="KeyB", item_data={}),
            ]
        )
        existing = {}

        result = compare_citations(extraction, existing)

        self.assertEqual(result["new_keys"], {"KeyA", "KeyB"})
        self.assertEqual(result["removed_keys"], set())
        self.assertEqual(result["unchanged_keys"], set())

    def test_compare_mixed(self):
        """Test when some citations are new, some removed."""
        extraction = ZoteroExtractionResult(
            source_file=Path("test.docx"),
            citations=[
                ZoteroCitation(zotero_key="KeyA", item_data={}),
                ZoteroCitation(zotero_key="KeyB", item_data={}),
            ]
        )
        existing = {"KeyA": "ref001", "KeyC": "ref002"}

        result = compare_citations(extraction, existing)

        self.assertEqual(result["new_keys"], {"KeyB"})
        self.assertEqual(result["removed_keys"], {"KeyC"})
        self.assertEqual(result["unchanged_keys"], {"KeyA"})


if __name__ == "__main__":
    unittest.main()
