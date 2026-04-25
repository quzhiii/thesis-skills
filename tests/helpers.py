from __future__ import annotations

import json
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


def readiness_pass_fixture_files() -> dict[str, str]:
    return {
        "reports/run-summary.json": json.dumps(
            {
                "ruleset": "university-generic",
                "steps": {
                    "references": {
                        "exit_code": 0,
                        "report": "reports/check_references-report.json",
                    },
                    "language": {
                        "exit_code": 0,
                        "report": "reports/check_language-report.json",
                    },
                    "format": {
                        "exit_code": 0,
                        "report": "reports/check_format-report.json",
                    },
                    "content": {
                        "exit_code": 0,
                        "report": "reports/check_content-report.json",
                    },
                    "compile": {
                        "status": "parsed",
                        "report": "reports/check_compile-report.json",
                    },
                },
            },
            ensure_ascii=False,
        ),
        "reports/check_references-report.json": json.dumps(
            {
                "summary": {"checker": "check_references", "errors": 0, "warnings": 0, "status": "PASS"},
                "findings": [],
            },
            ensure_ascii=False,
        ),
        "reports/check_language-report.json": json.dumps(
            {
                "summary": {"checker": "check_language", "errors": 0, "warnings": 0, "status": "PASS"},
                "findings": [],
            },
            ensure_ascii=False,
        ),
        "reports/check_format-report.json": json.dumps(
            {
                "summary": {"checker": "check_format", "errors": 0, "warnings": 0, "status": "PASS"},
                "findings": [],
            },
            ensure_ascii=False,
        ),
        "reports/check_content-report.json": json.dumps(
            {
                "summary": {"checker": "check_content", "errors": 0, "warnings": 0, "status": "PASS"},
                "findings": [],
            },
            ensure_ascii=False,
        ),
        "reports/check_compile-report.json": json.dumps(
            {
                "summary": {"checker": "check_compile", "errors": 0, "warnings": 0, "status": "PASS"},
                "findings": [],
            },
            ensure_ascii=False,
        ),
        "reports/latex_to_word-report.json": json.dumps(
            {
                "profile": "review-friendly",
                "warnings": [],
                "unsupported_constructs": [],
                "applied": False,
            },
            ensure_ascii=False,
        ),
    }
