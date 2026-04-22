# Review Loop Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a bounded review-loop workflow family to `thesis-skills` that produces review-diff artifacts, triage summaries, normalized feedback-ingest artifacts, TODOs, candidate patches, and revision summaries without collapsing into an unconstrained collaboration platform.

**Architecture:** Implement this as a staged workflow family rather than a single monolithic command. Phase 0 adds module registration and artifact contracts. Phase 1 introduces `03-latex-review-diff` for review package generation and triage. Phase 2 introduces `04-word-review-ingest` for bounded feedback normalization. Phase 3 adds selective-revision integration on top of existing patch/fixer patterns. Phase 4 strengthens runner summaries and review-round traceability.

**Tech Stack:** Python 3.10+, stdlib, existing `core/reports.py`, existing `core/patches.py`, existing fixer/report summary patterns, JSON artifact contracts, `pytest`, existing runner summary conventions.

---

## 0. Scope Lock

### 0.1 First-Release Boundary

The first review-loop release should ship:

- a `03-latex-review-diff` workflow
- a `04-word-review-ingest` workflow with bounded input contracts
- triage artifacts based on existing review queue/cluster patterns
- TODO-oriented and candidate-patch-oriented selective action outputs
- revision summary artifacts that preserve review-round outcomes

It should **not** ship:

- full live collaboration support
- arbitrary freeform comment understanding with perfect semantic accuracy
- automatic application of ambiguous advisor intent
- direct replacement of Word/Overleaf/Google Docs collaboration environments

### 0.2 Locked Product Decision

Implementation must follow the already-approved review-loop architecture:

- **Stage A:** review diff and triage
- **Stage B:** feedback ingest and selective action

The implementation must keep high-judgement changes review-gated.

---

## 1. Acceptance Criteria

The implementation is only accepted when all of the following are true:

1. the repo contains new review-loop modules with numbered workflow directories
2. review-diff mode creates explicit review package and triage artifacts
3. feedback-ingest mode normalizes bounded feedback into structured issue items
4. selective-action outputs distinguish TODO items, candidate patches, and blocked/ambiguous items
5. revision summary artifacts record review-round outcomes in machine-readable form
6. runner or workflow-level summaries remain inspectable and consistent with existing repository patterns

### 1.1 Non-Negotiable Guardrails

- Do not auto-apply ambiguous feedback.
- Do not collapse review-loop behavior into existing safe fixers.
- Do not let feedback-ingest silently rewrite source files.
- Do not replace raw review artifacts with only high-level summaries.
- Do not market the system as a generic academic collaboration platform.

---

## 2. Implementation Anchors

### Create

- `03-latex-review-diff/THESIS_REVIEW_DIFF.md`
- `03-latex-review-diff/review_diff.py`
- `04-word-review-ingest/THESIS_WORD_REVIEW_INGEST.md`
- `04-word-review-ingest/feedback_ingest.py`
- `core/review_loop.py`
- `core/review_queue.py`
- `core/review_clusters.py`
- `tests/test_review_loop.py`
- `tests/test_review_diff.py`
- `tests/test_feedback_ingest.py`
- `tests/data/review_loop/README.md`
- bounded fixture files under `tests/data/review_loop/`

### Modify

- `core/reports.py`
- `core/patches.py`
- `core/fixers.py`
- `run_fix_cycle.py`
- `tests/test_patch_preview.py`
- `tests/test_fixers.py`
- `tests/test_runner.py`
- `skills-manifest.json`
- `README.md`
- `README.zh-CN.md`
- `docs/architecture.md`
- `docs/roadmap.md`

### Optional Create

- `tests/test_review_artifacts.py`

Only add additional artifact-specific tests if they improve clarity around JSON schema contracts.

---

## 3. Phase Order

### Phase 0: Module and Artifact Contract Setup

Purpose:

- register the new review workflows
- define artifact families and minimal JSON schemas
- align docs and wording

### Phase 1: Review-Diff and Triage

Purpose:

- create review packages
- produce triage summaries, queues, and clusters
- build the safe first stage of the workflow family

### Phase 2: Feedback-Ingest Normalization

