# THESIS_WORD_TO_LATEX

This workflow owns the migration boundary from Word assets into a LaTeX project.

Use it to:

- inspect exported Word TeX or chapter text
- confirm bibliography source type (`zotero` or `endnote`)
- map source assets into the target LaTeX project structure

Recommended sequence:

1. Run `00-bib-zotero` or `00-bib-endnote` first.
2. Copy or convert chapter assets into the target LaTeX project.
3. Run `run_check_once.py` immediately after migration.
4. Use `run_fix_cycle.py` for mechanical fixes only.

Migration helper:

```bash
python 01-word-to-latex/migrate_project.py --source-root <intake> --target-root <latex-project> --spec <migration.json> --apply false
```

The `migration.json` file should declare `chapter_mappings` and `bibliography_mappings` with explicit `from` / `to` pairs.
