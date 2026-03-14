# THESIS_REFERENCES

## Purpose
Ensure citation integrity and bibliography hygiene with deterministic checks.

## Scope
- `\cite{key}` to `.bib` cross-validation.
- Orphan bibliography detection.
- Duplicate title candidate detection.
- Citation order anomaly detection.

## Quickstart
1. Run checker:
   - `python scripts/skills/03-references/check_references.py --rules tsinghua`
2. Read report:
   - `scripts/skills/03-references/check_references-report.json`
3. Fix `error` findings first, then `warning` findings.

## Rules
- Missing citation key: `error`
- Orphan bib entry: `warning`
- Possible duplicate entry: `warning`
- Non-monotonic numeric citation order (when applicable): `info`

## Inputs And Outputs
- Input:
  - `thuthesis-example.tex`
  - discovered chapter files
  - `ref/refs.bib`
  - `ref/refs-import.bib`
- Output:
  - JSON report with summary/findings

## Troubleshooting
- Missing key appears but exists in bib:
  - check for typo, extra spaces, or capitalization mismatch
- Too many duplicate warnings:
  - tune duplicate heuristic threshold in script config
- No citations found:
  - verify parser can read all included chapter files

## Verification
- `python scripts/skills/03-references/check_references.py --help`
- `python scripts/skills/03-references/check_references.py --rules tsinghua`

## Related Guides
- `scripts/skills/THESIS_SKILLS_GUIDE.zh-CN.md`
- `scripts/skills/THESIS_SKILLS_GUIDE.en.md`
