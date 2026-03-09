from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from core.rules import load_rule_pack


def _rewrite_pack_file(path: Path, replacements: dict[str, str]) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    updated: list[str] = []
    for line in lines:
        matched = False
        for key, value in replacements.items():
            prefix = f"{key}:"
            if line.startswith(prefix):
                updated.append(f"{key}: {value}")
                matched = True
                break
        if not matched:
            updated.append(line)
    path.write_text("\n".join(updated) + "\n", encoding="utf-8")


def _load_intake(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def create_rule_pack(
    repo_root: str | Path,
    output_root: str | Path,
    pack_id: str,
    display_name: str,
    starter: str,
    kind: str,
) -> Path:
    repo_root = Path(repo_root)
    output_root = Path(output_root)
    starter_path = repo_root / "90-rules" / "packs" / starter
    if not starter_path.exists():
        raise FileNotFoundError(f"starter pack not found: {starter}")
    destination = output_root / pack_id
    if destination.exists():
        raise FileExistsError(f"target pack already exists: {destination}")
    shutil.copytree(starter_path, destination)
    _rewrite_pack_file(
        destination / "pack.yaml",
        {
            "id": pack_id,
            "display_name": display_name,
            "kind": kind,
            "starter": "false",
        },
    )
    load_rule_pack(destination)
    return destination


def create_draft_pack(
    repo_root: str | Path,
    output_root: str | Path,
    intake_path: str | Path,
) -> Path:
    intake = _load_intake(intake_path)
    pack_id = str(intake["pack_id"])
    display_name = str(intake["display_name"])
    starter = str(intake.get("starter", "university-generic"))
    kind = str(intake.get("kind", "university-thesis"))
    destination = create_rule_pack(
        repo_root, output_root, pack_id, display_name, starter, kind
    )

    mappings_path = destination / "mappings.yaml"
    source_template_mappings = intake.get("word_style_mappings", [])
    chapter_role_mappings = intake.get("chapter_role_mappings", [])
    if not isinstance(source_template_mappings, list):
        source_template_mappings = []
    if not isinstance(chapter_role_mappings, list):
        chapter_role_mappings = []
    mapping_lines = [
        "source_template_mappings:",
    ]
    if source_template_mappings:
        for item in source_template_mappings:
            if not isinstance(item, dict):
                continue
            style = item.get("style", "")
            mapping_lines.append(f"  {style}:")
            mapping_lines.append(f"    role: {item.get('role', '')}")
            mapping_lines.append(f"    latex_command: {item.get('latex_command', '')}")
    else:
        mapping_lines.append("  Heading 1:")
        mapping_lines.append("    role: chapter")
        mapping_lines.append("    latex_command: chapter")
    mapping_lines.append("chapter_role_mappings:")
    if chapter_role_mappings:
        for item in chapter_role_mappings:
            if not isinstance(item, dict):
                continue
            source = item.get("source", "")
            mapping_lines.append(f"  {source}:")
            mapping_lines.append(f"    role: {item.get('role', '')}")
            mapping_lines.append(f"    target: {item.get('target', '')}")
    else:
        mapping_lines.append("  chapter1:")
        mapping_lines.append("    role: introduction")
        mapping_lines.append("    target: chapters/01-introduction.tex")
    mappings_path.write_text("\n".join(mapping_lines) + "\n", encoding="utf-8")

    notes = destination / "draft-notes.md"
    guide_sources = intake.get("guide_sources", [])
    template_sources = intake.get("template_sources", [])
    sample_sources = intake.get("sample_sources", [])
    institution = intake.get("institution", "")
    notes.write_text(
        "\n".join(
            [
                f"# Draft Pack Notes for {display_name}",
                "",
                f"Institution: {institution}",
                f"Starter: {starter}",
                "",
                "## Guide Sources",
                *[f"- {item}" for item in guide_sources],
                "",
                "## Template Sources",
                *[f"- {item}" for item in template_sources],
                "",
                "## Sample Sources",
                *[f"- {item}" for item in sample_sources],
                "",
                "## Manual Confirmation Needed",
                "- Resolve conflicts between written guide and template.",
                "- Confirm title page, abstract, bibliography, and chapter structure requirements.",
                "- Review generated source-template and chapter-role mappings.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    load_rule_pack(destination)
    return destination
