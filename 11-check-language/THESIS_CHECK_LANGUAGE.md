# THESIS_CHECK_LANGUAGE

Run the deterministic language checker for the `v0.5.0` basic language foundation.

```bash
python 11-check-language/check_language.py --project-root <latex-project> --ruleset <ruleset>
```

It reads `90-rules/packs/<ruleset>/rules.yaml` and applies rule objects under `language.<rule>`.

Phase 1 rule families:

- `cjk_latin_spacing`
- `repeated_punctuation`
- `mixed_quote_style`
- `weak_phrases`
- `bracket_mismatch`
- `quote_mismatch`
- `booktitle_mixed_style`
- `unit_spacing`
- `ellipsis_style`
- `dash_style`
- `zh_en_symbol_spacing`
- `number_range_style`
- `enum_punctuation_style`
- `connector_blacklist_simple`
- `fullwidth_halfwidth_mix`

Each rule can declare:

- `enabled`
- `severity`
- `autofix_safe`
- `patterns` when the rule needs literal phrase matching

This module stays deterministic and report-oriented. Deep review-only language analysis is planned for a later phase and is not part of `11-check-language`.
