# Changelog

All notable changes to Thesis Skills are summarized here.

## v1.0.0

- Stabilized the public README story around citation sync, deterministic checks, safe fixes, readiness gate, and defense preparation.
- Added a runnable minimal LaTeX demo under `examples/minimal-latex-project` for `--skip-compile` quickstart validation.
- Hardened rule-pack documentation and module references for public use.
- Documented the boundary that Thesis Skills checks and prepares thesis workflows; it does not generate thesis content.

## v1.1.0

- Added the local-first Citation Integrity Engine under `10-check-references`.
- Added `reports/citation-integrity-report.json` alongside the compatibility `check_references-report.json`.
- Added local checks for missing cited keys, unused bibliography entries, duplicate key conflicts, BibTeX field warnings, DOI/year shape warnings, and local undefined-citation log evidence.
- Integrated Citation Integrity evidence into the References dimension of the readiness gate.

## v1.2.0

- Added Markdown and CSV Citation Integrity outputs for review-friendly service reports.
- Added a clean Citation Integrity demo alongside the intentionally broken demo.

## v0.8.x

- Added defense preparation workflows for outlines, figure inventories, candidate visuals, and talk notes.
- Improved static showcase and rule-pack scorecard/lint/completeness tooling.

## v0.7.x

- Added the `PASS / WARN / BLOCK` readiness gate.
- Hardened review-summary and feedback-ingest workflows.

## v0.6.0

- Added review-friendly LaTeX-to-Word export.
- Added compile-log parsing and review-loop workflows.

## v0.5.x

- Added deterministic and deep language review.
- Added selective patch previews for safer fixes.

## v0.4.0

- Added EndNote XML/RIS/BibTeX import.
- Added DOI deduplication and stable `refNNN` reference IDs.

## v0.3.0

- Restructured the public repository.
- Added bilingual README coverage, CI, and Zotero-first bibliography workflow.
