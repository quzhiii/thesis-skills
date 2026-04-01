# Thesis Skills v0.5.2

<div align="center">
  **Deterministic thesis and journal writing skills with Python checkers, safe fixers, YAML rule packs, and one-click runners**

  [![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
  [![License](https://img.shields.io/github/license/quzhiii/thesis-skills)](LICENSE)
  [![Platform](https://img.shields.io/badge/platform-windows%20%7C%20linux%20%7C%20macos-lightgrey)](https://github.com/quzhiii/thesis-skills)

  [**中文文档**](README.zh-CN.md) | [English](README.md)

  [Quick Start](#quick-start) • [Getting Started Tutorial](#getting-started-tutorial) • [Features](#core-features) • [Documentation](docs/architecture.md) • [Contributing](CONTRIBUTING.md)
</div>

---

## Acknowledgments

**Special thanks to [tuna/thuthesis](https://github.com/tuna/thuthesis)** for their open-source LaTeX thesis template, which has greatly benefited Tsinghua University students and inspired this project.

---

## v0.5.2: Deep Patch Preview And Selective Apply

`v0.5.2` adds the deep fixer layer without collapsing review-oriented findings into auto-rewrite behavior.

The deep language path is positioned as a high-confidence screening assistant for thesis drafting, not as a final sign-off for thesis-ready prose.

- `24-fix-language-deep` converts deep language findings into validated span-based patches.
- patch previews include `file`, `start`, `end`, `old_text`, `new_text`, `issue_code`, and `confidence`.
- deep fixes validate `old_text`, reject overlapping patches, and skip `review_required=true` on apply unless explicitly overridden.
- `run_fix_cycle.py` now supports `--apply-mode safe|suggest|mixed`, so the old safe path remains intact while deep preview can run independently.

---

## v0.5.1: Deep Language Review Layer

`v0.5.1` adds a separate report-only deep language checker instead of overloading the basic language lint path.

- `14-check-language-deep` introduces sentence-aware and cross-file review for connector misuse, collocation misuse, terminology consistency, and acronym first-use.
- deep findings now carry richer fields such as `span`, `evidence`, `suggestions`, `confidence`, `review_required`, and `category`.
- deep reports now also expose `coverage`, `uncovered_risks`, `stratified_counts`, and review-oriented fields such as `original_text`, `rationale`, and `risk_level`.
- LaTeX-facing constructs such as cite/ref commands, math regions, and figure/table environments are masked during deep screening to reduce engineering-side false positives.
- `run_check_once.py` now supports `language-deep` in the default pipeline and also a focused path: `--only language-deep`.
- deep review is still report-only in `v0.5.1`; deep patch preview remains the next phase.

---

## v0.5.0: Basic Language Foundation

`v0.5.0` expands the deterministic language layer without shrinking the broader repository scope.

- `11-check-language` now covers baseline thesis-language lint for bracket/quote balance, book-title mark consistency, unit spacing, ellipsis style, dash style, zh/en punctuation boundaries, number ranges, enum punctuation, connector blacklist, and conservative punctuation-width mixing checks.
- `21-fix-language-style` stays low-risk and only auto-applies safe fixes: CJK/Latin spacing, repeated punctuation, unit spacing, ellipsis normalization, and conservative fullwidth/halfwidth punctuation normalization.
- language rules in each pack are now explicit objects under `language.<rule>` with `enabled`, `severity`, `autofix_safe`, and optional `patterns`.
- deep patch preview is planned next; it is not shipped in `v0.5.1`.

---

## What Thesis Skills Is

`thesis-skills` is a deterministic workflow layer for academic writing projects.

It is designed for:

- bibliography intake from Zotero and EndNote
- structured Word-to-LaTeX migration
- repeatable checks with JSON reports
- bounded, report-driven fixes instead of free-form rewriting
- reusable rule packs for schools and journals

It is not a general writing assistant, not a thesis template, and not a final
sign-off system for thesis-ready prose.

## Five-Layer Architecture

The current repository follows five layers:

1. bibliography intake
2. Word-to-LaTeX migration
3. deterministic checking
4. report-driven fixing
5. rule-pack onboarding and reuse

This maps directly to the repository layout:

- `00-bib-*`: intake workflows
- `01-word-to-latex`: migration workflow
- `10-check-*` and `14-check-language-deep`: checker layer
- `20-fix-*` and `24-fix-language-deep`: fixer layer
- `90-rules`: policy layer
- `core/`: shared implementation layer

## Current Boundaries

The most important `v0.5.x` boundary is the split between baseline language
lint, deep language review, safe fixes, and deep patch preview.

- `11-check-language` is the baseline deterministic language lint layer.
- `14-check-language-deep` is a structured screening layer for higher-order language issues.
- `21-fix-language-style` stays conservative and low-risk.
- `24-fix-language-deep` previews or selectively applies validated span-based patches.

That means `deep language` should be treated as a screening assistant plus human
review aid, not as the sole basis for final thesis language polish.

Operationally that now means:

- findings are grouped through summary strata instead of being presented as one undifferentiated signal
- `0 findings` only means no configured deep issues were detected in checked prose after LaTeX-aware masking
- all deep suggestions are framed for manual review first, with conservative rewrite guidance rather than final-signoff claims

## Recommended Entry Paths

- EndNote user: preflight export -> dry-run import -> apply import -> run checks -> review fixes
- Zotero + Word user: sync citations -> run bibliography quality check -> run checks -> review fixes
- Existing LaTeX project: choose a rule pack -> run checks -> apply safe fixes conservatively
- Rule-pack author: start from a starter pack -> adapt rules -> validate on the example project

Detailed architecture notes: [docs/architecture.md](docs/architecture.md)

---

## v0.3 vs v0.4: What's New?

> **EndNote import-first support** 🆕

### Key Improvements in v0.4

| Feature | v0.3 | v0.4 | Impact |
|---------|------|------|--------|
| **EndNote Import** | ❌ Manual BibTeX export only | ✅ XML/RIS/BibTeX auto-import | **First-class EndNote support** |
| **Citation Canonicalization** | ❌ Zotero-specific | ✅ Source-agnostic model | **Multi-source ready** |
| **Duplicate Detection** | ❌ None | ✅ DOI exact + low-confidence warnings | **Clean imports** |
| **Stable refNNN** | ✅ Zotero only | ✅ EndNote + Zotero | **Consistent numbering** |
| **Preflight Check** | ❌ None | ✅ `check_endnote_export.py` | **Catch issues early** |

### EndNote Workflow (v0.4 New)

```bash
# Import EndNote XML/RIS/BibTeX
python 00-bib-endnote/import_library.py \
  --project-root thesis \
  --input references.xml \
  --apply

# Preflight check before import
python 00-bib-endnote/check_endnote_export.py \
  --project-root thesis \
  --input references.xml
```

**Features**:
- Auto-detect format (XML/RIS/BibTeX)
- DOI-based deduplication with warnings
- Stable `refNNN` allocation (persistent across re-runs)
- Incremental imports (reuses existing mappings)
- Detailed JSON reports

👉 **First time using Thesis Skills?** Jump here: [Getting Started Tutorial](#getting-started-tutorial)

---

## v0.2 vs v0.3: What's New?

> **Efficiency improvements based on typical scenarios** ⚡

### Key Improvements

| Feature | v0.2 | v0.3 | Efficiency Gain |
|---------|------|------|-----------------|
| **Zotero Sync** | ❌ Manual mapping | ✅ Auto-extract & map | **80% faster** |
| **Citation Numbering** | ❌ Unstable when deleting | ✅ Citation Lock mechanism | **100% stable** |
| **Project Discovery** | ⚠️ Manual config | ✅ Auto-detect | **90% faster** |
| **Rule Pack Creation** | ⚠️ Copy-paste | ✅ One-click generate | **70% faster** |
| **One-click Check** | ⚠️ Run individually | ✅ Single command | **85% faster** |
| **Auto-fix** | ❌ Not available | ✅ run_fix_cycle.py | **4x faster** |

### Real-world Time Savings

**Scenario 1: Daily citation updates (10 new citations)**
- v0.2: ~85 minutes (manual comparison & mapping)
- v0.3: ~2 minutes (auto-detect & batch sync)
- 🚀 **42x faster**

**Scenario 2: First-time Word → LaTeX migration**
- v0.2: ~210 minutes (3.5 hours)
- v0.3: ~40 minutes
- 🚀 **5.25x faster**

**Scenario 3: Adapting to new university format**
- v0.2: ~100 minutes
- v0.3: ~56 minutes
- 🚀 **1.8x faster**

### Overall Impact

**v0.3 delivers 4-5x workflow efficiency improvement** by automating manual tasks and eliminating citation renumbering risks.

📊 **See detailed comparison**: [Technical Roadmap](docs/plans/2026-03-09-thesis-skills-restructure.md#v02-vs-v03-详细对比与效率分析)

---

## Why Thesis Skills?

### Pain Point 1: Chaotic citation management when converting Word → LaTeX

**Problem**: When writing in Word with Zotero and converting to LaTeX:
- Zotero citation-keys (like `WuZeXinZhongYiYouShiBingZhongNaRuDRGDIPFuFeiGuiFanFenXia`) don't work in LaTeX
- Manual mapping to `ref001, ref002, ...` is error-prone and time-consuming
- Every citation change in Word requires re-syncing to LaTeX

**Solution**: Thesis Skills v0.3.0 Zotero sync
- Auto-extract Zotero citations from Word docx (parses embedded CSL_CITATION JSON)
- Auto-create Zotero key ↔ LaTeX ref mapping
- Incremental updates: only handle new/removed citations, no need to regenerate entire bibliography

```bash
# Sync citations from Word to LaTeX
python 00-bib-zotero/sync_from_word.py --project-root thesis --word-file thesis.docx --apply
```

### Pain Point 2: Unstable citation numbering

**Problem**: When deleting a citation in Word:
- If you delete the corresponding bib entry, all subsequent citation numbers shift
- Example: deleting ref005 makes ref006 become ref005, breaking all `\cite{ref006}` references

**Solution**: Citation Lock mechanism
- Generate `citation-lock.tex` using `\nocite{}` to lock all reference numbers
- Preserve bib entries when deleting citations (they just don't appear in text)
- Citation numbers remain stable

```latex
% citation-lock.tex auto-generated
\nocite{ref001,ref002,ref003,...}
```

### Pain Point 3: Different formatting requirements for schools/journals

**Problem**: Each school/journal has unique formatting rules:
- Bibliography format (author name format, year position, etc.)
- Chapter structure requirements
- Figure/table numbering and reference rules

**Solution**: YAML rule pack system
- Rules defined in YAML, easy to read and modify
- Starter Packs provided (university-generic, journal-generic)
- One-click generate new school rule packs

```bash
# Create new school rule pack from Starter Pack
python 90-rules/create_pack.py --pack-id my-university \
  --display-name "My University Thesis" \
  --starter university-generic \
  --kind university-thesis
```

### Pain Point 4: Unclear check and fix workflow

**Problem**: Traditional LaTeX projects:
- Compile error messages are hard to understand
- Unclear which parts don't meet formatting requirements
- Need to recompile after fixes to verify

**Solution**: Deterministic checks + safe fixes
- Checkers output JSON reports clearly listing all issues
- Fixers read reports and make minimal changes
- One-click execution with dry-run preview

```bash
# One-click check (skip compile)
python run_check_once.py --project-root thesis --ruleset tsinghua-thesis --skip-compile

# One-click fix cycle (dry-run preview)
python run_fix_cycle.py --project-root thesis --ruleset tsinghua-thesis --apply false
```

## Use Cases

### Use Case 1: Writing in Word, need to convert to LaTeX

```bash
# 1. Sync Zotero citations from Word to LaTeX
python 00-bib-zotero/sync_from_word.py \
  --project-root thesis \
  --word-file thesis.docx \
  --apply

# 2. Run checks
python run_check_once.py \
  --project-root thesis \
  --ruleset tsinghua-thesis \
  --skip-compile

# 3. View reports
cat thesis/reports/sync_from_word-report.json
cat thesis/reports/run-summary.json
```

### Use Case 2: Existing LaTeX project, adapt to new school format

```bash
# 1. Create new school rule pack
python 90-rules/create_pack.py \
  --pack-id peking-thesis \
  --display-name "Peking University Thesis" \
  --starter university-generic \
  --kind university-thesis

# 2. Edit 90-rules/packs/peking-thesis/rules.yaml
# 3. Run checks
python run_check_once.py \
  --project-root thesis \
  --ruleset peking-thesis \
  --skip-compile
```

### Use Case 3: Complete Word → LaTeX migration

```bash
# 1. Prepare migration spec
cat > migration.json << EOF
{
  "document_metadata": {
    "source_format": "word-exported-tex",
    "bibliography_source": "zotero"
  },
  "chapter_mappings": [
    {"from": "chapters/chapter1.tex", "to": "chapters/01-introduction.tex"}
  ],
  "bibliography_mappings": [
    {"from": "refs.bib", "to": "ref/refs.bib"}
  ]
}
EOF

# 2. Execute migration (dry-run)
python 01-word-to-latex/migrate_project.py \
  --source-root intake \
  --target-root thesis \
  --spec migration.json \
  --apply false

# 3. Apply after confirmation
python 01-word-to-latex/migrate_project.py \
  --source-root intake \
  --target-root thesis \
  --spec migration.json \
  --apply true
```

## Core Features

### EndNote Import (v0.4 New)

```bash
# Import EndNote library (XML/RIS/BibTeX)
python 00-bib-endnote/import_library.py --project-root thesis --input refs.xml --apply

# Preflight check before import
python 00-bib-endnote/check_endnote_export.py --project-root thesis --input refs.xml
```

**Features**:
- **Multi-format support**: XML (recommended) > RIS > BibTeX
- **Auto canonicalization**: DOI normalization, title cleaning, author name standardization
- **Smart deduplication**: DOI exact match (auto-merge) + low-confidence warnings (title similarity, year+author)
- **Stable `refNNN` allocation**: Persistent across re-runs, incremental imports preserve existing keys
- **Dry-run preview**: See what would happen before applying changes
- **JSON reports**: Detailed import summary with warnings and statistics

**Recommended workflow**:
1. Export from EndNote: File → Export → XML (or RIS)
2. Run preflight check: `python 00-bib-endnote/check_endnote_export.py`
3. Dry-run import: `python 00-bib-endnote/import_library.py --input refs.xml`
4. Apply import: `python 00-bib-endnote/import_library.py --input refs.xml --apply`

### Zotero Sync

```bash
# BibTeX quality check
python 00-bib-zotero/check_bib_quality.py --project-root thesis --ruleset tsinghua-thesis

# Word → LaTeX citation sync
python 00-bib-zotero/sync_from_word.py --project-root thesis --word-file thesis.docx
```

**Features**:
- Extract Zotero citations from Word docx (CSL_CITATION JSON)
- Maintain Zotero key ↔ LaTeX ref mapping (`ref/citation-mapping.json`)
- Generate citation lock file (`citation-lock.tex`)
- Detect new/removed citations
- Support dry-run preview

### Checkers (10-check-*)

```bash
# Run all checks with one command
python run_check_once.py --project-root thesis --ruleset tsinghua-thesis
```

**Check items**:
- `10-check-references`: Reference integrity (missing keys, orphan entries, duplicate titles)
- `11-check-language`: Deterministic language checks (CJK-Latin spacing, repeated punctuation, mixed quotes, weak phrases, bracket/quote mismatch, book-title marks, unit spacing, ellipsis, dash, zh/en punctuation boundaries, number ranges, enum punctuation, connector blacklist)
- `14-check-language-deep`: Report-only deep language review (connector misuse, collocation misuse, terminology consistency, acronym first-use)
- `12-check-format`: Format checks (figure/table lists, figure centering)
- `13-check-content`: Content checks (required sections, abstract keyword count)

`14-check-language-deep` is intended for structured first-pass screening plus human review, not as the sole basis for final thesis language polish.

### Fixers (20-fix-*)

```bash
# One-click fix cycle
python run_fix_cycle.py --project-root thesis --ruleset tsinghua-thesis --apply false
```

**Features**:
- Read check reports, make minimal fixes
- `21-fix-language-style` only auto-applies low-risk language fixes in `v0.5.0`
- `24-fix-language-deep` generates patch previews first and only applies selected deep patches when explicitly requested
- Support dry-run preview
- Generate fix reports

**Deep fix example**:

```bash
python run_fix_cycle.py \
  --project-root thesis \
  --ruleset tsinghua-thesis \
  --apply false \
  --apply-mode suggest
```

## Rule Pack System

### Starter Packs

```bash
90-rules/packs/
├── university-generic/    # Generic university thesis Starter Pack
├── journal-generic/       # Generic journal Starter Pack
└── tsinghua-thesis/       # Tsinghua University thesis Pack (example)
```

### Rule Pack Structure

```yaml
# pack.yaml
id: tsinghua-thesis
kind: university-thesis
display_name: Tsinghua Graduate Thesis Pack
version: 1
precedence: guide_over_template
starter: false

# rules.yaml (partial example)
project:
  main_tex_candidates: [thuthesis-example.tex, thesis.tex, main.tex]
  chapter_globs: [chapters/*.tex, data/chap*.tex]
  bibliography_files: [ref/refs.bib, ref/refs-import.bib]

reference:
  missing_key:
    severity: error
  orphan_entry:
    severity: warning

language:
  cjk_latin_spacing:
    enabled: true
    severity: warning
    autofix_safe: true
  unit_spacing:
    enabled: true
    severity: warning
    autofix_safe: true
  connector_blacklist_simple:
    enabled: true
    severity: info
    autofix_safe: false
    patterns: [因此所以, 但是同时]
  weak_phrases:
    enabled: true
    severity: info
    autofix_safe: false
    patterns: [众所周知, 不难看出, 本文将]
```

### Create New Rule Pack

```bash
# Method 1: Create from Starter Pack
python 90-rules/create_pack.py \
  --pack-id my-university \
  --display-name "My University Thesis" \
  --starter university-generic \
  --kind university-thesis

# Method 2: Generate Draft Pack from uploaded materials
python 90-rules/create_draft_pack.py \
  --intake adapters/intake/example-intake.json
```

## Creating Rule Packs for Other Schools/Journals

Recommended to upload at least:

- **Official writing guide**: `PDF`/`HTML`/plain text
- **Official template**: `DOCX`/`DOTX` or `CLS`/`STY`/`TEX`
- **Compliant sample**: 1 `PDF` or source
- **Optional style files**: `BST`/`BBX`/`CBX`/`CSL`

Then start by copying one of these Starter Packs:

- `90-rules/packs/university-generic/`
- `90-rules/packs/journal-generic/`

Detailed guide: `adapters/intake/README.md`

## Technical Architecture

Thesis Skills uses a modular design:

```
thesis-skills/
├── core/                    # Core modules
│   ├── zotero_extract.py   # Zotero citation extraction
│   ├── citation_models.py  # Canonical reference model (NEW v0.4)
│   ├── canonicalize.py     # Reference normalization (NEW v0.4)
│   ├── endnote_xml.py      # EndNote XML parser (NEW v0.4)
│   ├── endnote_ris.py      # RIS parser (NEW v0.4)
│   ├── bib_render.py       # BibTeX output (NEW v0.4)
│   ├── match_refs.py       # Deduplication (NEW v0.4)
│   ├── citation_mapping.py # Citation mapping management
│   ├── project.py          # Project discovery
│   └── reports.py          # Report generation
├── 00-bib-endnote/         # EndNote workflow (NEW v0.4)
│   ├── import_library.py   # Main import CLI
│   └── check_endnote_export.py  # Preflight checker
├── 00-bib-zotero/          # Zotero workflow
│   ├── check_bib_quality.py
│   └── sync_from_word.py
├── 01-word-to-latex/       # Word migration workflow
│   └── migrate_project.py
├── 10-check-*/             # Deterministic checkers
├── 20-fix-*/               # Safe fixers
├── 90-rules/               # Rule pack system
│   ├── create_pack.py
│   ├── create_draft_pack.py
│   └── packs/              # School/journal rule packs
├── adapters/intake/        # Onboarding guide
├── run_check_once.py       # One-click check
├── run_fix_cycle.py        # One-click fix
└── examples/               # Example projects
```

**Workflow**:

```
EndNote XML/RIS/BibTeX                    Word (Zotero)
       ↓                                        ↓
[import_library.py]                      [sync_from_word.py]
       ↓                                        ↓
       └──────────────► LaTeX Project ◄─────────┘
                              ↓
                        [run_check_once.py]
                              ↓
                          JSON Reports
                              ↓
                        [run_fix_cycle.py]
                              ↓
                          Fixed LaTeX
```

Detailed technical docs: `docs/architecture.md`

## Getting Started Tutorial

### Step 1: Installation

```bash
# Clone the repository
git clone https://github.com/quzhiii/thesis-skills.git
cd thesis-skills

# Install dependencies (optional, most features work with Python standard library)
pip install -r requirements.txt
```

### Step 2: Prepare Your LaTeX Project

Your project should have this structure:

```
my-thesis/
├── main.tex              # Main document
├── chapters/             # Chapter files
│   ├── chapter1.tex
│   └── chapter2.tex
└── ref/                  # Bibliography folder
    └── refs.bib          # Your references
```

### Step 3: Import References

#### For EndNote Users

```bash
# 1. Export from EndNote: File → Export → Select "XML" format
# 2. Run preflight check (optional but recommended)
python 00-bib-endnote/check_endnote_export.py \
  --project-root my-thesis \
  --input exported-references.xml

# 3. Dry-run import (preview without writing)
python 00-bib-endnote/import_library.py \
  --project-root my-thesis \
  --input exported-references.xml

# 4. Apply import
python 00-bib-endnote/import_library.py \
  --project-root my-thesis \
  --input exported-references.xml \
  --apply
```

**What happens:**
- Creates `ref/refs-import.bib` with your references
- Creates `ref/citation-mapping.json` for stable numbering
- Assigns `ref001`, `ref002`, etc. to each reference
- Detects and warns about duplicates

#### For Zotero Users

```bash
# 1. Export your Word document with Zotero citations
# 2. Sync citations from Word to LaTeX
python 00-bib-zotero/sync_from_word.py \
  --project-root my-thesis \
  --word-file my-thesis.docx \
  --apply
```

### Step 4: Run Checks

```bash
# Run all checks
python run_check_once.py \
  --project-root my-thesis \
  --ruleset university-generic \
  --skip-compile

# View reports
cat my-thesis/reports/run-summary.json
```

### Step 5: Fix Issues (Optional)

```bash
# Preview fixes (dry-run)
python run_fix_cycle.py \
  --project-root my-thesis \
  --ruleset university-generic \
  --apply false

# Apply fixes
python run_fix_cycle.py \
  --project-root my-thesis \
  --ruleset university-generic \
  --apply true
```

### Quick Reference

| Task | Command |
|------|---------|
| Import EndNote | `python 00-bib-endnote/import_library.py --project-root thesis --input refs.xml --apply` |
| Sync Zotero | `python 00-bib-zotero/sync_from_word.py --project-root thesis --word-file thesis.docx --apply` |
| Run checks | `python run_check_once.py --project-root thesis --ruleset university-generic --skip-compile` |
| Fix issues | `python run_fix_cycle.py --project-root thesis --ruleset university-generic --apply` |
| Create rule pack | `python 90-rules/create_pack.py --pack-id my-school --starter university-generic` |

---

## Template Links

These repositories are good starting points before running migration or rule-pack onboarding. Always verify current university/journal rules against official guides.

### China

- Tsinghua University - `tuna/thuthesis` - https://github.com/tuna/thuthesis
- Shanghai Jiao Tong University - `sjtug/SJTUThesis` - https://github.com/sjtug/SJTUThesis
- USTC - `ustctug/ustcthesis` - https://github.com/ustctug/ustcthesis
- UESTC - `tinoryj/UESTC-Thesis-Latex-Template` - https://github.com/tinoryj/UESTC-Thesis-Latex-Template
- UCAS - `mohuangrui/ucasthesis` - https://github.com/mohuangrui/ucasthesis
- Peking University - `CasperVector/pkuthss` or maintained forks such as `Thesharing/pkuthss`

### International

- Stanford University - `dcroote/stanford-thesis-example` - https://github.com/dcroote/stanford-thesis-example
- University of Cambridge - `cambridge/thesis` - https://github.com/cambridge/thesis
- University of Oxford - `mcmanigle/OxThesis` - https://github.com/mcmanigle/OxThesis
- EPFL - `HexHive/thesis_template` - https://github.com/HexHive/thesis_template
- ETH Zurich - `tuxu/ethz-thesis` - https://github.com/tuxu/ethz-thesis
- MIT (widely used unofficial) - `alinush/mit-thesis-template` - https://github.com/alinush/mit-thesis-template

## Quick Start

```bash
# Clone project
git clone https://github.com/quzhiii/thesis-skills.git
cd thesis-skills

# Run example
python run_check_once.py \
  --project-root examples/minimal-latex-project \
  --ruleset university-generic \
  --skip-compile
```

## License

MIT License
