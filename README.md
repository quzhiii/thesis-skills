# Thesis 6 Skills (Staging Copy)

[中文 README](README.zh-CN.md)

This directory is a staging workspace for optimizing and publishing six thesis-writing skills.

## Included Skills

- `01-migrate`
- `02-content`
- `03-references`
- `04-language`
- `05-format`
- `06-rules`

## Current Scope

- Primary target: Tsinghua LaTeX thesis workflows
- Secondary target: other schools that already have LaTeX templates
- Current boundary: non-Tsinghua schools require filling a custom ruleset template under `06-rules/rules/custom/template/`

## Content Boundary

- These six skills do not generate thesis arguments, methods, or conclusions.
- They focus on migration, references, language style checks, structural format checks, and ruleset-driven validation.
- They may read existing thesis files (for checks), but they do not auto-rewrite chapter content by default.

## Quick Start (Check Once)

From this folder:

```bash
python run_check_once.py --project-root "../thuthesis-v7.6.0" --rules tsinghua
```

What it runs:

1. `03-references/check_references.py`
2. `04-language/check_language.py`
3. `05-format/check_structure.py`
4. `02-content/scan_symbols.py --mode report`
5. compile loop (`scripts/thesis_quality_loop.ps1`) unless `--skip-compile`

## Exit Behavior

- Returns non-zero if any step fails.
- Keeps checker JSON reports in each skill folder.

## Notes

- This is a staging copy for optimization. It does not replace the original thesis project files.
- For non-Tsinghua use, create a new ruleset folder and complete all four yaml files:
  - `format.yaml`
  - `citation.yaml`
  - `structure.yaml`
  - `language.yaml`

## Example Non-Tsinghua Ruleset

Starter example is included at:

- `06-rules/rules/my-university/`

Quick validation:

```bash
python run_check_once.py --project-root "../thuthesis-v7.6.0" --rules my-university --skip-compile
```

## Release Tracking

Use `RELEASE_CHECKLIST.md` to track publish readiness (P0/P1/P2).

## Acknowledgements

- Special thanks to the `thuthesis` project for the excellent thesis template foundation:
  - https://github.com/tuna/thuthesis
