from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.citation_integrity.final_reference_set import (
    build_final_reference_set_report,
    write_final_reference_set_csv,
    write_final_reference_set_json,
)
from core.project import ThesisProject
from core.rules import find_rule_pack


def main() -> int:
    parser = argparse.ArgumentParser(description="Build final reference set report from aux/bbl or TeX fallback")
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
    report = build_final_reference_set_report(project)
    json_output = project.reports_dir / "final-reference-set-report.json"
    csv_output = project.reports_dir / "final-reference-set-report.csv"
    write_final_reference_set_json(report, json_output)
    write_final_reference_set_csv(report, csv_output)
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
