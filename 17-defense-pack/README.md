# THESIS_DEFENSE_PACK

This workflow family owns the bounded defense-prep artifact layer for an existing thesis project.

Use it to:

- extract a defense outline from the current thesis structure
- summarize chapter-level highlights for presentation planning
- inventory figures and candidate visuals before slide design
- generate talk-prep notes as editable speaker-support material

Current runners:

- `17-defense-pack/generate_outline.py`
- `17-defense-pack/generate_chapter_highlights.py`
- `17-defense-pack/generate_figure_inventory.py`
- `17-defense-pack/generate_candidate_tables_diagrams.py`
- `17-defense-pack/generate_talk_prep_notes.py`

## Contract

- inputs: an existing thesis project plus a selected `--ruleset`
- outputs: bounded, inspectable artifact files written through the report/artifact layer
- scope: preparation artifacts only

## Important boundary

- this workflow does **not** generate a final defense PPT
- it does **not** decide your final talk strategy automatically
- it does **not** replace human judgment about contribution emphasis, slide design, or live Q&A preparation

## Example

```bash
python 17-defense-pack/generate_outline.py \
  --project-root <latex-project> \
  --ruleset <ruleset>

python 17-defense-pack/generate_figure_inventory.py \
  --project-root <latex-project> \
  --ruleset <ruleset>
```
