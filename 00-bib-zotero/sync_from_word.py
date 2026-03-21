#!/usr/bin/env python3
"""
Sync Zotero citations from Word to LaTeX project.

This script:
1. Extracts Zotero citations embedded in a Word docx file
2. Compares with existing LaTeX project citation mapping
3. Reports new/removed citations
4. Optionally updates mapping and citation-lock.tex

Usage:
    python 00-bib-zotero/sync_from_word.py --project-root <latex-project> --word-file <word.docx>
    python 00-bib-zotero/sync_from_word.py --project-root <latex-project> --word-file <word.docx> --apply
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.citation_mapping import CitationMapping, parse_bib_keys_from_files
from core.project import ThesisProject
from core.rules import find_rule_pack
from core.zotero_extract import extract_zotero_citations, compare_citations


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sync Zotero citations from Word to LaTeX project"
    )
    parser.add_argument("--project-root", required=True, help="Path to LaTeX project")
    parser.add_argument("--word-file", required=True, help="Path to Word docx file")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default: dry-run)")
    parser.add_argument("--ruleset", default="tsinghua-thesis", help="Rule pack to use")
    parser.add_argument("--report", help="Path to write JSON report")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    project_root = Path(args.project_root).resolve()
    word_path = Path(args.word_file).resolve()

    # Load rule pack
    pack = find_rule_pack(repo_root, args.ruleset)

    # Discover project structure
    try:
        project = ThesisProject.discover(
            project_root,
            pack.rules["project"]["main_tex_candidates"],
            pack.rules["project"]["chapter_globs"],
            pack.rules["project"]["bibliography_files"],
        )
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 2

    print("=" * 60)
    print("Word → LaTeX Citation Sync")
    print("=" * 60)
    print(f"Project: {project.root}")
    print(f"Word file: {word_path.name}")
    print(f"Mode: {'APPLY' if args.apply else 'DRY-RUN'}")

    # Extract citations from Word
    print("\n[1/4] Extracting Zotero citations from Word...")
    extraction = extract_zotero_citations(word_path)

    if extraction.errors:
        print("Errors:")
        for err in extraction.errors:
            print(f"  - {err}")
        return 2

    print(f"  Found {extraction.citation_count} unique citations")

    # Load existing mapping
    print("\n[2/4] Loading existing citation mapping...")
    mapping = CitationMapping.load(project_root)
    print(f"  Existing mappings: {len(mapping.mappings)}")

    # Get existing bib keys
    bib_keys = parse_bib_keys_from_files(project.bibliography_files)
    print(f"  BibTeX entries: {len(bib_keys)}")

    # Compare
    print("\n[3/4] Comparing citations...")
    comparison = compare_citations(extraction, mapping.mappings)

    new_keys = comparison["new_keys"]
    removed_keys = comparison["removed_keys"]

    print(f"  New citations: {len(new_keys)}")
    print(f"  Removed citations: {len(removed_keys)}")
    print(f"  Unchanged: {len(comparison['unchanged_keys'])}")

    # Generate report
    report = {
        "source_file": str(word_path),
        "project_root": str(project_root),
        "mode": "apply" if args.apply else "dry-run",
        "word_citations": extraction.citation_count,
        "existing_mappings": len(mapping.mappings),
        "bibtex_entries": len(bib_keys),
        "new_citations": sorted(new_keys),
        "removed_citations": sorted(removed_keys),
        "unchanged_count": len(comparison["unchanged_keys"]),
        "actions": []
    }

    # Handle new citations
    if new_keys:
        print("\n[4/4] Processing new citations...")
        for zotero_key in sorted(new_keys):
            latex_key = mapping.get_or_create_latex_key(zotero_key)
            print(f"  + {zotero_key[:50]}... → {latex_key}")
            report["actions"].append({
                "action": "add",
                "zotero_key": zotero_key,
                "latex_key": latex_key
            })

        if args.apply:
            mapping.save("Updated by sync_from_word.py")
            print(f"\n  Saved mapping to {mapping.mapping_file}")

            # Generate citation-lock.tex
            lock_file = project_root / "citation-lock.tex"
            lock_content = mapping.to_citation_lock_content()
            lock_file.write_text(lock_content, encoding="utf-8")
            print(f"  Generated {lock_file.name}")
    else:
        print("\n[4/4] No new citations to add")

    # Handle removed citations
    if removed_keys:
        print(f"\nNote: {len(removed_keys)} citations removed from Word")
        print("  (BibTeX entries are preserved to maintain numbering)")
        for key in sorted(removed_keys)[:5]:
            print(f"  - {key[:50]}...")
        if len(removed_keys) > 5:
            print(f"  ... and {len(removed_keys) - 5} more")

    # Summary
    print("\n" + "=" * 60)
    if args.apply:
        print("Changes applied successfully")
    else:
        print("Dry-run complete. Use --apply to make changes.")
    print("=" * 60)

    # Write report
    report_path = Path(args.report) if args.report else project.reports_dir / "sync_from_word-report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nReport: {report_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
