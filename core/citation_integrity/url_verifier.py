from __future__ import annotations

import csv
import json
import re

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlparse
import urllib.request

from core.citation_integrity.models import BibEntry


_URL_RE = re.compile(r"https?://[^\s{}]+")


@dataclass(frozen=True)
class UrlCheckResult:
    citation_key: str
    url: str
    status: str
    http_status: int | None = None
    final_url: str | None = None
    note: str = ""

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _extract_url(value: str) -> str | None:
    match = _URL_RE.search(value)
    return match.group(0) if match else None


def _domain_whitelisted(url: str, whitelist_domains: tuple[str, ...]) -> bool:
    hostname = (urlparse(url).hostname or "").lower()
    return any(hostname == domain or hostname.endswith(f".{domain}") for domain in whitelist_domains)


def _classify_status(http_status: int, original_url: str, final_url: str) -> str:
    if http_status == 200:
        if final_url and final_url != original_url:
            return "URL_REDIRECTED"
        return "URL_OK"
    if http_status == 403:
        return "URL_FORBIDDEN"
    if http_status == 404:
        return "URL_NOT_FOUND"
    return "URL_UNREACHABLE"


def _request(url: str, method: str, timeout: float) -> tuple[int, str]:
    request = urllib.request.Request(url, method=method, headers={"User-Agent": "thesis-skills/3.3.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = getattr(response, "status", None)
            final_url = getattr(response, "url", url)
            return int(status or 0), str(final_url)
    except HTTPError as error:
        return int(getattr(error, "code", 0) or 0), str(getattr(error, "url", url))


def verify_url(url: str, timeout: float = 10.0) -> UrlCheckResult:
    try:
        status_code, final_url = _request(url, "HEAD", timeout)
        if status_code == 405:
            status_code, final_url = _request(url, "GET", timeout)
        status = _classify_status(status_code, url, final_url)
        return UrlCheckResult(
            citation_key="",
            url=url,
            status=status,
            http_status=status_code,
            final_url=final_url,
            note="",
        )
    except (OSError, TimeoutError, ValueError):
        return UrlCheckResult(
            citation_key="",
            url=url,
            status="URL_UNREACHABLE",
            http_status=None,
            final_url=None,
            note="Request failed or timed out.",
        )


def verify_bib_urls(
    entries: list[BibEntry],
    whitelist_domains: tuple[str, ...] = ("gov.cn", "edu.cn"),
) -> list[UrlCheckResult]:
    results: list[UrlCheckResult] = []
    for entry in sorted(entries, key=lambda item: (item.key, item.file, item.line)):
        raw_value = entry.fields.get("url", "") or entry.fields.get("howpublished", "")
        if not raw_value:
            continue
        url = _extract_url(raw_value)
        if not url:
            continue
        if _domain_whitelisted(url, whitelist_domains):
            results.append(
                UrlCheckResult(
                    citation_key=entry.key,
                    url=url,
                    status="URL_WHITELISTED",
                    http_status=None,
                    final_url=url,
                    note="Skipped automated request for whitelisted domain.",
                )
            )
            continue
        verified = verify_url(url)
        results.append(
            UrlCheckResult(
                citation_key=entry.key,
                url=url,
                status=verified.status,
                http_status=verified.http_status,
                final_url=verified.final_url,
                note=verified.note,
            )
        )
    return results


def build_url_verification_report(results: list[UrlCheckResult]) -> dict[str, object]:
    summary = {
        "checked": len(results),
        "ok": sum(1 for result in results if result.status == "URL_OK"),
        "redirected": sum(1 for result in results if result.status == "URL_REDIRECTED"),
        "forbidden": sum(1 for result in results if result.status == "URL_FORBIDDEN"),
        "not_found": sum(1 for result in results if result.status == "URL_NOT_FOUND"),
        "unreachable": sum(1 for result in results if result.status == "URL_UNREACHABLE"),
        "whitelisted": sum(1 for result in results if result.status == "URL_WHITELISTED"),
        "flagged": sum(1 for result in results if result.status not in {"URL_OK", "URL_WHITELISTED"}),
    }
    return {
        "module": "url_verification",
        "version": "3.3",
        "generated_at": datetime.now(UTC).isoformat(),
        "summary": summary,
        "entries": [result.to_dict() for result in results],
    }


def write_url_verification_json(report: dict[str, object], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def write_url_flagged_csv(report: dict[str, object], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["citation_key", "url", "status", "http_status", "final_url", "note"]
    entries = report.get("entries")
    rows = [entry for entry in entries if isinstance(entry, dict) and entry.get("status") not in {"URL_OK", "URL_WHITELISTED"}] if isinstance(entries, list) else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})
