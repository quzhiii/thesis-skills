# Thesis Skills module reference

This page keeps the long module map out of the README while preserving a single place to look up entrypoints.

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

## Entrypoint table

| Stage | Module | Entrypoint | Output / role |
|---|---|---|---|
| Bibliography | `00-bib-zotero/` | `sync_from_word.py` | Extract Zotero citations from Word and create stable mapping artifacts |
| Bibliography | `00-bib-zotero/` | `check_bib_quality.py` | Check BibTeX quality: missing fields, DOI shape, language metadata |
| Bibliography | `00-bib-endnote/` | `check_endnote_export.py` | Preflight exported EndNote XML/RIS/BibTeX files |
| Bibliography | `00-bib-endnote/` | `import_library.py` | Normalize EndNote exports into stable `refNNN` IDs |
| Migration | `01-word-to-latex/` | `migrate_project.py` | Map Word-exported content into a LaTeX project structure |
| Migration | `02-latex-to-word/` | `migrate_project.py` | Generate review-friendly `.docx` and report degraded elements |
| Review | `03-latex-review-diff/` | `review_diff.py` | Generate review diff, triage, and TODO artifacts |
| Review | `04-word-review-ingest/` | `feedback_ingest.py` | Normalize Word feedback into structured issues |
| Check | `10-check-references/` | `check_references.py` | Validate `\cite{}` keys against bibliography files |
| Check | `11-check-language/` | `check_language.py` | Run deterministic language checks, including CJK/Latin spacing |
| Check | `12-check-format/` | `check_format.py` | Check figure/table blocks, labels, references, and front matter |
| Check | `13-check-content/` | `check_content.py` | Check abstract metadata and content structure |
| Check | `14-check-language-deep/` | `check_language_deep.py` | Flag higher-order language and consistency review items |
| Check | `15-check-compile/` | `check_compile.py` | Parse existing LaTeX compile logs into structured diagnostics |
| Gate | `16-check-readiness/` | `check_readiness.py` | Aggregate reports into `PASS / WARN / BLOCK` readiness artifact |
| Defense | `17-defense-pack/` | `generate_outline.py` | Generate thesis outline for defense preparation |
| Defense | `17-defense-pack/` | `generate_figure_inventory.py` | Inventory figures and visual evidence |
| Defense | `17-defense-pack/` | `generate_talk_prep_notes.py` | Generate editable talk-prep notes |
| Fix | `20-fix-references/` | `fix_references.py` | Preview and apply reference-related patches |
| Fix | `21-fix-language-style/` | `fix_language_style.py` | Preview and apply deterministic language style patches |
| Fix | `22-fix-format-structure/` | `fix_format_structure.py` | Preview and apply format-structure patches |
| Fix | `24-fix-language-deep/` | `fix_language_deep.py` | Preview deeper language patch candidates |
| Rules | `90-rules/` | `create_pack.py` | Create institution- or journal-specific rule packs |
| Rules | `90-rules/` | `lint_pack.py` | Validate rule-pack structure |
| Rules | `90-rules/` | `scorecard.py` | Summarize rule-pack completeness |
| Runner | repository root | `run_check_once.py` | Run the deterministic check pipeline once |
| Runner | repository root | `run_fix_cycle.py` | Preview or apply report-driven fix cycles |

## How to choose a module

- Start with `run_check_once.py` if you only want to know the current state of a project.
- Start with `00-bib-zotero/` or `00-bib-endnote/` if citation metadata is unstable.
- Start with `02-latex-to-word/` when the advisor review format is Word but the source of truth is LaTeX.
- Start with `16-check-readiness/` after reports exist and you need a one-page handoff verdict.
