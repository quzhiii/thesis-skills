from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.citation_integrity.bib_parser import parse_bib_entries_from_text
from core.citation_integrity.crossref_verifier import verify_with_crossref
from core.citation_integrity.external_report import (
    build_external_verification_report,
    write_external_verification_report,
)
from core.citation_integrity.doi_candidates import (
    build_doi_candidate_report,
    write_doi_candidate_csv,
    write_doi_candidate_json,
)
from core.citation_integrity.models import BibEntry
from core.citation_integrity.openalex_verifier import verify_with_openalex
from core.citation_integrity.external_models import ExternalProviderEvidence
from core.citation_integrity.semantic_scholar_verifier import verify_with_semantic_scholar
from core.citation_integrity.tex_parser import collect_citations_from_text
from core.citation_integrity.url_verifier import (
    build_url_verification_report,
    verify_bib_urls,
    write_url_flagged_csv,
    write_url_verification_json,
)
from core.project import ThesisProject
from core.rules import find_rule_pack


def _collect_entries(project: ThesisProject) -> list[BibEntry]:
    entries: list[BibEntry] = []
    for bib in project.bibliography_files:
        if not bib.exists():
            continue
        text = bib.read_text(encoding="utf-8", errors="ignore")
        entries.extend(parse_bib_entries_from_text(text, project.rel(bib)))
    return entries


