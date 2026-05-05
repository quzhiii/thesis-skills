from __future__ import annotations

import json
from pathlib import Path


def citation_integrity_dimension(project_root: str | Path) -> dict[str, object] | None:
    path = Path(project_root) / "reports" / "citation-integrity-report.json"
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {
            "verdict": "WARN",
            "evidence_status": "present",
            "reason": "citation-integrity-report.json is unreadable",
            "source": "citation-integrity-report.json",
        }
    if not isinstance(payload, dict):
        return None

    status = payload.get("status")
    issues = payload.get("issues")
    issue_count = len(issues) if isinstance(issues, list) else 0
    if status == "BLOCK":
        verdict = "BLOCK"
        reason = "citation integrity reported blocking findings"
    elif status == "WARN":
        verdict = "WARN"
        reason = "citation integrity reported warnings"
    elif status == "PASS":
        verdict = "PASS"
        reason = "citation integrity reported no blockers"
    else:
        verdict = "WARN"
        reason = "citation integrity report has unknown status"
    return {
        "verdict": verdict,
        "evidence_status": "present",
        "reason": reason,
        "source": "citation-integrity-report.json",
        "issue_count": issue_count,
    }
