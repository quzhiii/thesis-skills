# Release Checklist

This checklist is for publishing `thesis-skills` as a reusable public GitHub repository.

## P0 (Must Before Public Release)

- [x] Runner exists (`run_check_once.py`, `run_fix_cycle.py`)
- [x] Runtime artifacts ignored (`.gitignore`)
- [x] Top-level `LICENSE`
- [x] `SECURITY.md`
- [x] `CONTRIBUTING.md`
- [x] `THIRD_PARTY_NOTICES.md`
- [x] Bilingual README refresh
- [x] CI workflow present

## P1 (Included in v0.3.0 and v0.4.0)

- [x] Machine-readable consolidated result file (`run-summary.json`)
- [x] Regression tests for migration, rules, runner, and Zotero mapping
- [x] Report-driven fixers split by concern
- [x] Zotero Word citation sync workflow
- [x] Packaging metadata (`pyproject.toml`) and dependency declaration
- [x] Public roadmap document

### v0.4.0 Additions

- [x] EndNote XML/RIS/BibTeX import workflow
- [x] Canonical reference model (`citation_models.py`)
- [x] Reference normalization (`canonicalize.py`)
- [x] EndNote parsers (`endnote_xml.py`, `endnote_ris.py`)
- [x] BibTeX rendering (`bib_render.py`)
- [x] Duplicate detection (`match_refs.py`)
- [x] Preflight checker (`check_endnote_export.py`)
- [x] 45 tests passing (14 Zotero + 31 EndNote)

## P2 (Next Releases)

- [ ] Latex diff helper for advisor review loops
- [ ] Compile log parser for friendlier error hints
- [ ] Slide-deck export guidance for thesis defense
- [ ] Stronger EndNote structured intake contract

## Acceptance Gate for v0.4.0

Release only if all checks below pass:

1. `python -m pytest tests/ -v`
2. `python run_check_once.py --project-root examples/minimal-latex-project --ruleset university-generic --skip-compile`
3. `python run_fix_cycle.py --project-root examples/minimal-latex-project --ruleset university-generic --apply false`

Current status:

- [x] 1
- [x] 2
- [x] 3
