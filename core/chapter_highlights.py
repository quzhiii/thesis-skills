from __future__ import annotations

from typing import Any

from core.defense_outline import _extract_chapter_title, _extract_key_points
from core.project import ThesisProject


def _infer_defense_role(title: str) -> str:
    lowered = title.casefold()
    if "intro" in lowered or "background" in lowered:
        return "background"
    if "method" in lowered or "approach" in lowered or "design" in lowered:
        return "approach"
    if "result" in lowered or "discussion" in lowered or "experiment" in lowered:
        return "evidence"
    if "conclusion" in lowered or "summary" in lowered or "future" in lowered:
        return "takeaway"
    return "supporting"


def build_chapter_highlights(project: ThesisProject) -> dict[str, Any]:
    sections: list[dict[str, Any]] = []
    for chapter_path in project.chapter_files:
        raw_text = chapter_path.read_text(encoding="utf-8", errors="ignore")
        title = _extract_chapter_title(raw_text, chapter_path)
        sections.append(
            {
                "chapter": title,
                "source_chapter": project.rel(chapter_path),
                "defense_role": _infer_defense_role(title),
                "highlight_points": _extract_key_points(raw_text),
            }
        )

    return {
        "title": "Defense Chapter Highlights",
        "sections": sections,
    }
