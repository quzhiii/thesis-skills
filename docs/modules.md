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
   · Final reference set               17-final-reference-set/
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

6. External verification (alpha)
    · CrossRef / OpenAlex lookup        18-verify-references/

6.5 Hallucination risk (v3.0)
    · Deterministic risk scoring        19-check-hallucination-risk/

6.6 Claim-citation support triage (v3.1)
    · Deterministic triage scoring      20-check-claim-citation/

6.7 Final-audit foundations
    · Process residue scanning          23-check-final-cleanup/
    · Statistical notation consistency  25-check-statistical-consistency/
    · Manual contents anchor checks     26-check-manual-anchor/
    · JSON handoff aggregation          27-final-audit-report/
    · Reference audit ledger            28-reference-audit-ledger/
    · Static HTML report index          29-report-index/
    · Final audit HTML detail           30-final-audit-html/
    · Reference ledger HTML detail      31-reference-ledger-html/
    · Claim-citation HTML detail        32-claim-citation-html/

7. Defense preparation
    · Outline, figure inventory, notes  17-defense-pack/

8. Institutional adaptation
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
| Check | `10-check-references/` | `check_references.py` | Validate local citation integrity: cited keys, BibTeX fields, duplicate keys, and local log citation warnings |
| Check | `11-check-language/` | `check_language.py` | Run deterministic language checks, including CJK/Latin spacing |
| Check | `12-check-format/` | `check_format.py` | Check figure/table blocks, labels, references, and front matter |
| Check | `13-check-content/` | `check_content.py` | Check abstract metadata and content structure |
| Check | `14-check-language-deep/` | `check_language_deep.py` | Flag higher-order language and consistency review items |
| Check | `15-check-compile/` | `check_compile.py` | Parse existing LaTeX compile logs into structured diagnostics |
| Gate | `16-check-readiness/` | `check_readiness.py` | Aggregate reports into `PASS / WARN / BLOCK` readiness artifact |
| Check | `17-final-reference-set/` | `build_final_reference_set.py` | Parse `.aux` / `.bbl` or TeX fallback and write `final-reference-set-report.json` plus `final-reference-set-report.csv` |
| Verify (alpha) | `18-verify-references/` | `verify_external_references.py` | Query CrossRef / OpenAlex / Semantic Scholar for selected bibliography entries; write `external-verification-report.json`, `missing-doi-candidates.json`, and `url-verification-report.json` |
| Risk (v3.0) | `19-check-hallucination-risk/` | `check_hallucination_risk.py` | Score bibliography entries for hallucination risk; write `hallucination-risk-report.json` and `high-risk-references.csv` |
| Triage (v3.1+) | `20-check-claim-citation/` | `check_claim_citation.py` | Extract citation contexts and triage claim-citation pairs by structural support, local metadata-overlap, grouped-cluster, and citation-needed advisory signals; write `claim-citation-triage-report.json`, `claim-citation-triage.md`, and `claim-citation-triage.csv` with support-review enrichment fields |
| Final audit | `23-check-final-cleanup/` | `check_final_cleanup.py` | Scan final LaTeX source for process residue such as `TODO`, `FIXME`, `???`, blue text markers, `draft`, and `debug`; write `final-cleanup-report.json` without modifying source files |
| Final audit | `25-check-statistical-consistency/` | `check_statistical_consistency.py` | Report mixed statistical notation families such as `p值/P值`, `p=/P=`, confidence interval notation, Bootstrap terms, and SMD terms; write `statistical-consistency-report.json` without rewriting source files |
| Final audit | `26-check-manual-anchor/` | `check_manual_anchor.py` | Report manual `\addcontentsline` entries that may lack a nearby preceding `\phantomsection`; write `manual-anchor-report.json` without repairing anchors or numbering |
| Final audit | `27-final-audit-report/` | `build_final_audit_report.py` | Aggregate existing final-audit, readiness, citation, and reference evidence into `final-audit-report.json` without rerunning checks or rewriting source files |
| Final audit | `28-reference-audit-ledger/` | `build_reference_audit_ledger.py` | Aggregate existing reference evidence into `reference-audit-ledger.csv` with one spreadsheet-friendly row per source-specific reference status |
| Report UX | `29-report-index/` | `build_report_index.py` | Generate static local `reports/index.html` linking JSON / CSV source-of-truth artifacts without replacing them |
| Report UX | `30-final-audit-html/` | `build_final_audit_html.py` | Generate static local `reports/final-audit-report.html` from `final-audit-report.json` with verdict, KPI, dimension matrix, issues, and source links |
| Report UX | `31-reference-ledger-html/` | `build_reference_audit_ledger_html.py` | Generate static local `reports/reference-audit-ledger.html` from `reference-audit-ledger.csv` with summary stats, scope views, key-grouped slices, and full-table browsing |
| Report UX | `32-claim-citation-html/` | `build_claim_citation_html.py` | Generate static local `reports/claim-citation-triage.html` from `claim-citation-triage-report.json` with P0 / P1 / P2 / P3 review groups, issue-card summaries, citation-needed candidates, uncited references, cluster review, and deep links to readiness / references / claim-citation / final-audit while preserving JSON / CSV source artifacts |
| Defense | `17-defense-pack/` | `generate_outline.py` | Generate thesis outline for defense preparation |
| Defense | `17-defense-pack/` | `generate_figure_inventory.py` | Inventory figures and visual evidence |
| Defense | `17-defense-pack/` | `generate_talk_prep_notes.py` | Generate editable talk-prep notes |
| Fix | `20-fix-references/` | `fix_references.py` | Preview and apply reference-related patches |
| Fix | `21-fix-language-style/` | `fix_language_style.py` | Preview and apply deterministic language style patches |
| Fix | `22-fix-format-structure/` | `fix_format_structure.py` | Preview and apply format-structure patches |
| Fix | `23-fix-final-cleanup/` | `fix_final_cleanup.py` | Preview and apply safe final cleanup marker removals |
| Fix | `25-fix-statistical-consistency/` | `fix_statistical_consistency.py` | Preview and apply safe statistical notation normalization |
| Fix | `24-fix-language-deep/` | `fix_language_deep.py` | Preview deeper language patch candidates |
| Rules | `90-rules/` | `create_pack.py` | Create institution- or journal-specific rule packs |
| Rules | `90-rules/` | `lint_pack.py` | Validate rule-pack structure and write scorecard summaries |
| Rules | `90-rules/` | `export_pack.py` | Export linted rule-pack handoff bundles |
| Runner | repository root | `run_check_once.py` | Run the deterministic check pipeline once |
| Runner | repository root | `run_evidence_pipeline.py` | Orchestrate final reference set plus all citation evidence layers in sequence |
| Runner | repository root | `run_fix_cycle.py` | Preview or apply report-driven fix cycles |

