# Pre-Submission Gate Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a bounded pre-submission / readiness gate to `thesis-skills` that aggregates existing structured workflow artifacts into a clear `PASS / WARN / BLOCK` verdict with explicit blockers, warnings, per-dimension status, and next actions.

**Architecture:** Implement this as a summarizing workflow layer rather than a new hidden orchestration engine. Phase 0 sets up the module, verdict model, and artifact contract. Phase 1 adds artifact collection and per-dimension evaluation. Phase 2 introduces gate modes (`advisor-handoff`, `submission-prep`). Phase 3 integrates the gate into existing workflow summaries and public docs. The gate must reuse current check/fix/compile/export/review artifacts instead of re-implementing lower-level analysis.

**Tech Stack:** Python 3.10+, stdlib, existing `core/reports.py`, existing checker/fixer report JSON contracts, `run_check_once.py`, `run_fix_cycle.py`, existing runner summary conventions, `pytest`.

---

## 0. Scope Lock

### 0.1 First-Release Boundary

The first release of the readiness gate should ship:

- a new gate workflow/module
- a machine-readable gate artifact
- `PASS / WARN / BLOCK` verdicting
- per-dimension readiness evaluation
- at least two gate modes:
  - `advisor-handoff`
  - `submission-prep`

It should **not** ship:

- a universal institution-compliance certification engine
- automatic fixing during gate evaluation
- hidden re-execution of the whole repository in a new orchestration layer
- opaque scores with no traceability back to source artifacts

### 0.2 Locked Product Decision

Implementation must follow the approved product architecture:

- summarize existing artifacts
- keep mode policy explicit
- preserve a three-level verdict model
- remain downstream of compile/export/review workflows rather than replacing them

---

## 1. Acceptance Criteria

The implementation is only accepted when all of the following are true:

1. the repo contains a gate workflow/module with a stable artifact contract
2. the gate can aggregate structured checker/fixer/runner artifacts
3. the gate returns `PASS`, `WARN`, or `BLOCK` with explicit reasons
4. the gate exposes per-dimension verdicts and prioritized next actions
5. the difference between `advisor-handoff` and `submission-prep` is represented explicitly in policy
6. the gate remains a summarizing layer and does not silently re-implement low-level checks

### 1.1 Non-Negotiable Guardrails

- Do not auto-fix issues inside the gate.
- Do not treat missing evidence as if it were equivalent to a passing state.
- Do not hide underlying source reports.
- Do not introduce an opaque numeric quality score as the primary result.
- Do not overclaim institutional compliance.

---

## 2. Implementation Anchors

### Create

- `16-check-readiness/THESIS_CHECK_READINESS.md`
- `16-check-readiness/check_readiness.py`
- `core/readiness_gate.py`
- `tests/test_readiness_gate.py`
- `tests/test_readiness_modes.py`
- `tests/data/readiness_gate/README.md`
- optional fixture artifacts under `tests/data/readiness_gate/`

### Modify

- `core/reports.py`
- `run_check_once.py`
- `run_fix_cycle.py`
- `tests/test_runner.py`
- `skills-manifest.json`
- `README.md`
- `README.zh-CN.md`
- `docs/architecture.md`
- `docs/roadmap.md`

### Possible Optional Create

- `core/readiness_policy.py`

Create `core/readiness_policy.py` only if mode policy becomes materially clearer when separated from artifact collection logic.

---

## 3. Phase Order

### Phase 0: Module and Verdict Contract Setup

Purpose:

- register the readiness gate module
- define the gate artifact schema
- lock the verdict model and wording

### Phase 1: Artifact Collection and Per-Dimension Evaluation

Purpose:

- collect existing workflow artifacts
- compute readiness by dimension

### Phase 2: Gate Mode Policy

Purpose:

- add explicit policy differences between `advisor-handoff` and `submission-prep`

### Phase 3: Runner / Summary / Documentation Integration

Purpose:

- surface the gate consistently in CLI usage and repo docs

---

