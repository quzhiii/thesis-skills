from __future__ import annotations

import re
from pathlib import Path

from core.common import Finding


_LINE_RE = re.compile(r"l\.(\d+)")
_INPUT_LINE_WARNING_RE = re.compile(r"input line (\d+)")
_OVERFULL_RE = re.compile(r"Overfull \\hbox .*? at lines? (\d+)(?:--(\d+))?")
_UNDEFINED_CONTROL_RE = re.compile(r"Undefined control sequence")
_MISSING_FILE_RE = re.compile(r"File `([^`]+)' not found")
_MISSING_CITATION_RE = re.compile(r"Citation `([^`]+)' .* undefined")
_MISSING_REFERENCE_RE = re.compile(r"Reference `([^`]+)' .* undefined")
_BIB_BACKEND_RE = re.compile(
    r"(?:Please \(re\)run (?:Biber|BibTeX)|I couldn't open auxiliary file|No file .*?\.bbl)",
    re.IGNORECASE,
)
_FONT_RE = re.compile(r"font .* not loadable|fontspec error", re.IGNORECASE)
_ENCODING_RE = re.compile(r"inputenc error|unicode character .* not set up", re.IGNORECASE)
_RERUN_RE = re.compile(r"Label\(s\) may have changed|Rerun to get cross-references right")


def _line_from_text(text: str) -> int:
    match = _LINE_RE.search(text)
    if match:
        return int(match.group(1))
    match = _INPUT_LINE_WARNING_RE.search(text)
    if match:
        return int(match.group(1))
    match = _OVERFULL_RE.search(text)
    if match:
        return int(match.group(1))
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("l."):
            tail = stripped[2:].lstrip()
            digits = []
            seen_digit = False
            for ch in tail:
                if ch.isdigit():
                    digits.append(ch)
                    seen_digit = True
                    continue
                if not seen_digit and ch in {" ", "\t"}:
                    continue
                break
            if digits:
                return int("".join(digits))
    return 0


def _evidence(lines: list[str], start: int, width: int = 2) -> str:
    chunk = lines[start : start + width]
    return "\n".join(line.rstrip() for line in chunk if line.strip())


def _make_finding(
    severity: str,
    code: str,
    message: str,
    file: str,
    line: int,
    suggestion: str,
    *,
    category: str,
    evidence: str,
    rationale: str = "",
) -> Finding:
    return Finding(
        severity=severity,
        code=code,
        message=message,
        file=file,
        line=line,
        suggestion=suggestion,
        evidence=evidence,
        category=category,
        rationale=rationale,
    )


