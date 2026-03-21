# Thesis Skills v1.2.0

> Deterministic thesis and journal writing skills with Python checkers, safe fixers, YAML rule packs, and one-click runners.

## Why Thesis Skills?

### Pain Point 1: Chaotic citation management when converting Word → LaTeX

**Problem**: When writing in Word with Zotero and converting to LaTeX:
- Zotero citation-keys (like `WuZeXinZhongYiYouShiBingZhongNaRuDRGDIPFuFeiGuiFanFenXia`) don't work in LaTeX
- Manual mapping to `ref001, ref002, ...` is error-prone and time-consuming
- Every citation change in Word requires re-syncing to LaTeX

**Solution**: Thesis Skills v1.2.0 Zotero sync
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

### Zotero Sync (NEW in v1.2.0)

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
- `11-check-language`: Language checks (CJK-Latin spacing, repeated punctuation, mixed quotes, weak phrases)
- `12-check-format`: Format checks (figure/table lists, figure centering)
- `13-check-content`: Content checks (required sections, abstract keyword count)

### Fixers (20-fix-*)

```bash
# One-click fix cycle
python run_fix_cycle.py --project-root thesis --ruleset tsinghua-thesis --apply false
```

**Features**:
- Read check reports, make minimal fixes
- Support dry-run preview
- Generate fix reports

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
  weak_phrases:
    enabled: true
    severity: info
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
│   ├── citation_mapping.py # Citation mapping management
│   ├── project.py          # Project discovery
│   └── reports.py          # Report generation
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
Word (Zotero) → [sync_from_word.py] → LaTeX Project
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
