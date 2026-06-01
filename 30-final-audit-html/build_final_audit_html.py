from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.final_audit_html import write_final_audit_html


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a static HTML reading surface for final-audit-report.json"
    )
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--input")
    parser.add_argument("--output")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    input_path = Path(args.input) if args.input else project_root / "reports" / "final-audit-report.json"
    output_path = Path(args.output) if args.output else project_root / "reports" / "final-audit-report.html"
    write_final_audit_html(input_path, output_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