## How to choose a module

- Start with `run_check_once.py` if you only want to know the current state of a project.
- Start with `00-bib-zotero/` or `00-bib-endnote/` if citation metadata is unstable.
- Start with `02-latex-to-word/` when the advisor review format is Word but the source of truth is LaTeX.
- Start with `16-check-readiness/` after reports exist and you need a one-page handoff verdict.
- Start with `19-check-hallucination-risk/` when you want a fast screen for AI-drafted or suspicious references.
- Start with `23-check-final-cleanup/` before final PDF/submission handoff when you want to catch process residue without auto-editing the thesis.
- Start with `25-check-statistical-consistency/` when you need final-stage statistical notation consistency evidence.
- Start with `26-check-manual-anchor/` when manual TOC / LOF / LOT entries may affect PDF hyperlink jump targets.
- Start with `27-final-audit-report/` after source-of-truth JSON reports exist and you need a single final-audit handoff artifact.
- Start with `28-reference-audit-ledger/` when you need a spreadsheet handoff across local citation integrity, final reference set, external verification, DOI, URL, and hallucination-risk evidence.
- Start with `29-report-index/` when you want a local static HTML landing page for generated JSON / CSV artifacts.
- Start with `30-final-audit-html/` when you want a readable local detail page for the aggregated final-audit JSON.
- Start with `31-reference-ledger-html/` when you want a readable local HTML surface for the aggregated reference-audit CSV ledger.
- Start with `32-claim-citation-html/` when you want a readable local HTML surface for claim-citation support review groups, issue-card summaries, and citation-needed candidates without changing JSON / CSV source artifacts.
