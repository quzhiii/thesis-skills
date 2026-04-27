# Thesis Skills Roadmap v2

## Document Positioning

This document updates the roadmap for `thesis-skills` **after the public `v0.7.0` baseline**.

It replaces the earlier posture of “fill major missing capability gaps” with a new posture:

> harden the already-visible export / review / readiness story, improve scenario-first adoption, and prepare the repository for a clearer `v1.0.0` public narrative.

This version is intended to serve four purposes:

1. reset the roadmap baseline to the repo’s current public state
2. narrow the next execution windows instead of widening product scope
3. separate **core workflow hardening** from **showcase / adoption work**
4. give future agents a stable execution order with explicit acceptance gates

Applicable readers:

- repository maintainer and roadmap owner
- developers implementing `v0.7.x` and `v0.8.x`
- AI agents preparing execution plans and acceptance checklists
- contributors who need a current product story rather than a historical gap list

---

## 1. Current Public Baseline

`thesis-skills` is no longer just:

```text
bib intake -> Word->LaTeX -> check -> fix
```

At the current public baseline, the repository already presents a broader workflow story:

```text
bib intake
-> Word->LaTeX migration
-> deterministic checking
-> report-driven fixing
-> review-first LaTeX->Word export
-> bounded review loop
-> readiness gate
```

That means the roadmap should no longer be organized around whether these workflow families exist at all.

The roadmap should now focus on:

- hardening existing contracts
- clarifying user-facing scenarios
- improving cross-workflow summaries
- packaging the system so non-technical thesis users can immediately understand its value

---

## 2. Product Direction

The repository should continue to act as:

> a deterministic, inspectable, report-driven thesis workflow system for migration, export, review, diagnostics, and readiness.

This direction preserves the existing design rules:

- keep workflows explicit
- keep outputs inspectable
- keep fixers bounded
- keep policy in rule packs
- avoid overstating unsupported capabilities
- prefer workflow contracts over magical behavior

The strategic shift after `v0.7.0` is not “add as many new modules as possible.”

The strategic shift is:

> turn the existing workflow families into a coherent, user-comprehensible, release-stable system.

---

## 3. What Changes In This v2 Roadmap

Compared with the older roadmap shape, this v2 version makes five deliberate changes.

### Change 1: Reset the baseline to `v0.7.0`

The roadmap should stop describing `LaTeX -> Word`, compile diagnostics, review loop, and readiness gate as if they are still purely future work.

They now exist as public workflow families and should be treated as:

- hardening targets
- packaging targets
- scope-calibration targets

### Change 2: Split `v0.7.x` into two narrower execution windows

Instead of treating review + ingest + readiness as one large release theme, break them into:

- `v0.7.1` = review summary hardening
- `v0.7.2` = feedback ingest and gate calibration

This reduces scope drift and keeps the review-loop boundary aligned with the existing bounded philosophy.

### Change 3: Add an explicit showcase / adoption track

The repo now needs a **scenario-first presentation layer**.

This is not a GUI product rewrite.
It is a packaging layer that includes:

- landing page / homepage
- artifact demos
- scenario cards
- terminology translation for non-technical thesis users
- docs homepage / quickstarts by scenario

### Change 4: Separate user-facing work from infra-facing work

`Defense Pack` and `Rule-Pack Hardening` should no longer sit in one undifferentiated bucket.

The roadmap should distinguish:

- user-facing workflow expansion
- ecosystem / maintainability hardening

### Change 5: Make `v1.0.0` a public-story stabilization milestone

`v1.0.0` should not merely mean “more features.”

It should mean the repository tells one stable end-to-end story:

- intake
- migration
- export
- review
- readiness
- defense
- extension contracts

---

## 4. Strategic Goals After `v0.7.0`

### Goal A: Make the existing delivery / review / readiness layers easier to understand

Many users do not naturally search for terms like:

- review loop
- compile parser
- rule pack
- readiness gate

They search for:

- “导师只看 Word 怎么办”
- “论文报错看不懂”
- “返修意见太乱怎么整理”
- “盲审前怎么知道能不能交”

This means product packaging is now a first-class roadmap concern.

### Goal B: Harden the current workflow contracts before widening scope

The repository now has enough surface area that uncontrolled expansion becomes risky.

The next stage should strengthen:

- artifact schemas
- review summaries
- export/report consistency
- gate explanation quality
- cross-workflow linkage

before widening into more automation.

### Goal C: Protect the bounded philosophy

The repository should not drift into:

- generic collaborative editing
- vague AI writing assistant positioning
- hidden auto-merge of ambiguous advisor comments
- universal converter claims
- opaque “one click fixes everything” behavior

### Goal D: Improve adoption without weakening technical credibility

The repo now needs:

- scenario-first docs
- stable landing-page copy
- artifact examples
- clearer “supported vs not promised” sections

That work should improve adoption while preserving honest scope.

---

## 5. Roadmap Themes v2

The upgrade program after `v0.7.0` is organized into seven themes.

### Theme A: Delivery / Export Hardening

Stabilize and better present the existing `02-latex-to-word` workflow.

### Theme B: Review Summary And Revision Coordination

