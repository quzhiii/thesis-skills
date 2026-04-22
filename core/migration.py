from __future__ import annotations

import json
import shutil
import subprocess
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


def run_latex_to_word_migration(
    project_root: str | Path,
    output_file: str | Path,
    profile: str,
    apply: bool,
) -> dict[str, object]:
    project_root = Path(project_root).resolve()
    output_file = Path(output_file).resolve()
    main_tex = project_root / "main.tex"
    if not main_tex.exists():
        tex_candidates = sorted(project_root.glob("*.tex"))
        if not tex_candidates:
            raise FileNotFoundError("main tex file not found")
        main_tex = tex_candidates[0]

    chapter_files = sorted(project_root.glob("chapters/*.tex"))
    warnings: list[str] = []
    unsupported_constructs: list[str] = []
    for tex in [main_tex] + chapter_files:
        text = tex.read_text(encoding="utf-8", errors="ignore")
        rel = tex.relative_to(project_root).as_posix()
        if "\\begin{tikzpicture}" in text:
            unsupported_constructs.append(f"tikzpicture:{rel}")
        if "\\newcommand" in text or "\\renewcommand" in text:
            warnings.append(f"custom-macro:{rel}")
        for env in ("align", "align*", "equation", "equation*", "gather", "gather*"):
            if f"\\begin{{{env}}}" in text:
                warnings.append(f"math-env:{env}:{rel}")
                break

    result: dict[str, object] = {
        "project_root": str(project_root),
        "profile": profile,
        "output_file": str(output_file),
        "applied": False,
        "main_tex": main_tex.relative_to(project_root).as_posix(),
        "chapters": [path.relative_to(project_root).as_posix() for path in chapter_files],
        "warnings": warnings,
        "unsupported_constructs": unsupported_constructs,
    }

    if apply:
        pandoc_path = shutil.which("pandoc")
        if pandoc_path is None:
            try:
                import pypandoc
                pandoc_path = pypandoc.get_pandoc_path()
            except Exception:
                pass
        if pandoc_path is None:
            result["conversion_error"] = "pandoc not found: install pandoc or pypandoc-binary to enable .docx export"
            return result
        try:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(
                [
                    pandoc_path,
                    str(main_tex),
                    "-f", "latex",
                    "-t", "docx",
                    "-o", str(output_file),
                    "--wrap=none",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            result["applied"] = True
        except subprocess.CalledProcessError as exc:
            result["conversion_error"] = f"pandoc failed: {exc.stderr or exc.stdout or 'unknown error'}"
        except Exception as exc:
            result["conversion_error"] = f"conversion error: {exc}"

    return result
