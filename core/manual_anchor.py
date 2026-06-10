from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from core.common import Finding
from core.project import ThesisProject
from core.rules import RulePack


_ADDCONTENTSLINE_RE = re.compile(
    r"\\addcontentsline\s*\{\s*(toc|lof|lot)\s*\}\s*\{\s*([^{}]+)\s*\}\s*\{",
)


@dataclass(frozen=True)
class ManualAnchorOccurrence:
    file: str
    line: int
    span: dict[str, int]
    list_name: str
    entry_type: str
    evidence: str
    has_phantomsection: bool
    preceding_window: list[str]


def _source_files(project: ThesisProject) -> list[Path]:
    files: list[Path] = []
    seen: set[Path] = set()
    for path in [project.main_tex, *project.chapter_files, project.abstract_file]:
        if path is None or not path.exists() or not path.is_file():
            continue
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        files.append(path)
    return files


def _has_phantomsection(lines: list[str], index: int, window: int) -> tuple[bool, list[str]]:
    start = max(0, index - window)
    preceding = lines[start:index]
    return any(r"\phantomsection" in line for line in preceding), [line.strip() for line in preceding]


def collect_manual_anchor_occurrences(
    project: ThesisProject,
    *,
    preceding_window: int = 3,
) -> tuple[list[ManualAnchorOccurrence], list[str]]:
    occurrences: list[ManualAnchorOccurrence] = []
    source_files = _source_files(project)
    for path in source_files:
        rel = project.rel(path)
        text = path.read_text(encoding="utf-8", errors="ignore")
        lines = text.splitlines()
        for index, line in enumerate(lines):
            for match in _ADDCONTENTSLINE_RE.finditer(line):
                has_anchor, preceding = _has_phantomsection(lines, index, preceding_window)
                occurrences.append(
                    ManualAnchorOccurrence(
                        rel,
                        index + 1,
                        {"start": match.start() + 1, "end": match.end()},
                        match.group(1),
                        match.group(2).strip(),
                        line.strip(),
                        has_anchor,
                        preceding,
                    )
                )
    return occurrences, [project.rel(path) for path in source_files]


def build_manual_anchor_report(project: ThesisProject, ruleset: str) -> dict[str, object]:
    occurrences, source_files = collect_manual_anchor_occurrences(project)
    findings: list[Finding] = []
    for occurrence in occurrences:
        if occurrence.has_phantomsection:
            continue
        findings.append(
            Finding(
                "warning",
                "ANCHOR_MISSING_PHANTOMSECTION",
                f"Manual {occurrence.list_name} contents line may be missing a preceding \\phantomsection anchor",
                occurrence.file,
                occurrence.line,
                "Add or verify a nearby \\phantomsection before this manual contents line; this checker does not edit anchors or numbering.",
                span=occurrence.span,
                evidence=occurrence.evidence,
                suggestions=["\\phantomsection"],
                confidence=0.90,
                review_required=False,
                category="manual_anchor",
                original_text=f"\\addcontentsline{{{occurrence.list_name}}}{{{occurrence.entry_type}}}",
                rationale="Manual contents entries without a local anchor can make TOC, LOF, or LOT links jump to the previous section, figure, or table.",
                risk_level="P1",
            )
        )

    summary = {
        "checker": "check_manual_anchor",
        "ruleset": ruleset,
        "errors": 0,
        "warnings": len(findings),
        "infos": 0,
        "status": "FAIL" if findings else "PASS",
        "files_scanned": len(source_files),
        "manual_contents_lines": len(occurrences),
        "missing_phantomsection": len(findings),
        "preceding_window_lines": 3,
        "report_role": "final_audit_foundation",
    }
    return {
        "summary": summary,
        "findings": [finding.as_dict() for finding in findings],
        "source_files": source_files,
        "manual_contents_lines": [occurrence.__dict__ for occurrence in occurrences],
        "future_integration": {
            "final_audit_report": "Aggregate this report as the manual_anchor section of reports/final-audit-report.json.",
            "html_surface": "Render missing-anchor findings as issue cards with nearby preceding lines for manual verification.",
        },
    }


def write_manual_anchor_report(report: dict[str, object], output: str | Path) -> None:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def run_manual_anchor_check(
    project: ThesisProject,
    pack: RulePack,
    report_path: str | Path,
) -> int:
    report = build_manual_anchor_report(project, pack.ruleset)
    write_manual_anchor_report(report, report_path)
    summary = report["summary"]
    return 1 if isinstance(summary, dict) and summary.get("status") == "FAIL" else 0
