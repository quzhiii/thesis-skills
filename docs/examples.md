# Examples

## Minimal LaTeX project

The repository includes a runnable demo at:

```text
examples/minimal-latex-project/
```

Run it with:

```bash
python run_check_once.py \
  --project-root examples/minimal-latex-project \
  --ruleset university-generic \
  --skip-compile
```

## Citation Integrity demos

The repository includes two focused reference-check demos:

```text
examples/citation-integrity-broken/
examples/citation-integrity-clean/
```

### Broken demo

```bash
python 10-check-references/check_references.py \
  --project-root examples/citation-integrity-broken \
  --ruleset university-generic
```

Expected outputs:

- `reports/check_references-report.json` for pipeline compatibility
- `reports/citation-integrity-report.json` for machine-readable status
- `reports/citation-integrity-report.md` for human review
- `reports/citation-issues.csv` for spreadsheet-style triage

This demo should end in `BLOCK` and populate the CSV with concrete citation risks.

### Clean demo

```bash
python 10-check-references/check_references.py \
  --project-root examples/citation-integrity-clean \
  --ruleset university-generic
```

Expected outputs:

- `reports/check_references-report.json`
- `reports/citation-integrity-report.json`
- `reports/citation-integrity-report.md`
- `reports/citation-issues.csv`

This demo should end in `PASS`. The CSV is still written, but on a clean run it only contains the header row.

Boundary: Citation Integrity is still local-only and report-first. It does not verify references against external databases and does not auto-edit citations or bibliography entries.

## External verification demo

The external verification runner adds a separate evidence layer on top of the local Citation Integrity checks:

```bash
python 18-verify-references/verify_external_references.py \
  --project-root examples/citation-integrity-broken \
  --ruleset university-generic
```

Expected outputs:

- `reports/external-verification-report.json`
- `reports/.external-cache/`

This report combines CrossRef / OpenAlex / Semantic Scholar candidates and surfaces them as the `external_verification` readiness advisory dimension. It keeps the local readiness verdict unchanged and does not rewrite citations or bibliography entries.

Run the same command against `examples/citation-integrity-clean/` to see the clean case with the same external verification envelope and fewer review items.

### Final reference set, DOI candidates, and URL verification (v3.3.0)

When `.aux` and `.bbl` files are present, Thesis Skills can determine the final reference set that actually entered the compiled bibliography:

```bash
python 17-final-reference-set/build_final_reference_set.py \
  --project-root examples/citation-integrity-broken \
  --ruleset university-generic
```

Expected outputs:

- `reports/final-reference-set-report.json`
- `reports/final-reference-set-report.csv`

Then run external verification in `final` scope:

```bash
python 18-verify-references/verify_external_references.py \
  --project-root examples/citation-integrity-broken \
  --ruleset university-generic \
  --scope final \
  --resume
```

Additional advisory outputs:

- `reports/missing-doi-candidates.json`
- `reports/missing-doi-candidates.csv`
- `reports/url-verification-report.json`
- `reports/url-verification-flagged.csv`

These reports never rewrite `.bib` files. DOI candidates are suggestions only, and URL verification checks reachability, not document authenticity.

## Hallucination risk demos

The hallucination risk scorer adds a V3.0 evidence layer on top of the V2.0 external verification:

```text
examples/citation-hallucination-field-mismatch/
examples/citation-hallucination-fabricated/
examples/citation-hallucination-chinese-unsupported/
```

### Field mismatch demo

```bash
python 19-check-hallucination-risk/check_hallucination_risk.py \
  --project-root examples/citation-hallucination-field-mismatch \
  --ruleset university-generic
```

Expected outputs:

- `reports/hallucination-risk-report.json`
- `reports/high-risk-references.csv`

This demo produces `REVIEW` entries where the external metadata partially matches but fields differ.

### Fabricated demo

```bash
python 19-check-hallucination-risk/check_hallucination_risk.py \
  --project-root examples/citation-hallucination-fabricated \
  --ruleset university-generic
```

Expected outputs:

- `reports/hallucination-risk-report.json` with `HIGH_RISK` status
- `reports/high-risk-references.csv`

This demo exits with code `1` because at least one entry has no credible external match.

### Chinese unsupported demo

```bash
python 19-check-hallucination-risk/check_hallucination_risk.py \
  --project-root examples/citation-hallucination-chinese-unsupported \
  --ruleset university-generic
```

Expected outputs:

- `reports/hallucination-risk-report.json` with `UNSUPPORTED` entries
- `reports/high-risk-references.csv`

Chinese-language references are marked `UNSUPPORTED` because external databases do not cover them. This is not a failure; it means the reference needs manual verification.

Boundary: the hallucination risk scorer does not use LLMs and never auto-rewrites citations or bibliography entries. It reads `reports/external-verification-report.json` if present; otherwise it scores from local metadata only.

