from __future__ import annotations

import re
from dataclasses import dataclass


_SENTENCE_RE = re.compile(r"[^。！？!?；;]+[。！？!?；;]?")


@dataclass(frozen=True)
class SentenceSpan:
    line: int
    column_start: int
    column_end: int
    text: str


def index_sentences(text: str) -> list[SentenceSpan]:
    spans: list[SentenceSpan] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        for match in _SENTENCE_RE.finditer(line):
            raw = match.group(0)
            stripped = raw.strip()
            if not stripped:
                continue
            leading = len(raw) - len(raw.lstrip())
            trailing = len(raw) - len(raw.rstrip())
            spans.append(
                SentenceSpan(
                    line=line_no,
                    column_start=match.start() + leading + 1,
                    column_end=match.end() - trailing,
                    text=stripped,
                )
            )
    return spans


def find_sentence(
    sentences: list[SentenceSpan], line: int, column: int
) -> SentenceSpan | None:
    for sentence in sentences:
        if sentence.line != line:
            continue
        if sentence.column_start <= column <= sentence.column_end:
            return sentence
    return None
