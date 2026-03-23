# EndNote Import Workflow (v0.4 MVP)

Use this workflow when your references come from **EndNote** and you want to bring them into a LaTeX thesis project managed by `thesis-skills`.

This document describes the **currently implemented** EndNote support in the `endnote-v0.4` worktree. It does **not** describe future-only features.

---

## What v0.4 currently supports

Current EndNote support is **import-first**:

```text
EndNote XML / RIS
-> parse
-> canonicalize
-> DOI-based dedupe
-> reuse / allocate refNNN
-> render refs-import.bib
-> update citation-mapping.json
-> emit JSON report
```

Implemented in this worktree:

- XML import
- RIS import
- dry-run preview
- apply mode
- DOI exact dedupe
- existing mapping reuse
- stable `refNNN` allocation
- preflight export check

Not yet implemented in this MVP:

- EndNote Word field-code parsing
- Traveling Library extraction
- BibTeX input fallback
- low-confidence title/year/author merge logic
- GUI

---

## Recommended export order

For the currently implemented code, use this priority:

1. **XML** — best current path
2. **RIS** — supported and tested

BibTeX is still planned as a later fallback path and should not be treated as implemented in this MVP.

---

## Command 1: preflight-check an EndNote export

Before import, run the preflight checker.

### XML example

```bash
python 00-bib-endnote/check_endnote_export.py \
  --project-root path/to/thesis \
  --input path/to/endnote.xml \
  --format auto
```

### RIS example

```bash
python 00-bib-endnote/check_endnote_export.py \
  --project-root path/to/thesis \
  --input path/to/endnote.ris \
  --format auto
```

### Current behavior

The checker currently reports:

- source format
- total refs
- warnings count
- errors count

Warning examples in the current MVP:

- missing title
- missing authors
- DOI needs normalization

The default report path is:

- `reports/check_endnote_export-report.json`

---

## Command 2: import EndNote records into the thesis project

### Dry-run mode

Dry-run generates a report and preview data but does **not** write `refs-import.bib`.

```bash
python 00-bib-endnote/import_library.py \
  --project-root path/to/thesis \
  --input path/to/endnote.xml \
  --format auto
```

### Apply mode

Apply mode writes project files.

```bash
python 00-bib-endnote/import_library.py \
  --project-root path/to/thesis \
  --input path/to/endnote.xml \
  --format auto \
  --apply
```

### Current apply outputs

When `--apply` is used, the MVP writes:

- `ref/refs-import.bib`
- `ref/citation-mapping.json`
- `reports/endnote-import-report.json`

---

## What the importer currently does

### 1. Format detection

`--format auto` currently supports:

- `.xml`
- `.ris`

### 2. Canonicalization

Current canonicalization includes:

- DOI normalization
- title normalization for matching/canonical ID
- author name trimming
- basic `langid` inference
- entry type normalization

### 3. Dedupe

Current dedupe behavior is intentionally conservative:

- exact duplicate DOI -> dedupe
- first matching DOI record is kept
- a warning is emitted

The importer does **not** currently auto-merge low-confidence title/year/author matches.

### 4. Mapping reuse

If `ref/citation-mapping.json` already exists and contains a matching canonical ID, the importer reuses the existing `refNNN`.

### 5. Stable numbering

New references are allocated after the current maximum `refNNN`.

This means the current MVP already supports:

- repeat runs on the same input without renumber drift
- preserving existing imported numbering when mapping exists

---

## Report fields you can expect today

`endnote-import-report.json` currently includes:

- `mode`
- `source_format`
- `total_refs`
- `rendered_refs`
- `deduped_refs`
- `warnings`
- `errors`
- `mapping_preview`
- `render_preview`

This is enough for dry-run inspection before applying changes.

---

## Current limitations

Please treat these as real limitations of the current MVP, not hidden roadmap promises:

1. **BibTeX input is not implemented yet**
2. **Only DOI exact dedupe is implemented**
3. **Unknown types fall back to `misc`**
4. **Low-confidence duplicate suggestions are not implemented yet**
5. **This workflow does not read EndNote citations directly from Word documents**

---

## Relationship to Zotero workflow

The current EndNote MVP is designed to avoid breaking the existing Zotero path.

Important constraints:

- existing Zotero commands are left intact
- current `CitationMapping` behavior is still preserved for existing Zotero flows
- EndNote import currently reuses the same `refNNN` numbering model

So at this stage, EndNote support is an **adjacent import workflow**, not a replacement for Zotero sync.

---

## v0.4 / v0.5 boundary

### v0.4 MVP (implemented / in-progress scope)

- XML import
- RIS import
- preflight check
- dry-run import preview
- apply mode writing Bib + mapping
- DOI exact dedupe
- existing mapping reuse

### v0.5 candidates (not implemented here)

- EndNote Word field-code parser
- Traveling Library extraction
- richer duplicate matching
- BibTeX fallback import
- more complete mapping schema evolution

---

## Practical recommendation

If you want to use the current MVP safely:

1. export **XML** first, or RIS if XML is unavailable
2. run `check_endnote_export.py`
3. run `import_library.py` in dry-run mode first
4. inspect the JSON report
5. only then run `--apply`

This is the safest path with the functionality currently implemented in the worktree.
