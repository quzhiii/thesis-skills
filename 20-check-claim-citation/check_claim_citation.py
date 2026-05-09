from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.citation_integrity.bib_parser import parse_bib_entries_from_text
from core.citation_integrity.claim_citation import (
    build_claim_citation_report,
    write_claim_citation_report_csv,
    write_claim_citation_report_json,
    write_claim_citation_report_md,
)
from core.citation_integrity.models import BibEntry
from core.citation_integrity.tex_parser import extract_citation_contexts
from core.project import ThesisProject
from core.rules import find_rule_pack


def _collect_bib_entries(project: ThesisProject) -> list[BibEntry]:
    entries: list[BibEntry] = []
    for bib in project.bibliography_files:
        if not bib.exists():
            continue
        text = bib.read_text(encoding="utf-8", errors="ignore")
        entries.extend(parse_bib_entries_from_text(text, project.rel(bib)))
    return entries


def _load_hallucination_report(reports_dir: Path) -> dict[str, object] | None:
    path = reports_dir / "hallucination-risk-report.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _collect_contexts(project: ThesisProject) -> list:
    contexts = []
    for tex_path in project.chapter_files:
        if not tex_path.exists():
            continue
        text = tex_path.read_text(encoding="utf-8", errors="ignore")
        contexts.extend(extract_citation_contexts(text, project.rel(tex_path)))
    if project.main_tex.exists():
        text = project.main_tex.read_text(encoding="utf-8", errors="ignore")
        contexts.extend(extract_citation_contexts(text, project.rel(project.main_tex)))
    return contexts


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Triage claim-citation pairs for structural support signals"
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
    contexts = _collect_contexts(project)
    bib_entries = _collect_bib_entries(project)
    hallucination_report = _load_hallucination_report(project.reports_dir)
    report = build_claim_citation_report(contexts, bib_entries, hallucination_report)

    json_output = project.reports_dir / "claim-citation-triage-report.json"
    md_output = project.reports_dir / "claim-citation-triage.md"
    csv_output = project.reports_dir / "claim-citation-triage.csv"
    write_claim_citation_report_json(report, json_output)
    write_claim_citation_report_md(report, md_output)
    write_claim_citation_report_csv(report, csv_output)

    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    if report["status"] == "ORPHANED":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())