## 4. Phase 0: Module and Verdict Contract Setup

### Goal

Create the gate module, make it visible in the repository, and define the artifact contract before aggregation logic expands.

### Files

- Create: `16-check-readiness/THESIS_CHECK_READINESS.md`
- Create: `16-check-readiness/check_readiness.py`
- Create: `core/readiness_gate.py`
- Modify: `skills-manifest.json`
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `docs/architecture.md`
- Modify: `docs/roadmap.md`

### Task 0.1: Register The Readiness Gate Module

**Files:**
- Modify: `skills-manifest.json`

**Step 1: Write the failing manifest test**

Assert the manifest contains a new gate/checker-style entry for `16-check-readiness` with:

- `id`
- `entry`
- `type`
- `runner`

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_runner.py -q
```

Expected: FAIL because the readiness gate is not yet registered.

**Step 3: Update manifest**

Add the module entry following the repo’s numbered workflow/checker conventions.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_runner.py -q
```

Expected: PASS for the manifest assertion.

**Step 5: Commit**

```bash
git add skills-manifest.json tests/test_runner.py
git commit -m "feat: register readiness gate module"
```

### Task 0.2: Add Gate Doc Skeleton

**Files:**
- Create: `16-check-readiness/THESIS_CHECK_READINESS.md`

**Step 1: Write the workflow doc**

Document at least:

- gate purpose
- `PASS / WARN / BLOCK` model
- relationship to existing reports
- two gate modes
- first-release limits

**Step 2: Manual verification**

Ensure wording does not imply perfect compliance certification.

**Step 3: Commit**

```bash
git add 16-check-readiness/THESIS_CHECK_READINESS.md
git commit -m "docs: add readiness gate workflow entry"
```

### Task 0.3: Define Gate Artifact Contract

**Files:**
- Create: `core/readiness_gate.py`
- Create: `tests/test_readiness_gate.py`

**Step 1: Write the failing artifact-shape test**

Assert the gate artifact contains at least:

- `mode`
- `overall_verdict`
- `summary`
- `dimensions`
- `blockers`
- `warnings`
- `next_actions`
- `sources`

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_readiness_gate.py -q
```

Expected: FAIL because the gate artifact builder does not exist.

**Step 3: Write minimal implementation**

Add a minimal artifact builder in `core/readiness_gate.py` that produces the contract shape without full logic yet.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_readiness_gate.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add core/readiness_gate.py tests/test_readiness_gate.py
git commit -m "feat: define readiness gate artifact contract"
```

### Phase 0 Acceptance Criteria

Phase 0 is accepted only when:

1. the gate is visible in docs and manifest
2. the verdict model is explicit
3. the artifact schema exists and is tested

---

## 5. Phase 1: Artifact Collection and Per-Dimension Evaluation

### Goal

Collect existing workflow artifacts and translate them into explicit readiness dimensions.

### Files

- Modify: `core/readiness_gate.py`
- Modify: `core/reports.py`
- Create or extend: `tests/data/readiness_gate/README.md`
- Modify: `tests/test_readiness_gate.py`

### Task 1.1: Collect Existing Workflow Artifacts

**Files:**
- Modify: `core/readiness_gate.py`
- Modify: `tests/test_readiness_gate.py`

**Step 1: Write the failing artifact-collector test**

Assert that the gate can locate and read:

- checker reports
- `run-summary.json`
- `fix-summary.json`
- compile report/summary if present
- export/report artifacts if present
- review-loop artifacts if present

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_readiness_gate.py -q
```

Expected: FAIL because artifact collection is incomplete.

**Step 3: Write minimal implementation**

Add a collector that reads known artifact locations conservatively and records what evidence was actually found.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_readiness_gate.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add core/readiness_gate.py tests/test_readiness_gate.py
git commit -m "feat: collect readiness evidence from workflow artifacts"
```

### Task 1.2: Define Readiness Dimensions

**Files:**
- Modify: `core/readiness_gate.py`
- Modify: `tests/test_readiness_gate.py`

