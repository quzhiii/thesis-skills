# Final Audit HTML

## Module

`30-final-audit-html/build_final_audit_html.py`

## Purpose

Generate a Swiss-inspired static HTML reading surface for `reports/final-audit-report.json`. JSON remains the source of truth.

## Usage

```bash
python 30-final-audit-html/build_final_audit_html.py \
  --project-root thesis
```

## Output

- `reports/final-audit-report.html`

## Current Surface

- overall verdict hero
- KPI row
- dimension matrix
- blocking issues
- warnings
- next actions
- source artifact links

## Boundaries

- Static HTML only.
- No frontend framework.
- No hosted backend.
- No source mutation.
- Does not replace `final-audit-report.json`.
