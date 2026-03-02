# Contributing

Thanks for your interest in improving Thesis 6 Skills.

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
python run_check_once.py --project-root "examples/minimal-project" --rules tsinghua --skip-compile
python run_check_once.py --project-root "examples/minimal-project" --rules my-university --skip-compile
```

## Pull Request Checklist

- [ ] README updates if behavior changes
- [ ] No generated runtime artifacts committed (`*-report.json`, `__pycache__`)
- [ ] Rule changes include rationale
- [ ] Validation commands pass
