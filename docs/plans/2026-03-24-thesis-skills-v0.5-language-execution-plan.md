# Thesis Skills v0.5 Language Upgrade Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Upgrade `thesis-skills` from the current v0.4 language lint/fix baseline into a phased Chinese thesis final-draft language QA workflow with clear separation between deterministic lint, deep review-only checks, and patch preview.

**Architecture:** Keep the current repository shape and runner model. Phase 0 hardens the existing baseline so the repo is safe to evolve. Phase 1 expands `11-check-language` and `21-fix-language-style` into a usable v0.5.0 basic language foundation. Phase 2 adds a report-only `14-check-language-deep` layer with richer findings and consistency checks. Phase 3 adds `24-fix-language-deep` as patch preview plus selective apply without collapsing deep suggestions into safe fix.

**Tech Stack:** Python 3.10+, stdlib, pytest, YAML rule packs, existing `core/` helpers, existing JSON report structure, existing CLI runners.

---

## 0. Repository Facts and Scope Decisions

### 0.1 Current Baseline on 2026-03-24

- Public GitHub and local `main` are aligned at `v0.4.0`.
- `skills-manifest.json` has no `14-check-language-deep` or `24-fix-language-deep`.
- `run_check_once.py` only runs `bib-quality`, `references`, `language`, `format`, `content`.
- `run_fix_cycle.py` only runs `references`, `language`, `format`.
- `core/common.py` only supports a minimal `Finding` shape with `severity`, `code`, `message`, `file`, `line`, `suggestion`.
- Current language layer only covers:
  - `cjk_latin_spacing`
  - `repeated_punctuation`
  - `mixed_quote_style`
  - `weak_phrases`
- Current smoke workflow and local sandbox test behavior need tightening before v0.5 execution.

### 0.2 Scope Decisions Locked for v0.5

- Do not create a new repository.
- Do not rewrite the repository architecture.
- Do not merge deep review logic into `11-check-language`.
- Do not merge deep patch logic into `21-fix-language-style`.
- Do not introduce heavy NLP or LLM runtime dependencies in v0.5.
- Do not make deep fixes auto-apply by default.
- Do not build PDF-first intake, GUI, or web product surfaces in v0.5.

### 0.3 Release Structure

- Preflight: baseline hardening on top of `v0.4.0` before language expansion starts.
- `v0.5.0`: basic language foundation.
- `v0.5.1`: deep language checker.
- `v0.5.2`: deep language fixer with patch preview.

---

## 1. Global Acceptance Criteria

The full v0.5 program is only accepted when all of the following are true:

1. `11-check-language` is a usable deterministic thesis-language lint layer rather than a four-rule starter.
2. `21-fix-language-style` only applies low-risk, reversible fixes.
3. `14-check-language-deep` exists and outputs richer findings with `span`, `evidence`, `suggestions`, `confidence`, and `review_required`.
4. `24-fix-language-deep` exists and defaults to patch preview or selective apply only.
5. `skills-manifest.json`, runners, docs, and tests all reference the same module set and same versioned scope.
6. Basic language and deep language responsibilities are visibly separated in code, docs, and CLI behavior.
7. The repo remains deterministic, inspectable, and rollback-friendly.

### 1.1 Non-Negotiable Guardrails

- Safe fix must never auto-apply deep suggestions.
- Deep fix must skip `review_required=true` findings by default.
- Report generation must be stable JSON with explicit fields.
- New rule-pack schema must remain human-editable YAML.
- Existing v0.4 check/fix flow must keep working during the transition.

---

## 2. Phase Order and Gates

### Phase 0: Preflight Baseline Hardening

**Purpose:** Fix current repo-level inconsistencies before any v0.5 feature work.

**Must finish before Phase 1 starts.**

### Phase 1: v0.5.0 Basic Language Foundation

**Purpose:** Expand deterministic language lint and safe fix into a credible thesis-language baseline.

**Must finish before Phase 2 starts.**

### Phase 2: v0.5.1 Deep Language Checker

**Purpose:** Add review-oriented language analysis and consistency detection without mutating source files.

**Must finish before Phase 3 starts.**

### Phase 3: v0.5.2 Deep Language Fixer

**Purpose:** Convert deep findings into validated patches, preview output, and selective apply controls.

