# Custom Rules Template

This directory is a placeholder scaffold for future non-Tsinghua rulesets.

## How to use
1. Copy `template/` to a new ruleset directory name, for example:
   - `scripts/skills/06-rules/rules/my-university/`
2. Fill all required fields in:
   - `format.yaml`
   - `citation.yaml`
   - `structure.yaml`
   - `language.yaml`
3. Run any checker with `--rules my-university`.

## Validation Checklist
- All four yaml files exist.
- Required domain keys exist.
- Checker starts without ruleset errors.
