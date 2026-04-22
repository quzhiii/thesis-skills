# Compile Log Parser Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a compile-log parsing workflow to `thesis-skills` that turns LaTeX build failures and warnings into structured, friendlier findings without rewriting the repository into a full compile orchestration system.

**Architecture:** Implement this as a new checker-style module plus runner integration. Phase 0 locks wording, module shape, and current compile-step expectations. Phase 1 introduces a report-only parser for existing compile logs. Phase 2 integrates parsing with `run_check_once.py` and replaces the current hardcoded compile-unavailable summary. Phase 3 strengthens rule-pack policy and representative fixture coverage for common thesis compile failures.

**Tech Stack:** Python 3.10+, stdlib, existing `core/` project and report helpers, JSON report structure, `pytest`, existing runner architecture, optional subprocess-based compile invocation only where justified by tests.

---

## 0. Scope Lock

### 0.1 First-Release Boundary

The first release of the compile-log parser should ship:

- a new compile-check module
- a parser for common LaTeX compile logs
- structured findings and summary output
- runner integration in `run_check_once.py`
- rule-pack support for compile categories and severities

It should **not** ship:

- a full build-system replacement
- deep cross-platform compile orchestration for every TeX toolchain
- GUI or interactive debugging workflow
- magical repair of compile problems

### 0.2 Product Boundary

This feature should be positioned as:

> a diagnostic translator that converts raw LaTeX compile output into inspectable, friendlier findings

It should not be positioned as:

- a guarantee that the repository can always compile the thesis itself
- a replacement for understanding the LaTeX toolchain
- a promise of perfect parser coverage across arbitrary packages and engines

---

## 1. Acceptance Criteria

The implementation is only accepted when all of the following are true:

1. the repo contains a compile-check module following the checker pattern
2. compile findings are written as structured JSON reports
3. `run_check_once.py` no longer hardcodes compile as always unavailable when a compile adapter/log path is present
4. common failure classes are converted into clear findings with category and severity
5. the parser can distinguish at least build-blocking errors from softer warnings
6. runner and docs reflect the new behavior honestly

### 1.1 Non-Negotiable Guardrails

- Do not rewrite `run_check_once.py` into a generic TeX build framework.
- Do not hide raw compile failure when parsing fails.
- Do not drop the machine-readable report contract.
- Do not claim engine-agnostic perfection without fixtures.
- Do not let compile parsing silently mutate thesis source files.

---

## 2. Implementation Anchors

### Create

- `15-check-compile/THESIS_CHECK_COMPILE.md`
- `15-check-compile/check_compile.py`
- `tests/test_compile_parser.py`
- `tests/data/compile_logs/README.md`
- representative `.log` fixture files under `tests/data/compile_logs/`

### Modify

- `run_check_once.py`
- `core/checkers.py`
- `core/reports.py`
- `core/project.py` (only if log-location discovery needs extension)
- `skills-manifest.json`
- `tests/test_runner.py`
- `README.md`
- `README.zh-CN.md`
- `docs/architecture.md`
- `docs/roadmap.md`
- `90-rules/packs/university-generic/rules.yaml`
- `90-rules/packs/tsinghua-thesis/rules.yaml`
- `90-rules/packs/journal-generic/rules.yaml`

### Optional Create

- `core/compile_parser.py`
- `tests/test_compile_rules.py`

Create `core/compile_parser.py` only if it keeps parsing logic meaningfully separate from general checker orchestration. Avoid needless layering.

---

## 3. Phase Order

### Phase 0: Module and Contract Setup

Purpose:

- register the new compile-check feature
- create the module scaffold
- update wording and scope

### Phase 1: Report-Only Compile Log Parsing

Purpose:

- parse existing compile log fixtures into structured findings without relying on live compilation

### Phase 2: Runner Integration

Purpose:

- replace current hardcoded compile summary behavior with real compile report handling in `run_check_once.py`

### Phase 3: Rule-Pack and Fixture Expansion

Purpose:

- give compile findings configurable severities and broaden fixture coverage for realistic thesis failures

---

## 4. Phase 0: Module and Contract Setup

### Goal

Create the new compile-check module and align docs, manifest, and public wording before parsing logic is introduced.

### Files

- Create: `15-check-compile/THESIS_CHECK_COMPILE.md`
- Create: `15-check-compile/check_compile.py`
- Modify: `skills-manifest.json`
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `docs/architecture.md`
- Modify: `docs/roadmap.md`

