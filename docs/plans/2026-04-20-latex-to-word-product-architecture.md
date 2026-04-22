# 02-latex-to-word Product Architecture

## Document Positioning

This document defines the product boundary, architectural direction, and release scope for a new `02-latex-to-word` workflow in `thesis-skills`.

It is intended to answer the following questions before implementation begins:

1. why this workflow should exist
2. what user problem it solves first
3. what it should explicitly not promise
4. how it fits the current repository architecture
5. what output contracts and release modes should exist

Applicable readers:

- roadmap owner
- future implementers of `02-latex-to-word`
- reviewers validating scope before implementation
- AI agents generating implementation plans from this design

---

## 1. Why `02-latex-to-word` Exists

`thesis-skills` already provides:

1. bibliography intake
2. Word-to-LaTeX migration
3. deterministic checking
4. report-driven fixing
5. rule-pack onboarding and reuse

This means the repository is already strong at moving content into a structured LaTeX-centered workflow and then improving that workflow through explicit checks and bounded fixes.

The most obvious product gap now is the reverse direction:

> once a thesis lives in LaTeX, there is no first-class workflow for producing a Word-friendly output for advisor review, institutional submission, or mixed collaboration environments.

This matters because many real thesis workflows are not purely LaTeX-native end to end.

In practice, thesis authors often still need one or more of the following:

- a `.docx` file for an advisor who comments in Word
- a review copy for collaborators who do not use LaTeX
- a submission-oriented Word file for school-specific administrative flows
- a structured export that can be further edited in Word or WPS

Without this workflow, the repository remains strong on internal thesis mechanics but incomplete on final delivery and collaboration.

---

## 2. Product Strategy

The strategy for `02-latex-to-word` is not “build a universal LaTeX converter.”

The strategy is:

> build a bounded, inspectable, thesis-oriented export workflow that produces useful `.docx` outputs while making limitations explicit.

This keeps the workflow aligned with the existing `thesis-skills` philosophy:

- explicit contracts instead of vague magic
- inspectable artifacts instead of hidden behavior
- deterministic workflows instead of unconstrained rewriting
- bounded claims instead of marketing promises

The key product decision is:

## `02-latex-to-word` uses a dual-mode design

### Primary mode: review-friendly export

This is the first-class mode for the first release.

The goal is:

- readable
- commentable
- structurally faithful enough for thesis review
- explicit about degraded constructs

### Secondary mode: submission-friendly export

This mode is part of the product architecture, but not the first release’s main promise.

The goal is:

- support later school-facing `.docx` workflows
- reuse the same export pipeline where possible
- allow stricter style/template handling later

This mode should be treated as an architectural extension target, not as the primary guarantee of `v0.6.x`.

---

## 3. Product Boundary

### 3.1 What `02-latex-to-word` should do

At the product level, the workflow should:

1. take a LaTeX thesis project as input
2. produce a `.docx` output suitable for review or further downstream use
3. preserve structure and document meaning as far as realistically possible
4. emit an export report describing unsupported or degraded constructs
5. support explicit export profiles rather than a one-size-fits-all mode

### 3.2 What `02-latex-to-word` should not do

The workflow should not claim:

- perfect round-trip fidelity for arbitrary LaTeX
- full preservation of custom macros without explicit support
- complete visual equivalence with PDF output
- first-release suitability for every university’s final submission standard
- automatic repair of every unsupported construct during export

### 3.3 What the first release should explicitly promise

The first release should promise only that:

- it can produce a review-oriented `.docx` from a thesis LaTeX project
- document hierarchy is intentionally preserved
- common thesis structure can survive export in a usable form
- common unsupported constructs are surfaced in an export report
- future stricter export profiles can build on the same workflow contracts

---

## 4. User Scenarios

### Scenario A: Advisor review copy

An author has a working LaTeX thesis and needs a `.docx` file that an advisor can open, read, annotate, and return.

This is the primary user scenario for the first release.

### Scenario B: Mixed collaboration

An author needs to share content with collaborators who are more comfortable reading or editing in Word-like environments.

This is still aligned with the primary review-friendly mode.

### Scenario C: Submission-oriented export

An author needs a `.docx` file shaped more closely toward institutional formatting requirements.

This scenario matters, but should be treated as a later-stage mode with stronger template and style requirements.

---

## 5. Product Modes

The workflow should expose explicit export modes rather than hiding divergent behaviors under one command.

## Mode A: Review-Friendly Export

### Purpose

Produce a `.docx` optimized for readability, structure preservation, and commentability.

