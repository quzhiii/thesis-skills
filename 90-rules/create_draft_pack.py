from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.pack_generator import create_draft_pack


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a draft rule pack from intake metadata"
    )
    parser.add_argument("--intake", required=True)
    parser.add_argument(
        "--output-root", default=str(Path(__file__).resolve().parent / "packs")
    )
    args = parser.parse_args()
    path = create_draft_pack(
        Path(__file__).resolve().parents[1], args.output_root, args.intake
    )
    print(path.as_posix())
    return 0


if __name__ == "__main__":
    sys.exit(main())
