# Technical Roadmap

## Release Positioning

`v0.7.0` is the current public baseline for `thesis-skills`.

The repository now presents a coherent end-to-end workflow story:

```text
bibliography intake
-> Word-to-LaTeX migration
-> deterministic checking
-> report-driven fixing
-> review-first LaTeX-to-Word export
-> bounded review loop
-> readiness gate
```

The roadmap after `v0.7.0` is no longer organized around filling major capability gaps. It focuses on:

- hardening existing workflow contracts
- making the repo easier for real thesis users to understand
- improving scenario-first adoption and presentation
- preparing a stable `v1.0.0` public narrative

## Product Direction

`thesis-skills` is not a general writing assistant and not a thesis template.

It is a deterministic, inspectable, report-driven workflow system for academic writing projects that need:

- bibliography intake from Zotero and EndNote
- Word-to-LaTeX migration
- bounded LaTeX-to-Word export for review-oriented workflows
- bounded review-loop workflows for revision rounds
- bounded compile-log parsing
- bounded pre-submission readiness gating
- repeatable deterministic checks
- bounded report-driven fixes
- reusable rule packs for schools and journals

Design rules that stay in effect:

- keep workflows explicit
- keep outputs inspectable
- keep fixers bounded and reversible
- keep policy in rule packs, not hard-coded into runners
- avoid overstating unsupported capabilities
- prefer workflow contracts over magical behavior

## Current Workflow Status

All listed workflow families are publicly available in `v0.7.0`:

| Workflow | Status | Entrypoint |
|---|---|---|
| Zotero bibliography sync | Stable | `00-bib-zotero/sync_from_word.py` |
| EndNote import-first intake | Stable | `00-bib-endnote/import_library.py` |
| EndNote preflight check | Stable | `00-bib-endnote/check_endnote_export.py` |
| Word-to-LaTeX migration | Stable | `01-word-to-latex/migrate_project.py` |
| LaTeX-to-Word export (review-friendly) | Stable | `02-latex-to-word/migrate_project.py` |
| Review package and triage | Stable | `03-latex-review-diff/review_diff.py` |
| Feedback normalization | Stable | `04-word-review-ingest/feedback_ingest.py` |
| Reference checking | Stable | `10-check-references/check_references.py` |
| Baseline language lint | Stable | `11-check-language/check_language.py` |
| Format checking | Stable | `12-check-format/check_format.py` |
| Content checking | Stable | `13-check-content/check_content.py` |
| Deep language review | Stable | `14-check-language-deep/check_language_deep.py` |
| Compile-log diagnostics | Stable | `15-check-compile/check_compile.py` |
| Pre-submission readiness gate | Stable | `16-check-readiness/check_readiness.py` |
| Reference fixing | Stable | `20-fix-references/fix_references.py` |
| Safe language fixing | Stable | `21-fix-language-style/fix_language_style.py` |
| Format fixing | Stable | `22-fix-format-structure/fix_format_structure.py` |
| Deep patch preview | Stable | `24-fix-language-deep/fix_language_deep.py` |
| Rule-pack creation | Stable | `90-rules/create_pack.py` |

### Not yet implemented

| Capability | Notes |
|---|---|
| EndNote Word field-code parser | Traveling Library extraction and direct Word sync not yet available |
| Submission-friendly export profile | `review-friendly` is the only fully implemented export mode |
| GUI or web editor | Repository is CLI-first |

## Release History (Compact)

| Release | Theme |
|---|---|
| v0.3.0 | Public repository restructure, bilingual README, CI, Zotero as primary bib path |
| v0.4.0 | EndNote XML/RIS/BibTeX import, DOI deduplication, `refNNN` stability, 45 tests |
| v0.5.0 | Deterministic language lint layer (10+ rules) |
| v0.5.1 | Deep language review: sentence-aware, cross-file screening |
| v0.5.2 | Deep patch preview: span-based selective fixes |
| v0.6.0 | Review-friendly LaTeX-to-Word export, compile-log parsing, review-loop workflows |
| v0.7.0 | Pre-submission readiness gate (`PASS / WARN / BLOCK`), advisor-handoff and submission-prep modes |

## Roadmap After v0.7.0

### v0.7.1 — Review Summary Hardening

**Primary goal:** Make the current review-loop story clearer and more useful without drifting into unbounded auto-edit behavior.

**Must-have:**

- chapter-level review summaries
- section-level review summaries where defensible
- richer review digest artifacts
- review TODO generation improvements
- revision-summary artifact improvements
- scenario docs V1 for review, export, and readiness workflows
- landing page V1

**Should-have:**

- clearer linkage from review findings to changed scope
- better repeated-issue grouping and clustering
- more reviewer-friendly chapter digest output

**Must not:**

- widen to generic collaborative editing
- auto-merge ambiguous comments
- expand into broad patch automation by default
- mix review coordination with export mechanics

**Acceptance:** This release is complete when review summaries are more informative at chapter/section granularity, TODO-oriented artifacts are inspectable and reproducible, docs and landing page explain the review loop in scenario language, and no wording suggests the repo automatically "understands all advisor intent."

---

### v0.7.2 — Feedback Ingest And Gate Calibration

**Primary goal:** Connect bounded feedback ingestion with clearer readiness signaling.

**Must-have:**

