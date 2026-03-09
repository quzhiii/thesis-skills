from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


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

        chapters: list[Path] = []
        for pattern in chapter_globs:
            chapters.extend(sorted(root.glob(pattern)))
        chapters = [path for path in chapters if path.suffix == ".tex"]

        bibs = [root / rel for rel in bibliography_files if (root / rel).exists()]
        abstract_file = root / "abstract.tex"
        if not abstract_file.exists():
            abstract_file = None
        reports_dir = root / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        return cls(root, main_tex, chapters, bibs, abstract_file, reports_dir)

    def rel(self, path: Path) -> str:
        return path.relative_to(self.root).as_posix()
