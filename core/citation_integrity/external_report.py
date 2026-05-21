from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import re

from core.citation_integrity.external_models import (
    ExternalProviderEvidence,
    ExternalVerificationEntry,
    ExternalVerificationSummary,
)
from core.citation_integrity.models import BibEntry


def _local_metadata(entry: BibEntry) -> dict[str, object]:
    fields = entry.fields
    return {
        key: fields[key]
        for key in ("title", "author", "year", "doi", "journal", "booktitle", "volume", "number", "issue", "pages")
        if fields.get(key)
    }


def _consensus_score(candidate: dict[str, object]) -> float:
    if bool(candidate.get("doi_exact_match")):
        return 1.0
    similarity = candidate.get("title_similarity", 0.0)
    return float(similarity) if isinstance(similarity, (int, float)) else 0.0


def _normalize_text(value: object) -> str:
    return " ".join(str(value or "").lower().split())


def _author_names(value: str) -> list[str]:
    return [item.strip() for item in re.split(r"\s+and\s+", value) if item.strip()]


def _family_name(name: str) -> str:
    name = name.strip()
    if not name:
        return ""
    if "," in name:
        return name.split(",", 1)[0].strip().lower()
    return name.split()[-1].strip().lower()


def _metadata_mismatches(entry: BibEntry, candidate: dict[str, object]) -> list[str]:
    fields = entry.fields
    mismatches: list[str] = []
    local_doi = _normalize_text(fields.get("doi", ""))
    candidate_doi = _normalize_text(candidate.get("doi", ""))
    if local_doi and candidate_doi and local_doi != candidate_doi:
        mismatches.append("doi_mismatch")

    title_similarity = candidate.get("title_similarity")
    if isinstance(title_similarity, (int, float)) and 0 < float(title_similarity) < 0.70:
        mismatches.append("title_mismatch")

    local_title = str(fields.get("title", ""))
    candidate_title = str(candidate.get("title", ""))
    local_has_subtitle = ":" in local_title or "—" in local_title
    candidate_has_subtitle = ":" in candidate_title or "—" in candidate_title
    if local_title and candidate_title and local_has_subtitle != candidate_has_subtitle:
        mismatches.append("subtitle_missing")

    local_authors = _author_names(fields.get("author", ""))
    candidate_authors = candidate.get("authors")
    if isinstance(candidate_authors, list) and local_authors:
        candidate_names = [str(author) for author in candidate_authors if str(author).strip()]
        if candidate_names and len(local_authors) != len(candidate_names):
            mismatches.append("author_count_mismatch")
        if candidate_names and _family_name(local_authors[0]) != _family_name(candidate_names[0]):
            mismatches.append("author_order_mismatch")

    local_year = _normalize_text(fields.get("year", ""))
    candidate_year = _normalize_text(candidate.get("year", ""))
    if local_year and candidate_year and local_year != candidate_year:
        mismatches.append("year_mismatch")

    local_venue = _normalize_text(fields.get("journal", "") or fields.get("booktitle", ""))
    candidate_venue = _normalize_text(candidate.get("venue", "") or candidate.get("journal", "") or candidate.get("container_title", ""))
    if local_venue and candidate_venue and local_venue != candidate_venue:
        mismatches.append("venue_mismatch")

    local_volume = _normalize_text(fields.get("volume", ""))
    local_issue = _normalize_text(fields.get("number", "") or fields.get("issue", ""))
    local_pages = _normalize_text(fields.get("pages", ""))
    candidate_volume = _normalize_text(candidate.get("volume", ""))
    candidate_issue = _normalize_text(candidate.get("number", "") or candidate.get("issue", ""))
    candidate_pages = _normalize_text(candidate.get("pages", ""))
    if (
        (local_volume and candidate_volume and local_volume != candidate_volume)
        or (local_issue and candidate_issue and local_issue != candidate_issue)
        or (local_pages and candidate_pages and local_pages != candidate_pages)
    ):
        mismatches.append("volume_issue_pages_mismatch")
    return mismatches


def _merge_consensus(entry: BibEntry, providers: list[ExternalProviderEvidence]) -> dict[str, object]:
    merged: dict[str, dict[str, object]] = {}
    for provider in providers:
        if not provider.success:
            continue
        for candidate in provider.candidates:
            if not isinstance(candidate, dict):
                continue
            doi = str(candidate.get("doi", "")).strip().lower()
            title = str(candidate.get("title", "")).strip().lower()
            key = f"doi:{doi}" if doi else f"title:{title}"
            if not key or key.endswith(":"):
                continue
            existing = merged.get(key)
            source_names = [provider.source]
            if existing:
                prior_sources = existing.get("sources")
                if isinstance(prior_sources, list):
                    source_names = [*prior_sources]
                    if provider.source not in source_names:
                        source_names.append(provider.source)
            best = dict(existing) if existing else dict(candidate)
            if _consensus_score(candidate) > _consensus_score(best):
                best.update(candidate)
            best["sources"] = source_names
            best["source_count"] = len(source_names)
            best["consensus_score"] = max(_consensus_score(candidate), _consensus_score(best))
            merged[key] = best
    ranked = sorted(
        merged.values(),
        key=lambda item: (
            float(item.get("consensus_score", 0.0)),
            int(item.get("source_count", 0)),
            1 if item.get("doi") else 0,
        ),
        reverse=True,
    )
    for candidate in ranked:
        candidate["metadata_mismatches"] = _metadata_mismatches(entry, candidate)
    return {
        "candidate_count": len(ranked),
        "top_candidate": ranked[0] if ranked else None,
        "candidates": ranked,
    }


