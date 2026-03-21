# THESIS_FIX_REFERENCES

Use this fixer after `10-check-references` produced a report.

```bash
python 20-fix-references/fix_references.py --project-root <latex-project> --report <report.json> --apply false
```

Safe behavior:

- generate placeholder imported entries for missing citation keys
- never rewrite research content
