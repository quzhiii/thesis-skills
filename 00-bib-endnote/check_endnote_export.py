#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.canonicalize import normalize_doi
from core.endnote_ris import parse_ris
from core.endnote_xml import parse_endnote_xml
from core.project import ThesisProject
from core.rules import find_rule_pack


def _project_rules(pack: object) -> dict[str, list[str]]:
    rules = getattr(pack, "rules", None)
    if not isinstance(rules, dict):
        raise TypeError("Rule pack rules must be a dictionary")
    project_rules = rules.get("project")
    if not isinstance(project_rules, dict):
        raise TypeError("Rule pack project rules must be a dictionary")
    main_candidates = project_rules.get("main_tex_candidates")
    chapter_globs = project_rules.get("chapter_globs")
    bibliography_files = project_rules.get("bibliography_files")
    if (
        not isinstance(main_candidates, list)
        or not isinstance(chapter_globs, list)
        or not isinstance(bibliography_files, list)
    ):
        raise TypeError("Project rule values must be lists")
    return {
        "main_tex_candidates": [str(item) for item in main_candidates],
        "chapter_globs": [str(item) for item in chapter_globs],
        "bibliography_files": [str(item) for item in bibliography_files],
    }


def detect_format(input_path: Path, declared: str) -> str:
    if declared != "auto":
        return declared
    suffix = input_path.suffix.lower()
    if suffix == ".xml":
        return "xml"
    if suffix == ".ris":
        return "ris"
    raise ValueError(f"Unsupported input format: {input_path.suffix}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Preflight-check EndNote export before import"
    )
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--format", default="auto")
    parser.add_argument("--ruleset", default="tsinghua-thesis")
    parser.add_argument("--report")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    project_root = Path(args.project_root).resolve()
    input_path = Path(args.input).resolve()

    pack = find_rule_pack(repo_root, args.ruleset)
    project_rules = _project_rules(pack)
    project = ThesisProject.discover(
        project_root,
        project_rules["main_tex_candidates"],
        project_rules["chapter_globs"],
        project_rules["bibliography_files"],
    )

    source_format = detect_format(input_path, args.format)
    parsed = (
        parse_endnote_xml(input_path)
        if source_format == "xml"
        else parse_ris(input_path)
    )

    warnings = list(parsed.warnings)
    for ref in parsed.refs:
        if not ref.title:
            warnings.append(f"Record {ref.source_id or '?'} missing title")
        if not ref.authors:
            warnings.append(f"Record {ref.source_id or '?'} missing authors")
        if ref.doi and normalize_doi(ref.doi) != ref.doi.strip().lower().replace(
            "doi:", ""
        ):
            warnings.append(f"Record {ref.source_id or '?'} DOI needs normalization")

    report_path = (
        Path(args.report)
        if args.report
        else project.reports_dir / "check_endnote_export-report.json"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "summary": {
            "source_format": source_format,
            "total_refs": len(parsed.refs),
            "warnings": len(warnings),
            "errors": len(parsed.errors),
            "status": "PASS" if not parsed.errors else "FAIL",
        },
        "warnings": warnings,
        "errors": parsed.errors,
    }
    report_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return 0 if not parsed.errors else 1


if __name__ == "__main__":
    sys.exit(main())
