# Review Loop Product Architecture

## Document Positioning

This document defines the product boundary, architectural direction, and release scope for a thesis review loop in `thesis-skills`.

It is intended to answer the following questions before implementation begins:

1. why a review loop should exist as a first-class workflow
2. what kind of review problems it should solve first
3. what parts of the review loop should remain manual or bounded
4. how it should reuse existing report-driven and patch-driven repository patterns
5. what artifacts and modes should exist for review-driven iteration

Applicable readers:

- roadmap owner
- future implementers of review-loop workflows
- reviewers validating workflow scope and constraints
- AI agents generating implementation plans for review-diff and feedback-ingest modules

---

## 1. Why A Review Loop Exists

`thesis-skills` already supports:

1. bibliography intake
2. Word-to-LaTeX migration
3. deterministic checking
4. report-driven fixing
5. outward export planning via `02-latex-to-word`

These capabilities are strong for getting a thesis into a good internal state.

What is still missing is the structured coordination loop that usually happens after a thesis becomes reviewable:

> advisor review, issue triage, revision planning, selective application, and verification of what changed.

In real thesis workflows, the difficulty is often not “how do I write the next paragraph?”

The difficulty is:

- what should be reviewed first?
- what did the advisor actually ask for?
- which comments are duplicates versus unique issues?
- which requested changes are safe to apply directly?
- which changes need human judgement?
- how do I keep revision rounds inspectable rather than ad hoc?

Without a first-class review loop, authors fall back to unstructured comment handling, manual diffing, and conversational memory instead of reproducible artifacts.

---

## 2. Product Strategy

The review-loop strategy is not to build a generic collaborative document platform.

The strategy is:

> build a bounded, inspectable thesis review workflow that turns review inputs into structured artifacts, prioritized queues, selective patches, and explicit follow-up decisions.

This aligns with the existing `thesis-skills` philosophy:

- deterministic artifact generation
- review-first rather than auto-edit-first behavior
- selective apply instead of broad rewriting
- explicit reports and summaries instead of opaque agent actions

The review loop should therefore act as a workflow layer around:

- exported review copies
- diff summaries
- structured feedback ingestion
- patch proposal and TODO generation
- follow-up verification

---

## 3. Core Product Decision

The review loop should be defined as a **dual-stage workflow family**.

## Stage A: Review Diff And Triage

This stage answers:

- what changed since the last revision?
- what should the human review first?
- how should repeated issues be clustered?
- what review package should be handed to the advisor or author?

## Stage B: Feedback Ingest And Selective Action

This stage answers:

- how should feedback be normalized?
- which items become TODOs?
- which items can become candidate patches?
- which items must remain explicitly human-reviewed?

This dual-stage shape matches the repository’s current separation between:

- findings
- review queues
- patch previews
- bounded apply

---

## 4. Product Boundary

### 4.1 What the review loop should do

At the product level, the review loop should:

1. create review-ready artifacts from the current thesis state
2. summarize diffs or issue clusters in a reviewer-friendly way
3. normalize review input into structured internal artifacts
4. separate “needs review” from “safe to patch”
5. preserve a machine-readable trail of revision decisions

### 4.2 What the review loop should not do

The review loop should not claim:

- full two-way collaborative editing between arbitrary tools
- automatic interpretation of every natural-language advisor comment with perfect accuracy
- automatic application of ambiguous feedback without human review
- live Google Docs / Overleaf / Word collaboration replacement
- invisible merging of multiple review rounds without explicit artifacts

### 4.3 First-release promise

The first review-loop release should promise only that:

- it can generate structured review/diff artifacts
- it can ingest bounded feedback formats into structured issue representations
- it can propose TODOs and selective candidate patches
- it keeps ambiguous or high-risk changes explicitly review-gated

---

## 5. User Scenarios

### Scenario A: Author preparing advisor review

The author wants a clean review package showing what changed and what deserves attention first.

### Scenario B: Advisor comments return in a semi-structured format

The author wants comments converted into actionable, deduplicated, trackable items rather than an unstructured inbox.

### Scenario C: Author wants to selectively apply review-driven edits

The author wants machine assistance in forming candidate patches without losing control over high-judgement changes.

### Scenario D: Author wants to verify what was actually addressed in the revision round

The author wants a review summary showing what was accepted, what remains pending, and what still requires manual attention.

---

## 6. Reusable Existing Repository Patterns

