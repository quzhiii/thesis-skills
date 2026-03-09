from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any


def _load_spec(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _copy_mapping_group(
    source_root: Path,
    target_root: Path,
    mappings: list[dict[str, object]],
    apply: bool,
) -> tuple[int, list[str]]:
    copied = 0
    targets: list[str] = []
    for item in mappings:
        src_rel = item.get("from")
        dst_rel = item.get("to")
        if not isinstance(src_rel, str) or not isinstance(dst_rel, str):
            continue
        src = source_root / src_rel
        dst = target_root / dst_rel
        if not src.exists():
            raise FileNotFoundError(f"migration source not found: {src}")
        targets.append(dst.relative_to(target_root).as_posix())
        if apply:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        copied += 1
    return copied, targets


def run_word_to_latex_migration(
    source_root: str | Path,
    target_root: str | Path,
    spec_path: str | Path,
    apply: bool,
) -> dict[str, object]:
    source_root = Path(source_root)
    target_root = Path(target_root)
    spec = _load_spec(spec_path)
    document_metadata = spec.get("document_metadata", {})
    word_style_mappings = spec.get("word_style_mappings", [])
    chapter_role_mappings = spec.get("chapter_role_mappings", [])
    chapter_mappings = spec.get("chapter_mappings", [])
    bibliography_mappings = spec.get("bibliography_mappings", [])
    if not isinstance(document_metadata, dict):
        document_metadata = {}
    if not isinstance(word_style_mappings, list):
        word_style_mappings = []
    if not isinstance(chapter_role_mappings, list):
        chapter_role_mappings = []
    if not isinstance(chapter_mappings, list):
        chapter_mappings = []
    if not isinstance(bibliography_mappings, list):
        bibliography_mappings = []
    copied_chapters, chapter_targets = _copy_mapping_group(
        source_root, target_root, chapter_mappings, apply
    )
    copied_bibs, bib_targets = _copy_mapping_group(
        source_root, target_root, bibliography_mappings, apply
    )
    return {
        "copied_files": copied_chapters + copied_bibs,
        "document_metadata": document_metadata,
        "word_style_mappings": word_style_mappings,
        "chapter_role_mappings": chapter_role_mappings,
        "chapter_targets": chapter_targets,
        "bibliography_targets": bib_targets,
        "applied": apply,
    }
