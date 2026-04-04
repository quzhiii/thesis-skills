from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


_INPUT_PATTERN = re.compile(r"\\(?:input|include)\{([^{}]+)\}")


def _strip_tex_comments(text: str) -> str:
    return re.sub(r"(?m)(?<!\\)%.*$", "", text)


def _resolve_included_tex(root: Path, include_target: str) -> Path | None:
    normalized = include_target.strip()
    if not normalized:
        return None
    candidate = root / normalized
    if candidate.suffix != ".tex":
        candidate = candidate.with_suffix(".tex")
    if candidate.exists() and candidate.is_file():
        return candidate.resolve()
    return None


def _discover_chapters_from_main(root: Path, main_tex: Path) -> list[Path]:
    text = _strip_tex_comments(main_tex.read_text(encoding="utf-8", errors="ignore"))
    chapters: list[Path] = []
    seen: set[Path] = set()
    for include_target in _INPUT_PATTERN.findall(text):
        path = _resolve_included_tex(root, include_target)
        if path is None or path == main_tex.resolve():
            continue
        if path in seen:
            continue
        seen.add(path)
        chapters.append(path)
    return chapters


def _matches_chapter_globs(root: Path, path: Path, chapter_globs: list[str]) -> bool:
    relative = path.relative_to(root).as_posix()
    return any(Path(relative).match(pattern) for pattern in chapter_globs)


@dataclass
class ThesisProject:
    root: Path
    main_tex: Path
    chapter_files: list[Path]
    bibliography_files: list[Path]
    abstract_file: Path | None
    reports_dir: Path

    @classmethod
    def discover(
        cls,
        root: str | Path,
        main_candidates: list[str],
        chapter_globs: list[str],
        bibliography_files: list[str],
    ) -> "ThesisProject":
        root = Path(root).resolve()
        main_tex = None
        for candidate in main_candidates:
            path = root / candidate
            if path.exists():
                main_tex = path
                break
        if main_tex is None:
            raise FileNotFoundError("main tex file not found")

        chapters = [
            path
            for path in _discover_chapters_from_main(root, main_tex)
            if _matches_chapter_globs(root, path, chapter_globs)
        ]
        if not chapters:
            chapters = []
            for pattern in chapter_globs:
                chapters.extend(sorted(root.glob(pattern)))
            chapters = [path.resolve() for path in chapters if path.suffix == ".tex"]

        bibs = [root / rel for rel in bibliography_files if (root / rel).exists()]
        abstract_file = root / "abstract.tex"
        if not abstract_file.exists():
            abstract_file = None
        reports_dir = root / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        return cls(root, main_tex, chapters, bibs, abstract_file, reports_dir)

    def rel(self, path: Path) -> str:
        return path.relative_to(self.root).as_posix()
