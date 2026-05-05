from __future__ import annotations

import re

from collections import defaultdict

from core.citation_integrity.models import BibEntry, DuplicateKeyGroup


_ENTRY_RE = re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,(?P<body>.*?)(?=^@\w+\s*\{|\Z)", re.M | re.S)
_FIELD_RE = re.compile(r"(\w+)\s*=\s*(?:\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}|\"([^\"]*)\"|([^,\n]+))", re.S)


def _line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def _strip_trailing_entry_brace(body: str) -> str:
    stripped = body.strip()
    if stripped.endswith("}"):
        return stripped[:-1].rstrip()
    return stripped


def _clean_value(value: str) -> str:
    return " ".join(value.strip().strip(",").split())


def parse_bib_entries_from_text(text: str, file: str) -> list[BibEntry]:
    entries: list[BibEntry] = []
    for match in _ENTRY_RE.finditer(text):
        body = _strip_trailing_entry_brace(match.group("body"))
        fields: dict[str, str] = {}
        for field_match in _FIELD_RE.finditer(body):
            raw_value = next(
                group for group in field_match.groups()[1:] if group is not None
            )
            fields[field_match.group(1).lower()] = _clean_value(raw_value)
        entries.append(
            BibEntry(
                key=match.group(2),
                entry_type=match.group(1).lower(),
                file=file,
                line=_line_of(text, match.start()),
                fields=fields,
                body=body,
            )
        )
    return entries


def _comparable_metadata(entry: BibEntry) -> tuple[tuple[str, str], ...]:
    fields = {
        key: " ".join(value.lower().split())
        for key, value in entry.fields.items()
        if key in {"title", "author", "year", "journal", "journaltitle", "booktitle", "publisher", "doi"}
    }
    return tuple(sorted(fields.items()))


def find_duplicate_key_groups(entries: list[BibEntry]) -> list[DuplicateKeyGroup]:
    by_key: defaultdict[str, list[BibEntry]] = defaultdict(list)
    for entry in entries:
        by_key[entry.key].append(entry)

    groups: list[DuplicateKeyGroup] = []
    for key in sorted(by_key):
        group_entries = by_key[key]
        if len(group_entries) < 2:
            continue
        signatures = {_comparable_metadata(entry) for entry in group_entries}
        groups.append(
            DuplicateKeyGroup(
                key=key,
                entries=group_entries,
                has_conflicting_metadata=len(signatures) > 1,
            )
        )
    return groups