**Final phase of the v0.5 language program.**

---

## 3. Phase 0: Preflight Baseline Hardening

### Goal

Make the current repository testable, internally consistent, and ready for staged language expansion.

### Files

- Modify: `.github/workflows/check.yml`
- Modify: `docs/roadmap.md`
- Modify: `tests/test_language_checker.py`
- Modify: `tests/test_fixers.py`
- Modify: `tests/test_runner.py`
- Optional create: `tests/conftest.py`
- Optional create: `tests/helpers.py`

### Task 0.1: Fix Smoke Workflow Drift

**Files:**
- Modify: `.github/workflows/check.yml`

**Steps:**
1. Replace stale example paths such as `examples/minimal-project` with the real example path used by the repo.
2. Replace stale CLI arguments such as `--rules` with the actual `--ruleset`.
3. Ensure smoke commands target real rule-pack ids such as `tsinghua-thesis` and `university-generic`.

**Verify:**
Run:
```bash
python run_check_once.py --project-root examples/minimal-latex-project --ruleset university-generic --skip-compile
```
Expected: command completes and writes `examples/minimal-latex-project/reports/run-summary.json`.

### Task 0.2: Make Tests Sandbox-Friendly

**Files:**
- Modify: `tests/test_language_checker.py`
- Modify: `tests/test_fixers.py`
- Optional create: `tests/conftest.py`

**Steps:**
1. Stop relying on OS temp directories that may be blocked in the current execution environment.
2. Use repo-owned writable temp directories under `tests/.tmp/` or a fixture rooted in the workspace.
3. Make cleanup deterministic.

**Verify:**
Run:
```bash
pytest tests/test_language_checker.py tests/test_fixers.py -q
```
Expected: tests pass in the workspace sandbox.

### Task 0.3: Tighten Runner Baseline Assertions

**Files:**
- Modify: `tests/test_runner.py`

**Steps:**
1. Assert the existing runner step order explicitly.
2. Assert `language` exists in the run summary.
3. Keep current compile behavior assertions until compile adapters change in a later release.

**Verify:**
Run:
```bash
pytest tests/test_runner.py -q
```
Expected: runner tests pass and still reflect current v0.4 behavior.

### Task 0.4: Correct Roadmap Drift

**Files:**
- Modify: `docs/roadmap.md`

**Steps:**
1. Remove statements that imply unsupported capabilities are already stable if code and manifest do not match.
2. Add a short note that the language upgrade is planned as a phased v0.5 track.
3. Keep wording aligned with the actual repository state.

**Verify:**
- Manual review only.
- Roadmap must not claim `14` or `24` already exist.

### Phase 0 Acceptance Criteria

Phase 0 is accepted only when:

1. Smoke workflow points to real paths and real CLI flags.
2. `pytest tests/test_language_checker.py tests/test_fixers.py tests/test_runner.py -q` passes in the workspace.
3. `docs/roadmap.md` no longer overstates the current language feature set.
4. No v0.5 feature code has been added yet.

---

## 4. Phase 1: v0.5.0 Basic Language Foundation

### Goal

Turn the current starter language checker and safe fixer into a usable deterministic thesis-language baseline.

### Files

- Modify: `11-check-language/THESIS_CHECK_LANGUAGE.md`
- Modify: `11-check-language/check_language.py`
- Modify: `21-fix-language-style/THESIS_FIX_LANGUAGE_STYLE.md`
- Modify: `21-fix-language-style/fix_language_style.py`
- Modify: `core/checkers.py`
- Modify: `core/fixers.py`
- Optional create: `core/language_rules.py`
- Modify: `90-rules/packs/tsinghua-thesis/rules.yaml`
- Modify: `90-rules/packs/university-generic/rules.yaml`
- Modify: `90-rules/packs/journal-generic/rules.yaml`
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `skills-manifest.json`
- Modify: `pyproject.toml`
- Modify: `tests/test_language_checker.py`
- Modify: `tests/test_fixers.py`
- Optional create: `tests/test_language_rules.py`

### Required Basic Rules

At minimum, Phase 1 must implement these rule families:

1. bracket mismatch
2. quote mismatch
3. book-title mark mixed style
4. unit spacing
5. ellipsis style
6. dash style
7. zh/en symbol spacing
8. number range style
9. enum punctuation style
10. simple connector blacklist

