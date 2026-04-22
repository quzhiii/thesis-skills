# Latex-to-Word Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a bounded `02-latex-to-word` workflow to `thesis-skills` that produces a review-friendly `.docx` plus explicit export reporting, while defining a future-ready contract for submission-friendly export.

**Architecture:** Implement this as a new workflow module rather than overloading the current checker/fixer stack. Phase 0 locks wording, scaffolding, and contracts. Phase 1 adds a dry-run and report-first export boundary. Phase 2 introduces a Pandoc-first conversion path for review-friendly export. Phase 3 strengthens profile/mapping support and prepares the later submission-friendly mode without overpromising first-release fidelity.

**Tech Stack:** Python 3.10+, stdlib, existing `core/` helpers, JSON report patterns, existing project discovery, `pytest`, Pandoc or `pypandoc` integration, YAML rule packs and mapping concepts already present in the repository.

---

## 0. Scope Lock

### 0.1 First-Release Boundary

`v0.6.x` for `02-latex-to-word` should ship:

- a new workflow module directory
- a CLI runner
- a report-first dry-run path
- a Pandoc-first review-friendly export path
- explicit export reports and summary artifacts
- documentation that clearly states supported and unsupported areas

`v0.6.x` should **not** ship:

- school-perfect final submission support for arbitrary templates
- silent fixing of all unsupported LaTeX constructs
- broad package compatibility claims without fixtures and tests
- GUI features or interactive export editors

### 0.2 Locked Product Decision

The product architecture is already locked as:

- **Primary mode:** `review-friendly`
- **Secondary mode:** `submission-friendly` (defined as a contract but not the main promise of the first release)

Implementation should follow that boundary exactly.

---

## 1. Acceptance Criteria

The implementation is only accepted when all of the following are true:

1. `skills-manifest.json` includes `02-latex-to-word` with the correct module registration.
2. The repo contains a new `02-latex-to-word/` workflow with a runner and usage doc.
3. The workflow supports a dry-run/report path even when actual conversion is not applied.
4. The workflow emits a machine-readable export report and a human-readable summary.
5. Review-friendly export is the only first-class implemented export promise in `v0.6.x`.
6. Submission-friendly export is represented only as a future-ready mode/profile contract unless specifically proven by tests and docs.
7. Tests cover basic success, report generation, and bounded failure/degradation scenarios.

### 1.1 Non-Negotiable Guardrails

- Do not market the workflow as a universal LaTeX-to-Word converter.
- Do not silently swallow unsupported constructs.
- Do not hard-code school-specific submission behavior into generic export logic.
- Do not merge export behavior into checker or fixer modules.
- Do not require `--apply` for report-only export inspection.

---

## 2. Implementation Anchors

The implementation should be anchored around these files.

### Create

- `02-latex-to-word/THESIS_LATEX_TO_WORD.md`
- `02-latex-to-word/migrate_project.py`
- `tests/test_latex_to_word_workflow.py`
- `tests/data/latex_to_word/README.md`
- optional fixture files under `tests/data/latex_to_word/`

### Modify

- `skills-manifest.json`
- `core/migration.py`
- `core/project.py` (only if export preparation needs additional project discovery)
- `README.md`
- `README.zh-CN.md`
- `docs/architecture.md`
- `docs/roadmap.md`
- `adapters/intake/README.md`
- `tests/test_migration.py`

### Possible Optional Create

- `core/export_profiles.py`
- `core/export_reports.py`
- `tests/test_export_profiles.py`

These optional files should only be introduced if they materially improve separation of policy and mechanism. Avoid premature abstraction.

---

## 3. Phase Order

### Phase 0: Wording, Scaffolding, and Contracts

Purpose:

- make the new workflow visible in the repository
- lock the first-release boundary
- create the report-first interface before real conversion logic

### Phase 1: Report-First Export Boundary

Purpose:

- create a deterministic dry-run / summary path
- discover source structure and emit export intent plus warnings

### Phase 2: Review-Friendly Conversion Path

Purpose:

- add the first actual Pandoc-first `.docx` export path for review-friendly mode

### Phase 3: Profile and Mapping Strengthening

Purpose:

- introduce explicit export profile handling
- lay groundwork for later submission-friendly expansion without widening v0.6 scope

---

## 4. Phase 0: Wording, Scaffolding, and Contracts

### Goal

Make `02-latex-to-word` visible in the repository with correct wording, correct module registration, and a basic runner/doc skeleton.

### Files

- Create: `02-latex-to-word/THESIS_LATEX_TO_WORD.md`
- Create: `02-latex-to-word/migrate_project.py`
- Modify: `skills-manifest.json`
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `docs/architecture.md`
- Modify: `docs/roadmap.md`

### Task 0.1: Register The New Workflow Module

**Files:**
- Modify: `skills-manifest.json`

