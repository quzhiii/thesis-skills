# Thesis Skills Agent Prompt — Next Full Task After `v0.7.0`

You are working on the repository `quzhiii/thesis-skills`.

You are **not** starting from the old pre-`v0.6` state.
You must treat the repository as already being at a public **`v0.7.0` baseline** with visible workflow families for:

- bibliography intake
- Word-to-LaTeX migration
- deterministic checking
- report-driven fixing
- review-first LaTeX-to-Word export
- bounded review loop
- readiness gate

Your job is to execute the **next packaging + hardening cycle** in a narrow, disciplined way.

The objective is **not** to widen the repo into a generic writing assistant.
The objective is:

> harden the current review/export/readiness story, make it easier for real thesis users to understand, and preserve the bounded, inspectable workflow philosophy.

---

# 1. Working Rules

You must follow these rules throughout execution.

## 1.1 Product rules

- Do not reposition the repo as a general-purpose writing assistant.
- Do not market `02-latex-to-word` as a universal converter.
- Do not turn review loop features into opaque auto-edit behavior.
- Do not auto-apply ambiguous advisor feedback by default.
- Do not add showcase copy that claims support the repo cannot prove.

## 1.2 Engineering rules

- Prefer narrow, testable increments.
- Preserve current deterministic / inspectable artifact contracts.
- Update tests before or with behavior changes.
- Keep JSON summaries and report artifacts stable and explicit.
- Keep docs, README, roadmap, and visible behavior aligned.

## 1.3 Process rules

- Work in phases.
- Do not mix too many themes in one pass.
- Treat adoption / showcase work as a first-class deliverable, but do not let it outrun code truth.
- At the end of each phase, produce a short acceptance checklist and verify it explicitly.

---

# 2. Mission

Complete the following deliverables:

1. update the roadmap to a post-`v0.7.0` version
2. create a first landing-page / scenario-doc copy layer
3. harden the next narrow `v0.7.x` execution slice around **review summaries**
4. prepare the repo for the next slice: **feedback ingest + readiness calibration**

This means the next cycle is not “add the broadest new capability.”
It is:

- narrow `v0.7.x`
- improve review summary artifacts
- improve scenario-first presentation
- align docs and roadmap with actual current repo state

---

# 3. Phase Order

Execute in this order.
Do not skip ahead.

## Phase A — Repository Reality Check

### Goal
Confirm the repo’s current public state and identify what is already true vs what docs still describe as future work.

### Tasks

1. Inspect the current repo tree and visible workflow modules.
2. Inspect `README.md`, `README.zh-CN.md`, `docs/architecture.md`, and `docs/roadmap.md`.
3. Identify stale wording that still sounds like:
   - pre-`v0.6` capability gaps
   - speculative future-work phrasing for already-public modules
4. Write a short audit note summarizing:
   - current public baseline
   - stale roadmap wording
   - mismatches between docs and public story

### Acceptance

Phase A is done only when you can clearly state:

- what the current `v0.7.0` baseline already includes
- which roadmap lines are now outdated
- which user-facing surfaces need alignment first

---

## Phase B — Roadmap v2 Update

### Goal
Rewrite roadmap positioning from a historical gap roadmap into a post-`v0.7.0` hardening roadmap.

### Tasks

1. Update the roadmap baseline to `v0.7.0`.
2. Replace any wording that implies:
   - no `LaTeX -> Word`
   - no compile diagnostics
   - no review loop
   - no readiness gate
3. Split `v0.7.x` into two narrower slices:
   - `v0.7.1` = Review Summary Hardening
   - `v0.7.2` = Feedback Ingest And Gate Calibration
4. Add an explicit showcase / adoption track:
   - landing page
   - scenario docs
   - artifact demo layer
5. Separate `v0.8.0` and `v0.8.1` into:
   - Defense Pack And Showcase
   - Rule-Pack Ecosystem Hardening
6. Preserve bounded product principles.

### Files to modify

- `docs/roadmap.md`
- optionally `README.md`
- optionally `README.zh-CN.md`
- optionally `docs/architecture.md` if wording alignment is required

### Acceptance

Phase B is done only when:

- roadmap baseline clearly starts after `v0.7.0`
- `v0.7.x` is narrower and clearer
- showcase / scenario work is visible as a real track
- wording does not overclaim support

---

## Phase C — Landing Page / Scenario Layer v1

### Goal
Create a first scenario-first presentation layer for non-technical thesis users.

### Tasks

1. Create a landing-page or homepage copy file in docs, for example:
   - `docs/landing-page-copy.md`
   - or `docs/showcase/landing-page-v1.md`
2. Organize it around user situations, not internal module names.
3. Include these sections:
   - Hero
   - pain points
   - scenario cards
   - how it works
   - artifact showcase
   - why trust it
   - support boundaries
   - CTA
4. Translate repo capability into user language such as:
   - 导师只看 Word
   - 报错看不懂
   - 返修意见太散
   - 交稿前想先看 verdict
5. Keep all claims bounded and evidence-based.

### Acceptance

Phase C is done only when:

- the page can be understood without reading internal workflow IDs first
- the page explains real artifacts, not vague AI promises
- support boundaries are explicit
- the page can be used as the copy base for a future front-end or docs homepage

