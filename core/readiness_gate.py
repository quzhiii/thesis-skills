from __future__ import annotations

import json
from pathlib import Path
from typing import Any


VALID_MODES = {"advisor-handoff", "submission-prep"}


def resolve_gate_mode(mode: str) -> str:
    if mode not in VALID_MODES:
        raise ValueError(
            f"Unsupported readiness gate mode: {mode}. Expected one of: advisor-handoff, submission-prep"
        )
    return mode


def _load_json(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def _missing_source(path: str, *, reason: str) -> dict[str, object]:
    return {
        "status": "missing",
        "path": path,
        "reason": reason,
    }


def _present_source(path: str, payload: dict[str, object], **extra: object) -> dict[str, object]:
    source: dict[str, object] = {
        "status": "present",
        "path": path,
        "payload": payload,
    }
    source.update(extra)
    return source


def collect_readiness_sources(project_root: str | Path) -> dict[str, dict[str, object]]:
    root = Path(project_root)
    reports_dir = root / "reports"

    run_summary_path = reports_dir / "run-summary.json"
    fix_summary_path = reports_dir / "fix-summary.json"
    export_report_path = reports_dir / "latex_to_word-report.json"
    review_artifact_path = reports_dir / "review-diff-artifact.json"
    review_ingest_path = reports_dir / "review-ingest-artifact.json"

    run_summary = _load_json(run_summary_path)
    fix_summary = _load_json(fix_summary_path)
    export_report = _load_json(export_report_path)
    review_artifact = _load_json(review_artifact_path) or _load_json(review_ingest_path)

    report_paths: set[Path] = set()
    if isinstance(run_summary, dict):
        steps = run_summary.get("steps")
        if isinstance(steps, dict):
            for step in steps.values():
                if isinstance(step, dict):
                    report = step.get("report")
                    if isinstance(report, str):
                        report_paths.add(root / report)
    for path in sorted(reports_dir.glob("check_*-report.json")):
        report_paths.add(path)

    checker_reports: list[dict[str, object]] = []
    compile_payload: dict[str, object] | None = None
    for report_path in sorted(report_paths):
        payload = _load_json(report_path)
        if not payload:
            continue
        checker_reports.append(
            {
                "path": report_path.relative_to(root).as_posix(),
                "payload": payload,
            }
        )
        summary = payload.get("summary")
        checker_name = summary.get("checker") if isinstance(summary, dict) else None
        if checker_name == "check_compile":
            compile_payload = payload

    sources: dict[str, dict[str, object]] = {
        "run_summary": _present_source(
            run_summary_path.relative_to(root).as_posix(), run_summary
        )
        if run_summary
        else _missing_source(
            run_summary_path.relative_to(root).as_posix(),
            reason="run-summary.json not found",
        ),
        "fix_summary": _present_source(
            fix_summary_path.relative_to(root).as_posix(), fix_summary
        )
        if fix_summary
        else _missing_source(
            fix_summary_path.relative_to(root).as_posix(),
            reason="fix-summary.json not found",
        ),
        "checker_reports": {
            "status": "present" if checker_reports else "missing",
            "count": len(checker_reports),
            "reports": checker_reports,
            "reason": "No checker reports found" if not checker_reports else "",
        },
        "compile": _present_source(
            "reports/check_compile-report.json", compile_payload
        )
        if compile_payload
        else _missing_source(
            "reports/check_compile-report.json",
            reason="compile report not found",
        ),
        "export": _present_source(
            export_report_path.relative_to(root).as_posix(), export_report
        )
        if export_report
        else _missing_source(
            export_report_path.relative_to(root).as_posix(),
            reason="latex-to-word export report not found",
        ),
        "review_loop": _present_source(
            (review_artifact_path if review_artifact_path.exists() else review_ingest_path)
            .relative_to(root)
            .as_posix(),
            review_artifact,
        )
        if review_artifact
        else _missing_source(
            review_artifact_path.relative_to(root).as_posix(),
            reason="review-loop artifact not found",
        ),
    }
    return sources


def _checker_payload_by_name(sources: dict[str, dict[str, object]]) -> dict[str, dict[str, object]]:
    reports_source = sources.get("checker_reports", {})
    reports = reports_source.get("reports") if isinstance(reports_source, dict) else None
    result: dict[str, dict[str, object]] = {}
    if not isinstance(reports, list):
        return result
    for report in reports:
        if not isinstance(report, dict):
            continue
        payload = report.get("payload")
        if not isinstance(payload, dict):
            continue
        summary = payload.get("summary")
        checker_name = summary.get("checker") if isinstance(summary, dict) else None
        if isinstance(checker_name, str):
            result[checker_name] = payload
    return result


def _finding_counts(payload: dict[str, object]) -> tuple[int, int]:
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        return 0, 0
    errors = summary.get("errors", 0)
    warnings = summary.get("warnings", 0)
    return (
        errors if isinstance(errors, int) else 0,
        warnings if isinstance(warnings, int) else 0,
    )


def _build_dimension(verdict: str, evidence_status: str, reason: str, **extra: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "verdict": verdict,
        "evidence_status": evidence_status,
        "reason": reason,
    }
    payload.update(extra)
    return payload


def _evaluate_dimensions(
    sources: dict[str, dict[str, object]], mode: str
) -> dict[str, dict[str, object]]:
    payloads = _checker_payload_by_name(sources)

    def from_checker(checker_name: str, missing_reason: str) -> dict[str, object]:
        payload = payloads.get(checker_name)
        if payload is None:
            return _build_dimension("WARN", "missing", missing_reason)
        errors, warnings = _finding_counts(payload)
        if errors > 0:
            return _build_dimension("BLOCK", "present", f"{checker_name} reported blocking findings", errors=errors, warnings=warnings)
        if warnings > 0:
            return _build_dimension("WARN", "present", f"{checker_name} reported warnings", errors=errors, warnings=warnings)
        return _build_dimension("PASS", "present", f"{checker_name} reported no blockers", errors=errors, warnings=warnings)

    dimensions = {
        "references": from_checker("check_references", "references evidence missing"),
        "language": from_checker("check_language", "language evidence missing"),
        "format": from_checker("check_format", "format evidence missing"),
        "content": from_checker("check_content", "content evidence missing"),
    }

    compile_source = sources.get("compile", {})
    if compile_source.get("status") == "present":
        compile_payload = compile_source.get("payload")
        if isinstance(compile_payload, dict):
            errors, warnings = _finding_counts(compile_payload)
            verdict = "BLOCK" if errors > 0 else "WARN" if warnings > 0 else "PASS"
            reason = (
                "compile report contains blocking findings"
                if errors > 0
                else "compile report contains warnings"
                if warnings > 0
                else "compile report contains no blockers"
            )
            dimensions["compile"] = _build_dimension(
                verdict,
                "present",
                reason,
                errors=errors,
                warnings=warnings,
            )
        else:
            dimensions["compile"] = _build_dimension("WARN", "missing", "compile report payload unreadable")
    else:
        dimensions["compile"] = _build_dimension("WARN", "missing", "compile evidence missing")

    if mode == "submission-prep" and dimensions["compile"]["evidence_status"] == "missing":
        dimensions["compile"] = _build_dimension(
            "BLOCK",
            "missing",
            "submission-prep requires compile evidence before proceeding",
        )

    export_source = sources.get("export", {})
    if export_source.get("status") == "present":
        export_payload = export_source.get("payload")
        if isinstance(export_payload, dict):
            warnings_list = export_payload.get("warnings")
            unsupported = export_payload.get("unsupported_constructs")
            warning_count = len(warnings_list) if isinstance(warnings_list, list) else 0
            unsupported_count = len(unsupported) if isinstance(unsupported, list) else 0
            if unsupported_count > 0 or warning_count > 0:
                dimensions["export"] = _build_dimension(
                    "WARN",
                    "present",
                    "export report surfaces delivery risk",
                    warnings=warning_count,
                    unsupported_constructs=unsupported_count,
                )
            else:
                dimensions["export"] = _build_dimension(
                    "PASS",
                    "present",
                    "export report surfaces no delivery blockers",
                    warnings=0,
                    unsupported_constructs=0,
                )
        else:
            dimensions["export"] = _build_dimension("WARN", "missing", "export report payload unreadable")
    else:
        dimensions["export"] = _build_dimension("WARN", "missing", "export evidence missing")

    review_source = sources.get("review_loop", {})
    if review_source.get("status") == "present":
        review_payload = review_source.get("payload")
        if isinstance(review_payload, dict):
            payload_section = review_payload.get("payload")
            review_digest = payload_section.get("review_digest") if isinstance(payload_section, dict) else None
            total_items = review_digest.get("total_items", 0) if isinstance(review_digest, dict) else 0
            high_priority_items = review_digest.get("high_priority_items", 0) if isinstance(review_digest, dict) else 0
            if isinstance(total_items, int) and total_items > 0:
                dimensions["review_debt"] = _build_dimension(
                    "WARN",
                    "present",
                    "review-loop artifact contains unresolved review debt",
                    total_items=total_items,
                    high_priority_items=high_priority_items if isinstance(high_priority_items, int) else 0,
                )
            else:
                dimensions["review_debt"] = _build_dimension(
                    "PASS",
                    "present",
                    "review-loop artifact contains no unresolved review debt",
                    total_items=0,
                    high_priority_items=0,
                )
        else:
            dimensions["review_debt"] = _build_dimension("WARN", "missing", "review-loop payload unreadable")
    else:
        dimensions["review_debt"] = _build_dimension("WARN", "missing", "review-loop evidence missing")

    if mode == "submission-prep" and dimensions["review_debt"]["evidence_status"] == "present":
        total_items = dimensions["review_debt"].get("total_items", 0)
        if isinstance(total_items, int) and total_items > 0:
            dimensions["review_debt"] = _build_dimension(
                "BLOCK",
                "present",
                "submission-prep requires unresolved review debt to be cleared",
                total_items=total_items,
                high_priority_items=dimensions["review_debt"].get("high_priority_items", 0),
            )

    return dimensions


def _collect_issue_lists(dimensions: dict[str, dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]], list[str], str]:
    blockers: list[dict[str, object]] = []
    warnings: list[dict[str, object]] = []
    next_actions: list[str] = []

    for name, dimension in dimensions.items():
        verdict = dimension.get("verdict")
        reason = dimension.get("reason")
        item = {
            "dimension": name,
            "verdict": verdict,
            "evidence_status": dimension.get("evidence_status"),
            "reason": reason,
        }
        if verdict == "BLOCK":
            blockers.append(item)
            next_actions.append(f"Resolve blocking issues in {name}.")
        elif verdict == "WARN":
            warnings.append(item)
            if dimension.get("evidence_status") == "missing":
                next_actions.append(f"Generate or locate missing evidence for {name}.")
            else:
                next_actions.append(f"Review remaining risk in {name}.")

    if blockers:
        overall_verdict = "BLOCK"
    elif warnings:
        overall_verdict = "WARN"
    else:
        overall_verdict = "PASS"

    deduped_actions: list[str] = []
    seen: set[str] = set()
    for action in next_actions:
        if action not in seen:
            seen.add(action)
            deduped_actions.append(action)
    return blockers, warnings, deduped_actions, overall_verdict


