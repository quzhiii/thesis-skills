from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(
    os.environ.get("THESIS_PROJECT_ROOT", str(Path(__file__).resolve().parents[3]))
).resolve()
RULES_ROOT = Path(
    os.environ.get(
        "THESIS_RULES_ROOT",
        str(ROOT / "scripts" / "skills" / "06-rules" / "rules"),
    )
).resolve()


@dataclass
class Finding:
    severity: str
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


def ensure_ruleset(ruleset: str) -> None:
    rdir = RULES_ROOT / ruleset
    required = ["format.yaml", "citation.yaml", "structure.yaml", "language.yaml"]
    if not rdir.exists():
        raise ValueError(f"ruleset not found: {ruleset}")
    missing = [name for name in required if not (rdir / name).exists()]
    if missing:
        raise ValueError(f"ruleset incomplete: {ruleset}, missing={','.join(missing)}")


def discover_chapters() -> list[Path]:
    files: list[Path] = []
    for p in sorted((ROOT / "data").glob("chap*.tex")):
        if p.name.endswith(".template_backup.tex"):
            continue
        if ".bak" in p.suffixes:
            continue
        if p.suffix != ".tex":
            continue
        files.append(p)
    return files


def line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def check_env_block(text: str, env: str) -> list[tuple[str, int, str]]:
    issues: list[tuple[str, int, str]] = []
    for m in re.finditer(
        r"\\begin\{" + re.escape(env) + r"\}(.*?)\\end\{" + re.escape(env) + r"\}",
        text,
        re.S,
    ):
        block = m.group(1)
        ln = line_of(text, m.start())
        if "\\caption" not in block:
            issues.append(("FMT_MISSING_CAPTION", ln, f"{env} missing \\caption"))
        if "\\label" not in block:
            issues.append(("FMT_MISSING_LABEL", ln, f"{env} missing \\label"))
        if env == "figure" and "\\centering" not in block:
            issues.append(("FMT_MISSING_CENTERING", ln, "figure missing \\centering"))
    return issues


def has_any_longtable_marker(block: str) -> bool:
    markers = ["\\endfirsthead", "\\endhead", "\\endfoot", "\\endlastfoot"]
    return any(marker in block for marker in markers)


def needs_longtable_continuation_check(block: str) -> bool:
    # Require full continuation marker set only when table explicitly indicates continuation
    # or when author already started using continuation markers.
    return ("续表" in block) or has_any_longtable_marker(block)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Check thesis structure and cross references"
    )
    ap.add_argument("--rules", default="tsinghua", help="ruleset name")
    ap.add_argument("--main", default="thuthesis-example.tex", help="main tex file")
    ap.add_argument(
        "--report",
        default=str(Path(__file__).with_name("check_structure-report.json")),
        help="report output path",
    )
    args = ap.parse_args()

    try:
        ensure_ruleset(args.rules)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 2

    findings: list[Finding] = []
    try:
        main_tex = ROOT / args.main
        main_text = main_tex.read_text(encoding="utf-8", errors="ignore")

        if "\\listoffigures" not in main_text:
            findings.append(
                Finding(
                    "warning",
                    "FMT_NO_LISTOFFIGURES",
                    "Main file missing \\listoffigures",
                    args.main,
                    1,
                    "Add \\listoffigures in front matter",
                )
            )
        if "\\listoftables" not in main_text:
            findings.append(
                Finding(
                    "warning",
                    "FMT_NO_LISTOFTABLES",
                    "Main file missing \\listoftables",
                    args.main,
                    1,
                    "Add \\listoftables in front matter",
                )
            )

        files = [main_tex] + discover_chapters()

        labels: dict[str, tuple[str, int]] = {}
        refs: list[tuple[str, str, int]] = []

        for f in files:
            text = f.read_text(encoding="utf-8", errors="ignore")
            rel = str(f.relative_to(ROOT)).replace("\\", "/")

            for code, ln, msg in check_env_block(text, "figure"):
                findings.append(
                    Finding("error", code, msg, rel, ln, "Add required figure elements")
                )
            for code, ln, msg in check_env_block(text, "table"):
                findings.append(
                    Finding("error", code, msg, rel, ln, "Add required table elements")
                )

            for m in re.finditer(
                r"\\begin\{longtable\}(.*?)\\end\{longtable\}", text, re.S
            ):
                block = m.group(1)
                ln = line_of(text, m.start())
                # Only enforce full marker set when longtable continuation markers are used.
                # This avoids noisy warnings for short longtables that do not define continued headers.
                if needs_longtable_continuation_check(block):
                    missing_markers: list[str] = []
                    for marker in [
                        "\\endfirsthead",
                        "\\endhead",
                        "\\endfoot",
                        "\\endlastfoot",
                    ]:
                        if marker not in block:
                            missing_markers.append(marker)
                    if missing_markers:
                        # Common longtable pattern: only \endhead + \endlastfoot provided.
                        # Treat this as acceptable for non-continued tables to avoid false alarms.
                        if set(missing_markers) == {"\\endfirsthead", "\\endfoot"}:
                            continue
                        findings.append(
                            Finding(
                                "warning",
                                "FMT_LONGTABLE_MARKER",
                                f"longtable missing markers: {', '.join(missing_markers)}",
                                rel,
                                ln,
                                "Add the full continuation marker set for longtable",
                            )
                        )

            for m in re.finditer(
                r"\\begin\{table\}(.*?)\\begin\{equation\}", text, re.S
            ):
                findings.append(
                    Finding(
                        "warning",
                        "FMT_EQUATION_TABLE_WRAPPER",
                        "equation appears wrapped by table environment",
                        rel,
                        line_of(text, m.start()),
                        "Use equation/aligned/gathered without table wrapper",
                    )
                )

            for m in re.finditer(r"\\label\{([^}]+)\}", text):
                label = m.group(1)
                labels[label] = (rel, line_of(text, m.start()))
            for m in re.finditer(r"\\(?:ref|eqref|autoref)\{([^}]+)\}", text):
                refs.append((m.group(1), rel, line_of(text, m.start())))

        used_labels = {r[0] for r in refs}
        for ref, rel, ln in refs:
            if ref not in labels:
                findings.append(
                    Finding(
                        "error",
                        "FMT_BROKEN_REF",
                        f"reference target not found: {ref}",
                        rel,
                        ln,
                        "Define matching \\label or fix ref key",
                    )
                )

        for label, (rel, ln) in labels.items():
            if label not in used_labels:
                findings.append(
                    Finding(
                        "warning",
                        "FMT_ORPHAN_LABEL",
                        f"label not referenced: {label}",
                        rel,
                        ln,
                        "Remove unused label or add corresponding ref",
                    )
                )

        errors = sum(1 for f in findings if f.severity == "error")
        warnings = sum(1 for f in findings if f.severity == "warning")
        infos = sum(1 for f in findings if f.severity == "info")

        report = {
            "summary": {
                "checker": "check_structure",
                "ruleset": args.rules,
                "files_scanned": len(files),
                "errors": errors,
                "warnings": warnings,
                "infos": infos,
                "status": "FAIL" if errors else "PASS",
                "discovered_chapters": [
                    str(p.relative_to(ROOT)).replace("\\", "/")
                    for p in discover_chapters()
                ],
            },
            "findings": [f.as_dict() for f in findings],
        }
        Path(args.report).write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"written report: {args.report}")
        return 1 if errors else 0
    except FileNotFoundError as e:
        print(f"input missing: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"runtime failure: {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
