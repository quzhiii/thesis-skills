from __future__ import annotations

import re

from core.citation_integrity.models import CitationNeededCandidate, CitationOccurrence, CitationWithContext


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

_SENTENCE_RE = re.compile(r"[^.!?。！？]+[.!?。！？]", re.S)
_CITATION_NEEDED_PATTERNS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("empirical_result", ("significant", "significantly", "improve", "improves", "improved", "outperform", "outperforms", "achieve", "achieves", "increase", "decrease", "reduction", "accuracy")),
    ("universal_claim", ("always", "never", "all ", "every ", "must ", "clearly", "obviously")),
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


def _line_bounds(text: str, pos: int) -> tuple[int, int]:
    start = text.rfind("\n", 0, pos) + 1
    end = text.find("\n", pos)
    if end == -1:
        end = len(text)
    return start, end


def _is_bare_citation_line(text: str, start: int, end: int) -> bool:
    line_start, line_end = _line_bounds(text, start)
    line = text[line_start:line_end].strip()
    without_citation = (line[: start - line_start] + line[end - line_start :]).strip()
    return not without_citation.strip(".;, ")


def _context_bounds(text: str, start: int, end: int) -> tuple[int, int]:
    paragraph_start = text.rfind("\n\n", 0, start)
    if paragraph_start == -1:
        paragraph_start = 0
    else:
        paragraph_start += 2

    paragraph_end = text.find("\n\n", end)
    if paragraph_end == -1:
        paragraph_end = len(text)

    sentence_start = paragraph_start
    for index in range(start - 1, paragraph_start - 1, -1):
        if text[index] in ".!?":
            sentence_start = index + 1
            break

    sentence_end = paragraph_end
    for index in range(end, paragraph_end):
        if text[index] in ".!?":
            sentence_end = index + 1
            break

    return sentence_start, sentence_end


def _strip_latex_commands(text: str) -> str:
    cleaned = _CITATION_RE.sub(" ", text)
    cleaned = re.sub(r"\\(?:begin|end)\{[^}]+\}", " ", cleaned)
    cleaned = re.sub(r"\$([^$]*)\$", r"\1", cleaned)
    previous = None
    while previous != cleaned:
        previous = cleaned
        cleaned = re.sub(r"\\[A-Za-z]+\*?(?:\[[^\]]*\])*\{([^{}]*)\}", r"\1", cleaned)
    cleaned = re.sub(r"\\[A-Za-z]+\*?(?:\[[^\]]*\])*(?:\s+)?", " ", cleaned)
    cleaned = cleaned.replace("{", "").replace("}", "")
    cleaned = re.sub(r"\s+([.,!?;:])", r"\1", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _citation_needed_claim_type(sentence: str) -> tuple[str, str] | None:
    lowered = sentence.lower()
    for claim_type, patterns in _CITATION_NEEDED_PATTERNS:
        for pattern in patterns:
            if pattern in lowered:
                return claim_type, f"uncited_{claim_type}"
    return None


def extract_citation_needed_candidates(text: str, file: str) -> list[CitationNeededCandidate]:
    candidates: list[CitationNeededCandidate] = []
    for match in _SENTENCE_RE.finditer(text):
        raw_sentence = match.group(0)
        if _CITATION_RE.search(raw_sentence):
            continue
        stripped = raw_sentence.strip()
        if not stripped or stripped.startswith(("%", "\\")):
            continue
        cleaned = _strip_latex_commands(raw_sentence)
        if len(cleaned.split()) < 6:
            continue
        claim = _citation_needed_claim_type(cleaned)
        if claim is None:
            continue
        claim_type, risk_signal = claim
        candidates.append(
            CitationNeededCandidate(
                file=file,
                line=_line_of(text, match.start()),
                sentence=cleaned,
                claim_type=claim_type,
                risk_signal=risk_signal,
            )
        )
    return candidates


def _citation_context(text: str, start: int, end: int) -> str:
    if _is_bare_citation_line(text, start, end):
        return ""
    context_start, context_end = _context_bounds(text, start, end)
    return _strip_latex_commands(text[context_start:context_end])


def extract_citation_contexts(text: str, file: str) -> list[CitationWithContext]:
    contexts: list[CitationWithContext] = []
    for match in _CITATION_RE.finditer(text):
        command = match.group("command")
        line = _line_of(text, match.start())
        keys = [item.strip() for item in match.group("keys").split(",") if item.strip()]
        context = _citation_context(text, match.start(), match.end())
        for key in keys:
            contexts.append(
                CitationWithContext(
                    key=key,
                    command=command,
                    file=file,
                    line=line,
                    context=context,
                )
            )
    return contexts
