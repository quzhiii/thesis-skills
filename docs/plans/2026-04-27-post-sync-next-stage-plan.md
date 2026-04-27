# Post Progress Sync Next Stage Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Turn the repository's real post-sync state into a coherent next-stage execution sequence, without reopening already-landed v0.7.x scope.

**Architecture:** Treat `v0.7.1` and `v0.7.2` as core-hardening slices that are already mostly landed, treat `v0.8.0` as feature-complete enough for polish rather than net-new surface, and make the next push a two-step sequence: public-surface consistency first, ecosystem hardening second. Use `v1.0.0` as the narrative/stabilization gate instead of another broad feature expansion.

**Tech Stack:** Markdown planning docs, static HTML showcase pages, Python CLI workflows, JSON artifacts, YAML rule packs.

---

## Synced Baseline

### Already materially landed

- `v0.7.1`
  - chapter-level review summaries
  - richer review digest baseline
  - TODO-oriented selective action outputs
  - revision summary counts
  - landing page V1 / scenario docs V1 surfaces
- `v0.7.2`
  - ingest-to-readiness calibration
  - ingest-only `advisor-handoff => WARN` / `submission-prep => BLOCK`
  - bounded source-ref and debt-detail explanations
- `v0.8.0`
  - defense outline
  - chapter highlights
  - figure inventory
  - candidate tables / diagrams inventory
  - talk-prep notes
  - artifact gallery
  - docs homepage / scenario entry
  - showcase landing page entry

### Remaining high-value gaps

- `v0.7.1`
  - section-level summaries only if a stable bounded contract is defensible
  - digest polish around changed-scope linkage and repeated-issue grouping
- `v0.7.2`
  - deeper ingest schema / importer hardening if the input surface broadens
  - stronger docs/examples for ingestion and readiness scenarios
- `v0.8.0`
  - dedicated advisor-handoff / submission-prep scenario pages
  - before/after artifact examples
  - landing-page / site wording consistency polish
- `v0.8.1`
  - pack lint / completeness / schema-consistency foundation

---

## Recommended Next Push Order

### Phase 1 — Close `v0.8.0` Public-Surface Polish

**Why first:** The repo already has a broad visible surface for review, readiness, and defense-prep. The biggest remaining gap is not missing capability but inconsistent packaging and discoverability.

**Deliverables:**

1. Add dedicated advisor-handoff scenario page
2. Add dedicated submission-prep scenario page
3. Add before/after artifact examples grounded in real outputs
4. Align `site/README.md`, landing-page wording, and roadmap language around the current `v0.8` showcase state

**Completion signal:** A non-technical thesis user can understand the review → readiness → defense-prep path from the static site without reading internal module names.

---

### Phase 2 — Start `v0.8.1` Rule-Pack Hardening Foundation

**Why second:** The codebase already has enough user-facing value. The next leverage point is making extension quality visible and safer before expanding school-specific examples.

**Deliverables:**

1. Define the minimal lint contract for starter packs
2. Add completeness checks for required pack fields/files
3. Add schema consistency checks for pack structure
4. Add a first maintainability / portability scorecard output
5. Document mixed local / Git / export workflow expectations

**Completion signal:** A starter pack can be evaluated with explicit quality signals instead of only manual inspection.

---

### Phase 3 — `v1.0.0` Coherence / Stabilization Pass

**Why third:** After public-surface polish and ecosystem hardening, the remaining work is mostly narrative alignment and public packaging discipline.

**Deliverables:**

1. Align README / README.zh-CN / roadmap / site copy / manifest wording
2. Remove stale version wording and historical gap phrasing
3. Harden extension-contract language for third-party contributors
4. Refresh release checklist and public version-story consistency

**Completion signal:** Docs, code, landing pages, and repository positioning all tell the same bounded story.

---

## Explicit Deferrals

- Do **not** force section-level review summaries unless the bounded contract is genuinely stable.
- Do **not** widen feedback ingest into broad natural-language advisor-intent understanding.
- Do **not** start broad new feature families before `v0.8.0` polish and `v0.8.1` foundation work are done.

---

## Recommendation

If only one next execution track is chosen, choose **Phase 1 — `v0.8.0` public-surface polish**.

It has the best ratio of:

- user-facing clarity
- release coherence
- low technical risk
- direct support for eventual `v1.0.0` stabilization
