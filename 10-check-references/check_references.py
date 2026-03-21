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
    return run_reference_check(project, pack, report)


if __name__ == "__main__":
    sys.exit(main())
