from __future__ import annotations

import re
from dataclasses import dataclass

from core.sentence_index import find_sentence, index_sentences


@dataclass(frozen=True)
class TextOccurrence:
    file: str
    text: str
    line: int
    span: dict[str, int]
    sentence: str


def _build_occurrence(
    file_name: str,
    lines: list[str],
    line_no: int,
    start: int,
    end: int,
    matched_text: str,
) -> TextOccurrence:
    sentences = index_sentences("\n".join(lines))
    sentence = find_sentence(sentences, line_no, start + 1)
    return TextOccurrence(
        file=file_name,
        text=matched_text,
        line=line_no,
        span={"start": start + 1, "end": end},
        sentence=sentence.text if sentence else lines[line_no - 1].strip(),
    )


def find_literal_occurrences(
    text: str, literal: str, *, file_name: str = "", ignore_case: bool = False
) -> list[TextOccurrence]:
    flags = re.IGNORECASE if ignore_case else 0
    pattern = re.compile(re.escape(literal), flags)
    lines = text.splitlines()
    occurrences: list[TextOccurrence] = []
    for line_no, line in enumerate(lines, start=1):
        for match in pattern.finditer(line):
            occurrences.append(
                _build_occurrence(
                    file_name,
                    lines,
                    line_no,
                    match.start(),
                    match.end(),
                    match.group(0),
                )
            )
    return occurrences


def find_token_occurrences(
    text: str, token: str, *, file_name: str = ""
) -> list[TextOccurrence]:
    pattern = re.compile(
        rf"(?<![A-Za-z0-9_]){re.escape(token)}(?![A-Za-z0-9_])", re.IGNORECASE
    )
    lines = text.splitlines()
    occurrences: list[TextOccurrence] = []
    for line_no, line in enumerate(lines, start=1):
        for match in pattern.finditer(line):
            occurrences.append(
                _build_occurrence(
                    file_name,
                    lines,
                    line_no,
                    match.start(),
                    match.end(),
                    match.group(0),
                )
            )
    return occurrences


def find_non_overlapping_literal_occurrences(
    text: str, literals: list[str], *, file_name: str = "", ignore_case: bool = False
) -> dict[str, list[TextOccurrence]]:
    flags = re.IGNORECASE if ignore_case else 0
    lines = text.splitlines()
    occurrences: dict[str, list[TextOccurrence]] = {literal: [] for literal in literals}
    for line_no, line in enumerate(lines, start=1):
        candidates: list[tuple[int, int, str, str]] = []
        for literal in literals:
            pattern = re.compile(re.escape(literal), flags)
            for match in pattern.finditer(line):
                candidates.append((match.start(), match.end(), literal, match.group(0)))
        candidates.sort(key=lambda item: (item[0], -(item[1] - item[0]), item[2]))
        last_end = -1
        for start, end, literal, matched_text in candidates:
            if start < last_end:
                continue
            occurrences[literal].append(
                _build_occurrence(
                    file_name,
                    lines,
                    line_no,
                    start,
                    end,
                    matched_text,
                )
            )
            last_end = end
    return occurrences
