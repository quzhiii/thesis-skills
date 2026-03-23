#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.bib_render import render_bib_file
from core.canonicalize import canonicalize_ref
from core.citation_models import CanonicalRef, ImportResult
from core.endnote_ris import parse_ris
from core.endnote_xml import parse_endnote_xml
from core.project import ThesisProject
from core.rules import find_rule_pack


dedupe_refs = importlib.import_module("core.match_refs").dedupe_refs


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
    if suffix == ".bib":
        return "bib"
    raise ValueError(f"Unsupported input format: {input_path.suffix}")


def parse_input(input_path: Path, source_format: str) -> ImportResult:
    if source_format == "xml":
        return parse_endnote_xml(input_path)
    if source_format == "ris":
        return parse_ris(input_path)
    raise ValueError(f"Unsupported format for current dry-run slice: {source_format}")


def build_mapping(refs: list[CanonicalRef]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for index, ref in enumerate(refs, start=1):
        mapping[ref.canonical_id] = f"ref{index:03d}"
    return mapping


def reuse_mapping(refs: list[CanonicalRef], existing: dict[str, str]) -> dict[str, str]:
    mapping = dict(existing)
    next_ref = 1
    for value in mapping.values():
        if value.startswith("ref"):
            try:
                next_ref = max(next_ref, int(value[3:]) + 1)
            except ValueError:
                pass

    for ref in refs:
        if ref.canonical_id not in mapping:
            mapping[ref.canonical_id] = f"ref{next_ref:03d}"
            next_ref += 1
    return mapping


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Import EndNote library into thesis project"
    )
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--format", default="auto")
    parser.add_argument("--ruleset", default="tsinghua-thesis")
    parser.add_argument("--apply", action="store_true")
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
    parsed = parse_input(input_path, source_format)
    refs = [canonicalize_ref(ref) for ref in parsed.refs]
    deduped_refs, dedupe_warnings = dedupe_refs(refs)

    existing_mapping = {}
    mapping_file = project.root / "ref" / "citation-mapping.json"
    if mapping_file.exists():
        try:
            existing_payload = json.loads(mapping_file.read_text(encoding="utf-8"))
            mappings_raw = existing_payload.get("mappings", {})
            if isinstance(mappings_raw, dict):
                existing_mapping = {
                    str(key): str(value) for key, value in mappings_raw.items()
                }
        except json.JSONDecodeError:
            existing_mapping = {}

    mapping = reuse_mapping(deduped_refs, existing_mapping)
    rendered = render_bib_file(deduped_refs, mapping)

    report_path = (
        Path(args.report)
        if args.report
        else project.reports_dir / "endnote-import-report.json"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_payload = {
        "summary": {
            "mode": "apply" if args.apply else "dry-run",
            "source_format": source_format,
            "total_refs": len(refs),
            "rendered_refs": len(deduped_refs),
            "deduped_refs": len(refs) - len(deduped_refs),
            "warnings": len(parsed.warnings) + len(dedupe_warnings),
            "errors": len(parsed.errors),
        },
        "warnings": parsed.warnings + dedupe_warnings,
        "errors": parsed.errors,
        "mapping_preview": mapping,
        "render_preview": rendered,
    }
    report_path.write_text(
        json.dumps(report_payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    if args.apply:
        ref_dir = project.root / "ref"
        ref_dir.mkdir(parents=True, exist_ok=True)
        (ref_dir / "refs-import.bib").write_text(rendered, encoding="utf-8")
        mapping_payload = {
            "description": "Source citation key to LaTeX ref number mapping",
            "version": "2.0",
            "mappings": mapping,
        }
        mapping_file.parent.mkdir(parents=True, exist_ok=True)
        mapping_file.write_text(
            json.dumps(mapping_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
