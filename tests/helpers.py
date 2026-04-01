from __future__ import annotations

import shutil
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[1]
TMP_ROOT = ROOT / ".worktrees" / "pytest-tmp"


@contextmanager
def workspace_tempdir(prefix: str) -> Iterator[Path]:
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    path = TMP_ROOT / f"{prefix}{uuid4().hex}"
    path.mkdir(parents=True, exist_ok=False)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


@contextmanager
def workspace_project_copy(source: Path, prefix: str) -> Iterator[Path]:
    with workspace_tempdir(prefix) as tempdir:
        target = tempdir / source.name
        shutil.copytree(source, target)
        yield target


def materialize_project(root: Path, files: dict[str, str]) -> Path:
    for relative_path, content in files.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return root
