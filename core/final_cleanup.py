from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from core.common import Finding
from core.project import ThesisProject
from core.reports import write_report
from core.rules import RulePack


@dataclass(frozen=True)
class CleanupPattern:
    id: str
    label: str
    regex: re.Pattern[str]
    severity: str = "error"
    risk_level: str = "P0"


_PATTERN_SPECS: tuple[tuple[str, str, str, int], ...] = (
    ("TODO", "TODO", r"\bTODO\b", re.IGNORECASE),
    ("FIXME", "FIXME", r"\bFIXME\b", re.IGNORECASE),
    ("NEEDS_REVISION_ZH", "待修改", r"待修改", 0),
    ("NEEDS_CHECK_ZH", "待核查", r"待核查", 0),
    ("SCREENSHOT_REF_ZH", "见截图", r"见截图", 0),
    ("CHANGE_HERE_ZH", "这里再改", r"这里再改", 0),
    ("TEMPORARY_ZH", "临时", r"临时", 0),
    ("PLACEHOLDER_ZH", "占位", r"占位", 0),
    ("QUESTION_MARKERS", "???", r"\?\?\?", 0),
    ("TEXTCOLOR_BLUE", r"\textcolor{blue}", r"\\textcolor\s*\{\s*blue\s*\}", 0),
    ("COLOR_BLUE", r"\color{blue}", r"\\color\s*\{\s*blue\s*\}", 0),
    ("DRAFT", "draft", r"(?<![A-Za-z0-9_])draft(?![A-Za-z0-9_])", re.IGNORECASE),
    ("DEBUG", "debug", r"(?<![A-Za-z0-9_])debug(?![A-Za-z0-9_])", re.IGNORECASE),
)


def default_cleanup_patterns() -> list[CleanupPattern]:
    return [
        CleanupPattern(pattern_id, label, re.compile(regex, flags))
        for pattern_id, label, regex, flags in _PATTERN_SPECS
    ]


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


def collect_final_cleanup_findings(
    project: ThesisProject,
    patterns: list[CleanupPattern] | None = None,
) -> tuple[list[Finding], list[str], list[CleanupPattern]]:
    active_patterns = patterns if patterns is not None else default_cleanup_patterns()
    findings: list[Finding] = []
    source_files = _source_files(project)
    for path in source_files:
        rel = project.rel(path)
        text = path.read_text(encoding="utf-8", errors="ignore")
        for line_no, line in enumerate(text.splitlines(), start=1):
            for pattern in active_patterns:
                for match in pattern.regex.finditer(line):
                    findings.append(
                        Finding(
                            pattern.severity,
                            f"FINAL_CLEANUP_{pattern.id}",
                            f"Final cleanup residue detected: {pattern.label}",
                            rel,
                            line_no,
                            "Resolve or remove this process marker before final submission; this checker does not modify source files.",
                            span={"start": match.start() + 1, "end": match.end()},
                            evidence=line.strip(),
                            review_required=True,
                            category="final_cleanup",
                            original_text=match.group(0),
                            rationale="Process residue in a final thesis source can leak into handoff, PDF review, or submission workflows.",
                            risk_level=pattern.risk_level,
                        )
                    )
    return findings, [project.rel(path) for path in source_files], active_patterns


def run_final_cleanup_check(
    project: ThesisProject,
    pack: RulePack,
    report_path: str | Path,
) -> int:
    findings, source_files, patterns = collect_final_cleanup_findings(project)
    extra_summary = {
        "files_scanned": len(source_files),
        "residue_findings": len(findings),
        "patterns_scanned": len(patterns),
        "report_role": "final_audit_foundation",
    }
    extra_payload = {
        "source_files": source_files,
        "patterns": [
            {
                "id": pattern.id,
                "label": pattern.label,
                "severity": pattern.severity,
                "risk_level": pattern.risk_level,
            }
            for pattern in patterns
        ],
        "future_integration": {
            "final_audit_report": "Aggregate this report as the final_cleanup section of reports/final-audit-report.json.",
            "html_surface": "Render findings as issue cards grouped by risk_level, with file, line, evidence, and suggestion fields.",
        },
    }
    return write_report(
        report_path,
        "check_final_cleanup",
        pack.ruleset,
        findings,
        extra_summary,
        extra_payload,
    )
