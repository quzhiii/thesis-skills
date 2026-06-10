# Check Claim-Citation Support

## Module

`20-check-claim-citation/check_claim_citation.py`

## Purpose

Extract citation context from LaTeX source text, pair each `\cite{}` occurrence
with its surrounding claim sentence, and produce a structured triage report
flagging claim-citation pairs that may lack credible structural support.
All scoring is deterministic; no LLM is used. The report keeps backward-compatible
triage labels while also surfacing `support_review_label`,
`support_review_reason`, `support_signals`, `risk_signals`, `cluster_keys`,
`cluster_risk_summary`, `next_actions`, `citation_needed_candidates`, and
`uncited_references` as explicit human-review aids.

## Usage

```bash
python 20-check-claim-citation/check_claim_citation.py \
  --project-root examples/claim-citation-mixed \
  --ruleset university-generic
```

## Output

- `reports/claim-citation-triage-report.json`
- `reports/claim-citation-triage.md`
- `reports/claim-citation-triage.csv`

The JSON/Markdown report can carry review-enrichment fields such as
`support_review_label`, `support_review_reason`, `support_signals`,
`risk_signals`, `cluster_keys`, `cluster_risk_summary`, and `next_actions`.
It can also surface advisory `citation_needed_candidates` and
`uncited_references` for manual review.

## Triage Labels

| Label | Meaning |
|---|---|
| WELL_SUPPORTED | Cited reference PASS in V3.0, complete metadata, substantive context |
| SUPPORTED | Reference PASS/WARN in V3.0, minor risk signals |
| WEAK | Reference REVIEW in V3.0 or vague context or incomplete metadata |
| ORPHANED | Citation key not found in bibliography files |
| UNVERIFIABLE | Cited reference UNSUPPORTED in V3.0 (CJK, thesis type) |

## Exit Codes

- `0`: No orphaned claim-citation pairs
- `1`: At least one ORPHANED pair exists

## Boundaries

- No LLM usage.
- No semantic similarity between claim text and reference content.
- No automatic citation rewrite or bibliography insertion.
- Suggested actions are advisory review cues, not automatic fix instructions.
- No PubMed/DBLP/arXiv full-text retrieval.
- Reads hallucination-risk-report.json if present; treats missing it conservatively.
- ORPHANED means the citation key has no bib entry, not that the claim is wrong.
