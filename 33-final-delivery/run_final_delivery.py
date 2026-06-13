from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.final_delivery import run_final_delivery


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run final delivery workflow: evidence, checks, optional fixes, bundle rebuild"
    )
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--ruleset", default="university-generic")
    parser.add_argument("--skip-evidence", action="store_true", help="Skip citation evidence pipeline")
    parser.add_argument("--fix-preview", action="store_true", help="Run bounded auto-fix preview before bundle rebuild")
    parser.add_argument("--fix-apply", action="store_true", help="Apply bounded auto-fixes before bundle rebuild")
    args = parser.parse_args()

    summary = run_final_delivery(
        args.project_root,
        args.ruleset,
        skip_evidence=args.skip_evidence,
        fix_preview=args.fix_preview,
        fix_apply=args.fix_apply,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
