from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.migration import run_latex_to_word_migration


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a bounded LaTeX-to-Word export summary or output"
    )
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--output-file", required=True)
    parser.add_argument("--profile", default="review-friendly")
    parser.add_argument("--apply", choices=["true", "false"], default="false")
    parser.add_argument("--report")
    args = parser.parse_args()

    summary = run_latex_to_word_migration(
        project_root=args.project_root,
        output_file=args.output_file,
        profile=args.profile,
        apply=args.apply == "true",
    )

    report_path = Path(args.report) if args.report else Path(args.project_root) / "reports" / "latex_to_word-report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