**Step 1: Write the failing dimension-evaluation test**

Assert that the gate emits per-dimension entries for at least:

- references
- language
- format
- content
- compile
- export
- review_debt

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_readiness_gate.py -q
```

Expected: FAIL because dimension evaluation is not yet implemented.

**Step 3: Write minimal implementation**

Map source artifacts into dimension states without inventing unsupported evidence.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_readiness_gate.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add core/readiness_gate.py tests/test_readiness_gate.py
git commit -m "feat: add per-dimension readiness evaluation"
```

### Task 1.3: Emit Next Actions And Source References

**Files:**
- Modify: `core/readiness_gate.py`
- Modify: `tests/test_readiness_gate.py`

**Step 1: Write the failing guidance test**

Assert that the gate includes:

- top blockers
- top warnings
- next actions
- source artifact references

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_readiness_gate.py -q
```

Expected: FAIL because explanation fields are incomplete.

**Step 3: Write minimal implementation**

Add deterministic next-action generation from the strongest unresolved dimensions and available source reports.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_readiness_gate.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add core/readiness_gate.py tests/test_readiness_gate.py
git commit -m "feat: explain readiness verdicts with next actions and sources"
```

### Phase 1 Acceptance Criteria

Phase 1 is accepted only when:

1. the gate collects real workflow evidence
2. readiness is evaluated per dimension
3. the artifact explains its verdict and evidence sources

---

## 6. Phase 2: Gate Mode Policy

### Goal

Differentiate `advisor-handoff` and `submission-prep` without making the policy arbitrary or opaque.

### Files

- Modify: `core/readiness_gate.py`
- Optional create: `core/readiness_policy.py`
- Create: `tests/test_readiness_modes.py`

### Task 2.1: Add Mode Resolution

**Files:**
- Modify: `core/readiness_gate.py`
- Create: `tests/test_readiness_modes.py`

**Step 1: Write the failing mode-resolution test**

Assert that the gate accepts at least:

- `advisor-handoff`
- `submission-prep`

and rejects unknown modes clearly.

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_readiness_modes.py -q
```

Expected: FAIL because mode policy is not yet formalized.

**Step 3: Write minimal implementation**

Add explicit mode resolution. If needed, extract policy into `core/readiness_policy.py`.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_readiness_modes.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add core/readiness_gate.py core/readiness_policy.py tests/test_readiness_modes.py
git commit -m "feat: formalize readiness gate modes"
```

### Task 2.2: Add Mode-Specific Policy Differences

**Files:**
- Modify: `core/readiness_gate.py`
- Modify: `tests/test_readiness_modes.py`

**Step 1: Write the failing policy-difference test**

Assert that at least some conditions evaluate differently between modes, for example:

- unresolved review debt may yield `WARN` for advisor handoff but stronger consequences for submission prep
- export failure may weigh more heavily in submission-prep mode

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_readiness_modes.py -q
```

Expected: FAIL because mode-specific policy is not yet applied.

**Step 3: Write minimal implementation**

Keep the policy simple, explicit, and documented.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_readiness_modes.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add core/readiness_gate.py tests/test_readiness_modes.py
git commit -m "feat: add mode-specific readiness policy"
```

### Phase 2 Acceptance Criteria

Phase 2 is accepted only when:

1. mode selection is explicit
2. policy differences are small but real
3. the gate stays traceable and non-arbitrary

---

## 7. Phase 3: Runner / Summary / Documentation Integration

### Goal

Surface the gate consistently in CLI usage and repository docs, while preserving the current runner/fix summary conventions.

### Files

- Create: `16-check-readiness/check_readiness.py`
- Modify: `run_check_once.py`
- Modify: `tests/test_runner.py`
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `docs/architecture.md`
- Modify: `docs/roadmap.md`

### Task 3.1: Add Readiness Gate CLI Entry Point

**Files:**
- Create: `16-check-readiness/check_readiness.py`
- Modify: `tests/test_readiness_gate.py`

**Step 1: Write the failing CLI test**

