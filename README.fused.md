# Thesis Skills v1.0.0

<div align="center">

**Deterministic thesis workflow tools for citation sync, format checks, review handoff, and pre-submission readiness.**

Spend your time thinking, not fixing formatting.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/github/license/quzhiii/thesis-skills)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)](https://github.com/quzhiii/thesis-skills)
[![Showcase](https://img.shields.io/badge/Showcase-Live-success)](https://quzhiii.github.io/thesis-skills)

[中文文档](README.zh-CN.md) · **English** · [Showcase](https://quzhiii.github.io/thesis-skills)

</div>

---

## What is this?

Thesis Skills is **not** an AI writing assistant, **not** a thesis template, and **not** a tool that writes thesis content for you.

It is a **CLI workflow system** that connects the tools many graduate students and researchers already use: Word, Zotero, EndNote, LaTeX, structured check reports, safe fix patches, review handoff artifacts, and pre-submission readiness checks.

```text
Zotero / EndNote ──→ [ Thesis Skills ] ──→ LaTeX thesis
Word .docx ────────→                         │
                                              ├── Check reports
                                              ├── Dry-run fix patches
                                              ├── Review-friendly Word export
                                              ├── PASS / WARN / BLOCK readiness gate
                                              └── Defense preparation materials
```

The goal is simple: turn scattered, manual, error-prone thesis finishing work into a workflow that is **checkable, repeatable, and auditable**.

---

## Quickstart

Run the built-in sample project through the check pipeline:

```bash
git clone https://github.com/quzhiii/thesis-skills.git
cd thesis-skills

python run_check_once.py \
  --project-root examples/minimal-latex-project \
  --ruleset university-generic \
  --skip-compile
```

Expected result: structured check reports are generated without requiring a local LaTeX installation.

If you already have a LaTeX thesis project:

```bash
python run_check_once.py \
  --project-root thesis \
  --ruleset university-generic \
  --skip-compile
```

> Before publishing, verify that the sample project and all commands above run successfully from a clean clone.

---

## Why I built this

This project started from a real thesis workflow problem.

Like many researchers, I started writing my thesis in Word — low barrier to entry, my advisor uses it, and the Zotero plugin makes citation management easy. But by Chapter 3, the nightmare began: a three-line table took 40 minutes of border adjustments, adding one figure broke a dozen cross-references, and using AI to rewrite a paragraph collapsed Zotero field codes into plain text.

Word is convenient at the beginning. But for long dissertations, tables, captions, cross-references, citations, section numbering, and formatting rules all become fragile.

LaTeX is more stable for long-form academic writing, but migration, citation remapping, review handoff, format checking, and submission readiness are still repetitive and error-prone.

**Thesis Skills focuses on those mechanical but high-risk tasks.** Not to write your thesis for you, but to handle the repetitive, error-prone, time-consuming formatting labor.

---

## Problems it targets

| Problem | What usually goes wrong | Thesis Skills approach |
|---|---|---|
| Citation migration | Zotero / EndNote metadata gets lost or citation keys become unstable | Normalize references and maintain stable `refNNN` IDs |
| Word to LaTeX migration | Chapter structure, figures, tables, and references need manual reconstruction | Convert content into a rule-aware LaTeX project structure |
| AI-assisted editing | Word field codes or citation markers can collapse into plain text | Keep citation and review artifacts explicit and inspectable |
| Format checking | University or journal rules are checked manually and inconsistently | Run deterministic checks and output structured reports |
| Safe fixing | Blind automated edits may introduce new errors | Generate dry-run patches before applying changes |
| Advisor review | Advisors often expect Word, while the thesis source is LaTeX | Export review-friendly Word artifacts and track degraded elements |
| Pre-submission uncertainty | Reports are scattered and it is unclear whether the thesis is ready | Aggregate checks into a PASS / WARN / BLOCK readiness gate |
| Defense preparation | Figures, chapter highlights, and talk notes require repeated manual scanning | Generate structured defense preparation materials |

---

## Core workflow

| Stage | Traditional workflow | Thesis Skills output | Time saved |
|---|---|---|---|
| Bibliography intake | Export, rename, deduplicate, and manually stabilize citation keys (30–60 min) | Normalized bibliography and stable `refNNN` mapping | **~10×** |
| Word ↔ LaTeX migration | Rebuild structure, figures, tables, and references by hand (1–3 hrs) | Migration artifacts and review-friendly export paths | **~15×** |
| Deterministic checks | Repeated manual checking against school or journal rules (1–3 hrs/round) | JSON reports with files, lines, rules, severities, and suggestions | **~20×** |
| Safe fixes | Manually locate and edit every issue (1–2 hrs) | Previewable patches, dry-run first | **~10×** |
| Readiness gate | Read several disconnected reports before submission (30–60 min) | One PASS / WARN / BLOCK summary with next actions | **~30×** |
| Defense prep | Manually build outlines, figure inventories, and talking points (2–4 hrs) | Structured outline, figure inventory, candidate visuals, and notes | **~15×** |

> Time savings are conservative estimates for repetitive formatting work. The tool does not replace writing or thinking time.

---

## Example outputs

### Readiness gate report

```bash
python 16-check-readiness/check_readiness.py \
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

### Deterministic check report

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

## Use by scenario

### 1. I just switched from Word to LaTeX

```bash
# 1. Sync Zotero citations from Word to LaTeX
python 00-bib-zotero/sync_from_word.py \
  --project-root thesis \
  --word-file thesis.docx \
  --apply

# 2. Run comprehensive checks
python run_check_once.py \
  --project-root thesis \
  --ruleset tsinghua-thesis \
  --skip-compile

# 3. Preview and apply safe fixes
python run_fix_cycle.py \
  --project-root thesis \
  --ruleset tsinghua-thesis \
  --apply false
```

### 2. I already use LaTeX and want to check my thesis

```bash
python run_check_once.py \
  --project-root thesis \
  --ruleset tsinghua-thesis

python 16-check-readiness/check_readiness.py \
  --project-root thesis \
  --ruleset tsinghua-thesis \
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
  --ruleset tsinghua-thesis

python 17-defense-pack/generate_figure_inventory.py \
  --project-root thesis \
  --ruleset tsinghua-thesis

python 17-defense-pack/generate_talk_prep_notes.py \
  --project-root thesis \
  --ruleset tsinghua-thesis
```

---

## Pipeline overview

```text
THESIS WORKFLOW PHASE                  THESIS SKILLS MODULE
────────────────────────────────────────────────────────────────

1. Reference library
   · EndNote export                    00-bib-endnote/
   · Zotero sync                       00-bib-zotero/

2. Draft migration and review handoff
   · Word → LaTeX                      01-word-to-latex/
   · LaTeX → review-friendly Word      02-latex-to-word/
   · Review diff and TODOs             03-latex-review-diff/
   · Word feedback ingest              04-word-review-ingest/

3. Check phase
   · Reference integrity               10-check-references/
   · Language baseline checks          11-check-language/
   · Format structure checks           12-check-format/
   · Content completeness checks       13-check-content/
   · Deep language screening           14-check-language-deep/
   · Compile diagnostics               15-check-compile/

4. Fix phase
   · Reference fixes                   20-fix-references/
   · Language style fixes              21-fix-language-style/
   · Format structure fixes            22-fix-format-structure/
   · Deep language patches             24-fix-language-deep/

5. Submission readiness
   · PASS / WARN / BLOCK gate          16-check-readiness/

6. Defense preparation
   · Outline, figure inventory, notes  17-defense-pack/

7. Institutional adaptation
   · Custom rule packs                 90-rules/
```

---

## Rule packs

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

## What Thesis Skills is and is not

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
| [`docs/getting-started-zh.md`](docs/getting-started-zh.md) | Step-by-step beginner guide (Chinese, ~880 lines) |
| [`docs/architecture.md`](docs/architecture.md) | Workflow and module architecture |
| [`90-rules/`](90-rules/) | Rule-pack tooling and examples |
| [`examples/`](examples/) | Sample projects and demo inputs |
| [`site/`](site/) | Static showcase and landing-page materials |

---

## For absolute beginners

New to LaTeX or CLI tools? Start here:

1. **Day 1**: Read [`docs/getting-started-zh.md`](docs/getting-started-zh.md) — a complete walkthrough from installation to first check report
2. **Day 2**: Run the sample project (`examples/minimal-latex-project`) with `--skip-compile` to see all outputs
3. **Day 3**: Point `run_check_once.py` at your own thesis and review the check reports

---

## Module reference

| Stage | Module | Entrypoint |
|---|---|---|
| **Bibliography** | `00-bib-zotero/` | `sync_from_word.py`, `check_bib_quality.py` |
| | `00-bib-endnote/` | `check_endnote_export.py`, `import_library.py` |
| **Migration** | `01-word-to-latex/` | `migrate_project.py` |
| | `02-latex-to-word/` | `migrate_project.py` |
| | `03-latex-review-diff/` | `review_diff.py` |
| | `04-word-review-ingest/` | `feedback_ingest.py` |
| **Check** | `10-check-references/` | `check_references.py` |
| | `11-check-language/` | `check_language.py` (28+ rules) |
| | `12-check-format/` | `check_format.py` |
| | `13-check-content/` | `check_content.py` |
| | `14-check-language-deep/` | `check_language_deep.py` |
| | `15-check-compile/` | `check_compile.py` |
| **Fix** | `20-fix-references/` | `fix_references.py` |
| | `21-fix-language-style/` | `fix_language_style.py` |
| | `22-fix-format-structure/` | `fix_format_structure.py` |
| | `24-fix-language-deep/` | `fix_language_deep.py` |
| **Gate** | `16-check-readiness/` | `check_readiness.py` |
| **Defense** | `17-defense-pack/` | `generate_outline.py`, `generate_figure_inventory.py`, `generate_talk_prep_notes.py` |
| **Rules** | `90-rules/` | `create_pack.py`, `lint_pack.py`, `scorecard.py` |
| **Runner** | `99-runner/` | `run_check_once.py`, `run_fix_cycle.py` |

---

## Template recommendations

Thesis Skills is not a LaTeX thesis template. It is designed to work alongside mature templates and institution-specific document classes.

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
