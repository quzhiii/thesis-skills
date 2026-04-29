# Thesis Skills v1.0.0

<div align="center">

**Deterministic thesis workflow tools for citation sync, format checks, review handoff, and pre-submission readiness.**

Spend your time thinking, not fixing formatting.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/github/license/quzhiii/thesis-skills)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)](https://github.com/quzhiii/thesis-skills)
[![Showcase](https://img.shields.io/badge/Showcase-Live-success)](https://quzhiii.github.io/thesis-skills)

[中文文档](README.zh-CN.md) · **English** · [Showcase](https://quzhiii.github.io/thesis-skills)

[Quickstart](#quickstart) · [Outputs](#outputs) · [Scenarios](#scenarios) · [Rule Packs](#rule-packs) · [Boundaries](#boundaries)

</div>

---

## What is this?

Thesis Skills is **not** an AI writing assistant, **not** a thesis template, and **not** a tool that writes thesis content for you.

It is a **CLI workflow system** that connects the tools many graduate students and researchers already use: Word, Zotero, EndNote, LaTeX, structured check reports, safe fix patches, review handoff artifacts, and pre-submission readiness checks.

```text
                  ┌───────────────────────────────────────────┐
Zotero / EndNote ─┤                                           ├─→ LaTeX thesis
Word .docx ───────┤              Thesis Skills                ├─→ Review Word export
LaTeX project ────┤                                           ├─→ Defense pack
                  └───────────────────────────────────────────┘
                                      │
                                      ▼
                 check reports → dry-run fixes → readiness gate
```

The goal is simple: turn scattered, manual, error-prone thesis finishing work into a workflow that is **checkable, repeatable, and auditable**.

For repetitive finishing work, the expected time savings are concrete:

| Workflow | Manual baseline | With Thesis Skills |
|---|---:|---:|
| Bibliography intake | 30-60 min | 2-5 min |
| Word ↔ LaTeX review handoff | 1-3 hrs | 5-10 min |
| Deterministic format checks | 1-3 hrs | 2-5 min |
| Safe report-driven fixes | 1-2 hrs | 5-10 min |
| Pre-submission readiness review | 30-60 min | 1-2 min |
| Defense prep inventory | 2-4 hrs | 10-15 min |

> Time savings are conservative estimates for repetitive formatting and handoff work. Thesis Skills does not replace writing, thinking, advisor judgment, or institutional confirmation.

---

## Quickstart

Run the built-in sample project through the check pipeline:

```bash
git clone https://github.com/quzhiii/thesis-skills.git
cd thesis-skills

test -d examples/minimal-latex-project

python run_check_once.py \
  --project-root examples/minimal-latex-project \
  --ruleset university-generic \
  --skip-compile
```

Expected result: JSON reports are written to `examples/minimal-latex-project/reports/`, including `run-summary.json` and `readiness-report.json`, without requiring a local LaTeX installation.

If you already have a LaTeX thesis project:

```bash
python run_check_once.py \
  --project-root thesis \
  --ruleset university-generic \
  --skip-compile
```

More details: [`docs/quickstart.md`](docs/quickstart.md).

---

## Outputs

### Hero workflow

```text
1. Intake        2. Check           3. Fix safely        4. Gate          5. Handoff
──────────       ───────────        ─────────────        ─────────        ─────────────
Zotero           references         dry-run patches      PASS             advisor Word
EndNote     →    language      →    preview first   →    WARN       →     review TODOs
Word/LaTeX       format            apply explicitly      BLOCK            defense pack
```

### Readiness gate preview

```text
┌──────────────────────────────────────────────────────────────┐
│ Readiness verdict: WARN                                      │
├───────────────────────┬────────┬─────────────────────────────┤
│ Dimension             │ Status │ Why it matters              │
├───────────────────────┼────────┼─────────────────────────────┤
│ References            │ PASS   │ all cite keys resolve       │
│ Language              │ WARN   │ 2 style warnings remain     │
│ Format                │ PASS   │ labels and refs are stable  │
│ Compile evidence      │ WARN   │ skipped in demo mode        │
│ Export evidence       │ WARN   │ not produced by smoke test  │
│ Review-loop evidence  │ WARN   │ not produced by smoke test  │
└───────────────────────┴────────┴─────────────────────────────┘

Next actions:
1. Review reports/check_language-report.json
2. Generate Word export / review-loop artifacts when those handoffs are needed
3. Re-run without --skip-compile before final submission
```

A real run writes machine-readable artifacts such as:

- `reports/check_references-report.json`
- `reports/check_language-report.json`
- `reports/check_format-report.json`
- `reports/check_content-report.json`
- `reports/readiness-report.json`
- `reports/run-summary.json`

Example JSON snippets and demo walkthroughs: [`docs/examples.md`](docs/examples.md).

---

## Scenarios

### 1. I just switched from Word to LaTeX

```bash
python 00-bib-zotero/sync_from_word.py \
  --project-root thesis \
  --word-file thesis.docx \
  --apply

python run_check_once.py \
  --project-root thesis \
  --ruleset university-generic \
  --skip-compile
```

### 2. I already use LaTeX and want to check my thesis

```bash
python run_check_once.py \
  --project-root thesis \
  --ruleset university-generic

python 16-check-readiness/check_readiness.py \
  --project-root thesis \
  --ruleset university-generic \
  --mode advisor-handoff
```

### 3. My advisor needs a Word version for review

```bash
python 02-latex-to-word/migrate_project.py \
  --project-root thesis \
  --output-file thesis-review.docx \
  --profile review-friendly \
  --apply true
```

### 4. I received Word feedback and need to update LaTeX

```bash
python 04-word-review-ingest/feedback_ingest.py \
  --project-root thesis \
  --input review-feedback.json

python 03-latex-review-diff/review_diff.py \
  --project-root thesis
```

### 5. I am preparing for defense

```bash
python 17-defense-pack/generate_outline.py \
  --project-root thesis \
  --ruleset university-generic

python 17-defense-pack/generate_figure_inventory.py \
  --project-root thesis \
  --ruleset university-generic
```

More scenarios: [`docs/examples.md`](docs/examples.md).

---

## Rule Packs

Rule packs encode institution- or journal-specific requirements: project layout, reference format, language rules, formatting rules, content requirements, and readiness criteria.

```text
90-rules/packs/
 ├── university-generic/      # Generic university thesis starter
 ├── journal-generic/         # Generic journal article starter
 ├── tsinghua-thesis/         # Tsinghua University example
 └── demo-university-thesis/  # Concrete non-Tsinghua example pack
```

Create a custom rule pack:

```bash
python 90-rules/create_pack.py \
  --pack-id my-university \
  --display-name "My University Thesis" \
  --starter university-generic \
  --kind university-thesis
```

---

## Tested on

- Python 3.10+
- Windows / macOS / Linux
- LaTeX optional for the `--skip-compile` demo; run without `--skip-compile` when you want compile-log diagnostics

---

## Boundaries

| Thesis Skills is | Thesis Skills is not |
|---|---|
| A bridge between Word, Zotero, EndNote, and LaTeX | A thesis template or document class |
| A deterministic checker for formatting and structural rules | An AI writing assistant that generates thesis content |
| A report-driven workflow with dry-run previews | A replacement for Grammarly or other prose editors |
| A pre-submission readiness gate | An automatic final defense PPT generator |
| Extensible through institution-specific rule packs | A guarantee that every school or journal rule is already supported |
| CLI-based with auditable artifacts | A GUI or web-based editor |

---

## Documentation

| Document | Purpose |
|---|---|
| [`docs/quickstart.md`](docs/quickstart.md) | Minimal install and first check run |
| [`docs/examples.md`](docs/examples.md) | Output previews and scenario examples |
| [`docs/modules.md`](docs/modules.md) | Full module reference moved out of the README |
| [`docs/architecture.md`](docs/architecture.md) | Workflow and module architecture |
| [`docs/getting-started-zh.md`](docs/getting-started-zh.md) | Step-by-step beginner guide in Chinese |
| [`CHANGELOG.md`](CHANGELOG.md) | Release history |

---

## Module reference

The long module table lives in [`docs/modules.md`](docs/modules.md) so this README stays focused on the product workflow.

---

## Template recommendations

Thesis Skills is designed to work alongside mature templates and institution-specific document classes.

| Institution | Template repository |
|---|---|
| Tsinghua University | [tuna/thuthesis](https://github.com/tuna/thuthesis) |
| Shanghai Jiao Tong University | [sjtug/SJTUThesis](https://github.com/sjtug/SJTUThesis) |
| University of Science and Technology of China | [ustctug/ustcthesis](https://github.com/ustctug/ustcthesis) |
| Peking University | [CasperVector/pkuthss](https://github.com/CasperVector/pkuthss) |
| Stanford University | [dcroote/stanford-thesis-example](https://github.com/dcroote/stanford-thesis-example) |
| University of Cambridge | [cambridge/thesis](https://github.com/cambridge/thesis) |

---

## Acknowledgments

Special thanks to [tuna/thuthesis](https://github.com/tuna/thuthesis) and other open-source thesis template projects. These projects make high-quality LaTeX thesis writing more accessible and inspired the workflow design of Thesis Skills.

---

## License

MIT License
