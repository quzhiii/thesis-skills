from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

from core.common import Finding
from core.compile_parser import parse_compile_log_file
from core.language_rules import get_language_rule
from core.project import ThesisProject
from core.reports import write_report
from core.rules import RulePack


def _level(config: dict[str, object], key: str, default: str) -> str:
    node = config.get(key, {})
    if isinstance(node, dict):
        return str(node.get("severity", default))
    return default


def _line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def _parse_bib_entries(path: Path) -> list[tuple[str, str, str]]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    entries: list[tuple[str, str, str]] = []
    for match in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,(.*?)\n\}\s*", text, re.S):
        entries.append((match.group(1).lower(), match.group(2), match.group(3)))
    return entries


_LATEX_COMMAND_RE = re.compile(r"\\[A-Za-z@]+\*?(?:\[[^\]]*\])?")
_REPEATED_PUNCTUATION_RE = re.compile(r"[。]{2,}|[，,]{2,}|[；;]{2,}|[：:]{2,}")
_CJK_LATIN_GLUE_RE = re.compile(
    r"[\u4e00-\u9fff][A-Za-z][A-Za-z0-9-]{1,}|[A-Za-z][A-Za-z0-9-]{1,}[\u4e00-\u9fff]"
)
_UNIT_RE = re.compile(
    r"(?<![A-Za-z])\d+(?:\.\d+)?"
    r"(?:mg|kg|g|km|cm|mm|m|μm|nm|mL|uL|L|ms|min|h|s|kHz|MHz|GHz|Hz|mV|kV|V|mA|A|kW|W|kPa|MPa|Pa|GB|MB|TB|°C)\b"
)
_NUMBER_RANGE_RE = re.compile(r"(?<!\d)\d+(?:\.\d+)?\s*-\s*\d+(?:\.\d+)?(?!\d)")
_ENUM_STYLE_RE = re.compile(r"^\s*\d+\)")
_DASH_STYLE_RE = re.compile(r"---|--")
_ELLIPSIS_STYLE_RE = re.compile(r"(?:\.{3,6}|。{6})")
_ZH_EN_SYMBOL_SPACING_RE = re.compile(
    r"[\u4e00-\u9fff][,，;；:：]\s*[A-Za-z]|[A-Za-z][,，;；:：]\s*[\u4e00-\u9fff]"
)
_FULLWIDTH_HALFWIDTH_MIX_RE = re.compile(
    r"[\u4e00-\u9fff][,;:!?][\u4e00-\u9fff]|[A-Za-z0-9][，；：！？][A-Za-z0-9]"
)


def _language_view(line: str) -> str:
    text = _LATEX_COMMAND_RE.sub(" ", line)
    return text.replace("{", "").replace("}", "")


def _append_language_finding(
    findings: list[Finding],
    lang: dict[str, object],
    key: str,
    code: str,
    message: str,
    rel: str,
    line_no: int,
    suggestion: str,
    *,
    default_severity: str = "warning",
) -> None:
    rule = get_language_rule(lang, key, default_severity=default_severity)
    findings.append(
        Finding(
            rule.severity,
            code,
            message,
            rel,
            line_no,
            suggestion,
        )
    )


def _has_bracket_mismatch(text: str) -> bool:
    stack: list[str] = []
    pairs = {"(": ")", "（": "）", "[": "]", "【": "】"}
    closers = {value: key for key, value in pairs.items()}
    for ch in text:
        if ch in pairs:
            stack.append(ch)
        elif ch in closers:
            if not stack or stack[-1] != closers[ch]:
                return True
            stack.pop()
    return bool(stack)


def _has_quote_mismatch(text: str) -> bool:
    if text.count("“") != text.count("”"):
        return True
    if text.count("‘") != text.count("’"):
        return True
    if text.count('"') % 2 != 0:
        return True
    return False