## Claim-citation support triage demos (v3.1.0)

The claim-citation triage runner adds a V3.1 evidence layer on top of the V3.0 hallucination risk scoring:

```text
examples/claim-citation-mixed/
examples/claim-citation-orphaned/
examples/claim-citation-chinese/
```

### Mixed demo

```bash
python 20-check-claim-citation/check_claim_citation.py \
  --project-root examples/claim-citation-mixed \
  --ruleset university-generic
```

Expected outputs:

- `reports/claim-citation-triage-report.json`
- `reports/claim-citation-triage.md`
- `reports/claim-citation-triage.csv`

This demo produces all five triage labels (`WELL_SUPPORTED`, `SUPPORTED`, `WEAK`, `ORPHANED`, `UNVERIFIABLE`) and exits with code 1 because at least one pair is `ORPHANED`.

The JSON report also includes support-review enrichment fields such as `claim_type`, `support_review_label`, `support_review_reason`, `support_signals`, `risk_signals`, `cluster_keys`, `cluster_risk_summary`, and `next_actions`. These fields are advisory explanations for manual review; the original `triage_label` remains backward-compatible. When available, `.bib` title, abstract, and keywords are used as weak local lexical evidence through token-overlap fields. Reports may also include `citation_needed_candidates` for uncited high-assertion sentences; these candidates do not change the CLI exit code.

### Orphaned demo

```bash
python 20-check-claim-citation/check_claim_citation.py \
  --project-root examples/claim-citation-orphaned \
  --ruleset university-generic
```

This demo has citation keys with no corresponding bib entries. It produces `ORPHANED` triage entries and exits with code 1.

### Chinese reference demo

```bash
python 20-check-claim-citation/check_claim_citation.py \
  --project-root examples/claim-citation-chinese \
  --ruleset university-generic
```

All references in this demo are Chinese-language and marked `UNSUPPORTED` by V3.0. The triage labels them all as `UNVERIFIABLE`. The exit code is 0 because `UNVERIFIABLE` is not a blocking signal.

Boundary: the claim-citation triage runner does not use LLMs, does not judge semantic similarity between claims and references, and never auto-rewrites citations.

## Final cleanup checker

The final cleanup checker is the first final-audit foundation. It scans final LaTeX sources for process residue such as `TODO`, `FIXME`, `待修改`, `待核查`, `见截图`, `这里再改`, `临时`, `占位`, `???`, `\textcolor{blue}`, `\color{blue}`, `draft`, and `debug`.

```bash
python 23-check-final-cleanup/check_final_cleanup.py \
  --project-root examples/minimal-latex-project \
  --ruleset university-generic
```

Expected output:

- `reports/final-cleanup-report.json`

Boundary: this checker is deterministic and report-only. It does not delete markers, rewrite prose, or change source files. The JSON report is intended to become the `final_cleanup` section of a future `reports/final-audit-report.json` and can be rendered later as static HTML issue cards grouped by risk level.

## Statistical consistency checker

The statistical consistency checker reports mixed notation families and suggests reviewing deviations from the dominant style in the current project.

```bash
python 25-check-statistical-consistency/check_statistical_consistency.py \
  --project-root examples/minimal-latex-project \
  --ruleset university-generic
```

Expected output:

- `reports/statistical-consistency-report.json`

Boundary: this checker does not decide that one notation is universally correct. It reports mixed styles such as `p值/P值`, `p=/P=`, `95%CI/95\%CI/95%置信区间`, `Bootstrap/自助法`, and `SMD/标准化均数差` so a human can normalize final wording if needed.

## Manual anchor checker

The manual anchor checker reports manual contents entries that may be missing a nearby preceding `\phantomsection`, which can make TOC / LOF / LOT links jump to the previous section, figure, or table.

```bash
python 26-check-manual-anchor/check_manual_anchor.py \
  --project-root examples/minimal-latex-project \
  --ruleset university-generic
```

Expected output:

- `reports/manual-anchor-report.json`

Boundary: this checker does not repair labels, captions, numbering, tables, figures, or `\ref{}` usage. It only reports likely hyperlink-anchor risks for manual verification.

## Final audit report

After generating source-of-truth JSON evidence, build a single final-audit handoff artifact:

```bash
python 27-final-audit-report/build_final_audit_report.py \
  --project-root examples/minimal-latex-project \
  --ruleset university-generic
```

Expected output:

- `reports/final-audit-report.json`

This report aggregates available JSON evidence, including final cleanup, statistical consistency, manual anchor checks, readiness, citation integrity, final reference set, external verification, DOI candidates, URL verification, hallucination risk, and claim-citation support. It does not rerun checkers, call external services, modify sources, or replace the raw JSON reports.

## Reference audit ledger

Build a spreadsheet-friendly ledger from existing reference evidence:

