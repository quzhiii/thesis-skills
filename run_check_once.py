from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from core.project import ThesisProject
from core.rules import find_rule_pack


def _run(cmd: list[str], cwd: Path) -> int:
    proc = subprocess.run(cmd, cwd=cwd)
    return proc.returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run thesis-skills deterministic checks once"
    )
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--ruleset", default="tsinghua-thesis")
    parser.add_argument(
        "--only",
        choices=[
            "bib-quality",
            "references",
            "language",
            "language-deep",
            "format",
            "content",
        ],
    )
    parser.add_argument("--skip-compile", action="store_true")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent
    pack = find_rule_pack(repo_root, args.ruleset)
    project = ThesisProject.discover(
        args.project_root,
        pack.rules["project"]["main_tex_candidates"],
        pack.rules["project"]["chapter_globs"],
        pack.rules["project"]["bibliography_files"],
    )
    steps = [
        (
            "bib-quality",
            repo_root / "00-bib-zotero" / "check_bib_quality.py",
            project.reports_dir / "check_bib_quality-report.json",
        ),
        (
            "references",
            repo_root / "10-check-references" / "check_references.py",
            project.reports_dir / "check_references-report.json",
        ),
        (
            "language",
            repo_root / "11-check-language" / "check_language.py",
            project.reports_dir / "check_language-report.json",
        ),
        (
            "language-deep",
            repo_root / "14-check-language-deep" / "check_language_deep.py",
            project.reports_dir / "check_language_deep-report.json",
        ),
        (
            "format",
            repo_root / "12-check-format" / "check_format.py",
            project.reports_dir / "check_format-report.json",
        ),
        (
            "content",
            repo_root / "13-check-content" / "check_content.py",
            project.reports_dir / "check_content-report.json",
        ),
    ]
    if args.only:
        steps = [step for step in steps if step[0] == args.only]
    summary: dict[str, object] = {
        "ruleset": args.ruleset,
        "project_root": str(project.root),
        "steps": {},
    }
    overall = 0
    for name, script, report in steps:
        code = _run(
            [
                sys.executable,
                str(script),
                "--project-root",
                str(project.root),
                "--ruleset",
                args.ruleset,
                "--report",
                str(report),
            ],
            repo_root,
        )
        if code in {0, 1} and not report.exists():
            code = 3
        summary["steps"][name] = {
            "exit_code": code,
            "report": report.relative_to(project.root).as_posix(),
        }
        if code in {2, 3}:
            overall = code
            break
        if code == 1 and overall == 0:
            overall = 1
    if args.skip_compile:
        summary["steps"]["compile"] = {
            "status": "skipped",
            "reason": "Skipped by --skip-compile",
        }
    else:
        summary["steps"]["compile"] = {
            "status": "unavailable",
            "reason": "No compile adapter configured in stdlib starter",
        }
    (project.reports_dir / "run-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return overall


if __name__ == "__main__":
    sys.exit(main())
