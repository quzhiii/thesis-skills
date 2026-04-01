from __future__ import annotations

from dataclasses import dataclass
import re

from core.common import Finding
from core.consistency import analyze_terminology_group
from core.project import ThesisProject
from core.rules import RulePack
from core.terminology import (
    TextOccurrence,
    find_literal_occurrences,
    find_non_overlapping_literal_occurrences,
    find_token_occurrences,
)


@dataclass(frozen=True)
class ProjectText:
    file: str
    raw_text: str
    scan_text: str


@dataclass(frozen=True)
class DeepScanMeta:
    files_scanned: list[str]
    masked_construct_counts: dict[str, int]
    uncovered_risks: list[str]


def _rule_node(config: dict[str, object], key: str) -> dict[str, object]:
    node = config.get(key, {})
    return node if isinstance(node, dict) else {}


def _patterns(node: dict[str, object]) -> dict[str, dict[str, object]]:
    raw = node.get("patterns", {})
    if not isinstance(raw, dict):
        return {}
    return {
        str(key): value if isinstance(value, dict) else {}
        for key, value in raw.items()
    }


def _groups(node: dict[str, object]) -> dict[str, dict[str, object]]:
    raw = node.get("groups", {})
    if not isinstance(raw, dict):
        return {}
    return {
        str(key): value if isinstance(value, dict) else {}
        for key, value in raw.items()
    }


def _acronyms(node: dict[str, object]) -> dict[str, dict[str, object]]:
    raw = node.get("acronyms", {})
    if not isinstance(raw, dict):
        return {}
    return {
        str(key): value if isinstance(value, dict) else {}
        for key, value in raw.items()
    }


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _severity(node: dict[str, object], default: str = "warning") -> str:
    return str(node.get("severity", default))


def _confidence(node: dict[str, object], default: float = 0.7) -> float:
    value = node.get("min_confidence", default)
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _review_required(node: dict[str, object], default: bool = True) -> bool:
    return bool(node.get("review_required", default))


def _enabled(node: dict[str, object], default: bool = False) -> bool:
    return bool(node.get("enabled", default))


def _contains_variant(text: str, variant: str) -> bool:
    if any(ch.isascii() and ch.isalpha() for ch in variant):
        return variant.lower() in text.lower()
    return variant in text


def _build_finding(
    *,
    severity: str,
    code: str,
    message: str,
    occurrence: TextOccurrence,
    evidence: str,
    suggestions: list[str],
    confidence: float,
    review_required: bool,
    category: str,
    rationale: str,
) -> Finding:
    return Finding(
        severity=severity,
        code=code,
        message=message,
        file=occurrence.file,
        line=occurrence.line,
        suggestion=suggestions[0] if suggestions else "",
        span=occurrence.span,
        evidence=evidence,
        suggestions=suggestions,
        confidence=confidence,
        review_required=review_required,
        category=category,
        original_text=occurrence.text,
        rationale=rationale,
        risk_level="medium" if review_required else "low",
    )


def _collect_mask_spans(text: str, pattern: str, *, flags: int = 0) -> list[tuple[int, int]]:
    return [(match.start(), match.end()) for match in re.finditer(pattern, text, flags)]


def _apply_mask(text: str, spans: list[tuple[int, int]]) -> str:
    chars = list(text)
    for start, end in spans:
        for index in range(start, end):
            if chars[index] != "\n":
                chars[index] = " "
    return "".join(chars)


def _latex_aware_scan_text(text: str) -> tuple[str, dict[str, int]]:
    comments = _collect_mask_spans(text, r"(?m)(?<!\\)%.*$")
    commands = _collect_mask_spans(
        text,
        r"\\(?:cite[a-zA-Z*]*|ref|eqref|autoref|label|caption|section|subsection|subsubsection|paragraph|subparagraph|footnote)\s*(?:\[[^\]]*\]\s*)?\{[^{}]*\}",
    )
    inline_math = _collect_mask_spans(
        text,
        r"\$(?:\\.|[^$\n])+\$|\\\((?:\\.|[^)])+\\\)|\\\[(?:.|\n)*?\\\]",
        flags=re.S,
    )
    environments: list[tuple[int, int]] = []
    for env in (
        "table",
        "table*",
        "tabular",
        "tabular*",
        "figure",
        "figure*",
        "equation",
        "equation*",
        "align",
        "align*",
        "gather",
        "gather*",
        "multline",
        "multline*",
    ):
        environments.extend(
            _collect_mask_spans(
                text,
                rf"\\begin\{{{re.escape(env)}\}}.*?\\end\{{{re.escape(env)}\}}",
                flags=re.S,
            )
        )
    masked = _apply_mask(text, comments + commands + inline_math + environments)
    return masked, {
        "comments": len(comments),
        "latex_commands": len(commands),
        "math_regions": len(inline_math),
        "structured_environments": len(environments),
    }


