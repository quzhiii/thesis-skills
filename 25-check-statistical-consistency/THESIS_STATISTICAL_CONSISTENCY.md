# Statistical Consistency Checker

## Module

`25-check-statistical-consistency/check_statistical_consistency.py`

## Purpose

Scan final thesis LaTeX sources for mixed statistical notation. The checker reports the dominant style for each notation family and flags deviations. It does not force a global preference and does not rewrite source files.

## Usage

```bash
python 25-check-statistical-consistency/check_statistical_consistency.py \
  --project-root thesis \
  --ruleset university-generic
```

## Output

- `reports/statistical-consistency-report.json`

## First-Wave Families

- `p值` / `P值`
- `p=` / `P=`
- `q值` / `Q值`
- `95%CI` / `95\%CI` / `95% 置信区间` / `95%置信区间` / `95\%置信区间`
- `Bootstrap` / `自助法` / `自助抽样`
- `SMD` / `标准化均数差`

## Exit Codes

- `0`: no mixed notation family found
- `1`: at least one notation family mixes styles

## Boundaries

- No automatic statistical notation rewrite.
- No preference hard-coded as globally correct.
- Reports deviations from the dominant style in the current project.
- Intended as a final-audit foundation that can later be aggregated into `reports/final-audit-report.json` and rendered in static HTML report surfaces.
