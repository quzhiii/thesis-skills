# Runner

The repository exposes two top-level runners:

- `run_check_once.py` - run all deterministic checks and write `reports/run-summary.json`
- `run_fix_cycle.py` - read existing reports and run safe fixers

Recommended beginner flow:

1. Run `python run_check_once.py --project-root <project> --ruleset <ruleset> --skip-compile`
2. Review JSON reports in `<project>/reports/`
3. Run `python run_fix_cycle.py --project-root <project> --ruleset <ruleset> --apply false`
4. If results look safe, rerun with `--apply true`
