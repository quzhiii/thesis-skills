from __future__ import annotations

import csv
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

from core.citation_integrity.models import BibEntry


CJK_CJK_COMPAT_FIELDS = ("title", "journal", "booktitle", "publisher")
UNSUPPORTED_ENTRY_TYPES = ("mastersthesis", "phdthesis", "misc", "unpublished")
MATCH_STATUS_SCORES: dict[str, float] = {
    "MATCH": 0.0,
    "UNAVAILABLE": 0.25,
    "REVIEW": 0.35,
    "NO_CANDIDATE": 0.75,
}
TITLE_MATCH_BONUS = 0.15
NO_PROVIDER_FOUND_BONUS = 0.20
DOI_MISMATCH_BONUS = 0.25
LOW_TITLE_SIMILARITY_BONUS = 0.20
TITLE_SIMILARITY_THRESHOLD = 0.70
YEAR_MISMATCH_BONUS = 0.10
VENUE_MISMATCH_BONUS = 0.10

LABEL_THRESHOLDS: list[tuple[float, str]] = [
    (0.25, "PASS"),
    (0.50, "WARN"),
    (0.75, "REVIEW"),
    (1.01, "HIGH_RISK"),
]

STATUS_PRECEDENCE: list[str] = [
    "HIGH_RISK",
    "REVIEW",
    "WARN",
    "UNSUPPORTED",
    "PASS",
]


def contains_cjk(text: str) -> bool:
    for char in text:
        try:
            name = unicodedata.name(char, "")
        except ValueError:
            continue
        if "CJK" in name or "HIRAGANA" in name or "KATAKANA" in name or "HANGUL" in name:
            return True
    return False


def is_unsupported_reference(entry: BibEntry, external_entry: dict[str, object] | None) -> bool:
    for field in CJK_CJK_COMPAT_FIELDS:
        value = entry.fields.get(field, "")
        if value and contains_cjk(value):
            return True
    if entry.entry_type in UNSUPPORTED_ENTRY_TYPES and not entry.fields.get("doi", "").strip():
        return True
    if external_entry is not None and isinstance(external_entry, dict):
        providers = external_entry.get("providers")
        if isinstance(providers, list) and len(providers) > 0:
            if all(
                not (isinstance(p, dict) and p.get("success"))
                for p in providers
            ):
                title = entry.fields.get("title", "")
                if title and contains_cjk(title):
                    return True
    return False


def risk_label_for_score(score: float) -> str:
    for threshold, label in LABEL_THRESHOLDS:
        if score < threshold:
            return label
    return "HIGH_RISK"


def _extract_provider_candidates(providers: list[dict[str, object]]) -> list[dict[str, object]]:
    candidates: list[dict[str, object]] = []
    for provider in providers:
        if not isinstance(provider, dict):
            continue
        provider_candidates = provider.get("candidates")
        if isinstance(provider_candidates, list):
            for candidate in provider_candidates:
                if isinstance(candidate, dict):
                    candidates.append(candidate)
    return candidates


def _check_doi_mismatch(local_doi: str, candidates: list[dict[str, object]]) -> bool:
    if not local_doi:
        return False
    normalized_local = local_doi.strip().lower()
    for candidate in candidates:
        candidate_doi = str(candidate.get("doi", "")).strip().lower()
        if candidate_doi and candidate_doi != normalized_local:
            return True
    return False


def _best_title_similarity(candidates: list[dict[str, object]]) -> float:
    best = 1.0
    for candidate in candidates:
        sim = candidate.get("title_similarity")
        if isinstance(sim, (int, float)):
            best = max(best, float(sim))
    return best


def _check_year_mismatch(local_year: str, candidates: list[dict[str, object]]) -> bool:
    if not local_year:
        return False
    for candidate in candidates:
        candidate_year = str(candidate.get("year", ""))
        if candidate_year and candidate_year != local_year:
            return True
    return False


def _check_venue_mismatch(local_venue: str, candidates: list[dict[str, object]]) -> bool:
    if not local_venue:
        return False
    for candidate in candidates:
        candidate_venue = str(candidate.get("venue", "") or candidate.get("journal", "") or candidate.get("container_title", ""))
        if candidate_venue and candidate_venue.lower().strip() != local_venue.lower().strip():
            return True
    return False


