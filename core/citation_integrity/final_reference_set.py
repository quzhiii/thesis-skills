from __future__ import annotations

import csv
import json
import re

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from core.citation_integrity.bib_parser import parse_bib_entries_from_text
from core.citation_integrity.tex_parser import collect_citations_from_text
from core.project import ThesisProject


_AUX_CITATION_RE = re.compile(r"\\citation\{([^{}]*)\}")
_AUX_BIBDATA_RE = re.compile(r"\\bibdata\{([^{}]*)\}")
_AUX_BIBCITE_RE = re.compile(r"\\bibcite\{([^{}]*)\}")
_BBL_BIBITEM_RE = re.compile(r"\\bibitem(?:\[[^\]]*\])?\{([^{}]*)\}")


@dataclass(frozen=True)
class AuxData:
    citation_keys: list[str]
    bibdata_sources: list[str]
    bibcite_keys: list[str]


def _split_keys(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _unique_in_order(keys: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for key in keys:
        if key in seen:
            continue
        seen.add(key)
        result.append(key)
    return result


def parse_aux_file(path: Path) -> AuxData:
    text = path.read_text(encoding="utf-8", errors="ignore")
    citation_keys: list[str] = []
    bibdata_sources: list[str] = []
    bibcite_keys: list[str] = []

    for match in _AUX_CITATION_RE.finditer(text):
        citation_keys.extend(_split_keys(match.group(1)))
    for match in _AUX_BIBDATA_RE.finditer(text):
        bibdata_sources.extend(_split_keys(match.group(1)))
    for match in _AUX_BIBCITE_RE.finditer(text):
        bibcite_keys.append(match.group(1).strip())

    return AuxData(
        citation_keys=_unique_in_order(citation_keys),
        bibdata_sources=_unique_in_order(bibdata_sources),
        bibcite_keys=_unique_in_order([key for key in bibcite_keys if key]),
    )


def parse_bbl_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    return _unique_in_order([match.group(1).strip() for match in _BBL_BIBITEM_RE.finditer(text) if match.group(1).strip()])


def _read_bib_entries(project: ThesisProject) -> tuple[list[str], set[str]]:
    keys: list[str] = []
    sources: set[str] = set()
    for bib_file in project.bibliography_files:
        relative = project.rel(bib_file)
        sources.add(relative)
        entries = parse_bib_entries_from_text(
            bib_file.read_text(encoding="utf-8", errors="ignore"),
            relative,
        )
        keys.extend(entry.key for entry in entries)
    return keys, sources


def _collect_tex_citation_keys(project: ThesisProject) -> list[str]:
    paths = [project.main_tex, *project.chapter_files]
    keys: list[str] = []
    for path in paths:
        relative = project.rel(path)
        text = path.read_text(encoding="utf-8", errors="ignore")
        keys.extend(item.key for item in collect_citations_from_text(text, relative))
    return _unique_in_order(keys)


def _issue(code: str, key: str, severity: str, message: str) -> dict[str, str]:
    return {"code": code, "key": key, "severity": severity, "message": message}


def build_final_reference_set_report(project: ThesisProject) -> dict[str, object]:
    aux_path = project.main_tex.with_suffix(".aux")
    bbl_path = project.main_tex.with_suffix(".bbl")
    bib_keys, active_bib_sources = _read_bib_entries(project)
    bib_key_set = set(bib_keys)

    if aux_path.exists() and bbl_path.exists():
        aux_data = parse_aux_file(aux_path)
        aux_citation_keys = aux_data.citation_keys
        bbl_bibitem_keys = parse_bbl_file(bbl_path)
        final_keys = bbl_bibitem_keys
        source = "aux+bbl"
    else:
        aux_citation_keys = sorted(_collect_tex_citation_keys(project))
        bbl_bibitem_keys = []
        final_keys = aux_citation_keys
        source = "tex_fallback"

    final_key_set = set(final_keys)
    aux_key_set = set(aux_citation_keys)
    bbl_key_set = set(bbl_bibitem_keys)
    issues: list[dict[str, str]] = []

    if source == "aux+bbl":
        for key in sorted(aux_key_set - bbl_key_set):
            issues.append(_issue("FRS-AUX-NO-BBL", key, "warn", f"Citation key '{key}' appears in .aux but not in .bbl."))
        for key in sorted(bbl_key_set - bib_key_set):
            issues.append(_issue("FRS-MISSING-FROM-BIB", key, "error", f"Citation key '{key}' appears in .bbl but not in active .bib files."))

    for key in sorted(bib_key_set - final_key_set):
        issues.append(_issue("FRS-UNUSED-BIB", key, "info", f"Citation key '{key}' is present in .bib files but not in the final reference set."))

    return {
        "module": "final_reference_set",
        "version": "3.3",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "final_reference_count": len(final_keys),
        "active_bib_sources": sorted(active_bib_sources),
        "summary": {
            "aux_citation_keys": len(aux_citation_keys),
            "bbl_bibitem_keys": len(bbl_bibitem_keys),
            "bib_total_entries": len(bib_keys),
            "unused_bib_entries": len(bib_key_set - final_key_set),
            "aux_only_keys": len(aux_key_set - bbl_key_set) if source == "aux+bbl" else 0,
            "bbl_only_keys": len(bbl_key_set - aux_key_set) if source == "aux+bbl" else 0,
            "missing_from_bib": len(final_key_set - bib_key_set),
        },
        "final_keys": final_keys,
        "issues": issues,
    }


def write_final_reference_set_json(report: dict[str, object], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def write_final_reference_set_csv(report: dict[str, object], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["severity", "code", "key", "message"]
    issues = report.get("issues")
    rows = issues if isinstance(issues, list) else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            if isinstance(row, dict):
                writer.writerow({field: row.get(field, "") for field in fieldnames})
