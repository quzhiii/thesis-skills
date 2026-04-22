# Pre-Submission Gate Product Architecture

## Document Positioning

This document defines the product boundary, architectural direction, and release scope for a pre-submission / readiness gate in `thesis-skills`.

It is intended to answer the following questions before implementation begins:

1. why a readiness gate should exist as a first-class workflow artifact
2. what should be aggregated into the final go/no-go decision
3. how the gate should reuse existing reports rather than replace them
4. what decision model and output contracts should exist
5. what should remain explicitly out of scope in the first release

Applicable readers:

- roadmap owner
- future implementers of the readiness gate
- reviewers validating release and workflow scope
- AI agents generating implementation plans for pre-submission checks

---

## 1. Why A Pre-Submission Gate Exists

`thesis-skills` already contains many useful workflow outputs:

- checker reports
- fixer summaries
- run summaries
- compile status planning
- export workflow planning
- review-loop planning

What is still missing is the final synthesizing artifact that answers:

> “Given everything the repository knows right now, is this thesis package ready for advisor handoff, submission, or should the user stop and fix something first?”

This matters because users do not experience the workflow as a set of isolated modules.

They experience it as a decision problem:

- can I send this to my advisor now?
- can I prepare a submission package now?
- which blockers remain?
- which issues are real blockers versus tolerable warnings?
- what must be manually reviewed before I move forward?

Without a readiness gate, users have to manually inspect multiple reports and infer their own go/no-go judgement each time.

---

## 2. Product Strategy

The readiness-gate strategy is not to build a new all-powerful orchestration engine.

The strategy is:

> build a bounded, inspectable decision layer that synthesizes existing workflow artifacts into a single submission-readiness verdict and a structured explanation of that verdict.

This keeps the gate aligned with `thesis-skills` philosophy:

- reuse existing deterministic outputs
- preserve machine-readable evidence
- make gating logic explicit
- separate decision synthesis from low-level checking/fixing logic

The gate should therefore be treated as a summarizing workflow family, not as a replacement for checkers, fixers, compile parsing, export, or review-loop workflows.

---

## 3. Core Product Decision

The readiness gate should produce a **three-level decision model**.

## PASS

The thesis package is acceptable for the chosen gate mode.

This does not mean “perfect.”

It means no configured blocker remains for the selected workflow target.

## WARN

The thesis package is usable, but meaningful risk or manual-review items remain.

This is appropriate when the package can still move forward, but the user should do so knowingly.

## BLOCK

The thesis package should not proceed for the selected gate mode because critical blockers remain.

This model is better than binary pass/fail because thesis workflows often contain non-fatal but important review risks.

---

## 4. Product Boundary

### 4.1 What the gate should do

At the product level, the gate should:

1. aggregate existing workflow artifacts
2. classify findings into readiness-relevant categories
3. emit a single decision (`PASS`, `WARN`, `BLOCK`)
4. explain why that decision was reached
5. show which workflow areas remain the highest priority

### 4.2 What the gate should not do

The gate should not claim:

- that it replaces human judgement about thesis quality
- that it can prove institutional compliance exhaustively for every school
- that it can judge scholarly merit or advisor satisfaction
- that it can substitute for all manual review
- that it should automatically fix issues merely because they are surfaced in the gate

### 4.3 First-release promise

The first release should promise only that:

- it can synthesize known structured artifacts into a readiness verdict
- it can differentiate blockers from warnings using explicit policy
- it can show users what to do next when the package is not ready

---

## 5. User Scenarios

### Scenario A: Advisor handoff gate

The user wants to know whether the current package is clean enough to send to an advisor.

### Scenario B: Submission-prep gate

The user wants to know whether the current package is safe enough to continue toward a formal submission workflow.

### Scenario C: Post-fix verification gate

The user has run fixers and wants a final aggregated verdict on whether the workflow state improved enough to proceed.

### Scenario D: Release-quality example verification

The maintainer wants a high-level readiness verdict for sample projects and example workflows.

---

## 6. Reusable Existing Repository Patterns

The repository already contains strong building blocks for a readiness gate.

### 6.1 `core/reports.py` summary model

Current reports already expose:

- checker name
- ruleset
- error / warning / info counts
- `status: PASS/FAIL`

This is the natural low-level status source for a gate.

### 6.2 `run-summary.json`

