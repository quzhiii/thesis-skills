# Quickstart

This guide runs the sample project without requiring a LaTeX installation.

## Requirements

- Python 3.10+
- Windows, macOS, or Linux
- LaTeX is optional for this demo because it uses `--skip-compile`

## 1. Clone and enter the repository

```bash
git clone https://github.com/quzhiii/thesis-skills.git
cd thesis-skills
```

## 2. Confirm the demo project exists

```bash
test -d examples/minimal-latex-project
```

On Windows PowerShell, use:

```powershell
Test-Path examples/minimal-latex-project -PathType Container
```

## 3. Run the check pipeline

```bash
python run_check_once.py \
  --project-root examples/minimal-latex-project \
  --ruleset university-generic \
  --skip-compile
```

The command writes reports under:

```text
examples/minimal-latex-project/reports/
```

Important files:

- `run-summary.json` — step-by-step checker results
- `readiness-report.json` — aggregate `PASS / WARN / BLOCK` readiness gate
- `check_bib_quality-report.json` — bibliography-field and duplicate-entry precheck
- `check_references-report.json` — compatibility reference checker report
- `citation-integrity-report.json` — machine-readable Citation Integrity status
- `citation-integrity-report.md` — human-readable citation risk summary
- `citation-issues.csv` — spreadsheet-friendly list of BLOCK/WARN citation issues
- `check_language-report.json` — deterministic language checks
- `check_language_deep-report.json` — manual-first deeper language screening
- `check_format-report.json` — labels, references, figures, tables, structure
- `check_content-report.json` — abstract and content metadata checks

Optional final-audit foundation:

- `final-cleanup-report.json` — process-residue scan from `23-check-final-cleanup/check_final_cleanup.py`
- `statistical-consistency-report.json` — mixed statistical notation scan from `25-check-statistical-consistency/check_statistical_consistency.py`
- `manual-anchor-report.json` — manual `\addcontentsline` / `\phantomsection` scan from `26-check-manual-anchor/check_manual_anchor.py`
- `final-audit-report.json` — aggregate handoff report from `27-final-audit-report/build_final_audit_report.py`
- `reference-audit-ledger.csv` — spreadsheet reference handoff from `28-reference-audit-ledger/build_reference_audit_ledger.py`
- `index.html` — static local report index from `29-report-index/build_report_index.py`
- `final-audit-report.html` — static final-audit reading surface from `30-final-audit-html/build_final_audit_html.py`
- `reference-audit-ledger.html` — static reference-ledger reading surface from `31-reference-ledger-html/build_reference_audit_ledger_html.py`

## 4. Run on your own project

```bash
python run_check_once.py \
  --project-root path/to/your/thesis \
  --ruleset university-generic \
  --skip-compile
```

Use `--skip-compile` for a first smoke test. Remove it when you have a LaTeX toolchain and want compile-log diagnostics included in the readiness gate.

Before a final PDF or submission handoff, run the cleanup scan explicitly:

```bash
python 23-check-final-cleanup/check_final_cleanup.py \
  --project-root path/to/your/thesis \
  --ruleset university-generic

python 25-check-statistical-consistency/check_statistical_consistency.py \
  --project-root path/to/your/thesis \
  --ruleset university-generic

python 26-check-manual-anchor/check_manual_anchor.py \
  --project-root path/to/your/thesis \
  --ruleset university-generic

python 27-final-audit-report/build_final_audit_report.py \
  --project-root path/to/your/thesis \
  --ruleset university-generic

python 28-reference-audit-ledger/build_reference_audit_ledger.py \
  --project-root path/to/your/thesis \
  --ruleset university-generic

python 29-report-index/build_report_index.py \
  --project-root path/to/your/thesis

python 30-final-audit-html/build_final_audit_html.py \
  --project-root path/to/your/thesis

python 31-reference-ledger-html/build_reference_audit_ledger_html.py \
  --project-root path/to/your/thesis
```

## 5. What to inspect first

Open `reports/readiness-report.json` and look at:

- `overall_verdict`
- `blockers`
- `warnings`
- `next_actions`

Then open the checker report referenced by the first blocker or warning.
