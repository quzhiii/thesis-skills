from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def _run(cmd: list[str], cwd: Path) -> dict[str, Any]:
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    payload: dict[str, object] = {"exit_code": proc.returncode}
    if proc.stdout.strip():
        try:
            payload["summary"] = json.loads(proc.stdout)
        except json.JSONDecodeError:
            payload["stdout"] = proc.stdout
    if proc.stderr.strip():
        payload["stderr"] = proc.stderr
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run safe fixers against existing reports"
    )
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--ruleset", default="tsinghua-thesis")
    parser.add_argument("--apply", choices=["true", "false"], default="false")
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parent
    project_root = Path(args.project_root).resolve()
    reports_dir = project_root / "reports"
    steps = [
        (
            "references",
            repo_root / "20-fix-references" / "fix_references.py",
            reports_dir / "check_references-report.json",
        ),
        (
            "language",
            repo_root / "21-fix-language-style" / "fix_language_style.py",
            reports_dir / "check_language-report.json",
        ),
        (
            "format",
            repo_root / "22-fix-format-structure" / "fix_format_structure.py",
            reports_dir / "check_format-report.json",
        ),
    ]
    steps_summary: dict[str, Any] = {}
    summary: dict[str, Any] = {
        "ruleset": args.ruleset,
        "project_root": str(project_root),
        "steps": steps_summary,
    }
    for name, script, report in steps:
        if report.exists():
            steps_summary[name] = _run(
                [
                    sys.executable,
                    str(script),
                    "--project-root",
                    str(project_root),
                    "--report",
                    str(report),
                    "--apply",
                    args.apply,
                ],
                repo_root,
            )
        else:
            steps_summary[name] = {
                "exit_code": 0,
                "status": "skipped",
                "reason": f"Missing report: {report.name}",
            }
    (reports_dir / "fix-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
