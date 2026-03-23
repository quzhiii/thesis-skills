from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class PersonName:
    family: str = ""
    given: str = ""


@dataclass
class CanonicalRef:
    source_system: str
    source_id: str | None
    canonical_id: str
    entry_type: str
    title: str | None
    authors: list[PersonName] = field(default_factory=list)
    year: str | None = None
    doi: str | None = None
    isbn: str | None = None
    issn: str | None = None
    journal: str | None = None
    booktitle: str | None = None
    publisher: str | None = None
    langid: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class ImportResult:
    source_file: Path
    source_format: str
    refs: list[CanonicalRef] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
