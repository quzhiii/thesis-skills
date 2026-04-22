# THESIS_REVIEW_DIFF

This workflow creates bounded review-package and triage artifacts from the current thesis state.

Use it to:

- capture a review-ready snapshot of source scope and report references
- build a prioritized review queue from existing findings
- cluster repeated issues into reviewer-friendly triage summaries

First-release boundary:

- this workflow does not rewrite source files
- it does not replace advisor judgement
- it does not promise semantic understanding of every possible review concern

Relationship to ingest/action:

- `03-latex-review-diff` is Stage A: snapshot, queue, triage
- `04-word-review-ingest` is Stage B: normalize feedback and split actions
