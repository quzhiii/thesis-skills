from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.fixers import apply_reference_fixes


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Apply safe reference fixes from a report"
    )
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--apply", choices=["true", "false"], default="false")
    args = parser.parse_args()
    summary = apply_reference_fixes(
        args.project_root, args.report, args.apply == "true"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