### Priorities

1. preserve chapter and section hierarchy
2. preserve readable bibliography and citations
3. preserve figures, captions, and tables where feasible
4. keep the output easy to review in Word or WPS
5. surface unsupported constructs clearly

### Non-priorities

- exact visual matching to the compiled PDF
- school-specific final formatting guarantees
- exhaustive handling of every LaTeX package

## Mode B: Submission-Friendly Export

### Purpose

Produce a stricter `.docx` path intended for later institutional submission workflows.

### Priorities

1. stronger style mapping
2. template-aware output shaping
3. better handling of school-specific structure and metadata

### Status

Architecturally defined now, but not the main promise of the initial release.

---

## 6. Why Pandoc-First Is The Right Initial Direction

The first implementation should be built around a Pandoc-first export path.

### Why this fits

1. the repository already values explicit workflow contracts over bespoke magic
2. the Pandoc ecosystem is the most realistic open-source baseline for `.docx` export
3. a wrapper-plus-contract architecture fits the existing `thesis-skills` style better than a from-scratch converter
4. it keeps the first release realistic and bounded

### What this means in practice

The product should be architected as:

```text
LaTeX thesis project
-> export profile resolution
-> project normalization / export preparation
-> Pandoc-first conversion path
-> post-export reporting
-> export summary artifact
```

This does not mean Pandoc magically solves everything.

It means the first release should use Pandoc where it is strong, while explicitly reporting where fidelity breaks down.

---

## 7. Common Failure Modes The Product Must Respect

The architecture must be built around realistic export constraints, not idealized conversion promises.

Typical failure or degradation zones include:

1. custom macros
2. package-specific environments
3. complex math environments
4. highly customized tables
5. float placement expectations
6. TikZ or package-heavy figure logic
7. bibliography or citation rendering differences
8. front-matter and institution-specific title pages

The workflow should not attempt to hide these issues.

Instead, it should:

- classify them
- report them
- make later profiles more specific where needed

---

## 8. Architectural Fit With Existing Repository Shape

The current repository already has a clear layered model.

`02-latex-to-word` should fit as a new outward workflow layer while preserving the current core contracts.

### Existing repository logic to preserve

- checkers write reports
- fixers read reports
- rules define policy
- runners orchestrate but do not hide lower-level meaning

### New architectural role

`02-latex-to-word` should be treated as a delivery/export workflow, not as a checker and not as a fixer.

Its place is conceptually after the current core check/fix loop:

```text
bibliography intake
-> Word-to-LaTeX migration
-> deterministic checking
-> report-driven fixing
-> LaTeX-to-Word delivery/export
```

### Important repository fit decision

The workflow should reuse:

- project discovery
- rule-pack policy
- mapping concepts already present in Word-side migration
- report generation patterns

But it should not overload existing check/fix modules with export behavior.

---

## 9. Reusable Existing Concepts

The current repository already contains concepts that should influence `02-latex-to-word`.

### 9.1 Explicit mappings

`01-word-to-latex` already uses explicit mappings instead of guessing from filenames or structure.

This should carry over into export.

### 9.2 Word style intent already exists in the repo

The repository already has `word_style_mappings` and related intake/mapping concepts.

This is a strong signal that `02-latex-to-word` should use explicit style/profile contracts rather than hidden heuristics alone.

### 9.3 Structured summary/report behavior

The repository already prefers machine-readable summaries and explicit workflow artifacts.

`02-latex-to-word` should emit the same kind of inspectable outcome.

---

## 10. Core Product Architecture

The workflow should be designed around five product components.

## Component 1: Export Profile Resolution

This component decides which export mode and policy set apply.

Examples:

- `review-friendly`
- `submission-friendly`
- later school-specific profiles

This component is where policy should live, not in hard-coded procedural logic.

## Component 2: Export Preparation

This component prepares the LaTeX project for export.

Its purpose is not to rewrite the thesis deeply, but to normalize the export boundary enough for deterministic downstream behavior.

Examples of responsibilities:

- discover the main TeX file and thesis structure
- identify chapter order
- gather bibliography context
- identify likely unsupported constructs for reporting

## Component 3: Conversion Engine

This is the Pandoc-first conversion path.

Its responsibility is not to make product decisions, but to perform the actual transformation step within the selected export profile.

## Component 4: Export Report Generation

This component translates export issues into a structured report.

The report should include at least:

- export mode used
- files involved
- warnings
- unsupported constructs
- degraded constructs
- likely manual follow-up items

