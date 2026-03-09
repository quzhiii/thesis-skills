from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.migration import run_word_to_latex_migration


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Map Word-exported assets into a LaTeX project"
    )
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--target-root", required=True)
    parser.add_argument("--spec", required=True)
    parser.add_argument("--apply", choices=["true", "false"], default="false")
    args = parser.parse_args()
    summary = run_word_to_latex_migration(
        args.source_root, args.target_root, args.spec, args.apply == "true"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
