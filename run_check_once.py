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
        (
            "compile",
            repo_root / "15-check-compile" / "check_compile.py",
            project.reports_dir / "check_compile-report.json",
        ),
    ]
    if args.only:
        selected = [step for step in steps if step[0] == args.only]
        compile_steps = [step for step in steps if step[0] == "compile"]
        steps = selected + [step for step in compile_steps if step not in selected]
    summary: dict[str, object] = {
        "ruleset": args.ruleset,
        "project_root": str(project.root),
        "steps": {},
    }
    overall = 0
    for name, script, report in steps:
        if name == "compile" and args.skip_compile:
            summary["steps"]["compile"] = {
                "status": "skipped",
                "reason": "Skipped by --skip-compile",
            }
            continue
        if name == "compile" and not project.main_tex.with_suffix(".log").exists():
            summary["steps"]["compile"] = {
                "status": "missing-log",
                "reason": "No compile log discovered for the main TeX file",
                "expected_log": project.main_tex.with_suffix(".log")
                .relative_to(project.root)
                .as_posix(),
            }
            continue
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
        step_summary: dict[str, object] = {
            "exit_code": code,
            "report": report.relative_to(project.root).as_posix(),
        }
        if report.exists():
            try:
                payload = json.loads(report.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                payload = None
            if isinstance(payload, dict) and isinstance(payload.get("summary"), dict):
                step_summary["report_summary"] = payload["summary"]
        summary["steps"][name] = step_summary
        if code in {2, 3}:
            overall = code
            break
        if code == 1 and overall == 0:
            overall = 1
    compile_step = summary["steps"].get("compile")
    if isinstance(compile_step, dict) and "report_summary" in compile_step:
        compile_step["status"] = "parsed"
    (project.reports_dir / "run-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return overall


if __name__ == "__main__":
    sys.exit(main())
