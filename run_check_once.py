from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def run_step(cmd: list[str], workdir: Path, env: dict[str, str] | None = None) -> int:
    print(f"\n[run] {' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=str(workdir), env=env)
    print(f"[exit] {proc.returncode}")
    return proc.returncode


def powershell_command() -> str | None:
    for candidate in ("pwsh", "powershell", "powershell.exe"):
        if shutil.which(candidate):
            return candidate
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run thesis-latex-skills one-pass thesis checks from staging copy"
    )
    parser.add_argument(
        "--project-root",
        default="../thuthesis-v7.6.0",
        help="Target thesis project root containing data/, ref/, and scripts/thesis_quality_loop.ps1",
    )
    parser.add_argument("--rules", default="tsinghua", help="Ruleset key")
    parser.add_argument(
        "--skip-compile",
        action="store_true",
        help="Skip compile loop and run only four checkers",
    )
    parser.add_argument(
        "--jobname",
        default="thuthesis-example-skill-check",
        help="Compile loop jobname",
    )
    args = parser.parse_args()

    project_root = (ROOT / args.project_root).resolve()
    if not project_root.exists():
        print(f"project root not found: {project_root}", file=sys.stderr)
        return 2

    rules_root = (ROOT / "06-rules" / "rules").resolve()
    if not rules_root.exists():
        print(f"rules root not found: {rules_root}", file=sys.stderr)
        return 2

    step_env = dict(os.environ)
    step_env["THESIS_PROJECT_ROOT"] = str(project_root)
    step_env["THESIS_RULES_ROOT"] = str(rules_root)

    steps: list[tuple[str, list[str], Path]] = [
        (
            "bib-quality",
            [
                sys.executable,
                str(ROOT / "00-zotero" / "check_bib_quality.py"),
                "--bib",
                "ref/refs-import.bib",
                "--main",
                "thuthesis-example.tex",
            ],
            project_root,
        ),
        (
            "references",
            [
                sys.executable,
                str(ROOT / "03-references" / "check_references.py"),
                "--rules",
                args.rules,
            ],
            project_root,
        ),
        (
            "language",
            [
                sys.executable,
                str(ROOT / "04-language" / "check_language.py"),
                "--rules",
                args.rules,
            ],
            project_root,
        ),
        (
            "format",
            [
                sys.executable,
                str(ROOT / "05-format" / "check_structure.py"),
                "--rules",
                args.rules,
            ],
            project_root,
        ),
        (
            "symbols",
            [
                sys.executable,
                str(ROOT / "02-content" / "scan_symbols.py"),
                "--rules",
                args.rules,
                "--mode",
                "report",
            ],
            project_root,
        ),
    ]

    for name, cmd, workdir in steps:
        print(f"\n=== {name} ===")
        code = run_step(cmd, workdir, env=step_env)
        if code != 0:
            print(f"stopped at step: {name}", file=sys.stderr)
            return code

    if args.skip_compile:
        print("\n[done] checkers completed (compile skipped)")
        return 0

    ps = powershell_command()
    if not ps:
        print("no PowerShell runtime found (pwsh/powershell)", file=sys.stderr)
        return 2

    compile_script = project_root / "scripts" / "thesis_quality_loop.ps1"
    if not compile_script.exists():
        print(f"compile script not found: {compile_script}", file=sys.stderr)
        return 2

    compile_cmd = [
        ps,
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(compile_script),
        "-Action",
        "full",
        "-JobName",
        args.jobname,
    ]

    print("\n=== compile ===")
    code = run_step(compile_cmd, project_root)
    if code != 0:
        return code

    print("\n[done] all steps completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
