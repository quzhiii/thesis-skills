# Claim-Citation HTML

## Module

`32-claim-citation-html/build_claim_citation_html.py`

## Purpose

Generate a bilingual static HTML reading surface for `reports/claim-citation-triage-report.json`. JSON remains the source of truth.

## Usage

```bash
python 32-claim-citation-html/build_claim_citation_html.py \
  --project-root thesis
```

## Output

- `reports/claim-citation-triage.html`

## Current Surface

- status and KPI summary
- P0 / P1 / P2 / P3 review groups
- issue-card style summaries with evidence, rationale, and suggested action
- citation-needed candidates
- uncited references
- cluster/risk/support signal browsing
- related report links across readiness / references / claim-citation / final-audit surfaces
- mobile-readable narrow-screen reading layout
- Chinese default with English switch

## Boundaries

- Static HTML only.
- No frontend framework.
- No source mutation.
- JSON / Markdown / CSV / CLI contracts remain unchanged.
- Does not replace `claim-citation-triage-report.json`, `.md`, or `.csv`.
