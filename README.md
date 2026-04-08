# Thesis Skills v0.5.2

<div align="center">

![Thesis Skills](https://img.shields.io/badge/Thesis-Skills-4285f4?style=for-the-badge&logo=book&logoColor=white)

**Deterministic thesis and journal writing workflow**  
*Python checkers • Safe fixers • YAML rule packs • One-click runners*

[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/github/license/quzhiii/thesis-skills)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)](https://github.com/quzhiii/thesis-skills)

[中文文档](README.zh-CN.md) • **English**

[Quick Start](#quick-start) • [Beginner Guide (ZH)](docs/getting-started-zh.md) • [Features](#core-features) • [Changelog](#version-history) • [Architecture](docs/architecture.md) • [Contributing](CONTRIBUTING.md)

</div>

---

## Why Thesis Skills?

**The pain points we solve:**

| Pain Point | Traditional Workflow | Thesis Skills |
|:---|:---|:---|
| Citation migration Word→LaTeX | Manual mapping, error-prone | Auto-extract & sync |
| Citation numbering stability | Shifts when deleting refs | Citation Lock mechanism |
| University format compliance | Read docs, manual check | YAML rule packs + auto-check |
| Language quality | Proofread manually | Deterministic lint + deep review |
| Bibliography import | Copy-paste from EndNote | XML/RIS/BibTeX auto-import |

---

## Version History

### v0.5.2 — Deep Patch Preview 🆕

> **Review-oriented findings → Selective patches**

| Before (v0.5.1) | After (v0.5.2) | Impact |
|:---|:---|:---|
| Deep findings = read-only reports | Span-based patch previews | **Actionable fixes** |
| No auto-fix for deep issues | Validated `old_text` matching | **Safe application** |
| Single fix mode | `--apply-mode safe\|suggest\|mixed` | **Flexible control** |

**Key additions:**
- `24-fix-language-deep`: Converts findings to span-based patches
- Patch validation: checks `old_text`, rejects overlaps
- Respects `review_required` flag (skips by default)

### v0.5.1 — Deep Language Review

> **Sentence-aware, cross-file language screening**

| Metric | v0.5.0 | v0.5.1 | Change |
|:---|:---|:---|:---|
| Check depth | Character-level | Sentence + cross-file | **+3 layers** |
| Output fields | Basic | 10+ fields (span, evidence, confidence) | **Rich metadata** |
| Review workflow | Flat list | Prioritized queue + clusters | **Efficient triage** |

**New checker:** `14-check-language-deep`
- Connector misuse detection
- Collocation analysis
- Terminology consistency
- Acronym first-use validation
- LaTeX-aware masking (cite/ref, math, figures)

### v0.5.0 — Basic Language Foundation

> **Deterministic language lint layer**

```
v0.5.0 Coverage:
├── CJK/Latin spacing
├── Punctuation normalization
├── Bracket/quote balance
├── Book-title mark consistency
├── Unit spacing
├── Ellipsis & dash style
├── Zh/En punctuation boundaries
├── Number ranges
├── Enum punctuation
└── Connector blacklist
```

### v0.4 — EndNote Import-First Support

| Feature | v0.3 | v0.4 | Gain |
|:---|:---|:---|:---|
| Bibliography sources | Zotero only | Zotero + EndNote | **+100%** |
| Import formats | Manual BibTeX | XML/RIS/BibTeX | **Auto-detect** |
| Duplicate handling | None | DOI exact + fuzzy warn | **Clean imports** |
| Canonicalization | Zotero-specific | Source-agnostic | **Universal model** |

### v0.3 — Efficiency Revolution

> **4-5x workflow speedup**

| Workflow | v0.2 Time | v0.3 Time | Speedup |
|:---|:---|:---|:---|
| Daily citation updates (10 refs) | ~85 min | ~2 min | **42×** |
| Word→LaTeX migration (first time) | ~210 min | ~40 min | **5.25×** |
| New university format adaptation | ~100 min | ~56 min | **1.8×** |
| Citation sync | Manual mapping | Auto-extract | **80% faster** |
| Project discovery | Manual config | Auto-detect | **90% faster** |

---

## Core Features

### Five-Layer Architecture

```
┌─────────────────────────────────────────┐
│  Layer 5: Rule-Pack Onboarding          │  ← YAML configs, starter packs
├─────────────────────────────────────────┤
│  Layer 4: Report-Driven Fixing          │  ← 20-fix-*, 24-fix-language-deep
├─────────────────────────────────────────┤
│  Layer 3: Deterministic Checking        │  ← 10-check-*, 14-check-language-deep
├─────────────────────────────────────────┤
│  Layer 2: Word-to-LaTeX Migration       │  ← 01-word-to-latex
├─────────────────────────────────────────┤
│  Layer 1: Bibliography Intake           │  ← 00-bib-endnote, 00-bib-zotero
└─────────────────────────────────────────┘
```

### Feature Modules

| Module | Status | Description |
|:---|:---|:---|
| **EndNote Import** | ✅ v0.4 | XML/RIS/BibTeX → `refNNN` with deduplication |
| **Zotero Sync** | ✅ v0.3 | Word docx → LaTeX citation mapping |
| **Reference Check** | ✅ Stable | Missing keys, orphans, duplicates |
| **Language Lint** | ✅ v0.5.0 | 10+ deterministic rules |
| **Deep Language Review** | ✅ v0.5.1 | Sentence-aware screening |
| **Deep Patch Fix** | ✅ v0.5.2 | Selective span-based fixes |
| **Format Check** | ✅ Stable | Figures, tables, centering |
| **Content Check** | ✅ Stable | Required sections, abstract keywords |

---

## Quick Start

```bash
# Clone
git clone https://github.com/quzhiii/thesis-skills.git
cd thesis-skills

# Quick check example
python run_check_once.py \
  --project-root examples/minimal-latex-project \
  --ruleset university-generic \
  --skip-compile
```

### New to LaTeX?

If you are completely new to LaTeX, start here first:

- [Beginner getting-started guide (Chinese)](docs/getting-started-zh.md)

### EndNote Workflow

```bash
# 1. Export from EndNote → XML/RIS/BibTeX
# 2. Preflight check
python 00-bib-endnote/check_endnote_export.py \
  --project-root thesis --input refs.xml

# 3. Import
python 00-bib-endnote/import_library.py \
  --project-root thesis --input refs.xml --apply
```

### Zotero Workflow

```bash
# Sync from Word to LaTeX
python 00-bib-zotero/sync_from_word.py \
  --project-root thesis --word-file thesis.docx --apply

# Run checks
python run_check_once.py \
  --project-root thesis --ruleset tsinghua-thesis --skip-compile

# Fix issues (dry-run first)
python run_fix_cycle.py \
  --project-root thesis --ruleset tsinghua-thesis --apply false
```

---

## Rule Pack System

Starter packs included:

```
90-rules/packs/
├── university-generic/     # Generic university thesis
├── journal-generic/        # Generic journal article
└── tsinghua-thesis/        # Tsinghua University example
```

Create your own:

```bash
python 90-rules/create_pack.py \
  --pack-id my-university \
  --display-name "My University Thesis" \
  --starter university-generic \
  --kind university-thesis
```

---

## Technical Architecture

```
thesis-skills/
├── core/                   # Shared implementations
│   ├── canonicalize.py     # Reference normalization
│   ├── citation_*.py       # Mapping & models
│   └── reports.py          # JSON report generation
├── 00-bib-*/               # Bibliography workflows
├── 01-word-to-latex/       # Migration workflow
├── 10-check-*/             # Deterministic checkers
├── 20-fix-*/               # Safe fixers
├── 90-rules/               # Rule pack system
└── 99-runner/              # Entry points
```

---

## Template Recommendations

| University | Repository |
|:---|:---|
| Tsinghua | [tuna/thuthesis](https://github.com/tuna/thuthesis) |
| SJTU | [sjtug/SJTUThesis](https://github.com/sjtug/SJTUThesis) |
| USTC | [ustctug/ustcthesis](https://github.com/ustctug/ustcthesis) |
| Peking | [CasperVector/pkuthss](https://github.com/CasperVector/pkuthss) |
| Stanford | [dcroote/stanford-thesis-example](https://github.com/dcroote/stanford-thesis-example) |
| Cambridge | [cambridge/thesis](https://github.com/cambridge/thesis) |

---

## Acknowledgments

**Special thanks to [tuna/thuthesis](https://github.com/tuna/thuthesis)** for their open-source LaTeX thesis template, which has greatly benefited Tsinghua University students and inspired this project.

---

## License

MIT License
