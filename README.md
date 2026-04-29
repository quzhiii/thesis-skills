# Thesis Skills v1.0.0

<div align="center">

![Thesis Skills](https://img.shields.io/badge/Thesis-Skills-4285f4?style=for-the-badge&logo=book&logoColor=white)

# Spend Your Time Thinking, Not Formatting

*Automate the repetitive formatting work in academic writing — citation syncing, format checking, review handoffs, and defense prep*

[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/github/license/quzhiii/thesis-skills)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)](https://github.com/quzhiii/thesis-skills)
[![Landing Page](https://img.shields.io/badge/🚀%20Landing%20Page-Live-success)](https://quzhiii.github.io/thesis-skills)

[中文文档](README.zh-CN.md) • **English** • [🚀 Showcase](https://quzhiii.github.io/thesis-skills)

[6 Pain Points](#have-you-experienced-these) • [Capability Matrix](#core-capabilities) • [Use by Scenario](#use-by-scenario) • [Rule Packs](#rule-pack-system) • [Current Boundaries](#current-boundaries)

</div>

---

## Have You Experienced These?

> **「Added one reference, broke a dozen citation numbers.」**
>
> **「Advisor asked for a Word version. Panic.」**
>
> **「Used AI to rewrite a paragraph. Zotero citations collapsed.」**
>
> **「30+ format rules. Missed something even after 3 rounds.」**
>
> **「Pre-submission anxiety: afraid to click submit.」**
>
> **「Spent 3 hours manually inventorying figures before defense.」**

| 💔 Traditional Workflow | 😰 Typical Time Cost |
|:---|:---|
| Writing in Word → manually adjusting tables, cross-references, headers | Hours per issue |
| Switching to LaTeX → manually migrating chapters, rebuilding citations | 1-3 days |
| Using AI on Word docs → Zotero field codes corrupted, citations become plain text | Hours to fix |
| Manually checking university format guidelines | 1-3 hours per round |
| Flipping through 5-10 scattered reports before submission | 30-60 minutes |
| Manually outlining chapters, inventorying figures, preparing talk notes | 2-4 hours |

---

## Core Capabilities

### Before → After: Time Saved at Every Step

| Stage | Traditional | Thesis Skills | Time Saved |
|:---|:---|:---|:---|
| **📚 Bibliography Intake** | Manual copy-paste from Zotero/EndNote, rebuild citation numbers | Auto-import, stable `refNNN` IDs, incremental sync | **30-60 min → 2-5 min** |
| **🔄 Word ↔ LaTeX** | Manual content migration, structure rebuild, citation remapping | Auto-sync citations + structured checks; one-click review-friendly Word export | **1-3 hrs → 5-10 min** |
| **✅ Format Checking** | Manually verify 28+ rules, easy to miss | YAML rule-pack driven, 28+ auto-checks, report in 2 min | **1-3 hrs → 2-5 min** |
| **🔧 Safe Fixes** | Manual locate, edit, verify | Previewable patches from reports, apply after dry-run | **1-2 hrs → 5-10 min** |
| **🚦 Pre-Submission Gate** | Flip through multiple reports, still unsure | `PASS / WARN / BLOCK` one-page summary, blockers + next actions | **30-60 min → 1-2 min** |
| **🎯 Defense Prep** | Manual outline, figure inventory, talk notes | Auto-generate outline, highlights, figure inventory, candidate visuals | **2-4 hrs → 10-15 min** |

> ⚠️ **Objective note**: Times are conservative estimates for repetitive formatting work. The tool does not replace writing/thinking time.

### Real Output Examples

**Readiness Gate —— Final check before submission:**

```bash
$ python 16-check-readiness/check_readiness.py \
    --project-root thesis \
    --ruleset tsinghua-thesis \
    --mode advisor-handoff
```

```json
{
  "verdict": "WARN",
  "mode": "advisor-handoff",
  "blockers": [],
  "warnings": [
    "3 unreferenced citations (see 10-check-references report)",
    "2 figures lack alt-text (see 13-check-content report)"
  ],
  "next_actions": [
    "Run: python 20-fix-references/fix_references.py --apply false",
    "Review: reports/13-check-content-report.json lines 45-52"
  ]
}
```

**Format Check Report —— Specific file, line number, fix suggestion:**

```json
{
  "rule": "cjk_latin_spacing",
  "severity": "warning",
  "file": "chapters/introduction.tex",
  "line": 42,
  "message": "Missing space between CJK and Latin: '人工智能AI' → '人工智能 AI'",
  "autofix_safe": true,
  "suggested_fix": "人工智能 AI"
}
```

---

## Use by Scenario

### 🚀 Scenario 1: Just switched from Word to LaTeX

```bash
# 1. Sync Zotero citations from Word to LaTeX (stable refNNN numbering)
python 00-bib-zotero/sync_from_word.py \
  --project-root thesis --word-file thesis.docx --apply

# 2. Run comprehensive checks (references, language, format, content)
python run_check_once.py \
  --project-root thesis --ruleset tsinghua-thesis --skip-compile

# 3. Preview and apply safe fixes
python run_fix_cycle.py \
  --project-root thesis --ruleset tsinghua-thesis --apply false
```

### 🚀 Scenario 2: Already using LaTeX, want to check my thesis

```bash
# Run full check (including compile diagnostics)
python run_check_once.py \
  --project-root thesis --ruleset tsinghua-thesis

# Check readiness gate
python 16-check-readiness/check_readiness.py \
  --project-root thesis --ruleset tsinghua-thesis --mode advisor-handoff
```

### 🚀 Scenario 3: Advisor/collaborator needs Word version for review

```bash
# Generate review-friendly Word (explicitly reports degraded elements)
python 02-latex-to-word/migrate_project.py \
  --project-root thesis --output-file thesis-review.docx \
  --profile review-friendly --apply true

# Check reports/latex_to_word-report.json for degradation details
```

### 🚀 Scenario 4: Got Word feedback from advisor, need to update LaTeX

```bash
# 1. Normalize Word feedback into structured issues
python 04-word-review-ingest/feedback_ingest.py \
  --project-root thesis --input review-feedback.json

# 2. Generate review diff and TODOs
python 03-latex-review-diff/review_diff.py --project-root thesis
```

### 🚀 Scenario 5: Preparing for defense

```bash
# Auto-generate defense preparation materials
python 17-defense-pack/generate_outline.py \
  --project-root thesis --ruleset tsinghua-thesis

python 17-defense-pack/generate_figure_inventory.py \
  --project-root thesis --ruleset tsinghua-thesis
```

---

## Feature Overview

| Workflow | Entrypoint | Output / Role |
|:---|:---|:---|
| Zotero citation sync | `00-bib-zotero/sync_from_word.py` | Extract Zotero citations from Word, generate stable `refNNN` mapping |
| Zotero bibliography quality check | `00-bib-zotero/check_bib_quality.py` | Check BibTeX quality (missing fields, DOI format, etc.) |
| EndNote export preflight | `00-bib-endnote/check_endnote_export.py` | Check EndNote export files before import |
| EndNote import | `00-bib-endnote/import_library.py` | Normalize references with stable `refNNN` IDs |
| Word→LaTeX migration | `01-word-to-latex/migrate_project.py` | Map files to LaTeX project structure per spec |
| LaTeX→Word export | `02-latex-to-word/migrate_project.py` | Generate review-friendly `.docx`, explicitly reports degraded elements |
| Review package | `03-latex-review-diff/review_diff.py` | Generate review diff, triage, and TODO artifacts |
| Feedback ingest | `04-word-review-ingest/feedback_ingest.py` | Normalize Word feedback into structured issues |
| Reference check | `10-check-references/check_references.py` | Validate `\cite{}` keys against bibliography |
| Language check | `11-check-language/check_language.py` | 28+ deterministic language rule checks |
| Format check | `12-check-format/check_format.py` | Figure/table blocks, labels, cross-references, front matter |
| Content check | `13-check-content/check_content.py` | Content structure and abstract metadata |
| Deep language check | `14-check-language-deep/check_language_deep.py` | Higher-order language screening |
| Compile diagnostics | `15-check-compile/check_compile.py` | Structured parsing of LaTeX compile logs |
| Readiness gate | `16-check-readiness/check_readiness.py` | Aggregate all reports, output PASS/WARN/BLOCK |
| Defense prep | `17-defense-pack/*.py` | Outline, chapter highlights, figure inventory, candidate visuals, talk notes |
| Safe fixers | `20-fix-*` to `24-fix-*` | Report-driven patches with dry-run preview before apply |
| Rule-pack tooling | `90-rules/*.py` | Pack creation, lint, completeness checks, scorecard |

---

## Rule Pack System

Starter and example packs included:

```text
90-rules/packs/
 ├── university-generic/     # Generic university thesis starter
 ├── journal-generic/        # Generic journal article starter
 ├── tsinghua-thesis/        # Tsinghua University example
 └── demo-university-thesis/ # Concrete non-Tsinghua example pack
```

Create a custom rule pack:

```bash
python 90-rules/create_pack.py \
  --pack-id my-university \
  --display-name "My University Thesis" \
  --starter university-generic \
  --kind university-thesis
```

Rule packs encode school/journal-specific policy: project layout, reference format, language rules, formatting requirements, content requirements.

---

## Current Boundaries

| Not Supported / Not Promised | Current Position |
|:---|:---|
| Full GUI or web editor | CLI-first repository |
| Full compile orchestration | Parses existing logs; does not replace TeX toolchain |
| Universal school compliance | Rule packs encode policy; institutions still need manual confirmation |
| Automatic understanding of advisor intent | Feedback ingest is bounded and review-gated |
| AI-generated thesis content | System checks and fixes bounded issues; it does not write the thesis |
| Final PPT generation | Defense prep creates editable planning artifacts only |
| Formal rule-pack registry | Current workflows are local, Git-tracked, or handoff-oriented |
| Word .docx direct parsing | Word→LaTeX migration requires pre-export to `.tex` and `.bib` |
| Perfect LaTeX→Word conversion | Review-friendly mode is primary; some constructs will degrade |

---

## Technical Architecture

```text
thesis-skills/
├── core/                   # Shared implementations (project discovery, checkers, fixers, reports)
├── 00-bib-endnote/         # EndNote bibliography intake
├── 00-bib-zotero/          # Zotero bibliography intake and Word sync
├── 01-word-to-latex/       # Word→LaTeX migration (file mapping layer)
├── 02-latex-to-word/       # LaTeX→Word export (review-friendly)
├── 03-latex-review-diff/   # Review package and triage workflow
├── 04-word-review-ingest/  # Word feedback normalization
├── 10-check-references/    # Reference checks
├── 11-check-language/      # Language checks (28+ rules)
├── 12-check-format/        # Format checks
├── 13-check-content/       # Content checks
├── 14-check-language-deep/ # Deep language screening
├── 15-check-compile/       # Compile-log diagnostics
├── 16-check-readiness/     # Pre-submission readiness gate
├── 17-defense-pack/        # Defense preparation materials
├── 20-fix-references/      # Reference fixes
├── 21-fix-language-style/  # Language style fixes
├── 22-fix-format-structure/# Format structure fixes
├── 24-fix-language-deep/   # Deep language fixes (preview)
├── 90-rules/               # Rule pack system
├── 99-runner/              # Unified entry points (run_check_once.py, run_fix_cycle.py)
└── examples/               # Example projects
```

Detailed architecture in [`docs/architecture.md`](docs/architecture.md).

---

## Version History

| Release | Theme |
|:---|:---|
| v0.3.0 | Public repository restructure, bilingual README, CI, Zotero as primary bib path |
| v0.4.0 | EndNote XML/RIS/BibTeX import, DOI deduplication, `refNNN` stability |
| v0.5.x | Deterministic and deep language review plus selective patch previews |
| v0.6.0 | Review-friendly LaTeX-to-Word export, compile-log parsing, review-loop workflows |
| v0.7.x | Readiness gate, review-summary hardening, feedback-ingest calibration |
| v0.8.x | Defense prep, static showcase, rule-pack lint/completeness/schema/scorecard hardening |
| v1.0.0 | Stable public story across README, roadmap, site, manifest, rule-pack docs, and actual code paths |

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

Special thanks to [tuna/thuthesis](https://github.com/tuna/thuthesis) for their open-source LaTeX thesis template, which has greatly benefited Tsinghua University students and inspired this project.

---

## License

MIT License
