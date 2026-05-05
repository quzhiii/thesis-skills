# Citation Integrity Broken Demo

This demo intentionally contains local citation-integrity problems:

- `missing2024` is cited in `main.tex` but absent from `ref/refs.bib`.
- `duplicate2024` appears twice with conflicting metadata.
- `missingdoi2025` has no DOI.
- `badyear` has a non-numeric year and malformed DOI.
- `unusedbook` is present in the bibliography but not cited.
- `main.log` includes an undefined citation warning.

Run:

```bash
python 10-check-references/check_references.py \
  --project-root examples/citation-integrity-broken \
  --ruleset university-generic
```

Expected artifacts:

- `reports/check_references-report.json`
- `reports/citation-integrity-report.json`

V1.1 is local-only. It does not verify whether references exist in external databases, does not detect hallucinated references, and does not automatically edit citations or bibliography entries.
