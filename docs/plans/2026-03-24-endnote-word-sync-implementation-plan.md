# EndNote Word Sync Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a safe EndNote Word-to-LaTeX path to `thesis-skills` without breaking the current Zotero sync or the in-flight v0.5 language program.

**Architecture:** Build this as a separate post-v0.5 track. First add a read-only EndNote Word extractor and fixture corpus, then add a report-only sync CLI, and only after that allow mapping updates plus `citation-lock.tex` generation. Reuse the existing EndNote canonicalization/import pipeline where possible, but do not force the Zotero-specific mapping model to change until the extractor and matching contracts are proven by tests.

**Tech Stack:** Python 3.10+, `.docx` zip/XML parsing, current `core/` runner utilities, `unittest`/`pytest`, existing `CitationMapping`, EndNote XML/RIS import pipeline.

---

## Scheduling Decision

This plan should **not** be executed on the current in-flight `v0.5` language branch.

Execute it only after:

1. `v0.5.0`, `v0.5.1`, and `v0.5.2` are cut or at least merged back to `main`.
2. The current language-track files are stable:
   - `11-check-language/`
   - `14-check-language-deep/`
   - `21-fix-language-style/`
   - `24-fix-language-deep/`
   - `core/language_*`
3. A fresh branch is created from the post-v0.5 baseline, for example `codex/endnote-word-sync-<date>`.

Reason: the current `v0.5` execution plan is explicitly a language-quality track, and the working tree already contains substantial in-progress changes there. Mixing EndNote Word sync into that branch will create scope drift and make release boundaries harder to defend.

## Scope Boundary

Included in this plan:

- EndNote citation extraction from Word `.docx`
- Traveling Library-oriented data recovery when present
- report-only comparison against the existing thesis project mapping
- later safe `--apply` mode that reuses `refNNN` and `citation-lock.tex`

Not included in this plan:

- GUI or desktop integration
- PDF-first parsing
- broad rewrite of all bibliography architecture before extractor correctness is proven
- replacing the Zotero workflow

## Design Summary

The current Zotero sync path is tightly coupled to a Zotero-shaped extractor and `dict[str, str]` mapping:

- `00-bib-zotero/sync_from_word.py`
- `core/zotero_extract.py`
- `core/citation_mapping.py`

The EndNote Word path should therefore be introduced in three layers:

1. **Extraction layer**
   Read `.docx`, locate EndNote-related field payloads, and emit normalized in-document citation records.
2. **Matching layer**
   Match extracted records to imported EndNote references already normalized in project data, using DOI first and then a conservative normalized fingerprint.
3. **Sync layer**
   Reuse the existing mapping and citation lock workflow, but only after matching confidence is high enough.

The critical rule is: **no apply mode until report-only mode is stable on realistic fixtures**.

## Task 0: Lock The Execution Envelope

**Files:**
- Modify: `docs/roadmap.md`
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Test: none

**Step 1: Update roadmap wording**

Add a short note that the current `v0.5` program is the language track and that EndNote Word sync has moved to a follow-up track after `v0.5.2`.

**Step 2: Update public wording**

Keep EndNote support wording accurate:

- EndNote XML/RIS/BibTeX import is stable in `v0.4.0`
- EndNote Word direct sync is planned but not shipped

**Step 3: Verify wording consistency**

Run:

```bash
rg -n "EndNote direct sync|Word field|Traveling Library|v0.5" README.md README.zh-CN.md docs/roadmap.md
```

Expected: no line claims direct EndNote Word sync is already implemented.

**Step 4: Commit**

```bash
git add docs/roadmap.md README.md README.zh-CN.md
git commit -m "docs: separate endnote word sync from v0.5 language track"
```

## Task 1: Build A Realistic EndNote Word Fixture Corpus

**Files:**
- Create: `tests/data/endnote_word/minimal_with_single_citation.docx`
- Create: `tests/data/endnote_word/minimal_with_multi_citation.docx`
- Create: `tests/data/endnote_word/minimal_with_deleted_citation.docx`
- Create: `tests/data/endnote_word/README.md`
- Create: `tests/test_endnote_word_fixtures.py`

**Step 1: Write the failing fixture test**

