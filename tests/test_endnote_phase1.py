from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from core.canonicalize import (
    build_canonical_id,
    canonicalize_ref,
    normalize_doi,
    normalize_title,
)
from core.citation_models import CanonicalRef, ImportResult, PersonName
from core.endnote_ris import parse_ris
from core.endnote_xml import parse_endnote_xml


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "tests" / "data"


class TestCitationModels(unittest.TestCase):
    def test_person_name_defaults(self) -> None:
        person = PersonName()
        self.assertEqual(person.family, "")
        self.assertEqual(person.given, "")

    def test_import_result_records_metadata(self) -> None:
        result = ImportResult(
            source_file=Path("sample.xml"),
            source_format="xml",
            refs=[],
            warnings=["warn"],
            errors=[],
        )
        self.assertEqual(result.source_file.name, "sample.xml")
        self.assertEqual(result.source_format, "xml")
        self.assertEqual(result.warnings, ["warn"])


class TestCanonicalize(unittest.TestCase):
    def test_normalize_doi_strips_prefix_and_spaces(self) -> None:
        self.assertEqual(
            normalize_doi(" https://doi.org/10.1000/ABC 123 "), "10.1000/abc123"
        )

    def test_normalize_title_collapses_whitespace_and_braces(self) -> None:
        self.assertEqual(normalize_title("  {Deep}   Learning  "), "deep learning")

    def test_build_canonical_id_prefers_doi(self) -> None:
        ref = CanonicalRef(
            source_system="endnote",
            source_id="1",
            canonical_id="",
            entry_type="article",
            title="Example Title",
            authors=[PersonName(family="Doe", given="Jane")],
            year="2024",
            doi="10.1000/xyz",
            isbn=None,
            issn=None,
            journal=None,
            booktitle=None,
            publisher=None,
            langid=None,
            raw={},
        )
        self.assertEqual(build_canonical_id(ref), "doi:10.1000/xyz")

    def test_build_canonical_id_falls_back_to_title_year_author(self) -> None:
        ref = CanonicalRef(
            source_system="endnote",
            source_id="3",
            canonical_id="",
            entry_type="misc",
            title="Fallback Entry",
            authors=[PersonName(family="Li", given="Lei")],
            year="2023",
            doi=None,
            isbn=None,
            issn=None,
            journal=None,
            booktitle=None,
            publisher=None,
            langid=None,
            raw={},
        )
        self.assertEqual(build_canonical_id(ref), "title:fallback entry|2023|li")

    def test_build_canonical_id_falls_back_to_hash_when_title_missing(self) -> None:
        ref = CanonicalRef(
            source_system="endnote",
            source_id="4",
            canonical_id="",
            entry_type="misc",
            title=None,
            authors=[],
            year=None,
            doi=None,
            isbn=None,
            issn=None,
            journal=None,
            booktitle=None,
            publisher=None,
            langid=None,
            raw={"source": "fallback"},
        )
        self.assertTrue(build_canonical_id(ref).startswith("hash:"))

    def test_canonicalize_ref_normalizes_key_fields(self) -> None:
        ref = CanonicalRef(
            source_system="endnote",
            source_id="2",
            canonical_id="",
            entry_type="Journal Article",
            title=" {中文}  Title ",
            authors=[PersonName(family="Li", given="Lei")],
            year="2023",
            doi="https://doi.org/10.1000/ABC",
            isbn=None,
            issn=None,
            journal=None,
            booktitle=None,
            publisher=None,
            langid=None,
            raw={},
        )
        normalized = canonicalize_ref(ref)
        self.assertEqual(normalized.entry_type, "article")
        self.assertEqual(normalized.doi, "10.1000/abc")
        self.assertEqual(normalized.langid, "chinese")
        self.assertEqual(normalized.canonical_id, "doi:10.1000/abc")


class TestEndNoteXmlParser(unittest.TestCase):
    def test_parse_endnote_xml_extracts_basic_fields(self) -> None:
        result = parse_endnote_xml(DATA / "sample_endnote.xml")

        self.assertEqual(result.source_format, "xml")
        self.assertEqual(len(result.refs), 4)
        ref = result.refs[0]
        self.assertEqual(ref.source_id, "1")
        self.assertEqual(ref.entry_type, "article")
        self.assertEqual(ref.title, "Deep Learning 中文")
        self.assertEqual([author.family for author in ref.authors], ["Doe", "Smith"])
        self.assertEqual(ref.year, "2024")
        self.assertEqual(ref.doi, "https://doi.org/10.1000/xyz")

    def test_parse_endnote_xml_unknown_type_falls_back_to_misc(self) -> None:
        result = parse_endnote_xml(DATA / "sample_endnote.xml")
        ref = result.refs[1]
        self.assertEqual(ref.entry_type, "misc")
        self.assertEqual(ref.doi, None)

    def test_parse_endnote_xml_extracts_booktitle_publisher_and_identifiers(
        self,
    ) -> None:
        result = parse_endnote_xml(DATA / "sample_endnote.xml")
        ref = result.refs[2]
        self.assertEqual(ref.entry_type, "inproceedings")
        self.assertEqual(ref.booktitle, "Proceedings of TestConf")
        self.assertEqual(ref.publisher, "Fictional Press")
        self.assertEqual(ref.isbn, "978-1-23456-789-0")
        self.assertEqual(ref.issn, "1234-5678")

    def test_parse_endnote_xml_emits_warning_for_missing_title(self) -> None:
        result = parse_endnote_xml(DATA / "sample_endnote.xml")
        self.assertTrue(
            any("missing title" in warning.lower() for warning in result.warnings)
        )


class TestRisParser(unittest.TestCase):
    def test_parse_ris_extracts_basic_fields_and_multiline_title(self) -> None:
        result = parse_ris(DATA / "sample_endnote.ris")

        self.assertEqual(result.source_format, "ris")
        self.assertEqual(len(result.refs), 3)
        ref = result.refs[0]
        self.assertEqual(ref.entry_type, "article")
        self.assertEqual(ref.title, "Deep Learning in Practice")
        self.assertEqual(len(ref.authors), 2)
        self.assertEqual(ref.year, "2024")
        self.assertEqual(ref.doi, "10.1000/xyz")

    def test_parse_ris_unknown_type_falls_back_to_misc(self) -> None:
        result = parse_ris(DATA / "sample_endnote.ris")
        ref = result.refs[1]
        self.assertEqual(ref.entry_type, "misc")
        self.assertEqual(ref.title, "Fallback Entry")

    def test_parse_ris_extracts_secondary_fields_and_language(self) -> None:
        result = parse_ris(DATA / "sample_endnote.ris")
        ref = result.refs[2]
        self.assertEqual(ref.entry_type, "inproceedings")
        self.assertEqual(ref.booktitle, "Proceedings of TestConf")
        self.assertEqual(ref.publisher, "Fictional Press")
        self.assertEqual(ref.isbn, "978-1-23456-789-0")
        self.assertEqual(ref.langid, "zh")

    def test_parse_ris_emits_warning_for_missing_title(self) -> None:
        result = parse_ris(DATA / "sample_endnote.ris")
        self.assertTrue(
            any("missing title" in warning.lower() for warning in result.warnings)
        )


if __name__ == "__main__":
    unittest.main()
