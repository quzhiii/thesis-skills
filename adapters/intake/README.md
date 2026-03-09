# Intake Adapter Guide

For a new school or journal, collect these inputs first:

- official guide: `pdf`, `html`, or plain text
- official template: `docx`, `dotx`, `cls`, `sty`, `tex`
- one compliant sample: source preferred, otherwise `pdf`
- optional style files: `bst`, `bbx`, `cbx`, `csl`
- optional screenshots for title page, abstract page, figure/table pages

Suggested onboarding workflow:

1. Place raw inputs under an intake folder outside the project.
2. Copy the nearest starter pack from `90-rules/packs/`.
3. Encode high-confidence constraints into `rules.yaml`.
4. Record source-template names and logical roles in `mappings.yaml`.
5. Run the sample project through `run_check_once.py` and iterate.

## Suggested migration spec

For `01-word-to-latex/migrate_project.py`, create a JSON file like:

```json
{
  "chapter_mappings": [
    {"from": "chapters/chapter1.tex", "to": "chapters/01-introduction.tex"}
  ],
  "bibliography_mappings": [
    {"from": "refs-import.bib", "to": "ref/refs-import.bib"}
  ]
}
```

This keeps migration explicit and auditable rather than guessing from filenames.

Recommended stronger intake schema:

```json
{
  "document_metadata": {
    "source_format": "word-exported-tex",
    "bibliography_source": "zotero",
    "template_family": "university-generic"
  },
  "word_style_mappings": [
    {"style": "Heading 1", "role": "chapter", "latex_command": "chapter"},
    {"style": "Heading 2", "role": "section", "latex_command": "section"}
  ],
  "chapter_role_mappings": [
    {"source": "chapters/chapter1.tex", "role": "introduction", "target": "chapters/01-introduction.tex"}
  ],
  "chapter_mappings": [
    {"from": "chapters/chapter1.tex", "to": "chapters/01-introduction.tex", "role": "introduction", "word_style": "Heading 1"}
  ],
  "bibliography_mappings": [
    {"from": "refs-import.bib", "to": "ref/refs-import.bib"}
  ]
}
```

This gives the migration step enough information to preserve Word style intent, logical chapter roles, and bibliography source context.
