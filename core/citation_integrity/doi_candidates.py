from __future__ import annotations

import csv
import json

from datetime import datetime, timezone
from pathlib import Path

from core.citation_integrity.models import BibEntry


MIN_CONFIDENCE = 0.70
ELIGIBLE_ENTRY_TYPES = {"article", "inproceedings"}


def _external_entries_by_key(external_report: dict[str, object]) -> dict[str, dict[str, object]]:
    entries = external_report.get("entries")
    if not isinstance(entries, list):
        return {}
    result: dict[str, dict[str, object]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        key = entry.get("citation_key")
        if isinstance(key, str):
            result[key] = entry
    return result


def _candidate_confidence(candidate: dict[str, object]) -> float:
    if bool(candidate.get("doi_exact_match")):
        return 1.0
    for key in ("confidence", "consensus_score", "match_score", "title_similarity"):
        value = candidate.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    return 0.0


def _provider_candidates(external_entry: dict[str, object]) -> list[tuple[str, dict[str, object], float]]:
    providers = external_entry.get("providers")
    if not isinstance(providers, list):
        return []
    result: list[tuple[str, dict[str, object], float]] = []
    for provider in providers:
        if not isinstance(provider, dict) or not provider.get("success"):
            continue
        source = str(provider.get("source", ""))
        candidates = provider.get("candidates")
        if not isinstance(candidates, list):
            continue
        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue
            doi = str(candidate.get("doi", "")).strip()
            if not doi:
                continue
            confidence = _candidate_confidence(candidate)
            result.append((source, candidate, confidence))
    return sorted(result, key=lambda item: item[2], reverse=True)


def _candidate_authors(candidate: dict[str, object]) -> str:
    authors = candidate.get("authors")
    if isinstance(authors, list):
        return "; ".join(str(author) for author in authors if str(author).strip())
    return str(authors or "")


def build_doi_candidate_report(
    bib_entries: list[BibEntry],
    external_report: dict[str, object],
) -> dict[str, object]:
    external_by_key = _external_entries_by_key(external_report)
    candidates: list[dict[str, object]] = []
    for entry in sorted(bib_entries, key=lambda item: (item.key, item.file, item.line)):
        if entry.entry_type not in ELIGIBLE_ENTRY_TYPES:
            continue
        if entry.fields.get("doi", "").strip():
            continue
        external_entry = external_by_key.get(entry.key)
        if not external_entry:
            continue
        provider_candidates = _provider_candidates(external_entry)
        if not provider_candidates:
            continue
        provider, candidate, confidence = provider_candidates[0]
        if confidence < MIN_CONFIDENCE:
            continue
        candidates.append(
            {
                "citation_key": entry.key,
                "local_title": entry.fields.get("title", ""),
                "local_year": entry.fields.get("year", ""),
                "candidate_doi": str(candidate.get("doi", "")).strip(),
                "candidate_title": str(candidate.get("title", "")),
                "candidate_year": str(candidate.get("year", "")),
                "candidate_authors": _candidate_authors(candidate),
                "provider": provider,
                "confidence": round(confidence, 4),
                "recommended_action": "Verify DOI manually and add to bib entry if confirmed.",
            }
        )
    return {
        "module": "missing_doi_candidates",
        "version": "3.3",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {"candidate_count": len(candidates)},
        "entries": candidates,
    }


def write_doi_candidate_json(report: dict[str, object], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def write_doi_candidate_csv(report: dict[str, object], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "citation_key",
        "local_title",
        "local_year",
        "candidate_doi",
        "candidate_title",
        "candidate_year",
        "candidate_authors",
        "provider",
        "confidence",
        "recommended_action",
    ]
    entries = report.get("entries")
    rows = entries if isinstance(entries, list) else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            if isinstance(row, dict):
                writer.writerow({field: row.get(field, "") for field in fieldnames})