## Component 5: Export Summary Artifact

This component produces the final machine-readable and human-readable outputs that make the workflow auditable.

This is essential to align the workflow with `thesis-skills` philosophy.

---

## 11. Policy vs Mechanism

This workflow should preserve the repository’s current policy/mechanism separation.

### Mechanism belongs in workflow/core logic

Examples:

- discovering source files
- invoking the conversion engine
- collecting structured findings
- writing reports and summaries

### Policy belongs in export profiles and rule-pack-level mappings

Examples:

- which mode is used
- what degree of fidelity is expected
- style mappings for headings/captions
- template-related output preferences
- institution-specific handling in later releases

This separation is important because it avoids baking school-specific output assumptions into the general export path.

---

## 12. Output Contracts

The product should define explicit outputs for every export run.

### Required outputs

1. exported `.docx`
2. machine-readable export report
3. human-readable export summary

### Optional later outputs

- intermediate normalized markdown or export staging artifacts
- template-specific reports
- submission checklist linkage

### Why this matters

The user should never need to guess whether the export was “good.”

They should be told:

- what was produced
- what succeeded
- what degraded
- what likely needs manual review

---

## 13. Relationship To Rule Packs

`02-latex-to-word` should not bypass the rule-pack system.

Instead, the product architecture should assume that rule packs can later define or extend export-related policy such as:

- heading style mappings
- front-matter expectations
- chapter role expectations
- submission-facing docx template hints

This is another reason dual-mode design is better than a single monolithic export mode.

It leaves room for:

- generic review export now
- stricter institution-aware export later

---

## 14. Naming And Positioning

The workflow should be named and positioned carefully.

### Good positioning

`02-latex-to-word` is:

- a thesis-oriented export workflow
- review-friendly first
- deterministic in orchestration
- explicit about degraded fidelity

### Bad positioning

`02-latex-to-word` is not:

- a universal LaTeX-to-Word converter
- a promise of perfect PDF-to-docx equivalence
- a guarantee that any thesis template will export cleanly without profile work

---

## 15. Release Scope

## `v0.6.x` Scope

The first release should include:

1. dual-mode architecture in product design
2. review-friendly mode as the primary implemented path
3. submission-friendly mode as an explicit future-ready contract
4. Pandoc-first conversion path
5. structured export report
6. documentation that clearly states limitations

## Out of scope for the first release

1. school-perfect final submission support across arbitrary templates
2. full custom macro preservation
3. advanced GUI template editing
4. invisible auto-fixing of all export problems
5. broad package-specific compatibility claims without evidence

---

## 16. Success Criteria

The product architecture should be considered successful if it enables a first implementation that:

1. fits the existing repository style cleanly
2. has a realistic release promise
3. preserves thesis structure in useful ways
4. produces review-usable `.docx` outputs
5. emits explicit reports about degraded fidelity
6. leaves room for stricter submission-oriented profiles later

---

## 17. Risks

### Risk 1: Overpromising fidelity

If the workflow is described too broadly, users will treat it as a universal converter and judge it against impossible expectations.

Countermeasure:

- position the first release around review-friendly export
- always emit export reports
- keep claims bounded in docs and CLI help

### Risk 2: Mixing policy and mechanism

If school-specific formatting assumptions are hard-coded into the export logic, later extension becomes brittle.

Countermeasure:

- keep profile behavior explicit
- keep future style/template mapping policy outside generic workflow code where possible

### Risk 3: Hiding degradation

If unsupported constructs silently degrade, the product becomes untrustworthy.

Countermeasure:

- report warnings explicitly
- make summary artifacts mandatory

### Risk 4: Trying to solve submission and review equally in the first release

This will make the release scope too broad and weaken both paths.

Countermeasure:

- make review-friendly the primary release mode
- define submission-friendly at the architecture level only

---

## 18. Final Product Decision

The product architecture for `02-latex-to-word` is:

> a dual-mode thesis export workflow, with review-friendly `.docx` export as the primary first-release capability and submission-friendly export as a defined but later-strengthened mode.

It should be implemented as a Pandoc-first, report-driven, explicit-contract workflow that fits the current `thesis-skills` architecture.

This is the right balance between user value, realism, and architectural continuity.

---

## 19. Recommended Next Document

The next planning artifact after this document should be:

`docs/plans/2026-04-20-latex-to-word-implementation-plan.md`

That implementation plan should define:

- exact file layout
- exact CLI surface
- export profile contract
- report schema
- tests and fixtures
- phased delivery for `v0.6.x`