Purpose:

- normalize bounded feedback inputs into machine-readable issue items
- mark ambiguity explicitly

### Phase 3: Selective Action Integration

Purpose:

- transform structured feedback into TODOs and candidate patches using existing patch/fixer patterns

### Phase 4: Revision Summary and Runner Integration

Purpose:

- summarize review-round outcomes and connect them to existing runner/fix summary conventions

---

## 4. Phase 0: Module and Artifact Contract Setup

### Goal

Make the review-loop workflow family visible in the repository and lock the artifact contracts before behavior expands.

### Files

- Create: `03-latex-review-diff/THESIS_REVIEW_DIFF.md`
- Create: `03-latex-review-diff/review_diff.py`
- Create: `04-word-review-ingest/THESIS_WORD_REVIEW_INGEST.md`
- Create: `04-word-review-ingest/feedback_ingest.py`
- Modify: `skills-manifest.json`
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `docs/architecture.md`
- Modify: `docs/roadmap.md`

### Task 0.1: Register Review Workflow Modules

**Files:**
- Modify: `skills-manifest.json`

**Step 1: Write the failing manifest test**

Assert the manifest contains:

- `03-latex-review-diff` as a workflow with entry and runner
- `04-word-review-ingest` as a workflow with entry and runner

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_runner.py -q
```

Expected: FAIL because the review-loop modules are not yet registered.

**Step 3: Update manifest**

Add both module entries following existing workflow registration patterns.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_runner.py -q
```

Expected: PASS for the manifest assertions.

**Step 5: Commit**

```bash
git add skills-manifest.json tests/test_runner.py
git commit -m "feat: register review loop workflow modules"
```

### Task 0.2: Add Workflow Doc Skeletons

**Files:**
- Create: `03-latex-review-diff/THESIS_REVIEW_DIFF.md`
- Create: `04-word-review-ingest/THESIS_WORD_REVIEW_INGEST.md`

**Step 1: Write the doc skeletons**

Document at least:

- purpose
- workflow boundary
- relationship between diff/triage and ingest/action
- first-release limits

**Step 2: Manual verification**

Ensure wording stays bounded and does not claim universal comment understanding or real-time collaboration.

**Step 3: Commit**

```bash
git add 03-latex-review-diff/THESIS_REVIEW_DIFF.md 04-word-review-ingest/THESIS_WORD_REVIEW_INGEST.md
git commit -m "docs: add review loop workflow entries"
```

### Task 0.3: Define Artifact Families And Minimal JSON Contracts

**Files:**
- Modify: `core/reports.py`
- Create: `tests/test_review_loop.py`

**Step 1: Write the failing artifact-shape test**

Define minimal required artifact families:

- review package artifact
- triage artifact
- feedback-ingest artifact
- selective-action artifact
- revision summary artifact

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_review_loop.py -q
```

Expected: FAIL because artifact-specific helpers do not exist yet.

**Step 3: Write minimal artifact helpers**

Extend or wrap `core/reports.py` so review-loop workflows can produce structured JSON with explicit artifact type, summary, and payload sections.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_review_loop.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add core/reports.py tests/test_review_loop.py
git commit -m "feat: define review loop artifact contracts"
```

### Phase 0 Acceptance Criteria

Phase 0 is accepted only when:

1. review-loop modules exist in docs and manifest
2. artifact families are explicitly defined
3. public wording remains bounded and honest

---

## 5. Phase 1: Review-Diff and Triage

### Goal

Implement the safe first stage of the review loop: create review packages and triage summaries from existing thesis state and report artifacts.

### Files

- Create: `03-latex-review-diff/review_diff.py`
- Create: `core/review_queue.py`
- Create: `core/review_clusters.py`
- Create: `tests/test_review_diff.py`
- Modify: `core/reports.py`

### Task 1.1: Build Review Package Generation

**Files:**
- Create: `03-latex-review-diff/review_diff.py`
- Create: `tests/test_review_diff.py`

**Step 1: Write the failing review-package test**

Assert that review-diff can produce a review package artifact containing at least:

