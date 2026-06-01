from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from core.common import Finding
from core.project import ThesisProject
from core.reports import write_report
from core.rules import RulePack


@dataclass(frozen=True)
class StatisticalVariant:
    label: str
    regex: re.Pattern[str]


@dataclass(frozen=True)
class StatisticalFamily:
    id: str
    name: str
    variants: tuple[StatisticalVariant, ...]


@dataclass(frozen=True)
class StatisticalOccurrence:
    family_id: str
    family_name: str
    variant: str
    file: str
    line: int
    span: dict[str, int]
    evidence: str
    matched_text: str


def _variant(label: str, regex: str, flags: int = 0) -> StatisticalVariant:
    return StatisticalVariant(label, re.compile(regex, flags))


STATISTICAL_FAMILIES: tuple[StatisticalFamily, ...] = (
    StatisticalFamily(
        "p_value_term",
        "p-value term",
        (
            _variant("p值", r"p\s*值"),
            _variant("P值", r"P\s*值"),
        ),
    ),
    StatisticalFamily(
        "p_equals",
        "p equals notation",
        (
            _variant("p=", r"p\s*="),
            _variant("P=", r"P\s*="),
        ),
    ),
    StatisticalFamily(
        "q_value_term",
        "q-value term",
        (
            _variant("q值", r"q\s*值"),
            _variant("Q值", r"Q\s*值"),
        ),
    ),
    StatisticalFamily(
        "ci_95",
        "95% confidence interval notation",
        (
            _variant("95%CI", r"95\s*%\s*CI"),
            _variant(r"95\%CI", r"95\s*\\%\s*CI"),
            _variant("95% 置信区间", r"95\s*%\s+置信区间"),
            _variant("95%置信区间", r"95\s*%\s*置信区间"),
            _variant(r"95\%置信区间", r"95\s*\\%\s*置信区间"),
        ),
    ),
    StatisticalFamily(
        "bootstrap_term",
        "bootstrap terminology",
        (
            _variant("Bootstrap", r"Bootstrap", re.IGNORECASE),
            _variant("自助法", r"自助法"),
            _variant("自助抽样", r"自助抽样"),
        ),
    ),
    StatisticalFamily(
        "smd_term",
        "standardized mean difference terminology",
        (
            _variant("SMD", r"(?<![A-Za-z0-9_])SMD(?![A-Za-z0-9_])", re.IGNORECASE),
            _variant("标准化均数差", r"标准化均数差"),
        ),
    ),
)


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


def collect_statistical_occurrences(project: ThesisProject) -> tuple[list[StatisticalOccurrence], list[str]]:
    occurrences: list[StatisticalOccurrence] = []
    source_files = _source_files(project)
    for path in source_files:
        rel = project.rel(path)
        text = path.read_text(encoding="utf-8", errors="ignore")
        for line_no, line in enumerate(text.splitlines(), start=1):
            for family in STATISTICAL_FAMILIES:
                for variant in family.variants:
                    for match in variant.regex.finditer(line):
                        occurrences.append(
                            StatisticalOccurrence(
                                family.id,
                                family.name,
                                variant.label,
                                rel,
                                line_no,
                                {"start": match.start() + 1, "end": match.end()},
                                line.strip(),
                                match.group(0),
                            )
                        )
    return occurrences, [project.rel(path) for path in source_files]


def _dominant_variant(counts: dict[str, int]) -> str:
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]


def build_statistical_consistency_report(project: ThesisProject, ruleset: str) -> dict[str, object]:
    occurrences, source_files = collect_statistical_occurrences(project)
    occurrences_by_family: dict[str, list[StatisticalOccurrence]] = {}
    for occurrence in occurrences:
        occurrences_by_family.setdefault(occurrence.family_id, []).append(occurrence)

    findings: list[Finding] = []
    family_summaries: list[dict[str, object]] = []
    for family in STATISTICAL_FAMILIES:
        family_occurrences = occurrences_by_family.get(family.id, [])
        counts: dict[str, int] = {}
        for occurrence in family_occurrences:
            counts[occurrence.variant] = counts.get(occurrence.variant, 0) + 1

        dominant = _dominant_variant(counts) if counts else ""
        used_variants = [variant for variant, count in sorted(counts.items()) if count > 0]
        mixed = len(used_variants) > 1
        family_summaries.append(
            {
                "family_id": family.id,
                "name": family.name,
                "counts": counts,
                "dominant_variant": dominant,
                "mixed": mixed,
            }
        )
        if not mixed:
            continue
        for occurrence in family_occurrences:
            if occurrence.variant == dominant:
                continue
            findings.append(
                Finding(
                    "warning",
                    "STAT_MIXED_NOTATION",
                    f"Statistical notation mixes {occurrence.variant} with dominant style {dominant}",
                    occurrence.file,
                    occurrence.line,
                    f"Review whether this should be normalized to {dominant}; this checker does not rewrite statistical notation.",
                    span=occurrence.span,
                    evidence=occurrence.evidence,
                    review_required=True,
                    category="statistical_consistency",
                    original_text=occurrence.matched_text,
                    rationale="The final-audit rule reports deviations from the dominant notation style instead of forcing a global preference.",
                    risk_level="P1",
                )
            )

    summary = {
        "checker": "check_statistical_consistency",
        "ruleset": ruleset,
        "errors": 0,
        "warnings": len(findings),
        "infos": 0,
        "status": "FAIL" if findings else "PASS",
        "files_scanned": len(source_files),
        "families_scanned": len(STATISTICAL_FAMILIES),
        "mixed_families": sum(1 for family in family_summaries if family["mixed"]),
        "occurrences_scanned": len(occurrences),
        "report_role": "final_audit_foundation",
    }
    return {
        "summary": summary,
        "findings": [finding.as_dict() for finding in findings],
        "source_files": source_files,
        "families": family_summaries,
        "occurrences": [occurrence.__dict__ for occurrence in occurrences],
        "future_integration": {
            "final_audit_report": "Aggregate this report as the statistical_consistency section of reports/final-audit-report.json.",
            "html_surface": "Render mixed families as grouped issue cards with dominant style, deviation evidence, file, and line.",
        },
    }


def write_statistical_consistency_report(report: dict[str, object], output: str | Path) -> None:
    import json

    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def run_statistical_consistency_check(
    project: ThesisProject,
    pack: RulePack,
    report_path: str | Path,
) -> int:
    report = build_statistical_consistency_report(project, pack.ruleset)
    write_statistical_consistency_report(report, report_path)
    summary = report["summary"]
    return 1 if isinstance(summary, dict) and summary.get("status") == "FAIL" else 0
