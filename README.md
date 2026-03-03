# Thesis LaTeX Skills

![Python](https://img.shields.io/badge/python-3.x-blue?logo=python&logoColor=white)
![License](https://img.shields.io/github/license/quzhiii/thesis-skills)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20linux%20%7C%20macos-lightgrey)
![No dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)

> **Word → LaTeX migration, done right.**
> A deterministic AI skill pipeline for LaTeX academic writing QA — citation integrity, CJK style, format validation, and Zotero bib hygiene. Works for theses and journal submissions alike. No hallucinations. No rewrites. Precise error reports only.

[中文版说明](README.zh-CN.md)

---

## The Problem

Getting thesis formatting right is a real prerequisite for graduation. Word is approachable, but keeping formatting consistent across a full thesis — citation styles, cross-references, punctuation rules, figure numbering — is tedious and error-prone. LaTeX handles academic typesetting more robustly and produces cleaner, publication-quality output, but the learning curve is steep, especially when migrating an existing draft from Word.

When you make that switch, problems pile up silently: broken citation keys, orphaned cross-references, mixed CJK/Latin punctuation, missing figure labels, bib entries that fail GB7714-2015 validation. They don't throw errors. They surface all at once on submission day.

**Thesis LaTeX Skills** catches them before your advisor does — whether you're mid-migration from Word or already writing natively in LaTeX.

Built first for **Tsinghua University** (`thuthesis`). Extensible to any university thesis template or journal LaTeX submission template.

---

## What It Does (and What It Doesn't)

| ✅ Does | ❌ Does Not |
|---|---|
| Cross-validates `\cite{key}` against `.bib` files | Generate or rewrite your arguments |
| Detects orphan bibliography entries | Change your research methods or conclusions |
| Checks CJK punctuation & quote style consistency | Automatically edit chapter prose |
| Validates figure/table labels and `\ref` integrity | Rewrite chapter content by default |
| Scans and deduplicates symbols & abbreviations | Replace your advisor's review |
| Checks chapter structure completeness | Make judgment calls on content quality |
| Enforces school-specific format rules via YAML rulesets | Handle non-LaTeX (Word) submissions |

---

## Skill Modules

```
thesis-latex-skills/
├── 00-zotero/      # Zotero/EndNote → .bib export & quality check (run before 01-migrate)
├── 01-migrate/     # Word → LaTeX migration workflow
├── 02-content/     # Structure, abstract, and symbol/acronym checks
├── 03-references/  # Citation integrity and bibliography hygiene
├── 04-language/    # CJK punctuation and quote style checks
├── 05-format/      # Figure, table, equation, cross-reference validation
└── 06-rules/       # Pluggable YAML rulesets (Tsinghua built-in, custom extensible)
```

### `00-zotero` — Zotero/EndNote `.bib` Export & Quality Check

If you inserted references in Word using **Zotero** (or EndNote), run this skill **before** `01-migrate`. It validates the `.bib` file exported from your reference manager before it enters the rest of the pipeline. Catches missing `langid` fields (required by GB7714-2015 / ThuThesis), incomplete required fields, malformed DOIs, and cite-key mismatches between the `.bib` and your `.tex` files.

**Inputs:** `ref/refs-import.bib` (exported from Zotero Better BibLaTeX)
**Report:** `00-zotero/check_bib_quality-report.json`

### `01-migrate` — Word → LaTeX Migration

Converts Word-exported LaTeX (`from_word_full.tex`) into a clean `thuthesis`-compatible chapter structure. Normalizes citation markers into `\cite{...}` format and regenerates the sanitized bibliography import. Preserves all legacy migration scripts — this skill orchestrates them, not replaces them.

**Key outputs:** `data/chap02.tex` … `data/chap06.tex`, `ref/refs-import.bib`

### `02-content` — Content Structure & Symbol Scan

Checks that your thesis has the required chapter flow (problem → method → result → discussion → conclusion), that your abstract contains all four required elements (objective, method, result, conclusion) in both Chinese and English, and that keyword count is within limits. Also scans all chapters for symbol/abbreviation candidates, deduplicates them, flags conflicts, and optionally patches `denotation.tex`.

**Two modes:** `--mode report` (safe, read-only) → `--mode patch` (optional write)

### `03-references` — Citation Integrity

Deterministic cross-validation between your `\cite{key}` calls and your `.bib` files. Catches:
- **Missing keys** (error) — cited in text but absent from bib
- **Orphan entries** (warning) — in bib but never cited
- **Duplicate title candidates** (warning) — possible double entries
- **Non-monotonic citation order** (info) — numeric style violations

### `04-language` — CJK Language Style

Checks Chinese academic writing conventions that are easy to overlook:
- Mixed Chinese curly-quotes and straight-quotes in the same paragraph
- Missing space between CJK and Latin tokens
- Repeated punctuation anomalies (`。。`, `，，`)
- Configurable weak-phrase detection ("众所周知", "不难看出", etc.)

### `05-format` — Structure & Cross-Reference Integrity

Validates the mechanical structure of your LaTeX source:
- Every `\figure` and `\table` environment has `\caption` and `\label`
- All `\ref{key}` calls have a matching `\label{key}` somewhere
- Longtable continuation markers are complete (`\endfirsthead`, `\endhead`, `\endfoot`, `\endlastfoot`)
- List of figures and list of tables are present in main tex
- Integrates with the existing `thesis_quality_loop.ps1` compile loop

### `06-rules` — Pluggable Rulesets

All checkers read their rules from YAML files under `06-rules/rules/<ruleset>/`. The built-in `tsinghua` ruleset encodes Tsinghua graduate thesis requirements. Adding a new university requires filling four YAML files: `format.yaml`, `citation.yaml`, `structure.yaml`, `language.yaml`.

---

## Architecture & Technical Stack

```
┌─────────────────────────────────────────────────────┐
│                  AI Coding Assistant                │
│         (Claude / OpenCode / Cursor / etc.)         │
└────────────────────┬────────────────────────────────┘
                     │  invokes skill modules
┌────────────────────▼────────────────────────────────┐
│              run_check_once.py  (orchestrator)      │
│    ┌──────────────────────────────────────────┐     │
│    │  00-zotero (bib pre-check)               │     │
│    ├──────────────────────────────────────────┤     │
│    │  03-references  │  04-language  │  05-format │  │
│    │  02-content     │  (optional compile loop)  │  │
│    └──────────────────────────────────────────┘     │
│                        │                            │
│                 reads ruleset from                  │
│         06-rules/rules/<ruleset>/*.yaml             │
└────────────────────┬────────────────────────────────┘
                     │
         ┌───────────▼───────────┐
         │  Your LaTeX project   │
         │  (thuthesis or other) │
         └───────────────────────┘
```

**Stack:**
- Python 3.x checkers (no external dependencies beyond stdlib)
- YAML-driven ruleset configuration
- PowerShell compile loop (`thesis_quality_loop.ps1`) — optional, Windows
- JSON structured reports from each checker
- Exit code contract: `0` pass · `1` quality findings · `2` config error · `3` runtime failure

**Skill format:** Compatible with OpenCode / Claude skill system — each module ships a `THESIS_*.md` skill prompt alongside its Python checker.

---

## Quick Start

### For Tsinghua users (`thuthesis`)

```bash
# Run all checks at once (from this repository root)
python run_check_once.py --project-root "../thuthesis-v7.6.0" --rules tsinghua
```

This runs, in order:
1. `00-zotero/check_bib_quality.py` — bibliography export quality (Zotero/langid/DOI)
2. `03-references/check_references.py` — citation audit
3. `04-language/check_language.py` — language style
4. `05-format/check_structure.py` — structural integrity
5. `02-content/scan_symbols.py --mode report` — symbol scan
6. Compile loop (`thesis_quality_loop.ps1`) — unless `--skip-compile`

Skip compile (faster, for iterative checks):
```bash
python run_check_once.py --project-root "../thuthesis-v7.6.0" --rules tsinghua --skip-compile
```

### For other universities

1. Copy the template ruleset:
   ```
   06-rules/rules/custom/template/  →  06-rules/rules/my-university/
   ```
2. Fill in your school's requirements in all four YAML files.
3. Run:
   ```bash
   python run_check_once.py --project-root "../your-thesis-project" --rules my-university --skip-compile
   ```

A working starter example is included at `06-rules/rules/my-university/`.

---

## Roadmap

| Version | Status | What's included |
|---|---|---|
| **v0.1** | ✅ Released | 7 skill modules (incl. Zotero bib checker), Tsinghua ruleset, one-command runner |
| **v0.2** | 🔜 Planned | `07-literature-review` skill, `08-reviewer-audit` skill, consolidated `run-summary.json` |
| **Future** | 💡 Backlog | LaTeX diff helper for advisor review, compile log parser, defense slide export guidance |

---

## Who Is This For

- **Tsinghua graduates** writing with `thuthesis` — drop-in, zero config
- **Other university students** with an existing LaTeX template — fill four YAML files, done
- **Advisors and TAs** who want a reproducible quality gate before accepting chapter drafts
- **Anyone** who wants deterministic, non-AI-hallucinated checks on their LaTeX thesis

---

## Acknowledgements

Built on top of the excellent [`thuthesis`](https://github.com/tuna/thuthesis) template maintained by TUNA.

---

## License

See [LICENSE](LICENSE). Third-party notices in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
