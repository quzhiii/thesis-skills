# THESIS_LANGUAGE

## Purpose
Provide deterministic language-format checks for Chinese academic thesis writing.

## Scope
- Quote style consistency in Chinese context.
- CJK punctuation sanity checks.
- CJK-Latin spacing checks.
- Optional weak-phrase warning list.

## Quickstart
1. Run checker:
   - `python scripts/skills/04-language/check_language.py --rules tsinghua`
2. Review report:
   - `scripts/skills/04-language/check_language-report.json`
3. Fix `error` first, then decide on `warning` items.

## Rule Highlights
- Mixed Chinese and straight quotes in same paragraph -> warning/error per rules.
- Missing space between Chinese and English tokens -> warning.
- Repeated punctuation anomalies (`。。`, `，，`) -> error.

## Inputs And Outputs
- Input:
  - `data/chap*.tex`
  - optional `data/abstract.tex`
- Output:
  - JSON report with summary/findings

## Troubleshooting
- False positives in formulas/code snippets:
  - add exclusion pattern for math environments
- Excessive spacing warnings:
  - verify tokenizer is skipping commands and braces correctly
- No findings with obviously bad text:
  - confirm files are within scan glob and encoding is UTF-8

## Verification
- `python scripts/skills/04-language/check_language.py --help`
- `python scripts/skills/04-language/check_language.py --rules tsinghua`

## Related Guides
- `scripts/skills/THESIS_SKILLS_GUIDE.zh-CN.md`
- `scripts/skills/THESIS_SKILLS_GUIDE.en.md`