- revision identifier or timestamp
- project root
- changed scope or source set
- report references used to build the package

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_review_diff.py -q
```

Expected: FAIL because the review-diff module does not exist.

**Step 3: Write minimal implementation**

Create a review-diff entrypoint that builds a machine-readable review package without applying changes.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_review_diff.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add 03-latex-review-diff/review_diff.py tests/test_review_diff.py
git commit -m "feat: add review package generation workflow"
```

### Task 1.2: Add Review Queue Logic

**Files:**
- Create: `core/review_queue.py`
- Modify: `tests/test_review_diff.py`

**Step 1: Write the failing review-queue test**

Assert that issue items can be prioritized into a review queue using explicit fields such as:

- severity / priority
- review_required
- category
- confidence

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_review_diff.py -q
```

Expected: FAIL because queue logic does not exist.

**Step 3: Write minimal implementation**

Use existing deep-language review patterns as the starting model. Keep ordering deterministic.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_review_diff.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add core/review_queue.py tests/test_review_diff.py
git commit -m "feat: add prioritized review queue logic"
```

### Task 1.3: Add Review Cluster Logic

**Files:**
- Create: `core/review_clusters.py`
- Modify: `tests/test_review_diff.py`

**Step 1: Write the failing clustering test**

Assert that related issue items can be grouped into repeatable issue families with fields like:

- category
- affected files count
- recommended_action
- review_focus

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_review_diff.py -q
```

Expected: FAIL because clustering logic is missing.

**Step 3: Write minimal implementation**

Build conservative clustering by issue class and file scope. Avoid overclaiming semantic equivalence.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_review_diff.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add core/review_clusters.py tests/test_review_diff.py
git commit -m "feat: add review cluster summaries"
```

### Task 1.4: Emit Triage Artifact

**Files:**
- Modify: `03-latex-review-diff/review_diff.py`
- Modify: `core/reports.py`
- Modify: `tests/test_review_diff.py`

**Step 1: Write the failing triage-artifact test**

Assert that the review-diff workflow emits:

- `review_queue`
- `review_clusters`
- `review_digest`

in a review-loop artifact, not just raw findings.

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_review_diff.py -q
```

Expected: FAIL because the triage artifact is incomplete.

**Step 3: Write minimal implementation**

Emit a structured triage artifact that follows the style of deep-language review payloads, while staying workflow-oriented rather than checker-oriented.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_review_diff.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add 03-latex-review-diff/review_diff.py core/reports.py tests/test_review_diff.py
git commit -m "feat: emit review triage artifacts"
```

### Phase 1 Acceptance Criteria

Phase 1 is accepted only when:

1. review packages exist as explicit artifacts
2. triage outputs are prioritized and clustered
3. the workflow is useful without any feedback-ingest support yet

---

## 6. Phase 2: Feedback-Ingest Normalization

### Goal

Normalize bounded feedback inputs into structured issue items while preserving ambiguity and review-required status explicitly.

### Files

- Create: `04-word-review-ingest/feedback_ingest.py`
- Create: `tests/test_feedback_ingest.py`
- Create: `tests/data/review_loop/README.md`
- Create: bounded fixture files under `tests/data/review_loop/`
- Modify: `core/reports.py`

### Task 2.1: Build Feedback Fixture Corpus

**Files:**
- Create: `tests/data/review_loop/README.md`
- Create: fixture files under `tests/data/review_loop/`

**Step 1: Write the failing fixture test**

Add fixtures for bounded feedback inputs such as:

- structured comment export mock
- normalized notes list
- ambiguous freeform case

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_feedback_ingest.py -q
```

Expected: FAIL because fixtures do not yet exist.

**Step 3: Add fixtures**

Keep them bounded and explicit. Prefer artifact-like inputs over loose natural-language blobs.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_feedback_ingest.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add tests/data/review_loop tests/test_feedback_ingest.py
git commit -m "test: add review loop feedback fixture corpus"
```

### Task 2.2: Add Feedback-Ingest Entry Point

**Files:**
- Create: `04-word-review-ingest/feedback_ingest.py`
- Modify: `tests/test_feedback_ingest.py`

**Step 1: Write the failing entrypoint test**

