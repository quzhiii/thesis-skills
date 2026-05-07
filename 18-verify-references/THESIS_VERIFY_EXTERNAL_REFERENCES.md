# Verify External References (Alpha)

## Module

`18-verify-references/verify_external_references.py`

## Purpose

Query CrossRef and OpenAlex for each bibliography entry and produce an
`external-verification-report.json` that enriches the local citation-integrity
report with external metadata evidence.

## Usage

```bash
python 18-verify-references/verify_external_references.py \
  --project-root examples/citation-integrity-clean \
  --ruleset university-generic
```

## Output

- `reports/external-verification-report.json`
- `reports/.external-cache/` (local JSON cache, safe to delete)

## Alpha Scope

- Providers: CrossRef, OpenAlex only.
- No readiness gate blocking.
- No hallucination-risk score.
- No automatic citation rewriting.
- Network failures degrade to `UNAVAILABLE`, never crash.
