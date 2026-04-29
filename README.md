# Thesis Skills v1.0.0

<div align="center">

![Thesis Skills](https://img.shields.io/badge/Thesis-Skills-4285f4?style=for-the-badge&logo=book&logoColor=white)

**Deterministic, inspectable thesis and journal workflow system**
*Bibliography intake • LaTeX/Word handoff • Checkers • Safe fixers • Readiness gates • Rule packs*

[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/github/license/quzhiii/thesis-skills)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)](https://github.com/quzhiii/thesis-skills)
[![Landing Page](https://img.shields.io/badge/🚀%20Landing%20Page-Live-success)](https://quzhiii.github.io/thesis-skills)

[中文文档](README.zh-CN.md) • **English** • [🚀 Showcase](https://quzhiii.github.io/thesis-skills)

[Quick Start](#quick-start) • [Core Workflows](#core-workflows) • [Rule Packs](#rule-pack-system) • [Boundaries](#current-boundaries) • [Roadmap](docs/roadmap.md) • [Architecture](docs/architecture.md) • [Contributing](CONTRIBUTING.md)

</div>

---

## What Thesis Skills Is

`thesis-skills` is a deterministic, report-driven workflow layer for academic writing projects. It helps you move a thesis or journal manuscript through bibliography intake, Word/LaTeX handoff, deterministic checks, bounded fixes, review-loop artifacts, readiness decisions, defense-prep artifacts, and reusable school/journal rule packs.

It is intentionally **not** a general AI writing assistant, a thesis template, a GUI editor, a collaboration platform, or a promise of universal submission compliance. Every workflow should leave explicit artifacts that a human can inspect.

---

## Why Thesis Skills?

| Pain Point | Traditional Workflow | Thesis Skills |
|:---|:---|:---|
| Citation migration Word→LaTeX | Manual mapping, error-prone | Auto-extract and sync with stable IDs |
| Bibliography intake | Copy-paste from EndNote/Zotero | XML/RIS/BibTeX import and quality checks |
| University or journal policy | Read long docs manually | YAML rule packs and repeatable checks |
| Review handoff | Ad hoc Word exports and scattered comments | Review-friendly export, diff, ingest, and TODO artifacts |
| Final confidence | Manually inspect many reports | Bounded `PASS / WARN / BLOCK` readiness verdict |
| Defense prep | Re-read the whole thesis while making slides | Outline, highlights, figure inventory, candidate visuals, and talk-prep notes |

---

## Core Workflows

| Workflow | Entrypoint | Output / Role |
|:---|:---|:---|
| Zotero bibliography sync | `00-bib-zotero/sync_from_word.py` | Word citation mapping into LaTeX-friendly references |
| Zotero bibliography quality check | `00-bib-zotero/check_bib_quality.py` | Structured bibliography findings |
| EndNote preflight | `00-bib-endnote/check_endnote_export.py` | Export quality warnings before import |
| EndNote import | `00-bib-endnote/import_library.py` | Normalized references with stable `refNNN` IDs |
| Word→LaTeX migration | `01-word-to-latex/migrate_project.py` | Structured migration report |
| LaTeX→Word export | `02-latex-to-word/migrate_project.py` | Review-friendly `.docx` and limitation summary |
| Review package | `03-latex-review-diff/review_diff.py` | Review diff, triage, digest, and TODO-oriented artifacts |
| Feedback ingest | `04-word-review-ingest/feedback_ingest.py` | Bounded feedback normalization into structured issues |
| Deterministic checks | `10-check-*` to `14-check-*` | Reference, language, format, content, and deep-language reports |
| Compile diagnostics | `15-check-compile/check_compile.py` | Structured findings from existing LaTeX logs |
| Readiness gate | `16-check-readiness/check_readiness.py` | `PASS / WARN / BLOCK` summary from existing artifacts |
| Defense prep | `17-defense-pack/*.py` | Outline, highlights, figures, candidate visuals, and talk notes |
| Safe fixers | `20-fix-*` to `24-fix-*` | Report-driven patches with dry-run or review-gated application |
| Rule-pack tooling | `90-rules/*.py` | Pack creation, draft scaffolding, lint, completeness, schema, scorecard |

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

If you are completely new to LaTeX, start with the Chinese beginner guide first:

- [Beginner getting-started guide (Chinese)](docs/getting-started-zh.md)

### EndNote Intake

```bash
python 00-bib-endnote/check_endnote_export.py \
  --project-root thesis \
  --input refs.xml

python 00-bib-endnote/import_library.py \
  --project-root thesis \
  --input refs.xml \
  --apply
```

### Zotero Sync + Check + Fix Loop

```bash
python 00-bib-zotero/sync_from_word.py \
  --project-root thesis \
  --word-file thesis.docx \
  --apply

python run_check_once.py \
  --project-root thesis \
  --ruleset tsinghua-thesis \
  --skip-compile

python run_fix_cycle.py \
  --project-root thesis \
  --ruleset tsinghua-thesis \
  --apply false
```

### Compile Diagnostics

```bash
python run_check_once.py \
  --project-root thesis \
  --ruleset tsinghua-thesis

python run_check_once.py \
  --project-root thesis \
  --ruleset tsinghua-thesis \
  --skip-compile
```

Positioning:

- compile parsing translates existing LaTeX log output into structured findings
- it does not replace your TeX toolchain or guarantee full build orchestration
- if no log is available, the runner reports that explicitly instead of crashing

### LaTeX to Word Review Export

```bash
python 02-latex-to-word/migrate_project.py \
  --project-root thesis \
  --output-file thesis-review.docx \
  --profile review-friendly \
  --apply false
```

Positioning:

- `review-friendly` is the first-class implemented export profile
- stricter submission-friendly export remains a future path
- unsupported constructs should be surfaced explicitly rather than hidden

### Review Loop

```bash
python 03-latex-review-diff/review_diff.py \
  --project-root thesis

python 04-word-review-ingest/feedback_ingest.py \
  --project-root thesis \
  --input review-feedback.json
```

Positioning:

- review loop is a bounded workflow for revision rounds, not a collaboration platform
- diff/triage and feedback ingest stay inspectable through explicit JSON artifacts
- ambiguous or high-judgement changes remain review-gated rather than auto-applied

### Pre-Submission Gate

```bash
python 16-check-readiness/check_readiness.py \
  --project-root thesis \
  --ruleset tsinghua-thesis \
  --mode advisor-handoff
```

Positioning:

- the gate summarizes existing reports and workflow artifacts
- it returns `PASS`, `WARN`, or `BLOCK` with blockers, warnings, next actions, and source references
- it does not re-run the whole toolchain, auto-fix issues, or claim universal submission compliance
- `run_check_once.py` can surface the readiness gate as `derived_artifacts.readiness_gate` in `run-summary.json`

### Defense Prep

```bash
python 17-defense-pack/generate_outline.py \
  --project-root thesis \
  --ruleset tsinghua-thesis

python 17-defense-pack/generate_figure_inventory.py \
  --project-root thesis \
  --ruleset tsinghua-thesis
```

Positioning:

- defense-prep scripts generate bounded planning artifacts, not final slides
- outputs are editable outlines, summaries, inventories, candidate lists, and notes
- the system does not decide your final talk strategy or design PPT pages for you

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

Create a pack from a starter:

```bash
python 90-rules/create_pack.py \
  --pack-id my-university \
  --display-name "My University Thesis" \
  --starter university-generic \
  --kind university-thesis
```

Create a draft pack from intake metadata:

```bash
python 90-rules/create_draft_pack.py \
  --intake adapters/intake/example-intake.json
```

Current rule-pack contract docs:

- `90-rules/THESIS_RULE_PACKS.md`
- `90-rules/STARTER_PACK_BASELINE.md`
- `90-rules/MIXED_PACK_WORKFLOWS.md`

Lint a pack before trusting or sharing it:

```bash
python 90-rules/lint_pack.py --pack-path 90-rules/packs/university-generic
```

The current linter checks and reports:

- required pack files: `pack.yaml`, `rules.yaml`, `mappings.yaml`
- baseline metadata completeness in `pack.yaml`
- required top-level sections in `rules.yaml`: `project`, `reference`, `language`
- accepted `mappings.yaml` shapes:
  - starter-pack shape: `mappings`
  - draft-pack shape: `source_template_mappings` + `chapter_role_mappings`
- scorecard status for required files, metadata completeness, baseline completeness, schema consistency, overall status, and finding counts

---

## Current Boundaries

| Not Supported / Not Promised | Current Position |
|:---|:---|
| Full GUI or web editor | CLI-first repository |
| Full compile orchestration | Parses existing logs; does not replace TeX tools |
| Universal school compliance | Rule packs encode policy; institutions still need manual confirmation |
| Automatic understanding of advisor intent | Feedback ingest is bounded and review-gated |
| AI-generated thesis content | The system checks, organizes, and fixes bounded issues; it does not write the thesis |
| Final PPT generation | Defense prep creates artifacts for humans to edit |
| Formal rule-pack registry | Current workflows are local, Git-tracked, or handoff-oriented |

---

## Technical Architecture

```text
thesis-skills/
├── core/                   # Shared implementations
├── 00-bib-*/               # Bibliography workflows
├── 01-word-to-latex/       # Migration workflow
├── 02-latex-to-word/       # Review-first export workflow
├── 03-latex-review-diff/   # Review package and triage workflow
├── 04-word-review-ingest/  # Bounded feedback normalization workflow
├── 10-check-*/             # Deterministic checkers
├── 15-check-compile/       # Compile-log diagnostic translation
├── 16-check-readiness/     # Bounded pre-submission readiness gate
├── 17-defense-pack/        # Bounded defense-prep artifact generators
├── 20-fix-*/               # Safe fixers
├── 90-rules/               # Rule pack system
└── 99-runner/              # Entry points
```

See [`docs/architecture.md`](docs/architecture.md) for the detailed layer model.

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

See [`docs/roadmap.md`](docs/roadmap.md) for the current stabilization checklist.

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