**Step 1: Write the failing manifest assertion**

Add or extend a test that asserts the manifest contains a module entry for `02-latex-to-word` with:

- `id`
- `entry`
- `type: workflow`
- `runner`

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_migration.py -q
```

Expected: FAIL because `02-latex-to-word` is not yet registered.

**Step 3: Update manifest**

Add the module entry mirroring the `01-word-to-latex` registration style.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_migration.py -q
```

Expected: PASS for the updated manifest assertion.

**Step 5: Commit**

```bash
git add skills-manifest.json tests/test_migration.py
git commit -m "feat: register latex-to-word workflow module"
```

### Task 0.2: Add Workflow Doc Skeleton

**Files:**
- Create: `02-latex-to-word/THESIS_LATEX_TO_WORD.md`

**Step 1: Write the workflow doc**

Document:

- workflow boundary
- recommended sequence
- `review-friendly` as the first release target
- dry-run/report behavior
- explicit statement that not all LaTeX constructs are guaranteed to round-trip

**Step 2: Verify doc wording**

Manual review only.

Doc must not claim:

- perfect fidelity
- general submission guarantees in first release

**Step 3: Commit**

```bash
git add 02-latex-to-word/THESIS_LATEX_TO_WORD.md
git commit -m "docs: add latex-to-word workflow entry"
```

### Task 0.3: Add Runner Skeleton

**Files:**
- Create: `02-latex-to-word/migrate_project.py`
- Modify: `core/migration.py`

**Step 1: Write the failing runner test**

Add a test that expects the new CLI entrypoint to exist and print structured JSON.

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_latex_to_word_workflow.py -q
```

Expected: FAIL because the module and test target do not exist.

**Step 3: Write minimal runner implementation**

Mirror the `01-word-to-latex/migrate_project.py` structure:

- `argparse`
- `--project-root`
- `--output-file`
- `--profile`
- `--apply`
- `--report`
- JSON summary to stdout

For now the runner may call a placeholder `run_latex_to_word_migration(...)` that returns a report-first summary.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_latex_to_word_workflow.py -q
```

Expected: PASS for runner existence and JSON output shape.

**Step 5: Commit**

```bash
git add 02-latex-to-word/migrate_project.py core/migration.py tests/test_latex_to_word_workflow.py
git commit -m "feat: add latex-to-word runner skeleton"
```

### Task 0.4: Align Public Wording

**Files:**
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `docs/architecture.md`
- Modify: `docs/roadmap.md`

**Step 1: Add wording for the new workflow**

Update docs to say:

- `02-latex-to-word` exists as a new workflow direction
- first release is review-friendly
- submission-oriented support is future-facing and stricter

**Step 2: Verify wording consistency**

Run:

```bash
python - <<'PY'
from pathlib import Path
for p in [Path('README.md'), Path('README.zh-CN.md'), Path('docs/architecture.md'), Path('docs/roadmap.md')]:
    print(f'--- {p} ---')
    text = p.read_text(encoding='utf-8')
    for needle in ['latex-to-word', 'review-friendly', 'submission-friendly']:
        if needle in text:
            print(needle)
PY
```

Expected: wording is present where needed and does not overstate first-release capabilities.

**Step 3: Commit**

```bash
git add README.md README.zh-CN.md docs/architecture.md docs/roadmap.md
git commit -m "docs: position latex-to-word as review-first export workflow"
```

### Phase 0 Acceptance Criteria

Phase 0 is accepted only when:

1. the new workflow is visible in manifest and docs
2. a CLI skeleton exists
3. no public wording overclaims first-release scope

---

## 5. Phase 1: Report-First Export Boundary

### Goal

Create a deterministic dry-run / report path that understands the source thesis project and emits a useful export summary before real `.docx` conversion is relied on.

### Files

- Modify: `core/migration.py`
- Optional modify: `core/project.py`
- Create: `tests/data/latex_to_word/README.md`
- Create: `tests/test_latex_to_word_workflow.py`
- Modify: `tests/test_migration.py`

### Task 1.1: Define The Summary Shape

**Files:**
- Modify: `core/migration.py`
- Modify: `tests/test_migration.py`

**Step 1: Write the failing summary test**

The migration summary must include at least:

```python
{
    "project_root": "...",
    "profile": "review-friendly",
    "output_file": "...",
    "applied": False,
    "main_tex": "...",
    "chapters": [...],
    "warnings": [...],
    "unsupported_constructs": [...],
}
```

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_migration.py -q
```

Expected: FAIL because the reverse migration summary does not exist yet.

**Step 3: Write minimal summary implementation**

Add `run_latex_to_word_migration(...)` to `core/migration.py`.

Initially it should:

- accept the new CLI inputs
- reuse available project discovery
- gather chapter targets
- emit the summary shape with placeholder warnings where needed

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_migration.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add core/migration.py tests/test_migration.py
git commit -m "feat: add latex-to-word report-first migration summary"
```

