# Changelog

All notable changes to Thesis Skills are summarized here.

## v3.0.0

- Added deterministic hallucination risk scoring per bibliography entry based on local metadata and V2.0 external verification evidence.
- New CLI: `19-check-hallucination-risk/check_hallucination_risk.py` writes `reports/hallucination-risk-report.json` and `reports/high-risk-references.csv`.
- Risk labels: `PASS`, `WARN`, `REVIEW`, `HIGH_RISK`, `UNSUPPORTED`.
- Chinese-language references are marked `UNSUPPORTED` rather than `HIGH_RISK`.
- No LLM usage, no automatic citation rewriting, no live network calls.
- Three new demo projects: field mismatch, fabricated reference, Chinese unsupported.
- Updated README, Chinese README, roadmap, modules, examples, and manifest for V3.0.

## v2.0.0-alpha

- Added external metadata verification for bibliography entries via CrossRef and OpenAlex.
- New CLI: `18-verify-references/verify_external_references.py` writes `reports/external-verification-report.json`.
- Optional bridge flag `--with-external-verification` on `10-check-references/check_references.py`.
- Local JSON cache under `reports/.external-cache/` for repeat runs.
- Alpha scope: no readiness blocking, no hallucination score, no automatic citation rewriting.
- Network failures degrade to `UNAVAILABLE`, never crash the local checker path.

## v2.0.0

- Added Semantic Scholar as the third external verification source alongside CrossRef and OpenAlex.
- Added multi-source consensus candidates using DOI exact match and title similarity.
- Added `generated_at` timestamps to `external-verification-report.json`.
- Added `external_verification` as a readiness advisory dimension while preserving local References blocking logic.
- Updated examples, roadmap, and artifact gallery for the stable external verification workflow.

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
