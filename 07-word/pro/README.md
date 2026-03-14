# THU Formatter Pro (Word + Python Rule Engine)

Pro decouples decision-making from Word execution.

- Python side: parse/lint/plan (auditable JSON artifacts)
- Word macro side: execute whitelisted actions only

## Outputs
- `report.json`
- `fix_plan.json`
- `*_fixed.docx`
- `*_fixed.pdf`
- `fix_log.txt`

## Quickstart (skeleton)
```bash
python -m thu_word_lint.cli lint --doc thesis.docx --rules rules/thu_v1.yaml --out report.json
python -m thu_word_lint.cli plan --report report.json --out fix_plan.json
```

## One-pass runner
```bash
python run_word_check_once.py --doc "C:/path/to/thesis.docx"
```

Artifacts are written to `out/report.json` and `out/fix_plan.json` by default.

Then load `fix_plan.json` in Word executor macro and run action application.
