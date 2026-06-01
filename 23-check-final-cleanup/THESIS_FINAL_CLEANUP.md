# Final Cleanup Checker

## Module

`23-check-final-cleanup/check_final_cleanup.py`

## Purpose

Scan final thesis LaTeX sources for process residue that should not remain before submission. The checker is deterministic and report-first: it writes findings with file, line, evidence, and suggested action, but it never deletes or rewrites source content.

## Usage

```bash
python 23-check-final-cleanup/check_final_cleanup.py \
  --project-root thesis \
  --ruleset university-generic
```

## Output

- `reports/final-cleanup-report.json`

## Scanned Markers

- `TODO`
- `FIXME`
- `待修改`
- `待核查`
- `见截图`
- `这里再改`
- `临时`
- `占位`
- `???`
- `\textcolor{blue}`
- `\color{blue}`
- `draft`
- `debug`

## Exit Codes

- `0`: no cleanup residue found
- `1`: at least one cleanup residue finding exists

## Boundaries

- No automatic deletion.
- No source rewriting.
- No broad prose editing.
- Scans project LaTeX source files discovered from the active ruleset.
- Intended as a final-audit foundation that can later be aggregated into `reports/final-audit-report.json` and rendered in static HTML report surfaces.
