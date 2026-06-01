from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AuditSourceSpec:
    id: str
    title: str
    path: str
    required: bool = False


FINAL_AUDIT_SOURCES: tuple[AuditSourceSpec, ...] = (
    AuditSourceSpec("final_cleanup", "Final cleanup", "reports/final-cleanup-report.json", True),
    AuditSourceSpec("statistical_consistency", "Statistical consistency", "reports/statistical-consistency-report.json", True),
    AuditSourceSpec("manual_anchor", "Manual anchor", "reports/manual-anchor-report.json", True),
    AuditSourceSpec("readiness", "Readiness gate", "reports/readiness-report.json"),
    AuditSourceSpec("citation_integrity", "Citation integrity", "reports/citation-integrity-report.json"),
    AuditSourceSpec("final_reference_set", "Final reference set", "reports/final-reference-set-report.json"),
    AuditSourceSpec("external_verification", "External reference verification", "reports/external-verification-report.json"),
    AuditSourceSpec("doi_candidates", "Missing DOI candidates", "reports/missing-doi-candidates.json"),
    AuditSourceSpec("url_verification", "URL verification", "reports/url-verification-report.json"),
    AuditSourceSpec("hallucination_risk", "Hallucination risk", "reports/hallucination-risk-report.json"),
    AuditSourceSpec("claim_citation", "Claim-citation support", "reports/claim-citation-triage-report.json"),
)


_VERDICT_RANK = {"PASS": 0, "WARN": 1, "BLOCK": 2}