The runner already aggregates step-level state:

- exit codes
- report paths
- compile step status
- report summaries where available

This is the natural workflow-level aggregation anchor.

### 6.3 `fix-summary.json`

The fixer runner already records:

- step summaries
- applied flags
- changed files

This is a strong input for post-fix readiness evaluation.

### 6.4 Review-oriented summaries

Deep review already exposes:

- `review_digest`
- prioritized queues
- clustered review issues

This is important because readiness is not only about syntax or structure blockers; it also includes unresolved human-review risks.

### 6.5 Compile status integration

The compile step already exists conceptually in runner summaries, even when currently unavailable or skipped.

This makes compile-readiness a natural gate dimension rather than a foreign addition.

---

## 7. Borrowable External Patterns

The readiness gate should borrow patterns from systems that synthesize multiple workflow checks into an explicit decision artifact.

### 1. CI-style quality gates in deterministic engineering systems

Borrowable pattern:

- aggregate multiple signals into a single go/no-go summary while preserving drill-down evidence

Relevant implication for `thesis-skills`:

- the gate should not hide underlying reports; it should summarize them and link back to them

### 2. Release checklists and acceptance gates

Borrowable pattern:

- use explicit validation steps and named acceptance thresholds instead of implied readiness

Relevant implication:

- the gate should map structured artifacts to explicit readiness rules, not ad hoc judgement

### 3. Review-oriented workflow systems with triage summaries

Borrowable pattern:

- unresolved review-required items should influence the decision separately from raw syntax/format failures

Relevant implication:

- `WARN` should capture unresolved manual-review debt that is not a hard blocker but still matters

### 4. Ship-readiness dashboards in adjacent tooling

Borrowable pattern:

- present the final verdict with top blocking domains and next actions, not just a bare status code

Relevant implication:

- the gate artifact should include the dominant reasons for `WARN` or `BLOCK`

### 5. Deterministic pre-submit workflows

Borrowable pattern:

- keep the verdict model bounded and rule-driven, not model-opinion-driven

Relevant implication:

- the gate should be based on configured policy and current artifacts, not on vague heuristic prose

### What to avoid in a first release

- avoid claiming universal institutional compliance certification
- avoid inventing opaque scoring systems with no traceability
- avoid making the gate dependent on manual reading of raw files when structured reports already exist

---

## 8. Core Product Components

The gate should be designed around five components.

## Component 1: Artifact Collector

This component gathers the relevant structured workflow artifacts.

Examples:

- checker reports
- run summary
- fix summary
- compile summary or compile report
- export summary/report
- review-loop artifacts when present

Its purpose is collection, not interpretation.

## Component 2: Dimension Evaluator

This component evaluates readiness by domain.

Suggested readiness dimensions:

- references
- language
- format
- content
- compile
- export
- review debt

It decides the per-dimension state before the final gate verdict is produced.

## Component 3: Policy Layer

This component maps the collected states into the final verdict model.

Examples:

- when does a missing compile report mean `WARN` versus `BLOCK`?
- when do unresolved review-required items remain only `WARN`?
- what differs between advisor handoff mode and submission-prep mode?

This is where go/no-go policy belongs.

## Component 4: Verdict Builder

This component produces the final decision artifact.

At minimum it should include:

- overall verdict
- per-dimension verdicts
- top blockers
- top warnings
- suggested next actions

## Component 5: Summary Bridge

This component ensures the gate output can be surfaced consistently in:

- machine-readable gate artifacts
- CLI summaries
- later runner integrations

---

## 9. Gate Modes

The readiness gate should expose bounded modes instead of pretending there is one universal standard of “ready.”

## Mode A: Advisor-Handoff Gate

Purpose:

- determine whether the current thesis package is acceptable to send to an advisor

Characteristics:

- stronger tolerance for some non-fatal formatting imperfections
- more sensitivity to unresolved review-required issues
- review/export readiness matters more than formal template perfection

## Mode B: Submission-Prep Gate

Purpose:

- determine whether the current package is acceptable to continue toward formal submission or submission packaging

Characteristics:

- stricter on compile and format issues
- stricter on unresolved export risks
- stricter on known blockers that could invalidate a final package

The first implementation should support at least these two modes, even if the policy differences begin relatively simple.

---

## 10. Relationship To Existing Modules

