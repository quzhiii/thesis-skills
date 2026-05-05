# THESIS_CHECK_REFERENCES

Run the deterministic reference checker and local Citation Integrity Engine.

```bash
python 10-check-references/check_references.py --project-root <latex-project> --ruleset <ruleset>
```

It validates local citation integrity against bibliography files declared by the pack:

- cited keys missing from `.bib` files
- unused bibliography entries
- duplicate keys and conflicting duplicate metadata
- required BibTeX fields, DOI shape, and year shape
- local LaTeX log undefined-citation warnings when available through the Citation Integrity layer

Outputs:

- compatibility report: `reports/check_references-report.json`
- rich Citation Integrity report: `reports/citation-integrity-report.json`

V1.1 boundary: this module is local-first. It does not call external metadata APIs, does not use an LLM, does not detect hallucinated references yet, and does not automatically rewrite thesis citations.
