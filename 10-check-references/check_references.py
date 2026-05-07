from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.checkers import run_reference_check
from core.project import ThesisProject
from core.rules import find_rule_pack


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check citation and bibliography integrity"
    )
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--ruleset", default="tsinghua-thesis")
    parser.add_argument("--report")
    parser.add_argument("--with-external-verification", action="store_true")
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    pack = find_rule_pack(repo_root, args.ruleset)
    project = ThesisProject.discover(
        args.project_root,
        pack.rules["project"]["main_tex_candidates"],
        pack.rules["project"]["chapter_globs"],
        pack.rules["project"]["bibliography_files"],
    )
    report = (
        Path(args.report)
        if args.report
        else project.reports_dir / "check_references-report.json"
    )
    exit_code = run_reference_check(project, pack, report)
    if args.with_external_verification:
        from core.citation_integrity.bib_parser import parse_bib_entries_from_text
        from core.citation_integrity.crossref_verifier import verify_with_crossref
        from core.citation_integrity.external_report import (
            build_external_verification_report,
            write_external_verification_report,
        )
        from core.citation_integrity.openalex_verifier import verify_with_openalex

        cache_dir = project.reports_dir / ".external-cache"
        entries: list[object] = []
        for bib in project.bibliography_files:
            if bib.exists():
                entries.extend(parse_bib_entries_from_text(bib.read_text(encoding="utf-8", errors="ignore"), project.rel(bib)))
        evidence_by_key: dict[str, list[object]] = {}
        for entry in entries:
            fields = entry.fields
            local_meta: dict[str, object] = {}
            if fields.get("title"):
                local_meta["title"] = fields["title"]
            if fields.get("doi"):
                local_meta["doi"] = fields["doi"].strip().lower()
            if local_meta:
                evidence_by_key[entry.key] = [
                    verify_with_crossref(local_meta, cache_dir=cache_dir),
                    verify_with_openalex(local_meta, cache_dir=cache_dir),
                ]
        ext_report = build_external_verification_report(entries, evidence_by_key=evidence_by_key)
        write_external_verification_report(ext_report, project.reports_dir / "external-verification-report.json")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