### Task 1.2: Detect Basic Unsupported Constructs

**Files:**
- Modify: `core/migration.py`
- Optional modify: `core/project.py`
- Modify: `tests/test_latex_to_word_workflow.py`

**Step 1: Write the failing unsupported-construct test**

Cover detection of likely first-release problem areas such as:

- custom macros
- `tikzpicture`
- heavy math environments
- custom title-page logic

Only detection/reporting is required here.

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_latex_to_word_workflow.py -q
```

Expected: FAIL because warnings/unsupported construct classification is too weak.

**Step 3: Write minimal implementation**

Scan discovered source files conservatively and emit structured warnings. Avoid deep parsing beyond what is necessary for reliable first-release detection.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_latex_to_word_workflow.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add core/migration.py tests/test_latex_to_word_workflow.py
git commit -m "feat: report unsupported constructs for latex-to-word export"
```

### Task 1.3: Write The Export Report File

**Files:**
- Modify: `02-latex-to-word/migrate_project.py`
- Modify: `tests/test_latex_to_word_workflow.py`

**Step 1: Write the failing report-path test**

Assert that:

- a default report path is used when `--report` is omitted
- a custom report path is honored when provided
- the report JSON matches the stdout summary contract

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_latex_to_word_workflow.py -q
```

Expected: FAIL because the runner does not persist the report yet.

**Step 3: Write minimal implementation**

Write the report to:

- custom `--report` if provided
- otherwise a default report under the thesis project’s `reports/` directory, for example `latex_to_word-report.json`

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_latex_to_word_workflow.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add 02-latex-to-word/migrate_project.py tests/test_latex_to_word_workflow.py
git commit -m "feat: persist latex-to-word export reports"
```

### Phase 1 Acceptance Criteria

Phase 1 is accepted only when:

1. dry-run/report mode works without real `.docx` conversion
2. source structure is discovered and summarized
3. unsupported constructs are surfaced explicitly
4. report files are written deterministically

---

## 6. Phase 2: Review-Friendly Conversion Path

### Goal

Add the first actual `.docx` conversion path for `review-friendly` export using a Pandoc-first approach.

### Files

- Modify: `02-latex-to-word/migrate_project.py`
- Modify: `core/migration.py`
- Optional create: `core/export_profiles.py`
- Optional create: `tests/test_export_profiles.py`
- Modify: `tests/test_latex_to_word_workflow.py`
- Create or extend: `tests/data/latex_to_word/README.md`

### Task 2.1: Add A Bounded Conversion Adapter

**Files:**
- Modify: `core/migration.py`
- Modify: `tests/test_latex_to_word_workflow.py`

**Step 1: Write the failing conversion adapter test**

Cover these behaviors:

- conversion is attempted only when `--apply` or equivalent export mode is enabled
- `review-friendly` is the default profile
- missing Pandoc or conversion failure results in structured warnings/errors rather than silent failure

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_latex_to_word_workflow.py -q
```

Expected: FAIL because the conversion path does not exist yet.

**Step 3: Write minimal implementation**

Add a bounded conversion adapter that:

- checks for Pandoc availability
- executes the conversion path conservatively
- records conversion errors and warnings in the report
- does not hide failures

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_latex_to_word_workflow.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add core/migration.py tests/test_latex_to_word_workflow.py
git commit -m "feat: add bounded pandoc-first latex-to-word conversion adapter"
```

### Task 2.2: Produce Review-Friendly `.docx`

**Files:**
- Modify: `02-latex-to-word/migrate_project.py`
- Modify: `core/migration.py`
- Modify: `tests/test_latex_to_word_workflow.py`

**Step 1: Write the failing output-file test**

Assert that a successful review-friendly export:

- creates the target `.docx`
- records `applied: true`
- records the selected profile
- still includes export warnings where needed

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_latex_to_word_workflow.py -q
```

Expected: FAIL because `.docx` output is not yet generated.

**Step 3: Write minimal implementation**

Support a real output path for review-friendly mode. Prioritize structural readability over visual perfection.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_latex_to_word_workflow.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add 02-latex-to-word/migrate_project.py core/migration.py tests/test_latex_to_word_workflow.py
git commit -m "feat: enable review-friendly latex-to-word export"
```

### Task 2.3: Document Known Limitations In Workflow Doc

**Files:**
- Modify: `02-latex-to-word/THESIS_LATEX_TO_WORD.md`

**Step 1: Expand the doc with supported/unsupported areas**

Include at least:

- what review-friendly mode is for
- what is expected to degrade
- why the report matters
- why submission-friendly is not yet the main first-release guarantee

**Step 2: Manual verification**

Ensure wording remains aligned with the product architecture doc.

**Step 3: Commit**

