# THESIS_LATEX_TO_WORD

This workflow owns the bounded export boundary from a LaTeX thesis project into a Word-friendly `.docx` output.

Use it to:

- generate a review-friendly export target
- inspect likely unsupported or degraded constructs before export
- preserve explicit export mode and output contract boundaries

Recommended sequence:

1. Run `run_check_once.py` first.
2. Review compile, format, content, and language reports.
3. Generate a report-first `02-latex-to-word` summary.
4. Use review-friendly export as the first-class supported export target.

Current boundary:

- review-friendly export is the primary supported mode
- submission-friendly export is a future-facing contract, not the main first-release guarantee
- not every LaTeX construct will round-trip perfectly
- unsupported or degraded constructs should be surfaced explicitly in reports

## What review-friendly mode is for

- **Advisors and committee members** who prefer reading in Word with track-changes
- **Collaborative editing** where co-authors do not use LaTeX
- **Journal submission portals** that require `.docx` upload for initial review
- **Plagiarism-check systems** that parse Word better than raw LaTeX

## What is expected to degrade

| LaTeX Feature | Review-Friendly Behavior |
|:---|:---|
| TikZ figures | Omitted from export; listed as unsupported |
| Custom macros (`\newcommand`) | Expanded if simple; warned if complex |
| Math environments (`align`, `gather`) | Converted to Word equation fields; layout may shift |
| Bibliography / citations | Raw `[1]` style or basic author-year; no guaranteed CSL match |
| Cross-references (`\ref`, `\cite`) | May become static text |
| Float placement (`\begin{figure}[htbp]`) | Ignored; images inline |
| Custom title page logic | Simplified or omitted |

## Why the report matters

The export report (`reports/latex_to_word-report.json`) is the **source of truth** for what happened during conversion. Always inspect it before sharing the `.docx` with reviewers.

The report includes:

- discovered source files
- warnings for constructs that may degrade
- unsupported constructs that were skipped
- conversion errors (if any)

## Why submission-friendly is not yet the main guarantee

Submission-friendly export would require:

- university-specific `.docx` template mapping
- strict heading style compliance
- figure/table caption style matching
- bibliography CSL profile accuracy
- page margin and font enforcement

These are **future-facing constraints** and are **not** part of the current v1.0 first-class export promise.

## Migration helper

```bash
# Dry-run: generate report only
python 02-latex-to-word/migrate_project.py \
  --project-root <latex-project> \
  --output-file <review.docx> \
  --profile review-friendly \
  --apply false

# Export: create the .docx (requires pandoc)
python 02-latex-to-word/migrate_project.py \
  --project-root <latex-project> \
  --output-file <review.docx> \
  --profile review-friendly \
  --apply true
```
