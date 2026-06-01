from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.project import ThesisProject
from core.reference_audit_ledger import build_reference_audit_ledger_rows, write_reference_audit_ledger_csv
from core.rules import find_rule_pack


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Aggregate existing reference evidence into a CSV audit ledger"
    )
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--ruleset", default="tsinghua-thesis")
    parser.add_argument("--output")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    pack = find_rule_pack(repo_root, args.ruleset)
    project = ThesisProject.discover(
        args.project_root,
        pack.rules["project"]["main_tex_candidates"],
        pack.rules["project"]["chapter_globs"],
        pack.rules["project"]["bibliography_files"],
    )
    rows = build_reference_audit_ledger_rows(project)
    output = Path(args.output) if args.output else project.reports_dir / "reference-audit-ledger.csv"
    write_reference_audit_ledger_csv(rows, output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