Add tests that assert the fixtures exist, are valid `.docx` zip files, and contain `word/document.xml`.

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_endnote_word_fixtures.py -v
```

Expected: FAIL because the fixtures and test file do not exist yet.

**Step 3: Add the fixtures and minimal test**

Use real EndNote-generated samples if available. Avoid synthetic fake XML unless no real sample exists.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_endnote_word_fixtures.py -v
```

Expected: PASS.

**Step 5: Commit**

```bash
git add tests/data/endnote_word tests/test_endnote_word_fixtures.py
git commit -m "test: add endnote word fixture corpus"
```

## Task 2: Add A Read-Only EndNote Word Extractor

**Files:**
- Create: `core/endnote_word_extract.py`
- Create: `tests/test_endnote_word_extract.py`
- Test: `tests/data/endnote_word/*`

**Step 1: Write the failing extractor test**

Cover these behaviors:

- open `.docx` safely
- collect candidate EndNote field payloads in order
- emit a structured extraction result with `citations`, `errors`, and `source_file`
- preserve citation order and de-duplicate conservatively

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_endnote_word_extract.py -v
```

Expected: FAIL with missing module or missing functions.

**Step 3: Write minimal implementation**

Create a read-only extractor that:

- reads `word/document.xml`
- inspects field-related XML payloads and adjacent EndNote-specific text markers
- extracts whatever stable citation identity is available
- returns structured records such as:

```python
{
    "source_type": "endnote_word",
    "record_number": "...",
    "doi": "...",
    "title": "...",
    "authors": [...],
    "year": "...",
    "raw_payload": "...",
    "position": 0,
}
```

Do not update mapping here.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_endnote_word_extract.py -v
```

Expected: PASS.

**Step 5: Commit**

```bash
git add core/endnote_word_extract.py tests/test_endnote_word_extract.py
git commit -m "feat: add read-only endnote word extractor"
```

## Task 3: Add Conservative Match Logic Against Imported EndNote Data

**Files:**
- Create: `core/endnote_match.py`
- Create: `tests/test_endnote_match.py`
- Modify: `00-bib-endnote/import_library.py`
- Modify: `core/citation_models.py`

**Step 1: Write the failing match test**

Cover these match rules:

- DOI exact match wins
- normalized title + first author + year can produce a low-confidence match
- missing DOI and ambiguous title must remain unresolved
- multiple candidate matches must be flagged, not auto-applied

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_endnote_match.py -v
```

Expected: FAIL because the match module does not exist yet.

**Step 3: Write minimal implementation**

Expose a matcher that consumes extracted Word citations plus already imported reference objects and returns:

```python
{
    "matched": [...],
    "unmatched": [...],
    "ambiguous": [...],
}
```

Include explicit confidence levels:

- `high`: DOI exact
- `medium`: stable metadata fingerprint
- `low`: weak heuristic only

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_endnote_match.py -v
```

Expected: PASS.

**Step 5: Commit**

```bash
git add core/endnote_match.py core/citation_models.py 00-bib-endnote/import_library.py tests/test_endnote_match.py
git commit -m "feat: add conservative endnote citation matching"
```

## Task 4: Add Report-Only EndNote Word Sync CLI

**Files:**
- Create: `00-bib-endnote/sync_from_word.py`
- Create: `00-bib-endnote/THESIS_BIB_ENDNOTE_WORD.md`
- Create: `tests/test_endnote_sync_from_word.py`
- Modify: `README.md`
- Modify: `README.zh-CN.md`

**Step 1: Write the failing CLI test**

Test a dry-run path that:

- loads a thesis project
- extracts EndNote Word citations
- matches them against imported data
- writes a JSON report
- does not modify `citation-mapping.json`
- does not create `citation-lock.tex`

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_endnote_sync_from_word.py -v
```

Expected: FAIL because the CLI does not exist yet.

**Step 3: Write minimal implementation**

The initial CLI must support:

```bash
python 00-bib-endnote/sync_from_word.py --project-root thesis --word-file thesis.docx
```

Report shape should include:

- extracted citation count
- matched count
- ambiguous count
- unresolved count
- proposed `latex_key` assignments for high-confidence matches only

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_endnote_sync_from_word.py -v
```

Expected: PASS.

**Step 5: Commit**

```bash
git add 00-bib-endnote/sync_from_word.py 00-bib-endnote/THESIS_BIB_ENDNOTE_WORD.md README.md README.zh-CN.md tests/test_endnote_sync_from_word.py
git commit -m "feat: add report-only endnote word sync cli"
```

