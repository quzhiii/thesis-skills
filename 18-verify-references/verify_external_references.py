from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.citation_integrity.bib_parser import parse_bib_entries_from_text
from core.citation_integrity.crossref_verifier import verify_with_crossref
from core.citation_integrity.external_report import (
    build_external_verification_report,
    write_external_verification_report,
)
from core.citation_integrity.models import BibEntry
from core.citation_integrity.openalex_verifier import verify_with_openalex
from core.citation_integrity.external_models import ExternalProviderEvidence
from core.citation_integrity.semantic_scholar_verifier import verify_with_semantic_scholar
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


def _verify_entries(
    entries: list[BibEntry], cache_dir: Path
) -> dict[str, list[ExternalProviderEvidence]]:
    evidence_by_key: dict[str, list[ExternalProviderEvidence]] = {}
    for entry in entries:
        fields = entry.fields
        local_metadata: dict[str, object] = {}
        if fields.get("title"):
            local_metadata["title"] = fields["title"]
        if fields.get("doi"):
            local_metadata["doi"] = fields["doi"].strip().lower()
        if not local_metadata.get("title") and not local_metadata.get("doi"):
            continue
        providers: list[ExternalProviderEvidence] = [
            verify_with_crossref(local_metadata, cache_dir=cache_dir),
            verify_with_openalex(local_metadata, cache_dir=cache_dir),
            verify_with_semantic_scholar(local_metadata, cache_dir=cache_dir),
        ]
        evidence_by_key[entry.key] = providers
    return evidence_by_key


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify references against CrossRef, OpenAlex, and Semantic Scholar"
    )
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--ruleset", default="tsinghua-thesis")
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    pack = find_rule_pack(repo_root, args.ruleset)
    project = ThesisProject.discover(
        args.project_root,
        pack.rules["project"]["main_tex_candidates"],
        pack.rules["project"]["chapter_globs"],
        pack.rules["project"]["bibliography_files"],
    )
    cache_dir = project.reports_dir / ".external-cache"
    entries = _collect_entries(project)
    evidence_by_key = _verify_entries(entries, cache_dir)
    report = build_external_verification_report(entries, evidence_by_key=evidence_by_key)
    output = project.reports_dir / "external-verification-report.json"
    write_external_verification_report(report, output)
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
