# THU Formatter Lite (Word-only)

VBA-only formatter for a fixed Tsinghua Word template mapping.

## Scope (v1)
- Template bind/sync
- Pseudo heading conversion (1 / 1.1 / 1.1.1) with direct-format clearing
- Paragraph normalization
- Caption style normalization and SEQ auto-rebuild (M2)
- Convert nearby floating shapes to inline near captions to stabilize numbering
- Three-line table formatting with header-row rule and skip strategy for nested tables (M3)
- Field refresh and TOC rebuild
- Export fixed DOCX/PDF and text log

## Not in scope (v1)
- Content rewriting
- Fine-grained visual page beautification
- Arbitrary school template support

## Files
- `THU_Formatter_Lite.bas`: importable VBA module skeleton

## Build/Add-in Packaging
1. Open Word VBA editor.
2. Import `THU_Formatter_Lite.bas`.
3. Save as `.dotm` (macro-enabled template).
4. Add one Ribbon/QAT button mapped to `OneClickDetectAndFix`.

## Optional Template Binding
- Set environment variable `THU_TEMPLATE_PATH` to a local Tsinghua template path.
- If unset, formatter still runs and skips template attach.
