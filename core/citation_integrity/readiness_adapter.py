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


def external_verification_dimension(project_root: str | Path) -> dict[str, object] | None:
    path = Path(project_root) / "reports" / "external-verification-report.json"
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {
            "verdict": "WARN",
            "evidence_status": "present",
            "reason": "external-verification-report.json is unreadable",
            "source": "external-verification-report.json",
        }
    if not isinstance(payload, dict):
        return None

    status = payload.get("status")
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    review_entries = summary.get("review_entries", 0)
    matched_entries = summary.get("matched_entries", 0)
    network_failures = summary.get("network_failures", 0)

    if status == "PASS":
        verdict = "PASS"
        reason = "external verification reported strong matches"
    elif status in {"WARN", "REVIEW", "UNAVAILABLE", "NO_CANDIDATE"}:
        verdict = "WARN"
        if status == "REVIEW":
            reason = "external verification reported entries needing manual review"
        elif status == "UNAVAILABLE":
            reason = "external verification was unavailable; local checks remain authoritative"
        elif status == "NO_CANDIDATE":
            reason = "external verification found no candidates for some entries"
        else:
            reason = "external verification reported advisory warnings"
    else:
        verdict = "WARN"
        reason = "external verification report has unknown status"

    return {
        "verdict": verdict,
        "evidence_status": "present",
        "reason": reason,
        "source": "external-verification-report.json",
        "matched_entries": matched_entries if isinstance(matched_entries, int) else 0,
        "review_entries": review_entries if isinstance(review_entries, int) else 0,
        "network_failures": network_failures if isinstance(network_failures, int) else 0,
    }