def _project_texts(project: ThesisProject) -> tuple[list[ProjectText], DeepScanMeta]:
    files: list[ProjectText] = []
    masked_construct_counts = {
        "comments": 0,
        "latex_commands": 0,
        "math_regions": 0,
        "structured_environments": 0,
    }
    for tex in project.chapter_files:
        raw_text = tex.read_text(encoding="utf-8", errors="ignore")
        scan_text, counts = _latex_aware_scan_text(raw_text)
        for key, value in counts.items():
            masked_construct_counts[key] += value
        files.append(ProjectText(project.rel(tex), raw_text, scan_text))
    return files, DeepScanMeta(
        files_scanned=[item.file for item in files],
        masked_construct_counts=masked_construct_counts,
        uncovered_risks=[
            "Math regions are skipped to reduce LaTeX-side false positives.",
            "Figure/table and tabular environments are skipped, so caption-style wording is not part of deep prose screening.",
            "Citation, cross-reference, label, and section command arguments are skipped to avoid engineering-noise findings.",
            "Zero findings only means no configured deep issues were detected in checked prose after LaTeX-aware masking.",
        ],
    )


def _phrase_findings(
    files: list[ProjectText],
    node: dict[str, object],
    *,
    code: str,
    category: str,
    default_message: str,
) -> list[Finding]:
    if not _enabled(node):
        return []

    findings: list[Finding] = []
    severity = _severity(node)
    confidence = _confidence(node)
    review_required = _review_required(node)
    for pattern, detail in _patterns(node).items():
        suggestions = _string_list(detail.get("suggestions", []))
        message = str(detail.get("message", default_message.format(pattern=pattern)))
        item_confidence = _confidence(detail, confidence)
        for file in files:
            for occurrence in find_literal_occurrences(
                file.scan_text, pattern, file_name=file.file
            ):
                findings.append(
                    _build_finding(
                        severity=severity,
                        code=code,
                        message=message,
                        occurrence=occurrence,
                        evidence=occurrence.sentence,
                        suggestions=suggestions,
                        confidence=item_confidence,
                        review_required=review_required,
                        category=category,
                        rationale="Matched a configured high-confidence deep-language pattern in checked prose.",
                    )
                )
    return findings


def _terminology_findings(
    files: list[ProjectText], node: dict[str, object]
) -> list[Finding]:
    if not _enabled(node):
        return []

    findings: list[Finding] = []
    severity = _severity(node)
    confidence = _confidence(node, 0.8)
    review_required = _review_required(node)
    min_occurrences = int(node.get("min_occurrences", 2))
    for canonical, detail in _groups(node).items():
        variants = [canonical] + _string_list(detail.get("variants", []))
        occurrences_by_variant: dict[str, list[TextOccurrence]] = {
            variant: [] for variant in variants
        }
        for file in files:
            file_occurrences = find_non_overlapping_literal_occurrences(
                file.scan_text,
                variants,
                file_name=file.file,
                ignore_case=True,
            )
            for variant, occurrences in file_occurrences.items():
                occurrences_by_variant[variant].extend(occurrences)
        result = analyze_terminology_group(
            canonical,
            occurrences_by_variant,
            min_total_occurrences=min_occurrences,
        )
        if result is None:
            continue
        noncanonical_occurrences = [
            occurrence
            for variant, occurrences in occurrences_by_variant.items()
            if variant != canonical
            for occurrence in occurrences
        ]
        if noncanonical_occurrences and all(
            _contains_variant(occurrence.sentence, canonical)
            for occurrence in noncanonical_occurrences
        ):
            continue
        findings.append(
            _build_finding(
                severity=severity,
                code="LANG_DEEP_TERM_INCONSISTENT",
                message=f"Terminology variants should be unified to '{canonical}'",
                occurrence=result.anchor_occurrence,
                evidence=result.evidence,
                suggestions=[canonical],
                confidence=confidence,
                review_required=review_required,
                category="terminology_consistency",
                rationale="Detected competing terminology variants in checked prose without a stable canonical form nearby.",
            )
        )
    return findings


def _acronym_has_prior_expansion(
    files: list[ProjectText], occurrence: TextOccurrence, expansions: list[str]
) -> bool:
    for file in files:
        if file.file == occurrence.file:
            lines = file.scan_text.splitlines()
            prefix = "\n".join(lines[: occurrence.line - 1])
            line_prefix = lines[occurrence.line - 1][: occurrence.span["start"] - 1]
            prior_text = prefix + ("\n" if prefix and line_prefix else "") + line_prefix
            return any(_contains_variant(prior_text, expansion) for expansion in expansions)
        if any(_contains_variant(file.scan_text, expansion) for expansion in expansions):
            return True
    return False


