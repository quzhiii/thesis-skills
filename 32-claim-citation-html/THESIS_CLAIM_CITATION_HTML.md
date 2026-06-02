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
- citation-needed candidates
- uncited references
- triage-label grouped review cards
- cluster/risk/support signal browsing
- Chinese default with English switch

## Boundaries

- Static HTML only.
- No frontend framework.
- No source mutation.
- Does not replace `claim-citation-triage-report.json`, `.md`, or `.csv`.
