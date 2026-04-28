# Thesis Skills v0.7.0

<div align="center">

![Thesis Skills](https://img.shields.io/badge/Thesis-Skills-4285f4?style=for-the-badge&logo=book&logoColor=white)

**Deterministic thesis and journal writing workflow**  
*Python checkers • Safe fixers • YAML rule packs • One-click runners*

[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/github/license/quzhiii/thesis-skills)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)](https://github.com/quzhiii/thesis-skills)
[![Landing Page](https://img.shields.io/badge/🚀%20Landing%20Page-Live-success)](https://quzhiii.github.io/thesis-skills)

[中文文档](README.zh-CN.md) • **English** • [🚀 展示页面](https://quzhiii.github.io/thesis-skills)

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

### v0.7.0 — Readiness Gate 🆕

> **Bounded pre-submission verdicts from existing workflow artifacts**

| New in v0.7.0 | What it adds | Why it matters |
|:---|:---|:---|
| `16-check-readiness` | Pre-submission readiness gate | Summarizes existing check/fix/compile/export/review artifacts into one explicit go/no-go verdict |
| Gate modes | `advisor-handoff` + `submission-prep` | Makes readiness stricter only where the target workflow actually requires it |
| Runner bridge | `derived_artifacts.readiness_gate` in `run-summary.json` | Exposes readiness without turning the runner into a second orchestration engine |

**Key additions:**
- machine-readable readiness artifacts with `PASS / WARN / BLOCK`
- explicit blockers, warnings, next actions, and source references
- bounded integration with `run_check_once.py` as a derived artifact

### v0.6.0 — Delivery Foundation

> **Review-friendly export + compile diagnostics + bounded review loop**

| New in v0.6.0 | What it adds | Why it matters |
|:---|:---|:---|
| `02-latex-to-word` | Review-friendly `.docx` export | Makes advisor and collaborator review easier |
| `15-check-compile` | Structured compile-log parsing | Turns raw TeX failures into clearer findings |
| `03-latex-review-diff` + `04-word-review-ingest` | Review-loop artifacts | Makes revision rounds inspectable and repeatable |

**Key additions:**
- Review-first LaTeX→Word export with explicit limitation reporting
- Compile-log parser integrated into `run_check_once.py`
- Review package, feedback-ingest, TODO split, and revision summary support

### v0.5.2 — Deep Patch Preview

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

## After v0.7.0

The repository has moved past the stage of adding missing workflow families one by one.
The current hardening track is now:

- **v0.7.1 — Review Summary Hardening**
  - chapter-level review summaries are now part of the review artifact direction
  - the next narrow improvements focus on richer review digests, TODO-oriented artifacts, and clearer revision summaries
- **v0.7.2 — Feedback Ingest + Readiness Calibration**
  - the readiness gate now reads richer bounded review-debt evidence from ingest artifacts
  - the next narrow improvements focus on clearer `PASS / WARN / BLOCK` explanation quality and tighter ingest-to-gate linkage

See [`docs/roadmap.md`](docs/roadmap.md) for the current post-`v0.7.0` release train and acceptance gates.

---

## Core Features

### Five-Layer Architecture

```
┌─────────────────────────────────────────┐
│  Layer 6: Rule-Pack Onboarding          │  ← YAML configs, starter packs
├─────────────────────────────────────────┤
│  Layer 5: Report-Driven Fixing          │  ← 20-fix-*, 24-fix-language-deep
├─────────────────────────────────────────┤
│  Layer 4: Deterministic Checking        │  ← 10-check-*, 14-check-language-deep
├─────────────────────────────────────────┤
│  Layer 3: LaTeX-to-Word Export          │  ← 02-latex-to-word
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
| **LaTeX→Word Export** | ✅ v0.6 | Review-friendly `.docx` export with explicit limitations |
| **Reference Check** | ✅ Stable | Missing keys, orphans, duplicates |
| **Language Lint** | ✅ v0.5.0 | 10+ deterministic rules |
| **Deep Language Review** | ✅ v0.5.1 | Sentence-aware screening |
| **Deep Patch Fix** | ✅ v0.5.2 | Selective span-based fixes |
| **Format Check** | ✅ Stable | Figures, tables, centering |
| **Content Check** | ✅ Stable | Required sections, abstract keywords |
| **Compile Log Parser** | ✅ v0.6 | Friendlier compile diagnostics from existing `.log` files |
| **Review Loop** | ✅ v0.6 | Review diff, feedback ingest, TODO split, and revision summaries |
| **Pre-Submission Gate** | ✅ v0.7 | Bounded readiness verdict from existing workflow artifacts |

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

### Compile Diagnostics

```bash
# Parse compile findings when a .log file is present
python run_check_once.py \
  --project-root thesis \
  --ruleset tsinghua-thesis

# Skip compile parsing when you only want structure/content/language checks
python run_check_once.py \
  --project-root thesis \
  --ruleset tsinghua-thesis \
  --skip-compile
```

Positioning:

- compile parsing translates raw LaTeX log output into structured findings
- it does not replace your TeX toolchain or guarantee full build orchestration
- if no log is available, the runner reports that explicitly instead of crashing

### LaTeX to Word Workflow

```bash
# Generate a review-first export summary
python 02-latex-to-word/migrate_project.py \
  --project-root thesis \
  --output-file thesis-review.docx \
  --profile review-friendly \
  --apply false
```

First-release positioning:

- review-friendly export is the primary target
- submission-friendly export is planned as a stricter later path
- unsupported constructs should be surfaced explicitly rather than hidden

### Review Loop Workflow

```bash
# Build a review package and triage artifact from current reports
python 03-latex-review-diff/review_diff.py \
  --project-root thesis

# Normalize bounded review feedback into structured issues
python 04-word-review-ingest/feedback_ingest.py \
  --project-root thesis \
  --input review-feedback.json
```

Positioning:

- review loop is a bounded workflow for revision rounds, not a collaboration platform
- diff/triage and feedback ingest stay inspectable through explicit JSON artifacts
- chapter-level review summaries now make review-package output easier to scan before widening further
- ambiguous or high-judgement changes remain review-gated rather than auto-applied

### Pre-Submission Gate

```bash
# Emit a bounded readiness artifact
python 16-check-readiness/check_readiness.py \
  --project-root thesis \
  --ruleset tsinghua-thesis \
  --mode advisor-handoff
```

Positioning:

- the gate is a summarizing layer built on existing reports and workflow artifacts
- it returns `PASS`, `WARN`, or `BLOCK` with explicit blockers, warnings, and next actions
- it now consumes richer bounded review-debt evidence instead of relying only on a review-diff summary path
- it does not re-run the whole toolchain, auto-fix issues, or claim universal submission compliance
- `run_check_once.py` can also surface the readiness gate as a derived artifact reference in `run-summary.json`

---

## Rule Pack System

Starter packs included:

```
90-rules/packs/
 ├── university-generic/     # Generic university thesis
 ├── journal-generic/        # Generic journal article
 ├── tsinghua-thesis/        # Tsinghua University example
 └── demo-university-thesis/ # Concrete non-Tsinghua example pack
```

Create your own:

```bash
python 90-rules/create_pack.py \
  --pack-id my-university \
  --display-name "My University Thesis" \
  --starter university-generic \
  --kind university-thesis
```

Current starter-pack baseline and extension assumptions:

- `90-rules/STARTER_PACK_BASELINE.md`
- `90-rules/MIXED_PACK_WORKFLOWS.md`

First baseline lint command:

```bash
python 90-rules/lint_pack.py --pack-path 90-rules/packs/university-generic
```

The current completeness layer in that command also checks:

- required top-level sections in `rules.yaml`: `project`, `reference`, `language`
- required top-level section in `mappings.yaml`: `mappings`

The current schema-consistency layer also enforces:

- required top-level rule sections must be mappings
- `mappings.yaml` must match one of the two currently accepted shapes:
  - starter-pack shape: `mappings`
  - draft-pack shape: `source_template_mappings` + `chapter_role_mappings`

The current scorecard output summarizes:

- required files
- metadata completeness
- baseline completeness
- schema consistency
- overall status
- finding counts (`errors`, `warnings`, `infos`)

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
├── 02-latex-to-word/       # Review-first export workflow
├── 03-latex-review-diff/   # Review package and triage workflow
├── 04-word-review-ingest/  # Bounded feedback normalization workflow
├── 10-check-*/             # Deterministic checkers
├── 15-check-compile/       # Compile-log diagnostic translation
├── 16-check-readiness/     # Bounded pre-submission readiness gate
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
