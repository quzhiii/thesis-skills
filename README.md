# Thesis Skills

![Python](https://img.shields.io/badge/python-3.x-blue?logo=python&logoColor=white)
![License](https://img.shields.io/github/license/quzhiii/thesis-skills)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20linux%20%7C%20macos-lightgrey)
![No dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)

Deterministic thesis QA and migration workflows for `Word -> LaTeX`, citation integrity, CJK language checks, format validation, and reusable university rulesets.

[中文说明](README.zh-CN.md)

> Looking for the student-facing Word plugin?
> Use the separate repository: `thu-word-plugin-lite`.

---

## What This Repo Is

`thesis-skills` is the **skills and automation** repository in the overall thesis toolchain.

- It helps you migrate from Word to LaTeX.
- It runs deterministic checks on bibliography, language, structure, and formatting.
- It turns institutional policies into reusable YAML rulesets.
- It supports OpenCode / Claude / OpenClaw-style workflows.

This repository is built for people who want a reproducible pipeline, not a black-box writing assistant.

---

## What It Does

| Does | Does Not |
|---|---|
| Validate `\cite{key}` against `.bib` files | Rewrite your thesis arguments |
| Detect orphan bibliography entries | Change methods or conclusions |
| Check CJK punctuation and quote consistency | Freely edit full chapters |
| Verify figures, tables, labels, and refs | Replace advisor review |
| Scan symbols and abbreviations | Judge academic merit |
| Enforce school-specific rules through YAML | Handle final Word plugin distribution |

---

## Repository Boundary

This repo owns the **technical workflow layer**:

- migration helpers
- deterministic checkers
- report-driven fixers
- rulesets and pack generation
- Word automation specs and Pro planning skeleton

It does **not** own the end-user Word Ribbon add-in distribution. That lives in `thu-word-plugin-lite`.

---

## Core Modules

```text
thesis-skills/
├── 00-zotero/      # Zotero bibliography quality checks
├── 00-endnote/     # EndNote export workflow guidance
├── 01-migrate/     # Word -> LaTeX migration workflow
├── 02-content/     # Structure, abstract, symbols, abbreviations
├── 03-references/  # Citation integrity and bibliography hygiene
├── 04-language/    # CJK punctuation and language checks
├── 05-format/      # Labels, refs, figures, tables, structure
├── 06-rules/       # Reusable YAML rulesets
└── 07-word/        # Word technical specs, Lite backup, Pro skeleton
```

### Module Roles

- `00-zotero`: validates exported `.bib` files before they enter the migration/check pipeline
- `00-endnote`: guides EndNote users through export normalization before validation
- `01-migrate`: converts Word-exported LaTeX into a cleaner thesis-project layout
- `02-content`: checks structure, abstracts, symbols, and abbreviations
- `03-references`: validates citation keys and bibliography consistency
- `04-language`: enforces CJK language and punctuation hygiene
- `05-format`: validates figures, tables, labels, cross-references, and structural mechanics
- `06-rules`: isolates school and journal policy into reusable configuration packs
- `07-word`: keeps Word-related specs and the Pro automation direction inside the skills repo

---

## Quick Start

### Existing LaTeX project

```bash
python run_check_once.py --project-root "../your-thesis-project" --rules tsinghua --skip-compile
```

### Tsinghua `thuthesis`

```bash
python run_check_once.py --project-root "../thuthesis-v7.6.0" --rules tsinghua
```

### OpenClaw install

```bash
python install_openclaw.py
```

---

## Technical Flow

```text
Word draft / existing LaTeX project
    |
    +-- migration metadata / bibliography exports / school rules
    v
01-migrate/ + intake metadata
    |
    v
Target LaTeX project
    |
    +-- run_check_once.py
           |
           +-- 00-zotero
           +-- 03-references
           +-- 04-language
           +-- 05-format
           +-- 02-content
           v
         JSON reports
```

The key design principle is simple: **AI explains and assists, while code validates and constrains.**

---

## Rulesets and Extensibility

Rules live under `06-rules/rules/<ruleset>/`.

To support another university or journal, you mainly adapt:

- `format.yaml`
- `citation.yaml`
- `structure.yaml`
- `language.yaml`

This keeps policy separate from code, which is what makes the repository reusable.

---

## Current Status

- Working deterministic `check` pipeline
- Word-to-LaTeX migration workflow
- Ruleset-based architecture for new schools and journals
- OpenClaw installation support
- Word technical module retained inside `07-word/` for backup/spec/prototyping

---

## Related Repo

- `thu-word-plugin-lite`: end-user Word Ribbon add-in for one-click formatting

---

## License

See [LICENSE](LICENSE). Third-party notices are in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
