# THESIS_BIB_ZOTERO

Use this workflow for Zotero-based bibliography management in thesis projects.

## Overview

This module provides two main workflows:

1. **BibTeX Quality Check** - Validate exported bibliography
2. **Word→LaTeX Sync** - Extract Zotero citations from Word and sync to LaTeX

## BibTeX Quality Check

Run before Word-to-LaTeX migration when bibliography data comes from Zotero.

```bash
python 00-bib-zotero/check_bib_quality.py --project-root <latex-project> --ruleset <ruleset>
```

Checks:
- Missing `langid` field
- Unsupported entry types
- Malformed DOI values

## Word→LaTeX Citation Sync (NEW in v1.2.0)

Extract Zotero citations embedded in Word docx files and sync with LaTeX project.

### Usage

```bash
# Dry-run (preview changes)
python 00-bib-zotero/sync_from_word.py --project-root <latex-project> --word-file <word.docx>

# Apply changes
python 00-bib-zotero/sync_from_word.py --project-root <latex-project> --word-file <word.docx> --apply
```

### What it does

1. **Extract Zotero citations** from Word docx (CSL_CITATION JSON in document.xml)
2. **Load existing mapping** from `ref/citation-mapping.json`
3. **Compare and detect**:
   - New citations (in Word but not in mapping)
   - Removed citations (in mapping but not in Word)
4. **Update mapping** with new LaTeX keys (ref001, ref002, ...)
5. **Generate citation-lock.tex** to lock reference numbering

### Citation Key Mapping

Zotero citation-keys look like:
```
WuZeXinZhongYiYouShiBingZhongNaRuDRGDIPFuFeiGuiFanFenXia
```

LaTeX reference keys look like:
```
ref001, ref002, ref003, ...
```

The mapping is stored in `ref/citation-mapping.json`:

```json
{
  "description": "Zotero citation-key to LaTeX ref number mapping",
  "version": "1.0",
  "mappings": {
    "WuZeXinZhongYiYouShiBingZhongNaRuDRGDIPFuFeiGuiFanFenXia": "ref001",
    "ZhangSan2020SomeTitle": "ref002"
  }
}
```

### Citation Lock Mechanism

`citation-lock.tex` uses `\nocite{}` to force all references to appear in bibliography:

```latex
\nocite{ref001,ref002,ref003,...}
```

This ensures stable reference numbering even when:
- Some citations are not explicitly cited in the text
- Citations are removed from chapters

### Workflow for Users

1. **Edit in Word** with Zotero
2. **Save Word file** and note the path
3. **Run sync script**:
   ```bash
   python 00-bib-zotero/sync_from_word.py --project-root thesis --word-file thesis.docx --apply
   ```
4. **Export new bib entries** from Zotero if needed
5. **Compile LaTeX** project

### Citation Operation Rules

| Operation | bib file | Mapping | Citation lock |
|-----------|----------|---------|---------------|
| Add citation | Add new entry | Add mapping | Add to nocite |
| Remove citation | Keep entry | Keep mapping | Keep in nocite |
| Replace citation | Modify entry | Keep mapping | No change |

**Why keep removed citations?**

Removing a bib entry would shift all subsequent reference numbers. For example, if ref005 is removed:
- ref006 becomes ref005
- All citations after ref005 would be wrong

Instead:
- Remove `\cite{ref005}` from chapter files
- Keep the bib entry (it won't appear in output)
- Reference numbers stay stable

### Required Zotero Setup

1. Install [Better BibTeX](https://retorque.re/zotero-better-bibtex/)
2. Set citation key formula:
   ```
   [auth][year][veryshorttitle]
   ```
3. Export collection as "Better BibLaTeX" with "Keep updated" enabled

### Output

The script generates:
- `ref/citation-mapping.json` - Citation key mapping
- `citation-lock.tex` - Reference numbering lock
- `reports/sync_from_word-report.json` - Sync report

## Files

- `check_bib_quality.py` - BibTeX quality checker
- `sync_from_word.py` - Word→LaTeX citation sync
- `THESIS_BIB_ZOTERO.md` - This documentation

## Related

- `core/zotero_extract.py` - Zotero extraction core
- `core/citation_mapping.py` - Citation mapping management