def _load_json(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def _summary(payload: dict[str, object]) -> dict[str, object]:
    summary = payload.get("summary")
    return summary if isinstance(summary, dict) else {}


def _status_from_checker_summary(summary: dict[str, object]) -> tuple[str, str, int, int, int]:
    errors = summary.get("errors", 0)
    warnings = summary.get("warnings", 0)
    infos = summary.get("infos", 0)
    error_count = errors if isinstance(errors, int) else 0
    warning_count = warnings if isinstance(warnings, int) else 0
    info_count = infos if isinstance(infos, int) else 0
    status = summary.get("status")
    if status == "PASS":
        return "PASS", "checker reported no findings", error_count, warning_count, info_count
    if error_count > 0:
        return "BLOCK", "checker reported blocking findings", error_count, warning_count, info_count
    if warning_count > 0 or status == "FAIL":
        return "WARN", "checker reported review findings", error_count, warning_count, info_count
    return "WARN", "checker report status is unknown", error_count, warning_count, info_count


def _module_status_dimension(payload: dict[str, object], source_id: str) -> tuple[str, str, dict[str, object]]:
    status = payload.get("status")
    summary = _summary(payload)
    extra: dict[str, object] = {"status": status} if isinstance(status, str) else {}
    if source_id == "readiness":
        verdict = payload.get("overall_verdict")
        if verdict in {"PASS", "WARN", "BLOCK"}:
            return str(verdict), "readiness gate verdict imported", extra
        return "WARN", "readiness report has unknown verdict", extra
    if source_id == "citation_integrity":
        if status == "BLOCK":
            return "BLOCK", "citation integrity reported blocking issues", extra
        if status == "WARN":
            return "WARN", "citation integrity reported warnings", extra
        if status == "PASS":
            return "PASS", "citation integrity reported no blockers", extra
        return "WARN", "citation integrity status is unknown", extra
    if source_id == "final_reference_set":
        issues = payload.get("issues")
        issue_list = [item for item in issues if isinstance(item, dict)] if isinstance(issues, list) else []
        error_count = sum(1 for item in issue_list if item.get("severity") == "error")
        warning_count = sum(1 for item in issue_list if item.get("severity") == "warn")
        extra.update({"errors": error_count, "warnings": warning_count, "issues": len(issue_list)})
        if error_count > 0:
            return "BLOCK", "final reference set reported missing final bibliography entries", extra
        if warning_count > 0:
            return "WARN", "final reference set reported review issues", extra
        return "PASS", "final reference set reported no blocking issues", extra
    if source_id == "external_verification":
        if status == "PASS":
            return "PASS", "external verification reported strong matches", extra
        if status in {"WARN", "REVIEW", "UNAVAILABLE", "NO_CANDIDATE"}:
            return "WARN", "external verification reported advisory review items", extra
        return "WARN", "external verification status is unknown", extra
    if source_id == "doi_candidates":
        candidates = payload.get("candidates")
        count = len(candidates) if isinstance(candidates, list) else int(summary.get("candidate_count", 0) or 0)
        extra["candidate_count"] = count
        if count > 0:
            return "WARN", "missing DOI candidates are available for manual review", extra
        return "PASS", "no missing DOI candidates reported", extra
    if source_id == "url_verification":
        flagged = payload.get("flagged")
        count = len(flagged) if isinstance(flagged, list) else int(summary.get("flagged_urls", 0) or 0)
        extra["flagged_urls"] = count
        if count > 0 or status in {"WARN", "REVIEW"}:
            return "WARN", "URL verification reported flagged URLs", extra
        if status == "PASS":
            return "PASS", "URL verification reported no flagged URLs", extra
        return "WARN", "URL verification status is unknown", extra
    if source_id == "hallucination_risk":
        if status == "HIGH_RISK":
            return "WARN", "hallucination risk reported high-risk references for manual verification", extra
        if status in {"WARN", "REVIEW"}:
            return "WARN", "hallucination risk reported review items", extra
        if status in {"PASS", "UNSUPPORTED"}:
            return "PASS", "hallucination risk reported no blocking findings", extra
        return "WARN", "hallucination risk status is unknown", extra
    if source_id == "claim_citation":
        if status == "ORPHANED":
            return "BLOCK", "claim-citation triage found orphaned citation keys", extra
        if status in {"WEAK", "UNVERIFIABLE"}:
            return "WARN", "claim-citation triage reported review items", extra
        if status in {"WELL_SUPPORTED", "SUPPORTED", "PASS"}:
            return "PASS", "claim-citation triage reported no blocking findings", extra
        return "WARN", "claim-citation status is unknown", extra
    return "WARN", "report type is not mapped", extra


def _dimension_from_payload(spec: AuditSourceSpec, payload: dict[str, object]) -> dict[str, object]:
    summary = _summary(payload)
    if isinstance(summary.get("checker"), str):
        verdict, reason, errors, warnings, infos = _status_from_checker_summary(summary)
        return {
            "id": spec.id,
            "title": spec.title,
            "verdict": verdict,
            "evidence_status": "present",
            "source": spec.path,
            "reason": reason,
            "errors": errors,
            "warnings": warnings,
            "infos": infos,
            "summary": summary,
        }

    verdict, reason, extra = _module_status_dimension(payload, spec.id)
    return {
        "id": spec.id,
        "title": spec.title,
        "verdict": verdict,
        "evidence_status": "present",
        "source": spec.path,
        "reason": reason,
        "summary": summary,
        **extra,
    }


def _missing_dimension(spec: AuditSourceSpec) -> dict[str, object]:
    return {
        "id": spec.id,
        "title": spec.title,
        "verdict": "WARN",
        "evidence_status": "missing",
        "source": spec.path,
        "reason": "required evidence missing" if spec.required else "optional evidence missing",
        "required": spec.required,
    }


def _unreadable_dimension(spec: AuditSourceSpec) -> dict[str, object]:
    return {
        "id": spec.id,
        "title": spec.title,
        "verdict": "WARN",
        "evidence_status": "unreadable",
        "source": spec.path,
        "reason": "evidence JSON could not be read",
        "required": spec.required,
    }


def _issue_from_dimension(dimension: dict[str, object]) -> dict[str, object]:
    return {
        "dimension": dimension.get("id", ""),
        "title": dimension.get("title", ""),
        "verdict": dimension.get("verdict", "WARN"),
        "evidence_status": dimension.get("evidence_status", "missing"),
        "source": dimension.get("source", ""),
        "reason": dimension.get("reason", ""),
    }


def build_final_audit_report(project_root: str | Path, ruleset: str) -> dict[str, object]:
    root = Path(project_root)
    dimensions: dict[str, dict[str, object]] = {}
    sources: list[dict[str, object]] = []
    for spec in FINAL_AUDIT_SOURCES:
        path = root / spec.path
        if not path.exists():
            dimension = _missing_dimension(spec)
        else:
            payload = _load_json(path)
            dimension = _unreadable_dimension(spec) if payload is None else _dimension_from_payload(spec, payload)
        dimensions[spec.id] = dimension
        sources.append(
            {
                "id": spec.id,
                "title": spec.title,
                "path": spec.path,
                "status": dimension["evidence_status"],
                "required": spec.required,
            }
        )

    blockers = [_issue_from_dimension(item) for item in dimensions.values() if item.get("verdict") == "BLOCK"]
    warnings = [_issue_from_dimension(item) for item in dimensions.values() if item.get("verdict") == "WARN"]
    overall = "PASS"
    for dimension in dimensions.values():
        verdict = str(dimension.get("verdict", "WARN"))
        if _VERDICT_RANK.get(verdict, 1) > _VERDICT_RANK[overall]:
            overall = verdict
    missing_required = sum(
        1
        for item in dimensions.values()
        if item.get("required") and item.get("evidence_status") in {"missing", "unreadable"}
    )
    next_actions: list[str] = []
    for issue in blockers:
        next_actions.append(f"Resolve blocking findings in {issue['dimension']}.")
    for issue in warnings:
        if issue.get("evidence_status") in {"missing", "unreadable"}:
            next_actions.append(f"Generate or repair evidence for {issue['dimension']}.")
        else:
            next_actions.append(f"Review remaining risk in {issue['dimension']}.")

    return {
        "module": "final_audit_report",
        "ruleset": ruleset,
        "overall_verdict": overall,
        "summary": {
            "headline": f"Final audit verdict: {overall}",
            "dimension_count": len(dimensions),
            "blocker_count": len(blockers),
            "warning_count": len(warnings),
            "missing_required_evidence_count": missing_required,
            "source_of_truth": "JSON reports remain authoritative; this artifact aggregates them without rerunning checks or rewriting source files.",
        },
        "dimensions": dimensions,
        "blockers": blockers,
        "warnings": warnings,
        "next_actions": list(dict.fromkeys(next_actions)),
        "sources": sources,
        "future_html": {
            "report_index": "Use sources as the report index input.",
            "issue_cards": "Use blockers and warnings as grouped card data for static HTML surfaces.",
            "cross_links": "Use each dimension source path for local links to raw JSON evidence.",
        },
    }


def write_final_audit_report(report: dict[str, object], output: str | Path) -> None:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