def parse_compile_log(
    text: str,
    *,
    default_file: str = "",
    severity_map: dict[str, str] | None = None,
) -> list[Finding]:
    severity_map = severity_map or {}
    findings: list[Finding] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip("\n")
        stripped = line.strip()
        evidence = _evidence(lines, i, 6)
        line_no = _line_from_text(evidence or stripped)

        if stripped.startswith("! "):
            detail = stripped[2:].strip()
            if _UNDEFINED_CONTROL_RE.search(detail):
                findings.append(
                    _make_finding(
                        severity_map.get("undefined_control_sequence", "error"),
                        "COMPILE_UNDEFINED_CONTROL_SEQUENCE",
                        "Undefined control sequence during LaTeX compilation",
                        default_file,
                        line_no,
                        "Check the command spelling or load the package that defines it",
                        category="undefined_control_sequence",
                        evidence=evidence,
                        rationale="Build-blocking TeX command resolution error",
                    )
                )
                i += 1
                continue
            missing = _MISSING_FILE_RE.search(detail)
            if missing:
                findings.append(
                    _make_finding(
                        severity_map.get("missing_file_or_package", "error"),
                        "COMPILE_MISSING_FILE_OR_PACKAGE",
                        f"Missing file or package: {missing.group(1)}",
                        default_file,
                        line_no,
                        "Install the missing package or fix the referenced file path",
                        category="missing_file_or_package",
                        evidence=evidence,
                        rationale="Build-blocking dependency resolution error",
                    )
                )
                i += 1
                continue
            findings.append(
                _make_finding(
                    severity_map.get("compile_error_unknown", "error"),
                    "COMPILE_ERROR_UNKNOWN",
                    detail,
                    default_file,
                    line_no,
                    "Inspect the raw compile log snippet for the exact TeX engine failure",
                    category="compile_error_unknown",
                    evidence=evidence,
                    rationale="Unclassified build-blocking compile error preserved conservatively",
                )
            )
            i += 1
            continue

        missing_citation = _MISSING_CITATION_RE.search(stripped)
        if missing_citation:
            findings.append(
                _make_finding(
                    severity_map.get("missing_citation", "warning"),
                    "COMPILE_MISSING_CITATION",
                    f"Citation undefined during compilation: {missing_citation.group(1)}",
                    default_file,
                    line_no,
                    "Check the bibliography entry, cite key spelling, and rerun bibliography tools",
                    category="missing_citation",
                    evidence=evidence,
                )
            )
            i += 1
            continue

        missing_reference = _MISSING_REFERENCE_RE.search(stripped)
        if missing_reference:
            findings.append(
                _make_finding(
                    severity_map.get("missing_reference", "warning"),
                    "COMPILE_MISSING_REFERENCE",
                    f"Reference undefined during compilation: {missing_reference.group(1)}",
                    default_file,
                    line_no,
                    "Check the label name and rerun compilation until cross-references stabilize",
                    category="missing_reference",
                    evidence=evidence,
                )
            )
            i += 1
            continue

        if _BIB_BACKEND_RE.search(stripped):
            findings.append(
                _make_finding(
                    severity_map.get("bibliography_backend_issue", "warning"),
                    "COMPILE_BIBLIOGRAPHY_BACKEND_ISSUE",
                    stripped,
                    default_file,
                    line_no,
                    "Run the required bibliography backend and rebuild the document",
                    category="bibliography_backend_issue",
                    evidence=evidence,
                )
            )
            i += 1
            continue

        if _OVERFULL_RE.search(stripped):
            findings.append(
                _make_finding(
                    severity_map.get("overfull_box", "info"),
                    "COMPILE_OVERFULL_BOX",
                    stripped,
                    default_file,
                    line_no,
                    "Review the affected paragraph for line breaking, spacing, or oversized inline content",
                    category="overfull_box",
                    evidence=evidence,
                )
            )
            i += 1
            continue

        if _FONT_RE.search(stripped):
            findings.append(
                _make_finding(
                    severity_map.get("missing_file_or_package", "error"),
                    "COMPILE_FONT_OR_ENGINE_ISSUE",
                    stripped,
                    default_file,
                    line_no,
                    "Check engine selection and whether the required system font is installed",
                    category="missing_file_or_package",
                    evidence=evidence,
                )
            )
            i += 1
            continue

        if _ENCODING_RE.search(stripped):
            findings.append(
                _make_finding(
                    severity_map.get("compile_error_unknown", "error"),
                    "COMPILE_ENCODING_ISSUE",
                    stripped,
                    default_file,
                    line_no,
                    "Check file encoding and engine compatibility for the affected characters",
                    category="compile_error_unknown",
                    evidence=evidence,
                )
            )
            i += 1
            continue

        if _RERUN_RE.search(stripped):
            findings.append(
                _make_finding(
                    severity_map.get("compile_warning_unknown", "warning"),
                    "COMPILE_RERUN_REQUIRED",
                    stripped,
                    default_file,
                    line_no,
                    "Rerun compilation to stabilize labels, references, or table of contents entries",
                    category="compile_warning_unknown",
                    evidence=evidence,
                )
            )
            i += 1
            continue

        if stripped.startswith("LaTeX Warning:") or stripped.startswith("Package "):
            findings.append(
                _make_finding(
                    severity_map.get("compile_warning_unknown", "warning"),
                    "COMPILE_WARNING_UNKNOWN",
                    stripped,
                    default_file,
                    line_no,
                    "Inspect the raw warning and decide whether it needs a source or package change",
                    category="compile_warning_unknown",
                    evidence=evidence,
                )
            )
            i += 1
            continue

        i += 1

    return findings


def parse_compile_log_file(
    log_path: str | Path,
    *,
    default_file: str = "",
    severity_map: dict[str, str] | None = None,
) -> list[Finding]:
    path = Path(log_path)
    return parse_compile_log(
        path.read_text(encoding="utf-8", errors="ignore"),
        default_file=default_file,
        severity_map=severity_map,
    )