Assert that the gate entrypoint exists and emits JSON for a selected mode.

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_readiness_gate.py -q
```

Expected: FAIL because the CLI entrypoint does not exist.

**Step 3: Write minimal implementation**

Add a CLI wrapper that accepts at least:

- `--project-root`
- `--ruleset`
- `--mode`
- `--report`

and writes the gate artifact.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_readiness_gate.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add 16-check-readiness/check_readiness.py tests/test_readiness_gate.py
git commit -m "feat: add readiness gate cli entrypoint"
```

### Task 3.2: Integrate Gate With Runner Summaries Carefully

**Files:**
- Modify: `run_check_once.py`
- Modify: `tests/test_runner.py`

**Step 1: Write the failing runner-summary test**

Assert that the gate can be surfaced in workflow summaries without breaking the existing `run-summary.json` contract.

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_runner.py -q
```

Expected: FAIL because the gate is not yet integrated.

**Step 3: Write minimal implementation**

Expose readiness as a bounded additional step or derived artifact reference. Keep the current runner structure stable.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_runner.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add run_check_once.py tests/test_runner.py
git commit -m "feat: surface readiness gate in workflow summaries"
```

### Task 3.3: Refresh Public Docs

**Files:**
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `docs/architecture.md`
- Modify: `docs/roadmap.md`

**Step 1: Update public wording**

Document the readiness gate as:

- a final decision layer
- `PASS / WARN / BLOCK`
- artifact-driven, not all-knowing

**Step 2: Manual verification**

Ensure the docs still make it clear that the gate synthesizes evidence and does not replace human judgement.

**Step 3: Commit**

```bash
git add README.md README.zh-CN.md docs/architecture.md docs/roadmap.md
git commit -m "docs: explain pre-submission readiness gate"
```

### Phase 3 Acceptance Criteria

Phase 3 is accepted only when:

1. the gate has a CLI entrypoint
2. the gate can be surfaced in repo workflow summaries cleanly
3. public docs explain the gate honestly

---

## 8. Suggested Test Matrix

At minimum, the implementation should cover these categories.

### Artifact Contract

- gate artifact top-level fields
- per-dimension structure
- blocker/warning/next action shape

### Evidence Collection

- missing artifact handling
- present artifact aggregation
- source references preserved

### Verdict Logic

- PASS path
- WARN path
- BLOCK path
- review debt interaction
- compile/export interaction

### Modes

- advisor-handoff policy
- submission-prep policy
- unknown mode rejection

### Runner / CLI

- gate CLI writes report
- runner summary integration does not break existing structure

---

## 9. Risks And Countermeasures

### Risk 1: The gate becomes a second hidden orchestrator

Countermeasure:

- collect and synthesize existing evidence instead of rerunning the entire toolchain unnecessarily

### Risk 2: The gate collapses nuance into false certainty

Countermeasure:

- keep `WARN` first-class
- surface unresolved review debt explicitly

### Risk 3: Mode policy becomes arbitrary

Countermeasure:

- keep policy differences explicit, minimal, and documented

### Risk 4: Gate summaries drift away from existing repo summary conventions

Countermeasure:

- extend the current `summary` / `steps` / report patterns rather than inventing a completely different summary language

---

## 10. Final Execution Guidance

Implement this plan in order.

Do not skip directly to runner integration before the gate artifact and dimension logic exist.
Do not turn the gate into an all-knowing score engine.
Do not let it silently replace human judgement.

The first good release should already save users from reading five separate reports manually, even if it remains conservative.

---

## 11. Immediate Next Step After Planning

After this plan is saved, execution should move to **Direction B** as requested:

1. start implementation from `docs/plans/2026-04-20-latex-to-word-implementation-plan.md`
2. keep the remaining plans as queued execution artifacts

The recommended execution order is:

1. `latex-to-word-implementation-plan.md`
2. `compile-log-parser-implementation-plan.md`
3. `review-loop-implementation-plan.md`
4. `pre-submission-gate-implementation-plan.md`
