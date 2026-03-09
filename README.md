# Thesis Skills

Chinese README: [README.zh-CN.md](README.zh-CN.md)

`Thesis Skills` is a `Python + Skills` workflow repository for thesis writing, journal submission, template onboarding, manuscript formatting review, and `Word -> LaTeX` migration.

It is an executable workflow that turns academic writing policies into deterministic checks, report-driven fixes, and reusable rule packs.

## Table of Contents

- [Overview](#overview)
- [Project Highlights](#project-highlights)
- [Very Simple Start](#very-simple-start)
- [OpenClaw Support](#openclaw-support)
- [Main Capabilities](#main-capabilities)
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

This makes the repository useful for:

- students preparing theses or dissertations
- authors preparing journal submissions
- supervisors, reviewers, or editors who want to pre-check formatting and consistency
- teams onboarding new university or journal templates

## Project Highlights

- deterministic `check -> report -> fix` loop
- explicit `Word -> LaTeX` migration contracts
- reusable rule packs for schools and journals
- safe, minimal fixes instead of whole-document rewrites
- one-click OpenClaw skill installation support
- beginner-friendly entrypoints for people who do not want to learn the full repository layout first

## Very Simple Start

If you are new and just want the easiest path, use one of these:

### Option A: You already have a LaTeX project

```bash
python run_check_once.py --project-root <your-latex-project> --ruleset university-generic --skip-compile
```

Then, if you want a safe preview of suggested fixes:

```bash
python run_fix_cycle.py --project-root <your-latex-project> --ruleset university-generic --apply false
```

### Option B: You want OpenClaw support with one command

```bash
python install_openclaw.py
```

This installs generated skill folders into `~/.openclaw/skills`.

### Option C: You have a Word draft

1. Fill in `migration.json`
2. Run:

```bash
python 01-word-to-latex/migrate_project.py --source-root <intake> --target-root <latex-project> --spec <migration.json> --apply false
```

## OpenClaw Support

Yes, this project can work with OpenClaw.

OpenClaw supports local skill folders that contain `SKILL.md`. This repository now includes a one-click installer:

```bash
python install_openclaw.py
```

What it does:

- reads `skills-manifest.json`
- generates OpenClaw-compatible skill folders
- installs them into `~/.openclaw/skills` by default

If you want a custom install target:

```bash
python install_openclaw.py --target /path/to/openclaw/skills
```

## Main Capabilities

### 1. Deterministic checking

The repository can check:

- bibliography quality
- missing citation keys and orphan bibliography entries
- CJK/Latin spacing and repeated punctuation
- figure/table captions, labels, and broken refs
- required sections and abstract keyword counts

### 2. Report-driven fixing

Instead of asking AI to rewrite the document, fixers read structured reports and only apply bounded, mechanical changes.

### 3. Word-to-LaTeX migration

Migration is explicit. It preserves:

- document metadata
- Word style intent
- chapter-role mappings
- bibliography-source context

### 4. Rule-pack onboarding

The project can scaffold a new pack from uploaded-material metadata, then let you refine it against real samples.

### 5. Review and quality-gate use

This repository is not only useful for authors. Reviewers, supervisors, and editorial support staff can also use it to check whether a manuscript appears to follow a target formatting policy before deeper review.

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

- export or organize chapter assets and bibliography files
- create `migration.json`
- run `01-word-to-latex/migrate_project.py`
- run `run_check_once.py` and then `run_fix_cycle.py`

### 2. You already have a LaTeX project

- choose a pack such as `university-generic` or `tsinghua-thesis`
- run `run_check_once.py`
- review generated reports
- run `run_fix_cycle.py` for safe, minimal changes

### 3. You need to onboard a new university or journal

- gather the official guide, template, and compliant sample
- fill in `adapters/intake/example-intake.json` style metadata
- run `90-rules/create_draft_pack.py`
- refine the generated pack and validate it against sample projects

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
├── install_openclaw.py         # One-click OpenClaw installer
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

### Install OpenClaw skills

```bash
python install_openclaw.py
```

## Enhanced Intake Schema

The current `migration.json` supports explicit metadata instead of only raw file-copy instructions.

Supported top-level fields:

- `document_metadata`
- `word_style_mappings`
- `chapter_role_mappings`
- `chapter_mappings`
- `bibliography_mappings`

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

`thesis-skills` is an AI + Python infrastructure layer for migration, compliance, checking, fixing, and onboarding academic writing workflows.
