# Thesis Skills Architecture

## Positioning

`thesis-skills` is not a general writing assistant and not a thesis template.

It is a deterministic workflow layer for academic writing projects that need:

- bibliography intake from external tools such as Zotero and EndNote
- Word-to-LaTeX migration support
- bounded LaTeX-to-Word export support for review-oriented workflows
- bounded review-loop workflows for revision rounds and feedback handling
- bounded compile-log parsing for friendlier build diagnostics
- bounded pre-submission gating from existing workflow artifacts
- repeatable, inspectable checks
- bounded, report-driven fixes
- reusable rule packs for schools and journals

The repository is designed around explicit artifacts and narrow tool contracts.
Checkers write reports. Fixers read reports. Rule packs provide policy. Runners
orchestrate the sequence, but do not redefine the meaning of lower-level tools.

## Multi-Layer Model

The current repository is easiest to understand as layered workflows:

1. Bibliography intake
2. Word-to-LaTeX migration
3. LaTeX-to-Word export
4. Review-loop workflows
5. Compile-log diagnostics
6. Pre-submission gating
7. Deterministic checking
8. Report-driven fixing
9. Rule-pack onboarding and reuse

These layers map to concrete folders and scripts rather than abstract concepts.

## Repository Map

```text
thesis-skills/
├── 00-bib-endnote/           EndNote intake and preflight checks
├── 00-bib-zotero/            Zotero bibliography and Word-sync workflows
├── 01-word-to-latex/         Structured migration from Word exports to LaTeX
├── 02-latex-to-word/         Bounded LaTeX-to-Word export workflow
├── 03-latex-review-diff/      Review package and triage workflow
├── 04-word-review-ingest/     Bounded feedback normalization workflow
├── 15-check-compile/          Compile-log diagnostics
├── 16-check-readiness/        Pre-submission readiness gate
├── 10-check-references/       Deterministic reference checks
├── 11-check-language/        Baseline language checks
├── 12-check-format/          Format checks
├── 13-check-content/         Content checks
├── 14-check-language-deep/   Report-only deep language review
├── 20-fix-references/        Reference fixes
├── 21-fix-language-style/    Low-risk language fixes
├── 22-fix-format-structure/  Format fixes
├── 24-fix-language-deep/     Deep patch preview and selective apply
├── 90-rules/                 Rule pack definitions and generators
├── adapters/                 Intake guidance and optional integration notes
├── core/                     Shared implementation layer
├── examples/                 Example LaTeX projects
├── tests/                    Unit and workflow regression tests
├── run_check_once.py         One-pass checker runner
└── run_fix_cycle.py          Fix-cycle runner
```

## Layer Details

### 1. Bibliography Intake

Purpose:

- normalize references coming from external tools
- preserve stable `refNNN` allocation
- generate auditable JSON reports

Main entrypoints:

- `00-bib-endnote/import_library.py`
- `00-bib-endnote/check_endnote_export.py`
- `00-bib-zotero/check_bib_quality.py`
- `00-bib-zotero/sync_from_word.py`

Core support:

- `core/citation_models.py`
- `core/canonicalize.py`
- `core/citation_mapping.py`
- `core/endnote_xml.py`
- `core/endnote_ris.py`
- `core/bib_render.py`
- `core/match_refs.py`
- `core/zotero_extract.py`

### 2. Word-to-LaTeX Migration

Purpose:

- convert exported or semi-structured Word project assets into a LaTeX project
- keep mappings explicit instead of hiding migration policy in heuristics

Main entrypoint:

- `01-word-to-latex/migrate_project.py`

Core support:

- `core/migration.py`

### 3. LaTeX-to-Word Export

Purpose:

- produce a review-friendly `.docx` from a LaTeX thesis project
- surface unsupported constructs explicitly rather than hiding them
- keep export policy separate from conversion mechanism

Main entrypoint:

- `02-latex-to-word/migrate_project.py`

Core support:

- `core/migration.py`
- `core/export_profiles.py`

Important boundary:

- `review-friendly` is the only first-class implemented export mode in `v0.6.x`
- `submission-friendly` exists as a profile contract but is not yet fully implemented
- export reports are mandatory; dry-run without `--apply` is the default

### 4. Review-Loop Workflows

Purpose:

- generate review-package and triage artifacts from the current thesis state
- normalize bounded feedback into structured issues, TODOs, and candidate patches
- record revision-round outcomes without collapsing into live collaboration tooling

Main entrypoints:

- `03-latex-review-diff/review_diff.py`
- `04-word-review-ingest/feedback_ingest.py`

Core support:

- `core/review_queue.py`
- `core/review_clusters.py`
- `core/review_loop.py`
- `core/reports.py`

Important boundary:

- the review loop preserves explicit artifacts and review-gated ambiguity
- it does not replace Word, Overleaf, or Google Docs collaboration

### 5. Compile-Log Diagnostics

Purpose:

- translate raw LaTeX compile logs into structured findings
- preserve build-blocking versus warning-level distinctions
- keep compile support bounded to parsing and discovery rather than full orchestration

Main entrypoint:

- `15-check-compile/check_compile.py`

Core support:

- `core/compile_parser.py`
- `core/checkers.py`

Important boundary:

- this layer parses existing compile artifacts; it is not a replacement for `latexmk`, `xelatex`, or `bibtex`
- missing logs should be reported explicitly rather than masked

### 6. Pre-Submission Gating

Purpose:

