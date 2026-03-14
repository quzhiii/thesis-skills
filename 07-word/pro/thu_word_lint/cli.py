from __future__ import annotations

import argparse
import json
from pathlib import Path

from .linter import lint_doc
from .planner import build_fix_plan
from .rules_loader import load_rules


def cmd_lint(args: argparse.Namespace) -> int:
    doc = Path(args.doc).resolve()
    rules = Path(args.rules).resolve()
    out = Path(args.out).resolve()

    if not doc.exists():
        print(f"doc not found: {doc}")
        return 2
    if not rules.exists():
        print(f"rules not found: {rules}")
        return 2

    cfg = load_rules(rules)
    report = lint_doc(doc_path=doc, ruleset_name=str(cfg.get("ruleset", "thu_v1")))
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[ok] report: {out}")
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    report_path = Path(args.report).resolve()
    out = Path(args.out).resolve()
    if not report_path.exists():
        print(f"report not found: {report_path}")
        return 2

    report = json.loads(report_path.read_text(encoding="utf-8"))
    plan = build_fix_plan(report)
    out.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[ok] plan: {out}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="THU Word lint/planner CLI (skeleton)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_lint = sub.add_parser("lint", help="Generate report.json from docx and rules")
    p_lint.add_argument("--doc", required=True, help="Path to source docx")
    p_lint.add_argument("--rules", required=True, help="Path to rules file")
    p_lint.add_argument("--out", required=True, help="Output report path")
    p_lint.set_defaults(func=cmd_lint)

    p_plan = sub.add_parser("plan", help="Generate fix_plan.json from report.json")
    p_plan.add_argument("--report", required=True, help="Path to report.json")
    p_plan.add_argument("--out", required=True, help="Output fix plan path")
    p_plan.set_defaults(func=cmd_plan)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
