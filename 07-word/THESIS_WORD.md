# THESIS_WORD

## Purpose
Provide a Word-first formatting workflow for Tsinghua thesis submissions with a deterministic repair boundary.

## First Run: Macro Security (Required)
If Lite macro does not run, solve this before any testing:
1. Move `.dotm` and test docx into a trusted local folder.
2. Right-click downloaded `.dotm` -> Properties -> check **Unblock** if present.
3. Word -> Options -> Trust Center -> Trust Center Settings:
   - enable trusted location for your local test folder, or
   - allow signed macros in your org policy path.
4. Reopen Word and verify macro `OneClickDetectAndFix` appears in Macro list.

## Scope
- Lite (`07-word/lite`): VBA-only one-click detect/fix for fixed Tsinghua template mapping.
- Pro (`07-word/pro`): Python lint/planner + VBA executor with auditable `report.json` and `fix_plan.json`.
- Preserve content meaning. Focus on mechanical formatting integrity only.

## Goal Boundary
- Supported (v1): heading styles, paragraph normalization, caption style + SEQ auto-rebuild (M2), three-line table rules with header-row enforcement and nested-table skip (M3), field update, TOC rebuild, export.
- Not supported (v1): rewriting body content, deep page beautification, manual aesthetic layout tuning.

## Quickstart (Lite)
1. For end-user installation, use the separate plugin repo `thu-word-plugin-lite` to package/load `THU-Formatter-Lite.dotm`.
2. Click one button: detect + fix.
3. Receive outputs: `*_fixed.docx`, `*_fixed.pdf`, `fix_log.txt`.

## Quickstart (Pro)
1. Run Python lint/planner to generate `report.json` and `fix_plan.json`.
2. Load plan into Word macro executor.
3. Execute whitelisted actions, refresh fields, export outputs.
4. One-pass helper: `python 07-word/pro/run_word_check_once.py --doc "C:/path/to/thesis.docx"`.

## Core Specs
- `actions_spec.md`: whitelisted action contract.
- `plan_schema.md`: minimum schema for report and fix plan.
- `REPO_SPLIT_POSITIONING.zh-CN.md`: future split positioning for `thesis-skills` repo.

## Verification
- Lite: run macro on a sample thesis document; verify TOC/SEQ/page fields update and export success.
- Pro: run CLI on sample docx; validate JSON schema; execute a no-op and a safe plan.