def _has_booktitle_mixed_style(text: str) -> bool:
    if "《" not in text and "》" not in text:
        return False
    return any(mark in text for mark in ["〈", "〉", '"', "“", "”"])


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
    repeated_punctuation = get_language_rule(
        lang, "repeated_punctuation", default_severity="error"
    )
    mixed_quote_style = get_language_rule(lang, "mixed_quote_style")
    cjk_latin_spacing = get_language_rule(lang, "cjk_latin_spacing")
    weak_phrases = get_language_rule(lang, "weak_phrases", default_severity="info")
    bracket_mismatch = get_language_rule(lang, "bracket_mismatch")
    quote_mismatch = get_language_rule(lang, "quote_mismatch")
    booktitle_mixed_style = get_language_rule(lang, "booktitle_mixed_style")
    unit_spacing = get_language_rule(lang, "unit_spacing", default_autofix_safe=True)
    ellipsis_style = get_language_rule(
        lang, "ellipsis_style", default_autofix_safe=True
    )
    dash_style = get_language_rule(lang, "dash_style")
    zh_en_symbol_spacing = get_language_rule(lang, "zh_en_symbol_spacing")
    number_range_style = get_language_rule(lang, "number_range_style")
    enum_punctuation_style = get_language_rule(lang, "enum_punctuation_style")
    connector_blacklist = get_language_rule(lang, "connector_blacklist_simple")
    fullwidth_halfwidth_mix = get_language_rule(
        lang, "fullwidth_halfwidth_mix", default_autofix_safe=True
    )

    for tex in project.chapter_files:
        lines = tex.read_text(encoding="utf-8", errors="ignore").splitlines()
        rel = project.rel(tex)
        for line_no, line in enumerate(lines, start=1):
            text = _language_view(line)
            if repeated_punctuation.enabled and _REPEATED_PUNCTUATION_RE.search(text):
                _append_language_finding(
                    findings,
                    lang,
                    "repeated_punctuation",
                    "LANG_REPEAT_PUNC",
                    "Repeated punctuation detected",
                    rel,
                    line_no,
                    "Replace repeated punctuation with a single mark",
                    default_severity="error",
                )

            if mixed_quote_style.enabled and (
                ('"' in text or "'" in text)
                and any(mark in text for mark in ["“", "”", "‘", "’"])
            ):
                _append_language_finding(
                    findings,
                    lang,
                    "mixed_quote_style",
                    "LANG_MIXED_QUOTES",
                    "Mixed quote styles detected",
                    rel,
                    line_no,
                    "Use one quote style consistently",
                )

            if cjk_latin_spacing.enabled and _CJK_LATIN_GLUE_RE.search(text):
                _append_language_finding(
                    findings,
                    lang,
                    "cjk_latin_spacing",
                    "LANG_CJK_LATIN_SPACING",
                    "Possible missing spacing between CJK and Latin tokens",
                    rel,
                    line_no,
                    "Add a space between Chinese and English tokens where appropriate",
                )

            if weak_phrases.enabled:
                for pattern in weak_phrases.patterns:
                    if pattern in text:
                        _append_language_finding(
                            findings,
                            lang,
                            "weak_phrases",
                            "LANG_WEAK_PHRASE",
                            f"Weak academic phrase detected: {pattern}",
                            rel,
                            line_no,
                            "Consider replacing with more precise wording",
                            default_severity="info",
                        )

            if bracket_mismatch.enabled and _has_bracket_mismatch(text):
                _append_language_finding(
                    findings,
                    lang,
                    "bracket_mismatch",
                    "LANG_BRACKET_MISMATCH",
                    "Bracket pairing looks inconsistent",
                    rel,
                    line_no,
                    "Check whether opening and closing brackets are balanced",
                )

            if quote_mismatch.enabled and _has_quote_mismatch(text):
                _append_language_finding(
                    findings,
                    lang,
                    "quote_mismatch",
                    "LANG_QUOTE_MISMATCH",
                    "Quote pairing looks inconsistent",
                    rel,
                    line_no,
                    "Check whether opening and closing quotation marks are balanced",
                )

            if booktitle_mixed_style.enabled and _has_booktitle_mixed_style(text):
                _append_language_finding(
                    findings,
                    lang,
                    "booktitle_mixed_style",
                    "LANG_BOOKTITLE_MIXED_STYLE",
                    "Possible mixed book-title mark styles detected",
                    rel,
                    line_no,
                    "Use one title-mark style consistently in the same sentence",
                )

            if unit_spacing.enabled and _UNIT_RE.search(text):
                _append_language_finding(
                    findings,
                    lang,
                    "unit_spacing",
                    "LANG_UNIT_SPACING",
                    "Number and unit should be separated consistently",
                    rel,
                    line_no,
                    "Insert a space between the numeric value and the unit",
                )

            if ellipsis_style.enabled and _ELLIPSIS_STYLE_RE.search(text):
                _append_language_finding(
                    findings,
                    lang,
                    "ellipsis_style",
                    "LANG_ELLIPSIS_STYLE",
                    "Ellipsis style is not normalized",
                    rel,
                    line_no,
                    "Prefer the normalized ellipsis form",
                )

            if dash_style.enabled and _DASH_STYLE_RE.search(text):
                _append_language_finding(
                    findings,
                    lang,
                    "dash_style",
                    "LANG_DASH_STYLE",
                    "Dash style may be inconsistent",
                    rel,
                    line_no,
                    "Use one dash style consistently",
                )

            if zh_en_symbol_spacing.enabled and _ZH_EN_SYMBOL_SPACING_RE.search(text):
                _append_language_finding(
                    findings,
                    lang,
                    "zh_en_symbol_spacing",
                    "LANG_ZH_EN_SYMBOL_SPACING",
                    "Punctuation around Chinese and English text may need normalization",
                    rel,
                    line_no,
                    "Check punctuation style and spacing across Chinese/English boundaries",
                )

            if number_range_style.enabled and _NUMBER_RANGE_RE.search(text):
                _append_language_finding(
                    findings,
                    lang,
                    "number_range_style",
                    "LANG_NUMBER_RANGE_STYLE",
                    "Numeric range style may be inconsistent",
                    rel,
                    line_no,
                    "Use the preferred range style for the active ruleset",
                )

            if enum_punctuation_style.enabled and _ENUM_STYLE_RE.search(text):
                _append_language_finding(
                    findings,
                    lang,
                    "enum_punctuation_style",
                    "LANG_ENUM_STYLE",
                    "Enumeration punctuation style may be inconsistent",
                    rel,
                    line_no,
                    "Use the preferred enumeration punctuation style for the active ruleset",
                )

            if connector_blacklist.enabled:
                for pattern in connector_blacklist.patterns:
                    if pattern in text:
                        _append_language_finding(
                            findings,
                            lang,
                            "connector_blacklist_simple",
                            "LANG_CONNECTOR_BLACKLIST",
                            f"Connector combination is on the conservative blacklist: {pattern}",
                            rel,
                            line_no,
                            "Rewrite the connector combination with a more natural structure",
                        )

            if fullwidth_halfwidth_mix.enabled and _FULLWIDTH_HALFWIDTH_MIX_RE.search(
                text
            ):
                _append_language_finding(
                    findings,
                    lang,
                    "fullwidth_halfwidth_mix",
                    "LANG_FULLWIDTH_HALFWIDTH_MIX",
                    "Fullwidth and halfwidth punctuation styles are mixed",
                    rel,
                    line_no,
                    "Normalize punctuation width in contexts where the style is obvious",
                )
    return write_report(
        report_path,
        "check_language",
        pack.ruleset,
        findings,
        {"files_scanned": len(project.chapter_files)},
    )


