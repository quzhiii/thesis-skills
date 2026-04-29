# Examples

## Minimal LaTeX project

The repository includes a runnable demo at:

```text
examples/minimal-latex-project/
```

Run it with:

```bash
python run_check_once.py \
  --project-root examples/minimal-latex-project \
  --ruleset university-generic \
  --skip-compile
```

## Readiness gate preview

```json
{
  "mode": "advisor-handoff",
  "overall_verdict": "WARN",
  "summary": {
    "headline": "Readiness verdict: WARN",
    "evidence_status": "partial",
    "dimension_count": 7,
    "missing_evidence_count": 3
  },
  "next_actions": [
    "Generate or locate missing evidence for compile.",
    "Generate or locate missing evidence for export.",
    "Generate or locate missing evidence for review_debt."
  ]
}
```

`WARN` is normal for this smoke test because compile evidence is intentionally skipped and export/review-loop evidence is not produced by `run_check_once.py`. For final submission, rerun without `--skip-compile` after compiling your thesis, and generate the Word export or review-loop artifacts when those handoffs are part of your workflow.

## Deterministic check finding

```json
{
  "status": "FAIL",
  "severity": "warning",
  "code": "LANG_CJK_LATIN_SPACING",
  "message": "Possible missing spacing between CJK and Latin tokens",
  "file": "chapters/introduction.tex",
  "line": 42,
  "suggestion": "Add a space between Chinese and English tokens where appropriate"
}
```

## Scenario: advisor wants Word

```bash
python 02-latex-to-word/migrate_project.py \
  --project-root thesis \
  --output-file thesis-review.docx \
  --profile review-friendly \
  --apply true
```

Inspect `reports/latex_to_word-report.json` after export. It records conversion caveats so the Word handoff is explicit instead of silently lossy.

## Scenario: pre-submission smoke test

```bash
python run_check_once.py \
  --project-root thesis \
  --ruleset university-generic \
  --skip-compile
```

Use this when you want fast feedback before setting up the full TeX toolchain. The reports are still useful for references, language, format, and content checks.