Assert that the new workflow can read a bounded feedback input and emit structured JSON.

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_feedback_ingest.py -q
```

Expected: FAIL because the entrypoint does not exist.

**Step 3: Write minimal implementation**

Build a parser that emits normalized feedback items with fields such as:

- source_ref
- text
- category
- confidence
- ambiguous
- review_required

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_feedback_ingest.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add 04-word-review-ingest/feedback_ingest.py tests/test_feedback_ingest.py
git commit -m "feat: add feedback-ingest normalization workflow"
```

### Task 2.3: Preserve Ambiguity Explicitly

**Files:**
- Modify: `04-word-review-ingest/feedback_ingest.py`
- Modify: `tests/test_feedback_ingest.py`

**Step 1: Write the failing ambiguity test**

Assert that under-specified or conflicting feedback is marked as ambiguous instead of forced into fake certainty.

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_feedback_ingest.py -q
```

Expected: FAIL because ambiguity handling is insufficient.

**Step 3: Write minimal implementation**

Mark such items with explicit ambiguity fields and `review_required=true` by default.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_feedback_ingest.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add 04-word-review-ingest/feedback_ingest.py tests/test_feedback_ingest.py
git commit -m "feat: preserve ambiguity in review feedback normalization"
```

### Phase 2 Acceptance Criteria

Phase 2 is accepted only when:

1. bounded feedback inputs become structured issue artifacts
2. ambiguity is preserved explicitly
3. no source files are modified by ingest workflows

---

## 7. Phase 3: Selective Action Integration

### Goal

Convert structured feedback into TODOs and candidate patches using existing patch-preview and fixer patterns, while keeping ambiguous items gated.

### Files

- Create: `core/review_loop.py`
- Modify: `core/patches.py`
- Modify: `core/fixers.py`
- Modify: `tests/test_patch_preview.py`
- Modify: `tests/test_fixers.py`
- Modify: `tests/test_review_loop.py`

### Task 3.1: Add TODO / Candidate Patch Split

**Files:**
- Create: `core/review_loop.py`
- Modify: `tests/test_review_loop.py`

**Step 1: Write the failing selective-action test**

Assert that normalized feedback items are split into:

- TODO items
- candidate patches
- blocked items

based on confidence, ambiguity, and review_required rules.

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_review_loop.py -q
```

Expected: FAIL because selective-action orchestration does not exist.

**Step 3: Write minimal implementation**

Implement conservative rules:

- ambiguous -> blocked or TODO
- review_required -> TODO or blocked
- bounded, high-confidence text-local issues -> candidate patch

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_review_loop.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add core/review_loop.py tests/test_review_loop.py
git commit -m "feat: split review feedback into todos and candidate patches"
```

### Task 3.2: Reuse Patch Preview Safely

**Files:**
- Modify: `core/patches.py`
- Modify: `tests/test_patch_preview.py`

**Step 1: Write the failing review-patch test**

Assert that review-driven candidate patches still use:

- `old_text` validation
- conflict detection
- `review_required` visibility

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_patch_preview.py -q
```

Expected: FAIL because review-loop patch adaptation is missing.

**Step 3: Write minimal implementation**

Extend patch-building support only where needed so review-driven candidate patches remain compatible with the current patch model.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_patch_preview.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add core/patches.py tests/test_patch_preview.py
git commit -m "feat: adapt patch preview support for review-loop candidate patches"
```

### Task 3.3: Add Selective Revision Support To Fixer Layer

**Files:**
- Modify: `core/fixers.py`
- Modify: `run_fix_cycle.py`
- Modify: `tests/test_fixers.py`

**Step 1: Write the failing selective-revision test**

Assert that review-derived candidate patches can be previewed and optionally applied through a bounded revision mode.

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_fixers.py -q
```

Expected: FAIL because selective revision mode does not exist.

**Step 3: Write minimal implementation**

Add a bounded path to process review-derived candidate patches while keeping ambiguous items out of apply by default.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_fixers.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add core/fixers.py run_fix_cycle.py tests/test_fixers.py
git commit -m "feat: add selective revision support for review loop"
```