The codebase already contains several patterns that should be reused instead of reinvented.

### 6.1 Structured report contracts

Existing checker reports already provide:

- `summary`
- `findings`
- machine-readable counts
- prioritized review-related fields

This is the natural foundation for review-loop artifacts.

### 6.2 Review-oriented deep findings

`14-check-language-deep` already distinguishes between:

- raw findings
- `review_queue`
- `review_clusters`
- `summary.review_digest`

This is directly relevant to review-loop triage design.

### 6.3 Patch preview and selective apply

`24-fix-language-deep` already establishes:

- patch preview first
- overlap rejection
- `review_required=true` gating
- selective apply flags

This is a strong architectural base for feedback-driven revision flows.

### 6.4 Workflow summaries

`run-summary.json` and `fix-summary.json` already provide workflow-level summaries that can be extended into revision-round summaries.

---

## 7. Borrowable External Patterns

The review loop should borrow specific patterns from adjacent open-source systems, but only where they fit the repository’s bounded workflow philosophy.

### 1. academic-writing-agents

Borrowable pattern:

- split review dimensions by concern instead of treating all feedback as a single undifferentiated stream

Relevant implication for `thesis-skills`:

- advisor review should support clustering by issue class, not only by raw comment order

### 2. PaperKit

Borrowable pattern:

- document revision should be treated as staged workflow progression, not one giant editing event

Relevant implication:

- review loop should preserve round boundaries and iteration summaries

### 3. Open Academic Paper Machine

Borrowable pattern:

- maintain an explicit audit trail of workflow outcomes and decisions

Relevant implication:

- review loop should produce machine-readable revision artifacts rather than relying on chat memory alone

### 4. OpenDraft and adjacent export-focused systems

Borrowable pattern:

- review should be tied to explicit artifacts generated at a workflow boundary, not to vague “latest version” assumptions

Relevant implication:

- review-loop stage A should begin from an explicit exported review package or revision snapshot

### 5. Structured patch-preview systems in coding workflows

Borrowable pattern:

- candidate changes should be previewed, validated, and conflict-checked before application

Relevant implication:

- feedback-driven edits in `thesis-skills` should follow preview-first and selective-apply rules, not blanket application

### What to avoid in a first release

- avoid positioning the system as if it “understands all advisor intent automatically”
- avoid real-time collaborative platform claims
- avoid direct auto-merge of ambiguous comments into source text

---

## 8. Core Product Components

The review loop should be designed around five product components.

## Component 1: Review Package Generation

This component produces the artifacts that define the review boundary.

Examples:

- revision snapshot metadata
- changed-file summary
- chapter-level change digest
- exported review copy reference

Its purpose is to make review rounds explicit rather than implicit.

## Component 2: Review Triage Layer

This component organizes review work into actionable structure.

Examples:

- issue clusters
- priority queues
- repeated pattern grouping
- manual-review-first ordering

This should reuse existing ideas like `review_queue` and `review_clusters`.

## Component 3: Feedback Ingest Layer

This component normalizes inbound feedback from bounded formats into internal review artifacts.

Examples:

- structured Word comments in later phases
- machine-readable review notes
- revision notes or TODO files

This component should focus on normalization, not direct application.

## Component 4: Selective Action Layer

This component decides which feedback becomes:

- TODO items
- candidate patches
- human-review-required issues
- deferred or ambiguous items

This is the layer where `review_required` logic remains critical.

## Component 5: Revision Summary Layer

This component records what happened after a review round.

Examples:

- accepted items
- pending items
- skipped items
- changed files
- unresolved risk areas

This makes the review loop inspectable across rounds.

---

## 9. Relationship To Existing Modules

The review loop should not replace existing checkers or fixers.

Instead, it should sit around them and reuse them.

### Inputs it should reuse

- checker reports
- deep-review findings
- patch previews
- fix summaries
- exported review copies from `02-latex-to-word`

### Outputs it should produce

- review packages
- triage summaries
- feedback-ingest artifacts
- candidate patch bundles
- revision-round summaries

### Important architectural rule

The review loop should remain a workflow family, not a generic mutation engine.

---

## 10. Product Modes

The review loop should expose bounded modes, not one giant “do review” command.

## Mode A: Review-Diff Mode

Purpose:

- show what changed
- help decide what to review first
- produce review-facing summaries

This is the first and safest release mode.

## Mode B: Feedback-Ingest Mode

Purpose:

