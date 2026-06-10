# THESIS_FIX_STATISTICAL_CONSISTENCY

Use this fixer after `25-check-statistical-consistency`.

```bash
python 25-fix-statistical-consistency/fix_statistical_consistency.py --project-root <latex-project> --report reports/statistical-consistency-report.json --apply false
```

Safe bounded behavior:

- preview and apply normalization of non-dominant statistical notation variants when the dominant style is unambiguous
- only eligible when dominant variant has at least 3 occurrences and at least 2x the count of the next most common variant

Guardrails:

- `--apply false` keeps the fixer in preview mode (default)
- only findings with `review_required=False` are eligible for apply
- ambiguous or weak dominance cases remain review-only
- this fixer does not perform semantic claim rewriting or citation changes
