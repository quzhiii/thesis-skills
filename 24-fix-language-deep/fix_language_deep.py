from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.fixers import apply_language_deep_fixes


def _parse_issue_codes(value: str | None) -> set[str] | None:
    if not value:
        return None
    items = {item.strip() for item in value.split(",") if item.strip()}
    return items or None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate deep language patch previews or selectively apply them"
    )
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--apply", choices=["true", "false"], default="false")
    parser.add_argument(
        "--include-review-required", choices=["true", "false"], default="false"
    )
    parser.add_argument(
        "--issue-codes",
        help="Comma-separated deep issue codes to preview/apply selectively",
    )
    args = parser.parse_args()
    summary = apply_language_deep_fixes(
        args.project_root,
        args.report,
        args.apply == "true",
        include_review_required=args.include_review_required == "true",
        issue_codes=_parse_issue_codes(args.issue_codes),
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
