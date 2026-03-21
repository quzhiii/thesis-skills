# Technical Roadmap

## Release Positioning

`v0.3.0` is the release where `thesis-skills` becomes a cleaner public repository instead of only an internal workflow snapshot.

This release keeps the stronger local engineering core while presenting a clearer external story:

- deterministic checks instead of prompt-only QA
- report-driven fixers instead of unconstrained rewriting
- reusable rule packs instead of one-off template hacks
- bibliography intake workflows with explicit support levels

## Product Direction

The repository follows five layers:

1. bibliography intake
2. Word-to-LaTeX migration
3. deterministic checking
4. report-driven fixing
5. ruleset onboarding and reuse

That means the project is not trying to be a general writing assistant. It is an infrastructure layer for academic writing workflows that need to be repeatable, inspectable, and extensible.

## Support Matrix

| Workflow | Status in v0.3.0 | Notes |
|---|---|---|
| Zotero BibTeX quality check | Stable | `00-bib-zotero/check_bib_quality.py` |
| Zotero Word citation sync | Stable | extract -> compare -> map -> `citation-lock.tex` |
| EndNote export intake | Supported | export BibTeX, normalize, then run quality checks |
| EndNote direct sync | Planned | not implemented in v0.3.0 |
| Word -> LaTeX migration | Stable | explicit migration spec with structured metadata |
| Deterministic check -> fix loop | Stable | covered by regression tests |
| Rule pack generation | Stable | starter and draft-pack paths both exist |

## Why EndNote Is Not Symmetric Yet

Zotero support is deeper because Word documents can carry structured citation payloads that this repository can extract and map.

EndNote support is currently positioned as a controlled intake path:

1. export from EndNote
2. normalize BibTeX
3. validate quality
4. continue into the same check/fix pipeline

This is deliberate. It avoids promising a direct sync path before the repository has a robust EndNote field model, sample corpus, and mapping contract.

## Roadmap by Release

### v0.3.0

- publish the restructured repository
- ship bilingual README refresh
- expose the architecture as layered workflows
- keep Zotero sync as the strongest bibliography path
- position EndNote as an export-based intake workflow
- keep regression tests and CI in the public release

### v0.4.0

- add stronger bibliography intake docs and sample fixtures
- improve release docs for pack onboarding
- reduce pyright rough edges in runner typing
- improve example coverage for non-Tsinghua rulesets

### v0.5.0

- evaluate RIS/EndNote XML intake feasibility
- add more schools and journal packs
- add issue templates for false positives and pack onboarding
- improve compile-log diagnostics and user-facing error messages

### v1.0.0

- stable public architecture and packaging story
- clearer boundary between skills, runners, and optional Word-side tooling
- stronger test coverage for real-world bibliography and migration samples
- documented extension contract for third-party rule packs

## Repository Design Rules

- keep top-level folders user-comprehensible
- keep `core/` as the reusable implementation layer
- keep checkers deterministic
- keep fixers bounded and reversible
- keep policy in rule packs, not hard-coded into runners
- do not overstate EndNote support before direct sync exists

## Recommended Next Technical Work

1. harden typing in runner and checker entrypoints
2. add sample fixtures for malformed mapping files and noisy Word exports
3. add more example packs beyond starter packs
4. define a formal bibliography intake contract shared by Zotero and EndNote paths
5. decide whether future EndNote support should target BibTeX only, RIS, or XML
