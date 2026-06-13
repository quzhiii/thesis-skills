# THESIS_FIX_MANUAL_ANCHOR

Use this fixer after `26-check-manual-anchor`.

```bash
python 26-fix-manual-anchor/fix_manual_anchor.py --project-root <latex-project> --report reports/manual-anchor-report.json --apply false
```

Safe bounded behavior:

- preview and apply insertion of `\phantomsection` immediately before flagged `\addcontentsline` entries
- only eligible when the finding has `review_required=False` and valid patch metadata

Guardrails:

- `--apply false` keeps the fixer in preview mode (default)
- only low-risk direct insertion cases are auto-applied
- ambiguous or context-dependent findings remain review-only
- this fixer does not perform semantic claim rewriting or citation changes
