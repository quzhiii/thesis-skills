# THESIS_CONTENT

## Purpose
Support thesis writing quality at content level: structure completeness, abstract readiness, keyword sanity, and symbol/abbreviation collection.

## Scope
- Structural checks for chapter flow and required sections.
- Abstract and keyword readiness checklist.
- Symbol extraction through `scan_symbols.py`.
- Non-destructive first: report mode before patch mode.

## Quickstart
1. Run symbol scan in report mode:
   - `python scripts/skills/02-content/scan_symbols.py --mode report`
2. Review suggested items and conflicts.
3. Optionally generate patch preview:
   - `python scripts/skills/02-content/scan_symbols.py --mode patch --apply false`
4. If accepted, apply:
   - `python scripts/skills/02-content/scan_symbols.py --mode patch --apply true`

## Content Checklist
- Chapter logic present: problem -> method -> result -> discussion -> conclusion.
- Abstract has objective, method, result, conclusion (both Chinese and English).
- Keywords count <= 5 for each language.
- Acknowledgements, appendices, resume/comments/resolution status aligned with degree requirements.

## Symbol/Acronym Workflow
1. Discover candidates from `data/chap*.tex`.
2. Deduplicate by canonical token.
3. Detect conflicting definitions and mark for manual decision.
4. Produce report JSON and optional denotation patch output.

## Inputs And Outputs
- Input:
  - `data/chap*.tex`
  - `data/denotation.tex`
- Output:
  - `scripts/skills/02-content/symbols-report.json`
  - optional updated `data/denotation.tex` in patch mode

## Troubleshooting
- Too many false positives:
  - add ignore tokens list in rules config
- Same acronym with different meanings:
  - keep conflict unresolved in report and resolve manually
- Broken denotation format after patch:
  - restore snapshot and re-run in report mode only

## Verification
- `python scripts/skills/02-content/scan_symbols.py --help`
- `python scripts/skills/02-content/scan_symbols.py --mode report`

## Related Guides
- `scripts/skills/THESIS_SKILLS_GUIDE.zh-CN.md`
- `scripts/skills/THESIS_SKILLS_GUIDE.en.md`
