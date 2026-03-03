# THESIS_ZOTERO

## Purpose
Export a clean `.bib` from Zotero or EndNote **before** running the `01-migrate` Word→LaTeX
conversion, so that `refs-import.bib` contains real cite keys and complete metadata instead of
reconstructed plain-text placeholders.

Run the bundled `check_bib_quality.py` after export to catch missing `langid`, incomplete fields,
and DOI format issues before the rest of the pipeline sees the bibliography.

---

## When To Use This Skill

| Situation | Action |
|---|---|
| Zotero field codes still active in Word | ✅ Use this skill first |
| Original Zotero library available | ✅ Use this skill first |
| Only plain-text bibliography remains | ⚠️ Skip to `01-migrate` fallback path |
| Word document fields already stripped | ⚠️ Try online extractor (see below) |

---

## Path A: Zotero Export (Recommended)

1. Install **Better BibTeX** for Zotero:
   `https://retorque.re/zotero-better-bibtex/`

2. In Zotero → Preferences → Better BibTeX, set a citation key formula, for example:
   ```
   [auth][year][veryshorttitle]
   ```

3. Select your collection → right-click → **Export Collection**:
   - Format: **Better BibLaTeX**
   - ☑ Keep updated (auto-sync on library changes)

4. Save as `ref/references.bib` under your thesis project root.

5. Copy or rename to `ref/refs-import.bib` so `01-migrate` picks it up automatically:
   ```
   copy ref\references.bib ref\refs-import.bib
   ```

---

## Path B: EndNote Export

1. In Word (with EndNote plugin), use EndNote **Traveling Library** to export cited items back to
   an EndNote desktop library.
2. In EndNote, export to BibTeX (or RIS, then convert with JabRef or Zotero).
3. Save as `ref/refs-import.bib`.

*Note: EndNote metadata quality depends on original library fields. Chinese entries must still
have `langid = {chinese}` added manually if missing.*

---

## ThuThesis Setup Verification

Confirm `thusetup.tex` references the correct bib file:

```latex
\thusetup{
  bibliography = {ref/refs-import}
}
```

For standalone `biblatex` projects (non-ThuThesis):

```latex
\usepackage[backend=biber, style=gb7714-2015]{biblatex}
\addbibresource{ref/refs-import.bib}
```

---

## Required `.bib` Field Standards (GB7714-2015 / ThuThesis)

| Entry type | Required fields |
|---|---|
| `article` | author, title, journal, year |
| `book` | author, title, publisher, year |
| `inproceedings` | author, title, booktitle, year |
| `all types` | **`langid`** (`chinese` or `english`) |

Example of a correctly formatted Chinese entry:

```bibtex
@article{zhang2020mgmt,
  author   = {张三 and 李四},
  title    = {管理学研究的新进展},
  journal  = {管理世界},
  year     = {2020},
  volume   = {36},
  pages    = {1--20},
  langid   = {chinese},
}
```

---

## Quality Check After Export

Run the stdlib-only checker (no installation required):

```bash
python 00-zotero/check_bib_quality.py
```

Or specify paths explicitly:

```bash
python 00-zotero/check_bib_quality.py \
  --bib ref/refs-import.bib \
  --main thuthesis-example.tex \
  --report 00-zotero/check_bib_quality-report.json
```

If `biber` is installed, also run structural validation:

```bash
biber --tool --validate-datamodel ref/refs-import.bib
```

---

## Integration With 01-migrate

After completing this skill:

- `ref/refs-import.bib` is populated with **real cite keys** and full metadata.
- `scripts/normalize_citations.py` in `01-migrate` will match `\cite{key}` against these actual
  keys — much more reliable than the reconstructed placeholder approach.
- **Skip** `scripts/generate_sanitized_refs_import.py` in `01-migrate` to avoid overwriting the
  clean Zotero export. Comment it out or pass `--skip-generate-bib` if the script supports it.

Updated `01-migrate` flow when this skill is used:

```
Phase 0  →  00-zotero (this skill): export .bib from Zotero
Phase 1  →  01-migrate step 1: migrate_from_word_tex.py
Phase 2  →  01-migrate step 2: normalize_citations.py
            (skip generate_sanitized_refs_import.py)
Phase 3  →  03-references: check citation integrity
Phase 4  →  further checkers as normal
```

---

## Word-Only Recovery (No Zotero Access)

If Zotero fields are already stripped from Word:

1. Try the online field extractor: `https://rintze.zelle.me/ref-extractor/`
   - Upload your `.docx` → Export BibTeX.
2. If only plain-text references remain, use the `01-migrate` default path via
   `word-model/references.txt` → `generate_sanitized_refs_import.py`.

---

## Exit Codes From `check_bib_quality.py`

| Code | Meaning |
|---|---|
| `0` | All entries pass — clean bibliography |
| `1` | Quality findings (missing `langid`, required fields, DOI format issues) |
| `2` | Config or file-not-found error |
| `3` | Runtime failure |
