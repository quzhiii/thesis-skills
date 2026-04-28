# THESIS_RULE_PACKS

Each school or journal lives in `90-rules/packs/<ruleset>/`.

Current baseline and extension assumptions are documented in:

- `90-rules/STARTER_PACK_BASELINE.md`

Current mixed local / Git / export maintenance workflows are documented in:

- `90-rules/MIXED_PACK_WORKFLOWS.md`

Required files:

- `pack.yaml` - metadata, precedence, scope
- `rules.yaml` - actual checker/fixer rules
- `mappings.yaml` - source template and intake mappings

Starter packs included:

- `tsinghua-thesis`
- `university-generic`
- `journal-generic`

Concrete non-Tsinghua example pack:

- `demo-university-thesis`

When onboarding a new school or journal, copy the closest starter pack and then confirm ambiguous rules manually.

Helper command:

```bash
python 90-rules/create_pack.py --pack-id my-university --display-name "My University Thesis" --starter university-generic --kind university-thesis
```

Draft scaffold from uploaded-material metadata:

```bash
python 90-rules/create_draft_pack.py --intake adapters/intake/example-intake.json
```

Expected intake metadata fields:

- `pack_id`
- `display_name`
- `kind`
- `starter`
- `institution`
- `guide_sources`
- `template_sources`
- `sample_sources`
- `word_style_mappings`
- `chapter_role_mappings`
