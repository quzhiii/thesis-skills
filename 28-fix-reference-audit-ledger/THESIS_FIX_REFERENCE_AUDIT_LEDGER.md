# THESIS_FIX_REFERENCE_AUDIT_LEDGER

Use this fixer after `28-reference-audit-ledger`.

```bash
python 28-fix-reference-audit-ledger/fix_reference_audit_ledger.py --project-root <latex-project> --csv reports/reference-audit-ledger.csv --apply false
```

Safe bounded behavior:

- preview and apply removal of truly unused bibliography entries from .bib files
- only eligible when `is_unused_bib_entry=true`, `is_cited_in_tex=false`, and `is_final_reference=false`

Guardrails:

- `--apply false` keeps the fixer in preview mode (default)
- only truly unused entries are eligible for removal
- cited, final-scope, or advisory-only rows remain untouched
- this fixer does not insert or replace bibliography entries