### Task 0.1: Register The New Checker Module

**Files:**
- Modify: `skills-manifest.json`

**Step 1: Write the failing manifest assertion**

Add or extend a test asserting the manifest contains:

- `id: 15-check-compile`
- `entry`
- `type: checker`
- `runner`

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_runner.py -q
```

Expected: FAIL because the compile checker is not yet registered.

**Step 3: Update manifest**

Add the new checker module following the current checker registration pattern.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_runner.py -q
```

Expected: PASS for the manifest assertion.

**Step 5: Commit**

```bash
git add skills-manifest.json tests/test_runner.py
git commit -m "feat: register compile checker module"
```

### Task 0.2: Add Compile Checker Doc Skeleton

**Files:**
- Create: `15-check-compile/THESIS_CHECK_COMPILE.md`

**Step 1: Write the checker doc**

Document:

- purpose of compile-log parsing
- current limitation relative to full build systems
- expected CLI shape
- relationship to `--skip-compile`

**Step 2: Manual verification**

Ensure wording says this is a diagnostic parser, not a full compile framework.

**Step 3: Commit**

```bash
git add 15-check-compile/THESIS_CHECK_COMPILE.md
git commit -m "docs: add compile checker workflow entry"
```

### Task 0.3: Add Checker Script Skeleton

**Files:**
- Create: `15-check-compile/check_compile.py`

**Step 1: Write the failing checker test**

Add a test expecting the checker entrypoint to exist and emit JSON.

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_compile_parser.py -q
```

Expected: FAIL because the checker module does not exist.

**Step 3: Write minimal script implementation**

Mirror the structure of existing checker entrypoints:

- `argparse`
- `--project-root`
- `--ruleset`
- `--report`
- print JSON summary

For now it may call a placeholder compile-check function that returns an empty findings shape.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_compile_parser.py -q
```

Expected: PASS for entrypoint and JSON shape.

**Step 5: Commit**

```bash
git add 15-check-compile/check_compile.py tests/test_compile_parser.py
git commit -m "feat: add compile checker skeleton"
```

### Task 0.4: Align Public Wording

**Files:**
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `docs/architecture.md`
- Modify: `docs/roadmap.md`

**Step 1: Add wording for compile parsing**

Update docs so they say:

- compile-log parsing exists or is newly added
- the feature gives friendlier error hints
- compile remains bounded and deterministic in scope

**Step 2: Verify wording consistency**

Manual review only.

Wording must not imply the repository fully manages all TeX compilation workflows.

**Step 3: Commit**

```bash
git add README.md README.zh-CN.md docs/architecture.md docs/roadmap.md
git commit -m "docs: position compile parsing as diagnostic translation layer"
```

### Phase 0 Acceptance Criteria

Phase 0 is accepted only when:

1. the new checker exists in docs and manifest
2. a checker skeleton exists
3. wording does not overclaim build-system support

---

## 5. Phase 1: Report-Only Compile Log Parsing

### Goal

Turn raw compile logs into structured findings using fixture-driven tests, without relying on live compilation yet.

### Files

- Create: `tests/data/compile_logs/README.md`
- Create: representative `.log` fixtures under `tests/data/compile_logs/`
- Modify or create: `core/compile_parser.py`
- Modify: `core/checkers.py`
- Modify: `core/reports.py`
- Modify: `tests/test_compile_parser.py`

### Task 1.1: Build Fixture Corpus

**Files:**
- Create: `tests/data/compile_logs/README.md`
- Create: fixture `.log` files

**Step 1: Write the failing fixture test**

Assert that the fixture corpus exists and includes representative cases such as:

- undefined control sequence
- missing package/file
- missing citation/reference warning
- bibliography backend issue
- overfull hbox warning

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_compile_parser.py -q
```

Expected: FAIL because the fixture corpus does not yet exist.

**Step 3: Add fixtures and fixture README**

Prefer realistic or trimmed real logs over synthetic toy lines where possible.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_compile_parser.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add tests/data/compile_logs tests/test_compile_parser.py
git commit -m "test: add compile log fixture corpus"
```

### Task 1.2: Add Core Compile Parser

**Files:**
- Optional create: `core/compile_parser.py`
- Modify: `tests/test_compile_parser.py`

**Step 1: Write the failing parser tests**

Cover these behaviors:

