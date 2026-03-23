from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher

from core.canonicalize import normalize_doi, normalize_title
from core.citation_models import CanonicalRef


# Thresholds for low-confidence matching
TITLE_SIMILARITY_THRESHOLD = 0.85  # 85% title similarity
YEAR_AUTHOR_MATCH_THRESHOLD = 0.60  # Lower threshold for year+author combo


@dataclass
class PotentialMatch:
    """Represents a low-confidence potential duplicate match."""

    ref1: CanonicalRef
    ref2: CanonicalRef
    match_type: str  # "title_similarity", "year_author_match"
    confidence: float
    details: str


def title_similarity(title1: str | None, title2: str | None) -> float:
    """Calculate normalized title similarity using SequenceMatcher."""
    if not title1 or not title2:
        return 0.0

    normalized1 = normalize_title(title1)
    normalized2 = normalize_title(title2)

    if not normalized1 or not normalized2:
        return 0.0

    return SequenceMatcher(None, normalized1, normalized2).ratio()


def first_author_match(ref1: CanonicalRef, ref2: CanonicalRef) -> bool:
    """Check if first authors have the same family name."""
    if not ref1.authors or not ref2.authors:
        return False

    family1 = normalize_title(ref1.authors[0].family)
    family2 = normalize_title(ref2.authors[0].family)

    return bool(family1 and family2 and family1 == family2)


def year_match(ref1: CanonicalRef, ref2: CanonicalRef) -> bool:
    """Check if years match."""
    year1 = (ref1.year or "").strip()
    year2 = (ref2.year or "").strip()
    return bool(year1 and year2 and year1 == year2)


def find_potential_matches(
    refs: list[CanonicalRef],
) -> list[PotentialMatch]:
    """Find potential duplicate matches based on title similarity and year+author."""
    matches: list[PotentialMatch] = []
    seen_pairs: set[tuple[str, str]] = set()

    for i, ref1 in enumerate(refs):
        for j, ref2 in enumerate(refs):
            if i >= j:
                continue

            # Avoid duplicate pairs
            pair_key = (
                min(ref1.canonical_id, ref2.canonical_id),
                max(ref1.canonical_id, ref2.canonical_id),
            )
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)

            # Skip if both have same DOI (already handled as exact duplicate)
            doi1 = normalize_doi(ref1.doi)
            doi2 = normalize_doi(ref2.doi)
            if doi1 and doi2 and doi1 == doi2:
                continue

            # Check title similarity
            sim = title_similarity(ref1.title, ref2.title)
            if sim >= TITLE_SIMILARITY_THRESHOLD:
                matches.append(
                    PotentialMatch(
                        ref1=ref1,
                        ref2=ref2,
                        match_type="title_similarity",
                        confidence=sim,
                        details=f"Title similarity: {sim:.0%}",
                    )
                )
                continue

            # Check year + first author match (lower confidence)
            if year_match(ref1, ref2) and first_author_match(ref1, ref2):
                matches.append(
                    PotentialMatch(
                        ref1=ref1,
                        ref2=ref2,
                        match_type="year_author_match",
                        confidence=YEAR_AUTHOR_MATCH_THRESHOLD,
                        details=f"Same year ({ref1.year}) and first author ({ref1.authors[0].family if ref1.authors else 'N/A'})",
                    )
                )

    return matches


def dedupe_refs(refs: list[CanonicalRef]) -> tuple[list[CanonicalRef], list[str]]:
    """
    Deduplicate refs and warn about potential duplicates.

    Returns:
        tuple of (deduped refs, warnings)
        - deduped refs: list with DOI-exact duplicates removed
        - warnings: list of warning messages about exact and potential duplicates
    """
    deduped: list[CanonicalRef] = []
    warnings: list[str] = []
    seen_doi: dict[str, CanonicalRef] = {}

    # Phase 1: Remove exact DOI duplicates
    for ref in refs:
        doi = normalize_doi(ref.doi)
        if doi:
            if doi in seen_doi:
                warnings.append(
                    f"Duplicate DOI detected: {doi} "
                    f"(keeping source_id={seen_doi[doi].source_id}, "
                    f"dropping source_id={ref.source_id})"
                )
                continue
            seen_doi[doi] = ref
        deduped.append(ref)

    # Phase 2: Detect potential duplicates (low-confidence)
    potential_matches = find_potential_matches(deduped)

    for match in potential_matches:
        if match.match_type == "title_similarity":
            warnings.append(
                f"Potential duplicate (title similarity {match.confidence:.0%}): "
                f"source_id={match.ref1.source_id} '{match.ref1.title}' "
                f"<-> source_id={match.ref2.source_id} '{match.ref2.title}'"
            )
        elif match.match_type == "year_author_match":
            warnings.append(
                f"Potential duplicate (same year and author): "
                f"source_id={match.ref1.source_id} '{match.ref1.title}' "
                f"<-> source_id={match.ref2.source_id} '{match.ref2.title}'"
            )

    return deduped, warnings
