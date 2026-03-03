# THESIS_MIGRATE

## Purpose
Convert Word-derived LaTeX content into this ThuThesis project safely, while preserving existing legacy scripts.

---

## Phase 0 (Pre-migrate): Zotero / EndNote `.bib` Export

If your Word document still has **Zotero field codes active**, run the `00-zotero` skill first:

```
python 00-zotero/check_bib_quality.py
```

This exports a clean `ref/refs-import.bib` directly from your Zotero library with proper cite
keys and `langid` fields — far more reliable than the plain-text reconstruction path.

| Situation | Action |
|---|---|
| Zotero fields still active in Word | Run `00-zotero` skill first, then come back here |
| Only plain-text references remain | Skip Phase 0, continue with steps below |

If you ran Phase 0 and `ref/refs-import.bib` is already populated:
- Run steps 1–2 below normally
- **Skip step 3** (`generate_sanitized_refs_import.py`) to avoid overwriting the clean export

---

## Scope
- Use existing scripts only:
  - `scripts/migrate_from_word_tex.py`
  - `scripts/normalize_citations.py`
  - `scripts/generate_sanitized_refs_import.py`
- Do not rewrite or relocate these scripts.

## Quickstart
1. Confirm source files exist:
   - `data/from_word_full.tex`
   - `ref/refs-import.bib` target path is writable
2. Run migration sequence from project root:
   - `python scripts/migrate_from_word_tex.py`
   - `python scripts/normalize_citations.py`
   - `python scripts/generate_sanitized_refs_import.py`
3. Verify outputs:
   - Updated `data/chap02.tex` ... `data/chap06.tex`
   - Updated `ref/refs-import.bib`

## Standard Flow
1. Snapshot current files with format loop (`snapshot` action).
2. Run chapter migration script.
3. Normalize citation markers into `\cite{...}`.
4. Generate sanitized imported bibliography placeholders.
5. Run format compile/check loop.

## Inputs And Outputs
- Input:
  - `data/from_word_full.tex`
  - `word-model/references.txt` (for import bib generation)
- Output:
  - `data/chap02.tex` ... `data/chap06.tex`
  - `ref/refs-import.bib`
  - `data/*.template_backup.tex` (created by migration script)

## Safety Rules
- Never overwrite legacy script files.
- Never run migration without backup/snapshot.
- If migration output is malformed, restore snapshot first, then debug.

## Troubleshooting
- Missing source file:
  - Symptom: file not found error
  - Fix: ensure `data/from_word_full.tex` exists
- Broken citation conversion:
  - Symptom: `\textsuperscript` patterns remain
  - Fix: inspect source format and update conversion regex in a new script version (do not hot-edit legacy script in this skill run)
- Empty `refs-import.bib`:
  - Symptom: entries count is 0
  - Fix: verify `word-model/references.txt` format is `[N] ...`

## Verification
- `python scripts/migrate_from_word_tex.py`
- `python scripts/normalize_citations.py`
- `python scripts/generate_sanitized_refs_import.py`

## Related Guides
- `scripts/skills/THESIS_SKILLS_GUIDE.zh-CN.md`
- `scripts/skills/THESIS_SKILLS_GUIDE.en.md`
