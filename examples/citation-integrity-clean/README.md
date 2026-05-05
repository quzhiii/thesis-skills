# Citation Integrity Clean Demo

This demo is a minimal local PASS case for Citation Integrity.

Run:

```bash
python 10-check-references/check_references.py \
  --project-root examples/citation-integrity-clean \
  --ruleset university-generic
```

Expected artifacts:

- `reports/check_references-report.json`
- `reports/citation-integrity-report.json`
- `reports/citation-integrity-report.md`
- `reports/citation-issues.csv`

V1.2 adds Markdown and CSV outputs for service-style review, but still remains local-only and report-first.
