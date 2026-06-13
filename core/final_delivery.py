from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def _run(cmd: list[str], cwd: Path) -> dict[str, Any]:
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    payload: dict[str, object] = {"exit_code": proc.returncode}
    if proc.stdout.strip():
        try:
            payload["summary"] = json.loads(proc.stdout)
        except json.JSONDecodeError:
            payload["stdout"] = proc.stdout
    if proc.stderr.strip():
        payload["stderr"] = proc.stderr
    return payload


def run_final_delivery(
    project_root: str | Path,
    ruleset: str = "university-generic",
    *,
    skip_evidence: bool = False,
    fix_preview: bool = False,
    fix_apply: bool = False,
) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[1]
    project_root = Path(project_root).resolve()
    reports_dir = project_root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    steps: dict[str, Any] = {}

    if not skip_evidence:
        evidence_script = repo_root / "run_evidence_pipeline.py"
        if evidence_script.exists():
            steps["evidence-pipeline"] = _run(
                [sys.executable, str(evidence_script),
                 "--project-root", str(project_root),
                 "--ruleset", ruleset],
                repo_root,
            )

    final_cleanup_script = repo_root / "23-check-final-cleanup" / "check_final_cleanup.py"
    stat_script = repo_root / "25-check-statistical-consistency" / "check_statistical_consistency.py"
    anchor_script = repo_root / "26-check-manual-anchor" / "check_manual_anchor.py"

    final_audit_checks: dict[str, Any] = {}
    if final_cleanup_script.exists():
        final_audit_checks["final-cleanup"] = _run(
            [sys.executable, str(final_cleanup_script),
             "--project-root", str(project_root),
             "--ruleset", ruleset],
            repo_root,
        )
    if stat_script.exists():
        final_audit_checks["statistical-consistency"] = _run(
            [sys.executable, str(stat_script),
             "--project-root", str(project_root),
             "--ruleset", ruleset],
            repo_root,
        )
    if anchor_script.exists():
        final_audit_checks["manual-anchor"] = _run(
            [sys.executable, str(anchor_script),
             "--project-root", str(project_root),
             "--ruleset", ruleset],
            repo_root,
        )
    steps["final-audit-checks"] = final_audit_checks

    if fix_preview or fix_apply:
        fix_script = repo_root / "run_fix_cycle.py"
        if fix_script.exists():
            fix_mode = "final-audit"
            apply_flag = "true" if fix_apply else "false"
            steps["fix-preview"] = _run(
                [sys.executable, str(fix_script),
                 "--project-root", str(project_root),
                 "--ruleset", ruleset,
                 "--apply-mode", fix_mode,
                 "--apply", apply_flag],
                repo_root,
            )

    build_final_audit = repo_root / "27-final-audit-report" / "build_final_audit_report.py"
    build_ledger = repo_root / "28-reference-audit-ledger" / "build_reference_audit_ledger.py"
    build_index = repo_root / "29-report-index" / "build_report_index.py"
    build_final_audit_html = repo_root / "30-final-audit-html" / "build_final_audit_html.py"
    build_ledger_html = repo_root / "31-reference-ledger-html" / "build_reference_audit_ledger_html.py"
    build_claim_html = repo_root / "32-claim-citation-html" / "build_claim_citation_html.py"

    bundle_steps: dict[str, Any] = {}
    if build_final_audit.exists():
        bundle_steps["final-audit-report"] = _run(
            [sys.executable, str(build_final_audit),
             "--project-root", str(project_root),
             "--ruleset", ruleset],
            repo_root,
        )
    if build_ledger.exists():
        bundle_steps["reference-audit-ledger"] = _run(
            [sys.executable, str(build_ledger),
             "--project-root", str(project_root),
             "--ruleset", ruleset],
            repo_root,
        )
    if build_index.exists():
        bundle_steps["report-index"] = _run(
            [sys.executable, str(build_index),
             "--project-root", str(project_root)],
            repo_root,
        )
    if build_final_audit_html.exists():
        bundle_steps["final-audit-html"] = _run(
            [sys.executable, str(build_final_audit_html),
             "--project-root", str(project_root)],
            repo_root,
        )
    if build_ledger_html.exists():
        bundle_steps["reference-ledger-html"] = _run(
            [sys.executable, str(build_ledger_html),
             "--project-root", str(project_root)],
            repo_root,
        )
    if build_claim_html.exists():
        claim_json = reports_dir / "claim-citation-triage-report.json"
        if claim_json.exists():
            bundle_steps["claim-citation-html"] = _run(
                [sys.executable, str(build_claim_html),
                 "--project-root", str(project_root)],
                repo_root,
            )
    steps["bundle-rebuild"] = bundle_steps

    summary = {
        "workflow": "final-delivery",
        "ruleset": ruleset,
        "project_root": str(project_root),
        "skip_evidence": skip_evidence,
        "fix_preview": fix_preview,
        "fix_apply": fix_apply,
        "steps": steps,
    }
    return summary
