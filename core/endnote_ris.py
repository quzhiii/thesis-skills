from __future__ import annotations

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


def parse_ris(path: str | Path) -> ImportResult:
    source = Path(path)
    lines = source.read_text(encoding="utf-8").splitlines()
    refs: list[CanonicalRef] = []
    warnings: list[str] = []
    current: dict[str, list[str]] = {}
    last_tag: str | None = None

    def flush_current() -> None:
        nonlocal current
        if not current:
            return
        entry_type = normalize_entry_type((current.get("TY") or ["misc"])[0])
        title = " ".join(current.get("TI") or current.get("T1") or []).strip() or None
        authors = [
            _split_person_name(value)
            for value in current.get("AU", []) + current.get("A1", [])
        ]
        year = ((current.get("PY") or current.get("Y1") or [None])[0] or "").strip()[
            :4
        ] or None
        doi = (current.get("DO") or [None])[0] or None
        journal = (current.get("JO") or current.get("JF") or [None])[0] or None
        booktitle = (current.get("T2") or [None])[0] or None
        publisher = (current.get("PB") or [None])[0] or None
        isbn = (current.get("SN") or [None])[0] or None
        langid = (current.get("LA") or [None])[0] or None
        if not title:
            warnings.append("RIS record missing title")
        refs.append(
            CanonicalRef(
                source_system="endnote",
                source_id=None,
                canonical_id="",
                entry_type=entry_type,
                title=title,
                authors=authors,
                year=year,
                doi=doi,
                isbn=isbn,
                journal=journal,
                booktitle=booktitle,
                publisher=publisher,
                langid=langid,
                raw={"ris_tags": sorted(current.keys())},
            )
        )
        current = {}

    for raw_line in lines:
        if not raw_line.strip():
            continue
        if len(raw_line) >= 6 and raw_line[2:6] == "  - ":
            tag = raw_line[:2]
            value = raw_line[6:].strip()
            last_tag = tag
            current.setdefault(tag, []).append(value)
            if tag == "ER":
                flush_current()
                last_tag = None
        elif last_tag is not None and current.get(last_tag):
            current[last_tag][-1] = (
                current[last_tag][-1] + " " + raw_line.strip()
            ).strip()

    if current:
        flush_current()

    return ImportResult(
        source_file=source, source_format="ris", refs=refs, warnings=warnings, errors=[]
    )
