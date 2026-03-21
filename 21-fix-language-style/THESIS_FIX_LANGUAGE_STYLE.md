# THESIS_FIX_LANGUAGE_STYLE

Use this fixer after `11-check-language`.

```bash
python 21-fix-language-style/fix_language_style.py --project-root <latex-project> --report <report.json> --apply false
```

Safe behavior:

- insert CJK/Latin spacing for flagged lines
- collapse repeated punctuation
