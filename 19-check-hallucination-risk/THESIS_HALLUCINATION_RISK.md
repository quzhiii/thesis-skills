# Check Hallucination Risk

## Module

`19-check-hallucination-risk/check_hallucination_risk.py`

## Purpose

Score bibliography entries for hallucination risk using local metadata and
optional external verification evidence. Produce a per-entry risk label,
a JSON report, and a high-risk CSV suitable for manual review.

## Usage

```bash
python 19-check-hallucination-risk/check_hallucination_risk.py \
  --project-root examples/citation-hallucination-fabricated \
  --ruleset university-generic
```

## Output

- `reports/hallucination-risk-report.json`
- `reports/high-risk-references.csv`

## Risk Labels

| Label | Meaning |
|---|---|
| PASS | Multi-source match, metadata consistent |
| WARN | Entry exists but fields differ |
| REVIEW | Possible match but evidence is weak |
| HIGH_RISK | No credible match found in enabled databases |
| UNSUPPORTED | Chinese-language or non-standard entry that cannot be auto-verified |

## Exit Codes

- `0`: PASS, WARN, REVIEW, or UNSUPPORTED
- `1`: HIGH_RISK

## Boundaries

- No LLM usage.
- No automatic citation or bibliography rewriting.
- No live network calls; reads external-verification-report.json if present.
- UNSUPPORTED means "cannot be automatically judged," not "safe."
- HIGH_RISK means "manual verification strongly recommended," not "fake."