---

## Phase D — Review Summary Hardening (`v0.7.1` Core Slice)

### Goal
Improve the current review-loop artifacts without drifting into broad automation.

### Scope lock
This phase should focus on **summary / digest / queue quality**.
It should **not** widen into broad patch automation or speculative semantic comment understanding.

### Tasks

1. Inspect current review-related code and tests, especially around:
   - `core/review_loop.py`
   - review-loop tests
   - `03-latex-review-diff/`
   - `04-word-review-ingest/`
   - readiness dependencies on review debt
2. Define or refine a narrow artifact contract for:
   - chapter-level summary
   - section-level summary (if stable)
   - richer review digest
   - TODO generation
3. Write failing tests first.
4. Implement the minimal behavior required to satisfy those tests.
5. Verify no widening into unbounded apply logic.
6. Update docs if CLI/output shape changes.

### Acceptance

Phase D is done only when:

- chapter-level summaries exist and are meaningful
- section-level summaries exist only if they are stable and defensible
- TODO generation is clearer and still inspectable
- no new behavior silently applies ambiguous edits

---

## Phase E — Prepare `v0.7.2` (Feedback Ingest + Gate Calibration)

### Goal
Prepare the next execution slice without fully widening into it yet.

### Tasks

1. Audit the current Word review ingest contract.
2. Identify gaps in:
   - ambiguity markers
   - blocked-item handling
   - source reference tracking
   - linkage to readiness gate
3. Write a short implementation plan or TODO doc for the next slice.
4. If the repo is already close, optionally add test scaffolding only.

### Acceptance

Phase E is done only when:

- the next `v0.7.2` slice is clearly defined
- the handoff from review summaries to ingest/gate work is explicit
- no premature broadening of ingest behavior has happened

---

# 4. Concrete Output Files To Produce

You should aim to produce or update the following artifacts.

## Required

- updated `docs/roadmap.md`
- one landing-page/scenario copy doc
- code + tests for review summary hardening
- one short implementation / planning note for the next ingest+gate slice

## Recommended

- README top-section wording alignment
- docs homepage or showcase index stub
- screenshots placeholder list / artifact-demo TODO section

---

# 5. Recommended Implementation Style

## 5.1 For roadmap and docs work

- edit in place where appropriate
- avoid huge rewrites if targeted structural edits suffice
- keep wording concrete and release-aware

## 5.2 For review summary code work

- use TDD
- start from artifact shape
- write failing tests first
- make the smallest implementation that passes
- keep summaries explicit and bounded

## 5.3 For agent status reporting

After each phase, provide:

1. what changed
2. what files changed
3. what tests were added or updated
4. what still remains open
5. whether the phase acceptance criteria passed

---

# 6. Validation Checklist

You must explicitly validate the following before stopping.

## Roadmap validation

- [ ] baseline is clearly post-`v0.7.0`
- [ ] `v0.7.1` and `v0.7.2` are split cleanly
- [ ] showcase / scenario work is visible
- [ ] no stale “missing major capability” wording remains where untrue

## Landing-page validation

- [ ] hero is user-language first
- [ ] scenario cards are clear without internal jargon
- [ ] artifact showcase explains real outputs
- [ ] support boundaries are explicit
- [ ] copy does not overpromise AI behavior

## Review-summary validation

- [ ] chapter-level summaries are present
- [ ] section-level summaries are only included if stable
- [ ] TODO generation remains inspectable
- [ ] ambiguous review items are not auto-applied
- [ ] tests cover the new artifact shape

## Repository-alignment validation

- [ ] docs and code tell the same story
- [ ] no new wording implies unsupported universal conversion or collaboration features
- [ ] the repo still reads as deterministic / inspectable / bounded

---

# 7. Suggested Commit Sequence

Use a narrow, reviewable commit sequence.

1. `docs: reset roadmap baseline to v0.7 and narrow next release train`
2. `docs: add landing page and scenario-first showcase copy`
3. `test: add failing tests for review summary artifacts`
4. `feat: harden review loop chapter and section summaries`
5. `docs: add next-slice plan for feedback ingest and gate calibration`
6. `docs: align README top-level positioning with post-v0.7 story`

Adjust if necessary, but keep commits small and semantically clear.

---

# 8. What Not To Do

- Do not rewrite the repo into a web app.
- Do not add flashy demo copy unsupported by repo behavior.
- Do not let “landing page” work become fake product marketing.
- Do not widen review-loop scope into generic collaborative tooling.
- Do not start defense-pack or rule-pack linting work in this cycle unless the current phase is already complete.
- Do not collapse roadmap updates, code changes, and docs changes into one giant unreviewable patch.

---

# 9. Final Success Condition

This task is successful only if, at the end:

1. the roadmap clearly reflects the real post-`v0.7.0` state
2. the repo has a usable landing-page/scenario copy base
3. the next `v0.7.1` slice is concretely advanced through review-summary hardening
4. the next `v0.7.2` slice is clearly prepared but not prematurely widened
5. the repository’s public story becomes easier for real thesis users to understand without weakening its bounded, deterministic philosophy
