from __future__ import annotations

import importlib
import unittest

from core.citation_models import CanonicalRef, PersonName


canonical_ref_to_bibtex = importlib.import_module(
    "core.bib_render"
).canonical_ref_to_bibtex
render_bib_file = importlib.import_module("core.bib_render").render_bib_file


class TestBibRender(unittest.TestCase):
    def test_canonical_ref_to_bibtex_renders_stable_article_entry(self) -> None:
        ref = CanonicalRef(
            source_system="endnote",
            source_id="1",
            canonical_id="doi:10.1000/xyz",
            entry_type="article",
            title="Deep Learning 中文",
            authors=[
                PersonName(family="Doe", given="Jane"),
                PersonName(family="Smith", given="John"),
            ],
            year="2024",
            doi="10.1000/xyz",
            isbn=None,
            issn="1234-5678",
            journal="Journal of Tests",
            booktitle=None,
            publisher=None,
            langid="chinese",
            raw={},
        )

        rendered = canonical_ref_to_bibtex(ref, "ref001")

        self.assertIn("@article{ref001,", rendered)
        self.assertIn("author = {Doe, Jane and Smith, John}", rendered)
        self.assertIn("title = {Deep Learning 中文}", rendered)
        self.assertIn("journal = {Journal of Tests}", rendered)
        self.assertIn("year = {2024}", rendered)
        self.assertIn("doi = {10.1000/xyz}", rendered)
        self.assertIn("langid = {chinese}", rendered)

    def test_canonical_ref_to_bibtex_falls_back_to_misc_for_unknown_type(self) -> None:
        ref = CanonicalRef(
            source_system="endnote",
            source_id="2",
            canonical_id="title:fallback",
            entry_type="ancient-scroll",
            title="Fallback Entry",
            authors=[PersonName(family="Li", given="Lei")],
            year="2023",
            doi=None,
            isbn="978-1-23456-789-0",
            issn=None,
            journal=None,
            booktitle="Proceedings of TestConf",
            publisher="Fictional Press",
            langid=None,
            raw={},
        )

        rendered = canonical_ref_to_bibtex(ref, "ref002")

        self.assertIn("@misc{ref002,", rendered)
        self.assertIn("booktitle = {Proceedings of TestConf}", rendered)
        self.assertIn("publisher = {Fictional Press}", rendered)
        self.assertIn("isbn = {978-1-23456-789-0}", rendered)
        self.assertIn("langid = {english}", rendered)

    def test_render_bib_file_uses_mapping_order(self) -> None:
        refs = [
            CanonicalRef(
                source_system="endnote",
                source_id="b",
                canonical_id="title:b",
                entry_type="misc",
                title="Second Entry",
                authors=[PersonName(family="Li", given="Lei")],
                year="2023",
                doi=None,
                isbn=None,
                issn=None,
                journal=None,
                booktitle=None,
                publisher=None,
                langid="english",
                raw={},
            ),
            CanonicalRef(
                source_system="endnote",
                source_id="a",
                canonical_id="title:a",
                entry_type="article",
                title="First Entry",
                authors=[PersonName(family="Doe", given="Jane")],
                year="2024",
                doi="10.1000/xyz",
                isbn=None,
                issn=None,
                journal="Journal of Tests",
                booktitle=None,
                publisher=None,
                langid="english",
                raw={},
            ),
        ]
        mapping = {"title:a": "ref001", "title:b": "ref002"}

        rendered = render_bib_file(refs, mapping)

        self.assertLess(
            rendered.find("@article{ref001,"), rendered.find("@misc{ref002,")
        )


if __name__ == "__main__":
    unittest.main()
