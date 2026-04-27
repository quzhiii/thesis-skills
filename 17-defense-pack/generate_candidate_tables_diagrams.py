from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.candidate_tables_diagrams import build_candidate_tables_diagrams
from core.project import ThesisProject
from core.reports import write_review_artifact
from core.rules import find_rule_pack


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a bounded candidate tables and diagrams artifact")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--ruleset", default="tsinghua-thesis")
    parser.add_argument("--artifact")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    pack = find_rule_pack(repo_root, args.ruleset)
    project_rules = pack.rules.get("project", {})
    if not isinstance(project_rules, dict):
        raise TypeError("project rules missing")

    main_tex_candidates = project_rules.get("main_tex_candidates")
    chapter_globs = project_rules.get("chapter_globs")
    bibliography_files = project_rules.get("bibliography_files")
    if not isinstance(main_tex_candidates, list) or not isinstance(chapter_globs, list) or not isinstance(bibliography_files, list):
        raise TypeError("project rules incomplete")

    project = ThesisProject.discover(
        args.project_root,
        [str(item) for item in main_tex_candidates],
        [str(item) for item in chapter_globs],
        [str(item) for item in bibliography_files],
    )
    artifact_path = Path(args.artifact) if args.artifact else project.reports_dir / "candidate-tables-diagrams-artifact.json"

    payload = build_candidate_tables_diagrams(project)
    tables = payload.get("tables", [])
    diagrams = payload.get("diagrams", [])
    table_count = len(tables) if isinstance(tables, list) else 0
    diagram_count = len(diagrams) if isinstance(diagrams, list) else 0
    write_review_artifact(
        artifact_path,
        artifact_type="candidate_tables_diagrams",
        summary={
            "project_root": str(project.root),
            "chapter_count": len(project.chapter_files),
            "table_count": table_count,
            "diagram_count": diagram_count,
            "candidate_count": table_count + diagram_count,
        },
        payload=payload,
    )
    print(artifact_path.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
