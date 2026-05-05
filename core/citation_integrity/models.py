from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CitationOccurrence:
    key: str
    command: str
    file: str
    line: int


@dataclass(frozen=True)
class BibEntry:
    key: str
    entry_type: str
    file: str
    line: int
    fields: dict[str, str]
    body: str


@dataclass(frozen=True)
class DuplicateKeyGroup:
    key: str
    entries: list[BibEntry]
    has_conflicting_metadata: bool


@dataclass(frozen=True)
class CitationIntegrityIssue:
    code: str
    severity: str
    category: str
    message: str
    file: str
    line: int | None = None
    evidence: dict[str, object] | None = None
    suggested_action: str = ""
