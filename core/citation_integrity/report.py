from __future__ import annotations

import json
import csv
from pathlib import Path

from core.common import Finding
from core.citation_integrity.bib_parser import find_duplicate_key_groups, parse_bib_entries_from_text
from core.citation_integrity.cross_reference_lint import lint_cross_references
from core.citation_integrity.field_lint import lint_bib_fields
from core.citation_integrity.models import BibEntry, CitationIntegrityIssue
from core.citation_integrity.tex_parser import collect_citations_from_text


def _issue_to_payload(issue: CitationIntegrityIssue) -> dict[str, object]:
    return {
        "id": issue.code,
        "code": issue.code,
        "severity": issue.severity,
        "category": issue.category,
        "message": issue.message,
        "file": issue.file,
        "line": issue.line,
        "evidence": issue.evidence or {},
        "suggested_action": issue.suggested_action,
    }


def _status(issues: list[CitationIntegrityIssue]) -> str:
    if any(issue.severity == "BLOCK" for issue in issues):
        return "BLOCK"
    if any(issue.severity == "WARN" for issue in issues):
        return "WARN"
    return "PASS"


def _missing_key_issues(cited_keys: set[str], entries: list[BibEntry], occurrences_by_key: dict[str, list[object]]) -> list[CitationIntegrityIssue]:
    bib_keys = {entry.key for entry in entries}
    issues: list[CitationIntegrityIssue] = []
    for key in sorted(cited_keys - bib_keys):
        occurrence = occurrences_by_key[key][0]
        file = getattr(occurrence, "file")
        line = getattr(occurrence, "line")
        issues.append(
            CitationIntegrityIssue(
                code="CI-MISSING-KEY",
                severity="BLOCK",
                category="missing_cited_key",
                message=f"Citation key `{key}` is cited but not found in bibliography files.",
                file=file,
                line=line,
                evidence={"citation_key": key},
                suggested_action="Add the missing bibliography entry or fix the citation key after manual confirmation.",
            )
        )
    return issues


def _unused_entry_issues(cited_keys: set[str], entries: list[BibEntry]) -> list[CitationIntegrityIssue]:
    issues: list[CitationIntegrityIssue] = []
    seen: set[str] = set()
    for entry in sorted(entries, key=lambda item: (item.key, item.file, item.line)):
        if entry.key in cited_keys or entry.key in seen:
            continue
        seen.add(entry.key)
        issues.append(
            CitationIntegrityIssue(
                code="CI-UNUSED-BIB-ENTRY",
                severity="WARN",
                category="unused_bib_entry",
                message=f"Bibliography entry `{entry.key}` is not cited in discovered TeX files.",
                file=entry.file,
                line=entry.line,
                evidence={"citation_key": entry.key},
                suggested_action="Remove unused bibliography entries or cite them if they are required.",
            )
        )
    return issues


def _duplicate_key_issues(entries: list[BibEntry]) -> list[CitationIntegrityIssue]:
    issues: list[CitationIntegrityIssue] = []
    for group in find_duplicate_key_groups(entries):
        severity = "BLOCK" if group.has_conflicting_metadata else "WARN"
        code = "CI-DUPLICATE-KEY-CONFLICT" if group.has_conflicting_metadata else "CI-DUPLICATE-KEY"
        issues.append(
            CitationIntegrityIssue(
                code=code,
                severity=severity,
                category="duplicate_key",
                message=f"Duplicate bibliography key `{group.key}` appears in multiple entries.",
                file="|".join(entry.file for entry in group.entries),
                line=group.entries[0].line,
                evidence={
                    "citation_key": group.key,
                    "conflicting_metadata": group.has_conflicting_metadata,
                    "locations": [
                        {"file": entry.file, "line": entry.line, "entry_type": entry.entry_type}
                        for entry in group.entries
                    ],
                },
                suggested_action="Merge duplicate entries or rename conflicting citation keys after manual review.",
            )
        )
    return issues


def _sort_issues(issues: list[CitationIntegrityIssue]) -> list[CitationIntegrityIssue]:
    return sorted(issues, key=lambda item: (item.code, item.file, item.line or 0, item.message))


