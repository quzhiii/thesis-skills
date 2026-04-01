# THESIS_FIX_LANGUAGE_DEEP

Generate patch previews from `14-check-language-deep` findings, or selectively apply them when explicitly requested.

```bash
python 24-fix-language-deep/fix_language_deep.py --project-root <latex-project> --report <report.json> --apply false
```

Default behavior in `v0.5.2`:

- generate patch preview only
- validate `old_text` before apply
- reject overlapping patches
- keep `review_required=true` findings out of apply unless explicitly overridden

Useful flags:

- `--apply true`
- `--include-review-required true`
- `--issue-codes LANG_DEEP_CONNECTOR_MISUSE,LANG_DEEP_TERM_INCONSISTENT`

This module stays separate from `21-fix-language-style`:

- `21-fix-language-style` remains low-risk safe fix
- `24-fix-language-deep` is review-first patch preview plus selective apply
