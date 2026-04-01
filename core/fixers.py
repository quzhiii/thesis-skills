from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from core.patches import (
    apply_patch_to_text,
    build_patch_from_finding,
    detect_patch_conflicts,
    validate_patch_text,
)


_UNIT_PATTERN = (
    r"(mg|kg|g|km|cm|mm|m|μm|nm|mL|uL|L|ms|min|h|s|kHz|MHz|GHz|Hz|mV|kV|V|mA|A|"
    r"kW|W|kPa|MPa|Pa|GB|MB|TB|°C)\b"
)
_ASCII_TO_FULLWIDTH = str.maketrans({",": "，", ";": "；", ":": "：", "!": "！", "?": "？"})
_FULLWIDTH_TO_ASCII = str.maketrans({"，": ",", "；": ";", "：": ":", "！": "!", "？": "?"})


def _load_report(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _collapse_repeated_punctuation(text: str) -> str:
    text = re.sub(r"。{2,}", "。", text)
    text = re.sub(r"[，,]{2,}", lambda match: "，" if "，" in match.group(0) else ",", text)
    text = re.sub(r"[；;]{2,}", lambda match: "；" if "；" in match.group(0) else ";", text)
    text = re.sub(r"[：:]{2,}", lambda match: "：" if "：" in match.group(0) else ":", text)
    return text


def _normalize_ellipsis(text: str) -> str:
    text = text.replace("。。。。。。", "……")
    text = re.sub(
        r"(?<=[\u4e00-\u9fff])\.{6}(?=$|[\u4e00-\u9fff，。！？；：])", "……", text
    )
    return re.sub(
        r"(?<=[\u4e00-\u9fff])\.{3}(?=$|[\u4e00-\u9fff，。！？；：])", "……", text
    )


def _normalize_fullwidth_halfwidth_mix(text: str) -> str:
    text = re.sub(
        r"([\u4e00-\u9fff])([,;:!?])([\u4e00-\u9fff])",
        lambda match: (
            f"{match.group(1)}"
            f"{match.group(2).translate(_ASCII_TO_FULLWIDTH)}"
            f"{match.group(3)}"
        ),
        text,
    )
    return re.sub(
        r"([A-Za-z0-9])([，；：！？])([A-Za-z0-9])",
        lambda match: (
            f"{match.group(1)}"
            f"{match.group(2).translate(_FULLWIDTH_TO_ASCII)}"
            f"{match.group(3)}"
        ),
        text,
    )


def apply_language_fixes(
    project_root: str | Path, report_path: str | Path, apply: bool
) -> dict[str, object]:
    project_root = Path(project_root)
    report = _load_report(report_path)
    targets: dict[Path, set[str]] = {}
    findings: list[Any] = report.get("findings", [])
    if not isinstance(findings, list):
        findings = []
    for finding in findings:
        if not isinstance(finding, dict):
            continue
        file_name = finding.get("file")
        code = finding.get("code")
        if isinstance(file_name, str) and file_name and isinstance(code, str):
            targets.setdefault(project_root / file_name, set()).add(code)
    changed = 0
    preview: list[str] = []
    for path, codes in targets.items():
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        new_text = text
        if "LANG_CJK_LATIN_SPACING" in codes:
            new_text = re.sub(
                r"([\u4e00-\u9fff])([A-Za-z][A-Za-z0-9-]{1,})", r"\1 \2", new_text
            )
            new_text = re.sub(
                r"([A-Za-z][A-Za-z0-9-]{1,})([\u4e00-\u9fff])", r"\1 \2", new_text
            )
        if "LANG_REPEAT_PUNC" in codes:
            new_text = _collapse_repeated_punctuation(new_text)
        if "LANG_UNIT_SPACING" in codes:
            new_text = re.sub(
                rf"(?<![A-Za-z])(\d+(?:\.\d+)?)\s*{_UNIT_PATTERN}",
                r"\1 \2",
                new_text,
            )
        if "LANG_ELLIPSIS_STYLE" in codes:
            new_text = _normalize_ellipsis(new_text)
        if "LANG_FULLWIDTH_HALFWIDTH_MIX" in codes:
            new_text = _normalize_fullwidth_halfwidth_mix(new_text)
        if new_text != text:
            changed += 1
            preview.append(path.relative_to(project_root).as_posix())
            if apply:
                path.write_text(new_text, encoding="utf-8")
    return {"changed_files": changed, "changed": preview, "applied": apply}


def apply_language_deep_fixes(
    project_root: str | Path,
    report_path: str | Path,
    apply: bool,
    *,
    include_review_required: bool = False,
    issue_codes: set[str] | None = None,
) -> dict[str, object]:
    project_root = Path(project_root)
    report = _load_report(report_path)
    findings: list[Any] = report.get("findings", [])
    if not isinstance(findings, list):
        findings = []

    selected_findings: list[dict[str, object]] = []
    skipped_preview: list[dict[str, object]] = []
    for finding in findings:
        if not isinstance(finding, dict):
            continue
        code = finding.get("code")
        if issue_codes and isinstance(code, str) and code not in issue_codes:
            skipped_preview.append(
                {
                    "reason": "not_selected",
                    "code": code,
                    "file": finding.get("file", ""),
                    "line": finding.get("line", 0),
                }
            )
            continue
        selected_findings.append(finding)

    generated_patches = []
    skipped_generation: list[dict[str, object]] = []
    for finding in selected_findings:
        patch, reason = build_patch_from_finding(project_root, finding)
        if patch is None:
            skipped_generation.append(
                {
                    "reason": reason or "unsupported",
                    "code": finding.get("code", ""),
                    "file": finding.get("file", ""),
                    "line": finding.get("line", 0),
                }
            )
            continue
        generated_patches.append(patch)

    valid_patches = []
    mismatches: list[dict[str, object]] = []
    for patch in generated_patches:
        path = project_root / patch.file
        text = path.read_text(encoding="utf-8")
        if not validate_patch_text(text, patch):
            mismatches.append(
                {
                    "reason": "old_text_mismatch",
                    "patch": patch.as_dict(),
                }
            )
            continue
        valid_patches.append(patch)

    conflict_free_patches, conflicts = detect_patch_conflicts(project_root, valid_patches)
    preview = [patch.as_dict() for patch in conflict_free_patches]

    eligible = []
    skipped_review_required: list[dict[str, object]] = []
    for patch in conflict_free_patches:
        if patch.review_required and not include_review_required:
            skipped_review_required.append(
                {
                    "reason": "review_required",
                    "patch": patch.as_dict(),
                }
            )
            continue
        eligible.append(patch)

    changed_files: set[str] = set()
    applied_patches: list[dict[str, object]] = []
    if apply and eligible:
        by_file: dict[str, list[Any]] = {}
        for patch in eligible:
            by_file.setdefault(patch.file, []).append(patch)
        for file_name, patches in by_file.items():
            path = project_root / file_name
            text = path.read_text(encoding="utf-8")
            ordered = sorted(
                patches,
                key=lambda item: (
                    item.start["line"],
                    item.start["column"],
                    item.end["line"],
                    item.end["column"],
                ),
                reverse=True,
            )
            new_text = text
            for patch in ordered:
                if not validate_patch_text(new_text, patch):
                    mismatches.append(
                        {
                            "reason": "old_text_mismatch_after_rewrite",
                            "patch": patch.as_dict(),
                        }
                    )
                    continue
                new_text = apply_patch_to_text(new_text, patch)
                applied_patches.append(patch.as_dict())
            if new_text != text:
                path.write_text(new_text, encoding="utf-8")
                changed_files.add(file_name)

    return {
        "applied": apply,
        "preview_only": not apply,
        "include_review_required": include_review_required,
        "selected_issue_codes": sorted(issue_codes) if issue_codes else [],
        "preview_count": len(preview),
        "patches": preview,
        "applied_patches": applied_patches,
        "changed_files": len(changed_files),
        "changed": sorted(changed_files),
        "skipped_preview": skipped_preview,
        "skipped_generation": skipped_generation,
        "skipped_review_required": skipped_review_required,
        "conflicts": conflicts,
        "mismatches": mismatches,
    }


def apply_reference_fixes(
    project_root: str | Path, report_path: str | Path, apply: bool
) -> dict[str, object]:
    project_root = Path(project_root)
    report = _load_report(report_path)
    missing_keys = []
    findings: list[Any] = report.get("findings", [])
    if not isinstance(findings, list):
        findings = []
    for finding in findings:
        if not isinstance(finding, dict):
            continue
        if finding.get("code") == "REF_MISSING_KEY":
            message = str(finding.get("message", ""))
            missing_keys.append(message.rsplit(":", 1)[-1].strip())
    target = project_root / "ref" / "refs-import.generated.bib"
    additions = []
    for key in sorted(set(missing_keys)):
        additions.append(
            f"@misc{{{key},\n  title = {{{key}}},\n  note = {{TODO: complete imported reference}}\n}}\n"
        )
    if apply and additions:
        target.parent.mkdir(parents=True, exist_ok=True)
        existing = target.read_text(encoding="utf-8") if target.exists() else ""
        target.write_text(existing + "\n" + "\n".join(additions), encoding="utf-8")
    return {
        "generated_entries": len(additions),
        "target": target.as_posix(),
        "applied": apply,
    }


def apply_format_fixes(
    project_root: str | Path, report_path: str | Path, apply: bool
) -> dict[str, object]:
    project_root = Path(project_root)
    report = _load_report(report_path)
    targets: dict[Path, list[dict[str, object]]] = {}
    findings: list[Any] = report.get("findings", [])
    if not isinstance(findings, list):
        findings = []
    for finding in findings:
        if not isinstance(finding, dict):
            continue
        file_name = finding.get("file")
        code = finding.get("code")
        if (
            isinstance(file_name, str)
            and file_name.endswith(".tex")
            and isinstance(code, str)
        ):
            targets.setdefault(project_root / file_name, []).append(finding)
    changed = 0
    for path, file_findings in targets.items():
        if not path.exists():
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        original_text = "\n".join(lines) + ("\n" if lines else "")
        orphan_lines = {
            int(item.get("line", 0))
            for item in file_findings
            if item.get("code") == "FMT_ORPHAN_LABEL"
            and isinstance(item.get("line"), int)
        }
        centering_lines = {
            int(item.get("line", 0))
            for item in file_findings
            if item.get("code") == "FMT_MISSING_CENTERING"
            and isinstance(item.get("line"), int)
        }
        updated: list[str] = []
        for index, line in enumerate(lines, start=1):
            if index in orphan_lines and "\\label{" in line:
                continue
            updated.append(line)
            if index in centering_lines and line.strip() == "\\begin{figure}":
                updated.append("\\centering")
        new_text = "\n".join(updated) + ("\n" if lines else "")
        if new_text != original_text:
            changed += 1
            if apply:
                path.write_text(new_text, encoding="utf-8")
    return {"changed_files": changed, "applied": apply}