### Phase 3 Acceptance Criteria

Phase 3 is accepted only when:

1. feedback can become TODOs and candidate patches
2. patch preview safety guarantees still hold
3. ambiguous items remain blocked from silent apply

---

## 8. Phase 4: Revision Summary and Runner Integration

### Goal

Record what happened in a review round and expose it through summary artifacts aligned with existing runner/fix summary conventions.

### Files

- Modify: `run_fix_cycle.py`
- Modify: `tests/test_runner.py`
- Modify: `tests/test_review_loop.py`
- Optional create: `tests/test_review_artifacts.py`

### Task 4.1: Emit Revision Summary Artifact

**Files:**
- Modify: `run_fix_cycle.py`
- Modify: `tests/test_review_loop.py`

**Step 1: Write the failing revision-summary test**

Assert that a review round records:

- accepted items count
- pending items count
- blocked items count
- touched files
- review-required leftovers

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_review_loop.py -q
```

Expected: FAIL because revision summary artifacts are incomplete.

**Step 3: Write minimal implementation**

Extend workflow summary generation so review-loop actions are represented alongside existing fix-summary conventions.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_review_loop.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add run_fix_cycle.py tests/test_review_loop.py
git commit -m "feat: emit revision summary artifacts for review rounds"
```

### Task 4.2: Extend Runner Summary Expectations

**Files:**
- Modify: `tests/test_runner.py`
- Optional modify: `run_fix_cycle.py`

**Step 1: Write the failing runner-summary test**

Assert that review-loop-related summaries can be surfaced without breaking the current structure of `run-summary.json` or `fix-summary.json` expectations.

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_runner.py -q
```

Expected: FAIL because review-loop summary coverage is absent.

**Step 3: Write minimal implementation**

Expose review-loop outcomes through consistent summary fields. Keep the current runner structure stable.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_runner.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add run_fix_cycle.py tests/test_runner.py
git commit -m "test: align runner summaries with review loop workflows"
```

### Phase 4 Acceptance Criteria

Phase 4 is accepted only when:

1. review-round outcomes are summarized explicitly
2. summary artifacts remain consistent with repository conventions
3. the review-loop workflow can be traced round by round

---

## 9. Suggested Test Matrix

At minimum, the implementation should cover these categories.

### Module / Workflow Presence

- manifest registration
- workflow entrypoint existence
- JSON output shape stability

### Review-Diff

- review package generation
- triage queue ordering
- cluster generation
- review digest presence

### Feedback-Ingest

- bounded feedback normalization
- ambiguity preservation
- no source mutation

### Selective Action

- TODO / candidate patch split
- patch preview compatibility
- review_required gating

### Revision Summary

- accepted / pending / blocked counts
- touched file tracking
- review-round summary persistence

---

## 10. Risks And Countermeasures

### Risk 1: Review-loop scope becomes too broad

Countermeasure:

- ship review-diff and triage first
- keep ingest bounded
- keep selective action conservative

### Risk 2: Feedback normalization pretends to understand too much

Countermeasure:

- preserve ambiguity explicitly
- default to TODO or blocked rather than fake certainty

### Risk 3: Patch generation weakens current patch safety model

Countermeasure:

- reuse `TextPatch` model
- keep old-text validation and conflict detection mandatory

### Risk 4: Summary artifacts become inconsistent with the rest of the repo

Countermeasure:

- extend existing report and fix-summary conventions instead of inventing separate summary worlds

---

## 11. Final Execution Guidance

Implement this plan in order.

Do not skip directly to patch application before triage and bounded feedback normalization exist.
Do not allow ambiguous advisor comments to become silent source edits.
Do not let the workflow become a vague collaboration layer with no explicit artifacts.

The first successful version should already help authors handle real review rounds more systematically, even if it stays conservative.

---

## 12. Next Artifact After This Plan

After this plan, the next useful planning artifact would likely be either:

1. `docs/plans/2026-04-20-pre-submission-gate-product-architecture.md`
2. or a direct execution session against `latex-to-word-implementation-plan.md`

depending on whether the next priority is more planning or starting implementation.
