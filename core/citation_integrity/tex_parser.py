from __future__ import annotations

import re

from core.citation_integrity.models import CitationOccurrence


_CITATION_COMMANDS = (
    "cite",
    "citep",
    "citet",
    "parencite",
    "textcite",
    "autocite",
)

_CITATION_RE = re.compile(
    r"\\(?P<command>" + "|".join(_CITATION_COMMANDS) + r")\*?"
    r"\s*(?:\[[^\]]*\]\s*){0,2}"
    r"\{(?P<keys>[^}]*)\}",
    re.S,
)


def _line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def collect_citations_from_text(text: str, file: str) -> list[CitationOccurrence]:
    occurrences: list[CitationOccurrence] = []
    for match in _CITATION_RE.finditer(text):
        command = match.group("command")
        line = _line_of(text, match.start())
        keys = [item.strip() for item in match.group("keys").split(",") if item.strip()]
        for key in keys:
            occurrences.append(CitationOccurrence(key=key, command=command, file=file, line=line))
    return occurrences
