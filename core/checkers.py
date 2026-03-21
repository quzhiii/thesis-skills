from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

from core.common import Finding
from core.project import ThesisProject
from core.reports import write_report
from core.rules import RulePack


def _level(config: dict[str, object], key: str, default: str) -> str:
    node = config.get(key, {})
    if isinstance(node, dict):
        return str(node.get("severity", default))
    return default


def _enabled(config: dict[str, object], key: str) -> bool:
    node = config.get(key, {})
    if isinstance(node, dict):
        return bool(node.get("enabled", False))
    return False


def _line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def _parse_bib_entries(path: Path) -> list[tuple[str, str, str]]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    entries: list[tuple[str, str, str]] = []
    for match in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,(.*?)\n\}\s*", text, re.S):
        entries.append((match.group(1).lower(), match.group(2), match.group(3)))
    return entries


def run_bib_quality_check(
    project: ThesisProject, pack: RulePack, report_path: Path
) -> int:
    rules = pack.rules["reference"]["bib_quality"]
    allowed_types = set(rules.get("allowed_entry_types", []))
    findings: list[Finding] = []
    scanned = 0
    for bib in project.bibliography_files:
        for entry_type, key, body in _parse_bib_entries(bib):
            scanned += 1
            if allowed_types and entry_type not in allowed_types:
                findings.append(
                    Finding(
                        _level(rules, "unsupported_entry_type", "warning"),
                        "BIB_UNSUPPORTED_TYPE",
                        f"Unsupported entry type for {key}: {entry_type}",
                        project.rel(bib),
                        0,
                        "Normalize the entry type or update the pack rules",
                    )
                )
            if rules.get("require_langid", False) and "langid" not in body:
                findings.append(
                    Finding(
                        _level(rules, "missing_langid", "warning"),
                        "BIB_MISSING_LANGID",
                        f"Bibliography entry missing langid: {key}",
                        project.rel(bib),
                        0,
                        "Add a langid field such as english or chinese",
                    )
                )
            doi = re.search(r"doi\s*=\s*\{([^}]*)\}", body, re.I)
            if doi and " " in doi.group(1).strip():
                findings.append(
                    Finding(
                        _level(rules, "malformed_doi", "warning"),
                        "BIB_MALFORMED_DOI",
                        f"DOI contains spaces: {key}",
                        project.rel(bib),
                        0,
                        "Normalize the DOI value",
                    )
                )
    return write_report(
        report_path,
        "check_bib_quality",
        pack.ruleset,
        findings,
        {"files_scanned": len(project.bibliography_files), "entries_scanned": scanned},
    )


