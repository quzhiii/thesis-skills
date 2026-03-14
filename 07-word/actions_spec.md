# Word Formatter Action Spec (v1)

This document defines the allowed action whitelist for Word thesis auto-formatting.

## Principles
- Deterministic and auditable.
- Idempotent where possible.
- No semantic rewriting of thesis content.
- All actions target explicit locations.

## Location Model
- `paragraph_index`: zero-based paragraph index in main story.
- `bookmark`: named bookmark when available.
- `table_index`: zero-based table index.
- `range_selector`: optional fallback (`story`, `selection`, `all`).

## Whitelisted Actions

### 1) APPLY_STYLE
- **Target**: paragraph or character range
- **Params**: `style_name`, `kind` (`paragraph` | `character`), `clear_formatting` (bool, default true)
- **Effect**: assign style only, no text rewrite; when `clear_formatting=true`, clear direct formatting overrides before style assignment

### 2) SET_PARAGRAPH_FORMAT
- **Target**: paragraph
- **Params**: subset of Word paragraph options:
  - `line_spacing_rule`
  - `line_spacing`
  - `first_line_indent`
  - `left_indent`
  - `right_indent`
  - `space_before`
  - `space_after`
  - `keep_with_next`
  - `keep_together`
- **Effect**: normalize paragraph format safely

### 3) CONVERT_PSEUDO_HEADING
- **Target**: paragraph
- **Params**: `level` (1|2|3), `style_name`
- **Precondition**: matches v1 heading pattern (`1`, `1.1`, `1.1.1`)
- **Effect**: convert pseudo heading to template heading style

### 4) ENSURE_CAPTION
- **Target**: paragraph or nearest object anchor
- **Params**: `caption_kind` (`figure` | `table`), `label`, `position`
- **Effect**: ensure caption style and SEQ field consistency

### 5) SET_TABLE_BORDERS
- **Target**: table
- **Params**:
  - `mode` (`three_line`)
  - `header_row` (true/false)
  - `header_style` (optional)
- **Effect**: apply three-line table borders and header styling

### 6) UPDATE_FIELDS
- **Target**: document
- **Params**: `include_headers_footers` (bool)
- **Effect**: update TOC/REF/SEQ/page and related fields

### 7) REBUILD_TOC
- **Target**: document
- **Params**:
  - `toc` (bool)
  - `list_of_figures` (bool)
  - `list_of_tables` (bool)
- **Effect**: rebuild TOC and optional figure/table lists

### 8) EXPORT_PDF
- **Target**: document
- **Params**: `output_path`
- **Effect**: export fixed document to PDF

### 9) ENSURE_INLINE_SHAPE
- **Target**: shape(s) anchored near caption paragraph
- **Params**: `window_chars` (int, default 500)
- **Effect**: convert floating shapes to inline shapes near caption anchors to stabilize SEQ ordering

## Forbidden Actions (v1)
- Deleting arbitrary paragraphs.
- Rewriting sentence content.
- Moving figures/tables for visual aesthetics.
- Running non-whitelisted macros or shell commands.

## Error Strategy
- Skip-on-fail per action and append detailed log entry.
- Preserve original doc until explicit save-as fixed file step.
