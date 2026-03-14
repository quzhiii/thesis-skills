# THESIS_ENDNOTE

## Purpose
Export a clean, standards-compliant `.bib` file from **EndNote** so that `refs-import.bib`
contains valid BibLaTeX entry types, complete metadata, and the `langid` field required by
GB7714-2015 / ThuThesis — before `01-migrate` or any other pipeline step sees the bibliography.

After completing this skill, run `00-zotero/check_bib_quality.py` for final validation.

---

## When To Use This Skill

| Situation | Action |
|---|---|
| Word document uses EndNote field codes (active) | ✅ Use this skill first |
| EndNote desktop library available | ✅ Use this skill first |
| Zotero is your reference manager | ➡️ Use `00-zotero/THESIS_ZOTERO.md` instead |
| Only plain-text bibliography remains | ⚠️ Skip to `01-migrate` fallback path |

---

## Step 1: Export BibTeX from EndNote

1. In **EndNote** desktop, select your reference group or the full library.
2. Go to **File → Export…**:
   - Output style: choose **BibTeX Export** (install from
     `https://endnote.com/style_download/bibtex-export/` if not available)
   - File type: **Text File (*.txt)** — rename to `.bib` after saving
3. Alternatively: **Edit → Output Styles → Open Style Manager** → search "BibTeX".
4. Save output as `ref/refs-raw-endnote.bib` (keep a copy before modification).

> **Traveling Library users (Word plugin):** In Word, go to **EndNote X → Export to EndNote** 
> to push cited references from the Traveling Library back to an EndNote desktop library first.

---

## Step 2: Normalize Non-Standard Entry Types (Required)

EndNote's BibTeX exporter generates non-standard entry types that BibLaTeX and `biber` do not
recognise. You must convert these before the file enters the pipeline.

### Entry Type Mapping

| EndNote exports | BibLaTeX standard | Notes |
|---|---|---|
| `@Electronic` | `@online` | Web pages, online resources |
| `@Conference` | `@inproceedings` | Conference papers |
| `@Newspaper` | `@article` | Add `journaltitle` = newspaper name |
| `@Patent` | `@misc` | Add `type = {Patent}` |
| `@Report` | `@techreport` | Government / industry reports |
| `@Thesis` | `@phdthesis` / `@mastersthesis` | Specify by degree type |
| `@Webpage` | `@online` | Alias for `@Electronic` |
| `@Generic` | `@misc` | Catch-all fallback |

### Recommended: Use JabRef to Normalise

[JabRef](https://www.jabref.org/) is a free BibTeX manager that can fix entry types in bulk:

1. Install JabRef (free, cross-platform): `https://www.jabref.org/`
2. Open `ref/refs-raw-endnote.bib` in JabRef.
3. Select all entries with non-standard types → right-click → **Change entry type** → select
   the correct BibLaTeX type from the table above.
4. For `@Electronic` entries: JabRef may offer auto-convert — use **Quality → Resolve duplicate
   BibTeX keys** and **Quality → Find unlinked files** to clean up.
5. Export → **Save as** → `ref/refs-import.bib` (BibLaTeX format).

### Manual Find-and-Replace (Minimal)

If JabRef is not available, do a plain-text find-and-replace in your editor:

```
@Electronic{  →  @online{
@Conference{  →  @inproceedings{
@Newspaper{   →  @article{
@Patent{      →  @misc{
@Report{      →  @techreport{
@Webpage{     →  @online{
@Generic{     →  @misc{
```

---

## Step 3: Fix Common Field Name Differences

EndNote and BibLaTeX use different field names in several cases:

| EndNote field | BibLaTeX field | Action |
|---|---|---|
| `address` | `location` | Rename (BibLaTeX uses `location`) |
| `journal` | `journaltitle` | Rename for `biblatex` (not needed for `bibtex`) |
| `keyword` | `keywords` | Rename to plural form |
| `abstract` (very long) | — | Trim or delete to keep file readable |
| `notes` | `note` | Usually harmless; rename for consistency |

> **ThuThesis / gb7714-2015 style note:** The `gb7714-2015` style for biblatex accepts both
> `journal` and `journaltitle`. However, using `journaltitle` consistently avoids style warnings.

---

## Step 4: Add `langid` (Required for GB7714-2015)

Neither Zotero nor EndNote adds `langid` automatically. Every entry **must** have:

```bibtex
langid = {chinese}   % for Chinese-language sources
langid = {english}   % for English-language sources
```

**Bulk approach in JabRef:**
1. Filter entries by language (e.g. author names contain CJK characters).
2. Select all → **Edit → Manage field names** → Add `langid = chinese`.
3. Repeat for English entries.

**Manual rule of thumb:** If `author`, `title`, or `journal` contains Chinese characters, the
entry needs `langid = {chinese}`.

---

## Step 5: Set Consistent Cite Keys

EndNote's auto-generated cite keys are often inconsistent (`Author2024` with collision suffixes).
Recommended key pattern: `[author][year][keyword]`, e.g. `zhang2020mgmt`.

Bulk rename in JabRef: **Quality → Autogenerate BibTeX keys** → set pattern
`[auth][year][veryshorttitle]`.

---

## Step 6: Run Quality Check

After saving `ref/refs-import.bib`, run the stdlib-only checker:

```bash
python 00-zotero/check_bib_quality.py \
  --bib ref/refs-import.bib \
  --main thuthesis-example.tex \
  --report 00-endnote/check_bib_quality-report.json
```

The checker will flag:
- Remaining non-standard entry types (e.g. `@Electronic` that was missed)
- Missing `langid` fields
- Incomplete required fields
- Malformed DOIs
- Cite-key mismatches between `.bib` and `.tex`

Fix all **errors** before proceeding. **Warnings** (mainly `langid`) must also be resolved for
ThuThesis GB7714-2015 compliance.

---

## Step 7: Integrate With 01-migrate

After this skill:
- `ref/refs-import.bib` contains standard BibLaTeX entries with valid cite keys.
- **Skip** `scripts/generate_sanitized_refs_import.py` in `01-migrate` (it would overwrite
  your clean export). Pass `--skip-generate-bib` if the script supports it.

Updated `01-migrate` flow:
```
Phase 0  →  00-endnote (this skill): export + normalise .bib from EndNote
Phase 0b →  00-zotero/check_bib_quality.py: validate .bib quality
Phase 1  →  01-migrate step 1: migrate_from_word_tex.py
Phase 2  →  01-migrate step 2: normalize_citations.py
            (skip generate_sanitized_refs_import.py)
Phase 3  →  03-references: check citation integrity
Phase 4  →  further checkers as normal
```

---

## Required `.bib` Field Standards (GB7714-2015 / ThuThesis)

| Entry type | Required fields |
|---|---|
| `article` | author, title, journaltitle (or journal), year |
| `book` | author, title, publisher, year |
| `inproceedings` | author, title, booktitle, year |
| `online` | author (or editor), title, url, urldate |
| `all types` | **`langid`** (`chinese` or `english`) |

---

## Example: Correctly Formatted EndNote-Origin Entry

```bibtex
@article{wang2021supply,
  author       = {王明 and 陈静},
  title        = {供应链韧性研究综述},
  journaltitle = {管理科学},
  year         = {2021},
  volume       = {34},
  number       = {2},
  pages        = {1--15},
  langid       = {chinese},
}
```

---

## Exit Codes From `check_bib_quality.py`

| Code | Meaning |
|---|---|
| `0` | All entries pass — clean bibliography |
| `1` | Quality findings (non-standard types, missing `langid`, required fields, DOI issues) |
| `2` | Config or file-not-found error |
| `3` | Runtime failure |
