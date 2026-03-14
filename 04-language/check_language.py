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


def chapter_files() -> list[Path]:
    return sorted((ROOT / "data").glob("chap*.tex"))


def is_latex_command_line(line: str) -> bool:
    s = line.strip()
    return s.startswith("\\")


def strip_latex_noise(line: str) -> str:
    s = re.sub(r"%.*$", "", line)
    s = re.sub(r"\\[A-Za-z@]+\*?(\[[^\]]*\])?(\{[^{}]*\})?", " ", s)
    s = re.sub(r"\$[^$]*\$", " ", s)
    s = re.sub(r"\{[^{}]*\}", " ", s)
    return s


def has_cjk_latin_spacing_issue(line: str) -> bool:
    s = strip_latex_noise(line)
    if not s.strip():
        return False
    # Ignore common citation-like keys and compact section tokens.
    s = re.sub(r"\bref\d+\b", " ", s, flags=re.I)
    s = re.sub(r"\b[A-Z]{1,2}\d{1,3}\b", " ", s)
    # Flag only meaningful adjacent CJK and Latin words (>=2 letters) with lowercase letters.
    # This skips compact all-caps acronyms like DRG/DID that are commonly written inline in Chinese text.
    latin_word = r"(?=[A-Za-z]*[a-z])[A-Za-z]{2,}"
    return bool(
        re.search(r"[\u4e00-\u9fff]" + latin_word, s)
        or re.search(latin_word + r"[\u4e00-\u9fff]", s)
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Check language/punctuation formatting")
    ap.add_argument("--rules", default="tsinghua", help="ruleset name")
    ap.add_argument(
        "--report",
        default=str(Path(__file__).with_name("check_language-report.json")),
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
        files = chapter_files()

        for f in files:
            lines = f.read_text(encoding="utf-8", errors="ignore").splitlines()
            rel = str(f.relative_to(ROOT)).replace("\\", "/")
            for i, line in enumerate(lines, start=1):
                if is_latex_command_line(line):
                    continue

                if re.search(r"[。]{2,}|[，,]{2,}|[；;]{2,}|[：:]{2,}", line):
                    findings.append(
                        Finding(
                            severity="error",
                            code="LANG_REPEAT_PUNC",
                            message="Repeated punctuation detected",
                            file=rel,
                            line=i,
                            suggestion="Replace repeated punctuation with one valid punctuation mark",
                        )
                    )

                if ('"' in line or "'" in line) and (
                    "“" in line or "”" in line or "‘" in line or "’" in line
                ):
                    findings.append(
                        Finding(
                            severity="warning",
                            code="LANG_MIXED_QUOTES",
                            message="Mixed quote styles detected in one line",
                            file=rel,
                            line=i,
                            suggestion="Use one quote style consistently in Chinese context",
                        )
                    )

                if has_cjk_latin_spacing_issue(line):
                    findings.append(
                        Finding(
                            severity="warning",
                            code="LANG_CJK_LATIN_SPACING",
                            message="Possible missing spacing between CJK and Latin tokens",
                            file=rel,
                            line=i,
                            suggestion="Add a space between Chinese and English tokens where appropriate",
                        )
                    )

                for weak in ["本文将", "众所周知", "不难看出"]:
                    if weak in line:
                        findings.append(
                            Finding(
                                severity="info",
                                code="LANG_WEAK_PHRASE",
                                message=f"Weak academic phrase detected: {weak}",
                                file=rel,
                                line=i,
                                suggestion="Consider replacing with precise academic wording",
                            )
                        )

        errors = sum(1 for f in findings if f.severity == "error")
        warnings = sum(1 for f in findings if f.severity == "warning")
        infos = sum(1 for f in findings if f.severity == "info")

        report = {
            "summary": {
                "checker": "check_language",
                "ruleset": args.rules,
                "files_scanned": len(files),
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
