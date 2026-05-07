from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

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
        for key in ("title", "author", "year", "doi")
        if fields.get(key)
    }


def _consensus_score(candidate: dict[str, object]) -> float:
    if bool(candidate.get("doi_exact_match")):
        return 1.0
    similarity = candidate.get("title_similarity", 0.0)
    return float(similarity) if isinstance(similarity, (int, float)) else 0.0


def _merge_consensus(providers: list[ExternalProviderEvidence]) -> dict[str, object]:
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
    if match_status == "MATCH":
        return "Accept external match as supporting evidence."
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
        matched_entries=sum(1 for entry in entries if entry.match_status == "MATCH"),
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
        consensus = _merge_consensus(providers)
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