### Required Safe Fixes

At minimum, Phase 1 safe fix must cover:

1. cjk/latin spacing
2. repeated punctuation
3. unit spacing
4. ellipsis normalization
5. clearly safe fullwidth/halfwidth normalization

### Task 1.1: Normalize the Language Rule Schema

**Files:**
- Optional create: `core/language_rules.py`
- Modify: `90-rules/packs/tsinghua-thesis/rules.yaml`
- Modify: `90-rules/packs/university-generic/rules.yaml`
- Modify: `90-rules/packs/journal-generic/rules.yaml`

**Steps:**
1. Make every basic language rule object-based.
2. Support at least `enabled`, `severity`, and `autofix_safe`.
3. Allow rule-local `patterns` where needed.

**Verify:**
Run:
```bash
pytest tests/test_rules.py -q
```
Expected: rule packs still load and expose object-based language config.

### Task 1.2: Expand Deterministic Basic Language Checks

**Files:**
- Modify: `core/checkers.py`
- Modify: `11-check-language/check_language.py`
- Modify: `11-check-language/THESIS_CHECK_LANGUAGE.md`

**Steps:**
1. Add deterministic line-level checks for the required basic rules.
2. Keep findings in the current report model for Phase 1.
3. Avoid context-heavy heuristics in this layer.

**Verify:**
Run:
```bash
pytest tests/test_language_checker.py -q
python run_check_once.py --project-root examples/minimal-latex-project --ruleset university-generic --skip-compile
```
Expected: language report contains new issue codes and runner still works.

### Task 1.3: Expand Safe Fix Without Crossing Into Deep Review

**Files:**
- Modify: `core/fixers.py`
- Modify: `21-fix-language-style/fix_language_style.py`
- Modify: `21-fix-language-style/THESIS_FIX_LANGUAGE_STYLE.md`

**Steps:**
1. Add only low-risk replacements.
2. Keep file-level modifications predictable and reversible.
3. Document clearly which language findings remain suggestion-only.

**Verify:**
Run:
```bash
pytest tests/test_fixers.py -q
python run_fix_cycle.py --project-root examples/minimal-latex-project --ruleset university-generic --apply false
```
Expected: fix summary includes language step and no deep behavior exists yet.

### Task 1.4: Refresh Public Docs and Manifest

**Files:**
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `skills-manifest.json`
- Modify: `pyproject.toml`

**Steps:**
1. Describe `11-check-language` as a deterministic basic language lint layer.
2. Describe `21-fix-language-style` as safe fix only.
3. Keep versioning and public wording synchronized.

**Verify:**
Run:
```bash
pytest tests/test_manifest.py -q
```
Expected: manifest still points to real entries and docs match the current module set.

### Phase 1 Acceptance Criteria

Phase 1 is accepted only when:

1. Basic language layer supports at least 10 deterministic rule families.
2. Safe fix layer supports at least 5 low-risk fix families.
3. Rule packs expose object-based language rule config with `autofix_safe`.
4. `README`, `README.zh-CN.md`, `skills-manifest.json`, and `pyproject.toml` are version-consistent.
5. New or expanded language tests cover positive, negative, and boundary cases.
6. No deep checker or deep fixer behavior has been introduced yet.

---

## 5. Phase 2: v0.5.1 Deep Language Checker

### Goal

Add a report-only deep language review layer for Chinese thesis finalization.

### Files

- Create: `14-check-language-deep/THESIS_CHECK_LANGUAGE_DEEP.md`
- Create: `14-check-language-deep/check_language_deep.py`
- Modify: `core/common.py`
- Modify: `core/reports.py`
- Optional create: `core/language_deep.py`
- Optional create: `core/sentence_index.py`
- Optional create: `core/consistency.py`
- Optional create: `core/terminology.py`
- Optional create: `core/suggestion_ranker.py`
- Modify: `core/checkers.py`
- Modify: `run_check_once.py`
- Modify: `skills-manifest.json`
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `90-rules/packs/tsinghua-thesis/rules.yaml`
- Modify: `90-rules/packs/university-generic/rules.yaml`
- Modify: `90-rules/packs/journal-generic/rules.yaml`
- Create: `tests/test_language_deep_checker.py`
- Create: `tests/test_consistency.py`
- Optional create: `tests/data/language_deep_fixture/`

