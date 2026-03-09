# Thesis Skills

Deterministic thesis and journal writing skills with Python checkers, safe fixers, YAML rule packs, and one-click runners.

## What changed

- Keep `Python + Skills` as the main product shape.
- Split `check` and `fix` into separate modules.
- Make `90-rules` actually drive checker behavior.
- Add starter packs for `tsinghua-thesis`, `university-generic`, and `journal-generic`.
- Add intake guidance for other schools and journals.

## Quick start

```bash
python run_check_once.py --project-root examples/minimal-latex-project --ruleset university-generic --skip-compile
python run_fix_cycle.py --project-root examples/minimal-latex-project --ruleset university-generic --apply false
python 90-rules/create_pack.py --pack-id my-university --display-name "My University Thesis" --starter university-generic --kind university-thesis
python 90-rules/create_draft_pack.py --intake adapters/intake/example-intake.json
python 01-word-to-latex/migrate_project.py --source-root <intake> --target-root <latex-project> --spec <migration.json> --apply false
```

## Repository map

- `00-bib-zotero/`, `00-bib-endnote/`, `01-word-to-latex/` - migration-side workflows
- `10-check-*` - deterministic report generators
- `20-fix-*` - safe patch/fix workflows reading reports
- `90-rules/packs/` - reusable school and journal packs
- `adapters/intake/` - what users should upload for a new pack
- `examples/minimal-latex-project/` - runnable sample project

## New pack and migration helpers

- `90-rules/create_pack.py` creates a new school or journal pack from a starter.
- `90-rules/create_draft_pack.py` generates a draft pack directly from uploaded-material metadata.
- `01-word-to-latex/migrate_project.py` applies an explicit migration spec from intake assets to a LaTeX project.
- `adapters/intake/README.md` documents what users should upload before adaptation.

The stronger migration spec now supports:

- `document_metadata`
- `word_style_mappings`
- `chapter_role_mappings`
- explicit `chapter_mappings` and `bibliography_mappings`

## Other schools and journals

Users can start a new pack by copying either:

- `90-rules/packs/university-generic/`
- `90-rules/packs/journal-generic/`

Then provide:

- official guide (`pdf`, `html`, or plain text)
- official template (`docx`, `dotx`, `cls`, `sty`, `tex`)
- one compliant sample (`pdf` or source)
- optional bibliography style files (`bst`, `bbx`, `cbx`, `csl`)

See `adapters/intake/README.md` and `90-rules/THESIS_RULE_PACKS.md`.

## Template links

Use these repositories as jump-off points before running migration or rule-pack onboarding. Always verify the current university or journal rules against the official guide.

### China

- Tsinghua University - `tuna/thuthesis` - https://github.com/tuna/thuthesis
- Shanghai Jiao Tong University - `sjtug/SJTUThesis` - https://github.com/sjtug/SJTUThesis
- USTC - `ustctug/ustcthesis` - https://github.com/ustctug/ustcthesis
- UESTC - `tinoryj/UESTC-Thesis-Latex-Template` - https://github.com/tinoryj/UESTC-Thesis-Latex-Template
- UCAS - `mohuangrui/ucasthesis` - https://github.com/mohuangrui/ucasthesis
- Peking University - `CasperVector/pkuthss` or maintained forks such as `Thesharing/pkuthss`

### International

- Stanford University - `dcroote/stanford-thesis-example` - https://github.com/dcroote/stanford-thesis-example
- University of Cambridge - `cambridge/thesis` - https://github.com/cambridge/thesis
- University of Oxford - `mcmanigle/OxThesis` - https://github.com/mcmanigle/OxThesis
- EPFL - `HexHive/thesis_template` - https://github.com/HexHive/thesis_template
- ETH Zurich - `tuxu/ethz-thesis` - https://github.com/tuxu/ethz-thesis
- MIT (widely used unofficial) - `alinush/mit-thesis-template` - https://github.com/alinush/mit-thesis-template
