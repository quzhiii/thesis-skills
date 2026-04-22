# Thesis Skills Upgrade Roadmap

## Document Positioning

This document defines the next full upgrade program for `thesis-skills` after the current `v0.5.2` baseline.

It is intended to serve four purposes at once:

1. align product direction for the next several releases
2. turn high-level ideas into an execution-oriented backlog
3. capture which external open-source patterns are worth borrowing
4. provide a stable planning artifact that future AI agents and developers can implement against

Applicable readers:

- repository maintainer and roadmap owner
- developers implementing the next release train
- AI agents preparing execution plans or review checklists
- contributors who want to understand what is in scope next and why

---

## Current Repository State

`thesis-skills` is already a structured academic workflow repository rather than a loose collection of scripts.

The current public shape is:

1. bibliography intake
2. Word-to-LaTeX migration
3. deterministic checking
4. report-driven fixing
5. rule-pack onboarding and reuse

This positioning is explicitly documented in:

- `README.md`
- `docs/architecture.md`
- `docs/roadmap.md`

The repository is strong in the following areas:

- Zotero and EndNote bibliography intake
- Word -> LaTeX migration
- deterministic thesis QA
- bounded fixers with report contracts
- reusable YAML rule packs
- public-facing architecture and release documentation

The most visible product gaps now are:

1. no `LaTeX -> Word` delivery path
2. no first-class advisor review loop
3. no compile-log interpretation layer
4. no defense-pack / slide-export workflow
5. no pre-submission quality gate that unifies existing checks
6. limited ecosystem/onboarding support beyond the current core workflows

---

## Product Direction

The next upgrade cycle should not turn `thesis-skills` into a general-purpose writing assistant.

The repository should continue to act as:

> a deterministic, inspectable, report-driven workflow layer for thesis and academic writing projects

That means the next stage should preserve the current design rules:

- keep workflows explicit
- keep outputs inspectable
- keep fixers bounded
- keep policy in rule packs
- avoid overstating unsupported capabilities
- prefer workflow contracts over magical behavior

The strategic shift is not “become more AI”.

The strategic shift is:

> extend the repository from a strong ingestion + checking + fixing system into a full thesis delivery and collaboration workflow.

In practice, the next roadmap should move the product from:

```text
bib intake -> Word->LaTeX -> check -> fix
```

to:

```text
bib intake -> Word->LaTeX -> check -> fix -> review/export -> defense/pre-submission
```

---

## Strategic Goals For The Upgrade Program

The full upgrade program should aim to achieve the following product outcomes:

### 1. Complete the document-delivery loop

Today the repository can ingest Word and produce or improve LaTeX workflows.
It should also support delivering thesis content back into Word-friendly formats for advisor review and submission workflows.

### 2. Add explicit review-loop support

Many thesis workflows are blocked not by writing, but by review coordination:

- advisor comments
- chapter diffs
- Word review copies
- structured feedback ingestion

This should become a first-class workflow rather than an ad hoc manual process.

### 3. Add a friendlier “last mile” around compilation and submission

Compile failures, final checks, and defense prep are still high-friction areas.
The repository should make these steps more deterministic and easier to reason about.

### 4. Strengthen external usability and ecosystem fit

The repository should become easier to adopt in real mixed environments involving:

- local LaTeX projects
- GitHub-hosted repos
- Overleaf-like collaboration patterns
- Pandoc-based export pipelines
- university-specific rule packs

---

## Upgrade Themes

The roadmap is organized into six upgrade themes.

### Theme A: Delivery Workflows

Add outward-facing export capabilities so the repository is not only an intake and QA tool, but also a delivery workflow layer.

### Theme B: Review Loops

Support thesis review between author, advisor, and external reviewers using structured export, diff, and feedback ingestion.

### Theme C: Build / Submission Reliability

Make compile errors, release readiness, and final package generation easier to interpret and verify.

### Theme D: Rule-Pack Ecosystem

Strengthen the reusability and quality controls around school- and journal-specific packs.

### Theme E: Documentation / Onboarding

Improve scenario-oriented docs and make repository adoption easier for new users.

### Theme F: Platform Integrations

Add light integration guidance and contracts for mixed environments such as local Git + Word + Overleaf + Pandoc workflows.

---

## Borrowable Patterns From External Repositories

The next roadmap should explicitly borrow good patterns from adjacent open-source projects, but only where the pattern matches `thesis-skills` philosophy.

### 1. OpenDraft

Repository signal:

- export is treated as a formal pipeline stage
- multiple final output formats are part of the product story

