from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from core.defense_outline import _extract_chapter_title, _strip_tex_comments
from core.project import ThesisProject


_FIGURE_PATTERN = re.compile(r"\\begin\{(figure\*?)\}(.*?)\\end\{\1\}", re.S)
_INCLUDEGRAPHICS_PATTERN = re.compile(
    r"\\includegraphics(?:\[[^\]]*\])?\{([^{}]+)\}"
)
_CAPTION_PATTERN = re.compile(
    r"\\caption(?:\[[^\]]*\])?\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}",
    re.S,
)
_LABEL_PATTERN = re.compile(r"\\label\{([^{}]+)\}")
_COMMAND_PATTERN = re.compile(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{([^{}]*)\})?")


def _clean_latex_inline(text: str) -> str:
    cleaned = text.strip()
    previous = None
    while cleaned != previous:
        previous = cleaned
        cleaned = _COMMAND_PATTERN.sub(lambda match: match.group(1) or "", cleaned).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def _line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def build_figure_inventory(project: ThesisProject) -> dict[str, Any]:
    figures: list[dict[str, Any]] = []
    for chapter_path in project.chapter_files:
        raw_text = chapter_path.read_text(encoding="utf-8", errors="ignore")
        stripped = _strip_tex_comments(raw_text)
        chapter_title = _extract_chapter_title(raw_text, chapter_path)
        for match in _FIGURE_PATTERN.finditer(stripped):
            block = match.group(2)
            caption_match = _CAPTION_PATTERN.search(block)
            label_match = _LABEL_PATTERN.search(block)
            figures.append(
                {
                    "chapter": chapter_title,
                    "source_chapter": project.rel(chapter_path),
                    "source_line": _line_of(stripped, match.start()),
                    "caption": _clean_latex_inline(caption_match.group(1)) if caption_match else "",
                    "label": label_match.group(1).strip() if label_match else "",
                    "asset_paths": [item.strip() for item in _INCLUDEGRAPHICS_PATTERN.findall(block) if item.strip()],
                }
            )

    return {
        "title": "Defense Figure Inventory",
        "figures": figures,
    }
