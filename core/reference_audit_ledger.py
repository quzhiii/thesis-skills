from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

from core.citation_integrity.bib_parser import parse_bib_entries_from_text
from core.project import ThesisProject


LEDGER_FIELDS = [
    "key",
    "title",
    "authors",
    "year",
    "venue",
    "doi",
    "scope",
    "source_checked",
    "status",
    "issue",
    "action_suggested",
]


@dataclass
class ReferenceLedgerRow:
    key: str
    title: str = ""
    authors: str = ""
    year: str = ""
    venue: str = ""
    doi: str = ""
    scope: str = "bibliography"
    source_checked: str = "local_bib"
    status: str = "present"
    issue: str = ""
    action_suggested: str = ""

    def to_dict(self) -> dict[str, str]:
        return {field: str(getattr(self, field)) for field in LEDGER_FIELDS}


def _load_json(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def _entry_venue(fields: dict[str, str]) -> str:
    for key in ("journal", "journaltitle", "booktitle", "publisher", "school", "institution"):
        if fields.get(key):
            return fields[key]
    return ""


def _base_rows_from_bib(project: ThesisProject) -> dict[str, ReferenceLedgerRow]:
    rows: dict[str, ReferenceLedgerRow] = {}
    for bib_file in project.bibliography_files:
        if not bib_file.exists():
            continue
        rel = project.rel(bib_file)
        entries = parse_bib_entries_from_text(
            bib_file.read_text(encoding="utf-8", errors="ignore"),
            rel,
        )
        for entry in entries:
            fields = entry.fields
            rows.setdefault(
                entry.key,
                ReferenceLedgerRow(
                    key=entry.key,
                    title=fields.get("title", ""),
                    authors=fields.get("author", ""),
                    year=fields.get("year", ""),
                    venue=_entry_venue(fields),
                    doi=fields.get("doi", ""),
                    scope="bibliography",
                    source_checked="local_bib",
                    status="present",
                    issue="",
                    action_suggested="Review only if other evidence flags this entry.",
                ),
            )
    return rows


def _metadata_from_payload(payload: dict[str, object]) -> dict[str, str]:
    meta = payload.get("local_metadata")
    if not isinstance(meta, dict):
        meta = payload
    return {
        "title": str(meta.get("title", "")),
        "authors": str(meta.get("author", meta.get("authors", ""))),
        "year": str(meta.get("year", "")),
        "venue": str(meta.get("journal", meta.get("venue", meta.get("container_title", "")))),
        "doi": str(meta.get("doi", "")),
    }


def _seed_row(rows: dict[str, ReferenceLedgerRow], key: str, payload: dict[str, object] | None = None) -> ReferenceLedgerRow:
    if key not in rows:
        meta = _metadata_from_payload(payload or {})
        rows[key] = ReferenceLedgerRow(key=key, **meta)
    return rows[key]


def _append_row(rows: list[ReferenceLedgerRow], base: ReferenceLedgerRow, **updates: str) -> None:
    row = ReferenceLedgerRow(**base.to_dict())
    for key, value in updates.items():
        setattr(row, key, value)
    rows.append(row)


def _issue_key(issue: dict[str, object]) -> str:
    evidence = issue.get("evidence")
    if isinstance(evidence, dict):
        key = evidence.get("citation_key") or evidence.get("key")
        if isinstance(key, str) and key:
            return key
    key = issue.get("key") or issue.get("citation_key")
    if isinstance(key, str):
        return key
    return ""


def _apply_citation_integrity(project: ThesisProject, base_rows: dict[str, ReferenceLedgerRow], rows: list[ReferenceLedgerRow]) -> None:
    report = _load_json(project.reports_dir / "citation-integrity-report.json")
    if not report:
        return
    issues = report.get("issues")
    if not isinstance(issues, list):
        return
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        key = _issue_key(issue) or ""
        base = _seed_row(base_rows, key) if key else ReferenceLedgerRow(key="")
        _append_row(
            rows,
            base,
            scope="local_citation_integrity",
            source_checked="citation-integrity-report.json",
            status=str(issue.get("severity", "WARN")),
            issue=str(issue.get("message", issue.get("code", "Citation integrity issue"))),
            action_suggested=str(issue.get("suggested_action", "Review citation integrity issue manually.")),
        )


def _apply_final_reference_set(project: ThesisProject, base_rows: dict[str, ReferenceLedgerRow], rows: list[ReferenceLedgerRow]) -> None:
    report = _load_json(project.reports_dir / "final-reference-set-report.json")
    if not report:
        return
    final_keys = report.get("final_keys")
    if isinstance(final_keys, list):
        for key in final_keys:
            if not isinstance(key, str):
                continue
            base = _seed_row(base_rows, key)
            _append_row(
                rows,
                base,
                scope="final_reference_set",
                source_checked="final-reference-set-report.json",
                status="included_final",
                issue="Reference appears in final compiled/reference-set scope.",
                action_suggested="Use this row as final-scope reference evidence.",
            )
    issues = report.get("issues")
    if isinstance(issues, list):
        for issue in issues:
            if not isinstance(issue, dict):
                continue
            key = str(issue.get("key", ""))
            base = _seed_row(base_rows, key)
            _append_row(
                rows,
                base,
                scope="final_reference_set",
                source_checked="final-reference-set-report.json",
                status=str(issue.get("severity", "warn")),
                issue=str(issue.get("message", issue.get("code", "Final reference set issue"))),
                action_suggested="Review final reference set issue before submission.",
            )


def _apply_external_verification(project: ThesisProject, base_rows: dict[str, ReferenceLedgerRow], rows: list[ReferenceLedgerRow]) -> None:
    report = _load_json(project.reports_dir / "external-verification-report.json")
    if not report:
        return
    entries = report.get("entries")
    if not isinstance(entries, list):
        return
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        key = str(entry.get("citation_key", ""))
        base = _seed_row(base_rows, key, entry)
        status = str(entry.get("match_status", "UNKNOWN"))
        _append_row(
            rows,
            base,
            scope="external_metadata",
            source_checked="external-verification-report.json",
            status=status,
            issue=f"External verification status: {status}",
            action_suggested=str(entry.get("recommended_action", "Review external verification evidence manually.")),
        )


def _apply_doi_candidates(project: ThesisProject, base_rows: dict[str, ReferenceLedgerRow], rows: list[ReferenceLedgerRow]) -> None:
    report = _load_json(project.reports_dir / "missing-doi-candidates.json")
    if not report:
        return
    entries = report.get("entries")
    if not isinstance(entries, list):
        return
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        key = str(entry.get("citation_key", ""))
        base = _seed_row(base_rows, key)
        _append_row(
            rows,
            base,
            doi=base.doi or str(entry.get("candidate_doi", "")),
            scope="doi_candidate",
            source_checked="missing-doi-candidates.json",
            status="candidate",
            issue=f"Candidate DOI: {entry.get('candidate_doi', '')}",
            action_suggested=str(entry.get("recommended_action", "Verify candidate DOI manually before editing BibTeX.")),
        )


def _apply_url_verification(project: ThesisProject, base_rows: dict[str, ReferenceLedgerRow], rows: list[ReferenceLedgerRow]) -> None:
    report = _load_json(project.reports_dir / "url-verification-report.json")
    if not report:
        return
    entries = report.get("entries")
    if not isinstance(entries, list):
        return
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        key = str(entry.get("citation_key", ""))
        base = _seed_row(base_rows, key)
        status = str(entry.get("status", "UNKNOWN"))
        _append_row(
            rows,
            base,
            scope="url_verification",
            source_checked="url-verification-report.json",
            status=status,
            issue=f"URL {entry.get('url', '')}: {status}",
            action_suggested="Review flagged URL manually; reachability is not authenticity.",
        )


def _apply_hallucination_risk(project: ThesisProject, base_rows: dict[str, ReferenceLedgerRow], rows: list[ReferenceLedgerRow]) -> None:
    report = _load_json(project.reports_dir / "hallucination-risk-report.json")
    if not report:
        return
    entries = report.get("entries")
    if not isinstance(entries, list):
        return
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        key = str(entry.get("citation_key", ""))
        base = _seed_row(base_rows, key, entry)
        label = str(entry.get("risk_label", "UNKNOWN"))
        score = entry.get("hallucination_risk_score", "")
        _append_row(
            rows,
            base,
            scope="hallucination_risk",
            source_checked="hallucination-risk-report.json",
            status=label,
            issue=f"Hallucination risk label: {label}; score: {score}",
            action_suggested=str(entry.get("recommended_action", "Review hallucination risk evidence manually.")),
        )


def build_reference_audit_ledger_rows(project: ThesisProject) -> list[ReferenceLedgerRow]:
    base_rows = _base_rows_from_bib(project)
    rows = [
        ReferenceLedgerRow(**row.to_dict())
        for row in sorted(base_rows.values(), key=lambda item: item.key)
    ]
    _apply_citation_integrity(project, base_rows, rows)
    _apply_final_reference_set(project, base_rows, rows)
    _apply_external_verification(project, base_rows, rows)
    _apply_doi_candidates(project, base_rows, rows)
    _apply_url_verification(project, base_rows, rows)
    _apply_hallucination_risk(project, base_rows, rows)
    return rows


def write_reference_audit_ledger_csv(rows: list[ReferenceLedgerRow], output: str | Path) -> None:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=LEDGER_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.to_dict())