- aggregate existing workflow artifacts into a bounded readiness verdict
- distinguish blockers, warnings, and missing evidence explicitly
- stay downstream of checking, fixing, compile parsing, export, and review workflows

Main entrypoint:

- `16-check-readiness/check_readiness.py`

Core support:

- `core/readiness_gate.py`

Important boundary:

- the gate is a summarizing decision layer, not a second hidden orchestrator
- it must reuse existing structured artifacts instead of re-implementing lower-level analysis
- missing evidence should remain visible rather than being treated as `PASS`

### 7. Deterministic Checking

Purpose:

- detect concrete issues and write structured reports
- keep source files unchanged
- keep rule interpretation deterministic and reproducible

Main entrypoints:

- `10-check-references/check_references.py`
- `11-check-language/check_language.py`
- `12-check-format/check_format.py`
- `13-check-content/check_content.py`
- `14-check-language-deep/check_language_deep.py`

Core support:

- `core/checkers.py`
- `core/common.py`
- `core/language_rules.py`
- `core/language_deep.py`
- `core/consistency.py`
- `core/sentence_index.py`
- `core/terminology.py`
- `core/reports.py`

Important boundary:

- `11-check-language` is the baseline deterministic lint layer
- `14-check-language-deep` is a structured screening layer for higher-order
  language issues
- deep findings are intentionally not equivalent to final editorial judgment

### 8. Report-Driven Fixing

Purpose:

- read existing reports
- generate bounded edits
- support dry-run preview before apply

Main entrypoints:

- `20-fix-references/fix_references.py`
- `21-fix-language-style/fix_language_style.py`
- `22-fix-format-structure/fix_format_structure.py`
- `24-fix-language-deep/fix_language_deep.py`

Core support:

- `core/fixers.py`
- `core/patches.py`

Important boundary:

- safe fixers and deep fixers stay separated
- deep patches validate spans and skip `review_required` items by default
- the system prefers conservative edits over broad rewrites

### 9. Rule-Pack Onboarding And Reuse

Purpose:

- keep school- and journal-specific policy out of runner code
- make onboarding reproducible
- allow reuse beyond a single thesis template

Main entrypoints:

- `90-rules/create_pack.py`
- `90-rules/create_draft_pack.py`

Core support:

- `core/rules.py`
- `core/pack_generator.py`
- `core/yamlish.py`

## Shared Core Contracts

### Project Discovery

`core/project.py` discovers:

- main TeX file
- chapter files
- bibliography files
- report output directory

That discovery is driven by rule-pack configuration rather than hard-coded
project assumptions.

### Reports As Contracts

A checker should emit a structured report.
A fixer should read a report and produce bounded edits.

This is the main contract that keeps the repository inspectable.

In practice that means:

- checkers do not silently mutate source files
- fixers do not invent their own scan phase when a checker report already exists
- runners summarize orchestration results instead of owning domain logic

### Rule Packs As Policy

Rule packs define policy such as:

- project layout assumptions
- reference severities
- language rule enablement
- formatting requirements
- content requirements

The repository should keep policy in rule packs whenever possible and only keep
generic mechanics in `core/`.

## Runner Responsibilities

### `run_check_once.py`

Responsibilities:

- load the selected rule pack
- discover the target project
- run checkers in a stable order
- write `reports/run-summary.json`

Non-responsibilities:

- it should not redefine checker semantics
- it should not silently repair files

### `run_fix_cycle.py`

Responsibilities:

- read reports already produced for a project
- select the safe path, deep path, or mixed path
- write `reports/fix-summary.json`

Non-responsibilities:

- it should not blur safe fixes and deep review into one undifferentiated step
- it should not auto-apply review-oriented deep patches by default

## Current Product Boundaries

### What Thesis Skills Is Good At

- repeatable bibliography intake
- deterministic structural checks
- conservative automatic fixes
- review-friendly patch preview
- configurable rule-pack workflows

### What Thesis Skills Is Not

- a full thesis template distribution
- a GUI-first editing tool
- a general-purpose AI writing assistant
- a final thesis sign-off system

The `deep language` path in particular should be described as a
high-confidence screening assistant plus human review aid. It is valuable for
first-pass review and auditability, but it should not be treated as the sole
basis for final thesis language polish.

## Recommended Entry Paths

### EndNote User

1. Run EndNote export preflight
2. Dry-run import
3. Apply import
4. Run `run_check_once.py`
5. Run `run_fix_cycle.py` in preview mode

### Zotero + Word User

1. Sync citations from Word
2. Run bibliography quality check
3. Run `run_check_once.py`
4. Review reports and optional fix previews

### Existing LaTeX Project

1. Choose or create a rule pack
2. Run `run_check_once.py`
3. Apply safe fixes conservatively
4. Use deep review as a screening layer, not a final gate

### Rule-Pack Author

1. Start from `university-generic` or `journal-generic`
2. Adjust `pack.yaml`, `rules.yaml`, and `mappings.yaml`
3. Validate on `examples/minimal-latex-project`
4. Add tests before expanding scope

## Extension Rules

When adding new functionality, prefer these rules:

- add new checks as explicit checker modules
- add new fixes as explicit fixer modules
- keep reports auditable
- keep fixes conservative and reversible
- avoid mixing product policy into runners
- avoid over-claiming what deep language review can guarantee

## Verification

The repository relies on:

- unit tests in `tests/`
- workflow tests for runners and import paths
- example-project smoke flows

Recommended baseline command:

```bash
python -m unittest discover -s tests -p "test_*.py"
```