Borrowable pattern:

- make final delivery formats visible in the roadmap and README rather than treating export as an afterthought

### 2. academic-writing-agents

Repository signal:

- review responsibilities are split into specialized concerns
- academic review is treated as a workflow, not a single generic QA step

Borrowable pattern:

- separate consistency, technical quality, prose quality, and layout-oriented review paths in future `thesis-skills` review loops

### 3. PaperKit

Repository signal:

- workflows are packaged as staged, modular academic writing processes
- documentation is oriented around real author workflows rather than only internals

Borrowable pattern:

- add scenario-first documentation and release planning around “how a thesis actually moves” instead of only module descriptions

### 4. Open Academic Paper Machine

Repository signal:

- end-to-end academic production is represented as an explicit pipeline with audit trail

Borrowable pattern:

- formalize pre-submission and delivery workflows as named stages with clear artifacts and quality gates

### 5. Academic Pandoc Template / related Pandoc thesis templates

Repository signal:

- `docx`, `pdf`, `tex`, and other outputs are supported with explicit config files and output-specific contracts

Borrowable pattern:

- design `LaTeX -> Word` as a profile-driven export workflow with explicit limitations and configurable templates rather than a vague “conversion” promise

### 6. pypandoc / pandoc ecosystem

Repository signal:

- thin wrappers around Pandoc are often sufficient when paired with good configuration and output contracts

Borrowable pattern:

- prefer a `Pandoc-first` export path for the first `LaTeX -> Word` milestone instead of building a custom converter too early

### 7. Zettlr / academic markdown export ecosystems

Repository signal:

- users value format interoperability and output template support more than exotic editing features

Borrowable pattern:

- frame export features around stable outputs, template compatibility, and interoperability instead of promising perfect fidelity

### 8. Workflow guides from real academic writing setups

Observed pattern:

- the strongest real-world workflows combine Git, Zotero, LaTeX, and export tooling with clear operating conventions

Borrowable pattern:

- add “mixed workflow” guidance and contracts without trying to own the entire authoring environment

---

## Major Roadmap Initiatives

The following initiatives define the next upgrade program.

## Initiative 1: `02-latex-to-word`

### Why it exists

This is the highest-priority product gap.

The repository currently supports:

- bibliography intake
- Word -> LaTeX migration
- thesis checking and fixing

But many real thesis workflows still end with:

- advisor review in Word
- school submission in `.docx`
- collaboration with non-LaTeX users

### Product boundary

This should not be marketed as a universal perfect TeX converter.

It should be positioned as:

> a review-friendly and submission-friendly `LaTeX -> Word` thesis export workflow with explicit output contracts and auditable degradation reporting

### First-release target

Version target: `v0.6.x`

Expected outputs:

- `.docx` export
- export report describing degraded or unsupported constructs
- optional Word template mapping support

### Key success criteria

- chapter hierarchy preserved
- heading styles mapped predictably
- bibliography remains readable and usable
- common figures/tables survive export reasonably well
- unsupported constructs are surfaced in a report, not hidden

---

## Initiative 2: Advisor Review Loop

### Why it exists

The strongest missing workflow after export is review coordination.

The repository should support a bounded review loop such as:

```text
LaTeX thesis
-> export review copy
-> advisor comments / diff summary
-> structured feedback ingest
-> selective fixes or TODO generation
```

### Suggested components

- `03-latex-review-diff`
- `04-word-review-ingest`

### Product value

This is the feature family most likely to differentiate `thesis-skills` from generic academic-writing tools.

### Version target

- initial diff/report support: `v0.7.x`
- structured feedback ingest: later `v0.7.x` or `v0.8.x`

---

## Initiative 3: Compile Log Parser

### Why it exists

Compile failure remains one of the most painful “last mile” problems for thesis users.

Current raw logs are too hard to interpret for many users.

### Product boundary

This should be a diagnostic translator, not a compile system rewrite.

### Expected outputs

- categorized compile findings
- friendlier hints
- likely file/line/source context where available
- issue types such as:
  - missing package
  - undefined control sequence
  - bibliography mismatch
  - reference/citation failure
  - encoding problems
  - overfull/underfull box warnings

### Version target

`v0.6.x`

---

## Initiative 4: Pre-Submission Quality Gate

### Why it exists

The repository already contains many individual checkers and fixers.
It still lacks a single final quality gate that answers:

> “Is this thesis package ready for submission or advisor handoff?”

### Suggested product shape

Add a unified gate that summarizes:

