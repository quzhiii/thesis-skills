from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

readiness_gate = importlib.import_module("core.readiness_gate")
build_readiness_artifact = readiness_gate.build_readiness_artifact


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Emit a bounded readiness gate artifact from existing workflow evidence"
    )
    parser.add_argument("--project-root")
    parser.add_argument("--ruleset", default="tsinghua-thesis")
    parser.add_argument("--mode", default="advisor-handoff")
    parser.add_argument("--report")
    args = parser.parse_args()

    artifact = build_readiness_artifact(mode=args.mode, project_root=args.project_root)
    report_path = (
        Path(args.report)
        if args.report
        else Path(args.project_root) / "reports" / "readiness-report.json"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(artifact, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