def _count_successful_providers(providers: list[dict[str, object]]) -> int:
    count = 0
    for provider in providers:
        if isinstance(provider, dict) and provider.get("success"):
            count += 1
    return count


def _build_evidence(
    external_entry: dict[str, object] | None,
    candidates: list[dict[str, object]],
    providers: list[dict[str, object]],
    metadata_mismatches: list[str],
) -> dict[str, object]:
    successful = _count_successful_providers(providers)
    provider_count = len(providers)
    not_found = provider_count - successful
    return {
        "provider_count": provider_count,
        "matched_provider_count": successful,
        "not_found_provider_count": not_found,
        "metadata_mismatches": metadata_mismatches,
    }


def _recommended_action(risk_label: str) -> str:
    if risk_label == "UNSUPPORTED":
        return "This reference cannot be automatically verified by enabled external databases. Manual verification is recommended."
    if risk_label == "HIGH_RISK":
        return "No credible match was found in the enabled external databases. Manually verify DOI, journal website, database record, or source PDF."
    if risk_label == "REVIEW":
        return "Weak or conflicting external evidence found. Manually review the metadata and verify against the original source."
    if risk_label == "WARN":
        return "Some external evidence was unavailable or partially mismatched. Consider manual verification."
    return "External metadata matches local bibliography entry."


def score_hallucination_risk(
    entry: BibEntry,
    external_entry: dict[str, object] | None,
) -> dict[str, object]:
    if is_unsupported_reference(entry, external_entry):
        return {
            "citation_key": entry.key,
            "risk_label": "UNSUPPORTED",
            "hallucination_risk_score": 0.0,
            "local_metadata": {
                k: entry.fields[k]
                for k in ("title", "author", "year", "doi")
                if entry.fields.get(k)
            },
            "external_match_status": "UNSUPPORTED",
            "evidence": {
                "provider_count": 0,
                "matched_provider_count": 0,
                "not_found_provider_count": 0,
                "metadata_mismatches": [],
            },
            "recommended_action": _recommended_action("UNSUPPORTED"),
        }

    score = 0.0
    metadata_mismatches: list[str] = []
    match_status = "NO_CANDIDATE"
    providers: list[dict[str, object]] = []
    candidates: list[dict[str, object]] = []

    if external_entry is not None and isinstance(external_entry, dict):
        match_status = str(external_entry.get("match_status", "NO_CANDIDATE"))
        raw_providers = external_entry.get("providers")
        if isinstance(raw_providers, list):
            providers = raw_providers
        candidates = _extract_provider_candidates(providers)

    score += MATCH_STATUS_SCORES.get(match_status, 0.75)

    if match_status == "MATCH" and candidates:
        has_doi_exact = any(c.get("doi_exact_match") for c in candidates if isinstance(c, dict))
        if has_doi_exact:
            score = 0.0
        else:
            score += TITLE_MATCH_BONUS
    elif match_status == "MATCH":
        score += TITLE_MATCH_BONUS

    if providers and _count_successful_providers(providers) == 0:
        score += NO_PROVIDER_FOUND_BONUS

    if _check_doi_mismatch(entry.fields.get("doi", ""), candidates):
        score += DOI_MISMATCH_BONUS
        metadata_mismatches.append("doi")

    best_sim = _best_title_similarity(candidates) if candidates else 1.0
    if 0 < best_sim < TITLE_SIMILARITY_THRESHOLD:
        score += LOW_TITLE_SIMILARITY_BONUS
        metadata_mismatches.append("title")

    if _check_year_mismatch(entry.fields.get("year", ""), candidates):
        score += YEAR_MISMATCH_BONUS
        metadata_mismatches.append("year")

    local_venue = entry.fields.get("journal", "") or entry.fields.get("booktitle", "")
    if _check_venue_mismatch(local_venue, candidates):
        score += VENUE_MISMATCH_BONUS
        metadata_mismatches.append("venue")

    score = min(score, 1.0)
    risk_label = risk_label_for_score(score)

    return {
        "citation_key": entry.key,
        "risk_label": risk_label,
        "hallucination_risk_score": round(score, 4),
        "local_metadata": {
            k: entry.fields[k]
            for k in ("title", "author", "year", "doi")
            if entry.fields.get(k)
        },
        "external_match_status": match_status,
        "evidence": _build_evidence(external_entry, candidates, providers, metadata_mismatches),
        "recommended_action": _recommended_action(risk_label),
    }


