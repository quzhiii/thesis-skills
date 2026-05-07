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


def _match_status(providers: list[ExternalProviderEvidence]) -> str:
    if not providers:
        return "NO_CANDIDATE"
    if all(not provider.success for provider in providers):
        return "UNAVAILABLE"
    if any(provider.success and provider.candidate_count > 0 and (provider.match_score or 0.0) >= 0.8 for provider in providers):
        return "MATCH"
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
        match_status = _match_status(providers)
        verification_entries.append(
            ExternalVerificationEntry(
                citation_key=entry.key,
                local_metadata=_local_metadata(entry),
                match_status=match_status,
                providers=providers,
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
