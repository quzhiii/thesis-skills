from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from core.project import ThesisProject


_CHAPTER_TITLE_PATTERN = re.compile(r"\\chapter\{([^{}]+)\}")


def _strip_tex_comments(text: str) -> str:
    return re.sub(r"(?m)(?<!\\)%.*$", "", text)


def _extract_chapter_title(text: str, chapter_path: Path) -> str:
    match = _CHAPTER_TITLE_PATTERN.search(text)
    if match:
        return match.group(1).strip()
    return chapter_path.stem.replace("-", " ").replace("_", " ").title()


def _extract_key_points(text: str) -> list[str]:
    stripped = _strip_tex_comments(text)
    lines = [line.strip() for line in stripped.splitlines() if line.strip()]
    key_points: list[str] = []
    for line in lines:
        if line.startswith("\\chapter{"):
            continue
        cleaned = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?\{([^{}]*)\}", r"\1", line)
        cleaned = re.sub(r"\\[a-zA-Z]+\*?", "", cleaned).strip()
        if cleaned:
            key_points.append(cleaned)
        if len(key_points) >= 3:
            break
    return key_points


def build_defense_outline(project: ThesisProject) -> dict[str, Any]:
    sections: list[dict[str, Any]] = []
    for chapter_path in project.chapter_files:
        raw_text = chapter_path.read_text(encoding="utf-8", errors="ignore")
        sections.append(
            {
                "section": _extract_chapter_title(raw_text, chapter_path),
                "source_chapters": [project.rel(chapter_path)],
                "key_points": _extract_key_points(raw_text),
            }
        )

    return {
        "title": "Thesis Defense Outline",
        "sections": sections,
    }
