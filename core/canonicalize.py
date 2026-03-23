from __future__ import annotations

import hashlib
import re
from dataclasses import replace

from core.citation_models import CanonicalRef, PersonName


def normalize_title(text: str) -> str:
    cleaned = re.sub(r"[{}]", " ", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip().lower()
    return cleaned


def normalize_doi(text: str | None) -> str | None:
    if not text:
        return None
    cleaned = text.strip().lower()
    cleaned = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", cleaned)
    cleaned = cleaned.replace("doi:", "")
    cleaned = re.sub(r"\s+", "", cleaned)
    return cleaned or None


def normalize_person_name(person: PersonName) -> PersonName:
    return PersonName(family=person.family.strip(), given=person.given.strip())


def guess_langid(ref: CanonicalRef) -> str | None:
    title = ref.title or ""
    if re.search(r"[\u4e00-\u9fff]", title):
        return "chinese"
    if title:
        return "english"
    return None


def normalize_entry_type(entry_type: str | None) -> str:
    value = (entry_type or "misc").strip().lower()
    mapping = {
        "journal article": "article",
        "journal": "article",
        "jour": "article",
        "conf": "inproceedings",
        "article-journal": "article",
        "book": "book",
        "conference paper": "inproceedings",
        "conference proceedings": "inproceedings",
    }
    return mapping.get(
        value,
        value
        if value
        in {
            "article",
            "book",
            "inproceedings",
            "misc",
            "online",
            "phdthesis",
            "mastersthesis",
        }
        else "misc",
    )


def build_canonical_id(ref: CanonicalRef) -> str:
    doi = normalize_doi(ref.doi)
    if doi:
        return f"doi:{doi}"

    title = normalize_title(ref.title or "")
    first_author = normalize_title(ref.authors[0].family) if ref.authors else ""
    year = (ref.year or "").strip()
    if title:
        parts = [part for part in [title, year, first_author] if part]
        if parts:
            return "title:" + "|".join(parts)

    fallback = hashlib.sha1(repr(ref.raw).encode("utf-8")).hexdigest()[:12]
    return f"hash:{fallback}"


def canonicalize_ref(ref: CanonicalRef) -> CanonicalRef:
    normalized_authors = [normalize_person_name(author) for author in ref.authors]
    normalized = replace(
        ref,
        authors=normalized_authors,
        doi=normalize_doi(ref.doi),
        entry_type=normalize_entry_type(ref.entry_type),
    )
    normalized = replace(
        normalized,
        langid=normalized.langid or guess_langid(normalized),
    )
    normalized = replace(normalized, canonical_id=build_canonical_id(normalized))
    return normalized
