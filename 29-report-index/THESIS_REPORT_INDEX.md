# Report Index HTML

## Module

`29-report-index/build_report_index.py`

## Purpose

Generate a static local HTML index for report artifacts in `reports/`. This is a reading surface only: JSON and CSV files remain the source of truth.

## Usage

```bash
python 29-report-index/build_report_index.py \
  --project-root thesis
```

## Output

- `reports/index.html`

## Current Scope

- Links to known JSON / CSV report artifacts.
- Shows present / missing / unreadable counts.
- Shows small summaries for JSON reports when available.
- Shows CSV row count for `reference-audit-ledger.csv` when available.

## Boundaries

- Static HTML only.
- No frontend framework.
- No hosted backend.
- No source mutation.
- Does not replace raw JSON / CSV artifacts.
- Individual HTML detail pages can be added later after the source-of-truth artifacts stay stable.