- parse build-blocking errors into findings
- parse warnings into findings
- capture best-effort file/line context where available
- preserve unknown/raw cases rather than discarding them silently

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_compile_parser.py -q
```

Expected: FAIL because parsing logic does not exist yet.

**Step 3: Write minimal implementation**

Add a parser that produces structured categories such as:

- `undefined_control_sequence`
- `missing_file_or_package`
- `missing_citation`
- `missing_reference`
- `bibliography_backend_issue`
- `overfull_box`
- `compile_warning_unknown`
- `compile_error_unknown`

Keep raw snippets where precise categorization is not possible.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_compile_parser.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add core/compile_parser.py tests/test_compile_parser.py
git commit -m "feat: add core compile log parser"
```

### Task 1.3: Expose Compile Checker In `core/checkers.py`

**Files:**
- Modify: `core/checkers.py`
- Modify: `core/reports.py`
- Modify: `tests/test_compile_parser.py`

**Step 1: Write the failing checker integration test**

Assert that a compile-check function returns the standard report shape with:

- `summary`
- `findings`
- counts for errors/warnings

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_compile_parser.py -q
```

Expected: FAIL because the checker-level integration is missing.

**Step 3: Write minimal implementation**

Add a checker function such as `run_compile_check(...)` in `core/checkers.py` using the same general report contract as existing checkers.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_compile_parser.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add core/checkers.py core/reports.py tests/test_compile_parser.py
git commit -m "feat: expose compile log parsing through checker contract"
```

### Phase 1 Acceptance Criteria

Phase 1 is accepted only when:

1. representative `.log` fixtures exist
2. raw logs become structured findings
3. the feature works as a report-only checker without needing live compile orchestration

---

## 6. Phase 2: Runner Integration

### Goal

Replace the current hardcoded compile summary in `run_check_once.py` with real compile-check behavior when compile is not skipped.

### Files

- Modify: `run_check_once.py`
- Modify: `tests/test_runner.py`
- Optional modify: `core/project.py`

### Task 2.1: Add Compile Step To The Runner Step List

**Files:**
- Modify: `run_check_once.py`
- Modify: `tests/test_runner.py`

**Step 1: Write the failing runner test**

Update runner tests so that when compile is not skipped, compile is no longer always `unavailable`.

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_runner.py -q
```

Expected: FAIL because runner still reports compile as unavailable.

**Step 3: Write minimal runner integration**

Add a real compile-check step after the other checks. Keep `--skip-compile` behavior intact.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_runner.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add run_check_once.py tests/test_runner.py
git commit -m "feat: integrate compile checker into run_check_once"
```

### Task 2.2: Support Log Location / Build Output Discovery

**Files:**
- Optional modify: `core/project.py`
- Modify: `run_check_once.py`
- Modify: `tests/test_runner.py`

**Step 1: Write the failing discovery test**

Assert that compile-check can locate or accept the relevant log file path for the thesis project.

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_runner.py -q
```

Expected: FAIL because compile-log discovery is not yet explicit enough.

**Step 3: Write minimal implementation**

Add best-effort log discovery based on the project’s main TeX file and expected `.log` naming conventions. Avoid broad assumptions beyond existing repo patterns.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_runner.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add run_check_once.py core/project.py tests/test_runner.py
git commit -m "feat: add compile log discovery for thesis projects"
```

### Task 2.3: Preserve Graceful Behavior When Compile Support Is Missing

**Files:**
- Modify: `run_check_once.py`
- Modify: `tests/test_runner.py`

**Step 1: Write the failing graceful-fallback test**

Assert that when compile is requested but no log or adapter is available, the runner returns a clear structured status rather than crashing.

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_runner.py -q
```

Expected: FAIL because graceful fallback is incomplete.

**Step 3: Write minimal implementation**

Return a clear compile-step summary such as:

- `status: unavailable`
- `status: missing-log`
- `status: parsed`

Do not hide raw failure context.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_runner.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add run_check_once.py tests/test_runner.py
git commit -m "feat: handle missing compile artifacts gracefully"
```

### Phase 2 Acceptance Criteria

Phase 2 is accepted only when:

1. compile is a real runner step when not skipped
2. compile-log parsing feeds structured results into `run-summary.json`
3. missing compile support fails gracefully and explicitly

---

## 7. Phase 3: Rule-Pack and Fixture Expansion

### Goal

Add rule-pack-level policy and strengthen coverage across realistic thesis compile issues.

