# Thesis Skills v2.0.0

<div align="center">

**Deterministic thesis workflow tools for citation sync, format checks, review handoff, and pre-submission readiness.**

Spend your time thinking, not fixing formatting.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/github/license/quzhiii/thesis-skills)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)](https://github.com/quzhiii/thesis-skills)
[![Showcase](https://img.shields.io/badge/Showcase-Live-success)](https://quzhiii.github.io/thesis-skills)

[中文文档](README.zh-CN.md) · **English** · [Showcase](https://quzhiii.github.io/thesis-skills)

[Quickstart](#quickstart) · [Outputs](#outputs) · [Scenarios](#scenarios) · [Updating](#updating-your-local-copy) · [Rule Packs](#rule-packs) · [Creating Your Own](#creating-your-own-school-rule-pack) · [Boundaries](#boundaries)

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

| Workflow | Manual baseline | With Thesis Skills | Speedup |
|---|---:|---:|---:|
| Bibliography intake | 30-60 min | 2-5 min | **~10× faster** |
| Word ↔ LaTeX review handoff | 1-3 hrs | 5-10 min | **~15× faster** |
| Deterministic format checks | 1-3 hrs | 2-5 min | **~20× faster** |
| Safe report-driven fixes | 1-2 hrs | 5-10 min | **~10× faster** |
| Pre-submission readiness review | 30-60 min | 1-2 min | **~30× faster** |
| Defense prep inventory | 2-4 hrs | 10-15 min | **~15× faster** |

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
- `reports/citation-integrity-report.json`
- `reports/citation-integrity-report.md`
- `reports/citation-issues.csv`
- `reports/check_language-report.json`
- `reports/check_format-report.json`
- `reports/check_content-report.json`
- `reports/readiness-report.json`
- `reports/run-summary.json`

Example JSON snippets and demo walkthroughs: [`docs/examples.md`](docs/examples.md).

### Citation Integrity preview

The current v1.2 release line includes a local-first Citation Integrity workflow for pre-submission reference risk:

```text
References: BLOCK
- cited keys missing from bibliography files
- duplicate citation keys with conflicting metadata
- DOI/year field warnings
- LaTeX undefined-citation warnings from local compile logs
```

Boundary: the current Citation Integrity workflow only checks local citation integrity. It does not query external databases, does not detect hallucinated references yet, and never auto-inserts or rewrites citations.

### External Verification (v2.0.0)

An optional external metadata verification layer queries **CrossRef**, **OpenAlex**, and **Semantic Scholar** for each bibliography entry and writes `reports/external-verification-report.json`.

```bash
python 18-verify-references/verify_external_references.py \
  --project-root thesis \
  --ruleset university-generic
```

Or via the existing reference checker with an explicit flag:

```bash
python 10-check-references/check_references.py \
  --project-root thesis \
  --ruleset university-generic \
  --with-external-verification
```

V2.0 boundaries:

- Providers: CrossRef, OpenAlex, and Semantic Scholar.
- No readiness gate blocking from the local References dimension.
- `external_verification` is advisory only.
- No hallucination-risk score yet.
- No automatic citation rewriting.
- Network failures degrade to `UNAVAILABLE`, never crash.

## What's new in v2.0.0

- External metadata verification is now part of the public workflow as an advisory layer.
- A run can emit `reports/external-verification-report.json` alongside the Citation Integrity reports for machine review and manual triage.
- The repository includes both `examples/citation-integrity-broken/` and `examples/citation-integrity-clean/` plus external verification behavior that stays stable when the network is unavailable.
- The readiness gate now surfaces `external_verification` as an advisory dimension without changing the local `references` verdict.

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

Rule packs are the most important concept in Thesis Skills: they encode your institution's formatting requirements as structured YAML so the checkers know what counts as "correct" and what counts as an issue.

### Built-in Packs

```text
90-rules/packs/
 ├── university-generic/        # Generic university thesis starter (default, permissive)
 ├── journal-generic/           # Generic journal article starter (English, minimal)
 ├── tsinghua-thesis/           # Tsinghua University Master's/PhD thesis pack
 │                              #   First-pass calibrated against 《研究生学位论文写作指南（202503）》
 │                              #   CJK/English rules, figure numbering, and reference defaults tuned to the guide
 └── demo-university-thesis/    # Concrete non-Tsinghua example pack
```

- `university-generic` is suitable for **most Chinese universities** — broad coverage, moderate thresholds.
- `tsinghua-thesis` is specifically calibrated for Tsinghua students: GB/T 7714 reference style, mixed CJK/English rules per the university writing guide, and Chinese chapter naming conventions. For many Tsinghua thesis projects this works as a direct starting point, but you should still verify against your department template and local requirements.
- `journal-generic` targets English journal submissions, with CJK-specific rules disabled.

### Inside a Rule Pack

Each pack is a folder with three files:

```
90-rules/packs/your-school/
 ├── pack.yaml      # Metadata: name, kind, version
 ├── rules.yaml     # Rules: what to check, severity, thresholds
 └── mappings.yaml  # File/path mappings (main tex candidates, bib paths)
```

`rules.yaml` is organized by dimension:

| Section | Controls | Examples |
|---|---|---|
| `project` | Project structure: main tex file names, chapter globs, bib paths | `main_tex_candidates`, `chapter_globs` |
| `reference` | Citation integrity: missing keys, orphans, duplicates, bib quality | `missing_key: error` |
| `language` | Surface language: CJK/Latin spacing, brackets, punctuation, weak phrases | `cjk_latin_spacing`, `bracket_mismatch` |
| `language_deep` | Deep language: connectors, collocations, inference strength, boundary signposts | `inference_overclaim`, `boundary_signpost` |
| `consistency` | Terminology: variant detection for the same concept | `terminology_consistency` |
| `format` | Format structure: figure/table lists, numbering, cross-references | `require_list_of_figures` |
| `content` | Content completeness: required sections, keyword count | `required_sections` |
| `compile` | Compile diagnostics: engine, error categories, severity mapping | `engine_hint: xelatex` |

### Creating Your Own School Rule Pack

If you are not a Tsinghua student, or your department/journal has specific requirements, create a custom pack from one of the built-in starters.

**Step 1: Scaffold the pack**

```bash
python 90-rules/create_pack.py \
  --pack-id my-university \
  --display-name "My University Master's Thesis" \
  --starter university-generic \
  --kind university-thesis
```

This generates three files under `90-rules/packs/my-university/`, copied from `university-generic` as a starting point.

**Step 2: Adjust project structure**

Edit `rules.yaml` → `project` to match your thesis directory layout:

```yaml
project:
  main_tex_candidates:       # Possible names for your main tex file, in priority order
    - thesis.tex
    - main.tex
  chapter_globs:             # Where chapter files live and their naming pattern
    - chapters/*.tex
  bibliography_files:        # Paths to .bib files
    - ref/refs.bib
```

**Step 3: Tune rules to your school's guide**

Check your institutional thesis writing guide and decide rule by rule:

- **Keep enabled**: Rules that your guide explicitly requires and the checker can reliably detect (e.g., missing citation keys, figure/table numbering)
- **Demote**: Rules your guide does not mandate — change `severity` from `warning` to `info` (e.g., CJK/Latin spacing if not required)
- **Disable**: Rules clearly irrelevant to your institution or discipline — set `enabled: false` (e.g., CJK rules for English-only theses)

Example — demoting CJK spacing when your guide doesn't require it:

```yaml
# Before
cjk_latin_spacing:
  enabled: true
  severity: warning

# After (school guide does not mandate CJK-Latin spacing)
cjk_latin_spacing:
  enabled: true
  severity: info
```

**Step 4: Update required section names**

If your thesis uses Chinese section naming (not English IMRaD), sync the content rules:

```yaml
content:
  required_sections:
    - Introduction (or 绪论)
    - Literature Review (or 文献综述)
    - Methods (or 研究方法)
    - Conclusion (or 结论)
```

**Step 5: Run checks with your custom pack**

```bash
python run_check_once.py \
  --project-root thesis \
  --ruleset my-university \
  --skip-compile
```

**Step 6: Validate and iterate**

After running, inspect the JSON reports under `reports/`. If you notice:

- **Too many false positives in a category** → demote or disable that rule
- **Real issues not detected** → check if the rule is enabled and severity is set high enough
- **Project discovery failed** → adjust `main_tex_candidates` or `chapter_globs`

Tweak → re-run → review reports. Most packs converge in 1–2 calibration rounds.

> **For non-Tsinghua users**: If your calibrated rule pack is stable and you'd like it featured, PRs adding new packs to `90-rules/packs/` are welcome. Future students from your school won't have to start from scratch.

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

## Release history

- `v2.0.0`: added CrossRef / OpenAlex / Semantic Scholar external verification, consensus candidates, and an `external_verification` readiness advisory.
- `v1.0.0`: stabilized the public workflow story across README, roadmap, site, examples, and code paths.
- `v1.1.0`: added the local-first Citation Integrity engine and readiness integration.
- `v1.2.0`: added Markdown/CSV Citation Integrity outputs, clean/broken demos, and public version-line alignment.
- See [`CHANGELOG.md`](CHANGELOG.md) for the full changelog.

---

## Updating your local copy

Downloading or cloning the repository once does **not** make future updates appear automatically on your machine.

Choose the update path that matches how you got Thesis Skills:

### If you cloned with Git

Run:

```bash
git pull origin main
```

This fetches the newest committed changes from GitHub into your local checkout.

If you want to see what changed before pulling:

```bash
git fetch origin
git log --oneline HEAD..origin/main
```

### If you downloaded a ZIP

A ZIP download is just a snapshot. It will **not** sync by itself.

To get updates, either:

1. download a fresh ZIP from GitHub and replace your local copy manually, or
2. switch to a Git clone so future updates only need `git pull`

### If you edited the repository locally

Pulling new changes is easiest when your local copy has no uncommitted edits.

Before updating, check:

```bash
git status
```

If you have local modifications, commit or back them up first so `git pull` does not create conflicts unexpectedly.

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
