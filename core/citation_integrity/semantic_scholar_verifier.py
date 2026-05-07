from __future__ import annotations

import json
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import quote
import urllib.request

from core.citation_integrity.external_cache import read_cache, write_cache
from core.citation_integrity.external_models import ExternalProviderEvidence


_HTTP_TIMEOUT_SECONDS = 3.0


def _normalize_doi(value: object) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    return value.strip().lower()


def _authors(item: dict[str, object]) -> list[str]:
    raw_authors = item.get("authors")
    if not isinstance(raw_authors, list):
        return []
    names: list[str] = []
    for author in raw_authors:
        if not isinstance(author, dict):
            continue
        name = author.get("name")
        if isinstance(name, str) and name.strip():
            names.append(name.strip())
    return names


def _candidate(item: dict[str, object]) -> dict[str, object]:
    candidate: dict[str, object] = {}
    title = item.get("title")
    year = item.get("year")
    venue = item.get("venue")
    external_ids = item.get("externalIds")
    doi = external_ids.get("DOI") if isinstance(external_ids, dict) else None
    if isinstance(title, str) and title.strip():
        candidate["title"] = title.strip()
    normalized_doi = _normalize_doi(doi)
    if normalized_doi:
        candidate["doi"] = normalized_doi
    if isinstance(year, int):
        candidate["year"] = year
    if isinstance(venue, str) and venue.strip():
        candidate["venue"] = venue.strip()
    names = _authors(item)
    if names:
        candidate["authors"] = names
    return candidate


def _score_candidate(candidate: dict[str, object], local_metadata: dict[str, object]) -> dict[str, object]:
    scored = dict(candidate)
    local_doi = str(local_metadata.get("doi", "")).strip().lower()
    candidate_doi = str(candidate.get("doi", "")).strip().lower()
    local_title = str(local_metadata.get("title", "")).strip().lower()
    candidate_title = str(candidate.get("title", "")).strip().lower()
    scored["doi_exact_match"] = bool(local_doi and candidate_doi and local_doi == candidate_doi)
    scored["title_similarity"] = (
        SequenceMatcher(None, local_title, candidate_title).ratio()
        if local_title and candidate_title
        else 0.0
    )
    return scored


def _evidence_from_payload(
    payload: dict[str, object], query_type: str, query: str, *, used_cache: bool
) -> ExternalProviderEvidence:
    return ExternalProviderEvidence(
        source="semantic_scholar",
        query_type=query_type,
        query=query,
        used_cache=used_cache,
        success=bool(payload.get("success", True)),
        candidate_count=int(payload.get("candidate_count", 0)),
        top_candidate=payload.get("top_candidate") if isinstance(payload.get("top_candidate"), dict) else None,
        candidates=payload.get("candidates") if isinstance(payload.get("candidates"), list) else [],
        match_score=float(payload.get("match_score", 0.0)),
        error=str(payload["error"]) if payload.get("error") else None,
    )


def _payload_from_response(
    response: dict[str, object], query_type: str, local_metadata: dict[str, object]
) -> dict[str, object]:
    if query_type == "doi":
        items = [response] if response.get("title") or response.get("externalIds") else []
    else:
        raw_items = response.get("data")
        items = raw_items if isinstance(raw_items, list) else []
    candidates = [_candidate(item) for item in items if isinstance(item, dict)]
    candidates = [item for item in candidates if item]
    scored_candidates = [_score_candidate(item, local_metadata) for item in candidates]
    top_candidate = scored_candidates[0] if scored_candidates else None
    match_score = 0.0
    if isinstance(top_candidate, dict):
        if bool(top_candidate.get("doi_exact_match")):
            match_score = 1.0
        else:
            match_score = float(top_candidate.get("title_similarity", 0.0))
    return {
        "source": "semantic_scholar",
        "success": True,
        "candidate_count": len(scored_candidates),
        "top_candidate": top_candidate,
        "candidates": scored_candidates,
        "match_score": match_score,
    }


def _fetch_json(url: str) -> dict[str, object]:
    request = urllib.request.Request(url, headers={"User-Agent": "thesis-skills/2.0-stable"})
    with urllib.request.urlopen(request, timeout=_HTTP_TIMEOUT_SECONDS) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload if isinstance(payload, dict) else {}


def verify_with_semantic_scholar(
    local_metadata: dict[str, object], *, cache_dir: str | Path
) -> ExternalProviderEvidence:
    doi = str(local_metadata.get("doi", "")).strip()
    title = str(local_metadata.get("title", "")).strip()
    query_type = "doi" if doi else "title"
    query = doi or title
    cache_hit = read_cache(cache_dir, "semantic_scholar", query_type, query)
    if cache_hit.hit:
        return _evidence_from_payload(cache_hit.payload, query_type, query, used_cache=True)

    try:
        if query_type == "doi":
            url = (
                "https://api.semanticscholar.org/graph/v1/paper/DOI:"
                f"{quote(query)}?fields=title,year,venue,authors,externalIds"
            )
        else:
            url = (
                "https://api.semanticscholar.org/graph/v1/paper/search?query="
                f"{quote(query)}&limit=1&fields=title,year,venue,authors,externalIds"
            )
        payload = _payload_from_response(_fetch_json(url), query_type, local_metadata)
    except (OSError, ValueError) as exc:
        payload = {
            "source": "semantic_scholar",
            "success": False,
            "candidate_count": 0,
            "top_candidate": None,
            "candidates": [],
            "match_score": 0.0,
            "error": str(exc),
        }
    write_cache(cache_dir, "semantic_scholar", query_type, query, payload)
    return _evidence_from_payload(payload, query_type, query, used_cache=False)
