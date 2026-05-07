from __future__ import annotations

import json
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import quote
import urllib.request

from core.citation_integrity.external_cache import read_cache, write_cache
from core.citation_integrity.external_models import ExternalProviderEvidence


_HTTP_TIMEOUT_SECONDS = 3.0


def _nested_venue(item: dict[str, object]) -> str | None:
    primary_location = item.get("primary_location")
    if isinstance(primary_location, dict):
        source = primary_location.get("source")
        if isinstance(source, dict) and isinstance(source.get("display_name"), str):
            return source["display_name"]
    host_venue = item.get("host_venue")
    if isinstance(host_venue, dict) and isinstance(host_venue.get("display_name"), str):
        return host_venue["display_name"]
    return None


def _normalize_doi(value: object) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    doi = value.strip()
    prefix = "https://doi.org/"
    if doi.lower().startswith(prefix):
        doi = doi[len(prefix) :]
    return doi.lower()


def _candidate(item: dict[str, object]) -> dict[str, object]:
    candidate: dict[str, object] = {}
    title = item.get("display_name")
    doi = _normalize_doi(item.get("doi"))
    year = item.get("publication_year")
    venue = _nested_venue(item)
    if isinstance(title, str) and title:
        candidate["title"] = title
    if doi:
        candidate["doi"] = doi
    if isinstance(year, int):
        candidate["year"] = year
    if venue:
        candidate["venue"] = venue
    authorships = item.get("authorships")
    if isinstance(authorships, list):
        names = []
        for authorship in authorships:
            if not isinstance(authorship, dict):
                continue
            author = authorship.get("author")
            if isinstance(author, dict) and isinstance(author.get("display_name"), str):
                names.append(author["display_name"])
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
        source="openalex",
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
        items = [response] if response.get("display_name") or response.get("doi") else []
    else:
        raw_results = response.get("results")
        items = raw_results if isinstance(raw_results, list) else []
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
        "source": "openalex",
        "success": True,
        "candidate_count": len(scored_candidates),
        "top_candidate": top_candidate,
        "candidates": scored_candidates,
        "match_score": match_score,
    }


def _fetch_json(url: str) -> dict[str, object]:
    request = urllib.request.Request(url, headers={"User-Agent": "thesis-skills/2.0-alpha"})
    with urllib.request.urlopen(request, timeout=_HTTP_TIMEOUT_SECONDS) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload if isinstance(payload, dict) else {}


def verify_with_openalex(
    local_metadata: dict[str, object], *, cache_dir: str | Path
) -> ExternalProviderEvidence:
    doi = str(local_metadata.get("doi", "")).strip()
    title = str(local_metadata.get("title", "")).strip()
    query_type = "doi" if doi else "title"
    query = doi or title
    cache_hit = read_cache(cache_dir, "openalex", query_type, query)
    if cache_hit.hit:
        return _evidence_from_payload(cache_hit.payload, query_type, query, used_cache=True)

    try:
        if query_type == "doi":
            url = f"https://api.openalex.org/works/doi:{quote(query)}"
        else:
            url = f"https://api.openalex.org/works?search={quote(query)}&per-page=1"
        payload = _payload_from_response(_fetch_json(url), query_type, local_metadata)
    except (OSError, ValueError) as exc:
        payload = {
            "source": "openalex",
            "success": False,
            "candidate_count": 0,
            "top_candidate": None,
            "candidates": [],
            "match_score": 0.0,
            "error": str(exc),
        }
    write_cache(cache_dir, "openalex", query_type, query, payload)
    return _evidence_from_payload(payload, query_type, query, used_cache=False)
