from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict
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


def parse_bib_entries(path: Path) -> tuple[set[str], dict[str, str]]:
    if not path.exists():
        return set(), {}
    text = path.read_text(encoding="utf-8", errors="ignore")
    keys = set(re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,", text))
    titles: dict[str, str] = {}
    for m in re.finditer(r"@\w+\s*\{\s*([^,\s]+)\s*,(.*?)\n\}\s*", text, re.S):
        key = m.group(1)
        body = m.group(2)
        t = re.search(r"title\s*=\s*\{(.*?)\}", body, re.S)
        titles[key] = t.group(1).strip().lower() if t else ""
    return keys, titles


def extract_citations(path: Path) -> list[tuple[str, int]]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    findings: list[tuple[str, int]] = []
    pattern = re.compile(r"\\cite[a-zA-Z*]*\s*(?:\[[^\]]*\]\s*)?\{([^}]+)\}")
    for m in pattern.finditer(text):
        line = text.count("\n", 0, m.start()) + 1
        for key in [k.strip() for k in m.group(1).split(",") if k.strip()]:
            findings.append((key, line))
    return findings


def detect_order_anomaly(citation_order: list[str]) -> bool:
    nums: list[int] = []
    for key in citation_order:
        m = re.fullmatch(r"ref(\d+)", key)
        if m:
            nums.append(int(m.group(1)))
    if len(nums) < 2:
        return False
    return any(b < a for a, b in zip(nums, nums[1:]))


def main() -> int:
    ap = argparse.ArgumentParser(description="Check citation-bibliography integrity")
    ap.add_argument(
        "--rules",
        default="tsinghua",
        help="ruleset name under scripts/skills/06-rules/rules",
    )
    ap.add_argument("--main", default="thuthesis-example.tex", help="main tex file")
    ap.add_argument(
        "--report",
        default=str(Path(__file__).with_name("check_references-report.json")),
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
        main_tex = (ROOT / args.main).resolve()
        tex_files = discover_tex_files(main_tex)

        bib_keys: set[str] = set()
        title_to_keys: defaultdict[str, list[str]] = defaultdict(list)
        for bib_rel in ["ref/refs.bib", "ref/refs-import.bib"]:
            keys, titles = parse_bib_entries(ROOT / bib_rel)
            bib_keys |= keys
            for k, t in titles.items():
                if t:
                    title_to_keys[t].append(k)

        cited_keys: set[str] = set()
        citation_order: list[str] = []
        for tex in tex_files:
            for key, line in extract_citations(tex):
                cited_keys.add(key)
                citation_order.append(key)
                if key not in bib_keys:
                    findings.append(
                        Finding(
                            severity="error",
                            code="REF_MISSING_KEY",
                            message=f"Citation key not found in bibliography: {key}",
                            file=str(tex.relative_to(ROOT)).replace("\\", "/"),
                            line=line,
                            suggestion="Add the missing key to ref/refs.bib or fix typo in cite command",
                        )
                    )

        for orphan in sorted(bib_keys - cited_keys):
            findings.append(
                Finding(
                    severity="warning",
                    code="REF_ORPHAN_BIB",
                    message=f"Bibliography key not cited in thesis: {orphan}",
                    file="ref/refs.bib|ref/refs-import.bib",
                    line=0,
                    suggestion="Remove unused entry or cite it where relevant",
                )
            )

        for title, keys in title_to_keys.items():
            if len(keys) > 1:
                findings.append(
                    Finding(
                        severity="warning",
                        code="REF_DUPLICATE_TITLE",
                        message=f"Possible duplicate bibliography entries: {','.join(sorted(keys))}",
                        file="ref/refs.bib|ref/refs-import.bib",
                        line=0,
                        suggestion="Confirm if duplicates are intentional; merge if not",
                    )
                )

        if detect_order_anomaly(citation_order):
            findings.append(
                Finding(
                    severity="info",
                    code="REF_ORDER_ANOMALY",
                    message="Potential non-monotonic numeric citation order detected",
                    file="thesis",
                    line=0,
                    suggestion="Review citation ordering if numeric sequence is required",
                )
            )

        errors = sum(1 for f in findings if f.severity == "error")
        warnings = sum(1 for f in findings if f.severity == "warning")
        infos = sum(1 for f in findings if f.severity == "info")

        report = {
            "summary": {
                "checker": "check_references",
                "ruleset": args.rules,
                "files_scanned": len(tex_files),
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
        return 1 if errors else 0
    except FileNotFoundError as e:
        print(f"input missing: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"runtime failure: {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