- references status
- language status
- format status
- content status
- compile status
- export status

### Expected output

- `PASS / WARN / BLOCK`
- machine-readable summary
- human-readable checklist summary

### Version target

`v0.7.x`

---

## Initiative 5: Defense Pack / Slide Support

### Why it exists

Current planning docs already identify slide-deck support as a future area.

The product should support turning an almost-finished thesis into an easier defense-prep package.

### Product boundary

The first version does not need to generate a full PowerPoint deck automatically.

The first useful version can generate:

- defense outline markdown
- chapter highlights
- figure inventory for slides
- candidate tables and diagrams
- summary notes for talk preparation

### Version target

`v0.8.x`

---

## Initiative 6: Rule-Pack Linting And Pack Scorecard

### Why it exists

The repository already has a meaningful rule-pack system.

The next maturity step is to make rule-pack quality itself measurable and easier to maintain.

### Expected outputs

- pack lint checks
- completeness checks
- schema consistency checks
- pack scorecard for maintainability and portability

### Version target

`v0.8.x`

---

## Initiative 7: Scenario-Oriented Onboarding Docs

### Why it exists

Current docs are good at architecture and module documentation.
The next step is to improve scenario-driven usability.

### Recommended doc tracks

1. Word draft -> LaTeX thesis
2. LaTeX thesis -> advisor Word review copy
3. thesis finalization -> defense prep package
4. mixed workflow guide: local Git + Zotero + LaTeX + export tooling

### Version target

Start in `v0.6.x`, expand in later releases

---

## Recommended Release Train

## `v0.6.x` - Delivery Foundation

### Primary goal

Turn `thesis-skills` from a strong intake/check/fix system into a system that can also produce review-friendly outward deliverables.

### Must-have items

- `02-latex-to-word` initial release
- compile log parser
- scenario-oriented documentation refresh
- update README and architecture docs to reflect delivery workflows

### Should-have items

- export template contract
- export report contract
- example fixture coverage for export edge cases

### Must not do

- do not promise full-fidelity conversion for arbitrary LaTeX
- do not add GUI surface area
- do not overreach into full review-loop automation in the same release

---

## `v0.7.x` - Review And Readiness

### Primary goal

Add explicit advisor review loops and final thesis readiness signaling.

### Must-have items

- review diff workflow
- pre-submission quality gate
- first structured review feedback ingestion path

### Should-have items

- richer final summary artifacts
- chapter-level change summaries
- review TODO generation

### Must not do

- do not collapse review features into unconstrained editing
- do not auto-apply ambiguous advisor feedback by default

---

## `v0.8.x` - Defense And Ecosystem Hardening

### Primary goal

Support final-mile thesis packaging and make the repository easier to extend and adopt.

### Must-have items

- defense-pack generation
- rule-pack linting
- rule-pack scorecard

### Should-have items

- mixed workflow integration guidance
- stronger examples for non-Tsinghua real-world setups
- more explicit extension contracts

---

## `v1.0.0` - Stable Delivery And Extension Story

### Primary goal

Ship a stable public story covering:

- intake
- migration
- checking
- fixing
- delivery/export
- review readiness
- extension contracts

### Acceptance direction

The repository should be ready to present itself as a complete thesis workflow layer rather than a partially-connected toolkit.

---

## Priority Matrix

| Initiative | User Value | Strategic Value | Implementation Risk | Recommended Priority |
|---|---:|---:|---:|---|
| `02-latex-to-word` | High | High | Medium | P0 |
| Compile log parser | High | High | Low-Medium | P0 |
| Advisor review loop | High | High | Medium | P1 |
| Pre-submission quality gate | High | High | Low-Medium | P1 |
| Scenario docs refresh | Medium | High | Low | P1 |
| Defense pack | Medium | Medium | Medium | P2 |
| Rule-pack lint/scorecard | Medium | Medium | Medium | P2 |
| Mixed workflow integration docs | Medium | Medium | Low | P2 |

---

## Non-Negotiable Design Rules For The Upgrade Program

1. Do not break the current deterministic/report-driven core.
2. Do not turn export or review workflows into opaque magic.
3. Do not overstate conversion fidelity.
4. Do not merge safe fix and review-oriented fix concepts.
5. Do not hard-code school-specific policy into general workflows.
6. Do not introduce heavyweight dependencies unless they materially improve the workflow.
7. Do not widen product scope unless the previous release gate is satisfied.

---

## Cross-Release Acceptance Gates

Each release in this roadmap should only be considered complete when all of the following are true:

