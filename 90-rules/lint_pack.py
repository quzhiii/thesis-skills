from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.pack_linter import build_pack_scorecard, lint_pack
from core.reports import write_report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Lint a rule pack against the current starter-pack baseline"
    )
    parser.add_argument("--pack-path", required=True)
    parser.add_argument("--report")
    args = parser.parse_args()

    pack_path = Path(args.pack_path)
    report_path = (
        Path(args.report)
        if args.report
        else pack_path / "pack-lint-report.json"
    )

    findings = lint_pack(pack_path)
    ruleset = pack_path.name
    scorecard = build_pack_scorecard(findings)
    exit_code = write_report(
        report_path,
        checker="lint_pack",
        ruleset=ruleset,
        findings=findings,
        extra_summary={"pack_path": str(pack_path)},
        extra_payload={"scorecard": scorecard},
    )
    print(report_path.read_text(encoding="utf-8"))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
