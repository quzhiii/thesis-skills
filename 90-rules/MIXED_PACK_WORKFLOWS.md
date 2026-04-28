# Mixed Rule-Pack Workflows

This document describes the **current practical workflows** for maintaining rule packs across three common situations:

1. local-only editing
2. Git-tracked pack evolution
3. export / handoff packaging

It is intentionally narrow and grounded in the repo as it exists now. It does not introduce a new packaging layer or claim a registry / release system that the repository does not yet implement.

---

## 1. When to use which workflow

### A. Local-only editing

Use this when you are still exploring a pack on your own machine and do **not** yet want to treat it as a shared baseline.

Typical cases:

- trying a new university pack copied from `university-generic`
- testing a journal-specific tweak against one manuscript
- checking whether a draft intake scaffold is even directionally correct

### B. Git-tracked pack evolution

Use this when the pack has moved past one-off experimentation and should become reproducible for future work.

Typical cases:

- the pack is now expected to be reused across projects
- you want explicit diff history on `pack.yaml`, `rules.yaml`, and `mappings.yaml`
- you want `lint_pack.py` output to be part of normal review before merging

### C. Export / handoff workflow

Use this when the immediate goal is to hand a pack, its notes, and its validation state to another person or to another environment without assuming they will reconstruct your local context.

Typical cases:

- handing a draft pack to a collaborator for manual rule confirmation
- attaching rule-pack artifacts to a review or migration handoff
- preserving the exact pack state used for a one-off institutional submission

---

## 2. Local-only editing workflow

### Recommended starting points

Use `create_pack.py` when you already know the closest starter:

```bash
python 90-rules/create_pack.py \
  --pack-id my-university \
  --display-name "My University Thesis" \
  --starter university-generic \
  --kind university-thesis
```

Use `create_draft_pack.py` when you have intake metadata and need a first scaffold:

```bash
python 90-rules/create_draft_pack.py \
  --intake adapters/intake/example-intake.json
```

### Files you should expect to keep intact

Every loadable pack currently depends on these three files:

- `pack.yaml`
- `rules.yaml`
- `mappings.yaml`

For draft scaffolds, you will also commonly see:

- `draft-notes.md`

### Local loop

The safest current local loop is:

1. generate or copy the pack
2. edit `pack.yaml`, `rules.yaml`, and `mappings.yaml`
3. run lint before trusting the pack again

```bash
python 90-rules/lint_pack.py --pack-path 90-rules/packs/my-university
```

If lint fails, treat the report as the first repair queue before widening the pack further.

---

## 3. Git-tracked pack evolution workflow

Once a pack is no longer purely experimental, treat it as a normal tracked artifact in the repository.

### What to commit together

Keep these changes in the same logical review unit when possible:

- `pack.yaml` metadata updates
- `rules.yaml` behavior changes
- `mappings.yaml` shape or role changes
- `draft-notes.md` or supporting docs that explain why the pack changed

### Minimum review discipline

Before considering the pack change reviewable, run:

```bash
python 90-rules/lint_pack.py --pack-path 90-rules/packs/<pack-id>
```

The current lint report now summarizes:

- required files
- metadata completeness
- baseline completeness
- schema consistency
- overall status
- finding counts

That means the current Git-tracked baseline is not just “did the YAML parse?” but also “does the pack still fit the repository’s accepted starter/draft shapes?”

### What Git history is best at here

Git is the right workflow once you care about:

- when a rule changed
- why `kind`, `precedence`, or `starter` metadata moved
- how a pack diverged from its original starter
- whether a mapping-shape change was intentional or accidental

At the current repo stage, Git is the system of record for pack evolution; there is no separate pack registry or release pipeline yet.

---

## 4. Export / handoff workflow

The repository does not yet implement a dedicated pack exporter, so “export” currently means **handoff as a bounded file set**.

### Minimum handoff set

If you need to hand a pack to someone else, include at least:

- the pack directory under `90-rules/packs/<pack-id>/`
- the latest lint report JSON from `90-rules/lint_pack.py`
- any `draft-notes.md` or equivalent context notes if the pack came from intake scaffolding

### Why the lint report matters

Without the lint report, a receiver only knows the files exist.
With the lint report, they also know whether the pack currently passes:

- required-file checks
- metadata completeness checks
- baseline completeness checks
- schema consistency checks

That makes the handoff inspectable instead of relying on “it worked on my machine.”

### Good export / handoff situations

- a local experimental pack is ready for another reviewer
- a draft-generated pack needs manual confirmation from someone who knows the institution better
- a one-off submission environment should preserve the exact pack state used for that run

---

## 5. Which path to choose in practice

### Choose local-only editing if:

- you are still discovering the right starter
- you expect large rule churn
- you are not yet ready to make the pack reproducible for others

### Choose Git-tracked evolution if:

- the pack has crossed from experiment to reusable baseline
- another contributor may need to understand the change later
- you want lint results and file diffs to be part of normal review

### Choose export / handoff if:

- the next user of the pack is not sharing your current working context
- you need to preserve the exact validated pack state used in a workflow
- you want a bounded pack package without claiming a formal publishing system

---

## 6. Current repository limits

This workflow doc assumes the repo state that exists today:

- there is a starter-pack baseline document
- there is a lint command
- there are completeness checks
- there are schema-consistency checks
- there is a scorecard summary in the lint report

But there is **not yet**:

- a formal pack publish command
- a pack registry
- a versioned export bundle format
- a dedicated portability score beyond the current lint scorecard summary

So keep workflow guidance bounded: use the existing files, existing lint, and Git history rather than inventing an ecosystem process the repo does not yet support.
