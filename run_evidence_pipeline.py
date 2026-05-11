from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent


def _run(script: Path, project_root: Path, ruleset: str) -> int:
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--project-root",
            str(project_root),
            "--ruleset",
            ruleset,
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if result.stdout.strip():
        try:
            payload = json.loads(result.stdout.strip())
            if isinstance(payload, dict) and "summary" in payload:
                pass
        except json.JSONDecodeError:
            pass
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run all citation evidence pipeline steps in sequence"
    )
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--ruleset", default="tsinghua-thesis")
    parser.add_argument("--skip-external", action="store_true")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    steps: list[tuple[str, Path]] = [
        ("references", REPO_ROOT / "10-check-references" / "check_references.py"),
    ]
    if not args.skip_external:
        steps.append(
            ("external_verification", REPO_ROOT / "18-verify-references" / "verify_external_references.py")
        )
    steps.extend(
        [
            ("hallucination_risk", REPO_ROOT / "19-check-hallucination-risk" / "check_hallucination_risk.py"),
            ("claim_citation", REPO_ROOT / "20-check-claim-citation" / "check_claim_citation.py"),
        ]
    )

    summary: dict[str, object] = {}
    overall = 0
    for name, script in steps:
        exit_code = _run(script, project_root, args.ruleset)
        summary[name] = {"exit_code": exit_code}
        if exit_code != 0 and overall == 0:
            overall = 1

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return overall


if __name__ == "__main__":
    sys.exit(main())