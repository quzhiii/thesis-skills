# Release Checklist

This checklist is for publishing the six-skills package as a reusable GitHub project.

## P0 (Must Before Public Release)

- [x] Staging copy exists and is isolated from source project
- [x] One-command runner exists (`run_check_once.py`)
- [x] Runner works with `--rules tsinghua` and `--skip-compile`
- [x] Non-Tsinghua starter ruleset exists (`06-rules/rules/my-university/`)
- [x] Runtime artifacts ignored (`.gitignore`)
- [x] Add top-level `LICENSE`
- [x] Add `SECURITY.md`
- [x] Add `CONTRIBUTING.md`
- [x] Add `THIRD_PARTY_NOTICES.md`
- [x] Add CI workflow to run one-command checks on sample project

## P1 (Should in v0.2)

- [ ] Add `07-literature-review` skill (workflow + report contract)
- [ ] Add `08-reviewer-audit` skill (rubric + revision suggestions)
- [ ] Add machine-readable consolidated result file (`run-summary.json`)
- [ ] Add sample issue templates for checker false positives

## P2 (Nice to Have)

- [ ] Add latex diff helper for advisor review loops
- [ ] Add compile log parser for friendlier error hints
- [ ] Add optional slide-deck export guidance for thesis defense

## Acceptance Gate for v0.1

Release only if all checks below pass:

1. `python run_check_once.py --project-root "../thuthesis-v7.6.0" --rules tsinghua --skip-compile`
2. `python run_check_once.py --project-root "../thuthesis-v7.6.0" --rules my-university --skip-compile`
3. `python run_check_once.py --project-root "../thuthesis-v7.6.0" --rules tsinghua`

Current status:

- [x] 1
- [x] 2
- [x] 3