def run_language_deep_check(
    project: ThesisProject, pack: RulePack, report_path: Path
) -> int:
    from core.language_deep import collect_language_deep_report_data

    findings, extra_summary, extra_payload = collect_language_deep_report_data(
        project, pack
    )
    return write_report(
        report_path,
        "check_language_deep",
        pack.ruleset,
        findings,
        extra_summary,
        extra_payload,
        fail_on_warnings=True,
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


def run_compile_check(
    project: ThesisProject,
    pack: RulePack,
    report_path: Path,
    *,
    log_path: Path | None = None,
) -> int:
    compile_rules = pack.rules.get("compile", {})
    if not isinstance(compile_rules, dict):
        compile_rules = {}
    categories = compile_rules.get("categories", {})
    if not isinstance(categories, dict):
        categories = {}
    severity_map: dict[str, str] = {}
    for key, value in categories.items():
        if isinstance(value, dict):
            severity_map[str(key)] = str(value.get("severity", "warning"))
    if log_path is None:
        log_path = project.main_tex.with_suffix(".log")
    findings = parse_compile_log_file(
        log_path,
        default_file=project.rel(project.main_tex),
        severity_map=severity_map,
    )
    extra_summary = {
        "log_file": project.rel(log_path)
        if log_path.is_relative_to(project.root)
        else str(log_path),
        "files_scanned": 1,
    }
    extra_payload = {"artifacts": {"log_file": str(log_path)}}
    return write_report(
        report_path,
        "check_compile",
        pack.ruleset,
        findings,
        extra_summary,
        extra_payload,
        fail_on_warnings=True,
    )
