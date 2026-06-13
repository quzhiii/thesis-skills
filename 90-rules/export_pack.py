from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.pack_exporter import export_pack


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export a rule pack as a versioned zip bundle"
    )
    parser.add_argument("--pack-path", required=True, help="Path to the pack directory")
    parser.add_argument("--output", required=True, help="Output zip file path")
    parser.add_argument("--lint-report", help="Optional lint report JSON to include")
    args = parser.parse_args()

    result = export_pack(args.pack_path, args.output, lint_report=args.lint_report)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