def _source_refs(sources: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    refs: list[dict[str, object]] = []
    for name, source in sources.items():
        ref: dict[str, object] = {"name": name, "status": source.get("status")}
        if "path" in source:
            ref["path"] = source["path"]
        if "count" in source:
            ref["count"] = source["count"]
        if source.get("status") == "missing" and "reason" in source:
            ref["reason"] = source["reason"]
        refs.append(ref)
    return refs


def build_readiness_artifact(mode: str, project_root: str | Path | None = None) -> dict[str, object]:
    resolved_mode = resolve_gate_mode(mode)
    if project_root is None:
        return {
            "mode": resolved_mode,
            "overall_verdict": "WARN",
            "summary": {
                "headline": "Readiness gate scaffold created.",
                "evidence_status": "not-yet-evaluated",
            },
            "dimensions": {},
            "blockers": [],
            "warnings": [],
            "next_actions": [],
            "sources": [],
        }

    sources = collect_readiness_sources(project_root)
    dimensions = _evaluate_dimensions(sources, resolved_mode)
    blockers, warnings, next_actions, overall_verdict = _collect_issue_lists(dimensions)

    missing_count = sum(
        1
        for dimension in dimensions.values()
        if dimension.get("evidence_status") == "missing"
    )
    summary: dict[str, object] = {
        "headline": f"Readiness verdict: {overall_verdict}",
        "evidence_status": "partial" if missing_count else "complete",
        "dimension_count": len(dimensions),
        "missing_evidence_count": missing_count,
    }

    return {
        "mode": resolved_mode,
        "overall_verdict": overall_verdict,
        "summary": summary,
        "dimensions": dimensions,
        "blockers": blockers,
        "warnings": warnings,
        "next_actions": next_actions,
        "sources": _source_refs(sources),
    }