def external_entries_by_key(external_report: dict[str, object] | None) -> dict[str, dict[str, object]]:
    if external_report is None:
        return {}
    entries = external_report.get("entries")
    if not isinstance(entries, list):
        return {}
    result: dict[str, dict[str, object]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        key = str(entry.get("citation_key", ""))
        if key:
            result[key] = entry
    return result


def _compute_status(risk_entries: list[dict[str, object]]) -> str:
    labels = {entry.get("risk_label", "PASS") for entry in risk_entries}
    for status in STATUS_PRECEDENCE:
        if status in labels:
            return status
    return "PASS"


def _compute_summary(risk_entries: list[dict[str, object]]) -> dict[str, object]:
    max_score = 0.0
    counts: dict[str, int] = {
        "pass_entries": 0,
        "warn_entries": 0,
        "review_entries": 0,
        "high_risk_entries": 0,
        "unsupported_entries": 0,
    }
    for entry in risk_entries:
        label = str(entry.get("risk_label", "PASS"))
        score = float(entry.get("hallucination_risk_score", 0.0))
        if score > max_score:
            max_score = score
        key = {
            "PASS": "pass_entries",
            "WARN": "warn_entries",
            "REVIEW": "review_entries",
            "HIGH_RISK": "high_risk_entries",
            "UNSUPPORTED": "unsupported_entries",
        }.get(label)
        if key:
            counts[key] += 1
    return {
        "entries_considered": len(risk_entries),
        **counts,
        "max_hallucination_risk_score": round(max_score, 4),
    }


def build_hallucination_risk_report(
    entries: list[BibEntry],
    external_report: dict[str, object] | None,
) -> dict[str, object]:
    ext_by_key = external_entries_by_key(external_report)
    risk_entries = [
        score_hallucination_risk(entry, ext_by_key.get(entry.key))
        for entry in sorted(entries, key=lambda e: (e.key, e.file, e.line))
    ]
    return {
        "module": "citation_hallucination_risk",
        "version": "3.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": _compute_status(risk_entries),
        "summary": _compute_summary(risk_entries),
        "entries": risk_entries,
    }


def write_hallucination_risk_report(report: dict[str, object], output: str | Path) -> None:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def write_high_risk_csv(report: dict[str, object], output: str | Path) -> None:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "citation_key",
        "risk_label",
        "hallucination_risk_score",
        "title",
        "year",
        "doi",
        "evidence_summary",
        "recommended_action",
    ]
    entries = report.get("entries")
    if not isinstance(entries, list):
        entries = []
    non_pass = [e for e in entries if isinstance(e, dict) and e.get("risk_label") != "PASS"]
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for entry in non_pass:
            local_meta = entry.get("local_metadata")
            meta = local_meta if isinstance(local_meta, dict) else {}
            evidence = entry.get("evidence")
            ev = evidence if isinstance(evidence, dict) else {}
            mismatches = ev.get("metadata_mismatches", [])
            if isinstance(mismatches, list) and mismatches:
                summary = f"mismatches: {', '.join(str(m) for m in mismatches)}"
            else:
                providers = ev.get("provider_count", 0)
                not_found = ev.get("not_found_provider_count", 0)
                summary = f"providers checked: {providers}, not found: {not_found}"
            writer.writerow({
                "citation_key": entry.get("citation_key", ""),
                "risk_label": entry.get("risk_label", ""),
                "hallucination_risk_score": str(entry.get("hallucination_risk_score", 0.0)),
                "title": meta.get("title", ""),
                "year": meta.get("year", ""),
                "doi": meta.get("doi", ""),
                "evidence_summary": summary,
                "recommended_action": entry.get("recommended_action", ""),
            })
