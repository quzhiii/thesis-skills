from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def _load_report(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def apply_language_fixes(
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
            new_text = re.sub(r"[。]{2,}", "。", new_text)
            new_text = re.sub(r"[，,]{2,}", "，", new_text)
        if new_text != text:
            changed += 1
            preview.append(path.name)
            if apply:
                path.write_text(new_text, encoding="utf-8")
    return {"changed_files": changed, "changed": preview, "applied": apply}


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
    targets: dict[Path, set[str]] = {}
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
