from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.final_audit import build_final_audit_report, write_final_audit_report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Aggregate existing final-audit evidence into a JSON handoff report"
    )
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--ruleset", default="tsinghua-thesis")
    parser.add_argument("--report")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    report = build_final_audit_report(project_root, args.ruleset)
    output = (
        Path(args.report)
        if args.report
        else project_root / "reports" / "final-audit-report.json"
    )
    write_final_audit_report(report, output)
    return 1 if report["overall_verdict"] == "BLOCK" else 0


if __name__ == "__main__":
    sys.exit(main())
