from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.pack_generator import create_rule_pack


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a new rule pack from a starter"
    )
    parser.add_argument("--pack-id", required=True)
    parser.add_argument("--display-name", required=True)
    parser.add_argument(
        "--starter",
        choices=["university-generic", "journal-generic", "tsinghua-thesis"],
        required=True,
    )
    parser.add_argument(
        "--kind", choices=["university-thesis", "journal"], required=True
    )
    parser.add_argument(
        "--output-root", default=str(Path(__file__).resolve().parent / "packs")
    )
    args = parser.parse_args()
    path = create_rule_pack(
        Path(__file__).resolve().parents[1],
        args.output_root,
        args.pack_id,
        args.display_name,
        args.starter,
        args.kind,
    )
    print(path.as_posix())
    return 0


if __name__ == "__main__":
    sys.exit(main())