```bash
python 28-reference-audit-ledger/build_reference_audit_ledger.py \
  --project-root examples/citation-integrity-broken \
  --ruleset university-generic
```

Expected output:

- `reports/reference-audit-ledger.csv`

Ledger columns:

```text
key,title,authors,year,venue,doi,scope,source_checked,status,issue,action_suggested
```

Boundary: this ledger aggregates existing evidence only. It does not rerun reference checks, call external services, edit `.bib`, insert DOI values, replace URLs, or label externally not-found references as fake.

## Static report index

Generate a local HTML landing page for available report artifacts:

```bash
python 29-report-index/build_report_index.py \
  --project-root examples/minimal-latex-project
```

Expected output:

- `reports/index.html`

Boundary: the HTML index is a reading surface only. JSON / CSV remain the source of truth. It links known artifacts, shows present / missing / unreadable counts, and avoids a frontend framework or hosted backend.

## Final audit HTML

Generate a local detail page for the aggregated final-audit JSON:

```bash
python 30-final-audit-html/build_final_audit_html.py \
  --project-root examples/minimal-latex-project
```

Expected output:

- `reports/final-audit-report.html`

Boundary: this page is generated from `final-audit-report.json` and remains a reading surface only. It does not replace the JSON, rerun checks, or modify thesis sources.

## Reference audit ledger HTML

Generate a local detail page for the spreadsheet-friendly reference ledger:

```bash
python 31-reference-ledger-html/build_reference_audit_ledger_html.py \
  --project-root examples/citation-integrity-broken
```

Expected output:

- `reports/reference-audit-ledger.html`

Boundary: this page is generated from `reference-audit-ledger.csv` and remains a reading surface only. It does not replace the CSV, rerun checks, call external services, or modify bibliography or thesis source files.

## Claim-citation HTML

Generate a local detail page for claim-citation support review:

```bash
python 32-claim-citation-html/build_claim_citation_html.py \
  --project-root examples/claim-citation-mixed
```

Expected output:

- `reports/claim-citation-triage.html`

Boundary: this page is generated from `claim-citation-triage-report.json` and remains a reading surface only. It does not replace the JSON / Markdown / CSV artifacts, rerun claim-citation checks, or modify thesis source files.

## Unified Evidence Pipeline (v3.3.0)

Run final reference set plus all four citation evidence layers in a single command:

```bash
python run_evidence_pipeline.py \
  --project-root examples/claim-citation-mixed \
  --ruleset university-generic \
  --skip-external
```

Expected outputs:
- `reports/check_references-report.json`
- `reports/final-reference-set-report.json`
- `reports/hallucination-risk-report.json`
- `reports/claim-citation-triage-report.json`
- `reports/claim-citation-triage.md`
- `reports/claim-citation-triage.csv`

After the pipeline completes, run the readiness gate to see all evidence dimensions:

```bash
python 16-check-readiness/check_readiness.py \
  --project-root examples/claim-citation-mixed \
  --ruleset university-generic
```

The `readiness-report.json` now includes `hallucination_risk` and `claim_citation` dimensions alongside `external_verification`, giving a complete citation health profile in a single artifact.

## Readiness gate preview

```json
{
  "mode": "advisor-handoff",
  "overall_verdict": "WARN",
  "summary": {
    "headline": "Readiness verdict: WARN",
    "evidence_status": "partial",
    "dimension_count": 7,
    "missing_evidence_count": 3
  },
  "next_actions": [
    "Generate or locate missing evidence for compile.",
    "Generate or locate missing evidence for export.",
    "Generate or locate missing evidence for review_debt."
  ]
}
```

`WARN` is normal for this smoke test because compile evidence is intentionally skipped and export/review-loop evidence is not produced by `run_check_once.py`. For final submission, rerun without `--skip-compile` after compiling your thesis, and generate the Word export or review-loop artifacts when those handoffs are part of your workflow.

## Deterministic check finding

```json
{
  "status": "FAIL",
  "severity": "warning",
  "code": "LANG_CJK_LATIN_SPACING",
  "message": "Possible missing spacing between CJK and Latin tokens",
  "file": "chapters/introduction.tex",
  "line": 42,
  "suggestion": "Add a space between Chinese and English tokens where appropriate"
}
```

## Scenario: advisor wants Word

```bash
python 02-latex-to-word/migrate_project.py \
  --project-root thesis \
  --output-file thesis-review.docx \
  --profile review-friendly \
  --apply true
```

Inspect `reports/latex_to_word-report.json` after export. It records conversion caveats so the Word handoff is explicit instead of silently lossy.

## Scenario: pre-submission smoke test

```bash
python run_check_once.py \
  --project-root thesis \
  --ruleset university-generic \
  --skip-compile
```

Use this when you want fast feedback before setting up the full TeX toolchain. The reports are still useful for references, language, format, and content checks.
