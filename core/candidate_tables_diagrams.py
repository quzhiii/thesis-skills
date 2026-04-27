from __future__ import annotations

import re
from typing import Any

from core.defense_outline import _extract_chapter_title, _strip_tex_comments
from core.figure_inventory import (
    _CAPTION_PATTERN,
    _FIGURE_PATTERN,
    _INCLUDEGRAPHICS_PATTERN,
    _LABEL_PATTERN,
    _clean_latex_inline,
    _line_of,
)
from core.project import ThesisProject


_TABLE_PATTERN = re.compile(r"\\begin\{(table\*?)\}(.*?)\\end\{\1\}", re.S)
_DIAGRAM_KEYWORDS = ("pipeline", "architecture", "framework", "workflow", "diagram", "overview")


def _extract_tables(project: ThesisProject) -> list[dict[str, Any]]:
    tables: list[dict[str, Any]] = []
    for chapter_path in project.chapter_files:
        raw_text = chapter_path.read_text(encoding="utf-8", errors="ignore")
        stripped = _strip_tex_comments(raw_text)
        chapter_title = _extract_chapter_title(raw_text, chapter_path)
        for match in _TABLE_PATTERN.finditer(stripped):
            block = match.group(2)
            caption_match = _CAPTION_PATTERN.search(block)
            label_match = _LABEL_PATTERN.search(block)
            tables.append(
                {
                    "chapter": chapter_title,
                    "source_chapter": project.rel(chapter_path),
                    "source_line": _line_of(stripped, match.start()),
                    "caption": _clean_latex_inline(caption_match.group(1)) if caption_match else "",
                    "label": label_match.group(1).strip() if label_match else "",
                }
            )
    return tables


def _diagram_reason(caption: str, asset_paths: list[str]) -> str | None:
    caption_lower = caption.casefold()
    for keyword in _DIAGRAM_KEYWORDS:
        if keyword in caption_lower:
            return f"caption_keyword:{keyword}"

    for asset_path in asset_paths:
        asset_lower = asset_path.casefold()
        for keyword in _DIAGRAM_KEYWORDS:
            if keyword in asset_lower:
                return f"asset_keyword:{keyword}"
    return None


def _extract_diagrams(project: ThesisProject) -> list[dict[str, Any]]:
    diagrams: list[dict[str, Any]] = []
    for chapter_path in project.chapter_files:
        raw_text = chapter_path.read_text(encoding="utf-8", errors="ignore")
        stripped = _strip_tex_comments(raw_text)
        chapter_title = _extract_chapter_title(raw_text, chapter_path)
        for match in _FIGURE_PATTERN.finditer(stripped):
            block = match.group(2)
            caption_match = _CAPTION_PATTERN.search(block)
            label_match = _LABEL_PATTERN.search(block)
            caption = _clean_latex_inline(caption_match.group(1)) if caption_match else ""
            asset_paths = [item.strip() for item in _INCLUDEGRAPHICS_PATTERN.findall(block) if item.strip()]
            reason = _diagram_reason(caption, asset_paths)
            if reason is None:
                continue
            diagrams.append(
                {
                    "chapter": chapter_title,
                    "source_chapter": project.rel(chapter_path),
                    "source_line": _line_of(stripped, match.start()),
                    "caption": caption,
                    "label": label_match.group(1).strip() if label_match else "",
                    "asset_paths": asset_paths,
                    "candidate_reason": reason,
                }
            )
    return diagrams


def build_candidate_tables_diagrams(project: ThesisProject) -> dict[str, Any]:
    tables = _extract_tables(project)
    diagrams = _extract_diagrams(project)
    return {
        "title": "Defense Candidate Tables And Diagrams",
        "tables": tables,
        "diagrams": diagrams,
    }
