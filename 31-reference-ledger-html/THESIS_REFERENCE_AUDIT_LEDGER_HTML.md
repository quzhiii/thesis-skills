# Reference Audit Ledger HTML

## Module

`31-reference-ledger-html/build_reference_audit_ledger_html.py`

## Purpose

Generate a bilingual static HTML reading surface for `reports/reference-audit-ledger.csv`. CSV remains the source of truth.

## Usage

```bash
python 31-reference-ledger-html/build_reference_audit_ledger_html.py \
  --project-root thesis
```

## Output

- `reports/reference-audit-ledger.html`

## Current Surface

- summary stats
- Final references only
- All bibliography entries
- Unused bibliography entries
- Evidence rows
- browse by scope
- related report links across readiness / references / claim-citation / final-audit surfaces
- full table
- Chinese default with English switch
- narrow-screen responsive reading layout

## Boundaries

- Static HTML only.
- No frontend framework.
- No source mutation.
- Does not replace `reference-audit-ledger.csv`.
