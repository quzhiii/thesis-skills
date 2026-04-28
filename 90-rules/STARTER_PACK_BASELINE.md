# Starter Pack Baseline

This document records the **current repository baseline** for rule-pack starters before `v0.8.1` adds lint, completeness, or scorecard tooling.

It is intentionally descriptive, not aspirational: the goal is to state what a starter pack currently means in this repo, which assumptions are already explicit, and which assumptions are only implied by the code path.

---

## 1. Current starter-pack inventory

Starter packs currently live under `90-rules/packs/<pack-id>/`.

### Included packs

| Pack ID | Kind | `starter` flag | Role in current repo |
|---|---|---:|---|
| `university-generic` | `university-thesis` | `true` | Generic thesis starter for new university packs |
| `journal-generic` | `journal` | `true` | Generic journal starter for new submission packs |
| `tsinghua-thesis` | `university-thesis` | `false` | Concrete example pack, not treated as a starter baseline in metadata |

Sources:

- `90-rules/packs/university-generic/pack.yaml`
- `90-rules/packs/journal-generic/pack.yaml`
- `90-rules/packs/tsinghua-thesis/pack.yaml`

---

## 2. Minimal pack shape that the runtime actually loads

The runtime loader in `core/rules.py` currently expects exactly three files in a pack directory:

- `pack.yaml`
- `rules.yaml`
- `mappings.yaml`

Code path:

- `core/rules.py::load_rule_pack()` loads those three files directly
- `core/rules.py::find_rule_pack()` resolves packs from `90-rules/packs/<ruleset>`

That means the current runtime contract is file-presence-based, not schema-enforced.

### What is explicit today

- Pack directories are resolved by folder name.
- A pack is considered loadable if those three YAML files exist and can be parsed.
- There is no dedicated pack linter yet.
- There is no separate completeness checker yet.
- There is no schema-consistency gate beyond “can these YAML files be loaded?”

### What is **not** explicit yet

- No repo-level enforcement that `pack.yaml` contains a complete required field set.
- No repo-level enforcement that `rules.yaml` exposes all expected checker sections.
- No repo-level enforcement that `mappings.yaml` follows one normalized internal structure.

---

## 3. Starter-pack creation flow as it exists now

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
2. Rewrite only these `pack.yaml` fields:
   - `id`
   - `display_name`
   - `kind`
   - `starter` → forced to `false`
3. Re-load the pack with `load_rule_pack()` to confirm the copied files are still parseable.

### Current implication

The starter-pack mechanism is a **copy-and-rewrite scaffold**, not a schema migration system.

Any structure that is not explicitly rewritten is inherited from the starter as-is.

---

## 4. Draft-pack flow and the current extension assumption

`90-rules/create_draft_pack.py` wraps `core/pack_generator.py::create_draft_pack()`.

It accepts intake metadata and currently expects fields documented in `90-rules/THESIS_RULE_PACKS.md`, including:

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

### Important current assumption

`create_draft_pack()` writes a new `mappings.yaml` using this structure:

- `source_template_mappings`
- `chapter_role_mappings`

But the existing starter packs currently use a different baseline shape in `mappings.yaml`, for example:

- `mappings.source_styles`
- `mappings.latex_roles`

Example source:

- `90-rules/packs/university-generic/mappings.yaml`

### Why this matters

This is the clearest current extension assumption gap:

- the runtime only checks that `mappings.yaml` parses,
- but the repository does **not** yet enforce one normalized mapping schema across starter packs and draft-generated packs.

`v0.8.1` should treat this as a documentation-first hardening target before adding stronger validation.

---

## 5. Metadata fields already visible in starter packs

The current `pack.yaml` starter baseline visibly includes:

- `id`
- `kind`
- `display_name`
- `version`
- `precedence`
- `starter`

This is explicit in:

- `90-rules/packs/university-generic/pack.yaml`
- `90-rules/packs/journal-generic/pack.yaml`
- `90-rules/packs/tsinghua-thesis/pack.yaml`

### Extension assumption

For now, a third-party pack should assume those fields are part of the practical baseline, even though the repo does not yet have a dedicated validator that rejects incomplete metadata.

---

## 6. Rules baseline visible in the current starters

The current starter packs are not empty templates; they already embed practical rule defaults.

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

### Extension assumption

Today, “starter pack” means more than metadata scaffolding:

- it carries a default file-layout assumption,
- a default reference-check posture,
- and a default language/style checking posture.

So extending from a starter is currently a policy inheritance decision, not just a folder bootstrap action.

---

## 7. What `v0.8.1` should assume as baseline from this point

Before adding lint or scorecards, treat the following as the documented baseline:

1. A pack lives at `90-rules/packs/<pack-id>/`.
2. A loadable pack currently means three parseable YAML files:
   - `pack.yaml`
   - `rules.yaml`
   - `mappings.yaml`
3. The current starter inventory is:
   - `university-generic`
   - `journal-generic`
   - `tsinghua-thesis`
4. Only the first two are marked `starter: true` in metadata.
5. Pack generation is currently copy-first, not schema-first.
6. Mapping-schema consistency is **not** fully normalized yet.
7. Any new lint/completeness tooling should check against this repo-state baseline instead of inventing a broader contract first.

---

## 8. Immediate hardening implications

This baseline suggests that the first `v0.8.1` hardening passes should answer four concrete questions:

1. Does every pack have the three required YAML files?
2. Does every `pack.yaml` include the baseline metadata fields already used by current starters?
3. Does every starter-generated or draft-generated pack produce a mapping file shape that the repo is willing to support long-term?
4. Can we distinguish “starter baseline”, “concrete example pack”, and “draft-generated pack” without relying only on folder naming and loose convention?

Those are the questions the later lint / completeness / schema-consistency work should formalize.
