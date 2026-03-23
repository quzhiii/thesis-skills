from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from core.canonicalize import normalize_entry_type
from core.citation_models import CanonicalRef, ImportResult, PersonName


def _split_person_name(value: str) -> PersonName:
    if "," in value:
        family, given = [part.strip() for part in value.split(",", 1)]
        return PersonName(family=family, given=given)
    parts = value.strip().split()
    if not parts:
        return PersonName()
    if len(parts) == 1:
        return PersonName(family=parts[0])
    return PersonName(family=parts[-1], given=" ".join(parts[:-1]))


def parse_endnote_xml(path: str | Path) -> ImportResult:
    source = Path(path)
    root = ET.parse(source).getroot()
    refs: list[CanonicalRef] = []
    warnings: list[str] = []

    for record in root.findall(".//record"):
        source_id = record.findtext("rec-number")
        ref_type = record.find("ref-type")
        entry_type = normalize_entry_type(
            ref_type.get("name") if ref_type is not None else None
        )
        title = record.findtext("titles/title")
        year = record.findtext("dates/year")
        doi = record.findtext("urls/related-urls/url")
        journal = record.findtext("periodical/full-title")
        booktitle = record.findtext("secondary-title")
        publisher = record.findtext("publisher")
        isbn = record.findtext("isbn")
        issn = record.findtext("issn")
        author_nodes = record.findall("contributors/authors/author")
        authors = [
            _split_person_name(node.text or "")
            for node in author_nodes
            if (node.text or "").strip()
        ]

        if not title:
            warnings.append(f"Record {source_id or '?'} missing title")

        refs.append(
            CanonicalRef(
                source_system="endnote",
                source_id=source_id,
                canonical_id="",
                entry_type=entry_type,
                title=title,
                authors=authors,
                year=year,
                doi=doi,
                isbn=isbn,
                issn=issn,
                journal=journal,
                booktitle=booktitle,
                publisher=publisher,
                raw={"xml_tag": "record"},
            )
        )

    return ImportResult(
        source_file=source, source_format="xml", refs=refs, warnings=warnings, errors=[]
    )