```bash
git add 02-latex-to-word/THESIS_LATEX_TO_WORD.md
git commit -m "docs: explain latex-to-word first-release limitations"
```

### Phase 2 Acceptance Criteria

Phase 2 is accepted only when:

1. `review-friendly` export creates a real `.docx`
2. conversion failures are reported explicitly
3. docs explain the first-release boundary honestly

---

## 7. Phase 3: Profile And Mapping Strengthening

### Goal

Strengthen profile handling and prepare the repo for later submission-friendly expansion without widening `v0.6.x` promises.

### Files

- Optional create: `core/export_profiles.py`
- Optional create: `tests/test_export_profiles.py`
- Modify: `adapters/intake/README.md`
- Modify: `docs/architecture.md`
- Modify: `README.md`
- Modify: `README.zh-CN.md`

### Task 3.1: Define Export Profile Contract

**Files:**
- Optional create: `core/export_profiles.py`
- Optional create: `tests/test_export_profiles.py`

**Step 1: Write the failing profile test**

Cover:

- `review-friendly` resolves to the default policy
- `submission-friendly` resolves to a stricter but still limited policy contract
- unknown profiles fail clearly

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_export_profiles.py -q
```

Expected: FAIL because profile resolution is not yet formalized.

**Step 3: Write minimal implementation**

Add profile resolution only if needed to keep policy separate from mechanism. Keep the contract simple and human-readable.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_export_profiles.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add core/export_profiles.py tests/test_export_profiles.py
git commit -m "feat: formalize latex-to-word export profile contract"
```

### Task 3.2: Extend Intake / Mapping Guidance

**Files:**
- Modify: `adapters/intake/README.md`

**Step 1: Add reverse/export-aware mapping guidance**

Document how future export-aware mappings may include:

- heading style targets
- caption style targets
- front-matter template references
- later submission-friendly docx profile hints

Keep this guidance descriptive, not overengineered.

**Step 2: Manual verification**

Ensure the doc still reads as practical intake guidance and does not invent unsupported functionality.

**Step 3: Commit**

```bash
git add adapters/intake/README.md
git commit -m "docs: add export-aware mapping guidance for latex-to-word"
```

### Task 3.3: Align Architecture Docs With Export Layer

**Files:**
- Modify: `docs/architecture.md`
- Modify: `README.md`
- Modify: `README.zh-CN.md`

**Step 1: Update architecture wording**

Reflect that the repository now includes an outward delivery/export workflow layer, while preserving the existing deterministic core.

**Step 2: Verify wording consistency**

Manual review only.

The docs must still position the repo as a deterministic workflow layer rather than a general writing assistant or universal converter.

**Step 3: Commit**

```bash
git add docs/architecture.md README.md README.zh-CN.md
git commit -m "docs: align architecture with latex-to-word export layer"
```

### Phase 3 Acceptance Criteria

Phase 3 is accepted only when:

1. export policy is clearly separated from mechanism
2. future submission-friendly expansion has a clean contract
3. docs remain honest and stable

---

## 8. Suggested Test Matrix

At minimum, the implementation should cover these test categories.

### CLI / Runner

- module exists
- JSON summary shape is stable
- report path behavior is deterministic

### Dry-run / Report-first

- source structure is discovered
- unsupported constructs are reported
- no `.docx` is created when not applied

### Conversion Path

- `review-friendly` is default
- successful conversion writes target `.docx`
- missing Pandoc or failed conversion produces structured errors

### Documentation / Wording

- manifest and docs agree on scope
- docs do not overclaim first-release fidelity

---

## 9. Risks And Countermeasures

### Risk 1: The plan drifts into full submission support too early

Countermeasure:

- keep `review-friendly` as the only first-class implemented release target
- keep `submission-friendly` at contract/profile level unless concrete tests justify more

### Risk 2: Conversion logic becomes opaque

Countermeasure:

- keep dry-run/report-first behavior mandatory
- keep export reports machine-readable and human-readable

### Risk 3: Implementation introduces unnecessary abstraction too early

Countermeasure:

- add `core/export_profiles.py` only if needed
- prefer minimal extension of existing `core/migration.py` before creating many new layers

### Risk 4: Docs outrun real capability

Countermeasure:

- update wording only after tests and behavior are real
- keep architecture and README aligned with implementation proofs

---

## 10. Final Execution Guidance

Implement this plan in order.

Do not skip directly to “real export” before the report-first boundary exists.
Do not widen the first-release promise while coding.
Do not merge submission-friendly assumptions into generic review-friendly behavior.

The first successful version should already be useful even if it is conservative.

That is a better fit for `thesis-skills` than a flashy but unreliable converter.

---

## 11. Next Artifact After This Plan

After implementation of this plan is stable, the next recommended planning artifact is:

`docs/plans/2026-04-20-compile-log-parser-implementation-plan.md`
