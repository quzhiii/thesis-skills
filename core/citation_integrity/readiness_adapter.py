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


def hallucination_risk_dimension(project_root: str | Path) -> dict[str, object] | None:
    path = Path(project_root) / "reports" / "hallucination-risk-report.json"
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {
            "verdict": "WARN",
            "evidence_status": "present",
            "reason": "hallucination-risk-report.json is unreadable",
            "source": "hallucination-risk-report.json",
        }
    if not isinstance(payload, dict):
        return None

    status = payload.get("status")
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    pass_entries = summary.get("pass_entries", 0)
    warn_entries = summary.get("warn_entries", 0)
    review_entries = summary.get("review_entries", 0)
    high_risk_entries = summary.get("high_risk_entries", 0)
    unsupported_entries = summary.get("unsupported_entries", 0)

    if status == "PASS":
        verdict = "PASS"
        reason = "hallucination risk scoring reported no concerns"
    elif status == "UNSUPPORTED":
        verdict = "PASS"
        reason = "hallucination risk scoring found unsupported entries that cannot be auto-verified; manual review may be needed"
    elif status == "HIGH_RISK":
        verdict = "WARN"
        reason = "hallucination risk scoring flagged high-risk entries; manual verification strongly recommended"
    elif status in {"WARN", "REVIEW"}:
        verdict = "WARN"
        if status == "REVIEW":
            reason = "hallucination risk scoring reported entries needing manual review"
        else:
            reason = "hallucination risk scoring reported warnings"
    else:
        verdict = "WARN"
        reason = "hallucination risk report has unknown status"

    return {
        "verdict": verdict,
        "evidence_status": "present",
        "reason": reason,
        "source": "hallucination-risk-report.json",
        "pass_entries": pass_entries if isinstance(pass_entries, int) else 0,
        "warn_entries": warn_entries if isinstance(warn_entries, int) else 0,
        "review_entries": review_entries if isinstance(review_entries, int) else 0,
        "high_risk_entries": high_risk_entries if isinstance(high_risk_entries, int) else 0,
        "unsupported_entries": unsupported_entries if isinstance(unsupported_entries, int) else 0,
    }


def claim_citation_dimension(project_root: str | Path) -> dict[str, object] | None:
    path = Path(project_root) / "reports" / "claim-citation-triage-report.json"
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {
            "verdict": "WARN",
            "evidence_status": "present",
            "reason": "claim-citation-triage-report.json is unreadable",
            "source": "claim-citation-triage-report.json",
        }
    if not isinstance(payload, dict):
        return None

    status = payload.get("status")
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    claim_citation_pairs = summary.get("claim_citation_pairs", 0)
    orphaned_pairs = summary.get("orphaned_pairs", 0)
    weak_pairs = summary.get("weak_pairs", 0)
    unverifiable_pairs = summary.get("unverifiable_pairs", 0)

    if status == "ORPHANED":
        verdict = "BLOCK"
        reason = "claim-citation triage found orphaned citation keys with no bibliography entry"
    elif status in {"WELL_SUPPORTED", "SUPPORTED"}:
        verdict = "PASS"
        if status == "WELL_SUPPORTED":
            reason = "claim-citation triage reported all pairs well-supported"
        else:
            reason = "claim-citation triage reported minor risk signals"
    elif status in {"WEAK", "UNVERIFIABLE"}:
        verdict = "WARN"
        if status == "WEAK":
            reason = "claim-citation triage reported weakly-supported pairs"
        else:
            reason = "claim-citation triage found unverifiable pairs that cannot be auto-verified"
    else:
        verdict = "WARN"
        reason = "claim-citation triage report has unknown status"

    return {
        "verdict": verdict,
        "evidence_status": "present",
        "reason": reason,
        "source": "claim-citation-triage-report.json",
        "claim_citation_pairs": claim_citation_pairs if isinstance(claim_citation_pairs, int) else 0,
        "orphaned_pairs": orphaned_pairs if isinstance(orphaned_pairs, int) else 0,
        "weak_pairs": weak_pairs if isinstance(weak_pairs, int) else 0,
        "unverifiable_pairs": unverifiable_pairs if isinstance(unverifiable_pairs, int) else 0,
    }
