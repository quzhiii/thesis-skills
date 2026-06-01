# Manual Anchor Checker

## Module

`26-check-manual-anchor/check_manual_anchor.py`

## Purpose

Scan final thesis LaTeX sources for manual `\addcontentsline` entries that may be missing a nearby preceding `\phantomsection` anchor. This helps catch TOC / LOF / LOT hyperlink jump risks before final PDF handoff.

## Usage

```bash
python 26-check-manual-anchor/check_manual_anchor.py \
  --project-root thesis \
  --ruleset university-generic
```

## Output

- `reports/manual-anchor-report.json`

## First-Wave Checks

- `\addcontentsline{toc}{...}{...}`
- `\addcontentsline{lof}{figure}{...}`
- `\addcontentsline{lot}{table}{...}`
- whether `\phantomsection` appears in the expected preceding region

## Exit Codes

- `0`: no missing-anchor risk found
- `1`: at least one manual contents line may be missing a preceding `\phantomsection`

## Boundaries

- No automatic anchor repair.
- No label, caption, numbering, figure, table, or `\ref{}` rewrite.
- Reports likely hyperlink-jump risk for manual review.
- Intended as a final-audit foundation that can later be aggregated into `reports/final-audit-report.json` and rendered in static HTML report surfaces.
