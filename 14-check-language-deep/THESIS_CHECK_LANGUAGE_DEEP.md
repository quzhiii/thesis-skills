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
- `original_text`
- `rationale`
- `risk_level`

The report also carries:

- `coverage`: what prose was screened and which LaTeX-side constructs were masked
- `uncovered_risks`: what the checker intentionally does not over-claim
- `stratified_counts`: grouped counts for deep-language vs consistency-style findings
- `review_queue`: a prioritized manual-review queue sorted for human triage
- `review_clusters`: deduplicated issue groups with `recommended_action`, `rewrite_hint`, and `review_focus`
- `summary.review_digest`: compact counts for priority mix and deduplicated action items

The review-oriented payload is layered on purpose:

- `findings` stays as the raw traceable truth
- `review_queue` answers “what should I review first?”
- `review_clusters` answers “which repeated issue types can I fix together?”

Recommended use:

- run it after the basic checker
- review findings manually before deciding on edits
- keep deep review separate from safe auto-fix
- treat `0 findings` as “no configured issues detected in checked prose”, not as final thesis sign-off
