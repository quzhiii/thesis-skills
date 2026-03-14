from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime
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
class Candidate:
    token: str
    file: str
    line: int
    context: str
    conflict: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "token": self.token,
            "file": self.file,
            "line": self.line,
            "context": self.context,
            "conflict": self.conflict,
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
    return sorted((ROOT / "data").glob("chap*.tex"))


def existing_denotation_tokens(path: Path) -> set[str]:
    if not path.exists():
        return set()
    text = path.read_text(encoding="utf-8", errors="ignore")
    return set(re.findall(r"\\item\[([^\]]+)\]", text))


def extract_candidates(files: list[Path]) -> list[Candidate]:
    out: list[Candidate] = []
    seen_ctx: dict[str, str] = {}
    pattern = re.compile(r"(?<!\\)\b[A-Z][A-Z0-9-]{1,}\b")
    for f in files:
        rel = str(f.relative_to(ROOT)).replace("\\", "/")
        lines = f.read_text(encoding="utf-8", errors="ignore").splitlines()
        for i, line in enumerate(lines, start=1):
            if line.strip().startswith("%"):
                continue
            for m in pattern.finditer(line):
                tok = m.group(0)
                ctx = line.strip()[:200]
                conflict = tok in seen_ctx and seen_ctx[tok] != ctx
                if tok not in seen_ctx:
                    seen_ctx[tok] = ctx
                out.append(Candidate(tok, rel, i, ctx, conflict))
    return out


def dedupe(cands: list[Candidate]) -> list[Candidate]:
    by_token: dict[str, Candidate] = {}
    for c in cands:
        if c.token not in by_token:
            by_token[c.token] = c
        else:
            by_token[c.token].conflict = (
                by_token[c.token].conflict
                or c.conflict
                or (by_token[c.token].context != c.context)
            )
    return sorted(by_token.values(), key=lambda x: x.token)


def patch_denotation(
    deno_path: Path, new_tokens: list[str], apply: bool
) -> dict[str, object]:
    additions = [f"  \\item[{t}] TODO: define {t}" for t in new_tokens]
    if not additions:
        return {"patched": False, "added": 0, "backup": ""}

    text = (
        deno_path.read_text(encoding="utf-8", errors="ignore")
        if deno_path.exists()
        else "\\begin{denotation}[3cm]\n\\end{denotation}\n"
    )
    idx = text.rfind("\\end{denotation}")
    if idx == -1:
        raise RuntimeError("denotation block not found")
    patched = text[:idx] + "\n" + "\n".join(additions) + "\n" + text[idx:]

    backup = ""
    if apply:
        if deno_path.exists():
            backup = str(
                deno_path.with_suffix(
                    f".bak-{datetime.now().strftime('%Y%m%d-%H%M%S')}.tex"
                )
            )
            Path(backup).write_text(text, encoding="utf-8")
        deno_path.write_text(patched, encoding="utf-8")
    return {"patched": apply, "added": len(additions), "backup": backup}


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Scan symbols/acronyms and optionally patch denotation"
    )
    ap.add_argument("--rules", default="tsinghua", help="ruleset name")
    ap.add_argument("--mode", choices=["report", "patch"], default="report")
    ap.add_argument("--apply", choices=["true", "false"], default="false")
    ap.add_argument(
        "--report",
        default=str(Path(__file__).with_name("symbols-report.json")),
        help="report output path",
    )
    args = ap.parse_args()

    try:
        ensure_ruleset(args.rules)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 2

    try:
        files = discover_chapters()
        existing = existing_denotation_tokens(ROOT / "data" / "denotation.tex")
        deduped = dedupe(extract_candidates(files))
        fresh = [c.token for c in deduped if c.token not in existing]
        conflicts = [c.token for c in deduped if c.conflict]

        patch_result = {"patched": False, "added": 0, "backup": ""}
        if args.mode == "patch":
            patch_result = patch_denotation(
                ROOT / "data" / "denotation.tex", fresh, args.apply == "true"
            )

        report = {
            "summary": {
                "checker": "scan_symbols",
                "ruleset": args.rules,
                "files_scanned": len(files),
                "candidates": len(deduped),
                "new_tokens": len(fresh),
                "conflicts": len(conflicts),
                "status": "PASS",
                "mode": args.mode,
            },
            "new_tokens": fresh,
            "conflicts": conflicts,
            "patch": patch_result,
            "candidates": [c.as_dict() for c in deduped],
        }
        Path(args.report).write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"written report: {args.report}")
        return 0
    except FileNotFoundError as e:
        print(f"input missing: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"runtime failure: {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