Strengthen review-diff, triage, TODO generation, and revision summaries before widening automated ingest/apply logic.

### Theme C: Build / Readiness Reliability

Calibrate compile diagnostics, readiness verdicts, and cross-workflow explanation quality.

### Theme D: Defense Workflow

Support final-mile defense preparation with bounded artifacts rather than auto-generated slide decks.

### Theme E: Rule-Pack Ecosystem

Improve linting, completeness checks, and pack scorecards.

### Theme F: Documentation / Onboarding / Showcase

Create scenario-first docs, landing page messaging, artifact demos, and terminology translation.

### Theme G: Mixed Workflow Integration Guidance

Clarify how the repository fits local Git + Word + Zotero + LaTeX + Pandoc workflows without trying to own the full authoring environment.

---

## 6. Non-Negotiable Design Rules

1. Do not break the current deterministic/report-driven core.
2. Do not turn export or review workflows into opaque magic.
3. Do not overstate conversion fidelity.
4. Do not auto-apply ambiguous advisor feedback by default.
5. Do not hard-code school-specific policy into general workflows.
6. Do not add showcase/UI work that misrepresents actual repo capability.
7. Do not widen product scope unless the previous release gate is satisfied.
8. Do not let adoption work outrun contract clarity.

---

## 7. Release Train v2

## `v0.7.1` — Review Summary Hardening

### Primary goal

Make the current review-loop story clearer, narrower, and more useful without drifting into unbounded auto-edit behavior.

### Must-have items

- chapter-level review summaries
- section-level review summaries where defensible
- richer review digest artifacts
- review TODO generation
- revision-summary artifact improvements
- scenario docs V1 for review / export / readiness
- landing page V1

### Should-have items

- clearer linkage from review findings to changed scope
- better repeated-issue grouping / clustering summaries
- more reviewer-friendly chapter digest output

### Must not do

- do not widen to generic collaborative editing
- do not auto-merge ambiguous comments
- do not expand into broad patch automation by default
- do not mix review coordination with export mechanics

### Acceptance direction

This release is only complete when:

1. review summaries are more informative at chapter/section granularity
2. TODO-oriented artifacts are inspectable and reproducible
3. docs and landing page explain the review loop in scenario language
4. no new wording suggests the repo automatically “understands all advisor intent”

---

## `v0.7.2` — Feedback Ingest And Gate Calibration

### Primary goal

Connect bounded feedback ingestion with clearer readiness signaling.

### Must-have items

- Word review ingest contract hardening
- first feedback parser / importer hardening
- review-debt to readiness linkage calibration
- clearer `PASS / WARN / BLOCK` explanation output
- richer final gate summary artifacts

### Should-have items

- source reference tracking inside feedback-ingest artifacts
- ambiguity markers and blocked-item surfaces
- better explanation of “why this thesis is not yet ready”

### Must not do

- do not accept all freeform review comments as machine-safe instructions
- do not silently apply high-judgement feedback
- do not position the system as a collaborative platform replacement

### Acceptance direction

This release is only complete when:

1. feedback-ingest artifacts are bounded and auditable
2. readiness output clearly reflects review debt and unresolved blockers
3. ambiguous items remain explicitly review-gated
4. tests cover both ingest and gate summary boundaries

---

## `v0.8.0` — Defense Pack And Showcase

### Primary goal

Make `thesis-skills` easier to understand from the outside while adding a bounded defense-prep workflow.

### Must-have items

- defense outline artifact
- chapter highlights for defense prep
- figure inventory for slides
- candidate tables / diagrams inventory
- talk-prep notes artifact
- landing page V2
- artifact demo gallery
- docs homepage / scenario entry page

### Should-have items

- advisor handoff scenario page
- submission prep scenario page
- clearer before/after artifact examples

### Must not do

- do not promise automatic full PPT generation
- do not let showcase pages market unsupported functionality
- do not hide workflow limitations on export/review fidelity

### Acceptance direction

This release is only complete when:

1. defense prep produces useful bounded artifacts
2. the landing page makes the repo understandable to non-technical thesis users
3. showcase materials are grounded in real repo outputs

---

## `v0.8.1` — Rule-Pack Ecosystem Hardening

### Primary goal

Strengthen the extension and maintenance story of the repository.

### Must-have items

- pack lint checks
- completeness checks
- schema consistency checks
- pack maintainability / portability scorecard
- mixed workflow integration docs
- more explicit example packs / examples

### Should-have items

- stronger non-Tsinghua examples
- guidance for future third-party pack contributors
- clearer pack acceptance criteria

### Must not do

- do not overengineer the pack system before the lint/scorecard value is visible
- do not widen generic workflows to solve school-specific edge cases too early

### Acceptance direction

This release is only complete when:

1. starter packs can be evaluated with explicit quality signals
2. docs make extension safer and easier
3. ecosystem hardening does not distort generic workflow policy

---

## `v1.0.0` — Stable Public Story

### Primary goal

Ship a stable public story covering:

- bibliography intake
- Word-to-LaTeX migration
- deterministic checking
- report-driven fixing
- LaTeX-to-Word export
- review loop
- readiness gate
- defense prep
- extension contracts

