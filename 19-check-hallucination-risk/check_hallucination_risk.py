from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.citation_integrity.bib_parser import parse_bib_entries_from_text
from core.citation_integrity.hallucination_risk import (
    build_hallucination_risk_report,
    write_hallucination_risk_report,
    write_high_risk_csv,
)
from core.citation_integrity.models import BibEntry
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


def _load_external_report(reports_dir: Path) -> dict[str, object] | None:
    path = reports_dir / "external-verification-report.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Score bibliography entries for hallucination risk"
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
    entries = _collect_entries(project)
    external_report = _load_external_report(project.reports_dir)
    report = build_hallucination_risk_report(entries, external_report)
    json_output = project.reports_dir / "hallucination-risk-report.json"
    csv_output = project.reports_dir / "high-risk-references.csv"
    write_hallucination_risk_report(report, json_output)
    write_high_risk_csv(report, csv_output)
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    if report["status"] == "HIGH_RISK":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
