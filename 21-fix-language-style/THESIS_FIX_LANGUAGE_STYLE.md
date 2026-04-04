# THESIS_FIX_LANGUAGE_STYLE

Use this fixer after `11-check-language`.

```bash
python 21-fix-language-style/fix_language_style.py --project-root <latex-project> --report <report.json> --apply false
```

Safe `v0.5.0` behavior:

- insert CJK/Latin spacing
- collapse repeated punctuation
- normalize number-unit spacing
- normalize ellipsis style
- normalize fullwidth/halfwidth punctuation only in obvious same-script contexts

Guardrails:

- `--apply false` keeps the fixer in preview mode
- only low-risk language codes are auto-applied in Phase 1
- quote, bracket, book-title, connector, dash, and range findings remain review-only
- deep language patch preview is planned for a later phase and is not part of `21-fix-language-style`