## Task 5: Add Safe Apply Mode

**Files:**
- Modify: `00-bib-endnote/sync_from_word.py`
- Modify: `core/citation_mapping.py`
- Create: `tests/test_endnote_sync_apply.py`

**Step 1: Write the failing apply-mode test**

Cover these rules:

- `--apply` only updates mappings for `high` confidence matches
- ambiguous and unresolved citations stay report-only
- `citation-lock.tex` is regenerated after mapping updates
- previously assigned `refNNN` values remain stable

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_endnote_sync_apply.py -v
```

Expected: FAIL because apply mode does not exist yet.

**Step 3: Write minimal implementation**

Add `--apply` with these guards:

- reject apply when unresolved or ambiguous citations exist unless `--force-low-confidence` is explicitly set
- default behavior only writes high-confidence matches
- preserve existing `refNNN` numbering model

If schema changes are needed in `citation-mapping.json`, add them as optional metadata fields without breaking the current `dict[str, str]` contract used by Zotero.

**Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_endnote_sync_apply.py -v
```

Expected: PASS.

**Step 5: Run compatibility tests**

Run:

```bash
pytest tests/test_runner.py tests/test_manifest.py tests/test_rules.py tests/test_endnote_sync_from_word.py tests/test_endnote_sync_apply.py -v
```

Expected: PASS.

**Step 6: Commit**

```bash
git add 00-bib-endnote/sync_from_word.py core/citation_mapping.py tests/test_endnote_sync_apply.py
git commit -m "feat: add safe apply mode for endnote word sync"
```

## Task 6: Regression Proof For Zotero Compatibility

**Files:**
- Modify: `tests/test_runner.py`
- Modify: `tests/test_manifest.py`
- Modify: `tests/test_rules.py`
- Create: `tests/test_cross_source_mapping.py`

**Step 1: Write the failing compatibility tests**

Cover:

- Zotero sync still works unchanged
- EndNote import plus EndNote Word sync reuses `refNNN`
- `citation-lock.tex` content remains valid
- no public docs imply EndNote and Zotero share identical extraction semantics

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_cross_source_mapping.py -v
```

Expected: FAIL until the compatibility layer is in place.

**Step 3: Write minimal implementation**

Adjust only the minimal shared utilities needed for both sources to coexist.

**Step 4: Run full targeted suite**

Run:

```bash
pytest tests/test_zotero_extract.py tests/test_runner.py tests/test_rules.py tests/test_manifest.py tests/test_cross_source_mapping.py -v
```

Expected: PASS.

**Step 5: Commit**

```bash
git add tests/test_runner.py tests/test_manifest.py tests/test_rules.py tests/test_cross_source_mapping.py
git commit -m "test: lock zotero and endnote cross-source compatibility"
```

## Risks And Mitigations

- **Risk:** EndNote Word field payloads differ across Word/EndNote versions.
  Mitigation: collect fixture corpus from at least 3 real documents before trusting parser assumptions.

- **Risk:** extractor cannot recover stable external ids from Word alone.
  Mitigation: keep matching conservative and report-only until DOI or normalized metadata matching is proven.

- **Risk:** changing `citation-mapping.json` breaks Zotero sync.
  Mitigation: preserve current `mappings: dict[str, str]` contract and add optional metadata only.

- **Risk:** scope drifts into a v0.5 language branch already in progress.
  Mitigation: execute only after the current `v0.5` track lands, on a fresh isolated branch.

## Release Recommendation

Do not ship this as part of `v0.5.x`.

Recommended release framing:

1. `v0.5.x`: complete the language-quality program already in progress.
2. `v0.6.0`: EndNote Word extractor plus report-only sync.
3. `v0.6.1`: safe apply mode after fixture coverage and compatibility tests are stable.

## Current Session Alignment

The referenced session `019d1fc5-dd45-75f2-8ffa-92507c35e066` is already executing a separate `v0.5` language track:

- worktree branch: `codex/v0.5-language-execution-20260324`
- backup tag: `backup/pre-v0.5-language-20260324`
- direction: Phase 0 hardening, then `v0.5.0`, `v0.5.1`, `v0.5.2`

That means the correct move now is to keep this EndNote Word plan parked as the next major track instead of mixing it into the current release train.
