from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.report_index import write_report_index_html


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a static local HTML index for thesis-skills reports"
    )
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    reports_dir = project_root / "reports"
    output = Path(args.output) if args.output else reports_dir / "index.html"
    write_report_index_html(
        reports_dir,
        output,
        project_label=project_root.name or "Local thesis project",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
