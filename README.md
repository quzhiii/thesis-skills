# Thesis Skills

`Thesis Skills` is a `Python + Skills` workflow repository for thesis writing, journal submission, template onboarding, and `Word -> LaTeX` migration.

It is not a prompt bundle. It is an executable, testable workflow that turns academic writing policies into deterministic checks, report-driven fixes, and reusable rule packs.

## Table of Contents

- [Overview](#overview)
- [Why This Project Exists](#why-this-project-exists)
- [Advantages](#advantages)
- [Technical Roadmap](#technical-roadmap)
- [Common Use Cases](#common-use-cases)
- [Repository Layout](#repository-layout)
- [Quick Start](#quick-start)
- [Enhanced Intake Schema](#enhanced-intake-schema)
- [Adapting Other Universities and Journals](#adapting-other-universities-and-journals)
- [Template Links](#template-links)
- [Detailed Architecture Doc](#detailed-architecture-doc)
- [Current Status](#current-status)

## Overview

`thesis-skills` focuses on the parts of academic writing that are repetitive, error-prone, and suitable for structured automation.

It gives you:

- `Word -> LaTeX` migration helpers
- deterministic checkers for references, language, format, and content structure
- safe fixers driven by JSON reports instead of freeform rewriting
- YAML rule packs for universities and journals
- draft-pack scaffolding from uploaded-material metadata

This makes the repository useful as:

- a migration assistant
- a template onboarding toolkit
- a thesis and journal quality gate
- an AI + Python collaboration layer for academic writing workflows

## Why This Project Exists

Most AI writing helpers stop at prompting. That is useful for brainstorming, but weak for long-lived, policy-heavy workflows such as dissertations and journal submissions.

This project separates responsibilities clearly:

1. Python handles deterministic scanning, file discovery, rule evaluation, and report generation.
2. Skills handle orchestration, interpretation, and selective human-in-the-loop editing.
3. Rule packs hold school- and journal-specific requirements in reusable form.

Instead of asking a model to remember an entire style guide, you encode what can be encoded and keep AI focused on the parts where AI is actually helpful.

## Advantages

### 1. Executable workflow instead of prompt-only behavior

The main loop is real code: `run_check_once.py`, `run_fix_cycle.py`, deterministic checkers, and starter packs. That makes the workflow more stable and more verifiable.

### 2. Clear split between AI work and deterministic work

- Python does scanning, matching, rule evaluation, and report output.
- Skills and AI help with interpretation, migration decisions, and minimal edits.

This reduces hallucination while preserving flexibility.

### 3. Reusable beyond one school

The repository already includes:

- `tsinghua-thesis`
- `university-generic`
- `journal-generic`

So the structure is ready for additional universities, departments, and journals.

### 4. Migration and policy are separate layers

`01-word-to-latex` moves assets into a project. `90-rules` defines policy. `run_check_once.py` and `run_fix_cycle.py` consume project state plus rules. This keeps the system easier to understand and extend.

### 5. Beginner-friendly while still engineering-grade

Users can start with one-click commands, while contributors still get explicit module boundaries, tests, examples, and contracts.

## Technical Roadmap

```text
Uploaded materials or existing LaTeX project
    |
    +-- official guide / template / sample / bibliography exports
    v
adapters/intake/
    |
    +-- example-intake.json
    +-- migration.json
    v
01-word-to-latex/migrate_project.py
    |
    +-- document_metadata
    +-- word_style_mappings
    +-- chapter_role_mappings
    +-- chapter_mappings
    +-- bibliography_mappings
    v
Target LaTeX project
    |
    +-- run_check_once.py
           |
           +-- 00-bib-zotero/check_bib_quality.py
           +-- 10-check-references/check_references.py
           +-- 11-check-language/check_language.py
           +-- 12-check-format/check_format.py
           +-- 13-check-content/check_content.py
           v
         JSON reports
           |
           +-- run_fix_cycle.py
                  |
                  +-- 20-fix-references/fix_references.py
                  +-- 21-fix-language-style/fix_language_style.py
                  +-- 22-fix-format-structure/fix_format_structure.py
                  v
                Minimal fixes

Uploaded-material metadata
    |
    +-- pack_id / display_name / starter / sources / mappings
    v
90-rules/create_draft_pack.py
    v
90-rules/packs/<ruleset>/
    |
    +-- pack.yaml
    +-- rules.yaml
    +-- mappings.yaml
    +-- draft-notes.md
```

## Common Use Cases

### 1. You already have a Word draft

- Export or organize chapter assets and bibliography files
- Create `migration.json`
- Run `01-word-to-latex/migrate_project.py`
- Run `run_check_once.py` and then `run_fix_cycle.py`

### 2. You already have a LaTeX project

- Choose an existing pack such as `university-generic` or `tsinghua-thesis`
- Run `run_check_once.py`
- Review the generated reports
- Run `run_fix_cycle.py` for safe, minimal changes

### 3. You need to onboard a new university or journal

- Gather the official guide, template, and compliant sample
- Fill in `adapters/intake/example-intake.json` style metadata
- Run `90-rules/create_draft_pack.py`
- Refine the generated pack and validate it against sample projects

## Repository Layout

```text
thesis-skills/
├── 00-bib-zotero/              # Zotero bibliography intake checks
├── 00-bib-endnote/             # EndNote bibliography workflow docs
├── 01-word-to-latex/           # Word -> LaTeX migration entrypoint
├── 10-check-references/        # Citation integrity checks
├── 11-check-language/          # Language and spacing checks
├── 12-check-format/            # Figure/table/ref/format checks
├── 13-check-content/           # Content structure checks
├── 20-fix-references/          # Report-driven reference fixes
├── 21-fix-language-style/      # Report-driven language fixes
├── 22-fix-format-structure/    # Report-driven format fixes
├── 90-rules/                   # Rulesets and pack generators
├── 99-runner/                  # Runner documentation
├── adapters/intake/            # User-provided intake metadata
├── core/                       # Deterministic core logic
├── docs/                       # Architecture and supporting docs
├── examples/                   # Minimal runnable examples
├── tests/                      # Regression tests
├── run_check_once.py           # One-click check runner
└── run_fix_cycle.py            # One-click fix runner
```

## Quick Start

### Run a full deterministic check pass

```bash
python run_check_once.py --project-root examples/minimal-latex-project --ruleset university-generic --skip-compile
```

### Preview minimal fixes from reports

```bash
python run_fix_cycle.py --project-root examples/minimal-latex-project --ruleset university-generic --apply false
```

### Generate a draft pack from uploaded-material metadata

```bash
python 90-rules/create_draft_pack.py --intake adapters/intake/example-intake.json
```

### Migrate intake assets into a target LaTeX project

```bash
python 01-word-to-latex/migrate_project.py --source-root <intake> --target-root <latex-project> --spec <migration.json> --apply false
```

## Enhanced Intake Schema

The current `migration.json` supports explicit metadata instead of only raw file-copy instructions.

Supported top-level fields:

- `document_metadata`
- `word_style_mappings`
- `chapter_role_mappings`
- `chapter_mappings`
- `bibliography_mappings`

Example:

```json
{
  "document_metadata": {
    "source_format": "word-exported-tex",
    "bibliography_source": "zotero",
    "template_family": "university-generic"
  },
  "word_style_mappings": [
    {"style": "Heading 1", "role": "chapter", "latex_command": "chapter"},
    {"style": "Heading 2", "role": "section", "latex_command": "section"}
  ],
  "chapter_role_mappings": [
    {"source": "chapters/chapter1.tex", "role": "introduction", "target": "chapters/01-introduction.tex"}
  ],
  "chapter_mappings": [
    {"from": "chapters/chapter1.tex", "to": "chapters/01-introduction.tex", "role": "introduction", "word_style": "Heading 1"}
  ],
  "bibliography_mappings": [
    {"from": "refs-import.bib", "to": "ref/refs-import.bib"}
  ]
}
```

## Adapting Other Universities and Journals

To onboard another school or journal, prepare as many of these as possible:

- official writing guide: `PDF`, `HTML`, or plain text
- official template: `DOCX`, `DOTX`, `CLS`, `STY`, or `TEX`
- at least one compliant sample: source preferred, otherwise `PDF`
- optional style files: `BST`, `BBX`, `CBX`, `CSL`
- optional screenshots: title page, abstract page, figure/table pages, references page

Recommended starting points:

- start from `90-rules/packs/university-generic/` for theses
- start from `90-rules/packs/journal-generic/` for journals

## Template Links

Use these as jump-off repositories before migration or rule-pack onboarding. Always double-check against the latest official guide.

### China

- Tsinghua University - `tuna/thuthesis` - https://github.com/tuna/thuthesis
- Shanghai Jiao Tong University - `sjtug/SJTUThesis` - https://github.com/sjtug/SJTUThesis
- USTC - `ustctug/ustcthesis` - https://github.com/ustctug/ustcthesis
- UESTC - `tinoryj/UESTC-Thesis-Latex-Template` - https://github.com/tinoryj/UESTC-Thesis-Latex-Template
- UCAS - `mohuangrui/ucasthesis` - https://github.com/mohuangrui/ucasthesis
- Peking University - `CasperVector/pkuthss` and maintained forks such as `Thesharing/pkuthss`

### International

- Stanford University - `dcroote/stanford-thesis-example` - https://github.com/dcroote/stanford-thesis-example
- University of Cambridge - `cambridge/thesis` - https://github.com/cambridge/thesis
- University of Oxford - `mcmanigle/OxThesis` - https://github.com/mcmanigle/OxThesis
- EPFL - `HexHive/thesis_template` - https://github.com/HexHive/thesis_template
- ETH Zurich - `tuxu/ethz-thesis` - https://github.com/tuxu/ethz-thesis
- MIT (widely used unofficial) - `alinush/mit-thesis-template` - https://github.com/alinush/mit-thesis-template

## Detailed Architecture Doc

For a more detailed explanation of runners, rule packs, intake flow, pack lifecycle, and check/fix sequencing, see `docs/architecture.md`.

## Current Status

The repository currently provides:

- a working `check -> fix` loop
- a working `Word -> LaTeX` migration entrypoint
- a working `uploaded materials -> draft pack` scaffold path
- starter packs for `tsinghua-thesis`, `university-generic`, and `journal-generic`
- regression tests covering the main flow

In one sentence:

`thesis-skills` is not an AI thesis writer; it is an AI + Python infrastructure layer for migration, compliance, checking, fixing, and onboarding academic writing workflows.