- Word review ingest contract hardening
- feedback parser and importer hardening
- review-debt to readiness linkage calibration
- clearer `PASS / WARN / BLOCK` explanation output
- richer final gate summary artifacts

**Should-have:**

- source reference tracking inside feedback-ingest artifacts
- ambiguity markers and blocked-item surfaces
- better explanation of "why this thesis is not yet ready"

**Must not:**

- accept all freeform review comments as machine-safe instructions
- silently apply high-judgement feedback
- position the system as a collaborative platform replacement

**Acceptance:** This release is complete when feedback-ingest artifacts are bounded and auditable, readiness output clearly reflects review debt and unresolved blockers, ambiguous items remain explicitly review-gated, and tests cover both ingest and gate summary boundaries.

---

### v0.8.0 — Defense Pack And Showcase

**Primary goal:** Make `thesis-skills` easier to understand from the outside while adding a bounded defense-prep workflow.

**Must-have:**

- defense outline artifact
- chapter highlights for defense prep
- figure inventory for slides
- candidate tables and diagrams inventory
- talk-prep notes artifact
- landing page V2
- artifact demo gallery
- docs homepage and scenario entry page

**Should-have:**

- advisor handoff scenario page
- submission prep scenario page
- clearer before/after artifact examples

**Must not:**

- promise automatic full PPT generation
- let showcase pages market unsupported functionality
- hide workflow limitations on export/review fidelity

**Acceptance:** This release is complete when defense prep produces useful bounded artifacts, the landing page makes the repo understandable to non-technical thesis users, and showcase materials are grounded in real repo outputs.

---

### v0.8.1 — Rule-Pack Ecosystem Hardening

**Primary goal:** Strengthen the extension and maintenance story.

**Must-have:**

- pack lint checks
- completeness checks
- schema consistency checks
- pack maintainability and portability scorecard
- mixed workflow integration docs
- more explicit example packs

**Should-have:**

- stronger non-Tsinghua examples
- guidance for third-party pack contributors
- clearer pack acceptance criteria

**Must not:**

- overengineer the pack system before lint/scorecard value is visible
- widen generic workflows to solve school-specific edge cases too early

**Acceptance:** This release is complete when starter packs can be evaluated with explicit quality signals, docs make extension safer and easier, and ecosystem hardening does not distort generic workflow policy.

---

### v1.0.0 — Stable Public Story

**Primary goal:** Ship a stable public narrative covering intake, migration, export, review, readiness, defense prep, and extension contracts.

**Acceptance:** `v1.0.0` is complete when:

1. README, roadmap, docs, landing page, and actual code paths all match
2. the repository does not claim support that does not exist
3. output artifacts are inspectable and reproducible across main workflows
4. the landing page and GitHub positioning tell the same story
5. the repo reads as one coherent system rather than a loose set of scripts

## Showcase And Scenario Track

The repository already has a scenario-first copy base at `site/copy-source.md`. This track runs parallel to core workflow hardening:

| Milestone | Status |
|---|---|
| Landing page V1 copy source | Existing in `site/copy-source.md` |
| Scenario cards (Word review, compile, feedback, readiness) | Existing in `site/copy-source.md` |
| Artifact showcase examples | Existing in `site/copy-source.md` |
| v0.7 scope boundaries section | Existing in `site/copy-source.md` |
| Static HTML landing page | Existing in `site/index.html` |
| Artifact demo gallery | Planned (v0.8.0) |
| Docs homepage / scenario hub | Planned (v0.8.0) |

Showcase work must follow the same bounded philosophy as code: no marketing copy that claims support the repo cannot prove.

## Priority Matrix

| Track | User Value | Strategic Value | Risk | Priority |
|---|---|---|---|---|
| Review summary hardening (v0.7.1) | High | High | Low-Medium | P0 |
| Feedback ingest + gate calibration (v0.7.2) | High | High | Medium | P0 |
| Landing page / scenario docs V1 | High | High | Low | P0 |
| Defense pack (v0.8.0) | Medium | Medium | Medium | P1 |
| Rule-pack lint / scorecard (v0.8.1) | Medium | Medium | Medium | P1 |
| Mixed workflow integration docs | Medium | Medium | Low | P1 |

## Suggested Execution Order

If only one track is chosen:

1. `v0.7.1` review summary hardening

If two tracks:

1. `v0.7.1` review summary hardening
2. landing page / scenario docs V1

If three tracks:

1. `v0.7.1` review summary hardening
2. landing page / scenario docs V1
3. `v0.7.2` feedback ingest and gate calibration

This order preserves the narrative: first make the current review story clearer, then make the repo easier to understand, then connect ingest and readiness more tightly.

## Cross-Release Acceptance Gates

Every release in this roadmap is only complete when:

1. docs, manifest, landing page, and actual code paths match
2. the repository does not claim support that does not exist
3. test fixtures cover the workflow boundary being described
4. output artifacts are inspectable and reproducible
5. README positioning still matches the actual repository philosophy
6. non-technical thesis users can understand the main value proposition without reading internal module names first

## Planning References

- `docs/plans/thesis-skills-roadmap-v2.md` — full strategic roadmap after v0.7.0
- `docs/plans/thesis-skills-agent-next-steps-prompt.md` — agent execution prompt for the next packaging and hardening cycle
