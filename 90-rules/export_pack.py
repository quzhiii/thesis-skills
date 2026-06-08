from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.pack_exporter import export_rule_pack_bundle


def main() -> int:
    parser = argparse.ArgumentParser(description="Export a linted rule pack bundle")
    parser.add_argument("--pack-path", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    try:
        path = export_rule_pack_bundle(args.pack_path, args.output)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(path.as_posix())
    return 0


if __name__ == "__main__":
    sys.exit(main())