### Required Deep Issue Types

Phase 2 must launch with these four categories:

1. connector misuse
2. collocation misuse
3. terminology consistency
4. acronym first-use

### Required Deep Finding Fields

Every deep finding must include:

- `severity`
- `code`
- `file`
- `line`
- `span`
- `message`
- `evidence`
- `suggestions`
- `confidence`
- `review_required`
- `category`

### Task 2.1: Extend the Finding and Report Model

**Files:**
- Modify: `core/common.py`
- Modify: `core/reports.py`

**Steps:**
1. Keep basic finding compatibility intact.
2. Add optional fields needed by deep review.
3. Ensure JSON payloads remain stable for both old and new consumers.

**Verify:**
Run:
```bash
pytest tests/test_runner.py tests/test_manifest.py -q
```
Expected: existing summaries still work and new deep fields are serializable.

### Task 2.2: Build Sentence, Span, and Terminology Infrastructure

**Files:**
- Optional create: `core/sentence_index.py`
- Optional create: `core/terminology.py`
- Optional create: `core/consistency.py`
- Optional create: `core/suggestion_ranker.py`

**Steps:**
1. Index sentence spans within source text.
2. Extract candidate terminology and acronym occurrences.
3. Support aggregated consistency output for repeated variants.
4. Rank replacement suggestions down to a small list.

**Verify:**
Run:
```bash
pytest tests/test_consistency.py -q
```
Expected: terminology and consistency logic are testable without mutating files.

### Task 2.3: Implement the Deep Checker Entry Point

**Files:**
- Create: `14-check-language-deep/check_language_deep.py`
- Create: `14-check-language-deep/THESIS_CHECK_LANGUAGE_DEEP.md`
- Optional create: `core/language_deep.py`
- Modify: `core/checkers.py`

**Steps:**
1. Implement report-only deep detection.
2. Cover the four launch categories.
3. Keep confidence thresholds and `review_required` driven by rules.

**Verify:**
Run:
```bash
pytest tests/test_language_deep_checker.py -q
```
Expected: deep reports contain the required finding fields and no files are modified.

### Task 2.4: Integrate Deep Checker Into Runner and Manifest

**Files:**
- Modify: `run_check_once.py`
- Modify: `skills-manifest.json`
- Modify: `README.md`
- Modify: `README.zh-CN.md`

**Steps:**
1. Register `14-check-language-deep` in the manifest.
2. Add runner support for `language-deep` without breaking current behavior.
3. Support a focused invocation path such as `--only language-deep` or a language mode flag.

**Verify:**
Run:
```bash
python run_check_once.py --project-root examples/minimal-latex-project --ruleset university-generic --only language-deep
```
Expected: deep report is generated independently of safe fix.

### Phase 2 Acceptance Criteria

Phase 2 is accepted only when:

1. `14-check-language-deep` exists in code, manifest, docs, and runner.
2. Deep checker supports the four launch issue categories.
3. Deep findings include `span`, `evidence`, `suggestions`, `confidence`, and `review_required`.
4. Deep checker does not mutate source files.
5. Rule packs expose `language_deep` and `consistency` sections with at least `enabled`, `severity`, `min_confidence`, and `review_required`.
6. Tests cover both issue detection and non-trigger cases.

---

## 6. Phase 3: v0.5.2 Deep Language Fixer

### Goal

Convert deep findings into validated patches, preview output, and selective apply controls without collapsing into auto-rewrite behavior.

### Files

- Create: `24-fix-language-deep/THESIS_FIX_LANGUAGE_DEEP.md`
- Create: `24-fix-language-deep/fix_language_deep.py`
- Optional create: `core/patches.py`
- Modify: `core/fixers.py`
- Modify: `run_fix_cycle.py`
- Modify: `skills-manifest.json`
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Create: `tests/test_patch_preview.py`
- Create: `tests/test_language_deep_fixer.py`
- Optional create: `tests/data/patch_cases/`

### Required Patch Fields

Every patch object must include:

- `file`
- `start`
- `end`
- `old_text`
- `new_text`
- `issue_code`
- `confidence`

### Required Deep Fix Behaviors

Phase 3 must support:

