# THESIS_FIX_FORMAT_STRUCTURE

Use this fixer after `12-check-format`.

```bash
python 22-fix-format-structure/fix_format_structure.py --project-root <latex-project> --report <report.json> --apply false
```

Safe behavior:

- add `\centering` to flagged figure blocks
- remove orphan labels
