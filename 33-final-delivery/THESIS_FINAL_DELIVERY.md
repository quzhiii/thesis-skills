# THESIS_FINAL_DELIVERY

Run the final delivery workflow: evidence generation, final-audit checks, optional bounded fixes, and bundle rebuild.

```bash
python 33-final-delivery/run_final_delivery.py --project-root <latex-project> --ruleset university-generic
```

Options:

- `--skip-evidence`: Skip citation evidence pipeline (faster for local iteration)
- `--fix-preview`: Run bounded auto-fix preview before bundle rebuild
- `--fix-apply`: Apply bounded auto-fixes before bundle rebuild

Workflow steps:

1. Citation evidence pipeline (unless `--skip-evidence`)
2. Final-audit foundation checks (final cleanup, statistical consistency, manual anchor)
3. Optional bounded auto-fix preview/apply
4. Bundle rebuild:
   - `reports/final-audit-report.json`
   - `reports/reference-audit-ledger.csv`
   - `reports/index.html`
   - `reports/final-audit-report.html`
   - `reports/reference-audit-ledger.html`
   - `reports/claim-citation-triage.html` (when source JSON exists)

Output: JSON summary to stdout with step results.