def _unique_in_order(keys: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for key in keys:
        if key in seen:
            continue
        seen.add(key)
        result.append(key)
    return result


def _collect_cited_keys(project: ThesisProject) -> list[str]:
    keys: list[str] = []
    for tex in [project.main_tex, *project.chapter_files]:
        text = tex.read_text(encoding="utf-8", errors="ignore")
        keys.extend(item.key for item in collect_citations_from_text(text, project.rel(tex)))
    return _unique_in_order(keys)


def _load_final_reference_keys(project: ThesisProject) -> list[str] | None:
    report_path = project.reports_dir / "final-reference-set-report.json"
    if not report_path.exists():
        return None
    try:
        payload = json.loads(report_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    keys = payload.get("final_keys")
    if not isinstance(keys, list):
        return None
    return _unique_in_order([str(key) for key in keys if str(key).strip()])


def _select_entries(
    project: ThesisProject,
    entries: list[BibEntry],
    *,
    scope: str,
    only_key: str | None,
) -> list[BibEntry]:
    selected_keys: list[str] | None
    if scope == "all":
        selected_keys = None
    elif scope == "final":
        selected_keys = _load_final_reference_keys(project) or _collect_cited_keys(project)
    else:
        selected_keys = _collect_cited_keys(project)

    if selected_keys is None:
        selected = entries
    else:
        allowed = set(selected_keys)
        selected = [entry for entry in entries if entry.key in allowed]

    if only_key:
        only_keys = set(_split_key_arg(only_key))
        selected = [entry for entry in selected if entry.key in only_keys]
    return selected


def _split_key_arg(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _load_existing_report(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def _existing_entries_by_key(report: dict[str, object] | None) -> dict[str, dict[str, object]]:
    if not report:
        return {}
    entries = report.get("entries")
    if not isinstance(entries, list):
        return {}
    result: dict[str, dict[str, object]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        key = entry.get("citation_key")
        if isinstance(key, str):
            result[key] = entry
    return result


def _atomic_write_report(report: dict[str, object], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    temp = output.with_suffix(output.suffix + ".tmp")
    temp.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(output)


def _provider_dicts(entry: dict[str, object]) -> list[dict[str, object]]:
    providers = entry.get("providers")
    return [provider for provider in providers if isinstance(provider, dict)] if isinstance(providers, list) else []


def _summary_from_entry_payloads(entries: list[dict[str, object]]) -> dict[str, int]:
    providers = [provider for entry in entries for provider in _provider_dicts(entry)]
    return {
        "entries_considered": len(entries),
        "doi_queries": sum(1 for provider in providers if provider.get("query_type") == "doi"),
        "title_queries": sum(1 for provider in providers if provider.get("query_type") == "title"),
        "crossref_matches": sum(1 for provider in providers if provider.get("source") == "crossref" and provider.get("success") and int(provider.get("candidate_count", 0)) > 0),
        "openalex_matches": sum(1 for provider in providers if provider.get("source") == "openalex" and provider.get("success") and int(provider.get("candidate_count", 0)) > 0),
        "semantic_scholar_matches": sum(1 for provider in providers if provider.get("source") == "semantic_scholar" and provider.get("success") and int(provider.get("candidate_count", 0)) > 0),
        "matched_entries": sum(1 for entry in entries if entry.get("match_status") in {"MATCH", "CONFIRMED_MATCH", "LIKELY_MATCH_WITH_METADATA_DIFF"}),
        "review_entries": sum(1 for entry in entries if entry.get("match_status") == "REVIEW"),
        "unavailable_queries": sum(1 for provider in providers if not provider.get("success")),
        "cache_hits": sum(1 for provider in providers if provider.get("used_cache")),
        "network_failures": sum(1 for provider in providers if not provider.get("success")),
    }


def _status_from_entry_payloads(entries: list[dict[str, object]]) -> str:
    statuses = [entry.get("match_status") for entry in entries]
    if any(status == "UNAVAILABLE" for status in statuses):
        return "UNAVAILABLE"
    if any(status == "REVIEW" for status in statuses):
        return "REVIEW"
    if any(status == "NO_CANDIDATE" for status in statuses):
        return "WARN"
    return "PASS"


def _merge_report(
    selected_entries: list[BibEntry],
    evidence_by_key: dict[str, list[ExternalProviderEvidence]],
    existing_by_key: dict[str, dict[str, object]],
) -> dict[str, object]:
    new_entries = [entry for entry in selected_entries if entry.key not in existing_by_key]
    new_report = build_external_verification_report(new_entries, evidence_by_key=evidence_by_key)
    new_by_key = {
        str(entry["citation_key"]): entry
        for entry in new_report["entries"]
        if isinstance(entry, dict) and "citation_key" in entry
    }
    merged_entries = [existing_by_key.get(entry.key) or new_by_key[entry.key] for entry in selected_entries if entry.key in existing_by_key or entry.key in new_by_key]
    return {
        "module": "citation_external_verification",
        "version": "2.0-alpha",
        "generated_at": new_report["generated_at"],
        "status": _status_from_entry_payloads(merged_entries),
        "summary": _summary_from_entry_payloads(merged_entries),
        "entries": merged_entries,
    }


def _verify_entries(
    entries: list[BibEntry],
    cache_dir: Path,
    *,
    limit: int | None = None,
    timeout_per_entry: float = 15.0,
    progress: bool = True,
    after_entry: object | None = None,
) -> dict[str, list[ExternalProviderEvidence]]:
    evidence_by_key: dict[str, list[ExternalProviderEvidence]] = {}
    verifiable = [
        entry for entry in entries
        if entry.fields.get("title") or entry.fields.get("doi")
    ]
    total = len(verifiable)
    if limit is not None:
        verifiable = verifiable[:limit]
    for idx, entry in enumerate(verifiable, 1):
        if progress:
            print(f"[{idx}/{total}] {entry.key}", file=sys.stderr, flush=True)
        fields = entry.fields
        local_metadata: dict[str, object] = {}
        if fields.get("title"):
            local_metadata["title"] = fields["title"]
        if fields.get("doi"):
            local_metadata["doi"] = fields["doi"].strip().lower()
        start = time.time()
        providers: list[ExternalProviderEvidence] = []
        providers.append(verify_with_crossref(local_metadata, cache_dir=cache_dir))
        if time.time() - start < timeout_per_entry:
            providers.append(verify_with_openalex(local_metadata, cache_dir=cache_dir))
        if time.time() - start < timeout_per_entry:
            providers.append(verify_with_semantic_scholar(local_metadata, cache_dir=cache_dir))
        evidence_by_key[entry.key] = providers
        if after_entry is not None:
            after_entry(evidence_by_key)
    return evidence_by_key


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify references against CrossRef, OpenAlex, and Semantic Scholar"
    )
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--ruleset", default="tsinghua-thesis")
    parser.add_argument("--limit", type=int, default=None, help="Max entries to verify (for large projects)")
    parser.add_argument("--timeout-per-entry", type=float, default=15.0, help="Seconds budget per entry")
    parser.add_argument("--cache-dir", default=None, help="Override cache directory path")
    parser.add_argument("--scope", choices=("final", "cited", "all"), default="final")
    parser.add_argument("--resume", action="store_true", help="Skip keys already present in the existing report")
    parser.add_argument("--only-key", default=None, help="Comma-separated citation keys to verify")
    parser.add_argument("--partial-report", dest="partial_report", action="store_true", default=True)
    parser.add_argument("--no-partial-report", dest="partial_report", action="store_false")
    parser.add_argument("--quiet", action="store_true", help="Suppress per-entry progress output")
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    pack = find_rule_pack(repo_root, args.ruleset)
    project = ThesisProject.discover(
        args.project_root,
        pack.rules["project"]["main_tex_candidates"],
        pack.rules["project"]["chapter_globs"],
        pack.rules["project"]["bibliography_files"],
    )
    cache_dir = Path(args.cache_dir) if args.cache_dir else project.reports_dir / ".external-cache"
    entries = _collect_entries(project)
    entries = _select_entries(project, entries, scope=args.scope, only_key=args.only_key)
    output = project.reports_dir / "external-verification-report.json"
    existing_report = _load_existing_report(output) if args.resume else None
    existing_by_key = _existing_entries_by_key(existing_report)
    if args.resume:
        entries_to_verify = [entry for entry in entries if entry.key not in existing_by_key]
    else:
        entries_to_verify = entries

    def write_partial(evidence: dict[str, list[ExternalProviderEvidence]]) -> None:
        if not args.partial_report:
            return
        partial = _merge_report(entries, evidence, existing_by_key)
        _atomic_write_report(partial, output)

    evidence_by_key = _verify_entries(
        entries_to_verify,
        cache_dir,
        limit=args.limit,
        timeout_per_entry=args.timeout_per_entry,
        progress=not args.quiet,
        after_entry=write_partial,
    )
    report = _merge_report(entries, evidence_by_key, existing_by_key)
    write_external_verification_report(report, output)
    doi_report = build_doi_candidate_report(entries, report)
    write_doi_candidate_json(doi_report, project.reports_dir / "missing-doi-candidates.json")
    write_doi_candidate_csv(doi_report, project.reports_dir / "missing-doi-candidates.csv")
    url_results = verify_bib_urls(entries)
    url_report = build_url_verification_report(url_results)
    write_url_verification_json(url_report, project.reports_dir / "url-verification-report.json")
    write_url_flagged_csv(url_report, project.reports_dir / "url-verification-flagged.csv")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