def run_reference_check(
    project: ThesisProject, pack: RulePack, report_path: Path
) -> int:
    ref_rules = pack.rules["reference"]
    findings: list[Finding] = []
    bib_keys: set[str] = set()
    title_to_keys: defaultdict[str, list[str]] = defaultdict(list)
    for bib in project.bibliography_files:
        text = bib.read_text(encoding="utf-8", errors="ignore")
        bib_keys |= set(re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,", text))
        for match in re.finditer(r"@\w+\s*\{\s*([^,\s]+)\s*,(.*?)\n\}\s*", text, re.S):
            title = re.search(r"title\s*=\s*\{(.*?)\}", match.group(2), re.S)
            if title:
                title_to_keys[title.group(1).strip().lower()].append(match.group(1))

    cited: list[tuple[str, str, int]] = []
    pattern = re.compile(r"\\cite[a-zA-Z*]*\s*(?:\[[^\]]*\]\s*)?\{([^}]+)\}")
    for tex in [project.main_tex] + project.chapter_files:
        text = tex.read_text(encoding="utf-8", errors="ignore")
        for match in pattern.finditer(text):
            for key in [
                item.strip() for item in match.group(1).split(",") if item.strip()
            ]:
                cited.append((key, project.rel(tex), _line_of(text, match.start())))
                if key not in bib_keys:
                    findings.append(
                        Finding(
                            _level(ref_rules, "missing_key", "error"),
                            "REF_MISSING_KEY",
                            f"Citation key not found in bibliography: {key}",
                            project.rel(tex),
                            _line_of(text, match.start()),
                            "Add the missing key or fix the cite command",
                        )
                    )

    cited_keys = {key for key, _, _ in cited}
    for key in sorted(bib_keys - cited_keys):
        findings.append(
            Finding(
                _level(ref_rules, "orphan_entry", "warning"),
                "REF_ORPHAN_BIB",
                f"Bibliography key not cited: {key}",
                "|".join(project.rel(path) for path in project.bibliography_files),
                0,
                "Remove unused entry or cite it",
            )
        )

    for title, keys in title_to_keys.items():
        if len(keys) > 1:
            findings.append(
                Finding(
                    _level(ref_rules, "duplicate_title", "warning"),
                    "REF_DUPLICATE_TITLE",
                    f"Possible duplicate title group: {', '.join(sorted(keys))}",
                    "|".join(project.rel(path) for path in project.bibliography_files),
                    0,
                    "Merge duplicate bibliography entries if appropriate",
                )
            )

    return write_report(
        report_path,
        "check_references",
        pack.ruleset,
        findings,
        {"files_scanned": len(project.chapter_files) + 1},
    )


def run_language_check(
    project: ThesisProject, pack: RulePack, report_path: Path
) -> int:
    lang = pack.rules["language"]
    findings: list[Finding] = []
    weak_patterns = []
    weak = lang.get("weak_phrases", {})
    if isinstance(weak, dict):
        weak_patterns = [str(item) for item in weak.get("patterns", [])]

    for tex in project.chapter_files:
        lines = tex.read_text(encoding="utf-8", errors="ignore").splitlines()
        rel = project.rel(tex)
        for line_no, line in enumerate(lines, start=1):
            if _enabled(lang, "repeated_punctuation") and re.search(
                r"[。]{2,}|[，,]{2,}|[；;]{2,}|[：:]{2,}", line
            ):
                findings.append(
                    Finding(
                        _level(lang, "repeated_punctuation", "error"),
                        "LANG_REPEAT_PUNC",
                        "Repeated punctuation detected",
                        rel,
                        line_no,
                        "Replace repeated punctuation with a single mark",
                    )
                )
            if _enabled(lang, "mixed_quote_style") and (
                ('"' in line or "'" in line)
                and any(mark in line for mark in ["“", "”", "‘", "’"])
            ):
                findings.append(
                    Finding(
                        _level(lang, "mixed_quote_style", "warning"),
                        "LANG_MIXED_QUOTES",
                        "Mixed quote styles detected",
                        rel,
                        line_no,
                        "Use one quote style consistently",
                    )
                )
            if _enabled(lang, "cjk_latin_spacing"):
                text = re.sub(r"\\[A-Za-z@]+\*?(\[[^\]]*\])?(\{[^{}]*\})?", " ", line)
                if re.search(
                    r"[\u4e00-\u9fff](?=[A-Za-z]*[a-z])[A-Za-z]{2,}", text
                ) or re.search(r"(?=[A-Za-z]*[a-z])[A-Za-z]{2,}[\u4e00-\u9fff]", text):
                    findings.append(
                        Finding(
                            _level(lang, "cjk_latin_spacing", "warning"),
                            "LANG_CJK_LATIN_SPACING",
                            "Possible missing spacing between CJK and Latin tokens",
                            rel,
                            line_no,
                            "Add a space between Chinese and English tokens where appropriate",
                        )
                    )
            if isinstance(weak, dict) and weak.get("enabled", False):
                for pattern in weak_patterns:
                    if pattern in line:
                        findings.append(
                            Finding(
                                _level(lang, "weak_phrases", "info"),
                                "LANG_WEAK_PHRASE",
                                f"Weak academic phrase detected: {pattern}",
                                rel,
                                line_no,
                                "Consider replacing with more precise wording",
                            )
                        )
    return write_report(
        report_path,
        "check_language",
        pack.ruleset,
        findings,
        {"files_scanned": len(project.chapter_files)},
    )


def run_format_check(project: ThesisProject, pack: RulePack, report_path: Path) -> int:
    fmt = pack.rules["format"]
    findings: list[Finding] = []
    main_text = project.main_tex.read_text(encoding="utf-8", errors="ignore")
    if fmt.get("require_list_of_figures", False) and "\\listoffigures" not in main_text:
        findings.append(
            Finding(
                "warning",
                "FMT_NO_LISTOFFIGURES",
                "Main file missing \\listoffigures",
                project.rel(project.main_tex),
                1,
                "Add \\listoffigures",
            )
        )
    if fmt.get("require_list_of_tables", False) and "\\listoftables" not in main_text:
        findings.append(
            Finding(
                "warning",
                "FMT_NO_LISTOFTABLES",
                "Main file missing \\listoftables",
                project.rel(project.main_tex),
                1,
                "Add \\listoftables",
            )
        )

    labels: dict[str, tuple[str, int]] = {}
    refs: list[tuple[str, str, int]] = []
    for tex in [project.main_tex] + project.chapter_files:
        text = tex.read_text(encoding="utf-8", errors="ignore")
        rel = project.rel(tex)
        for env in ("figure", "table"):
            for match in re.finditer(
                r"\\begin\{" + env + r"\}(.*?)\\end\{" + env + r"\}", text, re.S
            ):
                block = match.group(1)
                line_no = _line_of(text, match.start())
                if "\\caption" not in block:
                    findings.append(
                        Finding(
                            "error",
                            "FMT_MISSING_CAPTION",
                            f"{env} missing \\caption",
                            rel,
                            line_no,
                            "Add a caption",
                        )
                    )
                if "\\label" not in block:
                    findings.append(
                        Finding(
                            "error",
                            "FMT_MISSING_LABEL",
                            f"{env} missing \\label",
                            rel,
                            line_no,
                            "Add a label",
                        )
                    )
                if (
                    env == "figure"
                    and fmt.get("figure_requires_centering", False)
                    and "\\centering" not in block
                ):
                    findings.append(
                        Finding(
                            "warning",
                            "FMT_MISSING_CENTERING",
                            "figure missing \\centering",
                            rel,
                            line_no,
                            "Add \\centering",
                        )
                    )
            for match in re.finditer(r"\\label\{([^}]+)\}", text):
                labels[match.group(1)] = (rel, _line_of(text, match.start()))
            for match in re.finditer(r"\\(?:ref|eqref|autoref)\{([^}]+)\}", text):
                refs.append((match.group(1), rel, _line_of(text, match.start())))
    used = {name for name, _, _ in refs}
    for ref, rel, line_no in refs:
        if ref not in labels:
            findings.append(
                Finding(
                    "error",
                    "FMT_BROKEN_REF",
                    f"reference target not found: {ref}",
                    rel,
                    line_no,
                    "Define matching \\label or fix ref key",
                )
            )
    for label, (rel, line_no) in labels.items():
        if label not in used:
            findings.append(
                Finding(
                    "warning",
                    "FMT_ORPHAN_LABEL",
                    f"label not referenced: {label}",
                    rel,
                    line_no,
                    "Remove the unused label or add a ref",
                )
            )
    return write_report(
        report_path,
        "check_format",
        pack.ruleset,
        findings,
        {"files_scanned": len(project.chapter_files) + 1},
    )


def run_content_check(project: ThesisProject, pack: RulePack, report_path: Path) -> int:
    content = pack.rules["content"]
    findings: list[Finding] = []
    titles: list[str] = []
    acronym_candidates: set[str] = set()
    for tex in project.chapter_files:
        text = tex.read_text(encoding="utf-8", errors="ignore")
        titles.extend(re.findall(r"\\section\{([^}]+)\}", text))
        acronym_candidates |= set(re.findall(r"(?<!\\)\b[A-Z][A-Z0-9-]{1,}\b", text))
    for required in content.get("required_sections", []):
        if required not in titles:
            findings.append(
                Finding(
                    "error",
                    "CONTENT_MISSING_SECTION",
                    f"Required section not found: {required}",
                    project.rel(project.main_tex),
                    1,
                    "Add the missing section or update the rule pack",
                )
            )

    if project.abstract_file and project.abstract_file.exists():
        abstract_text = project.abstract_file.read_text(
            encoding="utf-8", errors="ignore"
        )
        keyword_line = re.search(r"Keywords:\s*(.*)", abstract_text)
        if keyword_line:
            keywords = [
                item.strip()
                for item in keyword_line.group(1).split(",")
                if item.strip()
            ]
            limits = content.get("abstract_keywords", {})
            if len(keywords) < int(limits.get("min", 0)) or len(keywords) > int(
                limits.get("max", 99)
            ):
                findings.append(
                    Finding(
                        "error",
                        "CONTENT_KEYWORD_COUNT",
                        f"Keyword count out of range: {len(keywords)}",
                        project.rel(project.abstract_file),
                        1,
                        "Adjust abstract keywords to meet the rule pack",
                    )
                )

    extra = {
        "files_scanned": len(project.chapter_files)
        + (1 if project.abstract_file else 0),
        "acronym_candidates": sorted(acronym_candidates),
    }
    return write_report(report_path, "check_content", pack.ruleset, findings, extra)
