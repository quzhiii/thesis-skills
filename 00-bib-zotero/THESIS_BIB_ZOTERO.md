# THESIS_BIB_ZOTERO

Use this workflow before Word-to-LaTeX migration when bibliography data comes from Zotero.

Run:

```bash
python 00-bib-zotero/check_bib_quality.py --project-root <latex-project> --ruleset <ruleset>
```

Purpose:

- check missing `langid`
- check unsupported entry types
- catch malformed DOI values