def build_citation_integrity_report(
    tex_texts: dict[str, str],
    bib_texts: dict[str, str],
    *,
    current_year: int,
    extra_issues: list[CitationIntegrityIssue] | None = None,
) -> dict[str, object]:
    occurrences = [
        occurrence
        for file, text in tex_texts.items()
        for occurrence in collect_citations_from_text(text, file)
    ]
    entries = [
        entry
        for file, text in bib_texts.items()
        for entry in parse_bib_entries_from_text(text, file)
    ]
    cited_keys = {occurrence.key for occurrence in occurrences}
    occurrences_by_key: dict[str, list[object]] = {}
    for occurrence in occurrences:
        occurrences_by_key.setdefault(occurrence.key, []).append(occurrence)

    issues = [
        *_missing_key_issues(cited_keys, entries, occurrences_by_key),
        *_unused_entry_issues(cited_keys, entries),
        *_duplicate_key_issues(entries),
        *lint_bib_fields(entries, current_year=current_year),
        *lint_cross_references(tex_texts),
        *(extra_issues or []),
    ]
    sorted_issues = _sort_issues(issues)
    summary = {
        "tex_files": len(tex_texts),
        "bib_files": len(bib_texts),
        "cited_keys": len(cited_keys),
        "bib_entries": len(entries),
        "missing_cited_keys": sum(1 for issue in sorted_issues if issue.category == "missing_cited_key"),
        "unused_bib_entries": sum(1 for issue in sorted_issues if issue.category == "unused_bib_entry"),
        "duplicate_bib_keys": sum(1 for issue in sorted_issues if issue.category == "duplicate_key"),
        "field_warnings": sum(1 for issue in sorted_issues if issue.category == "field_warning"),
        "latex_log_warnings": sum(1 for issue in sorted_issues if issue.category == "latex_log_warning"),
        "cross_reference_warnings": sum(1 for issue in sorted_issues if issue.category in {"missing_label", "unused_label"}),
    }
    return {
        "module": "citation_integrity",
        "version": "1.1",
        "status": _status(sorted_issues),
        "summary": summary,
        "issues": [_issue_to_payload(issue) for issue in sorted_issues],
    }


def citation_integrity_findings(report: dict[str, object]) -> list[Finding]:
    issues = report.get("issues")
    if not isinstance(issues, list):
        return []
    severity_map = {"BLOCK": "error", "WARN": "warning", "INFO": "info"}
    findings: list[Finding] = []
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        severity = severity_map.get(str(issue.get("severity", "WARN")), "warning")
        raw_line = issue.get("line")
        line = raw_line if isinstance(raw_line, int) else 0
        findings.append(
            Finding(
                severity=severity,
                code=str(issue.get("code", "CI-ISSUE")),
                message=str(issue.get("message", "Citation integrity issue")),
                file=str(issue.get("file", "")),
                line=line,
                suggestion=str(issue.get("suggested_action", "Review citation integrity report.")),
                category=str(issue.get("category", "")),
                evidence=json.dumps(issue.get("evidence", {}), ensure_ascii=False, sort_keys=True),
            )
        )
    return findings


def write_citation_integrity_report(report: dict[str, object], output: str | Path) -> None:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def _issue_dicts(report: dict[str, object]) -> list[dict[str, object]]:
    issues = report.get("issues")
    if not isinstance(issues, list):
        return []
    return [issue for issue in issues if isinstance(issue, dict)]


def render_citation_integrity_markdown(report: dict[str, object]) -> str:
    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    issues = _issue_dicts(report)
    blocks = [issue for issue in issues if issue.get("severity") == "BLOCK"]
    warnings = [issue for issue in issues if issue.get("severity") == "WARN"]
    lines = [
        "# Citation Integrity Report",
        "",
        f"**Status:** {report.get('status', 'UNKNOWN')}",
        "",
        "## Summary",
        "",
    ]
    for key in sorted(summary):
        lines.append(f"- `{key}`: {summary[key]}")
    lines.extend(["", "## Blocking Issues", ""])
    if blocks:
        for issue in blocks:
            lines.append(
                f"- `{issue.get('code')}` {issue.get('file')}:{issue.get('line')} - {issue.get('message')}"
            )
    else:
        lines.append("- None")
    lines.extend(["", "## Warnings", ""])
    if warnings:
        for issue in warnings:
            lines.append(
                f"- `{issue.get('code')}` {issue.get('file')}:{issue.get('line')} - {issue.get('message')}"
            )
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Next Actions",
            "",
            "1. Resolve all BLOCK issues before submission or advisor handoff.",
            "2. Review WARN issues and decide whether they are acceptable for your ruleset.",
            "3. Re-run the checker after updating citations, bibliography files, or compile logs.",
            "",
            "V1.2 report boundary: this is a local citation-integrity report. It does not verify references against external databases and does not detect hallucinated references.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_citation_integrity_markdown(report: dict[str, object], output: str | Path) -> None:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_citation_integrity_markdown(report), encoding="utf-8")


def write_citation_integrity_csv(report: dict[str, object], output: str | Path) -> None:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["severity", "code", "category", "file", "line", "message", "suggested_action"]
    issues = sorted(
        _issue_dicts(report),
        key=lambda issue: (
            0 if issue.get("severity") == "BLOCK" else 1,
            str(issue.get("code", "")),
            str(issue.get("file", "")),
            int(issue.get("line") or 0),
        ),
    )
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for issue in issues:
            writer.writerow({key: issue.get(key, "") for key in fieldnames})