- convert bounded feedback inputs into structured artifacts
- classify what can become TODOs or patches

This should be introduced only when artifact contracts are clear.

## Mode C: Selective-Revision Mode

Purpose:

- propose candidate patches for safe or review-bounded application

This should remain selective and explicit, not automatic by default.

---

## 11. Artifact Contracts

The review loop should define explicit artifacts for every review round.

### Required artifact families

1. **Review package artifact**
   - what is being reviewed
   - revision id / snapshot reference
   - changed scope

2. **Review triage artifact**
   - prioritized queue
   - clustered issue families
   - review digest

3. **Feedback-ingest artifact**
   - normalized feedback items
   - source references where available
   - confidence / ambiguity status

4. **Selective-action artifact**
   - TODO items
   - candidate patches
   - blocked items

5. **Revision summary artifact**
   - accepted / pending / unresolved counts
   - touched files
   - review-required leftovers

### Why this matters

This prevents review rounds from degrading into undocumented conversational state.

---

## 12. Human Review Boundaries

Human review must stay central in this workflow.

The system should assist with:

- organization
- triage
- normalization
- patch proposal

The system should not silently decide:

- ambiguous scholarly meaning changes
- argument-level restructuring
- advisor intent when comments are underspecified
- major revisions that exceed bounded patch semantics

This is especially important because many thesis changes are not just wording fixes; they often involve argument structure, evidence framing, or methodological nuance.

---

## 13. First-Release Scope

The first release of the review loop should prioritize:

1. review-diff and triage artifacts
2. bounded feedback-ingest contracts
3. TODO generation
4. candidate patch generation only for selective, review-bounded cases

The first release should not prioritize:

1. full comment round-tripping across arbitrary review tools
2. perfect semantic understanding of freeform advisor comments
3. automatic acceptance of all suggested revisions
4. workflow claims that require full collaborative platform features

---

## 14. Relationship To `02-latex-to-word`

The review loop depends on `02-latex-to-word`, but should not collapse into it.

### `02-latex-to-word` is about delivery/export

It creates reviewable outputs.

### The review loop is about coordination after export

It turns review inputs and revision state into structured iteration artifacts.

This separation is important because:

- export and review coordination are different concerns
- export can exist without feedback ingestion
- review loops can later consume non-Word review artifacts too

---

## 15. Release Positioning

### `v0.7.x` review-loop target

The first review-loop release should focus on:

- `03-latex-review-diff`
- triage summaries
- TODO-oriented outputs
- bounded groundwork for `04-word-review-ingest`

### Later extension target

Later releases can strengthen:

- richer comment ingestion
- stronger patch bundling
- review-round state tracking across iterations

---

## 16. Risks

### Risk 1: Review loop becomes a vague collaboration umbrella

Countermeasure:

- anchor it in explicit artifacts
- keep every stage bounded and inspectable

### Risk 2: Ambiguous comments are treated as machine-safe instructions

Countermeasure:

- preserve ambiguity markers
- keep high-judgement changes behind human review gates

### Risk 3: Review and export concerns get mixed together

Countermeasure:

- keep export in `02-latex-to-word`
- keep review coordination in the review-loop family

### Risk 4: Too much happens in the first release

Countermeasure:

- ship review-diff and triage first
- keep ingest/apply workflows incremental

---

## 17. Success Criteria

The product architecture should be considered successful if it enables a first implementation that:

1. reuses existing report and patch patterns instead of inventing a new system
2. creates explicit review-round artifacts
3. gives authors a clear way to triage revision work
4. keeps ambiguous edits review-gated
5. integrates naturally with export and fix workflows without replacing them

---

## 18. Final Product Decision

The thesis review loop in `thesis-skills` should be:

> a bounded, artifact-driven revision workflow family that turns review rounds into explicit packages, triage summaries, structured feedback artifacts, and selective action paths.

It should begin with review-diff and triage, then expand into bounded feedback ingest and selective revision support.

This gives `thesis-skills` a strong differentiator without abandoning its deterministic and inspectable workflow philosophy.

---

## 19. Recommended Next Document

The next planning artifact after this document should be:

`docs/plans/2026-04-20-review-loop-implementation-plan.md`

That implementation plan should define:

- exact module split between review-diff and feedback-ingest
- artifact file names and JSON schemas
- patch/TODO thresholds
- runner or workflow integration points
- phased rollout for `v0.7.x`
