# THESIS_CHECK_LANGUAGE_DEEP

Run the report-only deep language checker introduced in `v0.5.1`.

```bash
python 14-check-language-deep/check_language_deep.py --project-root <latex-project> --ruleset <ruleset>
```

This module is separate from `11-check-language` on purpose:

- `11-check-language` stays deterministic and line-level
- `14-check-language-deep` adds sentence-aware and cross-file review findings
- no source files are modified by the deep checker

Launch categories in Phase 2:

- `connector_misuse`
- `collocation_misuse`
- `terminology_consistency`
- `acronym_first_use`

Deep findings include these extra fields when present:

- `span`
- `evidence`
- `suggestions`
- `confidence`
- `review_required`
- `category`

Recommended use:

- run it after the basic checker
- review findings manually before deciding on edits
- keep deep review separate from safe auto-fix