def _acronym_findings(files: list[ProjectText], node: dict[str, object]) -> list[Finding]:
    if not _enabled(node):
        return []

    findings: list[Finding] = []
    severity = _severity(node)
    confidence = _confidence(node, 0.85)
    review_required = _review_required(node)
    require_expansion_first = bool(
        node.get("require_expansion_before_short_form", True)
    )
    if not require_expansion_first:
        return findings

    for acronym, detail in _acronyms(node).items():
        expansions = _string_list(detail.get("expansions", []))
        item_confidence = _confidence(detail, confidence)
        first_occurrence: TextOccurrence | None = None
        for file in files:
            occurrences = find_token_occurrences(
                file.scan_text, acronym, file_name=file.file
            )
            if occurrences:
                first_occurrence = occurrences[0]
                break
        if first_occurrence is None:
            continue
        if any(
            _contains_variant(first_occurrence.sentence, expansion)
            for expansion in expansions
        ):
            continue
        if _acronym_has_prior_expansion(files, first_occurrence, expansions):
            continue
        findings.append(
            _build_finding(
                severity=severity,
                code="LANG_DEEP_ACRONYM_FIRST_USE",
                message=f"Acronym '{acronym}' appears before a full-form introduction",
                occurrence=first_occurrence,
                evidence=first_occurrence.sentence,
                suggestions=expansions,
                confidence=item_confidence,
                review_required=review_required,
                category="acronym_first_use",
                rationale="Detected the short form before any supported full-form introduction in checked prose.",
            )
        )
    return findings


def collect_language_deep_report_data(
    project: ThesisProject, pack: RulePack
) -> tuple[list[Finding], dict[str, object], dict[str, object]]:
    files, scan_meta = _project_texts(project)
    deep = pack.rules.get("language_deep", {})
    consistency = pack.rules.get("consistency", {})
    if not isinstance(deep, dict):
        deep = {}
    if not isinstance(consistency, dict):
        consistency = {}

    findings: list[Finding] = []
    findings.extend(
        _phrase_findings(
            files,
            _rule_node(deep, "connector_misuse"),
            code="LANG_DEEP_CONNECTOR_MISUSE",
            category="connector_misuse",
            default_message="Potential connector misuse detected: {pattern}",
        )
    )
    findings.extend(
        _phrase_findings(
            files,
            _rule_node(deep, "collocation_misuse"),
            code="LANG_DEEP_COLLOCATION_MISUSE",
            category="collocation_misuse",
            default_message="Potential collocation misuse detected: {pattern}",
        )
    )
    findings.extend(
        _terminology_findings(files, _rule_node(consistency, "terminology_consistency"))
    )
    findings.extend(_acronym_findings(files, _rule_node(deep, "acronym_first_use")))
    findings.sort(key=lambda item: (item.file, item.line, item.code))
    category_counts: dict[str, int] = {}
    for finding in findings:
        category_counts[finding.category] = category_counts.get(finding.category, 0) + 1
    deep_language_count = sum(
        1
        for finding in findings
        if finding.category in {"connector_misuse", "collocation_misuse"}
    )
    consistency_count = sum(
        1
        for finding in findings
        if finding.category in {"terminology_consistency", "acronym_first_use"}
    )
    review_required_count = sum(1 for finding in findings if finding.review_required)
    high_confidence_count = sum(
        1 for finding in findings if (finding.confidence or 0.0) >= 0.8
    )
    summary = {
        "files_scanned": len(files),
        "coverage_mode": "partial_latex_aware_screening",
        "review_mode": "manual_first",
        "review_required": review_required_count,
        "stratified_counts": {
            "deep_language": deep_language_count,
            "consistency": consistency_count,
            "high_confidence": high_confidence_count,
            "conservative_suggestions": len(findings),
        },
        "category_counts": category_counts,
    }
    payload = {
        "coverage": {
            "mode": "partial_latex_aware_screening",
            "checked_files": scan_meta.files_scanned,
            "masked_construct_counts": scan_meta.masked_construct_counts,
        },
        "uncovered_risks": scan_meta.uncovered_risks,
        "review_guidance": {
            "positioning": "Deep language review is a screening assistant plus human-review aid, not final thesis sign-off.",
            "default_edit_policy": "Treat all suggestions as conservative review prompts before applying edits.",
        },
    }
    return findings, summary, payload
