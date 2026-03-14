# THESIS_RULES

## Purpose
Define a pluggable ruleset interface for all thesis skill checkers.

## V1 Scope
- Supported ruleset: `tsinghua`
- Future extension hook: `custom` template pack
- Non-goal in v1: full multi-school runtime adaptation

## Directory Layout
`scripts/skills/06-rules/rules/<ruleset>/`

Required files for each ruleset:
- `format.yaml`
- `citation.yaml`
- `structure.yaml`
- `language.yaml`

## Quickstart
1. Use default ruleset:
   - `--rules tsinghua`
2. Validate ruleset directory contains all required files.
3. Run each checker with the same ruleset key.

## Extension Contract
To add a school in future:
1. Copy template pack from `rules/custom/template/`.
2. Fill all required keys in four domain files.
3. Run checker `--rules <new-key>` and fix missing-key failures.

## Troubleshooting
- Unknown ruleset:
  - create `scripts/skills/06-rules/rules/<ruleset>/`
- Missing domain file:
  - add missing yaml file with required keys
- Checker refuses rules:
  - verify all required files are readable

## Related Guides
- `scripts/skills/THESIS_SKILLS_GUIDE.zh-CN.md`
- `scripts/skills/THESIS_SKILLS_GUIDE.en.md`
