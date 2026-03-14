# My University Ruleset (Example)

This is a starter non-Tsinghua ruleset for schools that already have a LaTeX thesis template.

## How to adapt

1. Update `structure.yaml`:
   - `main_tex`
   - `chapter_glob`
   - `exclude_glob`
2. Update `citation.yaml` bib source paths.
3. Adjust `format.yaml` numbering separators and strictness.
4. Adjust `language.yaml` based on your school's writing guidance.

## Validation command

```bash
python run_check_once.py --project-root "../thuthesis-v7.6.0" --rules my-university --skip-compile
```
