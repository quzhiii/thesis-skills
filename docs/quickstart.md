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
- `check_references-report.json` — citation key integrity
- `check_language-report.json` — deterministic language checks
- `check_format-report.json` — labels, references, figures, tables, structure
- `check_content-report.json` — abstract and content metadata checks

## 4. Run on your own project

```bash
python run_check_once.py \
  --project-root path/to/your/thesis \
  --ruleset university-generic \
  --skip-compile
```

Use `--skip-compile` for a first smoke test. Remove it when you have a LaTeX toolchain and want compile-log diagnostics included in the readiness gate.

## 5. What to inspect first

Open `reports/readiness-report.json` and look at:

- `overall_verdict`
- `blockers`
- `warnings`
- `next_actions`

Then open the checker report referenced by the first blocker or warning.