1. patch preview generation
2. selective apply
3. old_text validation
4. overlap/conflict detection
5. skip `review_required=true` by default
6. fix report output

### Task 3.1: Implement Patch Data Model and Validation

**Files:**
- Optional create: `core/patches.py`

**Steps:**
1. Convert deep findings into span-based patches.
2. Validate `old_text` before apply.
3. Detect overlapping or conflicting edits.

**Verify:**
Run:
```bash
pytest tests/test_patch_preview.py -q
```
Expected: patch generation and conflict handling are stable.

### Task 3.2: Implement Deep Fix CLI

**Files:**
- Create: `24-fix-language-deep/fix_language_deep.py`
- Create: `24-fix-language-deep/THESIS_FIX_LANGUAGE_DEEP.md`
- Modify: `core/fixers.py`

**Steps:**
1. Read deep checker reports.
2. Generate preview output by default.
3. Apply only selected or allowed patches when explicitly requested.

**Verify:**
Run:
```bash
pytest tests/test_language_deep_fixer.py -q
```
Expected: default behavior is preview-only and review-required findings are skipped.

### Task 3.3: Integrate Deep Fix Into Runner

**Files:**
- Modify: `run_fix_cycle.py`
- Modify: `skills-manifest.json`
- Modify: `README.md`
- Modify: `README.zh-CN.md`

**Steps:**
1. Register `24-fix-language-deep`.
2. Add an apply mode contract such as `safe|suggest|mixed`.
3. Keep existing safe fix path unchanged.

**Verify:**
Run:
```bash
python run_fix_cycle.py --project-root examples/minimal-latex-project --ruleset university-generic --apply false --apply-mode suggest
```
Expected: deep patch preview is generated and source files are not changed.

### Phase 3 Acceptance Criteria

Phase 3 is accepted only when:

1. `24-fix-language-deep` exists in code, manifest, docs, and runner.
2. Patch preview is the default deep-fix behavior.
3. `review_required=true` findings are skipped unless explicitly overridden later.
4. Patch conflicts and `old_text` mismatches are reported rather than silently applied.
5. Safe fix and deep fix remain separate execution paths.
6. Tests cover patch generation, selective apply, mismatch handling, and overlap rejection.

---

## 7. Release Gate Checklist

### 7.1 Gate for Starting Execution

Do not start implementation until this plan is accepted and the following decisions remain unchanged:

1. Phase 0 is mandatory before feature work.
2. v0.5 is split into `0.5.0`, `0.5.1`, `0.5.2`.
3. Deep layer stays review-first, not auto-rewrite-first.
4. No heavy runtime dependency is added without an explicit separate decision.

### 7.2 Gate for Cutting `v0.5.0`

- Phase 0 and Phase 1 both passed.
- New basic language docs are published.
- Manifest, README, and package version are in sync.

### 7.3 Gate for Cutting `v0.5.1`

- Phase 2 passed.
- Deep checker reports are stable.
- No deep mutations happen during check runs.

### 7.4 Gate for Cutting `v0.5.2`

- Phase 3 passed.
- Patch preview and selective apply are both stable.
- Safe fix remains isolated from deep fix.

---

## 8. Out of Scope for This Plan

The following are explicitly deferred:

- LLM sentence rewriting
- AI-detection-rate reduction features
- PDF-first checking pipeline
- VS Code panel or standalone GUI
- full Word/Markdown/LaTeX unified deep parser
- broad university/journal pack expansion beyond what v0.5 needs
- end-to-end terminology external config plugin system

---

## 9. Recommended Execution Order

1. Execute Phase 0 and cut a clean baseline branch.
2. Execute Phase 1 and release `v0.5.0`.
3. Execute Phase 2 and release `v0.5.1`.
4. Execute Phase 3 and release `v0.5.2`.
5. Only after all three releases, revisit v0.6 pluginization or heavier language analysis.

---

## 10. Execution Notes for the Maintainer

- Phase 0 is not optional. It removes avoidable friction before the real language work begins.
- Phase 1 delivers visible user value fastest and should be the first actual feature milestone.
- Phase 2 depends on expanding `Finding` and report shape cleanly; do not hack deep fields into ad hoc dicts.
- Phase 3 should operate on validated spans, not file-wide regex replacement.
- Keep each phase shippable on its own branch and release note.
