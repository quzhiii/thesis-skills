from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class ExternalProviderEvidence:
    source: str
    query_type: str
    query: str
    used_cache: bool
    success: bool
    candidate_count: int
    top_candidate: dict[str, object] | None = None
    match_score: float | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {key: value for key, value in asdict(self).items() if value is not None}


@dataclass(frozen=True)
class ExternalVerificationEntry:
    citation_key: str
    local_metadata: dict[str, object]
    match_status: str
    providers: list[ExternalProviderEvidence] = field(default_factory=list)
    recommended_action: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "citation_key": self.citation_key,
            "local_metadata": self.local_metadata,
            "match_status": self.match_status,
            "providers": [provider.to_dict() for provider in self.providers],
            "recommended_action": self.recommended_action,
        }


@dataclass(frozen=True)
class ExternalVerificationSummary:
    entries_considered: int = 0
    doi_queries: int = 0
    title_queries: int = 0
    crossref_matches: int = 0
    openalex_matches: int = 0
    matched_entries: int = 0
    review_entries: int = 0
    unavailable_queries: int = 0
    cache_hits: int = 0
    network_failures: int = 0

    def to_dict(self) -> dict[str, int]:
        return asdict(self)