The readiness gate should not replace any existing module.

It should sit above them.

### Inputs it should reuse

- checker reports
- fixer summaries
- compile parser outputs
- export reports from `02-latex-to-word`
- review-loop artifacts

### Outputs it should produce

- a unified gate artifact
- a verdict summary
- prioritized next actions

### Important architectural rule

The gate should never become a second hidden runner that re-implements the whole repository logic.

It should summarize existing artifacts and configured policy.

---

## 11. Artifact Contract

The readiness gate should emit an explicit artifact.

### Required top-level fields

- `mode`
- `overall_verdict`
- `summary`
- `dimensions`
- `blockers`
- `warnings`
- `next_actions`
- `sources`

### Why this matters

The user should never need to guess why the gate returned `WARN` or `BLOCK`.

They should be told:

- what evidence was used
- which areas failed or remain risky
- what should be fixed first

---

## 12. Human Judgement Boundaries

Human judgement remains necessary in this workflow.

The gate should help answer:

- “what is blocking?”
- “what is still risky?”
- “what should I review next?”

The gate should not answer:

- “is the thesis intellectually good enough?”
- “will the advisor definitely be satisfied?”
- “is this universally compliant with every institution’s hidden rules?”

This is important because submission readiness in academic workflows always has a human component beyond deterministic checks.

---

## 13. First-Release Scope

The first release of the readiness gate should prioritize:

1. unified artifact collection
2. per-dimension readiness evaluation
3. `PASS / WARN / BLOCK` verdicting
4. explicit blocker and warning summaries
5. bounded mode differences between advisor handoff and submission-prep

The first release should not prioritize:

1. deep scoring models
2. institution-specific gate packs beyond current starter policy
3. automatic fix triggering inside the gate itself
4. UI-heavy dashboards

---

## 14. Relationship To Review Loop And Export

The gate is downstream of both export and review workflows.

### Export contributes delivery readiness

If the thesis cannot be exported in the intended mode, that should affect gate status.

### Review loop contributes revision readiness

If there are unresolved review-required items or blocked revision artifacts, that should affect gate status.

This is why the gate belongs in `v0.7.x`, after the delivery and review foundations begin to exist.

---

## 15. Release Positioning

### `v0.7.x` gate target

The first release should focus on:

- advisor-handoff gate
- submission-prep gate
- verdict summary artifacts
- bounded per-dimension aggregation

### Later extension targets

Later releases can strengthen:

- institution-specific gate policy
- richer integration with defense-pack workflows
- stronger artifact history across revision rounds

---

## 16. Risks

### Risk 1: The gate becomes a vague “quality score” system

Countermeasure:

- use explicit verdicts and explicit reasons
- keep all decisions traceable to structured source artifacts

### Risk 2: The gate duplicates checker logic

Countermeasure:

- summarize existing evidence rather than re-running low-level analysis where not necessary

### Risk 3: The gate overclaims certainty

Countermeasure:

- preserve `WARN` as a first-class state
- keep manual-review debt visible

### Risk 4: Mode differences become arbitrary and opaque

Countermeasure:

- keep mode policy explicit and inspectable
- document why advisor handoff and submission-prep differ

---

## 17. Success Criteria

The product architecture should be considered successful if it enables a first implementation that:

1. reuses existing report and summary artifacts instead of inventing a parallel system
2. produces a clear readiness verdict with explicit rationale
3. distinguishes blockers from warnings in a useful way
4. remains honest about what deterministic checks can and cannot prove
5. fits naturally into the existing `thesis-skills` workflow story

---

## 18. Final Product Decision

The pre-submission gate in `thesis-skills` should be:

> a bounded decision layer that synthesizes existing structured workflow artifacts into a clear `PASS / WARN / BLOCK` verdict, plus an explicit explanation of what blocks progress and what should be addressed next.

It should begin with advisor-handoff and submission-prep modes, reuse current run/fix/check/report patterns, and remain a summarizing layer rather than a second hidden orchestration engine.

---

## 19. Recommended Next Document

The next planning artifact after this document should be:

`docs/plans/2026-04-20-pre-submission-gate-implementation-plan.md`

That implementation plan should define:

- exact gate module location
- artifact schema
- dimension aggregation rules
- mode policy rules
- runner or CLI entrypoint behavior
- phased rollout for `v0.7.x`