### Files

- Modify: `90-rules/packs/university-generic/rules.yaml`
- Modify: `90-rules/packs/tsinghua-thesis/rules.yaml`
- Modify: `90-rules/packs/journal-generic/rules.yaml`
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Optional create: `tests/test_compile_rules.py`
- Extend: `tests/data/compile_logs/`

### Task 3.1: Add Compile Policy To Rule Packs

**Files:**
- Modify: `90-rules/packs/university-generic/rules.yaml`
- Modify: `90-rules/packs/tsinghua-thesis/rules.yaml`
- Modify: `90-rules/packs/journal-generic/rules.yaml`

**Step 1: Write the failing rule test**

Assert that all starter packs include a `compile` section covering at least:

- category enablement
- category severity defaults
- optional engine-specific notes or toggles

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_compile_rules.py -q
```

Expected: FAIL because compile policy is not yet present.

**Step 3: Write minimal rule-pack changes**

Add compile-related policy without overengineering. Keep YAML human-editable and aligned with the current pack style.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_compile_rules.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add 90-rules/packs/university-generic/rules.yaml 90-rules/packs/tsinghua-thesis/rules.yaml 90-rules/packs/journal-generic/rules.yaml tests/test_compile_rules.py
git commit -m "feat: add compile parsing policy to starter rule packs"
```

### Task 3.2: Expand Fixture Coverage

**Files:**
- Extend: `tests/data/compile_logs/`
- Modify: `tests/test_compile_parser.py`

**Step 1: Add more fixture cases**

Expand coverage for:

- XeLaTeX-related missing font / engine mismatch hints
- BibTeX or Biber ordering issues
- encoding-related failures
- cross-reference stabilization warnings

**Step 2: Run tests**

Run:

```bash
pytest tests/test_compile_parser.py -q
```

Expected: PASS with broader fixture coverage.

**Step 3: Commit**

```bash
git add tests/data/compile_logs tests/test_compile_parser.py
git commit -m "test: expand compile log fixture coverage"
```

### Task 3.3: Refresh Public Docs

**Files:**
- Modify: `README.md`
- Modify: `README.zh-CN.md`

**Step 1: Update public wording**

Document compile parsing as:

- friendlier error hinting
- structured compile findings
- still bounded in scope

**Step 2: Manual verification**

Make sure public docs still recommend `--skip-compile` when the user wants to isolate non-build issues, while also making the new compile parsing value visible.

**Step 3: Commit**

```bash
git add README.md README.zh-CN.md
git commit -m "docs: explain compile log parsing and bounded compile support"
```

### Phase 3 Acceptance Criteria

Phase 3 is accepted only when:

1. compile categories have rule-pack policy
2. fixture coverage includes realistic thesis failure classes
3. public docs explain the feature honestly

---

## 8. Suggested Test Matrix

At minimum, the implementation should cover these categories.

### Module / CLI

- checker module exists
- report file is written
- output JSON shape is stable

### Parser

- blocking errors become findings
- warnings become findings
- file/line context is captured when present
- unknown cases are preserved conservatively

### Runner

- `--skip-compile` still works
- compile becomes a real step when not skipped
- missing compile artifacts fail gracefully

### Rule Packs

- compile policy exists in starter packs
- severities are configurable

---

## 9. Risks And Countermeasures

### Risk 1: Feature drifts into full compile orchestration

Countermeasure:

- keep the implementation centered on parsing and reporting
- only add minimal compile/log discovery needed for deterministic runner behavior

### Risk 2: Parser becomes brittle and overfit

Countermeasure:

- rely on realistic fixtures
- preserve unknown cases rather than pretending parser certainty

### Risk 3: Public wording overclaims support

Countermeasure:

- keep docs aligned with what fixtures and tests actually prove

### Risk 4: Compile integration destabilizes current runner expectations

Countermeasure:

- update `tests/test_runner.py` first
- keep graceful fallback states explicit

---

## 10. Final Execution Guidance

Implement this plan in order.

Do not skip directly to runner integration before the report-only parser exists.
Do not market this as a build system.
Do not erase the usefulness of `--skip-compile` for isolating structure/format issues.

The first good release should make compile output understandable, not make compile complexity disappear.

---

## 11. Next Artifact After This Plan

After this plan, the next recommended planning artifact is:

`docs/plans/2026-04-20-review-loop-product-architecture.md`
