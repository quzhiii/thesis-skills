# THESIS_FIX_FINAL_CLEANUP

Use this fixer after `23-check-final-cleanup`.

```bash
python 23-fix-final-cleanup/fix_final_cleanup.py --project-root <latex-project> --report reports/final-cleanup-report.json --apply false
```

Safe bounded behavior:

- preview and apply removal of exact process markers such as `TODO`, `FIXME`, `???`, `draft`, `debug`
- preview and apply removal of exact LaTeX color markers such as `\textcolor{blue}`
- only findings with `review_required=False` and valid patch spans are eligible

Guardrails:

- `--apply false` keeps the fixer in preview mode (default)
- only low-risk exact marker removals are auto-applied
- ambiguous or context-dependent findings remain review-only
- this fixer does not perform semantic claim rewriting or citation changes
