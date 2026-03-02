# THESIS_FORMAT

## Purpose
Provide a closed-loop format assurance flow: snapshot, compile, log check, and deterministic structure checks.

## Scope
- Keep and reuse existing compile loop:
  - `scripts/thesis_quality_loop.ps1`
- Add static checks through `check_structure.py`:
  - figure/table/equation structure
  - longtable continuation markers
  - `\ref` and `\label` cross-reference integrity
  - presence of list of figures/tables in main tex
  - dynamic chapter discovery (`data/chap*.tex`)

## Quickstart
1. Run compile loop:
   - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/thesis_quality_loop.ps1 -Action full -JobName thuthesis-example-skill-check`
2. Run structure checker:
   - `python scripts/skills/05-format/check_structure.py --rules tsinghua`
3. Fix `error` findings, re-run both steps.

## Dynamic Chapter Discovery
- Include: `data/chap*.tex`
- Exclude: non-tex files and template/backup artifacts
- No hardcoded chapter count

## Troubleshooting
- Compile succeeds but structure fails:
  - check missing `\label` or malformed `figure/table` blocks
- Structure checker reports unknown rule set:
  - confirm `scripts/skills/06-rules/rules/<name>/` exists
- Longtable continuation warnings:
  - verify `\endfirsthead`, `\endhead`, `\endfoot`, `\endlastfoot` exist

## Verification
- `python scripts/skills/05-format/check_structure.py --help`
- `python scripts/skills/05-format/check_structure.py --rules tsinghua`

## Related Guides
- `scripts/skills/THESIS_SKILLS_GUIDE.zh-CN.md`
- `scripts/skills/THESIS_SKILLS_GUIDE.en.md`
