from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class CacheReadResult:
    hit: bool
    payload: dict[str, object] = field(default_factory=dict)


def build_cache_key(provider: str, query_type: str, query: str) -> str:
    normalized_provider = provider.strip().lower()
    normalized_query_type = query_type.strip().lower()
    normalized_query = " ".join(query.strip().lower().split())
    digest = hashlib.sha256(
        f"{normalized_provider}\0{normalized_query_type}\0{normalized_query}".encode("utf-8")
    ).hexdigest()[:32]
    return f"{normalized_provider}-{normalized_query_type}-{digest}.json"


def read_cache(
    cache_dir: str | Path, provider: str, query_type: str, query: str
) -> CacheReadResult:
    path = Path(cache_dir) / build_cache_key(provider, query_type, query)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return CacheReadResult(hit=False)
    if not isinstance(payload, dict):
        return CacheReadResult(hit=False)
    return CacheReadResult(hit=True, payload=payload)


def write_cache(
    cache_dir: str | Path,
    provider: str,
    query_type: str,
    query: str,
    payload: dict[str, object],
) -> Path:
    directory = Path(cache_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / build_cache_key(provider, query_type, query)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
