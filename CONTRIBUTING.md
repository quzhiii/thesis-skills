# Contributing

Thanks for your interest in improving Thesis Skills.

## Development Rules

- Keep behavior deterministic.
- Do not add hardcoded school-specific logic outside rulesets.
- Keep checker exit code contract stable:
  - `0` pass
  - `1` quality findings (errors)
  - `2` input/config error
  - `3` runtime failure

## Local Validation Before PR

Run from repository root:

```bash
python run_check_once.py --project-root "examples/minimal-latex-project" --ruleset university-generic --skip-compile
python 90-rules/lint_pack.py --pack-path 90-rules/packs/university-generic
python -m unittest discover -s tests -p "test_*.py"
```

## Pull Request Checklist

- [ ] README updates if behavior changes
- [ ] No generated runtime artifacts committed (`*-report.json`, `__pycache__`)
- [ ] Rule changes include rationale
- [ ] Validation commands pass