1. docs, manifest, and actual code paths match
2. the repository does not claim support that does not exist
3. test fixtures cover the new workflow boundary
4. output artifacts are inspectable and reproducible
5. README positioning still matches the actual repository philosophy

---

## Upgrade Backlog And Todo List

The following backlog is organized as execution-oriented batches.

## Batch A - Planning And Contracts (Start Immediately)

- [ ] finalize `02-latex-to-word` product boundary and README wording
- [ ] define export contract: inputs, outputs, report shape, template behavior
- [ ] define compile-log parser scope and supported finding categories
- [ ] define pre-submission gate contract and summary schema
- [ ] define what review-loop artifacts will exist in `v0.7.x`

## Batch B - `v0.6.x` Delivery Foundation

- [ ] create `02-latex-to-word/` module scaffold
- [ ] add `THESIS_LATEX_TO_WORD.md`
- [ ] add initial CLI entrypoint and dry-run/export-report behavior
- [ ] integrate Pandoc-first export path
- [ ] add degraded-construct reporting
- [ ] add export-oriented fixtures and regression tests
- [ ] implement compile-log parser module
- [ ] add compile-log parsing tests with representative error fixtures
- [ ] update `README.md`, `README.zh-CN.md`, `docs/architecture.md`, and `docs/roadmap.md`
- [ ] add scenario docs for review/export workflows

## Batch C - `v0.7.x` Review And Readiness

- [ ] create review diff workflow scaffold
- [ ] define diff summary artifact structure
- [ ] add chapter-level or section-level review summaries
- [ ] design Word review ingest contract
- [ ] implement first review feedback parser / importer
- [ ] add pre-submission quality gate runner
- [ ] generate final `PASS / WARN / BLOCK` summaries
- [ ] add tests for review-loop artifacts and readiness summaries

## Batch D - `v0.8.x` Defense And Ecosystem

- [ ] create defense-pack workflow scaffold
- [ ] generate defense-outline artifact
- [ ] generate slide-candidate figure inventory
- [ ] add rule-pack linting tool
- [ ] add pack scorecard output
- [ ] add docs for mixed local / Git / export workflows
- [ ] expand example packs and example projects

## Batch E - `v1.0.0` Stabilization

- [ ] review naming consistency across all workflows
- [ ] align manifest, roadmap, README, and architecture docs
- [ ] harden extension contracts for third-party packs
- [ ] review version boundaries and remove stale roadmap claims
- [ ] confirm the repository tells a stable end-to-end story

---

## Suggested Execution Order

If only one next track is chosen, do this first:

1. `02-latex-to-word`

If two tracks are chosen, do this:

1. `02-latex-to-word`
2. compile log parser

If three tracks are chosen, do this:

1. `02-latex-to-word`
2. compile log parser
3. review loop foundation

This order preserves a clean release narrative:

```text
first add delivery
then add diagnostics
then add review and final readiness
```

---

## Risks And Countermeasures

### Risk 1: `LaTeX -> Word` is oversold

Countermeasure:

- explicitly position it as thesis-oriented export with bounded guarantees
- always emit an export report for degraded constructs

### Risk 2: roadmap becomes too broad

Countermeasure:

- keep each release theme narrow
- refuse to mix delivery, review, defense, and ecosystem hardening into one release unless gates are met

### Risk 3: review features become unbounded editing features

Countermeasure:

- keep review artifacts explicit
- keep ingestion separate from apply
- keep ambiguous feedback in TODO/report form first

### Risk 4: ecosystem work outruns core workflow quality

Countermeasure:

- prioritize direct user-value workflow gaps before ecosystem polish

---

## Recommended Next Planning Artifacts

After this roadmap, the next planning documents should be created in this order:

1. `2026-04-20-latex-to-word-product-architecture.md`
2. `2026-04-20-latex-to-word-implementation-plan.md`
3. `2026-04-20-compile-log-parser-implementation-plan.md`
4. `2026-04-20-review-loop-product-architecture.md`

These documents should follow the existing repository pattern:

- product/architecture document first
- execution/implementation plan second
- release-facing roadmap updates after architecture is locked

---

## Final Recommendation

The next full upgrade cycle should be anchored around this statement:

> `thesis-skills` should evolve from a deterministic thesis QA toolkit into a deterministic thesis delivery and review workflow system.

That evolution should start with `LaTeX -> Word`, continue through compile/readiness support, and then expand into advisor review and defense workflows.

This keeps the repository’s strongest qualities intact while solving the most obvious remaining user-facing workflow gaps.
