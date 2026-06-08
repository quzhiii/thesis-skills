# Thesis Skills v3.4.1

<div align="center">

**Deterministic thesis workflow tools for citation sync, format checks, review handoff, and pre-submission readiness.**

Spend your time thinking, not fixing formatting.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/github/license/quzhiii/thesis-skills)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)](https://github.com/quzhiii/thesis-skills)
[![Showcase](https://img.shields.io/badge/Showcase-Live-success)](https://quzhiii.github.io/thesis-skills)

[中文文档](README.zh-CN.md) · **English** · [Showcase](https://quzhiii.github.io/thesis-skills)

[What's New](#whats-new-in-v341) · [Quickstart](#quickstart) · [Outputs](#outputs) · [Scenarios](#scenarios) · [Updating](#updating-your-local-copy) · [Rule Packs](#rule-packs) · [Creating Your Own](#creating-your-own-school-rule-pack) · [Boundaries](#boundaries)

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

## What's new in v3.4.1

- **Report navigation polish**: local HTML report surfaces now cross-link `index`, `final-audit`, `reference-ledger`, `claim-citation`, readiness, and raw JSON / CSV artifacts more consistently.
- **Support-risk heuristic calibration**: `possible_overclaim` no longer duplicates `possible_topic_mismatch` when a `PASS` reference is already flagged by the more specific topic-mismatch signal.
- **Readiness Gate Integration** remains in place from V3.2, and V3.4 extends that citation evidence stack with final-audit and local HTML report surfaces.
- **Final-audit surfaces**: new deterministic final cleanup, statistical consistency, and manual-anchor checks feed `reports/final-audit-report.json`.
- **Reference audit handoff**: `28-reference-audit-ledger/build_reference_audit_ledger.py` writes a spreadsheet-friendly `reports/reference-audit-ledger.csv` from existing reference evidence.
- **Static local report UX**: `reports/index.html`, `reports/final-audit-report.html`, `reports/reference-audit-ledger.html`, and `reports/claim-citation-triage.html` make JSON / CSV artifacts easier to review without replacing them as source of truth.
- **Claim-citation support review** now includes conservative advisory signals such as `possible_topic_mismatch`, `possible_outdated_support`, and `possible_overclaim`.
- **V3.3 reference verification hardening** remains in place: final reference set parsing, DOI candidates, URL verification, scoped/resumable external verification, and the unified evidence pipeline runner `run_evidence_pipeline.py`.

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

The baseline `run_check_once.py` command writes machine-readable artifacts such as:

- `reports/check_bib_quality-report.json`
- `reports/check_references-report.json`
- `reports/citation-integrity-report.json`
- `reports/citation-integrity-report.md`
- `reports/citation-issues.csv`
- `reports/check_language-report.json`
- `reports/check_language_deep-report.json`
- `reports/check_format-report.json`
- `reports/check_content-report.json`
- `reports/readiness-report.json`
- `reports/run-summary.json`

Optional final-audit foundation artifact:

- `reports/final-cleanup-report.json` from `23-check-final-cleanup/check_final_cleanup.py`
- `reports/statistical-consistency-report.json` from `25-check-statistical-consistency/check_statistical_consistency.py`
- `reports/manual-anchor-report.json` from `26-check-manual-anchor/check_manual_anchor.py`
- `reports/final-audit-report.json` from `27-final-audit-report/build_final_audit_report.py`
- `reports/reference-audit-ledger.csv` from `28-reference-audit-ledger/build_reference_audit_ledger.py`
- `reports/index.html` from `29-report-index/build_report_index.py`
- `reports/final-audit-report.html` from `30-final-audit-html/build_final_audit_html.py`
- `reports/reference-audit-ledger.html` from `31-reference-ledger-html/build_reference_audit_ledger_html.py`
- `reports/claim-citation-triage.html` from `32-claim-citation-html/build_claim_citation_html.py`

The optional v3.3 evidence pipeline writes the citation evidence artifacts:

- `reports/final-reference-set-report.json`
- `reports/final-reference-set-report.csv`
- `reports/external-verification-report.json` when external verification is not skipped
- `reports/missing-doi-candidates.json` when external verification is not skipped
- `reports/missing-doi-candidates.csv` when external verification is not skipped
- `reports/url-verification-report.json` when external verification is not skipped
- `reports/url-verification-flagged.csv` when external verification is not skipped
- `reports/hallucination-risk-report.json`
- `reports/high-risk-references.csv`
- `reports/claim-citation-triage-report.json`
- `reports/claim-citation-triage.md`
- `reports/claim-citation-triage.csv`

Example JSON snippets and demo walkthroughs: [`docs/examples.md`](docs/examples.md).

### Citation Integrity preview

The current v3.4.1 release line keeps local Citation Integrity as the first layer of pre-submission reference checking:

```text
References: BLOCK
- cited keys missing from bibliography files
- duplicate citation keys with conflicting metadata
- DOI/year field warnings
- LaTeX undefined-citation warnings from local compile logs
```

Boundary: the current Citation Integrity workflow only checks local citation integrity. It does not query external databases and never auto-inserts or rewrites citations. Use the external verification and hallucination risk layers for evidence-based screening.

### External Verification (v2.0.0)

An optional external metadata verification layer queries **CrossRef**, **OpenAlex**, and **Semantic Scholar** for each bibliography entry and writes `reports/external-verification-report.json`.

Use this when you want a fast authenticity screen for AI-drafted or suspicious-looking references before a manual final check.

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
- No automatic citation rewriting.
- Network failures degrade to `UNAVAILABLE`, never crash.

### Final Reference Set + DOI / URL checks (v3.3.0)

V3.3 hardens citation evidence by separating three scopes:

- `final`: references that actually entered the compiled bibliography via `.aux` / `.bbl`
- `cited`: citation keys extracted from TeX source `\cite{}` commands
- `all`: every entry in active `.bib` files

The final reference set builder writes:

- `reports/final-reference-set-report.json`
- `reports/final-reference-set-report.csv`

The external verification layer can now resume long runs and write partial results safely:

```bash
python 18-verify-references/verify_external_references.py \
  --project-root thesis \
  --ruleset university-generic \
  --scope final \
  --resume
```

V3.3 also adds advisory follow-up reports:

- `reports/missing-doi-candidates.json` and `.csv` for likely DOI additions
- `reports/url-verification-report.json` and `reports/url-verification-flagged.csv` for URL resolution checks

Boundaries:

- No LLM usage.
- No automatic DOI write-back to `.bib` files.
- No automatic URL replacement.
- URL verification checks whether a URL resolves; it does not judge document authenticity.

### Hallucination Risk (v3.0.0)

Score each bibliography entry for hallucination risk using local metadata and optional external verification evidence. The hallucination risk scorer reads `reports/external-verification-report.json` if present and writes `reports/hallucination-risk-report.json` plus `reports/high-risk-references.csv`.

```bash
python 19-check-hallucination-risk/check_hallucination_risk.py \
  --project-root thesis \
  --ruleset university-generic
```

Risk labels:

| Label | Meaning |
|---|---|
| `PASS` | Multi-source match with consistent metadata |
| `WARN` | Entry exists but fields differ noticeably |
| `REVIEW` | Possible match but evidence is weak |
| `HIGH_RISK` | No credible match found in enabled databases |
| `UNSUPPORTED` | Chinese-language or non-standard entry that cannot be auto-verified |

V3.0 boundaries:

- No LLM usage. Scoring is deterministic based on local metadata and external verification evidence.
- No automatic citation or bibliography rewriting.
- No live network calls. Reads `external-verification-report.json` if present.
- `UNSUPPORTED` means "cannot be automatically judged by enabled evidence," not "safe."
- `HIGH_RISK` means "manual verification strongly recommended," not "fake."

### Claim-Citation Support Triage (v3.1.0)

Extract the sentence surrounding each `\cite{}` command from `.tex` files and pair it with cited bibliography metadata and V3.0 hallucination risk data. Produce deterministic triage labels that help identify claim-citation pairs that may lack credible structural support — without LLM.

```bash
python 20-check-claim-citation/check_claim_citation.py \
  --project-root thesis \
  --ruleset university-generic
```

Triage labels:

| Label | Meaning |
|---|---|
| `WELL_SUPPORTED` | Cited reference PASS in V3.0, complete metadata, substantive context |
| `SUPPORTED` | Reference PASS/WARN in V3.0, minor risk signals |
| `WEAK` | Reference REVIEW in V3.0, or vague context, or incomplete metadata |
| `ORPHANED` | Citation key not found in bibliography files |
| `UNVERIFIABLE` | Cited reference UNSUPPORTED in V3.0 (CJK, thesis type) |

The report also includes a backward-compatible support-review layer: `claim_type`, `support_review_label`, `support_review_reason`, `support_signals`, `risk_signals`, `cluster_keys`, `cluster_risk_summary`, and `next_actions`. These fields explain why a pair or grouped citation cluster deserves manual review; they do not replace the original `triage_label` or make final truth claims. Local lexical evidence can use title, abstract, and keyword token overlap when those `.bib` fields are present. Conservative risk signals such as `possible_topic_mismatch`, `possible_outdated_support`, and `possible_overclaim` are advisory prompts for human review, not automatic judgments. The JSON/Markdown reports may also include advisory `citation_needed_candidates` for uncited high-assertion sentences; these are manual review prompts, not blocking findings.

V3.1 boundaries:

- No LLM usage. Scoring is deterministic based on V3.0 risk labels, metadata, context quality, grouping, and citation frequency.
- No semantic similarity between claim text and reference content.
- No automatic citation rewrite or suggestion.
- Reads `reports/hallucination-risk-report.json` if present; treats missing it conservatively.
- Exit code 1 when any pair is `ORPHANED`.

### Final Cleanup Checker

Before final PDF or submission handoff, scan LaTeX sources for process residue such as `TODO`, `FIXME`, `???`, `\textcolor{blue}`, `\color{blue}`, `draft`, `debug`, and Chinese review notes like `待修改` or `待核查`.

```bash
python 23-check-final-cleanup/check_final_cleanup.py \
  --project-root thesis \
  --ruleset university-generic
```

Output: `reports/final-cleanup-report.json`. This checker is report-only: it does not delete markers, rewrite prose, or change source files. The final-audit workflow can aggregate this JSON into `reports/final-audit-report.json` and render it through `reports/final-audit-report.html` and the local report index.

### Statistical Consistency Checker

Before final submission, scan for mixed statistical notation such as `p值/P值`, `p=/P=`, `95%CI/95\%CI/95%置信区间`, `Bootstrap/自助法`, and `SMD/标准化均数差`.

```bash
python 25-check-statistical-consistency/check_statistical_consistency.py \
  --project-root thesis \
  --ruleset university-generic
```

Output: `reports/statistical-consistency-report.json`. The checker reports the dominant style in the current project and flags deviations; it does not force a universal notation preference or rewrite source files.

### Manual Anchor Checker

If the project uses manual contents entries, scan for `\addcontentsline` commands that may be missing a nearby preceding `\phantomsection` anchor.

```bash
python 26-check-manual-anchor/check_manual_anchor.py \
  --project-root thesis \
  --ruleset university-generic
```

Output: `reports/manual-anchor-report.json`. The checker reports likely TOC / LOF / LOT hyperlink-jump risks, but it does not repair labels, captions, numbering, figures, tables, or references.

### Final Audit Report

After generating the source-of-truth JSON reports, aggregate them into a single final-audit handoff artifact:

```bash
python 27-final-audit-report/build_final_audit_report.py \
  --project-root thesis \
  --ruleset university-generic
```

Output: `reports/final-audit-report.json`. This report imports existing JSON evidence and groups dimensions, blockers, warnings, next actions, and source links. It does not rerun checks, call external services, modify thesis sources, or replace the raw JSON reports.

### Reference Audit Ledger

For spreadsheet review and advisor/service handoff, aggregate existing reference evidence into one CSV ledger:

```bash
python 28-reference-audit-ledger/build_reference_audit_ledger.py \
  --project-root thesis \
  --ruleset university-generic
```

Output: `reports/reference-audit-ledger.csv`. The ledger preserves source-specific statuses from local citation integrity, final reference set, external verification, DOI candidates, URL verification, and hallucination-risk reports. It does not edit `.bib`, insert DOI values, replace URLs, call external services, or treat `NO_CANDIDATE` as fake.

### Static Report Index

Generate a local HTML landing page for the reports directory:

```bash
python 29-report-index/build_report_index.py \
  --project-root thesis
```

Output: `reports/index.html`. This page links available JSON / CSV artifacts and shows present / missing / unreadable counts. It is a local reading surface only; JSON and CSV remain the source of truth.

### Final Audit HTML

Generate a readable local detail page for the aggregated final-audit JSON:

```bash
python 30-final-audit-html/build_final_audit_html.py \
  --project-root thesis
```

Output: `reports/final-audit-report.html`. This static page is generated from `final-audit-report.json` and shows the overall verdict, KPI row, dimension matrix, issues, next actions, and source links. JSON remains authoritative.

### Reference Audit Ledger HTML

Generate a readable local detail page for the reference-audit CSV ledger:

```bash
python 31-reference-ledger-html/build_reference_audit_ledger_html.py \
  --project-root thesis
```

Output: `reports/reference-audit-ledger.html`. This static page is generated from `reference-audit-ledger.csv` and shows summary stats, scope slices, citation-key groupings, and the full ledger table. CSV remains authoritative.

### Claim-Citation HTML

Generate a readable local detail page for claim-citation support review:

```bash
python 32-claim-citation-html/build_claim_citation_html.py \
  --project-root thesis
```

Output: `reports/claim-citation-triage.html`. This static page is generated from `claim-citation-triage-report.json` and shows triage groups, citation-needed candidates, uncited references, cluster review details, support/risk signals, and next actions. JSON remains authoritative.

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

### 6. I want to screen AI-generated or suspicious references

```bash
python 18-verify-references/verify_external_references.py \
  --project-root thesis \
  --ruleset university-generic

python 19-check-hallucination-risk/check_hallucination_risk.py \
  --project-root thesis \
  --ruleset university-generic
```

Use this when you want a fast authenticity screen for references drafted by AI or copied from sources you do not fully trust. It produces a `hallucination_risk_score` per entry and a `high-risk-references.csv` for manual review, without rewriting the bibliography. Chinese-language references are marked `UNSUPPORTED` since external databases do not cover them.

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

**Step 7: Export a handoff bundle**

After the pack passes lint, export a minimal versioned export bundle for handoff:

```bash
python 90-rules/export_pack.py \
  --pack-path 90-rules/packs/my-university \
  --output dist/my-university.zip
```

This creates a linted ZIP bundle for sharing the pack outside a local checkout. The ZIP includes `manifest.json` with pack metadata and the lint scorecard summary. There is still no formal registry or publish command.

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

- `v3.4.1`: polished cross-report HTML navigation and calibrated duplicate support-risk signals.
- `v3.4.0`: added final-audit report surfaces, reference-audit ledger HTML, and conservative claim-citation support-risk signals.
- `v3.3.0`: hardened reference verification with final reference set parsing, resumeable external verification, DOI candidate suggestions, and URL verification.
- `v3.2.0`: integrated hallucination risk and claim-citation triage into readiness gate, added unified evidence pipeline runner, `run_evidence_pipeline.py`.
- `v3.1.0`: added claim-citation support triage, `claim-citation-triage-report.json`, deterministic triage scoring, and three demo projects.
- `v3.0.0`: added hallucination risk scoring, `hallucination-risk-report.json`, `high-risk-references.csv`, Chinese-language `UNSUPPORTED` handling, and three demo projects.
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
