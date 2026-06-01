# Reference Audit Ledger

## Module

`28-reference-audit-ledger/build_reference_audit_ledger.py`

## Purpose

Aggregate existing reference evidence into one spreadsheet-friendly CSV ledger. This module does not rerun reference checks, call external services, modify `.bib`, or classify external-not-found references as fake.

## Usage

```bash
python 28-reference-audit-ledger/build_reference_audit_ledger.py \
  --project-root thesis \
  --ruleset university-generic
```

## Output

- `reports/reference-audit-ledger.csv`

## Columns

```text
key,title,authors,year,venue,doi,scope,source_checked,status,issue,action_suggested
```

## Inputs

Reads whichever evidence files are present:

- active BibTeX files discovered by the ruleset
- `reports/citation-integrity-report.json`
- `reports/final-reference-set-report.json`
- `reports/external-verification-report.json`
- `reports/missing-doi-candidates.json`
- `reports/url-verification-report.json`
- `reports/hallucination-risk-report.json`

## Boundaries

- CSV aggregation only.
- No bibliography edits.
- No automatic DOI insertion.
- No URL replacement.
- No external lookup.
- Preserves source-specific statuses instead of collapsing advisory evidence into fake/reference judgments.