### Acceptance direction

`v1.0.0` is only complete when:

1. README, roadmap, docs, manifest, and actual code paths all match
2. the repository does not claim support that does not exist
3. output artifacts are inspectable and reproducible across the main workflows
4. the landing page and GitHub positioning tell the same story
5. the repo feels like one coherent system rather than a loose set of scripts

---

## 8. Priority Matrix v2

| Track | User Value | Strategic Value | Implementation Risk | Recommended Priority |
|---|---:|---:|---:|---|
| Review summary hardening | High | High | Low-Medium | P0 |
| Feedback ingest + gate calibration | High | High | Medium | P0 |
| Landing page / scenario docs | High | High | Low | P0 |
| Defense pack first release | Medium | Medium | Medium | P1 |
| Rule-pack lint / scorecard | Medium | Medium | Medium | P1 |
| Mixed workflow integration docs | Medium | Medium | Low | P1 |

---

## 9. Execution Backlog v2

This backlog is synchronized to the repository state as of `2026-04-27`.
Checked items reflect behavior that is already present in the codebase and covered by direct artifact paths and tests.
Unchecked items are the remaining backlog, not historical work that has already landed.

## Batch A — `v0.7.1` Review Summary Hardening

- [x] audit current review-loop artifacts and JSON shapes
- [x] define chapter-level summary contract
- [ ] define section-level summary contract where stable
- [x] add richer review digest fields
- [x] add review TODO generation improvements
- [x] add tests for chapter-level summary artifacts and TODO-oriented digest fields
- [x] refresh review-related README / docs wording
- [x] create landing page V1 and scenario docs V1
- [ ] deepen changed-scope linkage, repeated-issue grouping, and reviewer-friendly digest polish without widening automation

## Batch B — `v0.7.2` Feedback Ingest And Gate Calibration

- [x] audit current `04-word-review-ingest` contract
- [ ] define feedback-ingest artifact schema updates for any broader ingest surface
- [ ] deepen ambiguity / blocked-item hardening beyond current bounded heuristics
- [x] calibrate readiness gate against review debt
- [x] improve `PASS / WARN / BLOCK` explanation quality
- [x] add tests for ingest + gate linkage
- [ ] update docs and examples for ingestion / readiness scenarios

## Batch C — `v0.8.0` Defense Pack And Showcase

- [x] create defense-pack workflow scaffold
- [x] generate defense outline artifact
- [x] generate chapter highlight artifact
- [x] generate figure inventory for slides
- [x] generate candidate table / diagram inventory
- [x] generate talk-prep notes artifact
- [x] create landing page V2 showcase entry
- [x] build artifact demo gallery
- [x] create docs homepage / scenario hub
- [x] add dedicated advisor-handoff / submission-prep scenario pages as static editorial guides
- [x] add clearer before/after artifact examples in the existing artifact gallery flow
- [x] polish landing-page and site-directory wording so `v0.8` showcase surfaces describe themselves consistently

## Batch D — `v0.8.1` Rule-Pack Ecosystem Hardening

- [ ] document the current starter-pack baseline and its extension assumptions
- [ ] add pack linting tool
- [ ] add completeness checks
- [ ] add schema consistency checks
- [ ] add pack scorecard output
- [ ] add docs for mixed local / Git / export workflows
- [ ] expand example packs and example projects

## Batch E — `v1.0.0` Stabilization

- [ ] review naming consistency across workflows and artifacts
- [ ] align README, roadmap, landing page, docs, and manifest
- [ ] harden extension contracts for third-party packs
- [ ] remove stale roadmap claims and historical gap wording
- [ ] confirm the repository tells one stable end-to-end story

---

## 10. Suggested Execution Order

From the synchronized project state, the next order should be:

1. close the remaining `v0.8.0` showcase / public-surface polish
2. start the `v0.8.1` rule-pack hardening foundation
3. use `v1.0.0` as a coherence and stabilization pass across docs, site, manifest, and public positioning

`v0.7.1` and `v0.7.2` still have optional polish items, but they are no longer the highest-leverage missing-capability tracks.

```text
first make the existing showcase and defense-prep story internally consistent
then harden the extension ecosystem
then lock the public narrative for v1.0.0
```

---

## 11. Cross-Release Acceptance Gates

Each release in this roadmap should only be considered complete when all of the following are true:

1. docs, manifest, landing page, and actual code paths match
2. the repository does not claim support that does not exist
3. test fixtures cover the workflow boundary being marketed
4. output artifacts are inspectable and reproducible
5. README positioning still matches the actual repository philosophy
6. non-technical thesis users can understand the main value proposition without reading internal module names first

---

## 12. Final Recommendation

The next stage of `thesis-skills` should be anchored around this statement:

> after `v0.7.0`, the priority is not to add the broadest new capability surface, but to harden and package the existing delivery, review, and readiness workflows into a coherent public system.

That means:

- narrow `v0.7.x`
- add a scenario-first showcase layer
- keep review ingest bounded
- defer ecosystem hardening until the user-facing story is clearer

This protects the repository’s strongest qualities while making it substantially easier for real thesis users to understand and adopt.
