"""check_bib_quality.py — Stdlib-only bibliography quality checker.

Validates a .bib file exported from Zotero / EndNote before it enters the thesis
pipeline.  Checks:
  - Required fields per entry type (article / book / inproceedings / misc)
  - Presence of `langid` on every entry (required for GB7714-2015 / ThuThesis)
  - DOI format sanity (must start with 10.<4+ digits>/)
  - Cross-validation: keys cited in .tex files must exist in the .bib

Exit codes (consistent with other thesis-6-skills checkers):
  0  — all checks pass
  1  — quality findings (warnings / errors present)
  2  — config / input-file error
  3  — runtime failure
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(
    os.environ.get("THESIS_PROJECT_ROOT", str(Path(__file__).resolve().parents[2]))
).resolve()

# ---------------------------------------------------------------------------
# Required fields per entry type (minimum viable for GB7714-2015)
# ---------------------------------------------------------------------------
REQUIRED_FIELDS: dict[str, list[str]] = {
    "article":       ["author", "title", "journal", "year"],
    "book":          ["author", "title", "publisher", "year"],
    "inproceedings": ["author", "title", "booktitle", "year"],
    "incollection":  ["author", "title", "booktitle", "publisher", "year"],
    "phdthesis":     ["author", "title", "school", "year"],
    "mastersthesis": ["author", "title", "school", "year"],
    "techreport":    ["author", "title", "institution", "year"],
    "misc":          ["author", "title", "year"],
}


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------
@dataclass
class Finding:
    severity: str    # "error" | "warning" | "info"
    code: str
    message: str
    file: str
    line: int
    suggestion: str

    def as_dict(self) -> dict[str, object]:
        return {
            "status": "FAIL",
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "file": self.file,
            "line": self.line,
            "suggestion": self.suggestion,
        }


# ---------------------------------------------------------------------------
# .bib parsing (stdlib regex, no bibtexparser)
# ---------------------------------------------------------------------------
def _field_value(body: str, field: str) -> str:
    """Extract the value of a single field from a bib entry body."""
    # Handles: field = {value}, field = "value", field = number
    pattern = re.compile(
        rf'\b{re.escape(field)}\s*=\s*(?:\{{([^{{}}]*(?:\{{[^{{}}]*\}}[^{{}}]*)*)\}}|"([^"]*)"|(\d+))',
        re.IGNORECASE | re.DOTALL,
    )
    m = pattern.search(body)
    if not m:
        return ""
    return (m.group(1) or m.group(2) or m.group(3) or "").strip()


def _read_bib_text(path: Path) -> str:
    """Read a .bib file, trying UTF-8 first then GBK as fallback."""
    for enc in ("utf-8-sig", "utf-8", "gbk", "gb2312", "latin-1"):
        try:
            return path.read_text(encoding=enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def parse_bib_file(path: Path) -> list[dict[str, str]]:
    """Return list of entry dicts with keys: ENTRYTYPE, ID, and all fields."""
    text = _read_bib_text(path)
    entries: list[dict[str, str]] = []

    # Match top-level @TYPE{KEY, ...body...}  (non-nested braces for the outer block)
    # We walk char-by-char to handle nested braces correctly.
    i = 0
    while i < len(text):
        m = re.search(r"@(\w+)\s*\{", text[i:])
        if not m:
            break
        start = i + m.start()
        entry_type = m.group(1).lower()
        brace_start = i + m.end() - 1  # position of opening {

        # Walk braces to find matching close
        depth = 0
        j = brace_start
        while j < len(text):
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        body = text[brace_start + 1 : j]  # content inside outer braces

        if entry_type not in ("comment", "string", "preamble"):
            # First token before first comma is the cite key
            key_m = re.match(r"\s*([^,\s]+)", body)
            if key_m:
                key = key_m.group(1).strip()
                entry: dict[str, str] = {"ENTRYTYPE": entry_type, "ID": key, "_body": body}
                entries.append(entry)

        i = j + 1

    return entries


def get_entry_fields(entry: dict[str, str]) -> dict[str, str]:
    """Extract all field=value pairs from the entry body."""
    body = entry.get("_body", "")
    # Skip the cite key (first token)
    comma_pos = body.find(",")
    if comma_pos == -1:
        return {}
    body_after_key = body[comma_pos + 1 :]
    # Find all field names
    field_pattern = re.compile(
        r"(\w+)\s*=\s*(?:\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}|\"([^\"]*)\"|(\d+))",
        re.IGNORECASE | re.DOTALL,
    )
    fields: dict[str, str] = {}
    for fm in field_pattern.finditer(body_after_key):
        fname = fm.group(1).lower()
        fval = (fm.group(2) or fm.group(3) or fm.group(4) or "").strip()
        fields[fname] = fval
    return fields


# ---------------------------------------------------------------------------
# .tex citation extraction (reused pattern from check_references.py)
# ---------------------------------------------------------------------------
def discover_tex_files(main_tex: Path) -> list[Path]:
    seen: set[Path] = set()
    out: list[Path] = []

    def walk(path: Path) -> None:
        if path in seen or not path.exists():
            return
        seen.add(path)
        out.append(path)
        text = path.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r"\\input\{([^}]+)\}", text):
            target = m.group(1)
            if not target.endswith(".tex"):
                target += ".tex"
            walk((path.parent / target).resolve())

    walk(main_tex.resolve())
    return out


def extract_cited_keys(tex_files: list[Path]) -> set[str]:
    pattern = re.compile(r"\\cite[a-zA-Z*]*\s*(?:\[[^\]]*\]\s*)?\{([^}]+)\}")
    keys: set[str] = set()
    for tex in tex_files:
        text = tex.read_text(encoding="utf-8", errors="ignore")
        for m in pattern.finditer(text):
            for k in [x.strip() for x in m.group(1).split(",") if x.strip()]:
                keys.add(k)
    return keys


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------
def check_entries(
    entries: list[dict[str, str]],
    bib_path: Path,
    tex_cited_keys: set[str] | None,
    findings: list[Finding],
) -> None:
    bib_rel = str(bib_path)
    bib_keys: set[str] = set()

    for entry in entries:
        key = entry["ID"]
        etype = entry["ENTRYTYPE"]
        bib_keys.add(key)
        fields = get_entry_fields(entry)

        # 1. Required fields
        for req in REQUIRED_FIELDS.get(etype, []):
            if not fields.get(req, "").strip():
                findings.append(
                    Finding(
                        severity="error",
                        code="BIB_MISSING_FIELD",
                        message=f"{key} (@{etype}): missing required field '{req}'",
                        file=bib_rel,
                        line=0,
                        suggestion=f"Add '{req} = {{...}}' to the entry in your Zotero library and re-export",
                    )
                )

        # 2. langid (required for GB7714-2015 Chinese/English distinction)
        if not fields.get("langid", "").strip():
            findings.append(
                Finding(
                    severity="warning",
                    code="BIB_MISSING_LANGID",
                    message=f"{key}: missing 'langid' field",
                    file=bib_rel,
                    line=0,
                    suggestion="Add 'langid = {chinese}' or 'langid = {english}' to the entry",
                )
            )

        # 3. DOI format
        doi = fields.get("doi", "").strip()
        if doi and not re.match(r"^10\.\d{4,}/", doi):
            findings.append(
                Finding(
                    severity="warning",
                    code="BIB_MALFORMED_DOI",
                    message=f"{key}: DOI does not match pattern '10.XXXX/...': {doi!r}",
                    file=bib_rel,
                    line=0,
                    suggestion="Verify and correct the DOI value in Zotero, then re-export",
                )
            )

    # 4. Cross-validate: tex cites keys not in bib
    if tex_cited_keys is not None:
        for missing in sorted(tex_cited_keys - bib_keys):
            findings.append(
                Finding(
                    severity="error",
                    code="BIB_KEY_NOT_IN_FILE",
                    message=f"Tex cites key '{missing}' which is absent from {bib_rel}",
                    file=bib_rel,
                    line=0,
                    suggestion="Add this entry to Zotero with the matching cite key, or fix the \\cite{} command",
                )
            )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description="Bib quality check for Zotero/EndNote exports")
    ap.add_argument(
        "--bib",
        default="ref/refs-import.bib",
        help="Path to .bib file relative to THESIS_PROJECT_ROOT (default: ref/refs-import.bib)",
    )
    ap.add_argument(
        "--main",
        default="thuthesis-example.tex",
        help="Main .tex file relative to THESIS_PROJECT_ROOT — used for cross-validation",
    )
    ap.add_argument(
        "--skip-tex-check",
        action="store_true",
        help="Skip cross-validation of cite keys against .tex files",
    )
    ap.add_argument(
        "--report",
        default=str(Path(__file__).with_name("check_bib_quality-report.json")),
        help="Path for the JSON report output",
    )
    args = ap.parse_args()

    bib_path = (ROOT / args.bib).resolve()
    if not bib_path.exists():
        print(f"bib file not found: {bib_path}", file=sys.stderr)
        return 2

    findings: list[Finding] = []

    try:
        # Parse bib
        entries = parse_bib_file(bib_path)
        if not entries:
            print(f"no entries found in {bib_path}", file=sys.stderr)
            return 2

        # Optionally load tex cited keys
        tex_cited_keys: set[str] | None = None
        if not args.skip_tex_check:
            main_tex = (ROOT / args.main).resolve()
            if main_tex.exists():
                tex_files = discover_tex_files(main_tex)
                tex_cited_keys = extract_cited_keys(tex_files)
            else:
                print(
                    f"[warn] main tex not found ({main_tex}); skipping tex cross-check",
                    file=sys.stderr,
                )

        check_entries(entries, bib_path, tex_cited_keys, findings)

        errors = sum(1 for f in findings if f.severity == "error")
        warnings = sum(1 for f in findings if f.severity == "warning")
        infos = sum(1 for f in findings if f.severity == "info")

        report = {
            "summary": {
                "checker": "check_bib_quality",
                "bib_file": str(bib_path),
                "entries_checked": len(entries),
                "errors": errors,
                "warnings": warnings,
                "infos": infos,
                "status": "FAIL" if errors else "PASS",
            },
            "findings": [f.as_dict() for f in findings],
        }
        Path(args.report).write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"written report: {args.report}")
        print(
            f"summary: {len(entries)} entries | errors={errors} warnings={warnings} infos={infos}"
        )
        if errors:
            print("STATUS: FAIL")
        else:
            print("STATUS: PASS")
        return 1 if (errors or warnings) else 0

    except FileNotFoundError as e:
        print(f"input missing: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"runtime failure: {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
