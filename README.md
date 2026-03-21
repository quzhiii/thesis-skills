# Thesis Skills

![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)
![License](https://img.shields.io/github/license/quzhiii/thesis-skills)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20linux%20%7C%20macos-lightgrey)

Chinese README: [README.zh-CN.md](README.zh-CN.md)

`thesis-skills` is a deterministic workflow repository for thesis and journal writing. It combines Python runners, reusable skill modules, report-driven fixers, and rulesets so that academic writing policies become executable instead of purely advisory.

`v0.3.0` is the release that makes the public repository clearer: stronger architecture, bilingual docs, tested runners, and a practical bibliography path that treats Zotero and EndNote with explicit support levels.

> Looking for the student-facing Word plugin?
> Use the separate repository: `thu-word-plugin-lite`.

## Why This Repo Exists

Most academic writing tooling fails in one of two ways:

- it is too manual and brittle
- or it is too AI-heavy and hard to verify

`thesis-skills` takes a different route:

- code handles deterministic checks, mappings, and bounded fixes
- rulesets isolate school or journal policy from implementation
- AI/skills stay in the assistive layer instead of silently owning the result

The goal is not to replace academic judgment. The goal is to reduce avoidable formatting, reference, and migration work.

## Highlights

- deterministic `check -> report -> fix` loop
- explicit `Word -> LaTeX` migration contracts
- reusable rule packs for universities and journals
- safe fixers that read reports instead of rewriting whole chapters
- regression-tested bibliography and migration paths
- bilingual public documentation designed for GitHub readers

## Support Matrix

| Workflow | Status in v0.3.0 | What it means |
|---|---|---|
| Zotero BibTeX quality check | Stable | validate exported bibliography before import |
| Zotero Word citation sync | Stable | extract Word citations, compare mappings, update `citation-lock.tex` |
| EndNote export intake | Supported | export BibTeX, normalize, then enter the same validation pipeline |
| EndNote direct sync | Not yet | intentionally not claimed in this release |
| Word -> LaTeX migration | Stable | explicit migration spec with structured metadata |
| Deterministic checkers | Stable | references, language, format, content |
| Report-driven fixers | Stable | bounded, mechanical, minimal edits |
| Rule pack generation | Stable | starter-based and draft-pack generation both supported |

## What v0.3.0 Changes

- clarifies the repository around workflow layers instead of loose scripts
- keeps the stronger local engineering structure (`core/`, `tests/`, fixers, CI)
- positions Zotero as the strongest bibliography path today
- keeps EndNote in the release, but honestly as an export-based intake path
- refreshes packaging and release metadata for public GitHub use

## Very Simple Start

### Option A: You already have a LaTeX project

```bash
python run_check_once.py --project-root <your-latex-project> --ruleset university-generic --skip-compile
python run_fix_cycle.py --project-root <your-latex-project> --ruleset university-generic --apply false
```

### Option B: You have a Word draft and want migration first

```bash
python 01-word-to-latex/migrate_project.py --source-root <intake> --target-root <latex-project> --spec <migration.json> --apply false
```

### Option C: You need Zotero citation sync from Word

```bash
python 00-bib-zotero/sync_from_word.py --project-root <latex-project> --word-file <word.docx>
```

### Option D: You want local skill installation

```bash
python install_openclaw.py
```

## Workflow Layers

### 1. Bibliography Intake

- `00-bib-zotero/`
- `00-bib-endnote/`
- `core/zotero_extract.py`
- `core/citation_mapping.py`

This layer handles bibliography entry quality and citation intake before the rest of the workflow runs.

### 2. Word-to-LaTeX Migration

- `01-word-to-latex/`
- `core/migration.py`
- `adapters/intake/`

Migration is explicit. The repository prefers structured mappings over magical filename guessing.

### 3. Deterministic Checking

- `run_check_once.py`
- `10-check-references/`
- `11-check-language/`
- `12-check-format/`
- `13-check-content/`

Checkers emit JSON reports instead of making hidden edits.

### 4. Report-Driven Fixing

- `run_fix_cycle.py`
- `20-fix-references/`
- `21-fix-language-style/`
- `22-fix-format-structure/`

Fixers consume reports and apply minimal, bounded changes.

### 5. Rulesets and Onboarding

- `90-rules/`
- `90-rules/packs/`
- `core/rules.py`
- `core/pack_generator.py`

Policy lives in packs, not scattered across scripts.

## Technical Roadmap

High-level roadmap: [docs/roadmap.md](docs/roadmap.md)

Detailed architecture: [docs/architecture.md](docs/architecture.md)

Current direction:

- keep the top-level layout easy to read
- keep `core/` as the reusable implementation layer
- keep Zotero strong today
- expand EndNote only when the data contract is explicit enough to be trustworthy

## Repository Layout

```text
thesis-skills/
├── 00-bib-zotero/              # Zotero bibliography intake and sync
├── 00-bib-endnote/             # EndNote export workflow guidance
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
├── adapters/intake/            # Intake metadata and migration specs
├── core/                       # Reusable deterministic core logic
├── docs/                       # Architecture and roadmap docs
├── examples/                   # Minimal runnable examples
├── tests/                      # Regression tests
├── install_openclaw.py         # One-command skill installer
├── run_check_once.py           # One-command check runner
└── run_fix_cycle.py            # One-command fix runner
```

## Main Use Cases

### You already have a thesis project

- choose a ruleset such as `university-generic` or `tsinghua-thesis`
- run `run_check_once.py`
- inspect JSON reports
- preview or apply bounded fixes with `run_fix_cycle.py`

### You need to migrate from Word

- prepare intake metadata and migration spec
- migrate assets with `01-word-to-latex/migrate_project.py`
- run the deterministic checks
- then apply minimal fixes if needed

### You need bibliography intake discipline

- Zotero: validate or sync citations from Word
- EndNote: export BibTeX, normalize, then validate through the same quality gate

### You need a new school or journal pack

- collect guide, template, and compliant sample
- use `90-rules/create_pack.py` or `90-rules/create_draft_pack.py`
- refine pack rules against sample projects

## Adapting Other Universities and Journals

Useful input materials:

- official guide (`PDF`, `HTML`, or plain text)
- official template (`DOCX`, `DOTX`, `CLS`, `STY`, `TEX`)
- at least one compliant sample (`PDF` or source)
- optional style files (`BST`, `BBX`, `CBX`, `CSL`)
- optional screenshots for title pages, figures, tables, and references

Recommended starting points:

- `90-rules/packs/university-generic/`
- `90-rules/packs/journal-generic/`

## Template Links

These are useful jump-off repositories before migration or ruleset onboarding. Always verify against the latest official guide.

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

## Current Status

The repository currently provides:

- a working `check -> report -> fix` loop
- a working `Word -> LaTeX` migration path
- Zotero bibliography quality checks and citation sync support
- EndNote export-based intake guidance
- reusable starter packs for theses and journals
- regression tests covering the main public workflow

In one sentence:

`thesis-skills` is a public-facing workflow repository that makes academic writing infrastructure more testable, more reusable, and easier to explain.

## License

See [LICENSE](LICENSE). Third-party notices are in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
