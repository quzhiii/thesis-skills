from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.checkers import run_compile_check
from core.project import ThesisProject
from core.rules import find_rule_pack


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Parse LaTeX compile logs into structured findings"
    )
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--ruleset", default="tsinghua-thesis")
    parser.add_argument("--report")
    parser.add_argument("--log-path")
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
        else project.reports_dir / "check_compile-report.json"
    )
    exit_code = run_compile_check(
        project,
        pack,
        report,
        log_path=Path(args.log_path) if args.log_path else None,
    )
    print(report.read_text(encoding="utf-8"))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
