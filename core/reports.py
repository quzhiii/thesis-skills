from __future__ import annotations

import json
from pathlib import Path

from core.common import Finding


def write_report(
    report_path: str | Path,
    checker: str,
    ruleset: str,
    findings: list[Finding],
    extra_summary: dict[str, object] | None = None,
    extra_payload: dict[str, object] | None = None,
) -> int:
    errors = sum(1 for item in findings if item.severity == "error")
    warnings = sum(1 for item in findings if item.severity == "warning")
    infos = sum(1 for item in findings if item.severity == "info")
    summary: dict[str, object] = {
        "checker": checker,
        "ruleset": ruleset,
        "errors": errors,
        "warnings": warnings,
        "infos": infos,
        "status": "FAIL" if errors else "PASS",
    }
    if extra_summary:
        summary.update(extra_summary)
    payload = {
        "summary": summary,
        "findings": [item.as_dict() for item in findings],
    }
    if extra_payload:
        payload.update(extra_payload)
    report_path = Path(report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return 1 if errors else 0
