from __future__ import annotations

import re

from core.citation_integrity.models import BibEntry, CitationIntegrityIssue


_DOI_RE = re.compile(r"^10\.\S+/\S+$", re.I)


def _issue(
    code: str,
    category: str,
    message: str,
    entry: BibEntry,
    *,
    evidence: dict[str, object] | None = None,
) -> CitationIntegrityIssue:
    return CitationIntegrityIssue(
        code=code,
        severity="WARN",
        category=category,
        message=message,
        file=entry.file,
        line=entry.line,
        evidence={"citation_key": entry.key, **(evidence or {})},
        suggested_action="Review and normalize the bibliography metadata before submission.",
    )


def _missing(entry: BibEntry, field: str) -> bool:
    return not entry.fields.get(field, "").strip()


def lint_bib_fields(entries: list[BibEntry], *, current_year: int) -> list[CitationIntegrityIssue]:
    issues: list[CitationIntegrityIssue] = []
    for entry in entries:
        if _missing(entry, "title"):
            issues.append(_issue("CI-MISSING-TITLE", "field_warning", f"Bibliography entry `{entry.key}` is missing title.", entry))
        if _missing(entry, "author"):
            issues.append(_issue("CI-MISSING-AUTHOR", "field_warning", f"Bibliography entry `{entry.key}` is missing author.", entry))

        year = entry.fields.get("year", "").strip()
        if not year:
            issues.append(_issue("CI-MISSING-YEAR", "year_format", f"Bibliography entry `{entry.key}` is missing year.", entry))
        elif not year.isdigit():
            issues.append(_issue("CI-INVALID-YEAR", "year_format", f"Bibliography entry `{entry.key}` has a non-numeric year: {year}.", entry, evidence={"year": year}))
        elif int(year) > current_year + 1:
            issues.append(_issue("CI-FUTURE-YEAR", "year_format", f"Bibliography entry `{entry.key}` has a future year: {year}.", entry, evidence={"year": year, "current_year": current_year}))

        if entry.entry_type == "article" and _missing(entry, "journal") and _missing(entry, "journaltitle"):
            issues.append(_issue("CI-MISSING-JOURNAL", "field_warning", f"Article `{entry.key}` is missing journal or journaltitle.", entry))
        if entry.entry_type == "inproceedings" and _missing(entry, "booktitle"):
            issues.append(_issue("CI-MISSING-BOOKTITLE", "field_warning", f"Inproceedings entry `{entry.key}` is missing booktitle.", entry))
        if entry.entry_type == "book" and _missing(entry, "publisher"):
            issues.append(_issue("CI-MISSING-PUBLISHER", "field_warning", f"Book entry `{entry.key}` is missing publisher.", entry))

        doi = entry.fields.get("doi", "").strip()
        if not doi:
            issues.append(_issue("CI-MISSING-DOI", "doi_format", f"Bibliography entry `{entry.key}` is missing DOI.", entry))
        elif not _DOI_RE.match(doi):
            issues.append(_issue("CI-MALFORMED-DOI", "doi_format", f"Bibliography entry `{entry.key}` has a malformed DOI: {doi}.", entry, evidence={"doi": doi}))
    return issues
