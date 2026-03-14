from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def run_step(cmd: list[str], workdir: Path) -> int:
    print(f"\n[run] {' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=str(workdir))
    print(f"[exit] {proc.returncode}")
    return proc.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Run THU Word Pro lint/plan one pass")
    parser.add_argument("--doc", required=True, help="Path to source thesis docx")
    parser.add_argument(
        "--rules",
        default=str(ROOT / "rules" / "thu_v1.yaml"),
        help="Rules file path",
    )
    parser.add_argument(
        "--out-dir",
        default=str(ROOT / "out"),
        help="Output directory for report/plan",
    )
    args = parser.parse_args()

    doc = Path(args.doc).resolve()
    rules = Path(args.rules).resolve()
    out_dir = Path(args.out_dir).resolve()

    if not doc.exists():
        print(f"doc not found: {doc}", file=sys.stderr)
        return 2
    if not rules.exists():
        print(f"rules not found: {rules}", file=sys.stderr)
        return 2

    out_dir.mkdir(parents=True, exist_ok=True)
    report = out_dir / "report.json"
    plan = out_dir / "fix_plan.json"

    lint_cmd = [
        sys.executable,
        "-m",
        "thu_word_lint.cli",
        "lint",
        "--doc",
        str(doc),
        "--rules",
        str(rules),
        "--out",
        str(report),
    ]
    plan_cmd = [
        sys.executable,
        "-m",
        "thu_word_lint.cli",
        "plan",
        "--report",
        str(report),
        "--out",
        str(plan),
    ]

    print("\n=== lint ===")
    code = run_step(lint_cmd, ROOT)
    if code != 0:
        return code

    print("\n=== plan ===")
    code = run_step(plan_cmd, ROOT)
    if code != 0:
        return code

    print("\n[done] report and plan generated")
    print(f"report: {report}")
    print(f"plan:   {plan}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
