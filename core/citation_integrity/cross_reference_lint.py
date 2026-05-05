from __future__ import annotations

import re

from core.citation_integrity.models import CitationIntegrityIssue


_LABEL_RE = re.compile(r"\\label\{([^}]+)\}")
_REF_RE = re.compile(r"\\(?:ref|eqref|autoref)\{([^}]+)\}")


def _line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def lint_cross_references(tex_texts: dict[str, str]) -> list[CitationIntegrityIssue]:
    labels: dict[str, tuple[str, int]] = {}
    refs: list[tuple[str, str, int]] = []
    for file, text in tex_texts.items():
        for match in _LABEL_RE.finditer(text):
            labels[match.group(1)] = (file, _line_of(text, match.start()))
        for match in _REF_RE.finditer(text):
            refs.append((match.group(1), file, _line_of(text, match.start())))

    issues: list[CitationIntegrityIssue] = []
    used = {ref for ref, _, _ in refs}
    for ref, file, line in refs:
        if ref not in labels:
            issues.append(
                CitationIntegrityIssue(
                    code="CI-MISSING-LABEL",
                    severity="WARN",
                    category="missing_label",
                    message=f"Reference target `{ref}` is not defined by a label.",
                    file=file,
                    line=line,
                    evidence={"label": ref},
                    suggested_action="Define the matching label or fix the reference key.",
                )
            )
    for label, (file, line) in sorted(labels.items()):
        if label not in used:
            issues.append(
                CitationIntegrityIssue(
                    code="CI-UNUSED-LABEL",
                    severity="WARN",
                    category="unused_label",
                    message=f"Label `{label}` is not referenced in discovered TeX files.",
                    file=file,
                    line=line,
                    evidence={"label": label},
                    suggested_action="Remove the unused label or add a reference if needed.",
                )
            )
    return issues
