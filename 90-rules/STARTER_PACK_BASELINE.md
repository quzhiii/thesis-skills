# Starter Pack Baseline

This document records the **current repository baseline** for rule-pack starters in the v1.0 public contract.

It is intentionally descriptive, not aspirational: the goal is to state what a starter pack currently means in this repo, which assumptions are explicit, and which assumptions are checked by the current lint / completeness / schema-consistency tooling.

---

## 1. Current starter-pack inventory

Starter packs currently live under `90-rules/packs/<pack-id>/`.

### Included packs

| Pack ID | Kind | `starter` flag | Role in current repo |
|---|---|---:|---|
| `university-generic` | `university-thesis` | `true` | Generic thesis starter for new university packs |
| `journal-generic` | `journal` | `true` | Generic journal starter for new submission packs |
| `tsinghua-thesis` | `university-thesis` | `false` | Concrete Tsinghua example pack, not treated as a starter baseline in metadata |
| `demo-university-thesis` | `university-thesis` | `false` | Concrete non-Tsinghua example pack for extension/story parity |

Sources:

- `90-rules/packs/university-generic/pack.yaml`
- `90-rules/packs/journal-generic/pack.yaml`
- `90-rules/packs/tsinghua-thesis/pack.yaml`
- `90-rules/packs/demo-university-thesis/pack.yaml`

---

## 2. Minimal pack shape the runtime loads

The runtime loader in `core/rules.py` expects three files in a pack directory:

- `pack.yaml`
- `rules.yaml`
- `mappings.yaml`

Code path:

- `core/rules.py::load_rule_pack()` loads those three files directly
- `core/rules.py::find_rule_pack()` resolves packs from `90-rules/packs/<ruleset>`

The runtime contract remains file-presence and parseability based. The lint contract adds stronger review-time checks before a pack is trusted or shared.

---

## 3. Current lint / scorecard baseline

Use:

```bash
python 90-rules/lint_pack.py --pack-path 90-rules/packs/<pack-id>
```

Current implementation:

- `90-rules/lint_pack.py`
- `core/pack_linter.py`
- `tests/test_pack_linter.py`

The current linter checks:

1. Required files exist:
   - `pack.yaml`
   - `rules.yaml`
   - `mappings.yaml`
2. Required `pack.yaml` fields exist:
   - `id`
   - `kind`
   - `display_name`
   - `version`
   - `precedence`
   - `starter`
3. Baseline `kind` values are valid:
   - `university-thesis`
   - `journal`
4. `starter` is a boolean.
5. `pack.yaml` `id` matches the directory name.
6. `rules.yaml` exposes required top-level sections:
   - `project`
   - `reference`
   - `language`
7. Required rule sections are mappings.
8. `mappings.yaml` matches one of the currently accepted shapes:
   - starter-pack shape: `mappings`
   - draft-pack shape: `source_template_mappings` + `chapter_role_mappings`

The current scorecard summarizes:

- `required_files`
- `metadata_completeness`
- `baseline_completeness`
- `schema_consistency`
- `overall_status`
- `finding_counts`

---

## 4. Starter-pack creation flow

### `create_pack.py`

Command:

```bash
python 90-rules/create_pack.py \
  --pack-id my-university \
  --display-name "My University Thesis" \
  --starter university-generic \
  --kind university-thesis
```

Current explicit constraints from `90-rules/create_pack.py`:

- `--starter` is limited to:
  - `university-generic`
  - `journal-generic`
  - `tsinghua-thesis`
- `--kind` is limited to:
  - `university-thesis`
  - `journal`

Underlying behavior from `core/pack_generator.py::create_rule_pack()`:

1. Copy the entire starter directory.
2. Rewrite these `pack.yaml` fields:
   - `id`
   - `display_name`
   - `kind`
   - `starter` → forced to `false`
3. Re-load the pack with `load_rule_pack()` to confirm the copied files are still parseable.

The starter-pack mechanism is a **copy-and-rewrite scaffold**, not a schema migration system. Any structure that is not explicitly rewritten is inherited from the starter as-is.

---

## 5. Draft-pack flow and extension assumption

`90-rules/create_draft_pack.py` wraps `core/pack_generator.py::create_draft_pack()`.

It accepts intake metadata and expects fields documented in `90-rules/THESIS_RULE_PACKS.md`, including:

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

`create_draft_pack()` writes a `mappings.yaml` using this structure:

- `source_template_mappings`
- `chapter_role_mappings`

Existing starter packs use a different baseline shape in `mappings.yaml`, for example:

- `mappings.source_styles`
- `mappings.latex_roles`

The current linter intentionally accepts both shapes. This preserves the real repo state without pretending a single normalized mapping schema exists yet.

---

## 6. Metadata fields visible in starter packs

The current `pack.yaml` starter baseline visibly includes:

- `id`
- `kind`
- `display_name`
- `version`
- `precedence`
- `starter`

For v1.0, a third-party pack should treat these fields as part of the practical baseline. Missing fields are lint errors.

---

## 7. Rules baseline visible in starters

The current starter packs are not empty templates; they embed practical rule defaults.

Examples visible in `rules.yaml` files:

- `project.main_tex_candidates`
- `project.chapter_globs`
- `project.bibliography_files`
- `reference.*`
- `language.*`
- `language_deep.*`

Comparative examples:

- `90-rules/packs/university-generic/rules.yaml`
- `90-rules/packs/journal-generic/rules.yaml`
- `90-rules/packs/tsinghua-thesis/rules.yaml`
- `90-rules/packs/demo-university-thesis/rules.yaml`

Today, “starter pack” means more than metadata scaffolding:

- it carries a default file-layout assumption
- it carries a default reference-check posture
- it carries a default language/style checking posture

Extending from a starter is therefore a policy inheritance decision, not just a folder bootstrap action.

---

## 8. Current v1.0 baseline summary

Treat the following as the documented baseline:

1. A pack lives at `90-rules/packs/<pack-id>/`.
2. A loadable pack has three parseable YAML files:
   - `pack.yaml`
   - `rules.yaml`
   - `mappings.yaml`
3. The starter inventory is:
   - `university-generic`
   - `journal-generic`
4. Concrete example packs include:
   - `tsinghua-thesis`
   - `demo-university-thesis`
5. Pack generation is copy-first, not schema-first.
6. The repository currently accepts two mapping shapes:
   - starter-pack shape
   - draft-pack shape
7. `lint_pack.py` is the current review-time quality gate for required files, metadata completeness, baseline completeness, schema consistency, and scorecard status.

---

## 9. Remaining hardening implications

The current baseline intentionally does not claim a full packaging ecosystem. Future hardening may still address:

1. A formal pack export bundle format.
2. A pack registry or publish command.
3. A dedicated portability score beyond the current lint scorecard summary.
4. A fully normalized internal mapping schema.

Until those exist, public docs should describe the current bounded model: local packs, Git-tracked evolution, handoff file sets, and lint reports.
