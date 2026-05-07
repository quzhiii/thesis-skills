from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import quote
import urllib.request

from core.citation_integrity.external_cache import read_cache, write_cache
from core.citation_integrity.external_models import ExternalProviderEvidence


_HTTP_TIMEOUT_SECONDS = 3.0


def _first_string(value: object) -> str | None:
    if isinstance(value, list) and value and isinstance(value[0], str):
        return value[0]
    if isinstance(value, str):
        return value
    return None


def _year(item: dict[str, object]) -> int | None:
    for key in ("published-print", "published-online", "published", "issued"):
        value = item.get(key)
        if not isinstance(value, dict):
            continue
        date_parts = value.get("date-parts")
        if (
            isinstance(date_parts, list)
            and date_parts
            and isinstance(date_parts[0], list)
            and date_parts[0]
            and isinstance(date_parts[0][0], int)
        ):
            return date_parts[0][0]
    return None


def _candidate(item: dict[str, object]) -> dict[str, object]:
    candidate: dict[str, object] = {}
    title = _first_string(item.get("title"))
    doi = item.get("DOI")
    venue = _first_string(item.get("container-title"))
    year = _year(item)
    if title:
        candidate["title"] = title
    if isinstance(doi, str) and doi:
        candidate["doi"] = doi.lower()
    if year is not None:
        candidate["year"] = year
    if venue:
        candidate["venue"] = venue
    authors = item.get("author")
    if isinstance(authors, list):
        names = []
        for author in authors:
            if not isinstance(author, dict):
                continue
            given = str(author.get("given", "")).strip()
            family = str(author.get("family", "")).strip()
            name = " ".join(part for part in [given, family] if part)
            if name:
                names.append(name)
        if names:
            candidate["authors"] = names
    return candidate


def _evidence_from_payload(
    payload: dict[str, object], query_type: str, query: str, *, used_cache: bool
) -> ExternalProviderEvidence:
    return ExternalProviderEvidence(
        source="crossref",
        query_type=query_type,
        query=query,
        used_cache=used_cache,
        success=bool(payload.get("success", True)),
        candidate_count=int(payload.get("candidate_count", 0)),
        top_candidate=payload.get("top_candidate") if isinstance(payload.get("top_candidate"), dict) else None,
        match_score=float(payload.get("match_score", 0.0)),
        error=str(payload["error"]) if payload.get("error") else None,
    )


def _payload_from_response(response: dict[str, object], query_type: str) -> dict[str, object]:
    message = response.get("message")
    if not isinstance(message, dict):
        message = {}
    if query_type == "doi":
        item = message if message.get("title") or message.get("DOI") else None
        items = [item] if isinstance(item, dict) else []
    else:
        raw_items = message.get("items")
        items = raw_items if isinstance(raw_items, list) else []
    candidates = [_candidate(item) for item in items if isinstance(item, dict)]
    candidates = [item for item in candidates if item]
    return {
        "source": "crossref",
        "success": True,
        "candidate_count": len(candidates),
        "top_candidate": candidates[0] if candidates else None,
        "match_score": 1.0 if candidates else 0.0,
    }


def _fetch_json(url: str) -> dict[str, object]:
    request = urllib.request.Request(url, headers={"User-Agent": "thesis-skills/2.0-alpha"})
    with urllib.request.urlopen(request, timeout=_HTTP_TIMEOUT_SECONDS) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload if isinstance(payload, dict) else {}


def verify_with_crossref(
    local_metadata: dict[str, object], *, cache_dir: str | Path
) -> ExternalProviderEvidence:
    doi = str(local_metadata.get("doi", "")).strip()
    title = str(local_metadata.get("title", "")).strip()
    query_type = "doi" if doi else "title"
    query = doi or title
    cache_hit = read_cache(cache_dir, "crossref", query_type, query)
    if cache_hit.hit:
        return _evidence_from_payload(cache_hit.payload, query_type, query, used_cache=True)

    try:
        if query_type == "doi":
            url = f"https://api.crossref.org/works/{quote(query)}"
        else:
            url = f"https://api.crossref.org/works?query.title={quote(query)}&rows=1"
        payload = _payload_from_response(_fetch_json(url), query_type)
    except (OSError, ValueError) as exc:
        payload = {
            "source": "crossref",
            "success": False,
            "candidate_count": 0,
            "top_candidate": None,
            "match_score": 0.0,
            "error": str(exc),
        }
    write_cache(cache_dir, "crossref", query_type, query, payload)
    return _evidence_from_payload(payload, query_type, query, used_cache=False)