def _match_status(
    providers: list[ExternalProviderEvidence], consensus: dict[str, object]
) -> str:
    if not providers:
        return "NO_CANDIDATE"
    if all(not provider.success for provider in providers):
        return "UNAVAILABLE"
    top_candidate = consensus.get("top_candidate") if isinstance(consensus, dict) else None
    if isinstance(top_candidate, dict):
        metadata_mismatches = top_candidate.get("metadata_mismatches")
        has_mismatches = isinstance(metadata_mismatches, list) and len(metadata_mismatches) > 0
        title_similarity = top_candidate.get("title_similarity", 0.0)
        if bool(top_candidate.get("doi_exact_match")) and isinstance(title_similarity, (int, float)) and float(title_similarity) >= 0.95:
            candidate_year = str(top_candidate.get("year", ""))
            year_related = [item for item in metadata_mismatches if item == "year_mismatch"] if isinstance(metadata_mismatches, list) else []
            if candidate_year and not year_related and not has_mismatches:
                return "CONFIRMED_MATCH"
        if has_mismatches and (bool(top_candidate.get("doi_exact_match")) or _consensus_score(top_candidate) >= 0.9):
            return "LIKELY_MATCH_WITH_METADATA_DIFF"
        if bool(top_candidate.get("doi_exact_match")):
            return "MATCH"
        score = _consensus_score(top_candidate)
        if score >= 0.9:
            return "MATCH"
        if score >= 0.5:
            return "REVIEW"
    if any(provider.success and provider.candidate_count > 0 for provider in providers):
        return "REVIEW"
    if any(not provider.success for provider in providers):
        return "UNAVAILABLE"
    return "NO_CANDIDATE"


def _recommended_action(match_status: str) -> str:
    if match_status == "CONFIRMED_MATCH":
        return "Accept external match as confirmed supporting evidence."
    if match_status == "MATCH":
        return "Accept external match as supporting evidence."
    if match_status == "LIKELY_MATCH_WITH_METADATA_DIFF":
        return "External candidate likely matches, but metadata differs; review and correct local fields manually."
    if match_status == "REVIEW":
        return "Review weak or conflicting external candidates manually."
    if match_status == "UNAVAILABLE":
        return "External provider evidence was unavailable; keep local citation checks as source of truth."
    return "No external candidate found; review manually if this reference is critical."


def _status(entries: list[ExternalVerificationEntry]) -> str:
    statuses = [entry.match_status for entry in entries]
    if any(status == "UNAVAILABLE" for status in statuses):
        return "UNAVAILABLE"
    if any(status == "REVIEW" for status in statuses):
        return "REVIEW"
    if any(status == "NO_CANDIDATE" for status in statuses):
        return "WARN"
    return "PASS"


def _summary(entries: list[ExternalVerificationEntry]) -> ExternalVerificationSummary:
    providers = [provider for entry in entries for provider in entry.providers]
    return ExternalVerificationSummary(
        entries_considered=len(entries),
        doi_queries=sum(1 for provider in providers if provider.query_type == "doi"),
        title_queries=sum(1 for provider in providers if provider.query_type == "title"),
        crossref_matches=sum(
            1
            for provider in providers
            if provider.source == "crossref" and provider.success and provider.candidate_count > 0
        ),
        openalex_matches=sum(
            1
            for provider in providers
            if provider.source == "openalex" and provider.success and provider.candidate_count > 0
        ),
        semantic_scholar_matches=sum(
            1
            for provider in providers
            if provider.source == "semantic_scholar" and provider.success and provider.candidate_count > 0
        ),
        matched_entries=sum(1 for entry in entries if entry.match_status in {"MATCH", "CONFIRMED_MATCH", "LIKELY_MATCH_WITH_METADATA_DIFF"}),
        review_entries=sum(1 for entry in entries if entry.match_status == "REVIEW"),
        unavailable_queries=sum(1 for provider in providers if not provider.success),
        cache_hits=sum(1 for provider in providers if provider.used_cache),
        network_failures=sum(1 for provider in providers if not provider.success),
    )


def build_external_verification_report(
    entries: list[BibEntry],
    *,
    evidence_by_key: dict[str, list[ExternalProviderEvidence]],
) -> dict[str, object]:
    verification_entries = []
    for entry in sorted(entries, key=lambda item: (item.key, item.file, item.line)):
        providers = evidence_by_key.get(entry.key, [])
        consensus = _merge_consensus(entry, providers)
        match_status = _match_status(providers, consensus)
        verification_entries.append(
            ExternalVerificationEntry(
                citation_key=entry.key,
                local_metadata=_local_metadata(entry),
                match_status=match_status,
                providers=providers,
                consensus=consensus,
                recommended_action=_recommended_action(match_status),
            )
        )
    return {
        "module": "citation_external_verification",
        "version": "2.0-alpha",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": _status(verification_entries),
        "summary": _summary(verification_entries).to_dict(),
        "entries": [entry.to_dict() for entry in verification_entries],
    }


def write_external_verification_report(report: dict[str, object], output: str | Path) -> None:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
